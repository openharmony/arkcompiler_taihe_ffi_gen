from taihe.codegen.abi_generator import (
    GlobFuncABIInfo,
    PackageABIInfo,
    TypeABIInfo,
)
from taihe.codegen.cpp_generator import (
    TypeCppInfo,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    PackageDecl,
    PackageGroup,
)
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import COutputBuffer, OutputManager


class PackageCppImplInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        self.header = f"{p.name}.impl.hpp"


class GlobFuncCppImplInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        self.macro = f"TH_EXPORT_CPP_API_{f.name}"


class CppImplCodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
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
        func_abi_info = GlobFuncABIInfo.get(self.am, func)
        func_cpp_impl_info = GlobFuncCppImplInfo.get(self.am, func)
        func_impl = "CPP_FUNC_IMPL"
        args_from_abi = []
        abi_params = []
        for param in func.params:
            type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
            type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_cpp_impl_target.include(*type_cpp_info.defn_headers)
            args_from_abi.append(type_cpp_info.pass_from_abi(param.name))
            abi_params.append(f"{type_abi_info.as_param} {param.name}")
        args_from_abi_str = ", ".join(args_from_abi)
        abi_params_str = ", ".join(abi_params)
        cpp_result = f"{func_impl}({args_from_abi_str})"
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
            pkg_cpp_impl_target.include(*type_cpp_info.defn_headers)
            abi_return_ty_name = type_abi_info.as_owner
            abi_result = type_cpp_info.return_into_abi(cpp_result)
        else:
            abi_return_ty_name = "void"
            abi_result = cpp_result
        pkg_cpp_impl_target.write(
            f"#define {func_cpp_impl_info.macro}({func_impl}) \\\n"
            f"    {abi_return_ty_name} {func_abi_info.mangled_name}({abi_params_str}) {{ \\\n"
            f"        return {abi_result}; \\\n"
            f"    }}\n"
        )
