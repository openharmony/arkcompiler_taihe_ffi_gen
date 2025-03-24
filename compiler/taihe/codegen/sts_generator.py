from json import dumps
from typing import TYPE_CHECKING

from taihe.codegen.ani_generator import (
    EnumANIInfo,
    GlobFuncANIInfo,
    IfaceANIInfo,
    IfaceMethodANIInfo,
    PackageANIInfo,
    StructANIInfo,
    TypeANIInfo,
)
from taihe.semantics.declarations import (
    EnumDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
    StructDecl,
    UnionDecl,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputBuffer, OutputManager

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        Type,
    )


class Namespace:
    def __init__(self):
        self.children: dict[str, Namespace] = {}
        self.packages: list[PackageDecl] = []

    def add_path(self, path_parts: list[str], pkg: PackageDecl):
        if not path_parts:
            self.packages.append(pkg)
            return
        head, *tail = path_parts
        child = self.children.setdefault(head, Namespace())
        child.add_path(tail, pkg)


class STSCodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        ns_dict: dict[str, Namespace] = {}

        for pkg in pg.packages:
            pkg_ani_info = PackageANIInfo.get(self.am, pkg)
            if pkg_ani_info.sts_ns:
                sts_ns_parts = pkg_ani_info.sts_ns.split()
            else:
                sts_ns_parts = []
            ns_dict.setdefault(pkg_ani_info.module, Namespace()).add_path(
                sts_ns_parts, pkg
            )

        for module, ns in ns_dict.items():
            self.gen_module_file(module, ns)

    def gen_module_file(self, module: str, ns: Namespace):
        module_sts_file = f"{module}.ets"

        pkg_sts_target = OutputBuffer.create(self.tm, module_sts_file)

        # pkg_sts_target.write(f'loadLibrary("{self.lib_name}");\n')

        self.gen_namespace_or_module(ns, pkg_sts_target)

    def gen_namespace_or_module(self, ns: Namespace, pkg_sts_target: OutputBuffer):
        for child_ns_name, child_ns in ns.children.items():
            pkg_sts_target.write(f"export namespace {child_ns_name} {{\n")
            with pkg_sts_target.indent_manager.code_block():
                self.gen_namespace_or_module(child_ns, pkg_sts_target)
            pkg_sts_target.write(f"}}\n")

        for pkg in ns.packages:
            self.gen_package(pkg, pkg_sts_target)

    def get_onoff_funcs(self, funcs: list[GlobFuncDecl]):
        glob_func_onoff_map: dict[
            tuple[str, tuple[Type, ...]], list[tuple[str, GlobFuncDecl]]
        ] = {}

        for func in funcs:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            if func_ani_info.onoff_type is not None:
                func_name, type_name = func_ani_info.onoff_type
                real_params_ty = []
                for real_param in func_ani_info.sts_real_params:
                    assert real_param.ty_ref.resolved_ty
                    real_params_ty.append(real_param.ty_ref.resolved_ty)
                glob_func_onoff_map.setdefault(
                    (func_name, tuple(real_params_ty)), []
                ).append((type_name, func))

        return glob_func_onoff_map

    def get_onoff_methods(self, methods: list[IfaceMethodDecl]):
        method_onoff_map: dict[
            tuple[str, tuple[Type, ...]], list[tuple[str, IfaceMethodDecl]]
        ] = {}

        for method in methods:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            if method_ani_info.onoff_type is not None:
                method_name, type_name = method_ani_info.onoff_type
                real_params_ty = []
                for real_param in method_ani_info.sts_real_params:
                    assert real_param.ty_ref.resolved_ty
                    real_params_ty.append(real_param.ty_ref.resolved_ty)
                method_onoff_map.setdefault(
                    (method_name, tuple(real_params_ty)), []
                ).append((type_name, method))

        return method_onoff_map

    def gen_package(self, pkg: PackageDecl, pkg_sts_target: OutputBuffer):
        # native funcs
        for func in pkg.functions:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            sts_native_params = []
            for param in func.params:
                type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
                sts_native_params.append(f"{param.name}: {type_ani_info.sts_type}")
            sts_native_params_str = ", ".join(sts_native_params)
            if return_ty_ref := func.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            pkg_sts_target.write(
                f"native function {func_ani_info.sts_native_name}({sts_native_params_str}): {sts_return_ty_name};\n"
            )

        ctors: dict[str, list[GlobFuncDecl]] = {}
        statics: dict[str, list[GlobFuncDecl]] = {}
        funcs: list[GlobFuncDecl] = []

        for func in pkg.functions:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            if class_name := func_ani_info.sts_static_scope:
                statics.setdefault(class_name, []).append(func)
            elif class_name := func_ani_info.sts_ctor_scope:
                ctors.setdefault(class_name, []).append(func)
            else:
                funcs.append(func)

        glob_func_onoff_map = self.get_onoff_funcs(funcs)

        for (func_name, real_params_ty), func_list in glob_func_onoff_map.items():
            sts_real_params = []
            sts_real_args = []
            sts_real_params.append("type: string")
            for index, param_ty in enumerate(real_params_ty):
                type_ani_info = TypeANIInfo.get(self.am, param_ty)
                param_name = f"p_{index}"
                sts_real_params.append(f"{param_name}: {type_ani_info.sts_type}")
                sts_real_args.append(param_name)
            sts_real_params_str = ", ".join(sts_real_params)
            pkg_sts_target.write(
                f"export function {func_name}({sts_real_params_str}): void {{\n"
                f"    switch(type) {{"
            )
            for type_name, func in func_list:
                func_ani_info = GlobFuncANIInfo.get(self.am, func)
                sts_native_call = func_ani_info.call_native_with(sts_real_args)
                pkg_sts_target.write(
                    f'        case "{type_name}": return {sts_native_call};\n'
                )
            pkg_sts_target.write(
                f"        default: throw new Error(`Unknown type: ${{type}}`);\n"
                f"    }}\n"
                f"}}\n"
            )

        for func in funcs:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            sts_real_params = []
            sts_real_args = []
            for sts_real_param in func_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(
                    self.am, sts_real_param.ty_ref.resolved_ty
                )
                sts_real_params.append(
                    f"{sts_real_param.name}: {type_ani_info.sts_type}"
                )
                sts_real_args.append(sts_real_param.name)
            sts_real_params_str = ", ".join(sts_real_params)
            sts_native_call = func_ani_info.call_native_with(sts_real_args)
            if return_ty_ref := func.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            # real
            if func_ani_info.sts_func_name is not None:
                pkg_sts_target.write(
                    f"export function {func_ani_info.sts_func_name}({sts_real_params_str}): {sts_return_ty_name} {{\n"
                    f"    return {sts_native_call};\n"
                    f"}}\n"
                )
                # promise
                if (promise_func_name := func_ani_info.sts_promise_name) is not None:
                    if return_ty_ref := func.return_ty_ref:
                        resolve_params = f"data: {sts_return_ty_name}"
                        resolve_args = f"ret as {sts_return_ty_name}"
                    else:
                        resolve_params = ""
                        resolve_args = ""
                    pkg_sts_target.write(
                        f"export function {promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}> {{\n"
                        f"    return new Promise<{sts_return_ty_name}>((resolve: ({resolve_params}) => void, reject: (err: Error) => void): void => {{\n"
                        f"        taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})\n"
                        f"        .then((ret: NullishType): void => {{\n"
                        f"            resolve({resolve_args});\n"
                        f"        }})\n"
                        f"        .catch((ret: NullishType): void => {{\n"
                        f"            reject(ret as Error);\n"
                        f"        }});\n"
                        f"    }});\n"
                        f"}}\n"
                    )
                # async
                if (async_func_name := func_ani_info.sts_async_name) is not None:
                    if return_ty_ref := func.return_ty_ref:
                        callback = f"callback: (err: Error, data?: {sts_return_ty_name}) => void"
                        then_args = f"new Error(), ret as {sts_return_ty_name}"
                    else:
                        callback = "callback: (err: Error) => void"
                        then_args = "new Error()"
                    sts_real_params_with_cb = [*sts_real_params, callback]
                    sts_real_params_with_cb_str = ", ".join(sts_real_params_with_cb)
                    pkg_sts_target.write(
                        f"export function {async_func_name}({sts_real_params_with_cb_str}): void {{\n"
                        f"    taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})\n"
                        f"    .then((ret: NullishType): void => {{\n"
                        f"        callback({then_args});\n"
                        f"    }})\n"
                        f"    .catch((ret: NullishType): void => {{\n"
                        f"        callback(ret as Error);\n"
                        f"    }});\n"
                        f"}}\n"
                    )

        for enum in pkg.enums:
            self.gen_enum(enum, pkg_sts_target)
        for struct in pkg.structs:
            self.gen_struct(struct, pkg_sts_target)
        for union in pkg.unions:
            self.gen_union(union, pkg_sts_target)
        for iface in pkg.interfaces:
            self.gen_iface_interface(iface, pkg_sts_target)
        for iface in pkg.interfaces:
            self.gen_iface_class(iface, pkg_sts_target, statics, ctors)

    def gen_enum(
        self,
        enum: EnumDecl,
        pkg_sts_target: OutputBuffer,
    ):
        enum_ani_info = EnumANIInfo.get(self.am, enum)
        pkg_sts_target.write(f"export enum {enum_ani_info.sts_type} {{\n")
        for item in enum.items:
            pkg_sts_target.write(f"    {item.name} = {dumps(item.value)},\n")
        pkg_sts_target.write(f"}}\n")

    def gen_union(
        self,
        union: UnionDecl,
        pkg_sts_target: OutputBuffer,
    ):
        pass

    def gen_struct(
        self,
        struct: StructDecl,
        pkg_sts_target: OutputBuffer,
    ):
        struct_ani_info = StructANIInfo.get(self.am, struct)
        pkg_sts_target.write(f"export class {struct_ani_info.sts_impl} {{\n")
        for field in struct.fields:
            ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            pkg_sts_target.write(f"    {field.name}: {ty_ani_info.sts_type};\n")
        pkg_sts_target.write(f"    constructor(\n")
        for field in struct.fields:
            ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            pkg_sts_target.write(f"        {field.name}: {ty_ani_info.sts_type},\n")
        pkg_sts_target.write(f"    ) {{\n")
        for field in struct.fields:
            pkg_sts_target.write(f"        this.{field.name} = {field.name};\n")
        pkg_sts_target.write(f"    }}\n" f"}}\n")

    def gen_iface_interface(
        self,
        iface: IfaceDecl,
        pkg_sts_target: OutputBuffer,
    ):
        iface_ani_info = IfaceANIInfo.get(self.am, iface)
        if iface_ani_info.sts_type == iface_ani_info.sts_impl:  # no interface
            return

        pkg_sts_target.write(f"export interface {iface_ani_info.sts_type} {{\n")

        method_onoff_map = self.get_onoff_methods(iface.methods)

        for (method_name, real_params_ty), _ in method_onoff_map.items():
            sts_real_params = []
            sts_real_params.append("type: string")
            for index, param_ty in enumerate(real_params_ty):
                type_ani_info = TypeANIInfo.get(self.am, param_ty)
                param_name = f"p_{index}"
                sts_real_params.append(f"{param_name}: {type_ani_info.sts_type}")
            sts_real_params_str = ", ".join(sts_real_params)
            pkg_sts_target.write(f"    {method_name}({sts_real_params_str}): void;\n")

        for method in iface.methods:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            sts_real_params = []
            for real_param in method_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(self.am, real_param.ty_ref.resolved_ty)
                sts_real_params.append(f"{real_param.name}: {type_ani_info.sts_type}")
            sts_real_params_str = ", ".join(sts_real_params)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            # real
            if real_method := method_ani_info.sts_method_name:
                pkg_sts_target.write(
                    f"    {real_method}({sts_real_params_str}): {sts_return_ty_name};\n"
                )
                # promise
                if (promise_func_name := method_ani_info.sts_promise_name) is not None:
                    pkg_sts_target.write(
                        f"    {promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}>;\n"
                    )
                # async
                if (async_func_name := method_ani_info.sts_async_name) is not None:
                    if return_ty_ref := method.return_ty_ref:
                        callback = f"callback: (err: Error, data?: {sts_return_ty_name}) => void"
                    else:
                        callback = "callback: (err: Error) => void"
                    sts_real_params_with_cb = [*sts_real_params, callback]
                    sts_real_params_with_cb_str = ", ".join(sts_real_params_with_cb)
                    pkg_sts_target.write(
                        f"    {async_func_name}({sts_real_params_with_cb_str}): void;\n"
                    )
            # getter
            if get_name := method_ani_info.get_name:
                pkg_sts_target.write(
                    f"    get {get_name}({sts_real_params_str}): {sts_return_ty_name};\n"
                )
            # setter
            if set_name := method_ani_info.set_name:
                pkg_sts_target.write(f"    set {set_name}({sts_real_params_str});\n")

        pkg_sts_target.write(f"}}\n")

    def gen_iface_class(
        self,
        iface: IfaceDecl,
        pkg_sts_target: OutputBuffer,
        statics: dict[str, list[GlobFuncDecl]],
        construct_methods: dict[str, list[GlobFuncDecl]],
    ):
        iface_ani_info = IfaceANIInfo.get(self.am, iface)

        if iface_ani_info.sts_impl == iface_ani_info.sts_type:
            pkg_sts_target.write(f"export class {iface_ani_info.sts_impl} {{\n")
        else:
            pkg_sts_target.write(
                f"class {iface_ani_info.sts_impl} implements {iface_ani_info.sts_type} {{\n"
            )

        pkg_sts_target.write(
            f"    private _vtbl_ptr: long;\n"
            f"    private _data_ptr: long;\n"
            f"    private constructor(_vtbl_ptr: long, _data_ptr: long) {{\n"
            f"        this._vtbl_ptr = _vtbl_ptr;\n"
            f"        this._data_ptr = _data_ptr;\n"
            f"    }}\n"
        )

        for func in construct_methods.get(iface.name, []):
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            sts_real_params = []
            sts_real_args = []
            for sts_real_param in func_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(
                    self.am, sts_real_param.ty_ref.resolved_ty
                )
                sts_real_params.append(
                    f"{sts_real_param.name}: {type_ani_info.sts_type}"
                )
                sts_real_args.append(sts_real_param.name)
            sts_real_params_str = ", ".join(sts_real_params)
            sts_native_call = func_ani_info.call_native_with(sts_real_args)
            pkg_sts_target.write(
                f"    constructor({sts_real_params_str}) {{\n"
                f"        let temp = {sts_native_call} as {iface_ani_info.sts_impl};\n"
                f"        this._data_ptr = temp._data_ptr;\n"
                f"        this._vtbl_ptr = temp._vtbl_ptr;\n"
                f"    }}\n"
            )

        static_onoff_map = self.get_onoff_funcs(statics.get(iface.name, []))

        for (func_name, real_params_ty), func_list in static_onoff_map.items():
            sts_real_params = []
            sts_real_args = []
            sts_real_params.append("type: string")
            for index, param_ty in enumerate(real_params_ty):
                type_ani_info = TypeANIInfo.get(self.am, param_ty)
                param_name = f"p_{index}"
                sts_real_params.append(f"{param_name}: {type_ani_info.sts_type}")
                sts_real_args.append(param_name)
            sts_real_params_str = ", ".join(sts_real_params)
            pkg_sts_target.write(
                f"    static {func_name}({sts_real_params_str}): void {{\n"
                f"        switch(type) {{"
            )
            for type_name, func in func_list:
                func_ani_info = GlobFuncANIInfo.get(self.am, func)
                sts_native_call = func_ani_info.call_native_with(sts_real_args)
                pkg_sts_target.write(
                    f'            case "{type_name}": return {sts_native_call};\n'
                )
            pkg_sts_target.write(
                f"            default: throw new Error(`Unknown type: ${{type}}`);\n"
                f"        }}\n"
                f"    }}\n"
            )

        for func in statics.get(iface.name, []):
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            sts_real_params = []
            sts_real_args = []
            for sts_real_param in func_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(
                    self.am, sts_real_param.ty_ref.resolved_ty
                )
                sts_real_params.append(
                    f"{sts_real_param.name}: {type_ani_info.sts_type}"
                )
                sts_real_args.append(sts_real_param.name)
            sts_real_params_str = ", ".join(sts_real_params)
            sts_native_call = func_ani_info.call_native_with(sts_real_args)
            if return_ty_ref := func.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            # real
            if func_ani_info.sts_func_name is not None:
                pkg_sts_target.write(
                    f"    static {func_ani_info.sts_func_name}({sts_real_params_str}): {sts_return_ty_name} {{\n"
                    f"        return {sts_native_call};\n"
                    f"    }}\n"
                )
                # promise
                if (promise_func_name := func_ani_info.sts_promise_name) is not None:
                    if return_ty_ref := func.return_ty_ref:
                        resolve_params = f"data: {sts_return_ty_name}"
                        resolve_args = f"ret as {sts_return_ty_name}"
                    else:
                        resolve_params = ""
                        resolve_args = ""
                    pkg_sts_target.write(
                        f"static {promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}> {{\n"
                        f"    return new Promise<{sts_return_ty_name}>((resolve: ({resolve_params}) => void, reject: (err: Error) => void): void => {{\n"
                        f"        taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})\n"
                        f"        .then((ret: NullishType): void => {{\n"
                        f"            resolve({resolve_args});\n"
                        f"        }})\n"
                        f"        .catch((ret: NullishType): void => {{\n"
                        f"            reject(ret as Error);\n"
                        f"        }});\n"
                        f"    }});\n"
                        f"}}\n"
                    )
                # async
                if (async_func_name := func_ani_info.sts_async_name) is not None:
                    if return_ty_ref := func.return_ty_ref:
                        callback = f"callback: (err: Error, data?: {sts_return_ty_name}) => void"
                        then_args = f"new Error(), ret as {sts_return_ty_name}"
                    else:
                        callback = "callback: (err: Error) => void"
                        then_args = "new Error()"
                    sts_real_params_with_cb = [*sts_real_params, callback]
                    sts_real_params_with_cb_str = ", ".join(sts_real_params_with_cb)
                    pkg_sts_target.write(
                        f"    static {async_func_name}({sts_real_params_with_cb_str}): void {{\n"
                        f"        taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})\n"
                        f"        .then((ret: NullishType): void => {{\n"
                        f"            callback({then_args});\n"
                        f"        }})\n"
                        f"        .catch((ret: NullishType): void => {{\n"
                        f"            callback(ret as Error);\n"
                        f"        }});\n"
                        f"    }}\n"
                    )

        # native funcs
        for method in iface.methods:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            sts_native_params = []
            for param in method.params:
                type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
                sts_native_params.append(f"{param.name}: {type_ani_info.sts_type}")
            sts_native_params_str = ", ".join(sts_native_params)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            pkg_sts_target.write(
                f"    native {method_ani_info.sts_native_name}({sts_native_params_str}): {sts_return_ty_name};\n"
            )

        method_onoff_map = self.get_onoff_methods(iface.methods)

        for (method_name, real_params_ty), method_list in method_onoff_map.items():
            sts_real_params = []
            sts_real_args = []
            sts_real_params.append("type: string")
            for index, param_ty in enumerate(real_params_ty):
                type_ani_info = TypeANIInfo.get(self.am, param_ty)
                param_name = f"p_{index}"
                sts_real_params.append(f"{param_name}: {type_ani_info.sts_type}")
                sts_real_args.append(param_name)
            sts_real_params_str = ", ".join(sts_real_params)
            pkg_sts_target.write(
                f"    {method_name}({sts_real_params_str}): void {{\n"
                f"        switch(type) {{"
            )
            for type_name, method in method_list:
                method_ani_info = IfaceMethodANIInfo.get(self.am, method)
                sts_native_call = method_ani_info.call_native_with(
                    "this", sts_real_args
                )
                pkg_sts_target.write(
                    f'            case "{type_name}": return {sts_native_call};\n'
                )
            pkg_sts_target.write(
                f"            default: throw new Error(`Unknown type: ${{type}}`);\n"
                f"        }}\n"
                f"    }}\n"
            )

        for method in iface.methods:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            sts_real_params = []
            sts_real_args = []
            for sts_real_param in method_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(
                    self.am, sts_real_param.ty_ref.resolved_ty
                )
                sts_real_params.append(
                    f"{sts_real_param.name}: {type_ani_info.sts_type}"
                )
                sts_real_args.append(sts_real_param.name)
            sts_real_params_str = ", ".join(sts_real_params)
            sts_native_call = method_ani_info.call_native_with("this", sts_real_args)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            # real
            if real_method := method_ani_info.sts_method_name:
                pkg_sts_target.write(
                    f"    {real_method}({sts_real_params_str}): {sts_return_ty_name} {{\n"
                    f"        return {sts_native_call};\n"
                    f"    }}\n"
                )
                # promise
                if (promise_func_name := method_ani_info.sts_promise_name) is not None:
                    if return_ty_ref := method.return_ty_ref:
                        resolve_params = f"data: {sts_return_ty_name}"
                        resolve_args = f"ret as {sts_return_ty_name}"
                    else:
                        resolve_params = ""
                        resolve_args = ""
                    pkg_sts_target.write(
                        f"    {promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}> {{\n"
                        f"        return new Promise<{sts_return_ty_name}>((resolve: ({resolve_params}) => void, reject: (err: Error) => void): void => {{\n"
                        f"            taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})\n"
                        f"            .then((ret: NullishType): void => {{\n"
                        f"                resolve({resolve_args});\n"
                        f"            }})\n"
                        f"            .catch((ret: NullishType): void => {{\n"
                        f"                reject(ret as Error);\n"
                        f"            }});\n"
                        f"        }});\n"
                        f"    }}\n"
                    )
                # async
                if (async_func_name := method_ani_info.sts_async_name) is not None:
                    if return_ty_ref := method.return_ty_ref:
                        callback = f"callback: (err: Error, data?: {sts_return_ty_name}) => void"
                        then_args = f"new Error(), ret as {sts_return_ty_name}"
                    else:
                        callback = "callback: (err: Error) => void"
                        then_args = "new Error()"
                    sts_real_params_with_cb = [*sts_real_params, callback]
                    sts_real_params_with_cb_str = ", ".join(sts_real_params_with_cb)
                    pkg_sts_target.write(
                        f"    {async_func_name}({sts_real_params_with_cb_str}): void {{\n"
                        f"        taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})\n"
                        f"        .then((ret: NullishType): void => {{\n"
                        f"            callback({then_args});\n"
                        f"        }})\n"
                        f"        .catch((ret: NullishType): void => {{\n"
                        f"            callback(ret as Error);\n"
                        f"        }});\n"
                        f"    }}\n"
                    )
            # getter
            if get_name := method_ani_info.get_name:
                pkg_sts_target.write(
                    f"    get {get_name}({sts_real_params_str}): {sts_return_ty_name} {{\n"
                    f"        return {sts_native_call};\n"
                    f"    }}\n"
                )
            # setter
            if set_name := method_ani_info.set_name:
                pkg_sts_target.write(
                    f"    set {set_name}({sts_real_params_str}) {{\n"
                    f"        return {sts_native_call};\n"
                    f"    }}\n"
                )

        pkg_sts_target.write(f"}}\n")
