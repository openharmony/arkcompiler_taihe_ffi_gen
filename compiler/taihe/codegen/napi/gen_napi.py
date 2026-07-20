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

from collections.abc import Callable

from taihe.codegen.abi.analyses import (
    GlobFuncAbiInfo,
    IfaceAbiInfo,
    IfaceMethodAbiInfo,
)
from taihe.codegen.abi.writer import (
    CHeaderWriter,
    CSourceWriter,
    render_c_value,
)
from taihe.codegen.cpp.analyses import (
    GlobFuncCppUserInfo,
    IfaceCppInfo,
    PackageCppUserInfo,
    StructCppInfo,
    TypeCppInfo,
    UnionCppInfo,
)
from taihe.codegen.napi.analyses import (
    EnumNapiInfo,
    GlobFuncNapiInfo,
    IfaceMethodNapiInfo,
    IfaceNapiInfo,
    Namespace,
    PackageGroupNapiInfo,
    PackageNapiInfo,
    StructNapiInfo,
    TypeNapiInfo,
    UnionNapiInfo,
)
from taihe.codegen.napi.attributes import ReadOnlyAttr
from taihe.semantics.declarations import (
    EnumDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
    StructDecl,
    UnionDecl,
)
from taihe.semantics.types import (
    ArrayType,
    MapType,
    NonVoidType,
    OpaqueType,
    ScalarType,
    StringType,
    UnitType,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import GEN_CXX_SRC_GROUP, OutputManager


class NapiCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.iterate():
            self.gen_package(pkg)
        pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
        for module, ns in pg_napi_info.module_dict.items():
            self.gen_register(module, ns)

    def gen_ns_register(self, ns: Namespace, reg_obj: str, target: CSourceWriter):
        for child_ns_name, child_ns in ns.children.items():
            child_reg_obj = f"{reg_obj}_{child_ns_name}"
            target.writelns(
                f"napi_value {child_reg_obj};",
                f"napi_create_object(env, &{child_reg_obj});",
            )
            self.gen_ns_register(child_ns, child_reg_obj, target)
            target.writelns(
                f'NAPI_CALL(env, napi_set_named_property(env, {reg_obj}, "{child_ns_name}", {child_reg_obj}));',
            )
        for pkg in ns.packages:
            pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
            target.add_include(pkg_napi_info.header)
            target.writelns(
                f"{pkg_napi_info.cpp_ns}::NapiInit(env, {reg_obj});",
            )

    def gen_register(self, module: str, ns: Namespace):
        with CSourceWriter(
            self.oc,
            f"temp/{module}.napi_register.cpp",
            group=None,
            is_template=True,
        ) as target:
            with target.indented(
                f"napi_value Init(napi_env env, napi_value exports) {{",
                f"}}",
            ):
                self.gen_ns_register(ns, "exports", target)
                target.writelns(
                    f"return exports;",
                )
            target.writelns(
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
        funcs_namespace = "local"
        with CSourceWriter(
            self.oc,
            f"src/{pkg_napi_info.source}",
            group=GEN_CXX_SRC_GROUP,
        ) as pkg_napi_target:
            pkg_napi_target.add_include(pkg_napi_info.header)
            pkg_napi_target.add_include(pkg_cpp_user_info.header)
            register_infos = []

            ctors_map: dict[str, GlobFuncDecl] = {}
            static_map: dict[str, list[tuple[str, GlobFuncDecl]]] = {}

            for func in pkg.functions:
                func_napi_info = GlobFuncNapiInfo.get(self.am, func)
                func_name = f"{funcs_namespace}::{func.name}"
                if class_name := func_napi_info.ctor_class_name:
                    # TODO: raise special error
                    if class_name in ctors_map:
                        raise ValueError(
                            f"Error: class_name '{class_name}' already have a constructor."
                        )
                    ctors_map[class_name] = func
                elif class_name := func_napi_info.static_class_name:
                    static_map.setdefault(class_name, []).append((func_name, func))
                else:
                    register_infos.append((func.name, func_name))
            for iface in pkg.interfaces:
                iface_napi_info = IfaceNapiInfo.get(self.am, iface)
                if ctor := ctors_map.get(iface.name):
                    iface_napi_info.ctor = ctor
                if static_funcs := static_map.get(iface.name):
                    iface_napi_info.static_funcs = static_funcs

            for struct in pkg.structs:
                struct_napi_info = StructNapiInfo.get(self.am, struct)
                if ctor := ctors_map.get(struct.name):
                    struct_napi_info.ctor = ctor
                if static_funcs := static_map.get(struct.name):
                    struct_napi_info.static_funcs = static_funcs

            with pkg_napi_target.indented(
                f"namespace {funcs_namespace} {{",
                f"}}",
                indent="",
            ):
                for func in pkg.functions:
                    func_napi_info = GlobFuncNapiInfo.get(self.am, func)
                    if func_napi_info.ctor_class_name is None:
                        self.gen_func(func, pkg_napi_target, func.name)
                for enum in pkg.enums:
                    self.gen_enum(enum, pkg_napi_target)
                for struct in pkg.structs:
                    self.gen_struct(struct, pkg_napi_target)
                for iface in pkg.interfaces:
                    self.gen_iface(iface, pkg_napi_target)
                for union in pkg.unions:
                    self.gen_union_files(union)
            with pkg_napi_target.indented(
                f"namespace {pkg_napi_info.cpp_ns} {{",
                f"}}",
                indent="",
            ):
                self.gen_module_init(pkg, register_infos, pkg_napi_target)
        self.gen_napi_header_file(pkg_napi_info)

    def gen_napi_header_file(self, pkg_napi_info: PackageNapiInfo):
        with CHeaderWriter(
            self.oc,
            f"include/{pkg_napi_info.header}",
            group=None,
        ) as target:
            target.add_include("taihe/runtime_napi.hpp")
            target.add_include("taihe/platform/napi.hpp")
            target.writelns(
                f"#if __has_include(<napi/native_api.h>)",
                f"#include <napi/native_api.h>",
                f"#elif __has_include(<node/node_api.h>)",
                f"#include <node/node_api.h>",
                f"#else",
                f'#error "Please ensure the napi is correctly installed."',
                f"#endif",
            )
            with target.indented(
                f"namespace {pkg_napi_info.cpp_ns} {{",
                f"}}",
                indent="",
            ):
                target.writelns(
                    f"TH_VISIBLE napi_value NapiInit(napi_env env, napi_value exports);",
                )

    def gen_module_init(
        self,
        pkg: PackageDecl,
        register_infos: list[tuple[str, str]],
        pkg_napi_target: CSourceWriter,
    ):
        with pkg_napi_target.indented(
            f"napi_value NapiInit(napi_env env, napi_value exports) {{",
            f"}}",
        ):
            pkg_napi_target.writelns(
                f"if (::taihe::get_env() == nullptr) {{",
                f"    ::taihe::set_env(env);",
                f"}}",
                f"taihe::_init_main_thread();",
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

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_napi_target: CSourceWriter,
        mangled_name: str,
    ):
        with pkg_napi_target.indented(
            f"static napi_value {mangled_name}(napi_env env, [[maybe_unused]] napi_callback_info info) {{",
            f"}}",
        ):
            self.gen_func_content(
                func,
                pkg_napi_target,
            )

    def gen_func_content(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        obj_ptr: str | None = None,
    ):
        if isinstance(func, IfaceMethodDecl):
            func_napi_info = IfaceMethodNapiInfo.get(self.am, func)
            func_abi_info = IfaceMethodAbiInfo.get(self.am, func)
        else:
            func_napi_info = GlobFuncNapiInfo.get(self.am, func)
            func_abi_info = GlobFuncAbiInfo.get(self.am, func)
        if func_napi_info.async_name is not None:
            self._gen_async_func_content(
                func,
                target,
                obj_ptr,
                is_noexcept=func_abi_info.is_noexcept,
                is_promise=False,
            )
        elif func_napi_info.promise_name is not None:
            self._gen_async_func_content(
                func,
                target,
                obj_ptr,
                is_noexcept=func_abi_info.is_noexcept,
                is_promise=True,
            )
        else:
            self._gen_sync_func_content(
                func,
                target,
                obj_ptr,
                is_noexcept=func_abi_info.is_noexcept,
            )

    def _get_func_cpp_name(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        obj_ptr: str | None,
    ) -> str:
        if obj_ptr:
            return f"({obj_ptr})->{func.name}"
        else:
            assert isinstance(func, GlobFuncDecl)
            return GlobFuncCppUserInfo.get(self.am, func).full_name

    def _get_result_storage_type(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        is_noexcept: bool,
    ) -> str:
        if isinstance(return_ty := func.return_ty, NonVoidType):
            cpp_ty = TypeCppInfo.get(self.am, return_ty).as_owner
        else:
            cpp_ty = "void"
        if not is_noexcept:
            cpp_ty = f"::taihe::expected<{cpp_ty}, ::taihe::error>"
        return cpp_ty

    def _read_func_params(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        args: str,
    ) -> list[str]:
        values = []
        for index, param in enumerate(func.params):
            value = f"value_{index}"
            param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
            param_ty_napi_info.from_napi(target, f"{args}[{index}]", value)
            values.append(value)
        return values

    def _gen_async_func_content(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        obj_ptr: str | None,
        *,
        is_noexcept: bool,
        is_promise: bool,
    ):
        argc = len(func.params)
        if not is_promise:
            argc += 1
        if argc:
            target.writelns(
                f"size_t argc = {argc};",
                f"napi_value args[{argc}] = {{nullptr}};",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
            )
        cpp_values = self._read_func_params(func, target, "args")
        result_storage_type = self._get_result_storage_type(func, is_noexcept)
        obj_field = None
        cpp_inputs = []
        result_storage = None
        target.add_include("optional")
        with target.indented(
            f"struct async_data_ctx {{",
            f"}};",
        ):
            target.writelns(
                f"napi_async_work work = nullptr;",
            )
            if is_promise:
                target.writelns(
                    f"napi_deferred defer = nullptr;",
                )
            else:
                target.writelns(
                    f"napi_ref cb_ref = nullptr;",
                )
            if obj_ptr:
                obj_field = "obj_ptr"
                target.writelns(
                    f"decltype({obj_ptr}) {obj_field};",
                )
            for param, value in zip(func.params, cpp_values, strict=True):
                cpp_input = f"cpp_input_{param.name}"
                cpp_inputs.append(cpp_input)
                target.writelns(
                    f"decltype({value}) {cpp_input};",
                )
            if result_storage_type != "void":
                result_storage = "cpp_result"
                target.writelns(
                    f"std::optional<{result_storage_type}> {result_storage};",
                )
        with target.indented(
            f"async_data_ctx *cb_data = new async_data_ctx{{",
            f"}};",
        ):
            if obj_field:
                target.writelns(
                    f".{obj_field} = {obj_ptr},",
                )
            for cpp_input, value in zip(cpp_inputs, cpp_values, strict=True):
                target.writelns(
                    f".{cpp_input} = std::forward<decltype({value})>({value}),",
                )
        if is_promise:
            target.writelns(
                f"napi_value promise = nullptr;",
                f"NAPI_CALL(env, napi_create_promise(env, &cb_data->defer, &promise));",
            )
        else:
            target.writelns(
                f"NAPI_CALL(env, napi_create_reference(env, args[{len(func.params)}], 1, &cb_data->cb_ref));",
            )
        target.writelns(
            f"napi_value napi_resname;",
            f'NAPI_CALL(env, napi_create_string_utf8(env, "AsyncCallback", NAPI_AUTO_LENGTH, &napi_resname));',
        )
        with target.indented(
            f"napi_create_async_work(",
            f");",
        ):
            target.writelns(
                f"env,",
                f"nullptr,",
                f"napi_resname,",
            )
            self._write_async_execute(
                func,
                target,
                obj_field,
                cpp_inputs,
                result_storage,
            )
            self._write_async_complete(
                func,
                target,
                result_storage,
                is_noexcept=is_noexcept,
                is_promise=is_promise,
            )
            target.writelns(
                f"cb_data,",
                f"&cb_data->work",
            )
        target.writelns(
            f"NAPI_CALL(env, napi_queue_async_work(env, cb_data->work));",
        )
        if is_promise:
            target.writelns(
                f"return promise;",
            )
        else:
            target.writelns(
                f"return nullptr;",
            )

    def _write_async_execute(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        obj_field: str | None,
        cpp_inputs: list[str],
        result_storage: str | None,
    ):
        with target.indented(
            f"[]([[maybe_unused]] napi_env env, void* data) {{",
            f"}},",
        ):
            target.writelns(
                f"async_data_ctx *cb_data = reinterpret_cast<async_data_ctx *>(data);",
            )
            func_cpp_name = self._get_func_cpp_name(
                func,
                f"cb_data->{obj_field}" if obj_field else None,
            )
            cpp_args_str = ", ".join(
                f"std::forward<decltype(cb_data->{cpp_input})>(cb_data->{cpp_input})"
                for cpp_input in cpp_inputs
            )
            cpp_call = f"{func_cpp_name}({cpp_args_str})"
            if result_storage is None:
                target.writelns(
                    f"{cpp_call};",
                )
            else:
                target.writelns(
                    f"cb_data->{result_storage}.emplace({cpp_call});",
                )

    def _write_async_complete(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        result_storage: str | None,
        *,
        is_noexcept: bool,
        is_promise: bool,
    ):
        with target.indented(
            f"[](napi_env env, napi_status status, void* data) {{",
            f"}},",
        ):
            target.writelns(
                f"async_data_ctx *cb_data = reinterpret_cast<async_data_ctx *>(data);",
            )
            if is_promise:
                reject = lambda error: target.writelns(
                    f"NAPI_CALL(env, napi_reject_deferred(env, cb_data->defer, {error}));",
                )
                resolve = lambda value: target.writelns(
                    f"NAPI_CALL(env, napi_resolve_deferred(env, cb_data->defer, {value}));",
                )
            else:
                reject = lambda error: target.writelns(
                    f"napi_value js_cb;",
                    f"NAPI_CALL(env, napi_get_reference_value(env, cb_data->cb_ref, &js_cb));",
                    f"napi_value undefined_value;",
                    f"NAPI_CALL(env, napi_get_undefined(env, &undefined_value));",
                    f"napi_value argv[1] = {{ {error} }};",
                    f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 1, argv, nullptr));",
                )
                resolve = lambda value: target.writelns(
                    f"napi_value js_cb;",
                    f"NAPI_CALL(env, napi_get_reference_value(env, cb_data->cb_ref, &js_cb));",
                    f"napi_value undefined_value;",
                    f"NAPI_CALL(env, napi_get_undefined(env, &undefined_value));",
                    f"napi_value null_value;",
                    f"napi_get_null(env, &null_value);",
                    f"napi_value argv[2] = {{ null_value, {value} }};",
                    f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 2, argv, nullptr));",
                )
            with target.indented(
                f"if (status == napi_pending_exception) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value error_obj;",
                    f"napi_get_and_clear_last_exception(env, &error_obj);",
                )
                reject("error_obj")
            with target.indented(
                f"else if (status == napi_cancelled) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value error;",
                    f'napi_create_string_utf8(env, "Async operation was cancelled", NAPI_AUTO_LENGTH, &error);',
                    f"napi_value error_obj;",
                    f"napi_create_error(env, nullptr, error, &error_obj);",
                )
                reject("error_obj")
            with target.indented(
                f"else {{",
                f"}}",
            ):
                if result_storage is not None:
                    result = f"cb_data->{result_storage}.value()"
                else:
                    result = "NULL"
                if is_noexcept:
                    self._write_noexcept_async_success(
                        func,
                        target,
                        result,
                        resolve=resolve,
                        reject=reject,
                    )
                else:
                    self._write_maythrow_async_success(
                        func,
                        target,
                        result,
                        resolve=resolve,
                        reject=reject,
                    )
            target.writelns(
                f"napi_delete_async_work(env, cb_data->work);",
                f"delete cb_data;",
            )

    def _write_noexcept_async_success(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        result: str,
        *,
        resolve: Callable[[str], None],
        reject: Callable[[str], None],
    ):
        if isinstance(return_ty := func.return_ty, NonVoidType):
            return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
            return_ty_napi_info.into_napi(target, result, "napi_result")
        else:
            target.writelns(
                f"napi_value napi_result;",
                f"napi_get_undefined(env, &napi_result);",
            )
        resolve("napi_result")

    def _write_maythrow_async_success(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        result: str,
        *,
        resolve: Callable[[str], None],
        reject: Callable[[str], None],
    ):
        with target.indented(
            f"if ({result}.has_value()) {{",
            f"}}",
        ):
            self._write_noexcept_async_success(
                func,
                target,
                f"{result}.value()",
                resolve=resolve,
                reject=reject,
            )
            target.writelns(
                f"return;",
            )
        target.writelns(
            f"napi_value error_obj = taihe::into_napi_error(env, {result}.error());",
        )
        reject("error_obj")

    def _gen_sync_func_content(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        obj_ptr: str | None,
        *,
        is_noexcept: bool,
    ):
        argc = len(func.params)
        if argc:
            target.writelns(
                f"size_t argc = {argc};",
                f"napi_value args[{argc}] = {{nullptr}};",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
            )
        values = self._read_func_params(func, target, "args")
        result_storage_type = self._get_result_storage_type(func, is_noexcept)
        func_cpp_name = self._get_func_cpp_name(func, obj_ptr)
        cpp_args_str = ", ".join(
            f"std::forward<decltype({value})>({value})" for value in values
        )
        cpp_call = f"{func_cpp_name}({cpp_args_str})"
        if result_storage_type == "void":
            target.writelns(
                f"{cpp_call};",
            )
        else:
            target.writelns(
                f"{result_storage_type} cpp_result = {cpp_call};",
            )
        if is_noexcept:
            self._gen_noexcept_sync_success(func, target, "cpp_result")
        else:
            self._gen_maythrow_sync_success(func, target, "cpp_result")

    def _gen_noexcept_sync_success(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        result: str,
    ):
        if isinstance(return_ty := func.return_ty, NonVoidType):
            return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
            return_ty_napi_info.into_napi(target, result, "napi_result")
            target.writelns(
                f"return napi_result;",
            )
        else:
            target.writelns(
                f"return nullptr;",
            )

    def _gen_maythrow_sync_success(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        result: str,
    ):
        with target.indented(
            f"if ({result}.has_value()) {{",
            f"}}",
        ):
            self._gen_noexcept_sync_success(func, target, f"{result}.value()")
        target.writelns(
            f"napi_value error_obj = taihe::into_napi_error(env, {result}.error());",
            f"napi_throw(env, error_obj);",
            f"return nullptr;",
        )

    def gen_struct(
        self,
        struct: StructDecl,
        pkg_napi_target: CSourceWriter,
    ):
        self.gen_struct_conv_decl_file(struct)
        self.gen_struct_conv_impl_file(struct)
        with pkg_napi_target.indented(
            f"namespace {struct.name} {{",
            f"}}",
        ):
            self.gen_struct_ctor_func(struct, pkg_napi_target)
            self.gen_struct_create_func(struct, pkg_napi_target)

    def gen_struct_conv_decl_file(
        self,
        struct: StructDecl,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with CHeaderWriter(
            self.oc,
            f"include/{struct_napi_info.decl_header}",
            group=None,
        ) as struct_napi_decl_target:
            struct_napi_decl_target.add_include("taihe/platform/napi.hpp")
            struct_napi_decl_target.add_include("taihe/runtime_napi.hpp")
            struct_napi_decl_target.add_include(struct_cpp_info.defn_header)
            with struct_napi_decl_target.indented(
                f"template<> struct ::taihe::from_napi_t<{struct_cpp_info.as_owner}> {{",
                f"}};",
            ):
                struct_napi_decl_target.writelns(
                    f"inline {struct_cpp_info.as_owner} operator()(napi_env env, napi_value napi_obj) const;",
                )
            with struct_napi_decl_target.indented(
                f"template<> struct ::taihe::into_napi_t<{struct_cpp_info.as_owner}> {{",
                f"}};",
            ):
                struct_napi_decl_target.writelns(
                    f"static inline napi_ref ctor_ref = nullptr;",
                    f"static inline napi_ref ctor_ref_inner = nullptr;",
                    f"inline napi_value operator()(napi_env env, {struct_cpp_info.as_owner} cpp_obj) const;",
                )

    def gen_struct_conv_impl_file(
        self,
        struct: StructDecl,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with CHeaderWriter(
            self.oc,
            f"include/{struct_napi_info.impl_header}",
            group=None,
        ) as struct_napi_impl_target:
            struct_napi_impl_target.add_include(struct_napi_info.decl_header)
            struct_napi_impl_target.add_include(struct_cpp_info.impl_header)
            self.gen_struct_from_napi_func(struct, struct_napi_impl_target)
            self.gen_struct_into_napi_func(struct, struct_napi_impl_target)

    def gen_struct_from_napi_func(
        self,
        struct: StructDecl,
        struct_napi_impl_target: CHeaderWriter,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with struct_napi_impl_target.indented(
            f"inline {struct_cpp_info.as_owner} taihe::from_napi_t<{struct_cpp_info.as_owner}>::operator()(napi_env env, napi_value napi_obj) const {{",
            f"}}",
        ):
            cpp_field_results = []
            for parts in struct_napi_info.dts_final_fields:
                final = parts[-1]
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                napi_field_value = f"napi_field_{final.name}"
                cpp_field_result = f"cpp_field_{final.name}"
                struct_napi_impl_target.writelns(
                    f"napi_value {napi_field_value} = nullptr;",
                    f'NAPI_CALL(env, napi_get_named_property(env, napi_obj, "{final.name}", &{napi_field_value}));',
                )
                type_napi_info.from_napi(
                    struct_napi_impl_target, napi_field_value, cpp_field_result
                )
                cpp_field_results.append(cpp_field_result)
            cpp_moved_fields_str = ", ".join(
                f"std::move({cpp_field_result})"
                for cpp_field_result in cpp_field_results
            )
            struct_napi_impl_target.writelns(
                f"return {struct_cpp_info.as_owner}{{{cpp_moved_fields_str}}};",
            )

    def gen_struct_into_napi_func(
        self,
        struct: StructDecl,
        struct_napi_impl_target: CHeaderWriter,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with struct_napi_impl_target.indented(
            f"inline napi_value taihe::into_napi_t<{struct_cpp_info.as_owner}>::operator()(napi_env env, {struct_cpp_info.as_owner} cpp_obj) const {{",
            f"}}",
        ):
            args = []
            for parts in struct_napi_info.dts_final_fields:
                final = parts[-1]
                napi_field_result = f"napi_field_{final.name}"
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                type_napi_info.into_napi(
                    struct_napi_impl_target,
                    ".".join(("cpp_obj", *(part.name for part in parts))),
                    napi_field_result,
                )
                args.append(napi_field_result)
            args_str = ", ".join(args)
            struct_napi_impl_target.writelns(
                f"napi_value args[{len(struct_napi_info.dts_final_fields)}] = {{{args_str}}};",
                f"napi_value napi_obj = nullptr, constructor = nullptr;",
                f"NAPI_CALL(env, napi_get_reference_value(env, ctor_ref_inner, &constructor));",
                f"NAPI_CALL(env, napi_new_instance(env, constructor, {len(struct_napi_info.dts_final_fields)}, args, &napi_obj));",
                f"return napi_obj;",
            )

    def gen_struct_ctor_func(
        self,
        struct: StructDecl,
        pkg_napi_target: CSourceWriter,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        for parts in struct_napi_info.dts_final_fields:
            final = parts[-1]
            field_ty_napi_info = TypeNapiInfo.get(self.am, final.ty)

            with pkg_napi_target.indented(
                f"namespace getter {{",
                f"}}",
            ):
                with pkg_napi_target.indented(
                    f"static napi_value {final.name}(napi_env env, napi_callback_info info) {{",
                    f"}}",
                ):
                    pkg_napi_target.writelns(
                        f"napi_value thisobj;",
                        f"NAPI_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                        f"{struct_cpp_info.as_owner}* cpp_ptr;",
                        f"NAPI_CALL(env, napi_unwrap(env, thisobj, reinterpret_cast<void **>(&cpp_ptr)));",
                    )
                    field_ty_napi_info.into_napi(
                        pkg_napi_target,
                        "cpp_ptr->" + ".".join(part.name for part in parts),
                        "napi_field_result",
                    )
                    pkg_napi_target.writelns(
                        f"return napi_field_result;",
                    )
            if ReadOnlyAttr.get(final) is None:
                struct_napi_info.register_infos.append(
                    (final.name, f"getter::{final.name}", f"setter::{final.name}")
                )
                with pkg_napi_target.indented(
                    f"namespace setter {{",
                    f"}}",
                ):
                    with pkg_napi_target.indented(
                        f"static napi_value {final.name}(napi_env env, napi_callback_info info) {{",
                        f"}}",
                    ):
                        pkg_napi_target.writelns(
                            f"size_t argc = 1;",
                            f"napi_value args[1] = {{nullptr}};",
                            f"napi_value thisobj;",
                            f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, &thisobj, nullptr));",
                            f"{struct_cpp_info.as_owner}* cpp_ptr;",
                            f"NAPI_CALL(env, napi_unwrap(env, thisobj, reinterpret_cast<void **>(&cpp_ptr)));",
                        )
                        field_ty_napi_info.from_napi(
                            pkg_napi_target, "args[0]", "cpp_field_result"
                        )
                        pkg_napi_target.writelns(
                            f"cpp_ptr->{'.'.join(part.name for part in parts)} = cpp_field_result;",
                            f"return nullptr;",
                        )
            else:
                struct_napi_info.register_infos.append(
                    (final.name, f"getter::{final.name}", "nullptr")
                )

        # process ctor
        if ctor := struct_napi_info.ctor:
            with pkg_napi_target.indented(
                f"inline napi_value ctor(napi_env env, napi_callback_info info) {{",
                f"}}",
            ):
                ctor_cpp_user_info = GlobFuncCppUserInfo.get(self.am, ctor)
                pkg_napi_target.writelns(
                    f"napi_status _status;",
                    f"napi_value thisobj;",
                    f"size_t argc = {len(ctor.params)};",
                    f"napi_value args[{len(ctor.params)}];",
                    f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, &thisobj, nullptr));",
                )
                args = []
                for i, param in enumerate(ctor.params):
                    value_ty = param.ty
                    value = f"value_{i}"
                    type_info = TypeNapiInfo.get(self.am, value_ty)
                    type_info.from_napi(pkg_napi_target, f"args[{i}]", value)
                    args.append(value)
                args_str = ", ".join(args)

                if isinstance(return_ty := ctor.return_ty, NonVoidType):
                    cpp_return_info = TypeCppInfo.get(self.am, return_ty)
                    return_ty_cpp_name = cpp_return_info.as_owner
                else:
                    return_ty_cpp_name = "void"
                return_ty_cpp_name_expected = (
                    f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
                )
                result_cpp = "cpp_result"
                result_expected = "expected_result"
                result_error = "error_result"
                pkg_napi_target.writelns(
                    f"{return_ty_cpp_name_expected} {result_expected} = {ctor_cpp_user_info.full_name}({args_str});",
                )
                with pkg_napi_target.indented(
                    f"if ({result_expected}) {{",
                    f"}}",
                ):
                    if isinstance(return_ty := ctor.return_ty, NonVoidType):
                        pkg_napi_target.writelns(
                            f"{return_ty_cpp_name} {result_cpp} = {result_expected}.value();",
                            f"{return_ty_cpp_name}* cpp_ptr = new {struct_cpp_info.as_owner}(std::move({result_cpp}));",
                        )
                        with pkg_napi_target.indented(
                            f"_status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                            f"}}, nullptr, nullptr);",
                        ):
                            pkg_napi_target.writelns(
                                f"delete static_cast<{struct_cpp_info.as_owner}*>(finalize_data);",
                            )
                        with pkg_napi_target.indented(
                            f"if (_status != napi_ok) {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"delete cpp_ptr;",
                                f"napi_throw_error(env,",
                                f"    nullptr,",
                                f'    ("Native object wrapping failed (status " + std::to_string(_status) + ")").c_str()',
                                f");",
                                f"return nullptr;",
                            )
                        pkg_napi_target.writelns(
                            f"return thisobj;",
                        )
                    else:
                        pkg_napi_target.writelns(
                            f"return nullptr;",
                        )
                with pkg_napi_target.indented(
                    f"else {{",
                    f"}}",
                ):
                    pkg_napi_target.writelns(
                        f"::taihe::error {result_error} = {result_expected}.error();",
                        f"napi_throw(env, ::taihe::into_napi_error(env, {result_error}));",
                        f"return nullptr;",
                    )
        else:
            with pkg_napi_target.indented(
                f"inline napi_value ctor([[maybe_unused]] napi_env env, [[maybe_unused]] napi_callback_info info) {{",
                f"}}",
            ):
                pkg_napi_target.writelns(
                    f"return nullptr;",
                )

        with pkg_napi_target.indented(
            f"inline napi_value ctor_inner(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            pkg_napi_target.writelns(
                f"napi_status _status;",
                f"napi_value thisobj;",
                f"size_t argc = {len(struct_napi_info.dts_final_fields)};",
                f"napi_value args[{len(struct_napi_info.dts_final_fields)}];",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, &thisobj, nullptr));",
            )
            cpp_field_results = []
            for i, parts in enumerate(struct_napi_info.dts_final_fields):
                final = parts[-1]
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                cpp_field_result = f"cpp_field_{final.name}"
                type_napi_info.from_napi(
                    pkg_napi_target, f"args[{i}]", f"cpp_field_{final.name}"
                )
                cpp_field_results.append(cpp_field_result)
            cpp_moved_fields_str = ", ".join(
                f"std::move({cpp_field_result})"
                for cpp_field_result in cpp_field_results
            )
            pkg_napi_target.writelns(
                f"{struct_cpp_info.as_owner}* cpp_ptr = new {struct_cpp_info.as_owner}{{{cpp_moved_fields_str}}};",
            )
            with pkg_napi_target.indented(
                f"_status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                pkg_napi_target.writelns(
                    f"delete static_cast<{struct_cpp_info.as_owner}*>(finalize_data);",
                )
            with pkg_napi_target.indented(
                f"if (_status != napi_ok) {{",
                f"}}",
            ):
                pkg_napi_target.writelns(
                    f"delete cpp_ptr;",
                    f"napi_throw_error(env,",
                    f"    nullptr,",
                    f'    ("Native object wrapping failed (status " + std::to_string(_status) + ")").c_str()',
                    f");",
                    f"return nullptr;",
                )
            pkg_napi_target.writelns(
                f"return thisobj;",
            )

    def gen_struct_create_func(
        self,
        struct: StructDecl,
        target: CSourceWriter,
    ):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        # create function
        with target.indented(
            f"inline void create(napi_env env, [[maybe_unused]] napi_value exports) {{",
            f"}}",
        ):
            target.writelns(f"napi_value result = nullptr;")
            with target.indented(
                f"napi_property_descriptor desc[] = {{",
                f"}};",
            ):
                for (
                    field_name,
                    field_getter,
                    field_setter,
                ) in struct_napi_info.register_infos:
                    target.writelns(
                        f'{{"{field_name}", nullptr, nullptr, {field_getter}, {field_setter}, nullptr, napi_default, nullptr}}, ',
                    )
            if struct_napi_info.is_class():
                target.writelns(
                    f'NAPI_CALL(env, napi_define_class(env, "{struct.name}", NAPI_AUTO_LENGTH, ctor, nullptr, sizeof(desc) / sizeof(desc[0]), desc, &result));',
                )
                if struct_napi_info.static_funcs:
                    with target.indented(
                        f"napi_property_descriptor static_properties[] = {{",
                        f"}};",
                    ):
                        for mng_name, static_func in struct_napi_info.static_funcs:
                            static_func_napi_info = GlobFuncNapiInfo.get(
                                self.am, static_func
                            )
                            target.writelns(
                                f'{{"{static_func_napi_info.norm_name}", nullptr, {mng_name}, nullptr, nullptr, nullptr, napi_static, nullptr}}, ',
                            )
                    target.writelns(
                        f"NAPI_CALL(env, napi_define_properties(env, result, {len(struct_napi_info.static_funcs)}, static_properties));",
                    )
                target.writelns(
                    f"NAPI_CALL(env, napi_create_reference(env, result, 1, &::taihe::into_napi_t<{struct_cpp_info.as_owner}>::ctor_ref));",
                    f'NAPI_CALL(env, napi_set_named_property(env, exports, "{struct.name}", result));',
                )
            target.writelns(
                f'NAPI_CALL(env, napi_define_class(env, "{struct.name}_inner", NAPI_AUTO_LENGTH, ctor_inner, nullptr, sizeof(desc) / sizeof(desc[0]), desc, &result));',
                f"NAPI_CALL(env, napi_create_reference(env, result, 1, &::taihe::into_napi_t<{struct_cpp_info.as_owner}>::ctor_ref_inner));",
                f"return;",
            )

    def gen_iface(
        self,
        iface: IfaceDecl,
        pkg_napi_target: CSourceWriter,
    ):
        self.gen_iface_conv_decl_file(iface)
        self.gen_iface_conv_impl_file(iface)
        with pkg_napi_target.indented(
            f"namespace {iface.name} {{",
            f"}}",
        ):
            with pkg_napi_target.indented(
                f"namespace method {{",
                f"}}",
            ):
                self.gen_iface_method_impls(iface, pkg_napi_target)
            self.gen_iface_ctor_func(iface, pkg_napi_target)
            self.gen_iface_create_func(iface, pkg_napi_target)

    def gen_iface_conv_decl_file(
        self,
        iface: IfaceDecl,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        with CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.decl_header}",
            group=None,
        ) as iface_napi_decl_target:
            iface_napi_decl_target.add_include("taihe/platform/napi.hpp")
            iface_napi_decl_target.add_include("taihe/runtime_napi.hpp")
            iface_napi_decl_target.add_include(iface_cpp_info.defn_header)
            with iface_napi_decl_target.indented(
                f"template<> struct ::taihe::from_napi_t<{iface_cpp_info.as_owner}> {{",
                f"}};",
            ):
                iface_napi_decl_target.writelns(
                    f"inline {iface_cpp_info.as_owner} operator()(napi_env env, napi_value napi_obj) const;",
                )
            with iface_napi_decl_target.indented(
                f"template<> struct ::taihe::into_napi_t<{iface_cpp_info.as_owner}> {{",
                f"}};",
            ):
                iface_napi_decl_target.writelns(
                    f"static inline napi_ref ctor_ref = nullptr;",
                    f"static inline napi_ref ctor_ref_inner = nullptr;",
                    f"inline napi_value operator()(napi_env env, {iface_cpp_info.as_owner} cpp_obj) const;",
                )

    def gen_iface_conv_impl_file(
        self,
        iface: IfaceDecl,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        with CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.impl_header}",
            group=None,
        ) as iface_napi_impl_target:
            iface_napi_impl_target.add_include(iface_napi_info.decl_header)
            iface_napi_impl_target.add_include(iface_cpp_info.impl_header)
            self.gen_iface_from_napi_func(iface, iface_napi_impl_target)
            self.gen_iface_into_napi_func(iface, iface_napi_impl_target)

    def gen_iface_from_napi_func(
        self,
        iface: IfaceDecl,
        iface_napi_impl_target: CHeaderWriter,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_abi_info = IfaceAbiInfo.get(self.am, iface)
        with iface_napi_impl_target.indented(
            f"inline {iface_cpp_info.as_owner} taihe::from_napi_t<{iface_cpp_info.as_owner}>::operator()(napi_env env, napi_value napi_obj) const {{",
            f"}}",
        ):
            with iface_napi_impl_target.indented(
                f"struct cpp_impl_t: ::taihe::napi_ref_guard {{",
                f"}};",
            ):
                iface_napi_impl_target.writelns(
                    f"using ::taihe::napi_ref_guard::napi_ref_guard;",
                )

                for ancestor in iface_abi_info.ancestor_infos:
                    for method in ancestor.methods:
                        self.gen_iface_napi_method(method, iface_napi_impl_target)
            iface_napi_impl_target.writelns(
                f"return taihe::make_holder<cpp_impl_t, {iface_cpp_info.as_owner}, ::taihe::platform::napi::NapiObject>(env, napi_obj);",
            )

    def gen_iface_napi_method(
        self,
        method: IfaceMethodDecl,
        iface_napi_impl_target: CHeaderWriter,
    ):
        method_abi_info = IfaceMethodAbiInfo.get(self.am, method)

        method_napi_info = IfaceMethodNapiInfo.get(self.am, method)
        params_cpp = []
        for param in method.params:
            param_cpp_type_info = TypeCppInfo.get(self.am, param.ty)
            params_cpp.append(f"{param_cpp_type_info.as_param} {param.name}")
        params_cpp_str = ", ".join(params_cpp)

        if isinstance(method.return_ty, NonVoidType):
            return_ty_info = TypeCppInfo.get(self.am, method.return_ty)
            return_ty_cpp_name = return_ty_info.as_owner
        else:
            return_ty_cpp_name = "void"
        return_ty_expected_name = (
            f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
        )
        lambda_params = ["napi_env env", "napi_ref ref", *params_cpp]
        lambda_params_str = ", ".join(lambda_params)
        method_args = ", ".join(param.name for param in method.params)

        def write_method_lambda_body(is_noexcept: bool) -> None:
            if method.params:
                iface_napi_impl_target.writelns(
                    f"napi_value args_inner[{len(method.params)}];",
                )
                args_inner = "args_inner"
            else:
                args_inner = "nullptr"

            for index, param in enumerate(method.params):
                value = f"value_{index}"
                param_napi_type_info = TypeNapiInfo.get(self.am, param.ty)
                param_napi_type_info.into_napi(
                    iface_napi_impl_target,
                    param.name,
                    value,
                )
                iface_napi_impl_target.writelns(
                    f"args_inner[{index}] = {value};",
                )

            iface_napi_impl_target.writelns(
                f"napi_value org_napi_obj;",
                f"NAPI_CALL(env, napi_get_reference_value(env, ref, &org_napi_obj));",
                f"napi_value {method_napi_info.norm_name}_ts_method;",
                f'NAPI_CALL(env, napi_get_named_property(env, org_napi_obj, "{method_napi_info.norm_name}", &{method_napi_info.norm_name}_ts_method));',
                f"napi_value method_result_napi;",
                f"NAPI_CALL(env, napi_call_function(env, org_napi_obj, {method_napi_info.norm_name}_ts_method, {len(method.params)}, {args_inner}, &method_result_napi));",
            )

            if not is_noexcept:
                iface_napi_impl_target.writelns(
                    f"bool has_error = false;",
                    f"napi_is_exception_pending(env, &has_error);",
                )
                with iface_napi_impl_target.indented(
                    f"if (has_error) {{",
                    f"}}",
                ):
                    iface_napi_impl_target.writelns(
                        f"napi_value exception = nullptr;",
                        f"NAPI_CALL(env, napi_get_and_clear_last_exception(env, &exception));",
                        f"return ::taihe::unexpected<::taihe::error>(::taihe::from_napi_error(env, exception));",
                    )
                with iface_napi_impl_target.indented(
                    f"else {{",
                    f"}}",
                ):
                    if isinstance(method.return_ty, NonVoidType):
                        return_napi_type_info = TypeNapiInfo.get(
                            self.am, method.return_ty
                        )
                        return_napi_type_info.from_napi(
                            iface_napi_impl_target,
                            f"method_result_napi",
                            f"method_result_cpp",
                        )
                        iface_napi_impl_target.writelns(
                            f"return method_result_cpp;",
                        )
                    else:
                        iface_napi_impl_target.writelns(
                            f"return {{}};",
                        )
                return

            if isinstance(method.return_ty, NonVoidType):
                return_napi_type_info = TypeNapiInfo.get(self.am, method.return_ty)
                return_napi_type_info.from_napi(
                    iface_napi_impl_target,
                    f"method_result_napi",
                    f"method_result_cpp",
                )
                iface_napi_impl_target.writelns(
                    f"return method_result_cpp;",
                )
            else:
                iface_napi_impl_target.writelns(
                    f"return;",
                )

        if method_abi_info.is_noexcept:
            return_type_name = return_ty_cpp_name
            is_noexcept = True
        else:
            return_type_name = return_ty_expected_name
            is_noexcept = False
        with iface_napi_impl_target.indented(
            f"{return_type_name} {method_napi_info.norm_name}({params_cpp_str}) {{",
            f"}}",
        ):
            with iface_napi_impl_target.indented(
                f"return this->sync_call([]( {lambda_params_str} ) -> {return_type_name} {{",
                f"}}, {method_args});" if method_args else f"}});",
            ):
                write_method_lambda_body(is_noexcept)

    def gen_iface_into_napi_func(
        self,
        iface: IfaceDecl,
        iface_napi_impl_target: CHeaderWriter,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        with iface_napi_impl_target.indented(
            f"inline napi_value taihe::into_napi_t<{iface_cpp_info.as_owner}>::operator()(napi_env env, {iface_cpp_info.as_owner} cpp_obj) const {{",
            f"}}",
        ):
            iface_napi_impl_target.writelns(
                f"int64_t cpp_vtbl_ptr = reinterpret_cast<int64_t>(cpp_obj.m_handle.vtbl_ptr);",
                f"int64_t cpp_data_ptr = reinterpret_cast<int64_t>(cpp_obj.m_handle.data_ptr);",
                f"cpp_obj.m_handle.data_ptr = nullptr;",
                f"napi_value napi_vtbl_ptr = nullptr, napi_data_ptr = nullptr;",
                f"napi_create_int64(env, cpp_vtbl_ptr, &napi_vtbl_ptr);",
                f"napi_create_int64(env, cpp_data_ptr, &napi_data_ptr);",
                f"napi_value argv[2] = {{napi_vtbl_ptr, napi_data_ptr}};",
                f"napi_value napi_obj = nullptr;",
                f"napi_value constructor;",
                f"NAPI_CALL(env, napi_get_reference_value(env, ctor_ref_inner, &constructor));",
                f"NAPI_CALL(env, napi_new_instance(env, constructor, 2, argv, &napi_obj));",
            )
            iface_napi_impl_target.writelns(
                f"return napi_obj;",
            )

    def gen_iface_ctor_func(
        self,
        iface: IfaceDecl,
        pkg_napi_target: CSourceWriter,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        iface_abi_info = IfaceAbiInfo.get(self.am, iface)
        with pkg_napi_target.indented(
            f"inline napi_value ctor_inner(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            pkg_napi_target.writelns(
                f"napi_status _status;",
                f"napi_value thisobj;",
                f"size_t argc = 2;",
                f"napi_value args[2];",
                f"napi_get_cb_info(env, info, &argc, args, &thisobj, nullptr);",
                f"int64_t vtbl_ptr;",
                f"napi_get_value_int64(env, args[0], &vtbl_ptr);",
                f"int64_t data_ptr;",
                f"napi_get_value_int64(env, args[1], &data_ptr);",
                f"DataBlockHead* cpp_data_ptr = reinterpret_cast<DataBlockHead*>(data_ptr);",
                f"{iface_abi_info.vtable}* cpp_vtbl_ptr = reinterpret_cast<{iface_abi_info.vtable}*>(vtbl_ptr);",
                f"{iface_cpp_info.as_owner}* cpp_ptr = new {iface_cpp_info.as_owner}({{cpp_vtbl_ptr, cpp_data_ptr}});",
            )
            with pkg_napi_target.indented(
                f"_status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                pkg_napi_target.writelns(
                    f"delete static_cast<{iface_cpp_info.as_owner}*>(finalize_data);",
                )
            with pkg_napi_target.indented(
                f"if (_status != napi_ok) {{",
                f"}}",
            ):
                pkg_napi_target.writelns(
                    f"delete cpp_ptr;",
                    f"napi_throw_error(env,",
                    f"    nullptr,",
                    f'    ("Native object wrapping failed (status " + std::to_string(_status) + ")").c_str()',
                    f");",
                    f"return nullptr;",
                )
            pkg_napi_target.writelns(
                f"return thisobj;",
            )

        # process ctor
        if ctor := iface_napi_info.ctor:
            with pkg_napi_target.indented(
                f"inline napi_value ctor(napi_env env, napi_callback_info info) {{",
                f"}}",
            ):
                ctor_cpp_user_info = GlobFuncCppUserInfo.get(self.am, ctor)
                pkg_napi_target.writelns(
                    f"napi_status _status;",
                    f"napi_value thisobj;",
                    f"size_t argc = {len(ctor.params)};",
                    f"napi_value args[{len(ctor.params)}];",
                    f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, &thisobj, nullptr));",
                )
                args = []
                for i, param in enumerate(ctor.params):
                    value_ty = param.ty
                    value = f"value_{i}"
                    type_info = TypeNapiInfo.get(self.am, value_ty)
                    type_info.from_napi(pkg_napi_target, f"args[{i}]", value)
                    args.append(value)
                args_str = ", ".join(args)

                if isinstance(return_ty := ctor.return_ty, NonVoidType):
                    cpp_return_info = TypeCppInfo.get(self.am, return_ty)
                    return_ty_cpp_name = cpp_return_info.as_owner
                else:
                    return_ty_cpp_name = "void"
                return_ty_cpp_name_expected = (
                    f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
                )
                result_cpp = "cpp_result"
                result_expected = "expected_result"
                result_error = "error_result"
                pkg_napi_target.writelns(
                    f"{return_ty_cpp_name_expected} {result_expected} = {ctor_cpp_user_info.full_name}({args_str});",
                )
                with pkg_napi_target.indented(
                    f"if ({result_expected}) {{",
                    f"}}",
                ):
                    if isinstance(return_ty := ctor.return_ty, NonVoidType):
                        pkg_napi_target.writelns(
                            f"{return_ty_cpp_name} {result_cpp} = {result_expected}.value();",
                            f"{return_ty_cpp_name}* cpp_ptr = new {return_ty_cpp_name}(std::move({result_cpp}));",
                        )
                        with pkg_napi_target.indented(
                            f"_status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                            f"}}, nullptr, nullptr);",
                        ):
                            pkg_napi_target.writelns(
                                f"delete static_cast<{return_ty_cpp_name}*>(finalize_data);",
                            )
                        with pkg_napi_target.indented(
                            f"if (_status != napi_ok) {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"delete cpp_ptr;",
                                f"napi_throw_error(env,",
                                f"    nullptr,",
                                f'    ("Native object wrapping failed (status " + std::to_string(_status) + ")").c_str()',
                                f");",
                                f"return nullptr;",
                            )
                        pkg_napi_target.writelns(
                            f"return thisobj;",
                        )
                    else:
                        pkg_napi_target.writelns(
                            f"return nullptr;",
                        )
                with pkg_napi_target.indented(
                    f"else {{",
                    f"}}",
                ):
                    pkg_napi_target.writelns(
                        f"::taihe::error {result_error} = {result_expected}.error();",
                        f"napi_throw(env, ::taihe::into_napi_error(env, {result_error}));",
                        f"return nullptr;",
                    )
        else:
            with pkg_napi_target.indented(
                f"inline napi_value ctor([[maybe_unused]] napi_env env, [[maybe_unused]] napi_callback_info info) {{",
                f"}}",
            ):
                pkg_napi_target.writelns(
                    f"return nullptr;",
                )

    def gen_iface_create_func(
        self,
        iface: IfaceDecl,
        target: CSourceWriter,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        with target.indented(
            f"inline void create(napi_env env, [[maybe_unused]] napi_value exports) {{",
            f"}}",
        ):
            target.writelns(f"napi_value result = nullptr;")
            with target.indented(
                f"napi_property_descriptor desc[] = {{",
                f"}};",
            ):
                for (
                    methods,
                    ancestor,
                    props_strs,
                ) in iface_napi_info.iface_register_infos:
                    target.writelns(f"{{{', '.join(props_strs)}}}, ")
            if iface_napi_info.is_class():
                target.writelns(
                    f'NAPI_CALL(env, napi_define_class(env, "{iface.name}", NAPI_AUTO_LENGTH, ctor, nullptr, sizeof(desc) / sizeof(desc[0]), desc, &result));',
                )
                if iface_napi_info.static_funcs:
                    with target.indented(
                        f"napi_property_descriptor static_properties[] = {{",
                        f"}};",
                    ):
                        for mng_name, static_func in iface_napi_info.static_funcs:
                            static_func_napi_info = GlobFuncNapiInfo.get(
                                self.am, static_func
                            )
                            target.writelns(
                                f'{{"{static_func_napi_info.norm_name}", nullptr, {mng_name}, nullptr, nullptr, nullptr, napi_static, nullptr}}, ',
                            )
                    target.writelns(
                        f"NAPI_CALL(env, napi_define_properties(env, result, {len(iface_napi_info.static_funcs)}, static_properties));",
                    )
                target.writelns(
                    f"NAPI_CALL(env, napi_create_reference(env, result, 1, &::taihe::into_napi_t<{iface_cpp_info.as_owner}>::ctor_ref));",
                    f'NAPI_CALL(env, napi_set_named_property(env, exports, "{iface.name}", result));',
                )
            target.writelns(
                f'NAPI_CALL(env, napi_define_class(env, "{iface.name}_inner", NAPI_AUTO_LENGTH, ctor_inner, nullptr, sizeof(desc) / sizeof(desc[0]), desc, &result));',
                f"NAPI_CALL(env, napi_create_reference(env, result, 1, &::taihe::into_napi_t<{iface_cpp_info.as_owner}>::ctor_ref_inner));",
                f"return;",
            )

    def gen_iface_method_impls(
        self,
        iface: IfaceDecl,
        target: CSourceWriter,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        for methods, ancestor, props_strs in iface_napi_info.iface_register_infos:
            iface_cpp_info_ancestor = IfaceCppInfo.get(self.am, ancestor)
            for method in methods:
                with target.indented(
                    f"static napi_value {method.name}(napi_env env, napi_callback_info info) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"napi_value thisobj;",
                        f"NAPI_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                        f"{iface_cpp_info.as_owner}* obj_ptr;",
                        f"NAPI_CALL(env, napi_unwrap(env, thisobj, reinterpret_cast<void**>(&obj_ptr)));",
                    )
                    self.gen_func_content(
                        method,
                        target,
                        f"({iface_cpp_info_ancestor.as_param})*obj_ptr",
                    )

    def gen_enum(
        self,
        enum: EnumDecl,
        pkg_napi_target: CSourceWriter,
    ):
        with pkg_napi_target.indented(
            f"namespace {enum.name} {{",
            f"}}",
        ):
            self.gen_enum_create_func(enum, pkg_napi_target)

    def gen_enum_create_func(
        self,
        enum: EnumDecl,
        pkg_napi_target: CSourceWriter,
    ):
        with pkg_napi_target.indented(
            f"inline void create(napi_env env, [[maybe_unused]] napi_value exports) {{",
            f"}}",
        ):
            enum_napi_info = EnumNapiInfo.get(self.am, enum)
            if enum_napi_info.is_literal:
                for item in enum.items:
                    value = f"value_{item.name}"
                    item_ty_napi_info = TypeNapiInfo.get(self.am, enum.ty)
                    item_ty_cpp_info = TypeCppInfo.get(self.am, enum.ty)
                    item_ty_napi_info.into_napi(
                        pkg_napi_target,
                        f"(({item_ty_cpp_info.as_owner}){render_c_value(item.typed_value)})",
                        value,
                    )
                    pkg_napi_target.writelns(
                        f'NAPI_CALL(env, napi_set_named_property(env, exports, "{item.name}", {value}));',
                    )

            else:
                pkg_napi_target.writelns(
                    f"napi_value enum_obj;",
                    f"napi_create_object(env, &enum_obj);",
                    f"napi_value key;",
                )
                for item in enum.items:
                    value = f"value_{item.name}"
                    item_ty_napi_info = TypeNapiInfo.get(self.am, enum.ty)
                    item_ty_cpp_info = TypeCppInfo.get(self.am, enum.ty)
                    item_ty_napi_info.into_napi(
                        pkg_napi_target,
                        f"(({item_ty_cpp_info.as_owner}){render_c_value(item.typed_value)})",
                        value,
                    )
                    pkg_napi_target.writelns(
                        f'NAPI_CALL(env, napi_create_string_utf8(env, "{item.name}", NAPI_AUTO_LENGTH, &key));',
                        f'NAPI_CALL(env, napi_set_named_property(env, enum_obj, "{item.name}", {value}));',
                        f"NAPI_CALL(env, napi_set_property(env, enum_obj, {value}, key));",
                    )
                pkg_napi_target.writelns(
                    f'NAPI_CALL(env, napi_set_named_property(env, exports, "{enum.name}", enum_obj));',
                )
            pkg_napi_target.writelns(
                f"return;",
            )

    def gen_iface_register(
        self,
        iface: IfaceDecl,
        pkg_napi_target: CSourceWriter,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        pkg_napi_target.add_include(iface_napi_info.impl_header)
        pkg_napi_target.writelns(
            f"local::{iface.name}::create(env, exports);",
        )

    def gen_struct_register(
        self,
        struct: StructDecl,
        pkg_napi_target: CSourceWriter,
    ):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        pkg_napi_target.add_include(struct_napi_info.impl_header)
        pkg_napi_target.writelns(
            f"local::{struct.name}::create(env, exports);",
        )

    def gen_enum_register(
        self,
        enum: EnumDecl,
        pkg_napi_target: CSourceWriter,
    ):
        pkg_napi_target.writelns(
            f"local::{enum.name}::create(env, exports);",
        )

    def gen_union_files(
        self,
        union: UnionDecl,
    ):
        self.gen_union_conv_decl_file(union)
        self.gen_union_conv_impl_file(union)

    def gen_union_conv_decl_file(
        self,
        union: UnionDecl,
    ):
        union_cpp_info = UnionCppInfo.get(self.am, union)
        union_napi_info = UnionNapiInfo.get(self.am, union)
        with CHeaderWriter(
            self.oc,
            f"include/{union_napi_info.decl_header}",
            group=None,
        ) as union_napi_decl_target:
            union_napi_decl_target.add_include("taihe/platform/napi.hpp")
            union_napi_decl_target.add_include(union_cpp_info.defn_header)
            with union_napi_decl_target.indented(
                f"template<> struct ::taihe::from_napi_t<{union_cpp_info.as_owner}> {{",
                f"}};",
            ):
                union_napi_decl_target.writelns(
                    f"inline {union_cpp_info.as_owner} operator()(napi_env env, napi_value napi_obj) const;",
                )
            with union_napi_decl_target.indented(
                f"template<> struct ::taihe::into_napi_t<{union_cpp_info.as_owner}> {{",
                f"}};",
            ):
                union_napi_decl_target.writelns(
                    f"static inline napi_ref ctor_ref = nullptr;",
                    f"static inline napi_ref ctor_ref_inner = nullptr;",
                    f"inline napi_value operator()(napi_env env, {union_cpp_info.as_owner} cpp_obj) const;",
                )

    def gen_union_conv_impl_file(
        self,
        union: UnionDecl,
    ):
        union_cpp_info = UnionCppInfo.get(self.am, union)
        union_napi_info = UnionNapiInfo.get(self.am, union)
        with CHeaderWriter(
            self.oc,
            f"include/{union_napi_info.impl_header}",
            group=None,
        ) as union_napi_impl_target:
            union_napi_impl_target.add_include(union_napi_info.decl_header)
            union_napi_impl_target.add_include(union_cpp_info.impl_header)
            self.gen_union_from_napi_func(union, union_napi_impl_target)
            self.gen_union_into_napi_func(union, union_napi_impl_target)

    def gen_union_from_napi_func(
        self,
        union: UnionDecl,
        union_napi_impl_target: CHeaderWriter,
    ):
        union_cpp_info = UnionCppInfo.get(self.am, union)
        union_napi_info = UnionNapiInfo.get(self.am, union)
        with union_napi_impl_target.indented(
            f"inline {union_cpp_info.as_owner} taihe::from_napi_t<{union_cpp_info.as_owner}>::operator()(napi_env env, napi_value napi_obj) const {{",
            f"}}",
        ):
            union_napi_impl_target.writelns(
                f"napi_valuetype value_ty;",
                f"NAPI_CALL(env, napi_typeof(env, napi_obj, &value_ty));",
                f"bool flag;",
            )
            for parts in union_napi_info.dts_final_fields:
                final = parts[-1]
                static_tags = []
                for part in parts:
                    path_cpp_info = UnionCppInfo.get(self.am, part.parent_union)
                    static_tags.append(
                        f"::taihe::static_tag<{path_cpp_info.full_name}::tag_t::{part.name}>"
                    )
                static_tags_str = ", ".join(static_tags)
                full_name = "_".join(part.name for part in parts)
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                if isinstance(
                    final.ty, ScalarType | StringType | UnitType | OpaqueType
                ):
                    with union_napi_impl_target.indented(
                        f"if (value_ty == {type_napi_info.napi_type_name}) {{",
                        f"}}",
                    ):
                        cpp_result_spec = f"cpp_field_{full_name}"
                        type_napi_info.from_napi(
                            union_napi_impl_target,
                            "napi_obj",
                            cpp_result_spec,
                        )
                        union_napi_impl_target.writelns(
                            f"return {union_cpp_info.full_name}({static_tags_str}, std::move({cpp_result_spec}));",
                        )
                elif isinstance(final.ty, ArrayType):
                    union_napi_impl_target.writelns(
                        f"NAPI_CALL(env, napi_is_array(env, napi_obj, &flag));",
                    )
                    with union_napi_impl_target.indented(
                        f"if (flag) {{",
                        f"}}",
                    ):
                        cpp_result_spec = f"cpp_field_{full_name}"
                        type_napi_info.from_napi(
                            union_napi_impl_target,
                            "napi_obj",
                            cpp_result_spec,
                        )
                        union_napi_impl_target.writelns(
                            f"return {union_cpp_info.full_name}({static_tags_str}, std::move({cpp_result_spec}));",
                        )
                elif isinstance(final.ty, MapType):
                    union_napi_impl_target.writelns(
                        f"napi_value global = nullptr, map_ctor = nullptr;",
                        f"napi_get_global(env, &global);",
                        f'NAPI_CALL(env, napi_get_named_property(env, global, "Map", &map_ctor));',
                        f"NAPI_CALL(env, napi_instanceof(env, napi_obj, map_ctor, &flag));",
                    )
                    with union_napi_impl_target.indented(
                        f"if (flag) {{",
                        f"}}",
                    ):
                        cpp_result_spec = f"cpp_field_{full_name}"
                        type_napi_info.from_napi(
                            union_napi_impl_target,
                            "napi_obj",
                            cpp_result_spec,
                        )
                        union_napi_impl_target.writelns(
                            f"return {union_cpp_info.full_name}({static_tags_str}, std::move({cpp_result_spec}));",
                        )

    def gen_union_into_napi_func(
        self,
        union: UnionDecl,
        union_napi_impl_target: CHeaderWriter,
    ):
        union_cpp_info = UnionCppInfo.get(self.am, union)
        with union_napi_impl_target.indented(
            f"inline napi_value taihe::into_napi_t<{union_cpp_info.as_owner}>::operator()(napi_env env, {union_cpp_info.as_owner} cpp_value) const {{",
            f"}}",
        ):
            union_napi_impl_target.writelns(
                f"napi_value napi_obj = nullptr;",
            )
            with union_napi_impl_target.indented(
                f"switch (cpp_value.get_tag()) {{",
                f"}}",
            ):
                for field in union.fields:
                    tag = f"{union_cpp_info.full_name}::tag_t::{field.name}"
                    union_napi_impl_target.write_label(f"case {tag}:")
                    with union_napi_impl_target.indented(
                        f"{{",
                        f"}}",
                    ):
                        type_napi_info = TypeNapiInfo.get(self.am, field.ty)
                        type_napi_info.into_napi(
                            union_napi_impl_target,
                            f"cpp_value.get_{field.name}_ref()",
                            "napi_obj_field",
                        )
                        union_napi_impl_target.writelns(
                            f"napi_obj = napi_obj_field;",
                            f"break;",
                        )
            union_napi_impl_target.writelns(
                f"return napi_obj;",
            )
