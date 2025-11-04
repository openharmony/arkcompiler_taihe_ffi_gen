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

from taihe.codegen.abi.writer import CHeaderWriter, CSourceWriter
from taihe.codegen.cpp.analyses import (
    PackageCppUserInfo,
    TypeCppInfo,
)
from taihe.codegen.napi.analyses import (
    GlobFuncNapiInfo,
    Namespace,
    PackageGroupNapiInfo,
    PackageNapiInfo,
    TypeNapiInfo,
    get_mangled_func_name,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
)
from taihe.semantics.types import (
    NonVoidType,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import FileKind, OutputManager


class NapiCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package(pkg)
        self.gen_register(pg)

    def gen_ns_register(
        self, ns: Namespace, reg_obj: str, ns_name: str, target: CSourceWriter
    ):
        for child_ns_name, child_ns in ns.children.items():
            ns_obj = f"{ns_name}_{child_ns_name}"
            target.writelns(
                f"napi_value {ns_obj};",
                f"napi_create_object(env, &{ns_obj});",
            )
            for pkg in child_ns.packages:
                pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
                target.add_include(pkg_napi_info.header)
                target.writelns(
                    f"{pkg_napi_info.init_func}(env, {ns_obj});",
                )
            self.gen_ns_register(child_ns, ns_obj, ns_obj, target)
            target.writelns(
                f'NAPI_CALL(env, napi_set_named_property(env, {reg_obj}, "{child_ns_name}", {ns_obj}));',
            )
        for pkg in ns.packages:
            pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
            target.add_include(pkg_napi_info.header)
            target.writelns(
                f"{pkg_napi_info.init_func}(env, exports);",
            )

    def gen_register(self, pg: PackageGroup):
        with CSourceWriter(
            self.oc,
            f"temp/napi_register.cpp",
            FileKind.CPP_SOURCE,
        ) as target:
            for pkg in pg.packages:
                pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
                target.add_include(pkg_napi_info.header)
            target.writelns(
                f"EXTERN_C_START",
            )
            pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
            with target.indented(
                f"napi_value Init(napi_env env, napi_value exports) {{",
                f"}}",
            ):
                for ns in pg_napi_info.module_dict.values():
                    self.gen_ns_register(ns, "exports", "ns", target)
                target.writelns(
                    f"return exports;",
                )
            target.writelns(
                f"EXTERN_C_END",
                f"static napi_module demoModule = {{",
                f"    .nm_version = 1,",
                f"    .nm_flags = 0,",
                f"    .nm_filename = nullptr,",
                f"    .nm_register_func = Init,",
                f'    .nm_modname = "entry",',
                f"    .nm_priv = ((void*)0),",
                f"    .reserved = {{ 0 }},",
                f"}};",
                f'extern "C" __attribute__((constructor)) void RegisterEntryModule(void)',
                f"{{",
                f"    napi_module_register(&demoModule);",
                f"}}",
            )

    def gen_package(
        self,
        pkg: PackageDecl,
    ):
        pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
        pkg_cpp_user_info = PackageCppUserInfo.get(self.am, pkg)
        with CSourceWriter(
            self.oc,
            f"src/{pkg_napi_info.source}",
            FileKind.CPP_SOURCE,
        ) as pkg_napi_target:
            pkg_napi_target.add_include(pkg_napi_info.header)
            pkg_napi_target.add_include(pkg_cpp_user_info.header)
            register_infos = []

            for func in pkg.functions:
                func_napi_info = GlobFuncNapiInfo.get(self.am, func)
                mangled_name = get_mangled_func_name(pkg, func)
                register_infos.append((func_napi_info.norm_name, mangled_name))

            for func in pkg.functions:
                func_napi_info = GlobFuncNapiInfo.get(self.am, func)
                if func_napi_info.ctor_class_name is None:
                    mangled_name = get_mangled_func_name(pkg, func)
                    self.gen_func(func, pkg_napi_info, pkg_napi_target, mangled_name)
            self.gen_module_init(pkg, register_infos, pkg_napi_target)
        self.gen_napi_header_file(pkg_napi_info)

    def gen_napi_header_file(self, pkg_napi_info: PackageNapiInfo):
        with CHeaderWriter(
            self.oc,
            f"include/{pkg_napi_info.header}",
            FileKind.C_HEADER,
        ) as target:
            target.add_include("taihe/napi_runtime.hpp")
            target.writelns(
                f"#if __has_include(<napi/native_api.h>)",
                f"#include <napi/native_api.h>",
                f"#elif __has_include(<node/node_api.h>)",
                f"#include <node/node_api.h>",
                f"#else",
                f'#error "Please ensure the napi is correctly installed."',
                f"#endif",
                f"#ifndef {pkg_napi_info.macro_name}",
                f"#define {pkg_napi_info.macro_name}",
                f"EXTERN_C_START",
                f"napi_value {pkg_napi_info.init_func}(napi_env env, napi_value exports);",
                f"EXTERN_C_END",
                f"#endif",
            )

    def gen_module_init(
        self,
        pkg: PackageDecl,
        register_infos: list[tuple[str, str]],
        pkg_napi_target: CSourceWriter,
    ):
        pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
        pkg_napi_target.writelns(
            f"EXTERN_C_START",
        )
        with pkg_napi_target.indented(
            f"napi_value {pkg_napi_info.init_func}(napi_env env, napi_value exports) {{",
            f"}}",
        ):
            pkg_napi_target.writelns(
                f"if (::taihe::get_env() == nullptr) {{",
                f"    ::taihe::set_env(env);",
                f"}}",
            )
            for iface in pkg.interfaces:
                self.gen_iface_register(iface, pkg_napi_target)
            for struct in pkg.structs:
                self.gen_struct_register(struct, pkg_napi_target)
            for enum in pkg.enums:
                self.gen_enum_register(enum, pkg_napi_target)
            with pkg_napi_target.indented(
                f"napi_property_descriptor desc[] = {{",
                f"}};",
            ):
                for meth_name, mng_name in register_infos:
                    pkg_napi_target.writelns(
                        f'{{"{meth_name}", nullptr, {mng_name}, nullptr, nullptr, nullptr, napi_default, nullptr}}, ',
                    )
            pkg_napi_target.writelns(
                f"napi_define_properties(env, exports, sizeof(desc) / sizeof(desc[0]), desc);",
                f"return exports;",
            )
        pkg_napi_target.writelns(
            f"EXTERN_C_END",
        )

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_napi_info: PackageNapiInfo,
        pkg_napi_target: CSourceWriter,
        mangled_name: str,
    ):
        with pkg_napi_target.indented(
            f"static napi_value {mangled_name}(napi_env env, [[maybe_unused]] napi_callback_info info) {{",
            f"}}",
        ):
            func_cpp_name = pkg_napi_info.cpp_ns + "::" + func.name
            self.gen_func_content(func, pkg_napi_target, func_cpp_name)

    def gen_func_content(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        pkg_napi_target: CSourceWriter,
        func_cpp_name: str,
    ):
        self.gen_get_cb_info(len(func.params), pkg_napi_target)
        cpp_args = []
        for i, param in enumerate(func.params):
            value_ty = param.ty
            param_ty_napi_info = TypeNapiInfo.get(self.am, value_ty)
            param_ty_napi_info.from_napi(pkg_napi_target, f"args[{i}]", f"value{i}")
            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
            cpp_args.append(f"std::forward<{param_ty_cpp_info.as_param}>(value{i})")
        cpp_args_str = ", ".join(cpp_args)

        if isinstance(return_ty := func.return_ty, NonVoidType):
            value_ty = return_ty
            cpp_return_info = TypeCppInfo.get(self.am, value_ty)
            pkg_napi_target.writelns(
                f"{cpp_return_info.as_owner} value = {func_cpp_name}({cpp_args_str});",
            )
            param_ty_napi_info = TypeNapiInfo.get(self.am, value_ty)
            param_ty_napi_info.into_napi(pkg_napi_target, "value", "result")
        else:
            pkg_napi_target.writelns(
                f"{func_cpp_name}({cpp_args_str});",
                f"napi_value result = nullptr;",
                f"napi_get_undefined(env, &result);",
            )
        pkg_napi_target.writelns(f"return result;")

    def gen_get_cb_info(
        self,
        params_num: int,
        pkg_napi_target: CSourceWriter,
    ):
        if params_num:
            pkg_napi_target.writelns(
                f"size_t argc = {params_num};",
                f"napi_value args[{params_num}] = {{nullptr}};",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args , nullptr, nullptr));",
            )
