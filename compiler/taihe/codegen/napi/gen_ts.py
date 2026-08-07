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
        for module, ns in pg_napi_info.module_dict.items():
            self.gen_module_file(module, ns)

    def gen_module_file(self, module: str, ns: Namespace):
        if not ns.lib_name:
            return

        with DtsWriter(
            self.oc,
            f"proxy/{module}.ts",
        ) as target:
            for head in ns.ts_injected_heads:
                target.write_block(head)
            target.writelns(
                f"const _taihe_native_lib = requireNapi('./{ns.lib_name}', RequireBaseDir.SCRIPT_DIR);",
            )
            self.gen_namespace(
                ns,
                target,
                "_taihe_native_lib",
            )

    def gen_namespace(self, ns: Namespace, target: DtsWriter, native_lib_name: str):
        for code in ns.ts_injected_codes:
            target.write_block(code)
        for pkg in ns.packages:
            self.gen_package(pkg, target, native_lib_name)

        for child_ns_name, child_ns in ns.children.items():
            dts_decl = f"namespace {child_ns_name}"
            dts_decl = f"export {dts_decl}"
            with target.indented(
                f"{dts_decl} {{",
                f"}}",
            ):
                self.gen_namespace(
                    child_ns,
                    target,
                    f"{native_lib_name}.{child_ns_name}",
                )

    def gen_package(self, pkg: PackageDecl, target: DtsWriter, native_lib_name: str):
        pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
        for func in pkg_napi_info.global_funcs:
            self.gen_func(func, target, native_lib_name)
        for struct in pkg.structs:
            self.gen_struct_class(struct, target, native_lib_name)
        for iface in pkg.interfaces:
            self.gen_iface_class(iface, target, native_lib_name)
        for enum in pkg.enums:
            self.gen_enum(enum, target, native_lib_name)

    def gen_func(self, func: GlobFuncDecl, target: DtsWriter, native_lib_name: str):
        func_napi_info = GlobFuncNapiInfo.get(self.am, func)
        target.writelns(
            f"export const {func_napi_info.norm_name} = {native_lib_name}.{func_napi_info.norm_name};",
        )

    def gen_struct_class(
        self,
        struct: StructDecl,
        target: DtsWriter,
        native_lib_name: str,
    ):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        if not struct_napi_info.is_class():
            return

        struct_decl = f"class {struct_napi_info.dts_type_name}"
        native_cls_name = f"{native_lib_name}.{struct_napi_info.dts_type_name}"
        struct_decl = f"{struct_decl} extends {native_cls_name}"
        struct_decl = f"export {struct_decl}"

        with target.indented(
            f"{struct_decl} {{",
            f"}}",
        ):
            for injected in struct_napi_info.class_ts_injected_codes:
                target.write_block(injected)

    def gen_iface_class(
        self,
        iface: IfaceDecl,
        target: DtsWriter,
        native_lib_name: str,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        if not iface_napi_info.is_class():
            return

        iface_decl = f"class {iface_napi_info.dts_type_name}"
        native_cls_name = f"{native_lib_name}.{iface_napi_info.dts_type_name}"
        iface_decl = f"{iface_decl} extends {native_cls_name}"
        iface_decl = f"export {iface_decl}"

        with target.indented(
            f"{iface_decl} {{",
            f"}}",
        ):
            for injected in iface_napi_info.class_ts_injected_codes:
                target.write_block(injected)

    def gen_enum(
        self,
        enum: EnumDecl,
        target: DtsWriter,
        native_lib_name: str,
    ):
        enum_napi_info = EnumNapiInfo.get(self.am, enum)
        if enum_napi_info.is_literal:
            for item in enum.items:
                target.writelns(
                    f"export const {item.name} = {native_lib_name}.{item.name};",
                )
        else:
            target.writelns(
                f"export const {enum_napi_info.dts_type_name} = {native_lib_name}.{enum_napi_info.dts_type_name};",
            )
