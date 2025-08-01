from collections.abc import Collection
from json import dumps

from taihe.codegen.ani.attributes import ReadOnlyAttr
from taihe.codegen.napi.analyses import (
    EnumNapiInfo,
    GlobFuncNapiInfo,
    IfaceNapiInfo,
    Namespace,
    PackageGroupNapiInfo,
    StructNapiInfo,
    TypeNapiInfo,
    UnionFieldNapiInfo,
    UnionNapiInfo,
)
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


class DtsCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
        for module, ns in pg_napi_info.module_dict.items():
            self.gen_module_file(module, ns)

    def gen_module_file(self, module: str, ns: Namespace):
        with DtsWriter(
            self.oc,
            f"{module}.d.ts",
            FileKind.DTS,
        ) as target:
            self.gen_namespace(ns, target)

    def gen_namespace(self, ns: Namespace, target: DtsWriter):
        for pkg in ns.packages:
            self.gen_package(pkg, target)
        for child_ns_name, child_ns in ns.children.items():
            dts_decl = f"namespace {child_ns_name}"
            dts_decl = f"export {dts_decl}"
            with target.indented(
                f"{dts_decl} {{",
                f"}}",
            ):
                self.gen_namespace(child_ns, target)

    def gen_package(self, pkg: PackageDecl, pkg_dts_target: DtsWriter):
        for func in pkg.functions:
            func_napi_info = GlobFuncNapiInfo.get(self.am, func)
            if (
                func_napi_info.ctor_class_name is None
                and func_napi_info.static_class_name is None
            ):
                self.gen_func(func, pkg_dts_target)
        for struct in pkg.structs:
            self.gen_struct_interface(struct, pkg_dts_target)
            self.gen_struct_class(struct, pkg_dts_target)
        for iface in pkg.interfaces:
            self.gen_iface_interface(iface, pkg_dts_target)
        for enum in pkg.enums:
            self.gen_enum(enum, pkg_dts_target)
        for union in pkg.unions:
            self.gen_union(union, pkg_dts_target)

    def gen_func(self, func: GlobFuncDecl, pkg_dts_target: DtsWriter):
        args = []
        for param in func.params:
            value_ty = param.ty_ref.resolved_ty
            param_dts_info = TypeNapiInfo.get(self.am, value_ty)
            args.append(
                f"{param.name}{'?' if param_dts_info.is_optional else ''}: {param_dts_info.dts_type_in(pkg_dts_target)}"
            )
        args_str = ", ".join(args)
        if func.return_ty_ref:
            return_ty_dts_info = TypeNapiInfo.get(
                self.am, func.return_ty_ref.resolved_ty
            )
            return_ty = return_ty_dts_info.dts_return_type_in(pkg_dts_target)
        else:
            return_ty = "void"
        pkg_dts_target.writelns(
            f"export function {func.name}({args_str}): {return_ty};",
        )

    def gen_struct_interface(
        self,
        struct: StructDecl,
        target: DtsWriter,
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
    ):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        if not struct_napi_info.is_class():
            return

        struct_decl = f"declare class {struct_napi_info.dts_type_name}"
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
            params = []
            for parts in struct_napi_info.dts_final_fields:
                final = parts[-1]
                readonly = "readonly " if ReadOnlyAttr.get(final) is not None else ""
                ty_napi_info = TypeNapiInfo.get(self.am, final.ty_ref.resolved_ty)
                target.writelns(
                    f"{readonly}{final.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)};"
                )
                params.append(
                    f"{final.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)}"
                )

            params_str = ", ".join(params)
            target.writelns(f"constructor({params_str});")

    def gen_iface_interface(
        self,
        iface: IfaceDecl,
        target: DtsWriter,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        if iface_napi_info.is_class():
            self.gen_iface_class(iface, target)
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
            self.gen_iface_methods_decl(iface.methods, target)

    def gen_iface_class(
        self,
        iface: IfaceDecl,
        target: DtsWriter,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        with target.indented(
            f"export declare class {iface_napi_info.dts_type_name} {{",
            f"}}",
        ):
            if ctor := iface_napi_info.ctor:
                params = []
                for param in ctor.params:
                    type_napi_info = TypeNapiInfo.get(self.am, param.ty_ref.resolved_ty)
                    params.append(
                        f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                    )
                params_str = ", ".join(params)
                target.writelns(f"constructor({params_str});")
            for mng_name, static_func in iface_napi_info.static_funcs:
                params = []
                for param in static_func.params:
                    value_ty = param.ty_ref.resolved_ty
                    param_dts_info = TypeNapiInfo.get(self.am, value_ty)
                    params.append(
                        f"{param.name}{'?' if param_dts_info.is_optional else ''}: {param_dts_info.dts_type_in(target)}"
                    )
                params_str = ", ".join(params)
                if static_func.return_ty_ref:
                    return_ty_dts_info = TypeNapiInfo.get(
                        self.am, static_func.return_ty_ref.resolved_ty
                    )
                    return_ty = return_ty_dts_info.dts_return_type_in(target)
                else:
                    return_ty = "void"
                target.writelns(
                    f"static {static_func.name}({params_str}): {return_ty};",
                )
            self.gen_iface_methods_decl(iface.methods, target)

    def gen_iface_methods_decl(
        self,
        methods: Collection[IfaceMethodDecl],
        target: DtsWriter,
    ):
        for method in methods:
            dts_params = []
            for param in method.params:
                type_napi_info = TypeNapiInfo.get(self.am, param.ty_ref.resolved_ty)
                dts_params.append(
                    f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                )
            dts_params_str = ", ".join(dts_params)
            if return_ty_ref := method.return_ty_ref:
                type_napi_info = TypeNapiInfo.get(self.am, return_ty_ref.resolved_ty)
                dts_return_ty_name = type_napi_info.dts_return_type_in(target)
            else:
                dts_return_ty_name = "void"
            target.writelns(
                f"{method.name}({dts_params_str}): {dts_return_ty_name};",
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
                    f"export declare const {item.name} = {dumps(item.value)};",
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
