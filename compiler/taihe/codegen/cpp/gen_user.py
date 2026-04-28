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
from taihe.semantics.types import NonVoidType
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputManager


class CppUserHeadersGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.iterate(include_stdlib=True):
            CppUserPackageGenerator(self.om, self.am, pkg).gen_package_file()


class CppUserPackageGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, pkg: PackageDecl):
        self.om = om
        self.am = am
        self.pkg = pkg
        pkg_cpp_user_info = PackageCppUserInfo.get(self.am, self.pkg)
        self.target = CHeaderWriter(
            self.om,
            f"include/{pkg_cpp_user_info.header}",
            group=None,
        )

    def gen_package_file(self):
        pkg_abi_info = PackageAbiInfo.get(self.am, self.pkg)
        pkg_cpp_info = PackageCppInfo.get(self.am, self.pkg)
        with self.target:
            # types
            self.target.add_include(pkg_cpp_info.header)
            # functions
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
        func_cpp_user_info = GlobFuncCppUserInfo.get(self.am, func)
        params_cpp = []
        args_tmpl = []
        args_call = []
        args_call.append(f"&{func_abi_info.impl_name}")
        if isinstance(return_ty := func.return_ty, NonVoidType):
            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
            return_ty_cpp_name = return_ty_cpp_info.as_owner
        else:
            return_ty_cpp_name = "void"
        if func_abi_info.is_noexcept:
            result_ty_cpp_name = return_ty_cpp_name
        else:
            result_ty_cpp_name = f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"  # fmt: skip
        args_tmpl.append(result_ty_cpp_name)
        for param in func.params:
            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
            param_ty_cpp_name = param_ty_cpp_info.as_param
            params_cpp.append(f"{param_ty_cpp_name} {param.name}")
            args_tmpl.append(param_ty_cpp_name)
            args_call.append(f"::std::forward<{param_ty_cpp_name}>({param.name})")
        params_cpp_str = ", ".join(params_cpp)
        args_tmpl_str = ", ".join(args_tmpl)
        args_call_str = ", ".join(args_call)
        with self.target.indented(
            f"namespace {func_cpp_user_info.namespace} {{",
            f"}}",
            indent="",
        ):
            with self.target.indented(
                f"inline {result_ty_cpp_name} {func_cpp_user_info.call_name}({params_cpp_str}) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"return ::taihe::call_abi_func<{args_tmpl_str}>({args_call_str});",
                )
