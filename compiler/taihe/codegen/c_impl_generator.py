from taihe.codegen.abi_generator import (
    ABIFuncBaseDeclInfo,
    ABIPackageInfo,
    ABITypeInfo,
    COutputBuffer,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    Package,
    PackageGroup,
)
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager


class CImplPackageInfo(AbstractAnalysis[Package]):
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
        c_impl_pkg_info = CImplPackageInfo.get(self.am, pkg)
        c_impl_pkg_target = COutputBuffer.create(
            self.tm, f"include/{c_impl_pkg_info.header}", True
        )
        abi_pkg_info = ABIPackageInfo.get(self.am, pkg)

        c_impl_pkg_target.include("taihe/common.h")
        c_impl_pkg_target.include(f"{abi_pkg_info.header}")

        for func in pkg.functions:
            self.gen_func(func, c_impl_pkg_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        c_impl_pkg_target: COutputBuffer,
    ):
        abi_func_info = ABIFuncBaseDeclInfo.get(self.am, func)

        c_impl_pkg_target.include(abi_func_info.return_ty_header)

        params = []
        args = []
        for param in func.params:
            abi_type_info = ABITypeInfo.get(self.am, param.ty_ref.resolved_ty)
            params.append(f"{abi_type_info.as_param} {param.name}")
            args.append(param.name)
        params_str = ", ".join(params)
        args_str = ", ".join(args)
        c_impl_pkg_target.write(
            f"#define TH_EXPORT_C_API_{func.name}(_func) \\\n"
            f"  TH_STATIC_ASSERT(TH_IS_SAME(TH_TYPEOF(_func), {abi_func_info.return_ty_name} ({params_str})), \\\n"
            f"    \"'\" #_func \"' is incompatible with '{abi_func_info.return_ty_name} {abi_func_info.name}({params_str})'\"); \\\n"
            f"  {abi_func_info.return_ty_name} {abi_func_info.name}({params_str}) {{ \\\n"
            f"    return _func({args_str}); \\\n"
            f"  }}\n"
        )
