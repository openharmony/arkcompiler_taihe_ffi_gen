# -*- coding: utf-8 -*-
#
# Copyright (c) 2025-2026 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from taihe.codegen.abi.analyses import (
    GlobFuncAbiInfo,
    IfaceAbiInfo,
    IfaceMethodAbiInfo,
    PackageAbiInfo,
    TypeAbiInfo,
)
from taihe.codegen.abi.writer import CHeaderWriter, CSourceWriter
from taihe.codegen.cpp.analyses import (
    GlobFuncCppImplInfo,
    IfaceCppImplInfo,
    IfaceCppInfo,
    IfaceMethodCppImplInfo,
    IfaceMethodCppInfo,
    PackageCppImplInfo,
    TypeCppInfo,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
)
from taihe.semantics.types import IfaceType, NonVoidType
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputManager


class CppImplHeadersGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.iterate():
            CppMacroPackageGenerator(self.om, self.am, pkg).gen_package_file()
            # for iface in pkg.interfaces:
            #     CppMacroIfaceGenerator(self.om, self.am, iface).gen_iface_file()


class CppMacroPackageGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, pkg: PackageDecl):
        self.om = om
        self.am = am
        self.pkg = pkg
        pkg_cpp_impl_info = PackageCppImplInfo.get(self.am, pkg)
        self.target = CHeaderWriter(
            self.om,
            f"include/{pkg_cpp_impl_info.header}",
            group=None,
        )

    def gen_package_file(self):
        pkg_abi_info = PackageAbiInfo.get(self.am, self.pkg)
        with self.target:
            self.target.add_include("taihe/common.hpp")
            self.target.add_include("taihe/invoke.hpp")
            self.target.add_include(pkg_abi_info.header)
            for func in self.pkg.functions:
                for param in func.params:
                    param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                    self.target.add_include(*param_ty_cpp_info.impl_headers)
                if isinstance(return_ty := func.return_ty, NonVoidType):
                    return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                    self.target.add_include(*return_ty_cpp_info.impl_headers)
                self.gen_func(func)

    def gen_func(self, func: GlobFuncDecl):
        func_abi_info = GlobFuncAbiInfo.get(self.am, func)
        func_cpp_impl_info = GlobFuncCppImplInfo.get(self.am, func)
        func_impl = "CPP_FUNC_IMPL"
        args_tmpl = [f"&{func_impl}"]
        params_abi = []
        args_call = []
        if isinstance(return_ty := func.return_ty, NonVoidType):
            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
            result_ty_cpp_name = return_ty_cpp_info.as_owner
        else:
            result_ty_cpp_name = "void"
        if func_abi_info.is_noexcept:
            return_ty_cpp_name = result_ty_cpp_name
        else:
            return_ty_cpp_name = f"::taihe::expected<{result_ty_cpp_name}, ::taihe::error>"  # fmt: skip
        args_tmpl.append(return_ty_cpp_name)
        for param in func.params:
            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
            param_ty_abi_info = TypeAbiInfo.get(self.am, param.ty)
            param_ty_cpp_name = param_ty_cpp_info.as_param
            param_ty_abi_name = param_ty_abi_info.as_param
            args_tmpl.append(param_ty_cpp_name)
            params_abi.append(f"{param_ty_abi_name} {param.name}")
            args_call.append(param.name)
        if not func_abi_info.is_noexcept:
            error_ty_abi_name = "TError"
            params_abi.append(f"{error_ty_abi_name}** abi_err")
            args_call.append("abi_err")
        if isinstance(return_ty := func.return_ty, NonVoidType):
            return_ty_abi_info = TypeAbiInfo.get(self.am, return_ty)
            result_ty_abi_name = return_ty_abi_info.as_owner
            params_abi.append(f"{result_ty_abi_name}* abi_ret")
            args_call.append("abi_ret")
        args_tmpl_str = ", ".join(args_tmpl)
        params_abi_str = ", ".join(params_abi)
        args_call_str = ", ".join(args_call)
        self.target.writelns(
            f"#define {func_cpp_impl_info.macro}({func_impl}) \\",
            f"    void {func_abi_info.impl_name}({params_abi_str}) {{ \\",
            f"        return ::taihe::function_calling_convention<{args_tmpl_str}>::abi_func({args_call_str}); \\",
            f"    }}",
        )


class CppMacroIfaceGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, iface: IfaceDecl):
        self.om = om
        self.am = am
        self.iface = iface
        iface_cpp_impl_info = IfaceCppImplInfo.get(self.am, iface)
        self.target = CHeaderWriter(
            self.om,
            f"include/{iface_cpp_impl_info.header}",
            group=None,
        )

    def gen_iface_file(self):
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        with self.target:
            self.target.add_include("taihe/common.hpp")
            self.target.add_include("taihe/invoke.hpp")
            self.target.add_include(iface_cpp_info.impl_header)
            for method in self.iface.methods:
                for param in method.params:
                    param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                    self.target.add_include(*param_ty_cpp_info.impl_headers)
                if isinstance(return_ty := method.return_ty, NonVoidType):
                    return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                    self.target.add_include(*return_ty_cpp_info.impl_headers)
                self.gen_method(method)

    def gen_method(self, method: IfaceMethodDecl):
        method_abi_info = IfaceMethodAbiInfo.get(self.am, method)
        method_cpp_impl_info = IfaceMethodCppImplInfo.get(self.am, method)
        method_impl = "CPP_METHOD_IMPL"
        args_tmpl = [f"&{method_impl}"]
        params_abi = []
        args_call = []
        if isinstance(return_ty := method.return_ty, NonVoidType):
            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
            result_ty_cpp_name = return_ty_cpp_info.as_owner
        else:
            result_ty_cpp_name = "void"
        if method_abi_info.is_noexcept:
            return_ty_cpp_name = result_ty_cpp_name
        else:
            return_ty_cpp_name = f"::taihe::expected<{result_ty_cpp_name}, ::taihe::error>"  # fmt: skip
        args_tmpl.append(return_ty_cpp_name)
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        iface_abi_info = IfaceAbiInfo.get(self.am, self.iface)
        iface_abi_name = iface_abi_info.as_param
        iface_cpp_name = iface_cpp_info.as_param
        iface_name = "tobj"
        args_tmpl.append(iface_cpp_name)
        params_abi.append(f"{iface_abi_name} {iface_name}")
        args_call.append(iface_name)
        for param in method.params:
            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
            param_ty_abi_info = TypeAbiInfo.get(self.am, param.ty)
            param_ty_cpp_name = param_ty_cpp_info.as_param
            param_ty_abi_name = param_ty_abi_info.as_param
            args_tmpl.append(param_ty_cpp_name)
            params_abi.append(f"{param_ty_abi_name} {param.name}")
            args_call.append(param.name)
        if not method_abi_info.is_noexcept:
            error_ty_abi_name = "TError"
            params_abi.append(f"{error_ty_abi_name}** abi_err")
            args_call.append("abi_err")
        if isinstance(return_ty := method.return_ty, NonVoidType):
            return_ty_abi_info = TypeAbiInfo.get(self.am, return_ty)
            result_ty_abi_name = return_ty_abi_info.as_owner
            params_abi.append(f"{result_ty_abi_name}* abi_ret")
            args_call.append("abi_ret")
        args_tmpl_str = ", ".join(args_tmpl)
        params_abi_str = ", ".join(params_abi)
        args_call_str = ", ".join(args_call)
        self.target.writelns(
            f"#define {method_cpp_impl_info.macro}({method_impl}) \\",
            f"    void {method_abi_info.impl_name}({params_abi_str}) {{ \\",
            f"        return ::taihe::function_calling_convention<{args_tmpl_str}>::abi_func({args_call_str}); \\",
            f"    }}",
        )


class CppImplSourcesGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am
        self.using_namespaces: list[str] = []

    def generate(self, pg: PackageGroup):
        for pkg in pg.iterate():
            CppTemplatePackageGenerator(self.om, self.am, pkg).gen_package_file()
            # for iface in pkg.interfaces:
            #     CppTemplateIfaceGenerator(self.om, self.am, iface).gen_iface_file()
        for pkg in pg.iterate():
            for iface in pkg.interfaces:
                CppTemplateClassHeaderGenerator(self.om, self.am, iface).gen_file()
                CppTemplateClassSourceGenerator(self.om, self.am, iface).gen_file()


