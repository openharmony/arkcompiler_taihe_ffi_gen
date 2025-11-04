# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Huawei Device Co., Ltd.
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

from taihe.codegen.napi.analyses import (
    GlobFuncNapiInfo,
    Namespace,
    PackageGroupNapiInfo,
    TypeNapiInfo,
)
from taihe.codegen.napi.writer import DtsWriter
from taihe.semantics.declarations import (
    GlobFuncDecl,
    PackageDecl,
    PackageGroup,
)
from taihe.semantics.types import NonVoidType
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import FileKind, OutputManager


class DtsCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
        for module, ns in pg_napi_info.module_dict.items():
            self.gen_module_file(module, ns)

    def gen_module_file(self, module: str, ns: Namespace):
        with DtsWriter(
            self.oc,
            f"{module}.d.ts",
            FileKind.DTS,
        ) as target:
            self.gen_namespace(ns, target)

    def gen_namespace(self, ns: Namespace, target: DtsWriter):
        for pkg in ns.packages:
            self.gen_package(pkg, target)
        for child_ns_name, child_ns in ns.children.items():
            dts_decl = f"namespace {child_ns_name}"
            dts_decl = f"export {dts_decl}"
            with target.indented(
                f"{dts_decl} {{",
                f"}}",
            ):
                self.gen_namespace(child_ns, target)

    def gen_package(self, pkg: PackageDecl, pkg_dts_target: DtsWriter):
        for func in pkg.functions:
            self.gen_func(func, pkg_dts_target)

    def gen_func(self, func: GlobFuncDecl, pkg_dts_target: DtsWriter):
        func_napi_info = GlobFuncNapiInfo.get(self.am, func)
        args = []
        for param in func.params:
            value_ty = param.ty
            param_dts_info = TypeNapiInfo.get(self.am, value_ty)
            args.append(
                f"{param.name}{'?' if param_dts_info.is_optional else ''}: {param_dts_info.dts_type_in(pkg_dts_target)}"
            )
        args_str = ", ".join(args)
        if isinstance(func.return_ty, NonVoidType):
            return_ty_dts_info = TypeNapiInfo.get(self.am, func.return_ty)
            return_ty = return_ty_dts_info.dts_return_type_in(pkg_dts_target)
        else:
            return_ty = "void"
        pkg_dts_target.writelns(
            f"export function {func_napi_info.norm_name}({args_str}): {return_ty};",
        )
