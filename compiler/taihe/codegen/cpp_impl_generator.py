from taihe.codegen.abi_generator import (
    ABIFuncBaseDeclInfo,
    ABIPackageInfo,
    ABITypeInfo,
    COutputBuffer,
)
from taihe.codegen.cpp_proj_generator import CppProjFuncBaseDeclInfo, CppProjTypeInfo
from taihe.semantics.declarations import (
    GlobFuncDecl,
    Package,
    PackageGroup,
)
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager


class CppImplPackageInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.impl.hpp"


class CppImplCodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: Package):
        cpp_impl_pkg_info = CppImplPackageInfo.get(self.am, pkg)
        cpp_impl_pkg_target = COutputBuffer.create(
            self.tm, f"include/{cpp_impl_pkg_info.header}", True
        )
        abi_pkg_info = ABIPackageInfo.get(self.am, pkg)

        cpp_impl_pkg_target.include("taihe/common.hpp")
        cpp_impl_pkg_target.include(f"{abi_pkg_info.header}")

        for func in pkg.functions:
            self.gen_func(func, cpp_impl_pkg_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        cpp_impl_pkg_target: COutputBuffer,
    ):
        cpp_proj_func_info = CppProjFuncBaseDeclInfo.get(self.am, func)
        abi_func_info = ABIFuncBaseDeclInfo.get(self.am, func)

        cpp_impl_pkg_target.include(*cpp_proj_func_info.return_ty_headers)

        cpp_params = []
        args_from_abi = []
        abi_params = []
        for param in func.params:
            cpp_proj_type_info = CppProjTypeInfo.get(self.am, param.ty_ref.resolved_ty)
            abi_type_info = ABITypeInfo.get(self.am, param.ty_ref.resolved_ty)
            cpp_impl_pkg_target.include(cpp_proj_type_info.header)
            cpp_params.append(f"{cpp_proj_type_info.as_param} {param.name}")
            args_from_abi.append(cpp_proj_type_info.pass_from_abi(param.name))
            abi_params.append(f"{abi_type_info.as_param} {param.name}")
        abi_params_str = ", ".join(abi_params)
        cpp_params_str = ", ".join(cpp_params)
        args_from_abi_str = ",".join(args_from_abi)

        cpp_impl_pkg_target.write(
            f"#define TH_EXPORT_CPP_API_{func.name}(_func) \\\n"
            f"    TH_STATIC_ASSERT(TH_IS_SAME(TH_TYPEOF(_func), {cpp_proj_func_info.return_ty_name} ({cpp_params_str})), \\\n"
            f"        \"'\" #_func \"' is incompatible with '{cpp_proj_func_info.return_ty_name} {cpp_proj_func_info.full_name}({cpp_params_str})'\"); \\\n"
            f"    {abi_func_info.return_ty_name} {abi_func_info.name}({abi_params_str}) {{ \\\n"
            f"        return {cpp_proj_func_info.return_into_abi(f'_func({args_from_abi_str})')}; \\\n"
            f"    }}\n"
        )