class CppTemplateBaseWriterGenerator:
    def __init__(
        self,
        om: OutputManager,
        am: AnalysisManager,
        target: CSourceWriter,
        using_namespaces: list[str],
    ):
        self.om = om
        self.am = am
        self.target = target
        self.using_namespaces = using_namespaces

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

    def gen_using_namespaces(self):
        if not self.using_namespaces:
            self.target.writelns(
                "// You can add using namespace statements here if needed.",
            )
        for namespace in self.using_namespaces:
            self.target.writelns(
                f"using namespace {namespace};",
            )


class CppTemplatePackageGenerator(CppTemplateBaseWriterGenerator):
    def __init__(self, om: OutputManager, am: AnalysisManager, pkg: PackageDecl):
        self.pkg = pkg
        pkg_cpp_impl_info = PackageCppImplInfo.get(am, pkg)
        target = CSourceWriter(
            om,
            f"temp/{pkg_cpp_impl_info.source}",
            group=None,
        )
        super().__init__(om, am, target, [])

    def gen_package_file(self):
        pkg_cpp_impl_info = PackageCppImplInfo.get(self.am, self.pkg)
        with self.target:
            self.target.add_include(pkg_cpp_impl_info.header)
            self.target.add_include("stdexcept")
            with self.target.indented(
                f"namespace {{",
                f"}}  // namespace",
                indent="",
            ):
                self.gen_using_namespaces()
                for func in self.pkg.functions:
                    self.target.newline()
                    self.gen_func_impl(func)
            self.target.newline()
            self.target.writelns(
                "// Since these macros are auto-generate, lint will cause false positive.",
                "// NOLINTBEGIN",
            )
            for func in self.pkg.functions:
                self.gen_func_macro(func)
            self.target.writelns(
                "// NOLINTEND",
            )

    def gen_func_impl(self, func: GlobFuncDecl):
        func_abi_info = GlobFuncAbiInfo.get(self.am, func)
        func_cpp_impl_info = GlobFuncCppImplInfo.get(self.am, func)
        params_cpp = []
        for param in func.params:
            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
            param_ty_cpp_name = self.mask(param_ty_cpp_info.as_param)
            params_cpp.append(f"{param_ty_cpp_name} {param.name}")
        params_cpp_str = ", ".join(params_cpp)
        if isinstance(return_ty := func.return_ty, NonVoidType):
            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
            result_ty_cpp_name = return_ty_cpp_info.as_owner
        else:
            result_ty_cpp_name = "void"
        if func_abi_info.is_noexcept:
            return_ty_cpp_name = result_ty_cpp_name
        else:
            return_ty_cpp_name = f"::taihe::expected<{result_ty_cpp_name}, ::taihe::error>"  # fmt: skip
        with self.target.indented(
            f"{return_ty_cpp_name} {func_cpp_impl_info.function}({params_cpp_str}) {{",
            f"}}",
        ):
            if isinstance(return_ty := func.return_ty, IfaceType):
                ret_cpp_impl_info = IfaceCppImplInfo.get(self.am, return_ty.decl)
                self.target.add_include(ret_cpp_impl_info.template_header)
                self.target.writelns(
                    f"// The parameters in the make_holder function should be of the same type",
                    f"// as the parameters in the constructor of the actual implementation class.",
                    f"return {self.make_holder}<{ret_cpp_impl_info.template_class}, {return_ty_cpp_name}>();",
                )
            else:
                self.target.writelns(
                    f'TH_THROW({self.runtime_error}, "not implemented");',
                )

    def gen_func_macro(self, func: GlobFuncDecl):
        func_cpp_impl_info = GlobFuncCppImplInfo.get(self.am, func)
        self.target.writelns(
            f"{func_cpp_impl_info.macro}({func_cpp_impl_info.function});",
        )


