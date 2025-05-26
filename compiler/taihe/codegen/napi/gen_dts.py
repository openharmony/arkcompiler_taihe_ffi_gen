from taihe.codegen.abi.writer import CSourceWriter
from taihe.codegen.napi.analyses import PackageNapiInfo, TypeNapiInfo
from taihe.semantics.declarations import (
    GlobFuncDecl,
    PackageDecl,
    PackageGroup,
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
        pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
        with CSourceWriter(
            self.oc,
            f"{pkg_napi_info.ts_decl}",
        ) as pkg_napi_target:
            for func in pkg.functions:
                self.gen_func(func, pkg_napi_target)

    def gen_func(self, func: GlobFuncDecl, pkg_dts_target: CSourceWriter):
        args = []
        for i, param in enumerate(func.params):
            value_ty = param.ty_ref.resolved_ty
            param_dts_info = TypeNapiInfo.get(self.am, value_ty)
            args.append(f"value{i}: {param_dts_info.dts_type}")
        args_str = ", ".join(args)
        if func.return_ty_ref:
            return_ty_dts_info = TypeNapiInfo.get(
                self.am, func.return_ty_ref.resolved_ty
            )
            return_ty = return_ty_dts_info.dts_type
        else:
            return_ty = "void"
        pkg_dts_target.writelns(
            f"export function {func.name}({args_str}): {return_ty};",
        )
