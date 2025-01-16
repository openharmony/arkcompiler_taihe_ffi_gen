from taihe.codegen.abi_generator import (
    COutputBuffer,
    GlobFuncDeclABIInfo,
    PackageABIInfo,
    TypeABIInfo,
)
from taihe.codegen.cpp_proj_generator import (
    GlobFuncDeclCppProjInfo,
    TypeCppProjInfo,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    Package,
    PackageGroup,
)
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager


class PackageCppImplInfo(AbstractAnalysis[Package]):
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
        pkg_cpp_impl_info = PackageCppImplInfo.get(self.am, pkg)
        pkg_cpp_impl_target = COutputBuffer.create(
            self.tm, f"include/{pkg_cpp_impl_info.header}", True
        )
        pkg_abi_info = PackageABIInfo.get(self.am, pkg)
        pkg_cpp_impl_target.include("taihe/common.hpp")
        pkg_cpp_impl_target.include(f"{pkg_abi_info.header}")
        for func in pkg.functions:
            self.gen_func(func, pkg_cpp_impl_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_cpp_impl_target: COutputBuffer,
    ):
        func_cpp_proj_info = GlobFuncDeclCppProjInfo.get(self.am, func)
        func_abi_info = GlobFuncDeclABIInfo.get(self.am, func)
        cpp_params = []
        args_from_abi = []
        abi_params = []
        for param in func.params:
            type_cpp_proj_info = TypeCppProjInfo.get(self.am, param.ty_ref.resolved_ty)
            type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_cpp_impl_target.include(*type_cpp_proj_info.defn_headers)
            cpp_params.append(f"{type_cpp_proj_info.as_param} {param.name}")
            args_from_abi.append(type_cpp_proj_info.pass_from_abi(param.name))
            abi_params.append(f"{type_abi_info.as_param} {param.name}")
        cpp_params_str = ", ".join(cpp_params)
        args_from_abi_str = ", ".join(args_from_abi)
        abi_params_str = ", ".join(abi_params)
        cpp_result = f"FUNC_IMPL({args_from_abi_str})"
        if return_ty_ref := func.return_ty_ref:
            type_cpp_proj_info = TypeCppProjInfo.get(self.am, return_ty_ref.resolved_ty)
            type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
            pkg_cpp_impl_target.include(*type_cpp_proj_info.defn_headers)
            abi_return_ty_name = type_abi_info.as_field
            cpp_return_ty_name = type_cpp_proj_info.as_owner
            abi_result = type_cpp_proj_info.return_into_abi(cpp_result)
        else:
            abi_return_ty_name = "void"
            cpp_return_ty_name = "void"
            abi_result = cpp_result
        pkg_cpp_impl_target.write(
            f"#define TH_EXPORT_CPP_API_{func.name}(FUNC_IMPL) \\\n"
            f"    /* TH_STATIC_ASSERT(TH_IS_SAME(TH_TYPEOF(FUNC_IMPL), {cpp_return_ty_name} ({cpp_params_str})), \\\n"
            f"       \"'\" #FUNC_IMPL \"' is incompatible with '{cpp_return_ty_name} {func_cpp_proj_info.name}({cpp_params_str})'\"); */ \\\n"
            f"    {abi_return_ty_name} {func_abi_info.mangled_name}({abi_params_str}) {{ \\\n"
            f"        return {abi_result}; \\\n"
            f"    }}\n"
        )
