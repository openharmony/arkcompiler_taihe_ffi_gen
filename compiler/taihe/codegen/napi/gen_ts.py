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


from taihe.codegen.napi.analyses import (
    EnumNapiInfo,
    GlobFuncNapiInfo,
    IfaceNapiInfo,
    Namespace,
    PackageGroupNapiInfo,
    PackageNapiInfo,
    StructNapiInfo,
)
from taihe.codegen.napi.writer import (
    DtsWriter,
)
from taihe.semantics.declarations import (
    EnumDecl,
    GlobFuncDecl,
    IfaceDecl,
    PackageDecl,
    PackageGroup,
    StructDecl,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputManager


class TsCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
        for _, ns in pg_napi_info.module_dict.items():
            TsModuleGenerator(self.oc, self.am, ns).gen_module_file()


class TsModuleGenerator:
    def __init__(
        self,
        oc: OutputManager,
        am: AnalysisManager,
        ns: Namespace,
    ):
        self.am = am
        self.ns = ns
        self.target = DtsWriter(oc, f"proxy/{self.ns.name}.ts")

    def gen_module_file(self):
        if not self.ns.lib_name:
            return

        with self.target:
            for head in self.ns.ts_injected_heads:
                self.target.write_block(head)
            native_lib_name = "_taihe_native_lib"
            self.target.writelns(
                f"const {native_lib_name} = requireNapi('./{self.ns.lib_name}', RequireBaseDir.SCRIPT_DIR);",
            )
            TsNamespaceGenerator(
                self.target,
                self.am,
                self.ns,
                native_lib_name,
            ).gen_namespace()


class TsNamespaceGenerator:
    def __init__(
        self,
        target: DtsWriter,
        am: AnalysisManager,
        ns: Namespace,
        native_lib_name: str,
    ):
        self.am = am
        self.ns = ns
        self.native_lib_name = native_lib_name
        self.target = target

    def gen_namespace(self):
        for code in self.ns.ts_injected_codes:
            self.target.write_block(code)
        for pkg in self.ns.packages:
            self.gen_package(pkg)

        for _, child_ns in self.ns.children.items():
            dts_decl = f"namespace {child_ns.name}"
            dts_decl = f"export {dts_decl}"
            with self.target.indented(
                f"{dts_decl} {{",
                f"}}",
            ):
                TsNamespaceGenerator(
                    self.target,
                    self.am,
                    child_ns,
                    f"{self.native_lib_name}.{child_ns.name}",
                ).gen_namespace()

    def gen_package(self, pkg: PackageDecl):
        pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
        for func in pkg_napi_info.global_funcs:
            self.gen_func(func)
        for struct in pkg.structs:
            self.gen_struct_class(struct)
        for iface in pkg.interfaces:
            self.gen_iface_class(iface)
        for enum in pkg.enums:
            self.gen_enum(enum)

    def gen_func(self, func: GlobFuncDecl):
        func_napi_info = GlobFuncNapiInfo.get(self.am, func)
        self.target.writelns(
            f"export const {func_napi_info.norm_name} = {self.native_lib_name}.{func_napi_info.norm_name};",
        )

    def gen_struct_class(self, struct: StructDecl):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        if not struct_napi_info.is_class():
            return

        struct_decl = f"class {struct_napi_info.dts_type_name}"
        native_cls_name = f"{self.native_lib_name}.{struct_napi_info.dts_type_name}"
        struct_decl = f"{struct_decl} extends {native_cls_name}"
        struct_decl = f"export {struct_decl}"

        with self.target.indented(
            f"{struct_decl} {{",
            f"}}",
        ):
            for injected in struct_napi_info.class_ts_injected_codes:
                self.target.write_block(injected)

    def gen_iface_class(self, iface: IfaceDecl):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        if not iface_napi_info.is_class():
            return

        iface_decl = f"class {iface_napi_info.dts_type_name}"
        native_cls_name = f"{self.native_lib_name}.{iface_napi_info.dts_type_name}"
        iface_decl = f"{iface_decl} extends {native_cls_name}"
        iface_decl = f"export {iface_decl}"

        with self.target.indented(
            f"{iface_decl} {{",
            f"}}",
        ):
            for injected in iface_napi_info.class_ts_injected_codes:
                self.target.write_block(injected)

    def gen_enum(self, enum: EnumDecl):
        enum_napi_info = EnumNapiInfo.get(self.am, enum)
        if enum_napi_info.is_literal:
            for item in enum.items:
                self.target.writelns(
                    f"export const {item.name} = {self.native_lib_name}.{item.name};",
                )
        else:
            self.target.writelns(
                f"export const {enum_napi_info.dts_type_name} = {self.native_lib_name}.{enum_napi_info.dts_type_name};",
            )
