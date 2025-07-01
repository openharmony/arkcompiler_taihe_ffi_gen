from collections.abc import Collection
from json import dumps

from taihe.codegen.ani.writer import StsWriter
from taihe.codegen.napi.analyses import (
    EnumNAPIInfo,
    IfaceNAPIInfo,
    PackageNAPIInfo,
    StructNAPIInfo,
    TypeNAPIInfo,
    UnionFieldNAPIInfo,
    UnionNAPIInfo,
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
from taihe.semantics.types import Type
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import FileKind, OutputManager


class DTSCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package(pkg)

    def gen_package(
        self,
        pkg: PackageDecl,
    ):
        pkg_napi_info = PackageNAPIInfo.get(self.am, pkg)
        with StsWriter(
            self.oc,
            f"{pkg_napi_info.ts_decl}",
            FileKind.ETS,
        ) as pkg_dts_target:
            for func in pkg.functions:
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

    def gen_func(self, func: GlobFuncDecl, pkg_dts_target: StsWriter):
        args = []
        for i, param in enumerate(func.params):
            value_ty = param.ty_ref.resolved_ty
            param_dts_info = TypeNAPIInfo.get(self.am, value_ty)
            args.append(
                f"value{i}{'?' if param_dts_info.is_optional else ''}: {param_dts_info.dts_type_in(pkg_dts_target)}"
            )
        args_str = ", ".join(args)
        if func.return_ty_ref:
            return_ty_dts_info = TypeNAPIInfo.get(
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
        target: StsWriter,
    ):
        struct_napi_info = StructNAPIInfo.get(self.am, struct)
        if struct_napi_info.is_class():
            # no interface
            return

        struct_decl = f"interface {struct_napi_info.dts_type_name}"
        if struct_napi_info.dts_iface_parents:
            parents = []
            for parent in struct_napi_info.dts_iface_parents:
                parent_ty = parent.ty_ref.resolved_ty
                parent_napi_info = TypeNAPIInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(target))
            extends_str = ", ".join(parents) if parents else ""
            struct_decl = f"{struct_decl} extends {extends_str}"
        struct_decl = f"export {struct_decl}"

        with target.indented(
            f"{struct_decl} {{",
            f"}}",
        ):
            for field in struct_napi_info.dts_fields:
                ty_napi_info = TypeNAPIInfo.get(self.am, field.ty_ref.resolved_ty)
                target.writelns(
                    f"{field.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)};"
                )

    def gen_struct_class(
        self,
        struct: StructDecl,
        target: StsWriter,
    ):
        struct_napi_info = StructNAPIInfo.get(self.am, struct)
        if not struct_napi_info.is_class():
            return

        struct_decl = f"declare class {struct_napi_info.dts_type_name}"
        if struct_napi_info.dts_iface_parents:
            parents = []
            for parent in struct_napi_info.dts_iface_parents:
                parent_ty = parent.ty_ref.resolved_ty
                parent_napi_info = TypeNAPIInfo.get(self.am, parent_ty)
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
                ty_napi_info = TypeNAPIInfo.get(self.am, final.ty_ref.resolved_ty)
                target.writelns(
                    f"{final.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)};"
                )
                params.append(
                    f"{final.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)}"
                )

            params_str = ", ".join(params)
            target.writelns(f"constructor({params_str});")

    def gen_iface_interface(
        self,
        iface: IfaceDecl,
        target: StsWriter,
    ):
        iface_napi_info = IfaceNAPIInfo.get(self.am, iface)
        if iface_napi_info.is_class():
            self.gen_iface_class(iface, target)
            return
        parents = []
        for parent in iface.parents:
            parent_ty = parent.ty_ref.resolved_ty
            parent_napi_info = TypeNAPIInfo.get(self.am, parent_ty)
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
        target: StsWriter,
    ):
        iface_napi_info = IfaceNAPIInfo.get(self.am, iface)
        with target.indented(
            f"export declare class {iface_napi_info.dts_type_name} {{",
            f"}}",
        ):
            if ctor := iface_napi_info.ctor:
                params = []
                for param in ctor.params:
                    type_napi_info = TypeNAPIInfo.get(self.am, param.ty_ref.resolved_ty)
                    params.append(f"{param.name}: {type_napi_info.dts_type_in(target)}")
                params_str = ", ".join(params)
                target.writelns(f"constructor({params_str});")

            self.gen_iface_methods_decl(iface.methods, target)

    def gen_iface_methods_decl(
        self,
        methods: Collection[IfaceMethodDecl],
        target: StsWriter,
    ):
        for method in methods:
            dts_params = []
            for param in method.params:
                type_napi_info = TypeNAPIInfo.get(self.am, param.ty_ref.resolved_ty)
                dts_params.append(
                    f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                )
            dts_params_str = ", ".join(dts_params)
            if return_ty_ref := method.return_ty_ref:
                type_napi_info = TypeNAPIInfo.get(self.am, return_ty_ref.resolved_ty)
                dts_return_ty_name = type_napi_info.dts_return_type_in(target)
            else:
                dts_return_ty_name = "void"
            target.writelns(
                f"{method.name}({dts_params_str}): {dts_return_ty_name};",
            )

    def gen_enum(
        self,
        enum: EnumDecl,
        target: StsWriter,
    ):
        enum_dts_info = EnumNAPIInfo.get(self.am, enum)
        with target.indented(
            f"export enum {enum_dts_info.dts_type_name} {{",
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
        target: StsWriter,
    ):
        union_napi_info = UnionNAPIInfo.get(self.am, union)
        dts_types = []
        for field in union.fields:
            field_napi_info = UnionFieldNAPIInfo.get(self.am, field)
            match field_napi_info.field_ty:
                case "null":
                    dts_types.append("null")
                case "undefined":
                    dts_types.append("undefined")
                case field_ty if isinstance(field_ty, Type):
                    ty_napi_info = TypeNAPIInfo.get(self.am, field_ty)
                    dts_types.append(ty_napi_info.dts_type_in(target))
        dts_types_str = " | ".join(dts_types)
        target.writelns(
            f"export type {union_napi_info.dts_type_name} = {dts_types_str};",
        )
