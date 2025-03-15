import re
from collections.abc import Callable

from taihe.codegen.abi_generator import (
    GlobFuncABIInfo,
    IfaceABIInfo,
    PackageABIInfo,
    TypeABIInfo,
)
from taihe.codegen.cpp_generator import (
    IfaceMethodCppInfo,
    TypeCppInfo,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
)
from taihe.semantics.types import (
    IfaceType,
)
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import COutputBuffer, OutputManager


class PackageCppImplInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        self.header = f"{p.name}.impl.hpp"
        self.source = f"{p.name}.impl.cpp"


class GlobFuncCppImplInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        self.macro = f"TH_EXPORT_CPP_API_{f.name}"


class CppImplHeadersGenerator:
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
        pkg_cpp_impl_target.include(pkg_abi_info.header)
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
            pkg_cpp_impl_target.include(*type_cpp_info.impl_headers)
            args_from_abi.append(type_cpp_info.pass_from_abi(param.name))
            abi_params.append(f"{type_abi_info.as_param} {param.name}")
        args_from_abi_str = ", ".join(args_from_abi)
        abi_params_str = ", ".join(abi_params)
        cpp_result = f"{func_impl}({args_from_abi_str})"
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
            pkg_cpp_impl_target.include(*type_cpp_info.impl_headers)
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


class CppImplSourcesGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_cpp_impl_info = PackageCppImplInfo.get(self.am, pkg)
        pkg_cpp_impl_target = COutputBuffer.create(
            self.tm, f"temp/{pkg_cpp_impl_info.source}", False
        )
        pkg_cpp_impl_target.include(pkg_cpp_impl_info.header)
        pkg_cpp_impl_target.write(
            "// Please delete <stdexcept> include when you implement\n"
        )
        pkg_cpp_impl_target.include("stdexcept")
        self.gen_using_namespace(pkg_cpp_impl_target)
        self.gen_anonymous_namespace_block(
            pkg_cpp_impl_target,
            content_generator=lambda: [
                self.gen_iface(iface, pkg_cpp_impl_target) for iface in pkg.interfaces
            ]
            + [self.gen_func(func, pkg_cpp_impl_target) for func in pkg.functions],
        )
        for func in pkg.functions:
            self.gen_func_macro(func, pkg_cpp_impl_target)

    def gen_using_namespace(
        self,
        pkg_cpp_impl_target: COutputBuffer,
    ):

        pkg_cpp_impl_target.write(f"using namespace taihe::core;\n")

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_cpp_impl_target: COutputBuffer,
    ):
        func_cpp_impl_name = f"{func.name}"
        cpp_params = []
        for param in func.params:
            type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
            cpp_params.append(f"{self._mask(type_cpp_info.as_param)} {param.name}")
        cpp_params_str = ", ".join(cpp_params)
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            cpp_return_ty_name = self._mask(type_cpp_info.as_owner)
        else:
            cpp_return_ty_name = "void"
        pkg_cpp_impl_target.write(
            f"{cpp_return_ty_name} {func_cpp_impl_name}({cpp_params_str}) {{\n"
        )
        if return_ty_ref and isinstance(return_ty_ref.resolved_ty, IfaceType):
            pkg_cpp_impl_target.write(
                f"    return make_holder<{return_ty_ref.resolved_ty.ty_decl.name}, {cpp_return_ty_name}>();\n"
            )
        else:
            pkg_cpp_impl_target.write(
                f'    throw std::runtime_error("Function {func_cpp_impl_name} Not implemented");\n'
            )
        pkg_cpp_impl_target.write(f"}}\n")

    def gen_iface(
        self,
        iface: IfaceDecl,
        pkg_cpp_impl_target: COutputBuffer,
    ):
        perantsList = IfaceABIInfo.get(self.am, iface).ancestor_dict

        pkg_cpp_impl_target.write(f"class {iface.name} {{\n" f"public:\n")
        for ifaceperant in perantsList:
            for func in ifaceperant.methods:
                self._gen_class_method_impl(iface.name, func, pkg_cpp_impl_target)

        pkg_cpp_impl_target.write(f"}};\n\n")

    def _gen_class_method_impl(
        self,
        iface_name: str,
        func: IfaceMethodDecl,
        pkg_cpp_impl_target: COutputBuffer,
    ):
        method_cpp_info = IfaceMethodCppInfo.get(self.am, func)
        func_cpp_impl_name = method_cpp_info.impl_name
        cpp_params = []
        for param in func.params:
            type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
            cpp_params.append(f"{self._mask(type_cpp_info.as_param)} {param.name}")
        cpp_params_str = ", ".join(cpp_params)
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            cpp_return_ty_name = self._mask(type_cpp_info.as_owner)
        else:
            cpp_return_ty_name = "void"
        pkg_cpp_impl_target.write(
            f"    {cpp_return_ty_name} {func_cpp_impl_name}({cpp_params_str}) {{\n"
        )
        if return_ty_ref and isinstance(return_ty_ref.resolved_ty, IfaceType):
            pkg_cpp_impl_target.write(
                f"        return make_holder<{return_ty_ref.resolved_ty.ty_decl.name}, {cpp_return_ty_name}>();\n"
            )
        else:
            pkg_cpp_impl_target.write(
                f'        throw std::runtime_error("Function {iface_name}::{func_cpp_impl_name} Not implemented");\n'
            )
        pkg_cpp_impl_target.write(f"    }}\n")

    def _mask(
        self,
        input_str: str,
    ) -> str:
        prefix = "::taihe::core::"
        if input_str.startswith(prefix):
            input_str = input_str[len(prefix) :]

        input_str = re.sub(r"<\s*::taihe::core::", "<", input_str)

        input_str = re.sub(r",\s*::taihe::core::", ", ", input_str)

        input_str = re.sub(r"\(\s*::taihe::core::", "(", input_str)

        return input_str

    def gen_func_macro(
        self,
        func: GlobFuncDecl,
        pkg_cpp_impl_target: COutputBuffer,
    ):
        func_cpp_impl_info = GlobFuncCppImplInfo.get(self.am, func)
        func_cpp_impl_name = f"{func.name}"
        pkg_cpp_impl_target.write(f"{func_cpp_impl_info.macro}({func_cpp_impl_name})\n")

    def gen_anonymous_namespace_block(
        self,
        pkg_cpp_impl_target: COutputBuffer,
        content_generator: Callable[[], list[None]],
    ):
        pkg_cpp_impl_target.write(f"namespace {{\n\n")

        content_generator()

        pkg_cpp_impl_target.write(f"\n}}\n\n")
