from json import dumps
from typing import TYPE_CHECKING, Optional

from taihe.codegen.abi_generator import (
    IfaceABIInfo,
)
from taihe.codegen.ani_generator import (
    EnumANIInfo,
    GlobFuncANIInfo,
    IfaceANIInfo,
    IfaceMethodANIInfo,
    PackageANIInfo,
    StructANIInfo,
    TypeANIInfo,
    UnionANIInfo,
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
from taihe.semantics.types import IfaceType, StructType
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputManager, STSOutputBuffer

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
            ns_dict.setdefault(pkg_ani_info.module, Namespace()).add_path(
                pkg_ani_info.sts_ns_parts, pkg
            )
        for module, ns in ns_dict.items():
            self.gen_module_file(module, ns)

    def gen_module_file(self, module: str, ns: Namespace):
        module_sts_file = f"{module}.ets"
        target = STSOutputBuffer.create(self.tm, module_sts_file)
        self.gen_namespace(ns, target)

    def gen_namespace(self, ns: Namespace, target: STSOutputBuffer):
        for child_ns_name, child_ns in ns.children.items():
            target.writeln(
                f"export namespace {child_ns_name} {{",
            )
            with target.indent_manager.offset(4):
                self.gen_namespace(child_ns, target)
            target.writeln(
                f"}}",
            )
        for pkg in ns.packages:
            self.gen_package(pkg, target)

    def stat_on_off_funcs(self, funcs: list[GlobFuncDecl]):
        glob_func_on_off_map: dict[
            tuple[str, tuple[Type, ...], Optional[Type]], list[tuple[str, GlobFuncDecl]]
        ] = {}
        for func in funcs:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            if func_ani_info.on_off_type is not None:
                func_name, type_name = func_ani_info.on_off_type
                real_params_ty = []
                for real_param in func_ani_info.sts_real_params:
                    assert real_param.ty_ref.resolved_ty
                    real_params_ty.append(real_param.ty_ref.resolved_ty)
                if func.return_ty_ref:
                    return_ty = func.return_ty_ref.resolved_ty
                else:
                    return_ty = None
                glob_func_on_off_map.setdefault(
                    (func_name, tuple(real_params_ty), return_ty), []
                ).append((type_name, func))
        return glob_func_on_off_map

    def stat_on_off_methods(self, methods: list[IfaceMethodDecl]):
        method_on_off_map: dict[
            tuple[str, tuple[Type, ...], Optional[Type]],
            list[tuple[str, IfaceMethodDecl]],
        ] = {}
        for method in methods:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            if method_ani_info.on_off_type is not None:
                method_name, type_name = method_ani_info.on_off_type
                real_params_ty = []
                for real_param in method_ani_info.sts_real_params:
                    assert real_param.ty_ref.resolved_ty
                    real_params_ty.append(real_param.ty_ref.resolved_ty)
                if method.return_ty_ref:
                    return_ty = method.return_ty_ref.resolved_ty
                else:
                    return_ty = None
                method_on_off_map.setdefault(
                    (method_name, tuple(real_params_ty), return_ty), []
                ).append((type_name, method))
        return method_on_off_map

    def gen_package(self, pkg: PackageDecl, target: STSOutputBuffer):
        # TODO: hack inject
        pkg_ani_info = PackageANIInfo.get(self.am, pkg)
        for injected in pkg_ani_info.injected_codes:
            target.writeln(injected)

        # TODO: finalizer
        self.gen_finalizer(target)
        self.gen_native_funcs(pkg, pkg.functions, target)
        ctors_map: dict[str, list[GlobFuncDecl]] = {}
        statics_map: dict[str, list[GlobFuncDecl]] = {}
        funcs: list[GlobFuncDecl] = []
        for func in pkg.functions:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            if class_name := func_ani_info.sts_static_scope:
                statics_map.setdefault(class_name, []).append(func)
            elif class_name := func_ani_info.sts_ctor_scope:
                ctors_map.setdefault(class_name, []).append(func)
            else:
                funcs.append(func)
        self.gen_global_funcs(pkg, funcs, target)
        for enum in pkg.enums:
            self.gen_enum(pkg, enum, target)
        for union in pkg.unions:
            self.gen_union(pkg, union, target)
        for struct in pkg.structs:
            self.gen_struct_interface(pkg, struct, target)
        for struct in pkg.structs:
            self.gen_struct_class(pkg, struct, target)
        for iface in pkg.interfaces:
            self.gen_iface_interface(pkg, iface, target)
        for iface in pkg.interfaces:
            self.gen_iface_class(pkg, iface, target, statics_map, ctors_map)

    def gen_finalizer(
        self,
        target: STSOutputBuffer,
    ):
        target.writeln(
            f"export native function localFinalizer(data_ptr: long): void;",
            f"export const localDestroyRegister = new FinalizationRegistry<long>(localFinalizer);",
        )

    def gen_native_funcs(
        self,
        pkg: PackageDecl,
        funcs: list[GlobFuncDecl],
        target: STSOutputBuffer,
    ):
        # native funcs
        for func in funcs:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            sts_native_params = []
            for param in func.params:
                type_ani_info = TypeANIInfo.get(self.am, pkg, param.ty_ref.resolved_ty)
                sts_native_params.append(
                    f"{param.name}: {type_ani_info.sts_type_in(pkg, target)}"
                )
            sts_native_params_str = ", ".join(sts_native_params)
            if return_ty_ref := func.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, pkg, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type_in(pkg, target)
            else:
                sts_return_ty_name = "void"
            target.writeln(
                f"native function {func_ani_info.sts_native_name}({sts_native_params_str}): {sts_return_ty_name};",
            )

    def gen_global_funcs(
        self,
        pkg: PackageDecl,
        funcs: list[GlobFuncDecl],
        target: STSOutputBuffer,
    ):
        # on_off
        glob_func_on_off_map = self.stat_on_off_funcs(funcs)
        for (
            func_name,
            real_params_ty,
            return_ty,
        ), func_list in glob_func_on_off_map.items():
            sts_real_params = []
            sts_real_args = []
            sts_real_params.append("type: string")
            for index, param_ty in enumerate(real_params_ty):
                type_ani_info = TypeANIInfo.get(self.am, pkg, param_ty)
                param_name = f"p_{index}"
                sts_real_params.append(
                    f"{param_name}: {type_ani_info.sts_type_in(pkg, target)}"
                )
                sts_real_args.append(param_name)
            sts_real_params_str = ", ".join(sts_real_params)
            if return_ty:
                type_ani_info = TypeANIInfo.get(self.am, pkg, return_ty)
                return_ty_str = type_ani_info.sts_type_in(pkg, target)
            else:
                return_ty_str = "void"
            target.writeln(
                f"export function {func_name}({sts_real_params_str}): {return_ty_str} {{",
                f"    switch(type) {{",
            )
            for type_name, func in func_list:
                func_ani_info = GlobFuncANIInfo.get(self.am, func)
                sts_native_call = func_ani_info.call_native_with(sts_real_args)
                target.writeln(
                    f'        case "{type_name}": return {sts_native_call};',
                )
            target.writeln(
                f"        default: throw new Error(`Unknown type: ${{type}}`);",
                f"    }}",
                f"}}",
            )
        # other
        for func in funcs:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            sts_real_params = []
            sts_real_args = []
            for sts_real_param in func_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(
                    self.am, pkg, sts_real_param.ty_ref.resolved_ty
                )
                sts_real_params.append(
                    f"{sts_real_param.name}: {type_ani_info.sts_type_in(pkg, target)}"
                )
                sts_real_args.append(sts_real_param.name)
            sts_real_params_str = ", ".join(sts_real_params)
            sts_native_call = func_ani_info.call_native_with(sts_real_args)
            if return_ty_ref := func.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, pkg, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type_in(pkg, target)
            else:
                sts_return_ty_name = "void"
            # real
            if func_ani_info.sts_func_name is not None:
                target.writeln(
                    f"export function {func_ani_info.sts_func_name}({sts_real_params_str}): {sts_return_ty_name} {{",
                    f"    return {sts_native_call};",
                    f"}}",
                )
                # promise
                if (promise_func_name := func_ani_info.sts_promise_name) is not None:
                    if return_ty_ref := func.return_ty_ref:
                        resolve_args = f"ret as {sts_return_ty_name}"
                    else:
                        resolve_args = "undefined"
                    target.writeln(
                        f"export function {promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}> {{",
                        f"    return new Promise<{sts_return_ty_name}>((resolve, reject): void => {{",
                        f"        taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})",
                        f"        .then((ret: NullishType): void => {{",
                        f"            resolve({resolve_args});",
                        f"        }})",
                        f"        .catch((ret: NullishType): void => {{",
                        f"            reject(ret as Error);",
                        f"        }});",
                        f"    }});",
                        f"}}",
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
                    target.writeln(
                        f"export function {async_func_name}({sts_real_params_with_cb_str}): void {{",
                        f"    taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})",
                        f"    .then((ret: NullishType): void => {{",
                        f"        callback({then_args});",
                        f"    }})",
                        f"    .catch((ret: NullishType): void => {{",
                        f"        callback(ret as Error);",
                        f"    }});",
                        f"}}",
                    )

    def gen_enum(
        self,
        pkg: PackageDecl,
        enum: EnumDecl,
        target: STSOutputBuffer,
    ):
        enum_ani_info = EnumANIInfo.get(self.am, enum)
        if enum_ani_info.const:
            assert enum.ty_ref
            type_ani_info = TypeANIInfo.get(self.am, pkg, enum.ty_ref.resolved_ty)
            for item in enum.items:
                target.writeln(
                    f"export const {item.name}: {type_ani_info.sts_type_in(pkg, target)} = {dumps(item.value)};",
                )
            return
        target.writeln(
            f"export enum {enum_ani_info.sts_type_name} {{",
        )
        with target.indent_manager.offset(4):
            for item in enum.items:
                if item.value is None:
                    target.writeln(
                        f"{item.name},",
                    )
                else:
                    target.writeln(
                        f"{item.name} = {dumps(item.value)},",
                    )
        target.writeln(
            f"}}",
        )

    def gen_union(
        self,
        pkg: PackageDecl,
        union: UnionDecl,
        target: STSOutputBuffer,
    ):
        union_ani_info = UnionANIInfo.get(self.am, union)
        sts_types = []
        for field in union.fields:
            if field.ty_ref is None:
                sts_types.append("null")
                continue
            ty_ani_info = TypeANIInfo.get(self.am, pkg, field.ty_ref.resolved_ty)
            sts_types.append(f"{ty_ani_info.sts_type_in(pkg, target)}")
        sts_types_str = " | ".join(sts_types)
        target.writeln(
            f"export type {union_ani_info.sts_type_name} = {sts_types_str};",
        )

    def gen_struct_interface(
        self,
        pkg: PackageDecl,
        struct: StructDecl,
        target: STSOutputBuffer,
    ):
        struct_ani_info = StructANIInfo.get(self.am, struct)
        if struct_ani_info.is_class():
            # no interface
            return
        parents = []
        for parent in struct_ani_info.sts_parents:
            ty = parent.ty_ref.resolved_ty
            assert isinstance(ty, StructType)
            parent_ani_info = StructANIInfo.get(self.am, ty.ty_decl)
            parents.append(parent_ani_info.sts_type_name)
        extends_str = " extends " + ", ".join(parents) if parents else ""
        target.writeln(
            f"export interface {struct_ani_info.sts_type_name}{extends_str} {{",
        )
        with target.indent_manager.offset(4):
            for field in struct_ani_info.sts_fields:
                ty_ani_info = TypeANIInfo.get(self.am, pkg, field.ty_ref.resolved_ty)
                target.writeln(
                    f"{field.name}: {ty_ani_info.sts_type_in(pkg, target)};",
                )
        target.writeln(
            f"}}",
        )

    def gen_struct_class(
        self,
        pkg: PackageDecl,
        struct: StructDecl,
        target: STSOutputBuffer,
    ):
        struct_ani_info = StructANIInfo.get(self.am, struct)
        if struct_ani_info.is_class():
            parents = []
            for parent in struct_ani_info.sts_parents:
                ty = parent.ty_ref.resolved_ty
                assert isinstance(ty, StructType)
                parent_ani_info = StructANIInfo.get(self.am, ty.ty_decl)
                parents.append(parent_ani_info.sts_type_name)
            implements_str = " implements " + ", ".join(parents) if parents else ""
            target.writeln(
                f"export class {struct_ani_info.sts_impl_name}{implements_str} {{",
            )
        else:
            target.writeln(
                f"class {struct_ani_info.sts_impl_name} implements {struct_ani_info.sts_type_name} {{",
            )
        with target.indent_manager.offset(4):
            for parts in struct_ani_info.sts_final_fields:
                final = parts[-1]
                ty_ani_info = TypeANIInfo.get(self.am, pkg, final.ty_ref.resolved_ty)
                target.writeln(
                    f"{final.name}: {ty_ani_info.sts_type_in(pkg, target)};",
                )
            target.writeln(
                f"constructor(",
            )
            for parts in struct_ani_info.sts_final_fields:
                final = parts[-1]
                ty_ani_info = TypeANIInfo.get(self.am, pkg, final.ty_ref.resolved_ty)
                target.writeln(
                    f"    {final.name}: {ty_ani_info.sts_type_in(pkg, target)},",
                )
            target.writeln(
                f") {{",
            )
            for parts in struct_ani_info.sts_final_fields:
                final = parts[-1]
                target.writeln(
                    f"    this.{final.name} = {final.name};",
                )
            target.writeln(
                f"}}",
            )
        target.writeln(
            f"}}",
        )

    def gen_iface_interface(
        self,
        pkg: PackageDecl,
        iface: IfaceDecl,
        target: STSOutputBuffer,
    ):
        iface_ani_info = IfaceANIInfo.get(self.am, iface)
        if iface_ani_info.is_class():
            # no interface
            return
        parents = []
        for parent in iface.parents:
            ty = parent.ty_ref.resolved_ty
            assert isinstance(ty, IfaceType)
            parent_ani_info = IfaceANIInfo.get(self.am, ty.ty_decl)
            parents.append(parent_ani_info.sts_type_name)
        extends_str = " extends " + ", ".join(parents) if parents else ""
        target.writeln(
            f"export interface {iface_ani_info.sts_type_name}{extends_str} {{",
        )
        with target.indent_manager.offset(4):
            # TODO: hack inject
            for injected in iface_ani_info.iface_injected_codes:
                target.writeln(injected)
            self.gen_iface_methods_decl(pkg, iface.methods, target)
        target.writeln(
            f"}}",
        )

    def gen_iface_methods_decl(
        self,
        pkg: PackageDecl,
        methods: list[IfaceMethodDecl],
        target: STSOutputBuffer,
    ):
        # on_off
        method_on_off_map = self.stat_on_off_methods(methods)
        for (
            method_name,
            real_params_ty,
            return_ty,
        ), _ in method_on_off_map.items():
            sts_real_params = []
            sts_real_params.append("type: string")
            for index, param_ty in enumerate(real_params_ty):
                type_ani_info = TypeANIInfo.get(self.am, pkg, param_ty)
                param_name = f"p_{index}"
                sts_real_params.append(
                    f"{param_name}: {type_ani_info.sts_type_in(pkg, target)}"
                )
            if return_ty:
                type_ani_info = TypeANIInfo.get(self.am, pkg, return_ty)
                return_ty_str = type_ani_info.sts_type_in(pkg, target)
            else:
                return_ty_str = "void"
            sts_real_params_str = ", ".join(sts_real_params)
            target.writeln(
                f"{method_name}({sts_real_params_str}): {return_ty_str};",
            )
        # other
        for method in methods:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            sts_real_params = []
            for real_param in method_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(
                    self.am, pkg, real_param.ty_ref.resolved_ty
                )
                sts_real_params.append(
                    f"{real_param.name}: {type_ani_info.sts_type_in(pkg, target)}"
                )
            sts_real_params_str = ", ".join(sts_real_params)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, pkg, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type_in(pkg, target)
            else:
                sts_return_ty_name = "void"
            # real
            if real_method := method_ani_info.sts_method_name:
                target.writeln(
                    f"{real_method}({sts_real_params_str}): {sts_return_ty_name};",
                )
                # promise
                if (promise_func_name := method_ani_info.sts_promise_name) is not None:
                    target.writeln(
                        f"{promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}>;",
                    )
                # async
                if (async_func_name := method_ani_info.sts_async_name) is not None:
                    if return_ty_ref := method.return_ty_ref:
                        callback = f"callback: (err: Error, data?: {sts_return_ty_name}) => void"
                    else:
                        callback = "callback: (err: Error) => void"
                    sts_real_params_with_cb = [*sts_real_params, callback]
                    sts_real_params_with_cb_str = ", ".join(sts_real_params_with_cb)
                    target.writeln(
                        f"{async_func_name}({sts_real_params_with_cb_str}): void;",
                    )
            # getter
            if get_name := method_ani_info.get_name:
                target.writeln(
                    f"get {get_name}({sts_real_params_str}): {sts_return_ty_name};",
                )
            # setter
            if set_name := method_ani_info.set_name:
                target.writeln(
                    f"set {set_name}({sts_real_params_str});",
                )

    def gen_iface_class(
        self,
        pkg: PackageDecl,
        iface: IfaceDecl,
        target: STSOutputBuffer,
        statics_map: dict[str, list[GlobFuncDecl]],
        ctors_map: dict[str, list[GlobFuncDecl]],
    ):
        iface_ani_info = IfaceANIInfo.get(self.am, iface)
        if iface_ani_info.is_class():
            parents = []
            for parent in iface.parents:
                ty = parent.ty_ref.resolved_ty
                assert isinstance(ty, IfaceType)
                parent_ani_info = IfaceANIInfo.get(self.am, ty.ty_decl)
                parents.append(parent_ani_info.sts_type_name)
            implements_str = " implements " + ", ".join(parents) if parents else ""
            target.writeln(
                f"export class {iface_ani_info.sts_impl_name}{implements_str} {{",
            )
        else:
            target.writeln(
                f"class {iface_ani_info.sts_impl_name} implements {iface_ani_info.sts_type_name} {{",
            )
        with target.indent_manager.offset(4):
            # TODO: hack inject
            for injected in iface_ani_info.class_injected_codes:
                target.writeln(injected)
            target.writeln(
                f"private _vtbl_ptr: long;",
                f"private _data_ptr: long;",
                f"private constructor(_vtbl_ptr: long, _data_ptr: long) {{",
                f"    this._vtbl_ptr = _vtbl_ptr;",
                f"    this._data_ptr = _data_ptr;",
                f"    localDestroyRegister.register(this, this._data_ptr)",
                f"}}",
            )
            ctors = ctors_map.get(iface.name, [])
            for tor in ctors:
                ctor_ani_info = GlobFuncANIInfo.get(self.am, tor)
                sts_real_params = []
                sts_real_args = []
                for sts_real_param in ctor_ani_info.sts_real_params:
                    type_ani_info = TypeANIInfo.get(
                        self.am, pkg, sts_real_param.ty_ref.resolved_ty
                    )
                    sts_real_params.append(
                        f"{sts_real_param.name}: {type_ani_info.sts_type_in(pkg, target)}"
                    )
                    sts_real_args.append(sts_real_param.name)
                sts_real_params_str = ", ".join(sts_real_params)
                sts_native_call = ctor_ani_info.call_native_with(sts_real_args)
                target.writeln(
                    f"constructor({sts_real_params_str}) {{",
                    f"    let temp = {sts_native_call} as {iface_ani_info.sts_impl_name};",
                    f"    this._data_ptr = temp._data_ptr;",
                    f"    this._vtbl_ptr = temp._vtbl_ptr;",
                    f"}}",
                )
            self.gen_static_funcs(pkg, statics_map.get(iface.name, []), target)
            iface_abi_info = IfaceABIInfo.get(self.am, iface)
            for ancestor in iface_abi_info.ancestor_dict:
                self.gen_native_methods(pkg, ancestor.methods, target)
                self.gen_iface_methods(pkg, ancestor.methods, target)
        target.writeln(
            f"}}",
        )

    def gen_static_funcs(
        self,
        pkg: PackageDecl,
        funcs: list[GlobFuncDecl],
        target: STSOutputBuffer,
    ):
        # on_off
        func_on_off_map = self.stat_on_off_funcs(funcs)
        for (
            func_name,
            real_params_ty,
            return_ty,
        ), func_list in func_on_off_map.items():
            sts_real_params = []
            sts_real_args = []
            sts_real_params.append("type: string")
            for index, param_ty in enumerate(real_params_ty):
                type_ani_info = TypeANIInfo.get(self.am, pkg, param_ty)
                param_name = f"p_{index}"
                sts_real_params.append(
                    f"{param_name}: {type_ani_info.sts_type_in(pkg, target)}"
                )
                sts_real_args.append(param_name)
            sts_real_params_str = ", ".join(sts_real_params)
            if return_ty:
                type_ani_info = TypeANIInfo.get(self.am, pkg, return_ty)
                return_ty_str = type_ani_info.sts_type_in(pkg, target)
            else:
                return_ty_str = "void"
            target.writeln(
                f"static {func_name}({sts_real_params_str}): {return_ty_str} {{",
                f"    switch(type) {{",
            )
            for type_name, func in func_list:
                func_ani_info = GlobFuncANIInfo.get(self.am, func)
                sts_native_call = func_ani_info.call_native_with(sts_real_args)
                target.writeln(
                    f'        case "{type_name}": return {sts_native_call};',
                )
            target.writeln(
                f"        default: throw new Error(`Unknown type: ${{type}}`);",
                f"    }}",
                f"}}",
            )
        # other
        for func in funcs:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            sts_real_params = []
            sts_real_args = []
            for sts_real_param in func_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(
                    self.am, pkg, sts_real_param.ty_ref.resolved_ty
                )
                sts_real_params.append(
                    f"{sts_real_param.name}: {type_ani_info.sts_type_in(pkg, target)}"
                )
                sts_real_args.append(sts_real_param.name)
            sts_real_params_str = ", ".join(sts_real_params)
            sts_native_call = func_ani_info.call_native_with(sts_real_args)
            if return_ty_ref := func.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, pkg, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type_in(pkg, target)
            else:
                sts_return_ty_name = "void"
            # real
            if func_ani_info.sts_func_name is not None:
                target.writeln(
                    f"static {func_ani_info.sts_func_name}({sts_real_params_str}): {sts_return_ty_name} {{",
                    f"    return {sts_native_call};",
                    f"}}",
                )
                # promise
                if (promise_func_name := func_ani_info.sts_promise_name) is not None:
                    if return_ty_ref := func.return_ty_ref:
                        resolve_args = f"ret as {sts_return_ty_name}"
                    else:
                        resolve_args = "undefined"
                    target.writeln(
                        f"static {promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}> {{",
                        f"    return new Promise<{sts_return_ty_name}>((resolve, reject): void => {{",
                        f"        taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})",
                        f"        .then((ret: NullishType): void => {{",
                        f"            resolve({resolve_args});",
                        f"        }})",
                        f"        .catch((ret: NullishType): void => {{",
                        f"            reject(ret as Error);",
                        f"        }});",
                        f"    }});",
                        f"}}",
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
                    target.writeln(
                        f"static {async_func_name}({sts_real_params_with_cb_str}): void {{",
                        f"    taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})",
                        f"    .then((ret: NullishType): void => {{",
                        f"        callback({then_args});",
                        f"    }})",
                        f"    .catch((ret: NullishType): void => {{",
                        f"        callback(ret as Error);",
                        f"    }});",
                        f"}}",
                    )
            # getter
            if get_name := func_ani_info.get_name:
                target.writeln(
                    f"static get {get_name}({sts_real_params_str}): {sts_return_ty_name} {{",
                    f"    return {sts_native_call};",
                    f"}}",
                )
            # setter
            if set_name := func_ani_info.set_name:
                target.writeln(
                    f"static set {set_name}({sts_real_params_str}) {{",
                    f"    return {sts_native_call};",
                    f"}}",
                )

    def gen_native_methods(
        self,
        pkg: PackageDecl,
        methods: list[IfaceMethodDecl],
        target: STSOutputBuffer,
    ):
        # native
        for method in methods:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            sts_native_params = []
            for param in method.params:
                type_ani_info = TypeANIInfo.get(self.am, pkg, param.ty_ref.resolved_ty)
                sts_native_params.append(
                    f"{param.name}: {type_ani_info.sts_type_in(pkg, target)}"
                )
            sts_native_params_str = ", ".join(sts_native_params)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, pkg, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type_in(pkg, target)
            else:
                sts_return_ty_name = "void"
            target.writeln(
                f"native {method_ani_info.sts_native_name}({sts_native_params_str}): {sts_return_ty_name};",
            )

    def gen_iface_methods(
        self,
        pkg: PackageDecl,
        methods: list[IfaceMethodDecl],
        target: STSOutputBuffer,
    ):
        # on_off
        method_on_off_map = self.stat_on_off_methods(methods)
        for (
            method_name,
            real_params_ty,
            return_ty,
        ), method_list in method_on_off_map.items():
            sts_real_params = []
            sts_real_args = []
            sts_real_params.append("type: string")
            for index, param_ty in enumerate(real_params_ty):
                type_ani_info = TypeANIInfo.get(self.am, pkg, param_ty)
                param_name = f"p_{index}"
                sts_real_params.append(
                    f"{param_name}: {type_ani_info.sts_type_in(pkg, target)}"
                )
                sts_real_args.append(param_name)
            sts_real_params_str = ", ".join(sts_real_params)
            if return_ty:
                type_ani_info = TypeANIInfo.get(self.am, pkg, return_ty)
                return_ty_str = type_ani_info.sts_type_in(pkg, target)
            else:
                return_ty_str = "void"
            target.writeln(
                f"{method_name}({sts_real_params_str}): {return_ty_str} {{",
                f"    switch(type) {{",
            )
            for type_name, method in method_list:
                method_ani_info = IfaceMethodANIInfo.get(self.am, method)
                sts_native_call = method_ani_info.call_native_with(
                    "this", sts_real_args
                )
                target.writeln(
                    f'        case "{type_name}": return {sts_native_call};',
                )
            target.writeln(
                f"        default: throw new Error(`Unknown type: ${{type}}`);",
                f"    }}",
                f"}}",
            )
        # other
        for method in methods:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            sts_real_params = []
            sts_real_args = []
            for sts_real_param in method_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(
                    self.am, pkg, sts_real_param.ty_ref.resolved_ty
                )
                sts_real_params.append(
                    f"{sts_real_param.name}: {type_ani_info.sts_type_in(pkg, target)}"
                )
                sts_real_args.append(sts_real_param.name)
            sts_real_params_str = ", ".join(sts_real_params)
            sts_native_call = method_ani_info.call_native_with("this", sts_real_args)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, pkg, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type_in(pkg, target)
            else:
                sts_return_ty_name = "void"
            # real
            if real_method := method_ani_info.sts_method_name:
                target.writeln(
                    f"{real_method}({sts_real_params_str}): {sts_return_ty_name} {{",
                    f"    return {sts_native_call};",
                    f"}}",
                )
                # promise
                if (promise_func_name := method_ani_info.sts_promise_name) is not None:
                    if return_ty_ref := method.return_ty_ref:
                        resolve_args = f"ret as {sts_return_ty_name}"
                    else:
                        resolve_args = "undefined"
                    target.writeln(
                        f"{promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}> {{",
                        f"    return new Promise<{sts_return_ty_name}>((resolve, reject): void => {{",
                        f"        taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})",
                        f"        .then((ret: NullishType): void => {{",
                        f"            resolve({resolve_args});",
                        f"        }})",
                        f"        .catch((ret: NullishType): void => {{",
                        f"            reject(ret as Error);",
                        f"        }});",
                        f"    }});",
                        f"}}",
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
                    target.writeln(
                        f"{async_func_name}({sts_real_params_with_cb_str}): void {{",
                        f"    taskpool.execute((): {sts_return_ty_name} => {{ return {sts_native_call}; }})",
                        f"    .then((ret: NullishType): void => {{",
                        f"        callback({then_args});",
                        f"    }})",
                        f"    .catch((ret: NullishType): void => {{",
                        f"        callback(ret as Error);",
                        f"    }});",
                        f"}}",
                    )
            # getter
            if get_name := method_ani_info.get_name:
                target.writeln(
                    f"get {get_name}({sts_real_params_str}): {sts_return_ty_name} {{",
                    f"    return {sts_native_call};",
                    f"}}",
                )
            # setter
            if set_name := method_ani_info.set_name:
                target.writeln(
                    f"set {set_name}({sts_real_params_str}) {{",
                    f"    return {sts_native_call};",
                    f"}}",
                )