class CppTemplateIfaceGenerator(CppTemplateBaseWriterGenerator):
    def __init__(self, om: OutputManager, am: AnalysisManager, iface: IfaceDecl):
        self.iface = iface
        iface_cpp_impl_info = IfaceCppImplInfo.get(am, iface)
        target = CSourceWriter(
            om,
            f"temp/{iface_cpp_impl_info.source}",
            group=None,
        )
        super().__init__(om, am, target, [])

    def gen_iface_file(self):
        iface_cpp_impl_info = IfaceCppImplInfo.get(self.am, self.iface)
        with self.target:
            self.target.add_include(iface_cpp_impl_info.header)
            self.target.add_include("stdexcept")
            with self.target.indented(
                f"namespace {{",
                f"}}  // namespace",
                indent="",
            ):
                self.gen_using_namespaces()
                for method in self.iface.methods:
                    self.target.newline()
                    self.gen_method_impl(method)
            self.target.newline()
            self.target.writelns(
                "// Since these macros are auto-generate, lint will cause false positive.",
                "// NOLINTBEGIN",
            )
            for method in self.iface.methods:
                self.gen_method_macro(method)
            self.target.writelns(
                "// NOLINTEND",
            )

    def gen_method_impl(self, method: IfaceMethodDecl):
        method_abi_info = IfaceMethodAbiInfo.get(self.am, method)
        method_cpp_impl_info = IfaceMethodCppImplInfo.get(self.am, method)
        params_cpp = []
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        iface_cpp_name = self.mask(iface_cpp_info.as_param)
        params_cpp.append(f"{iface_cpp_name} tobj")
        for param in method.params:
            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
            param_ty_cpp_name = self.mask(param_ty_cpp_info.as_param)
            params_cpp.append(f"{param_ty_cpp_name} {param.name}")
        params_cpp_str = ", ".join(params_cpp)
        if isinstance(return_ty := method.return_ty, NonVoidType):
            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
            result_ty_cpp_name = return_ty_cpp_info.as_owner
        else:
            result_ty_cpp_name = "void"
        if method_abi_info.is_noexcept:
            return_ty_cpp_name = result_ty_cpp_name
        else:
            return_ty_cpp_name = f"::taihe::expected<{result_ty_cpp_name}, ::taihe::error>"  # fmt: skip
        with self.target.indented(
            f"{return_ty_cpp_name} {method_cpp_impl_info.function}({params_cpp_str}) {{",
            f"}}",
        ):
            if isinstance(return_ty := method.return_ty, IfaceType):
                ret_cpp_impl_info = IfaceCppImplInfo.get(self.am, return_ty.decl)
                self.target.add_include(ret_cpp_impl_info.template_header)
                self.target.writelns(
                    f"// The parameters in the make_holder function should be of the same type",
                    f"// as the parameters in the constructor of the actual implementation class.",
                    f"return {self.make_holder}<{ret_cpp_impl_info.template_class}, {return_ty_cpp_name}>();",
                )
            else:
                self.target.writelns(
                    f'TH_THROW({self.runtime_error}, "not implemented");',
                )

    def gen_method_macro(self, method: IfaceMethodDecl):
        method_cpp_impl_info = IfaceMethodCppImplInfo.get(self.am, method)
        self.target.writelns(
            f"{method_cpp_impl_info.macro}({method_cpp_impl_info.function});",
        )


class CppTemplateClassHeaderGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, iface: IfaceDecl):
        self.om = om
        self.am = am
        self.iface = iface
        iface_cpp_impl_info = IfaceCppImplInfo.get(self.am, iface)
        self.target = CHeaderWriter(
            self.om,
            f"temp/{iface_cpp_impl_info.template_header}",
            group=None,
        )

    def gen_file(self):
        iface_abi_info = IfaceAbiInfo.get(self.am, self.iface)
        with self.target:
            self.target.add_include("taihe/common.hpp")
            for ancestor in iface_abi_info.ancestor_infos:
                for method in ancestor.methods:
                    for param in method.params:
                        param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                        self.target.add_include(*param_ty_cpp_info.impl_headers)
                    if isinstance(return_ty := method.return_ty, NonVoidType):
                        return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                        self.target.add_include(*return_ty_cpp_info.impl_headers)
            self.gen_iface_template_class()

    def gen_iface_template_class(self):
        iface_abi_info = IfaceAbiInfo.get(self.am, self.iface)
        iface_cpp_impl_info = IfaceCppImplInfo.get(self.am, self.iface)
        with self.target.indented(
            f"class {iface_cpp_impl_info.template_class} {{",
            f"}};",
        ):
            self.target.writelns(
                f"public:",
            )
            self.target.writelns(
                f"// You can add member variables and constructor here.",
            )
            for ancestor in iface_abi_info.ancestor_infos:
                for method in ancestor.methods:
                    self.gen_iface_method_decl(method)

    def gen_iface_method_decl(self, method: IfaceMethodDecl):
        method_abi_info = IfaceMethodAbiInfo.get(self.am, method)
        method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
        params_cpp = []
        for param in method.params:
            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
            param_ty_cpp_name = param_ty_cpp_info.as_param
            params_cpp.append(f"{param_ty_cpp_name} {param.name}")
        params_cpp_str = ", ".join(params_cpp)
        if isinstance(return_ty := method.return_ty, NonVoidType):
            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
            result_ty_cpp_name = return_ty_cpp_info.as_owner
        else:
            result_ty_cpp_name = "void"
        if method_abi_info.is_noexcept:
            return_ty_cpp_name = result_ty_cpp_name
        else:
            return_ty_cpp_name = f"::taihe::expected<{result_ty_cpp_name}, ::taihe::error>"  # fmt: skip
        self.target.writelns(
            f"{return_ty_cpp_name} {method_cpp_info.call_name}({params_cpp_str});",
        )


class CppTemplateClassSourceGenerator(CppTemplateBaseWriterGenerator):
    def __init__(self, om: OutputManager, am: AnalysisManager, iface: IfaceDecl):
        self.iface = iface
        iface_cpp_impl_info = IfaceCppImplInfo.get(am, iface)
        target = CSourceWriter(
            om,
            f"temp/{iface_cpp_impl_info.template_source}",
            group=None,
        )
        super().__init__(om, am, target, [])

    def gen_file(self):
        iface_abi_info = IfaceAbiInfo.get(self.am, self.iface)
        iface_cpp_impl_info = IfaceCppImplInfo.get(self.am, self.iface)
        with self.target:
            self.target.add_include(iface_cpp_impl_info.template_header)
            self.target.add_include("stdexcept")
            self.gen_using_namespaces()
            for ancestor in iface_abi_info.ancestor_infos:
                for method in ancestor.methods:
                    self.target.newline()
                    self.gen_iface_method_impl(method)

    def gen_iface_method_impl(self, method: IfaceMethodDecl):
        method_abi_info = IfaceMethodAbiInfo.get(self.am, method)
        method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
        iface_cpp_impl_info = IfaceCppImplInfo.get(self.am, self.iface)
        params_cpp = []
        for param in method.params:
            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
            param_ty_cpp_name = self.mask(param_ty_cpp_info.as_param)
            params_cpp.append(f"{param_ty_cpp_name} {param.name}")
        params_cpp_str = ", ".join(params_cpp)
        if isinstance(return_ty := method.return_ty, NonVoidType):
            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
            result_ty_cpp_name = return_ty_cpp_info.as_owner
        else:
            result_ty_cpp_name = "void"
        if method_abi_info.is_noexcept:
            return_ty_cpp_name = result_ty_cpp_name
        else:
            return_ty_cpp_name = f"::taihe::expected<{result_ty_cpp_name}, ::taihe::error>"  # fmt: skip
        with self.target.indented(
            f"{return_ty_cpp_name} {iface_cpp_impl_info.template_class}::{method_cpp_info.impl_name}({params_cpp_str}) {{",
            f"}}",
        ):
            if isinstance(return_ty := method.return_ty, IfaceType):
                ret_cpp_impl_info = IfaceCppImplInfo.get(self.am, return_ty.decl)
                self.target.add_include(ret_cpp_impl_info.template_header)
                self.target.writelns(
                    f"// The parameters in the make_holder function should be of the same type",
                    f"// as the parameters in the constructor of the actual implementation class.",
                    f"return {self.make_holder}<{ret_cpp_impl_info.template_class}, {return_ty_cpp_name}>();",
                )
            else:
                self.target.writelns(
                    f'TH_THROW({self.runtime_error}, "not implemented");',
                )
