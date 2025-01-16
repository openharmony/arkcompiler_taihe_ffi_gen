from taihe.codegen.abi_generator import (
    COutputBuffer,
    GlobFuncDeclABIInfo,
    PackageABIInfo,
    TypeABIInfo,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    Package,
    PackageGroup,
)
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager


class PackageCImplInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.impl.h"


class CImplCodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: Package):
        pkg_c_impl_info = PackageCImplInfo.get(self.am, pkg)
        pkg_c_impl_target = COutputBuffer.create(
            self.tm, f"include/{pkg_c_impl_info.header}", True
        )
        pkg_abi_info = PackageABIInfo.get(self.am, pkg)
        pkg_c_impl_target.include("taihe/common.h")
        pkg_c_impl_target.include(f"{pkg_abi_info.header}")
        for func in pkg.functions:
            self.gen_func(func, pkg_c_impl_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_c_impl_target: COutputBuffer,
    ):
        func_abi_info = GlobFuncDeclABIInfo.get(self.am, func)
        params = []
        args = []
        for param in func.params:
            type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_c_impl_target.include(*type_abi_info.defn_headers)
            params.append(f"{type_abi_info.as_param} {param.name}")
            args.append(param.name)
        params_str = ", ".join(params)
        args_str = ", ".join(args)
        if return_ty_ref := func.return_ty_ref:
            type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
            pkg_c_impl_target.include(*type_abi_info.defn_headers)
            return_ty_name = type_abi_info.as_field
        else:
            return_ty_name = "void"
        pkg_c_impl_target.write(
            f"#define TH_EXPORT_C_API_{func.name}(FUNC_IMPL) \\\n"
            f"  /* TH_STATIC_ASSERT(TH_IS_SAME(TH_TYPEOF(FUNC_IMPL), {return_ty_name} ({params_str})), \\\n"
            f"     \"'\" #FUNC_IMPL \"' is incompatible with '{return_ty_name} {func_abi_info.mangled_name}({params_str})'\"); */ \\\n"
            f"  {return_ty_name} {func_abi_info.mangled_name}({params_str}) {{ \\\n"
            f"    return FUNC_IMPL({args_str}); \\\n"
            f"  }}\n"
        )
