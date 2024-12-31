from taihe.codegen.abi_generator import (
    BaseFuncDeclABIInfo,
    COutputBuffer,
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
        func_abi_info = BaseFuncDeclABIInfo.get(self.am, func)
        params = []
        args = []
        for param in func.params:
            type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_c_impl_target.include(type_abi_info.header)
            params.append(f"{type_abi_info.as_param} {param.name}")
            args.append(param.name)
        params_str = ", ".join(params)
        args_str = ", ".join(args)
        pkg_c_impl_target.include(func_abi_info.return_ty_header)
        pkg_c_impl_target.write(
            f"#define TH_EXPORT_C_API_{func.name}(_func) \\\n"
            f"  TH_STATIC_ASSERT(TH_IS_SAME(TH_TYPEOF(_func), {func_abi_info.return_ty_name} ({params_str})), \\\n"
            f"    \"'\" #_func \"' is incompatible with '{func_abi_info.return_ty_name} {func_abi_info.name}({params_str})'\"); \\\n"
            f"  {func_abi_info.return_ty_name} {func_abi_info.name}({params_str}) {{ \\\n"
            f"    return _func({args_str}); \\\n"
            f"  }}\n"
        )
