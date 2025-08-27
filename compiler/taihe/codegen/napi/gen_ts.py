from collections.abc import Collection
from json import dumps

from taihe.codegen.abi.analyses import IfaceAbiInfo
from taihe.codegen.ani.attributes import ReadOnlyAttr
from taihe.codegen.napi.analyses import (
    EnumNapiInfo,
    GlobFuncNapiInfo,
    IfaceMethodNapiInfo,
    IfaceNapiInfo,
    Namespace,
    PackageGroupNapiInfo,
    StructNapiInfo,
    TypeNapiInfo,
    UnionFieldNapiInfo,
    UnionNapiInfo,
)
from taihe.codegen.napi.attributes import LibAttr
from taihe.codegen.napi.writer import DtsWriter
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
from taihe.semantics.types import Type
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import FileKind, OutputManager


def check_lib(ns: Namespace) -> bool:
    for pkg in ns.packages:
        if LibAttr.get(pkg):
            return True
    return any(check_lib(child_ns) for child_ns_name, child_ns in ns.children.items())


class TsCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
        for module, ns in pg_napi_info.module_dict.items():
            self.gen_module_file(module, ns)

    def gen_module_file(self, module: str, ns: Namespace):
        if check_lib(ns):
            with DtsWriter(
                self.oc,
                f"proxy/{module}.ts",
                FileKind.TS,
            ) as target:
                native_lib_name = "_taihe_native_lib"
                self.gen_namespace(ns, target, native_lib_name)

    def gen_namespace(self, ns: Namespace, target: DtsWriter, native_lib_name: str):
        for head in ns.ts_injected_heads:
            target.write_block(head)
        for code in ns.ts_injected_codes:
            target.write_block(code)
        for pkg in ns.packages:
            if attr := LibAttr.get(pkg):
                lib_name = attr.lib_name
                # TODO: hack to decide require/import
                if lib_name[-3:] == ".so":
                    target.writelns(
                        f"import * as _taihe_native_lib from '{lib_name}';",
                    )
                else:
                    target.writelns(
                        f"const _taihe_native_lib = require('{lib_name}');",
                    )
                self.gen_package(pkg, target, native_lib_name)

        for child_ns_name, child_ns in ns.children.items():
            dts_decl = f"namespace {child_ns_name}"
            dts_decl = f"export {dts_decl}"
            with target.indented(
                f"{dts_decl} {{",
                f"}}",
            ):
                native_lib_name = f"{native_lib_name}.{child_ns_name}"
                self.gen_namespace(child_ns, target, native_lib_name)

    def gen_package(self, pkg: PackageDecl, target: DtsWriter, native_lib_name: str):
        for func in pkg.functions:
            func_napi_info = GlobFuncNapiInfo.get(self.am, func)
            if (
                func_napi_info.ctor_class_name is None
                and func_napi_info.static_class_name is None
            ):
                self.gen_func(func, target, native_lib_name)
        for struct in pkg.structs:
            self.gen_struct_interface(struct, target, native_lib_name)
            self.gen_struct_class(struct, target, native_lib_name)
        for iface in pkg.interfaces:
            self.gen_iface_interface(iface, target, native_lib_name)
        for enum in pkg.enums:
            self.gen_enum(enum, target)
        for union in pkg.unions:
            self.gen_union(union, target)

    def gen_func(self, func: GlobFuncDecl, target: DtsWriter, native_lib_name: str):
        target.writelns(
            f"export const {func.name} = {native_lib_name}.{func.name};",
        )

    def gen_struct_interface(
        self,
        struct: StructDecl,
        target: DtsWriter,
        native_lib_name: str,
    ):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        if struct_napi_info.is_class():
            # no interface
            return

        struct_decl = f"interface {struct_napi_info.dts_type_name}"
        if struct_napi_info.dts_iface_parents:
            parents = []
            for parent in struct_napi_info.dts_iface_parents:
                parent_ty = parent.ty_ref.resolved_ty
                parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(target))
            extends_str = ", ".join(parents) if parents else ""
            struct_decl = f"{struct_decl} extends {extends_str}"
        struct_decl = f"export {struct_decl}"

        with target.indented(
            f"{struct_decl} {{",
            f"}}",
        ):
            for injected in struct_napi_info.interfacets_ts_injected_codes:
                target.write_block(injected)

            for field in struct_napi_info.dts_fields:
                readonly = "readonly " if ReadOnlyAttr.get(field) is not None else ""
                ty_napi_info = TypeNapiInfo.get(self.am, field.ty_ref.resolved_ty)
                target.writelns(
                    f"{readonly}{field.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)};"
                )

    def gen_struct_class(
        self,
        struct: StructDecl,
        target: DtsWriter,
        native_lib_name: str,
    ):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        if not struct_napi_info.is_class():
            return

        if not struct_napi_info.interfacets_ts_injected_codes:
            target.writelns(
                f"export const {struct_napi_info.dts_type_name} = {native_lib_name}.{struct_napi_info.dts_type_name};",
            )
            return

        struct_decl = f"class {struct_napi_info.dts_type_name}"
        if struct_napi_info.dts_iface_parents:
            parents = []
            for parent in struct_napi_info.dts_iface_parents:
                parent_ty = parent.ty_ref.resolved_ty
                parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(target))
            extends_str = ", ".join(parents) if parents else ""
            struct_decl = f"{struct_decl} implements {extends_str}"
        struct_decl = f"export {struct_decl}"

        with target.indented(
            f"{struct_decl} {{",
            f"}}",
        ):
            for injected in struct_napi_info.class_ts_injected_codes:
                target.write_block(injected)

            args = []
            for parts in struct_napi_info.dts_final_fields:
                final = parts[-1]
                readonly = "readonly " if ReadOnlyAttr.get(final) is not None else ""
                ty_napi_info = TypeNapiInfo.get(self.am, final.ty_ref.resolved_ty)
                target.writelns(
                    f"{readonly}{final.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)};"
                )
                args.append(
                    f"{final.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)}"
                )
            args_str = ", ".join(args)

            with target.indented(
                f"constructor({args_str}) {{",
                f"}}",
            ):
                for parts in struct_napi_info.dts_final_fields:
                    final = parts[-1]
                    target.writelns(f"this.{final.name} = {final.name};")

    def gen_iface_interface(
        self,
        iface: IfaceDecl,
        target: DtsWriter,
        native_lib_name: str,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        if iface_napi_info.is_class():
            self.gen_iface_class(iface, target, native_lib_name)
            return

        parents = []
        for parent in iface.parents:
            parent_ty = parent.ty_ref.resolved_ty
            parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
            parents.append(parent_napi_info.dts_type_in(target))
        extends_str = " extends " + ", ".join(parents) if parents else ""
        with target.indented(
            f"export interface {iface_napi_info.dts_type_name}{extends_str} {{",
            f"}}",
        ):
            for injected in iface_napi_info.interface_ts_injected_codes:
                target.write_block(injected)
            self.gen_iface_interface_methods_decl(iface.methods, target)

    def gen_iface_class(
        self,
        iface: IfaceDecl,
        target: DtsWriter,
        native_lib_name: str,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        iface_abi_info = IfaceAbiInfo.get(self.am, iface)

        if not iface_napi_info.class_ts_injected_codes:
            target.writelns(
                f"export const {iface_napi_info.dts_type_name} = {native_lib_name}.{iface_napi_info.dts_type_name};",
            )
            return

        iface_decl = f"class {iface_napi_info.dts_type_name}"
        if iface_napi_info.dts_iface_parents:
            parents = []
            for parent in iface_napi_info.dts_iface_parents:
                parent_ty = parent.ty_ref.resolved_ty
                parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(target))
            extends_str = ", ".join(parents) if parents else ""
            iface_decl = f"{iface_decl} implements {extends_str}"
        iface_decl = f"export {iface_decl}"

        nativa_class_name = f"native{iface_napi_info.dts_type_name}"
        with target.indented(
            f"{iface_decl} {{",
            f"}}",
        ):
            for injected in iface_napi_info.class_ts_injected_codes:
                target.write_block(injected)

            target.writelns(
                f"private {nativa_class_name};",
            )
            if ctor := iface_napi_info.ctor:
                params = []
                args = []
                for param in ctor.params:
                    type_napi_info = TypeNapiInfo.get(self.am, param.ty_ref.resolved_ty)
                    params.append(
                        f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                    )
                    args.append(param.name)
                params_str = ", ".join(params)
                args_str = ", ".join(args)
                with target.indented(
                    f"constructor({params_str}) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"this.{nativa_class_name} = new {native_lib_name}.{iface_napi_info.dts_type_name}({args_str});",
                    )
            for mng_name, static_func in iface_napi_info.static_funcs:
                params = []
                args = []
                for param in static_func.params:
                    value_ty = param.ty_ref.resolved_ty
                    param_dts_info = TypeNapiInfo.get(self.am, value_ty)
                    params.append(
                        f"{param.name}{'?' if param_dts_info.is_optional else ''}: {param_dts_info.dts_type_in(target)}"
                    )
                    args.append(param.name)
                params_str = ", ".join(params)
                args_str = ", ".join(args)
                if static_func.return_ty_ref:
                    return_ty_dts_info = TypeNapiInfo.get(
                        self.am, static_func.return_ty_ref.resolved_ty
                    )
                    return_ty = return_ty_dts_info.dts_return_type_in(target)
                else:
                    return_ty = "void"
                with target.indented(
                    f"static {static_func.name}({params_str}): {return_ty} {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return {native_lib_name}.{iface_napi_info.dts_type_name}.{static_func.name}({args_str});",
                    )
            for ancestor in iface_abi_info.ancestor_dict:
                self.gen_iface_class_methods_impl(
                    ancestor.methods, target, nativa_class_name
                )

    def gen_iface_interface_methods_decl(
        self,
        methods: Collection[IfaceMethodDecl],
        target: DtsWriter,
    ):
        for method in methods:
            iface_method_napi_info = IfaceMethodNapiInfo.get(self.am, method)
            dts_params = []
            for param in method.params:
                type_napi_info = TypeNapiInfo.get(self.am, param.ty_ref.resolved_ty)
                dts_params.append(
                    f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                )
            dts_params_str = ", ".join(dts_params)
            if return_ty_ref := method.return_ty_ref:
                type_napi_info = TypeNapiInfo.get(self.am, return_ty_ref.resolved_ty)
                dts_return_ty_name = ": " + type_napi_info.dts_return_type_in(target)
            else:
                dts_return_ty_name = ""
            if name := iface_method_napi_info.get_name:
                target.writelns(
                    f"get {name}({dts_params_str}){dts_return_ty_name};",
                )
            elif name := iface_method_napi_info.set_name:
                target.writelns(
                    f"set {name}({dts_params_str}){dts_return_ty_name};",
                )
            else:
                target.writelns(
                    f"{method.name}({dts_params_str}){dts_return_ty_name};",
                )

    def gen_iface_class_methods_impl(
        self,
        methods: Collection[IfaceMethodDecl],
        target: DtsWriter,
        nativa_class_name: str,
    ):
        for method in methods:
            iface_method_napi_info = IfaceMethodNapiInfo.get(self.am, method)
            params = []
            args = []
            for param in method.params:
                type_napi_info = TypeNapiInfo.get(self.am, param.ty_ref.resolved_ty)
                params.append(
                    f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                )
                args.append(param.name)
            params_str = ", ".join(params)
            args_str = ", ".join(args)
            if return_ty_ref := method.return_ty_ref:
                type_napi_info = TypeNapiInfo.get(self.am, return_ty_ref.resolved_ty)
                dts_return_ty_name = ": " + type_napi_info.dts_return_type_in(target)
            else:
                dts_return_ty_name = ""
            if name := iface_method_napi_info.get_name:
                with target.indented(
                    f"get {name}({params_str}){dts_return_ty_name} {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return this.{nativa_class_name}.{name};",
                    )
            elif name := iface_method_napi_info.set_name:
                with target.indented(
                    f"set {name}({params_str}){dts_return_ty_name} {{",
                    f"}}",
                ):
                    target.writelns(
                        f"this.{nativa_class_name}.{name} = {args_str};",
                    )
            else:
                with target.indented(
                    f"{method.name}({params_str}){dts_return_ty_name} {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return this.{nativa_class_name}.{method.name}({args_str});",
                    )

    def gen_enum(
        self,
        enum: EnumDecl,
        target: DtsWriter,
    ):
        enum_napi_info = EnumNapiInfo.get(self.am, enum)
        if enum_napi_info.is_literal:
            for item in enum.items:
                target.writelns(
                    f"export const {item.name} = {dumps(item.value)};",
                )
        else:
            with target.indented(
                f"export enum {enum_napi_info.dts_type_name} {{",
                f"}}",
            ):
                for item in enum.items:
                    if item.value is None:
                        target.writelns(
                            f"{item.name},",
                        )
                    else:
                        target.writelns(
                            f"{item.name} = {dumps(item.value)},",
                        )

    def gen_union(
        self,
        union: UnionDecl,
        target: DtsWriter,
    ):
        union_napi_info = UnionNapiInfo.get(self.am, union)
        dts_types = []
        for field in union.fields:
            field_napi_info = UnionFieldNapiInfo.get(self.am, field)
            match field_napi_info.field_ty:
                case "null":
                    dts_types.append("null")
                case "undefined":
                    dts_types.append("undefined")
                case field_ty if isinstance(field_ty, Type):
                    ty_napi_info = TypeNapiInfo.get(self.am, field_ty)
                    dts_types.append(ty_napi_info.dts_type_in(target))
        dts_types_str = " | ".join(dts_types)
        target.writelns(
            f"export type {union_napi_info.dts_type_name} = {dts_types_str};",
        )
