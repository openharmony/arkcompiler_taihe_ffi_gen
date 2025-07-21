import re

from taihe.codegen.abi.analyses import (
    GlobFuncAbiInfo,
    IfaceAbiInfo,
    PackageAbiInfo,
    TypeAbiInfo,
)
from taihe.codegen.abi.writer import CHeaderWriter, CSourceWriter
from taihe.codegen.cpp.analyses import (
    GlobFuncCppImplInfo,
    IfaceMethodCppInfo,
    PackageCppImplInfo,
    PackageCppInfo,
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
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import FileKind, OutputManager


class CppImplHeadersGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_abi_info = PackageAbiInfo.get(self.am, pkg)
        pkg_cpp_impl_info = PackageCppImplInfo.get(self.am, pkg)
        with CHeaderWriter(
            self.om,
            f"include/{pkg_cpp_impl_info.header}",
            FileKind.CPP_HEADER,
        ) as target:
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
        func_cpp_impl_info = GlobFuncCppImplInfo.get(self.am, func)
        func_impl = "CPP_FUNC_IMPL"
        args_from_abi = []
        abi_params = []
        for param in func.params:
            type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
            type_abi_info = TypeAbiInfo.get(self.am, param.ty_ref.resolved_ty)
            args_from_abi.append(type_cpp_info.pass_from_abi(param.name))
            abi_params.append(f"{type_abi_info.as_param} {param.name}")
        args_from_abi_str = ", ".join(args_from_abi)
        abi_params_str = ", ".join(abi_params)
        cpp_result = f"{func_impl}({args_from_abi_str})"
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            type_abi_info = TypeAbiInfo.get(self.am, return_ty_ref.resolved_ty)
            abi_return_ty_name = type_abi_info.as_owner
            abi_result = type_cpp_info.return_into_abi(cpp_result)
        else:
            abi_return_ty_name = "void"
            abi_result = cpp_result
        target.writelns(
            f"#define {func_cpp_impl_info.macro}({func_impl}) \\",
            f"    {abi_return_ty_name} {func_abi_info.mangled_name}({abi_params_str}) {{ \\",
            f"        return {abi_result}; \\",
            f"    }}",
        )


class CppImplSourcesGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am
        self.using_namespaces: list[str] = []

    @property
    def make_holder(self):
        return self.mask("taihe::make_holder")

    @property
    def runtime_error(self):
        return self.mask("std::runtime_error")

    def mask(self, cpp_type: str):
        pattern = r"(::)?([A-Za-z_][A-Za-z_0-9]*::)*[A-Za-z_][A-Za-z_0-9]*"

        def replace_ns(match):
            matched = match.group(0)
            for ns in self.using_namespaces:
                ns = ns + "::"
                if matched.startswith(ns):
                    return matched[len(ns) :]
                ns = "::" + ns
                if matched.startswith(ns):
                    return matched[len(ns) :]
            return matched

        return re.sub(pattern, replace_ns, cpp_type)

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_cpp_info = PackageCppInfo.get(self.am, pkg)
        pkg_cpp_impl_info = PackageCppImplInfo.get(self.am, pkg)
        with CSourceWriter(
            self.om,
            f"temp/{pkg_cpp_impl_info.source}",
            FileKind.TEMPLATE,
        ) as target:
            target.add_include(pkg_cpp_info.header)
            target.add_include(pkg_cpp_impl_info.header)
            target.add_include("taihe/runtime.hpp")
            target.add_include("stdexcept")
            target.newline()
            self.using_namespaces = []
            target.newline()
            self.gen_anonymous_namespace_block(pkg, target)
            target.newline()
            target.writelns(
                "// Since these macros are auto-generate, lint will cause false positive.",
                "// NOLINTBEGIN",
            )
            for func in pkg.functions:
                self.gen_func_macro(func, target)
            target.writelns(
                "// NOLINTEND",
            )
            self.using_namespaces = []

    def gen_using_namespace(
        self,
        target: CSourceWriter,
        namespace: str,
    ):
        target.writelns(
            f"using namespace {namespace};",
        )
        self.using_namespaces.append(namespace)

    def gen_anonymous_namespace_block(
        self,
        pkg: PackageDecl,
        target: CSourceWriter,
    ):
        with target.indented(
            f"namespace {{",
            f"}}  // namespace",
            indent="",
        ):
            target.writelns(
                f"// To be implemented.",
            )
            for iface in pkg.interfaces:
                target.newline()
                self.gen_iface(iface, target)
            for func in pkg.functions:
                target.newline()
                self.gen_func_impl(func, target)

    def gen_iface(
        self,
        iface: IfaceDecl,
        target: CSourceWriter,
    ):
        iface_abi_info = IfaceAbiInfo.get(self.am, iface)
        impl_name = f"{iface.name}Impl"
        with target.indented(
            f"class {impl_name} {{",
            f"}};",
        ):
            target.writelns(
                f"public:",
            )
            with target.indented(
                f"{impl_name}() {{",
                f"}}",
            ):
                target.writelns(
                    f"// Don't forget to implement the constructor.",
                )
            for ancestor in iface_abi_info.ancestor_dict:
                for func in ancestor.methods:
                    target.newline()
                    self.gen_method_impl(func, target)

    def gen_method_impl(
        self,
        func: IfaceMethodDecl,
        target: CSourceWriter,
    ):
        method_cpp_info = IfaceMethodCppInfo.get(self.am, func)
        func_cpp_impl_name = method_cpp_info.impl_name
        cpp_params = []
        for param in func.params:
            type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
            cpp_params.append(f"{self.mask(type_cpp_info.as_param)} {param.name}")
        cpp_params_str = ", ".join(cpp_params)
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            cpp_return_ty_name = self.mask(type_cpp_info.as_owner)
        else:
            cpp_return_ty_name = "void"
        with target.indented(
            f"{cpp_return_ty_name} {func_cpp_impl_name}({cpp_params_str}) {{",
            f"}}",
        ):
            if return_ty_ref and isinstance(return_ty_ref.resolved_ty, IfaceType):
                impl_name = f"{return_ty_ref.resolved_ty.ty_decl.name}Impl"
                target.writelns(
                    f"// The parameters in the make_holder function should be of the same type",
                    f"// as the parameters in the constructor of the actual implementation class.",
                    f"return {self.make_holder}<{impl_name}, {cpp_return_ty_name}>();",
                )
            else:
                target.writelns(
                    f'TH_THROW({self.runtime_error}, "{func_cpp_impl_name} not implemented");',
                )

    def gen_func_impl(
        self,
        func: GlobFuncDecl,
        target: CSourceWriter,
    ):
        func_cpp_impl_name = func.name
        cpp_params = []
        for param in func.params:
            type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
            cpp_params.append(f"{self.mask(type_cpp_info.as_param)} {param.name}")
        cpp_params_str = ", ".join(cpp_params)
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            cpp_return_ty_name = self.mask(type_cpp_info.as_owner)
        else:
            cpp_return_ty_name = "void"
        with target.indented(
            f"{cpp_return_ty_name} {func_cpp_impl_name}({cpp_params_str}) {{",
            f"}}",
        ):
            if return_ty_ref and isinstance(return_ty_ref.resolved_ty, IfaceType):
                impl_name = f"{return_ty_ref.resolved_ty.ty_decl.name}Impl"
                target.writelns(
                    f"// The parameters in the make_holder function should be of the same type",
                    f"// as the parameters in the constructor of the actual implementation class.",
                    f"return {self.make_holder}<{impl_name}, {cpp_return_ty_name}>();",
                )
            else:
                target.writelns(
                    f'TH_THROW({self.runtime_error}, "{func_cpp_impl_name} not implemented");',
                )

    def gen_func_macro(
        self,
        func: GlobFuncDecl,
        target: CSourceWriter,
    ):
        func_cpp_impl_info = GlobFuncCppImplInfo.get(self.am, func)
        func_cpp_impl_name = f"{func.name}"
        target.writelns(
            f"{func_cpp_impl_info.macro}({func_cpp_impl_name});",
        )
