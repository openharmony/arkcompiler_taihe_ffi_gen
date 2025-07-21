from taihe.codegen.abi.analyses import (
    GlobFuncAbiInfo,
    PackageAbiInfo,
)
from taihe.codegen.abi.writer import CHeaderWriter
from taihe.codegen.cpp.analyses import (
    GlobFuncCppUserInfo,
    PackageCppInfo,
    PackageCppUserInfo,
    TypeCppInfo,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    PackageDecl,
    PackageGroup,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import FileKind, OutputManager


class CppUserHeadersGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_abi_info = PackageAbiInfo.get(self.am, pkg)
        pkg_cpp_info = PackageCppInfo.get(self.am, pkg)
        pkg_cpp_user_info = PackageCppUserInfo.get(self.am, pkg)
        with CHeaderWriter(
            self.om,
            f"include/{pkg_cpp_user_info.header}",
            FileKind.CPP_HEADER,
        ) as target:
            # types
            target.add_include(pkg_cpp_info.header)
            # functions
            target.add_include("taihe/common.hpp")
            target.add_include(pkg_abi_info.header)
            for func in pkg.functions:
                for param in func.params:
                    type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
                    target.add_include(*type_cpp_info.impl_headers)
                if return_ty_ref := func.return_ty_ref:
                    type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
                    target.add_include(*type_cpp_info.impl_headers)
                self.gen_func(func, target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        target: CHeaderWriter,
    ):
        func_abi_info = GlobFuncAbiInfo.get(self.am, func)
        func_cpp_user_info = GlobFuncCppUserInfo.get(self.am, func)
        params_cpp = []
        args_into_abi = []
        for param in func.params:
            type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
            params_cpp.append(f"{type_cpp_info.as_param} {param.name}")
            args_into_abi.append(type_cpp_info.pass_into_abi(param.name))
        params_cpp_str = ", ".join(params_cpp)
        args_into_abi_str = ", ".join(args_into_abi)
        abi_result = f"{func_abi_info.mangled_name}({args_into_abi_str})"
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            cpp_return_ty_name = type_cpp_info.as_owner
            cpp_result = type_cpp_info.return_from_abi(abi_result)
        else:
            cpp_return_ty_name = "void"
            cpp_result = abi_result
        with target.indented(
            f"namespace {func_cpp_user_info.namespace} {{",
            f"}}",
            indent="",
        ):
            with target.indented(
                f"inline {cpp_return_ty_name} {func_cpp_user_info.call_name}({params_cpp_str}) {{",
                f"}}",
            ):
                target.writelns(
                    f"return {cpp_result};",
                )
