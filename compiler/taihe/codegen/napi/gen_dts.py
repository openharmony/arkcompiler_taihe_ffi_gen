from taihe.codegen.ani.writer import StsWriter
from taihe.codegen.napi.analyses import (
    IfaceNAPIInfo,
    PackageNAPIInfo,
    StructNAPIInfo,
    TypeNAPIInfo,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
    StructDecl,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputConfig


class DTSCodeGenerator:
    def __init__(self, oc: OutputConfig, am: AnalysisManager):
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
        ) as pkg_napi_target:
            for func in pkg.functions:
                self.gen_func(func, pkg_napi_target)
            for struct in pkg.structs:
                self.gen_struct_interface(struct, pkg_napi_target)
            for struct in pkg.structs:
                self.gen_struct_class(struct, pkg_napi_target)
            for iface in pkg.interfaces:
                self.gen_iface_interface(iface, pkg_napi_target)

    def gen_func(self, func: GlobFuncDecl, pkg_dts_target: StsWriter):
        args = []
        for i, param in enumerate(func.params):
            value_ty = param.ty_ref.resolved_ty
            param_dts_info = TypeNAPIInfo.get(self.am, value_ty)
            args.append(f"value{i}: {param_dts_info.dts_type_name}")
        args_str = ", ".join(args)
        if func.return_ty_ref:
            return_ty_dts_info = TypeNAPIInfo.get(
                self.am, func.return_ty_ref.resolved_ty
            )
            return_ty = return_ty_dts_info.dts_type_name
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
        with target.indented(
            f"export interface {struct_napi_info.dts_type_name} {{",
            f"}}",
        ):
            for field in struct_napi_info.sts_fields:
                ty_ani_info = TypeNAPIInfo.get(self.am, field.ty_ref.resolved_ty)
                target.writelns(
                    f"{field.name}: {ty_ani_info.dts_type_name};",
                )

    def gen_struct_class(
        self,
        struct: StructDecl,
        target: StsWriter,
    ):
        struct_napi_info = StructNAPIInfo.get(self.am, struct)
        if not struct_napi_info.is_class():
            return

        with target.indented(
            f"export class {struct_napi_info.dts_impl_name} {{",
            f"}}",
        ):
            for parts in struct_napi_info.sts_final_fields:
                final = parts[-1]
                ty_ani_info = TypeNAPIInfo.get(self.am, final.ty_ref.resolved_ty)
                target.writelns(f"{final.name}: {ty_ani_info.dts_type_name};")

            params = []
            for parts in struct_napi_info.sts_final_fields:
                final = parts[-1]
                ty_ani_info = TypeNAPIInfo.get(self.am, final.ty_ref.resolved_ty)
                params.append(f"{final.name}: {ty_ani_info.dts_type_name}")
            params_str = ", ".join(params)
            target.writelns(f"constructor({params_str});")

    def gen_iface_interface(
        self,
        iface: IfaceDecl,
        target: StsWriter,
    ):
        iface_napi_info = IfaceNAPIInfo.get(self.am, iface)
        if iface_napi_info.is_class():
            # no interface
            return
        with target.indented(
            f"export interface {iface_napi_info.dts_type_name} {{",
            f"}}",
        ):
            self.gen_iface_methods_decl(iface.methods, target)

    def gen_iface_methods_decl(
        self,
        methods: list[IfaceMethodDecl],
        target: StsWriter,
    ):
        sts_params = []
        for method in methods:
            for param in method.params:
                type_ani_info = TypeNAPIInfo.get(self.am, param.ty_ref.resolved_ty)
                sts_params.append(f"{param.name}: {type_ani_info.dts_type_name}")
            sts_params_str = ", ".join(sts_params)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeNAPIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.dts_type_name
            else:
                sts_return_ty_name = "void"
            target.writelns(
                f"{method.name}({sts_params_str}): {sts_return_ty_name};",
            )
