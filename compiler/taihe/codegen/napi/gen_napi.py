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
    IfaceMethodCppInfo,
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
    NonVoidType,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import GEN_CXX_SRC_GROUP, OutputManager


class NapiCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.iterate():
            for struct in pkg.structs:
                self.gen_struct_conv_decl_file(struct)
                self.gen_struct_conv_impl_file(struct)
            for iface in pkg.interfaces:
                self.gen_iface_conv_decl_file(iface)
                self.gen_iface_conv_impl_file(iface)
            for union in pkg.unions:
                self.gen_union_conv_decl_file(union)
                self.gen_union_conv_impl_file(union)
            self.gen_package_header(pkg)
            self.gen_package_source(pkg)
        pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
        for module, ns in pg_napi_info.module_dict.items():
            self.gen_register(module, ns)

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

    def gen_package_header(self, pkg: PackageDecl):
        pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
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

    def gen_package_source(
        self,
        pkg: PackageDecl,
    ):
        pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
        pkg_cpp_user_info = PackageCppUserInfo.get(self.am, pkg)
        with CSourceWriter(
            self.oc,
            f"src/{pkg_napi_info.source}",
            group=GEN_CXX_SRC_GROUP,
        ) as target:
            target.add_include(pkg_napi_info.header)
            target.add_include(pkg_cpp_user_info.header)

            ctors_map: dict[str, GlobFuncDecl] = {}

            non_ctor_funcs: list[GlobFuncDecl] = []

            static_register_infos: dict[str, dict[str, tuple[str, str, str]]] = {}
            static_funcs: dict[str, list[GlobFuncDecl]] = {}
            global_register_infos: dict[str, tuple[str, str, str]] = {}
            global_funcs: list[GlobFuncDecl] = []

            for func in pkg.functions:
                func_napi_info = GlobFuncNapiInfo.get(self.am, func)
                if class_name := func_napi_info.ctor_class_name:
                    # TODO: raise special error
                    if class_name in ctors_map:
                        raise ValueError(
                            f"Error: class_name '{class_name}' already have a constructor."
                        )
                    ctors_map[class_name] = func
                    continue
                non_ctor_funcs.append(func)
                full_name = f"local::{func.name}"
                if class_name := func_napi_info.static_class_name:
                    static_funcs.setdefault(class_name, []).append(func)
                    static_register_infos.setdefault(class_name, {})[func.name] = (
                        full_name,
                        "nullptr",
                        "nullptr",
                    )
                else:
                    global_funcs.append(func)
                    global_register_infos[func.name] = (
                        full_name,
                        "nullptr",
                        "nullptr",
                    )

            pkg_napi_info.global_funcs = global_funcs
            pkg_napi_info.global_register_infos = global_register_infos

            for iface in pkg.interfaces:
                iface_napi_info = IfaceNapiInfo.get(self.am, iface)
                iface_napi_info.ctor = ctors_map.get(iface.name)
                iface_napi_info.static_funcs = static_funcs.get(iface.name, [])
                iface_napi_info.static_register_infos = static_register_infos.get(
                    iface.name,
                    {},
                )

            for struct in pkg.structs:
                struct_napi_info = StructNapiInfo.get(self.am, struct)
                struct_napi_info.ctor = ctors_map.get(struct.name)
                struct_napi_info.static_funcs = static_funcs.get(struct.name, [])
                struct_napi_info.static_register_infos = static_register_infos.get(
                    struct.name,
                    {},
                )

            with target.indented(
                f"namespace local {{",
                f"}}",
                indent="",
            ):
                for func in non_ctor_funcs:
                    self.gen_func(func, target)
                for enum in pkg.enums:
                    self.gen_enum(enum, target)
                for struct in pkg.structs:
                    self.gen_struct(struct, target)
                for iface in pkg.interfaces:
                    self.gen_iface(iface, target)

            with target.indented(
                f"namespace {pkg_napi_info.cpp_ns} {{",
                f"}}",
                indent="",
            ):
                with target.indented(
                    f"napi_value NapiInit(napi_env env, napi_value exports) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"if (::taihe::get_env() == nullptr) {{",
                        f"    ::taihe::set_env(env);",
                        f"}}",
                        f"taihe::_init_main_thread();",
                    )
                    for iface in pkg.interfaces:
                        target.writelns(
                            f"local::{iface.name}::create(env, exports);",
                        )
                    for struct in pkg.structs:
                        target.writelns(
                            f"local::{struct.name}::create(env, exports);",
                        )
                    for enum in pkg.enums:
                        target.writelns(
                            f"local::{enum.name}::create(env, exports);",
                        )
                    with target.indented(
                        f"napi_property_descriptor desc[] = {{",
                        f"}};",
                    ):
                        for attribute_name, (
                            method,
                            getter,
                            setter,
                        ) in pkg_napi_info.global_register_infos.items():
                            target.writelns(
                                f'{{"{attribute_name}", nullptr, {method}, {getter}, {setter}, nullptr, napi_default, nullptr}}, ',
                            )
                    target.writelns(
                        f"napi_define_properties(env, exports, {len(pkg_napi_info.global_register_infos)}, desc);",
                        f"return exports;",
                    )

    def gen_func(
        self,
        func: GlobFuncDecl,
        target: CSourceWriter,
    ):
        with target.indented(
            f"static napi_value {func.name}(napi_env env, [[maybe_unused]] napi_callback_info info) {{",
            f"}}",
        ):
            self.gen_func_content(
                func,
                target,
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

    def _get_cpp_result_type(
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
        cpp_exprs = []
        for index, param in enumerate(func.params):
            from_napi = f"from_napi_arg_{param.name}"
            param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
            param_ty_napi_info.gen_from_napi(target, from_napi)
            cpp_exprs.append(f"{from_napi}(env, {args}[{index}])")
        return cpp_exprs

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
        target.writelns(
            f"size_t argc = {argc};",
            f"napi_value args[{argc}] = {{}};",
            f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
        )
        cpp_exprs = self._read_func_params(func, target, "args")
        cpp_result_type = self._get_cpp_result_type(func, is_noexcept)
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
            for param, cpp_expr in zip(func.params, cpp_exprs, strict=True):
                cpp_input = f"cpp_input_{param.name}"
                cpp_inputs.append(cpp_input)
                target.writelns(
                    f"decltype({cpp_expr}) {cpp_input};",
                )
            if cpp_result_type != "void":
                result_storage = "cpp_result"
                target.writelns(
                    f"std::optional<{cpp_result_type}> {result_storage};",
                )
        with target.indented(
            f"async_data_ctx *cb_data = new async_data_ctx{{",
            f"}};",
        ):
            if obj_field:
                target.writelns(
                    f".{obj_field} = {obj_ptr},",
                )
            for cpp_input, cpp_expr in zip(cpp_inputs, cpp_exprs, strict=True):
                target.writelns(
                    f".{cpp_input} = {cpp_expr},",
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
            if result_storage is None:
                target.writelns(
                    f"{func_cpp_name}({cpp_args_str});",
                )
            else:
                target.writelns(
                    f"cb_data->{result_storage}.emplace({func_cpp_name}({cpp_args_str}));",
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
                    f"NAPI_CALL(env, napi_delete_reference(env, cb_data->cb_ref));",
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
                    f"NAPI_CALL(env, napi_delete_reference(env, cb_data->cb_ref));",
                )
            with target.indented(
                f"do {{",
                f"}} while (false);",
            ):
                with target.indented(
                    f"if (status == napi_pending_exception) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"napi_value error_obj;",
                        f"napi_get_and_clear_last_exception(env, &error_obj);",
                    )
                    reject("error_obj")
                    target.writelns(
                        f"break;",
                    )
                with target.indented(
                    f"if (status == napi_cancelled) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"napi_value error;",
                        f'napi_create_string_utf8(env, "Async operation was cancelled", NAPI_AUTO_LENGTH, &error);',
                        f"napi_value error_obj;",
                        f"napi_create_error(env, nullptr, error, &error_obj);",
                    )
                    reject("error_obj")
                    target.writelns(
                        f"break;",
                    )
                result = f"cb_data->{result_storage}.value()"
                if not is_noexcept:
                    with target.indented(
                        f"if (not {result}.has_value()) {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"napi_value error_obj = taihe::into_napi_error(env, {result}.error());",
                        )
                        reject("error_obj")
                        target.writelns(
                            f"break;",
                        )
                    result = f"{result}.value()"
                if isinstance(return_ty := func.return_ty, NonVoidType):
                    return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
                    return_ty_napi_info.gen_into_napi(target, "into_napi_result")
                    target.writelns(
                        f"napi_value napi_result = into_napi_result(env, std::move({result}));",
                    )
                else:
                    target.writelns(
                        f"napi_value napi_result;",
                        f"napi_get_undefined(env, &napi_result);",
                    )
                resolve("napi_result")
            target.writelns(
                f"napi_delete_async_work(env, cb_data->work);",
                f"delete cb_data;",
            )

    def _gen_sync_func_content(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        target: CSourceWriter,
        obj_ptr: str | None,
        *,
        is_noexcept: bool,
    ):
        argc = len(func.params)
        target.writelns(
            f"size_t argc = {argc};",
            f"napi_value args[{argc}] = {{}};",
            f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
        )
        cpp_exprs = self._read_func_params(func, target, "args")
        cpp_result_type = self._get_cpp_result_type(func, is_noexcept)
        func_cpp_name = self._get_func_cpp_name(func, obj_ptr)
        cpp_exprs_str = ", ".join(cpp_exprs)
        result = "cpp_result"
        if cpp_result_type == "void":
            target.writelns(
                f"{func_cpp_name}({cpp_exprs_str});",
            )
        else:
            target.writelns(
                f"{cpp_result_type} {result} = {func_cpp_name}({cpp_exprs_str});",
            )
        if not is_noexcept:
            with target.indented(
                f"if (not {result}.has_value()) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value error_obj = taihe::into_napi_error(env, {result}.error());",
                    f"napi_throw(env, error_obj);",
                    f"return nullptr;",
                )
            result = f"{result}.value()"
        if isinstance(return_ty := func.return_ty, NonVoidType):
            return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
            return_ty_napi_info.gen_into_napi(target, "into_napi_result")
            target.writelns(
                f"return into_napi_result(env, std::move({result}));",
            )
        else:
            target.writelns(
                f"return nullptr;",
            )

    def gen_struct(
        self,
        struct: StructDecl,
        target: CSourceWriter,
    ):
        with target.indented(
            f"namespace {struct.name} {{",
            f"}}",
        ):
            self.gen_struct_attributes(struct, target)
            self.gen_struct_inner_constructor(struct, target)
            self.gen_struct_constructor(struct, target)
            self.gen_struct_create(struct, target)

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
        ) as target:
            target.add_include("taihe/platform/napi.hpp")
            target.add_include("taihe/runtime_napi.hpp")
            target.add_include(struct_cpp_info.defn_header)
            with target.indented(
                f"template<> struct ::taihe::from_napi_t<{struct_cpp_info.as_owner}> {{",
                f"}};",
            ):
                target.writelns(
                    f"inline {struct_cpp_info.as_owner} operator()(napi_env env, napi_value napi_obj) const;",
                )
            with target.indented(
                f"template<> struct ::taihe::into_napi_t<{struct_cpp_info.as_owner}> {{",
                f"}};",
            ):
                target.writelns(
                    f"static inline napi_ref ctor_ref = nullptr;",
                    f"static inline napi_ref inner_ctor_ref = nullptr;",
                    f"inline napi_value operator()(napi_env env, {struct_cpp_info.as_param} cpp_obj) const;",
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
        ) as target:
            target.add_include(struct_napi_info.decl_header)
            target.add_include(struct_cpp_info.impl_header)
            self.gen_struct_from_napi_func(struct, target)
            self.gen_struct_into_napi_func(struct, target)

    def gen_struct_from_napi_func(
        self,
        struct: StructDecl,
        target: CHeaderWriter,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with target.indented(
            f"inline {struct_cpp_info.as_owner} taihe::from_napi_t<{struct_cpp_info.as_owner}>::operator()(napi_env env, napi_value napi_obj) const {{",
            f"}}",
        ):
            cpp_field_results = []
            for i, parts in enumerate(struct_napi_info.dts_final_fields):
                final = parts[-1]
                napi_field_value = f"napi_field_{i}"
                target.writelns(
                    f"napi_value {napi_field_value} = nullptr;",
                    f'NAPI_CALL(env, napi_get_named_property(env, napi_obj, "{final.name}", &{napi_field_value}));',
                )
                from_napi = f"from_napi_field_{i}"
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                type_napi_info.gen_from_napi(target, from_napi)
                cpp_field_results.append(f"{from_napi}(env, {napi_field_value})")
            cpp_moved_fields_str = ", ".join(cpp_field_results)
            target.writelns(
                f"return {struct_cpp_info.as_owner}{{{cpp_moved_fields_str}}};",
            )

    def gen_struct_into_napi_func(
        self,
        struct: StructDecl,
        target: CHeaderWriter,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with target.indented(
            f"inline napi_value taihe::into_napi_t<{struct_cpp_info.as_owner}>::operator()(napi_env env, {struct_cpp_info.as_param} cpp_obj) const {{",
            f"}}",
        ):
            argc = len(struct_napi_info.dts_final_fields)
            target.writelns(
                f"napi_value args[{argc}];",
            )
            for i, parts in enumerate(struct_napi_info.dts_final_fields):
                final = parts[-1]
                into_napi = f"into_napi_field_{i}"
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                type_napi_info.gen_into_napi(target, into_napi)
                target.writelns(
                    f"args[{i}] = {into_napi}(env, cpp_obj.{'.'.join(part.name for part in parts)});",
                )
            target.writelns(
                f"napi_value napi_obj = nullptr;",
                f"napi_value inner_ctor = nullptr;",
                f"NAPI_CALL(env, napi_get_reference_value(env, inner_ctor_ref, &inner_ctor));",
                f"NAPI_CALL(env, napi_new_instance(env, inner_ctor, {argc}, args, &napi_obj));",
                f"return napi_obj;",
            )

    def gen_struct_attributes(
        self,
        struct: StructDecl,
        target: CSourceWriter,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with target.indented(
            f"namespace getter {{",
            f"}}",
        ):
            for i, (getter, parts) in enumerate(struct_napi_info.getters):
                field = parts[-1]
                field_ty_napi_info = TypeNapiInfo.get(self.am, field.ty)
                with target.indented(
                    f"static napi_value {getter}(napi_env env, napi_callback_info info) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"napi_value thisobj;",
                        f"NAPI_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                        f"{struct_cpp_info.as_owner}* cpp_ptr;",
                        f"NAPI_CALL(env, napi_unwrap(env, thisobj, reinterpret_cast<void **>(&cpp_ptr)));",
                    )
                    field_into_napi = f"into_napi_field_{i}"
                    field_ty_napi_info.gen_into_napi(target, field_into_napi)
                    target.writelns(
                        f"return {field_into_napi}(env, cpp_ptr->{'.'.join(part.name for part in parts)});",
                    )
        with target.indented(
            f"namespace setter {{",
            f"}}",
        ):
            for i, (setter, parts) in enumerate(struct_napi_info.setters):
                field = parts[-1]
                field_ty_napi_info = TypeNapiInfo.get(self.am, field.ty)
                with target.indented(
                    f"static napi_value {setter}(napi_env env, napi_callback_info info) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"size_t argc = 1;",
                        f"napi_value args[1] = {{nullptr}};",
                        f"napi_value thisobj;",
                        f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, &thisobj, nullptr));",
                        f"{struct_cpp_info.as_owner}* cpp_ptr;",
                        f"NAPI_CALL(env, napi_unwrap(env, thisobj, reinterpret_cast<void **>(&cpp_ptr)));",
                    )
                    field_from_napi = f"from_napi_field_{i}"
                    field_ty_napi_info.gen_from_napi(target, field_from_napi)
                    target.writelns(
                        f"cpp_ptr->{'.'.join(part.name for part in parts)} = {field_from_napi}(env, args[0]);",
                        f"return nullptr;",
                    )

    def gen_struct_inner_constructor(
        self,
        struct: StructDecl,
        target: CSourceWriter,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with target.indented(
            f"inline napi_value inner_constructor(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            argc = len(struct_napi_info.dts_final_fields)
            target.writelns(
                f"size_t argc = {argc};",
                f"napi_value args[{argc}];",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
            )
            cpp_exprs = []
            for i, parts in enumerate(struct_napi_info.dts_final_fields):
                final = parts[-1]
                from_napi = f"from_napi_field_{i}"
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                type_napi_info.gen_from_napi(target, from_napi)
                cpp_exprs.append(f"{from_napi}(env, args[{i}])")
            cpp_exprs_str = ", ".join(cpp_exprs)
            target.writelns(
                f"napi_value thisobj;",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                f"auto* cpp_ptr = new {struct_cpp_info.as_owner}{{{cpp_exprs_str}}};",
            )
            with target.indented(
                f"napi_status _status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                target.writelns(
                    f"delete static_cast<{struct_cpp_info.as_owner}*>(finalize_data);",
                )
            with target.indented(
                f"if (_status != napi_ok) {{",
                f"}}",
            ):
                target.writelns(
                    f"delete cpp_ptr;",
                    f'napi_throw_error(env, nullptr, ("Native object wrapping failed (status " + std::to_string(_status) + ")").c_str());',
                    f"return nullptr;",
                )
            target.writelns(
                f"return thisobj;",
            )

    def gen_struct_constructor(
        self,
        struct: StructDecl,
        target: CSourceWriter,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with target.indented(
            f"inline napi_value constructor(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            if (ctor := struct_napi_info.ctor) is None:
                target.writelns(
                    f"return inner_constructor(env, info);",
                )
                return
            ctor_abi_info = GlobFuncAbiInfo.get(self.am, ctor)
            ctor_cpp_user_info = GlobFuncCppUserInfo.get(self.am, ctor)
            argc = len(ctor.params)
            target.writelns(
                f"size_t argc = {argc};",
                f"napi_value args[{argc}];",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
            )
            cpp_exprs = self._read_func_params(ctor, target, "args")
            cpp_result_type = self._get_cpp_result_type(ctor, ctor_abi_info.is_noexcept)
            cpp_exprs_str = ", ".join(cpp_exprs)
            result = "cpp_result"
            target.writelns(
                f"{cpp_result_type} {result} = {ctor_cpp_user_info.full_name}({cpp_exprs_str});",
            )
            if not ctor_abi_info.is_noexcept:
                with target.indented(
                    f"if (!{result}) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"napi_value error_obj = taihe::into_napi_error(env, {result}.error());",
                        f"napi_throw(env, error_obj);",
                        f"return nullptr;",
                    )
                result = f"{result}.value()"
            target.writelns(
                f"napi_value thisobj;",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                f"auto* cpp_ptr = new {struct_cpp_info.as_owner}(std::move({result}));",
            )
            with target.indented(
                f"napi_status _status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                target.writelns(
                    f"delete static_cast<{struct_cpp_info.as_owner}*>(finalize_data);",
                )
            with target.indented(
                f"if (_status != napi_ok) {{",
                f"}}",
            ):
                target.writelns(
                    f"delete cpp_ptr;",
                    f'napi_throw_error(env, nullptr, ("Native object wrapping failed (status " + std::to_string(_status) + ")").c_str());',
                    f"return nullptr;",
                )
            target.writelns(
                f"return thisobj;",
            )

    def gen_struct_create(
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
            target.add_include(struct_napi_info.decl_header)
            with target.indented(
                f"napi_property_descriptor desc[] = {{",
                f"}};",
            ):
                for attribute_name, (
                    method,
                    getter,
                    setter,
                ) in struct_napi_info.register_infos.items():
                    target.writelns(
                        f'{{"{attribute_name}", nullptr, {method}, {getter}, {setter}, nullptr, napi_default, nullptr}}, ',
                    )
                for attribute_name, (
                    method,
                    getter,
                    setter,
                ) in struct_napi_info.static_register_infos.items():
                    target.writelns(
                        f'{{"{attribute_name}", nullptr, {method}, {getter}, {setter}, nullptr, napi_static, nullptr}}, ',
                    )
            target.writelns(
                f"napi_value global;",
                f"NAPI_CALL(env, napi_get_global(env, &global));",
                f"napi_value object_ctor;",
                f'NAPI_CALL(env, napi_get_named_property(env, global, "Object", &object_ctor));',
                f"napi_value set_proto_fn;",
                f'NAPI_CALL(env, napi_get_named_property(env, object_ctor, "setPrototypeOf", &set_proto_fn));',
            )
            target.writelns(
                f"napi_value ctor = nullptr;",
                f'NAPI_CALL(env, napi_define_class(env, "{struct_napi_info.dts_type_name}", NAPI_AUTO_LENGTH, constructor, nullptr, {len(struct_napi_info.register_infos) + len(struct_napi_info.static_register_infos)}, desc, &ctor));',
                f"NAPI_CALL(env, napi_create_reference(env, ctor, 1, &::taihe::into_napi_t<{struct_cpp_info.as_owner}>::ctor_ref));",
            )
            if struct_napi_info.is_class():
                target.writelns(
                    f'NAPI_CALL(env, napi_set_named_property(env, exports, "{struct_napi_info.dts_type_name}", ctor));',
                )
            target.writelns(
                f"napi_value inner_ctor = nullptr;",
                f'NAPI_CALL(env, napi_define_class(env, "{struct_napi_info.dts_type_name}", NAPI_AUTO_LENGTH, inner_constructor, nullptr, 0, nullptr, &inner_ctor));',
                f"NAPI_CALL(env, napi_create_reference(env, inner_ctor, 1, &::taihe::into_napi_t<{struct_cpp_info.as_owner}>::inner_ctor_ref));",
                f"napi_value proto;",
                f'NAPI_CALL(env, napi_get_named_property(env, ctor, "prototype", &proto));',
                f"napi_value inner_proto;",
                f'NAPI_CALL(env, napi_get_named_property(env, inner_ctor, "prototype", &inner_proto));',
                f"napi_value inner_proto_set_proto_args[2] = {{inner_proto, proto}};",
                f"napi_value inner_proto_set_proto_result;",
                f"NAPI_CALL(env, napi_call_function(env, global, set_proto_fn, 2, inner_proto_set_proto_args, &inner_proto_set_proto_result));",
                f"napi_value inner_ctor_set_proto_args[2] = {{inner_ctor, ctor}};",
                f"napi_value inner_ctor_set_proto_result;",
                f"NAPI_CALL(env, napi_call_function(env, global, set_proto_fn, 2, inner_ctor_set_proto_args, &inner_ctor_set_proto_result));",
            )
            if parent := struct_napi_info.dts_class_parent:
                parent_cpp_info = StructCppInfo.get(self.am, parent.ty.decl)  # type: ignore
                parent_napi_info = StructNapiInfo.get(self.am, parent.ty.decl)  # type: ignore
                target.add_include(parent_napi_info.decl_header)
                target.writelns(
                    f"napi_value parent_ctor;",
                    f"NAPI_CALL(env, napi_get_reference_value(env, ::taihe::into_napi_t<{parent_cpp_info.as_owner}>::ctor_ref, &parent_ctor));",
                    f"napi_value parent_proto;",
                    f'NAPI_CALL(env, napi_get_named_property(env, parent_ctor, "prototype", &parent_proto));',
                    f"napi_value proto_set_proto_args[2] = {{proto, parent_proto}};",
                    f"napi_value proto_set_proto_result;",
                    f"NAPI_CALL(env, napi_call_function(env, global, set_proto_fn, 2, proto_set_proto_args, &proto_set_proto_result));",
                    f"napi_value ctor_set_proto_args[2] = {{ctor, parent_ctor}};",
                    f"napi_value ctor_set_proto_result;",
                    f"NAPI_CALL(env, napi_call_function(env, global, set_proto_fn, 2, ctor_set_proto_args, &ctor_set_proto_result));",
                )

    def gen_iface(
        self,
        iface: IfaceDecl,
        target: CSourceWriter,
    ):
        with target.indented(
            f"namespace {iface.name} {{",
            f"}}",
        ):
            self.gen_iface_method_impls(iface, target)
            self.gen_iface_inner_constructor(iface, target)
            self.gen_iface_constructor(iface, target)
            self.gen_iface_create(iface, target)

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
        ) as target:
            target.add_include("taihe/platform/napi.hpp")
            target.add_include("taihe/runtime_napi.hpp")
            target.add_include(iface_cpp_info.defn_header)
            with target.indented(
                f"template<> struct ::taihe::from_napi_t<{iface_cpp_info.as_owner}> {{",
                f"}};",
            ):
                target.writelns(
                    f"inline {iface_cpp_info.as_owner} operator()(napi_env env, napi_value napi_obj) const;",
                )
            with target.indented(
                f"template<> struct ::taihe::into_napi_t<{iface_cpp_info.as_owner}> {{",
                f"}};",
            ):
                target.writelns(
                    f"static inline napi_ref ctor_ref = nullptr;",
                    f"static inline napi_ref inner_ctor_ref = nullptr;",
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
        ) as target:
            target.add_include(iface_napi_info.decl_header)
            target.add_include(iface_cpp_info.impl_header)
            self.gen_iface_from_napi_func(iface, target)
            self.gen_iface_into_napi_func(iface, target)

    def gen_iface_from_napi_func(
        self,
        iface: IfaceDecl,
        target: CHeaderWriter,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_abi_info = IfaceAbiInfo.get(self.am, iface)
        with target.indented(
            f"inline {iface_cpp_info.as_owner} taihe::from_napi_t<{iface_cpp_info.as_owner}>::operator()(napi_env env, napi_value napi_obj) const {{",
            f"}}",
        ):
            with target.indented(
                f"struct cpp_impl_t: ::taihe::napi_ref_guard {{",
                f"}};",
            ):
                target.writelns(
                    f"using ::taihe::napi_ref_guard::napi_ref_guard;",
                )
                for ancestor in iface_abi_info.ancestor_infos:
                    for method in ancestor.methods:
                        self.gen_iface_method_from_napi(method, target)
            target.writelns(
                f"return taihe::make_holder<cpp_impl_t, {iface_cpp_info.as_owner}, ::taihe::platform::napi::NapiObject>(env, napi_obj);",
            )

    def gen_iface_method_from_napi(
        self,
        method: IfaceMethodDecl,
        target: CHeaderWriter,
    ):
        method_abi_info = IfaceMethodAbiInfo.get(self.am, method)
        method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
        method_params = []
        method_args = []
        for param in method.params:
            param_cpp_type_info = TypeCppInfo.get(self.am, param.ty)
            method_arg = f"arg_{param.name}"
            method_params.append(f"{param_cpp_type_info.as_param} {method_arg}")
            method_args.append(method_arg)
        method_params_str = ", ".join(method_params)
        if isinstance(method.return_ty, NonVoidType):
            return_ty_info = TypeCppInfo.get(self.am, method.return_ty)
            return_ty_cpp_name = return_ty_info.as_owner
        else:
            return_ty_cpp_name = "void"
        if not method_abi_info.is_noexcept:
            return_ty_cpp_name = (
                f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
            )
        with target.indented(
            f"{return_ty_cpp_name} {method_cpp_info.impl_name}({method_params_str}) {{",
            f"}}",
        ):
            method_napi_info = IfaceMethodNapiInfo.get(self.am, method)
            if (napi_name := method_napi_info.norm_name) is None:
                # TODO: support generating reverse call for getter/setter/async method
                target.writelns(
                    f'TH_THROW(std::runtime_error, "not supported");',
                )
                return
            with target.indented(
                f"return this->sync_call(",
                f");",
            ):
                self.write_sync_call_lambda(method, target, napi_name)
                for method_arg in method_args:
                    target.writelns(
                        f", std::forward<decltype({method_arg})>({method_arg})",
                    )

    def write_sync_call_lambda(
        self,
        method: IfaceMethodDecl,
        target: CHeaderWriter,
        napi_name: str,
    ):
        method_abi_info = IfaceMethodAbiInfo.get(self.am, method)
        method_params = ["napi_env env", "napi_ref ref"]
        method_args = []
        for param in method.params:
            param_cpp_type_info = TypeCppInfo.get(self.am, param.ty)
            method_arg = f"arg_{param.name}"
            method_params.append(f"{param_cpp_type_info.as_param} {method_arg}")
            method_args.append(method_arg)
        method_params_str = ", ".join(method_params)
        if isinstance(method.return_ty, NonVoidType):
            return_ty_info = TypeCppInfo.get(self.am, method.return_ty)
            return_ty_cpp_name = return_ty_info.as_owner
        else:
            return_ty_cpp_name = "void"
        if not method_abi_info.is_noexcept:
            return_ty_cpp_name = (
                f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
            )
        with target.indented(
            f"[]({method_params_str}) -> {return_ty_cpp_name} {{",
            f"}}",
        ):
            target.writelns(
                f"napi_value args[{len(method.params)}];",
            )
            for index, (param, method_arg) in enumerate(
                zip(method.params, method_args, strict=True)
            ):
                param_napi_type_info = TypeNapiInfo.get(self.am, param.ty)
                into_napi = f"into_napi_arg_{param.name}"
                param_napi_type_info.gen_into_napi(target, into_napi)
                target.writelns(
                    f"args[{index}] = {into_napi}(env, std::forward<decltype({method_arg})>({method_arg}));",
                )
            target.writelns(
                f"napi_value org_napi_obj;",
                f"NAPI_CALL(env, napi_get_reference_value(env, ref, &org_napi_obj));",
                f"napi_value ts_method;",
                f'NAPI_CALL(env, napi_get_named_property(env, org_napi_obj, "{napi_name}", &ts_method));',
                f"napi_value method_result_napi;",
                f"NAPI_CALL(env, napi_call_function(env, org_napi_obj, ts_method, {len(method.params)}, args, &method_result_napi));",
            )
            if not method_abi_info.is_noexcept:
                target.writelns(
                    f"bool has_error = false;",
                    f"napi_is_exception_pending(env, &has_error);",
                )
                with target.indented(
                    f"if (has_error) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"napi_value exception = nullptr;",
                        f"NAPI_CALL(env, napi_get_and_clear_last_exception(env, &exception));",
                        f"return ::taihe::unexpected<::taihe::error>(::taihe::from_napi_error(env, exception));",
                    )
            if isinstance(return_ty := method.return_ty, NonVoidType):
                return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
                return_ty_napi_info.gen_from_napi(target, "from_napi_result")
                target.writelns(
                    f"return from_napi_result(env, method_result_napi);",
                )
            elif not method_abi_info.is_noexcept:
                target.writelns(
                    f"return {{}};",
                )
            else:
                target.writelns(
                    f"return;",
                )

    def gen_iface_into_napi_func(
        self,
        iface: IfaceDecl,
        target: CHeaderWriter,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        with target.indented(
            f"inline napi_value taihe::into_napi_t<{iface_cpp_info.as_owner}>::operator()(napi_env env, {iface_cpp_info.as_owner} cpp_obj) const {{",
            f"}}",
        ):
            argc = 2
            target.writelns(
                f"napi_value args[{argc}];",
            )
            target.writelns(
                f"int64_t cpp_vtbl_ptr = reinterpret_cast<int64_t>(cpp_obj.m_handle.vtbl_ptr);",
                f"int64_t cpp_data_ptr = reinterpret_cast<int64_t>(cpp_obj.m_handle.data_ptr);",
                f"cpp_obj.m_handle.data_ptr = nullptr;",
                f"napi_create_int64(env, cpp_vtbl_ptr, &args[0]);",
                f"napi_create_int64(env, cpp_data_ptr, &args[1]);",
            )
            target.writelns(
                f"napi_value napi_obj = nullptr;",
                f"napi_value inner_ctor = nullptr;",
                f"NAPI_CALL(env, napi_get_reference_value(env, inner_ctor_ref, &inner_ctor));",
                f"NAPI_CALL(env, napi_new_instance(env, inner_ctor, {argc}, args, &napi_obj));",
                f"return napi_obj;",
            )

    def gen_iface_inner_constructor(
        self,
        iface: IfaceDecl,
        target: CSourceWriter,
    ):
        iface_abi_info = IfaceAbiInfo.get(self.am, iface)
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        with target.indented(
            f"inline napi_value inner_constructor(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            argc = 2
            target.writelns(
                f"size_t argc = {argc};",
                f"napi_value args[{argc}];",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
            )
            target.writelns(
                f"int64_t vtbl_ptr;",
                f"napi_get_value_int64(env, args[0], &vtbl_ptr);",
                f"{iface_abi_info.vtable}* cpp_vtbl_ptr = reinterpret_cast<{iface_abi_info.vtable}*>(vtbl_ptr);",
                f"int64_t data_ptr;",
                f"napi_get_value_int64(env, args[1], &data_ptr);",
                f"DataBlockHead* cpp_data_ptr = reinterpret_cast<DataBlockHead*>(data_ptr);",
            )
            target.writelns(
                f"napi_value thisobj;",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                f"auto* cpp_ptr = new {iface_cpp_info.as_owner}({{cpp_vtbl_ptr, cpp_data_ptr}});",
            )
            with target.indented(
                f"napi_status _status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                target.writelns(
                    f"delete static_cast<{iface_cpp_info.as_owner}*>(finalize_data);",
                )
            with target.indented(
                f"if (_status != napi_ok) {{",
                f"}}",
            ):
                target.writelns(
                    f"delete cpp_ptr;",
                    f'napi_throw_error(env, nullptr, ("Native object wrapping failed (status " + std::to_string(_status) + ")").c_str());',
                    f"return nullptr;",
                )
            target.writelns(
                f"return thisobj;",
            )

    def gen_iface_constructor(
        self,
        iface: IfaceDecl,
        target: CSourceWriter,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        with target.indented(
            f"inline napi_value constructor(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            if (ctor := iface_napi_info.ctor) is None:
                target.writelns(
                    f"return inner_constructor(env, info);",
                )
                return
            ctor_abi_info = GlobFuncAbiInfo.get(self.am, ctor)
            ctor_cpp_user_info = GlobFuncCppUserInfo.get(self.am, ctor)
            argc = len(ctor.params)
            target.writelns(
                f"size_t argc = {argc};",
                f"napi_value args[{argc}];",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
            )
            cpp_exprs = self._read_func_params(ctor, target, "args")
            cpp_result_type = self._get_cpp_result_type(ctor, ctor_abi_info.is_noexcept)
            cpp_exprs_str = ", ".join(cpp_exprs)
            result = "cpp_result"
            target.writelns(
                f"{cpp_result_type} {result} = {ctor_cpp_user_info.full_name}({cpp_exprs_str});",
            )
            if not ctor_abi_info.is_noexcept:
                with target.indented(
                    f"if (!{result}) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"napi_value error_obj = taihe::into_napi_error(env, {result}.error());",
                        f"napi_throw(env, error_obj);",
                        f"return nullptr;",
                    )
                result = f"{result}.value()"
            target.writelns(
                f"napi_value thisobj;",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                f"auto* cpp_ptr = new {iface_cpp_info.as_owner}(std::move({result}));",
            )
            with target.indented(
                f"napi_status _status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                target.writelns(
                    f"delete static_cast<{iface_cpp_info.as_owner}*>(finalize_data);",
                )
            with target.indented(
                f"if (_status != napi_ok) {{",
                f"}}",
            ):
                target.writelns(
                    f"delete cpp_ptr;",
                    f'napi_throw_error(env, nullptr, ("Native object wrapping failed (status " + std::to_string(_status) + ")").c_str());',
                    f"return nullptr;",
                )
            target.writelns(
                f"return thisobj;",
            )

    def gen_iface_create(
        self,
        iface: IfaceDecl,
        target: CSourceWriter,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        # create function
        with target.indented(
            f"inline void create(napi_env env, [[maybe_unused]] napi_value exports) {{",
            f"}}",
        ):
            target.add_include(iface_napi_info.decl_header)
            with target.indented(
                f"napi_property_descriptor desc[] = {{",
                f"}};",
            ):
                for attribute_name, (
                    method,
                    getter,
                    setter,
                ) in iface_napi_info.register_infos.items():
                    target.writelns(
                        f'{{"{attribute_name}", nullptr, {method}, {getter}, {setter}, nullptr, napi_default, nullptr}}, '
                    )
                for attribute_name, (
                    method,
                    getter,
                    setter,
                ) in iface_napi_info.static_register_infos.items():
                    target.writelns(
                        f'{{"{attribute_name}", nullptr, {method}, {getter}, {setter}, nullptr, napi_static, nullptr}}, ',
                    )
            target.writelns(
                f"napi_value global;",
                f"NAPI_CALL(env, napi_get_global(env, &global));",
                f"napi_value object_ctor;",
                f'NAPI_CALL(env, napi_get_named_property(env, global, "Object", &object_ctor));',
                f"napi_value set_proto_fn;",
                f'NAPI_CALL(env, napi_get_named_property(env, object_ctor, "setPrototypeOf", &set_proto_fn));',
            )
            target.writelns(
                f"napi_value ctor = nullptr;",
                f'NAPI_CALL(env, napi_define_class(env, "{iface_napi_info.dts_type_name}", NAPI_AUTO_LENGTH, constructor, nullptr, {len(iface_napi_info.register_infos) + len(iface_napi_info.static_register_infos)}, desc, &ctor));',
                f"NAPI_CALL(env, napi_create_reference(env, ctor, 1, &::taihe::into_napi_t<{iface_cpp_info.as_owner}>::ctor_ref));",
            )
            if iface_napi_info.is_class():
                target.writelns(
                    f'NAPI_CALL(env, napi_set_named_property(env, exports, "{iface_napi_info.dts_type_name}", ctor));',
                )
            target.writelns(
                f"napi_value inner_ctor = nullptr;",
                f'NAPI_CALL(env, napi_define_class(env, "{iface_napi_info.dts_type_name}", NAPI_AUTO_LENGTH, inner_constructor, nullptr, 0, nullptr, &inner_ctor));',
                f"NAPI_CALL(env, napi_create_reference(env, inner_ctor, 1, &::taihe::into_napi_t<{iface_cpp_info.as_owner}>::inner_ctor_ref));",
                f"napi_value proto;",
                f'NAPI_CALL(env, napi_get_named_property(env, ctor, "prototype", &proto));',
                f"napi_value inner_proto;",
                f'NAPI_CALL(env, napi_get_named_property(env, inner_ctor, "prototype", &inner_proto));',
                f"napi_value inner_proto_set_proto_args[2] = {{inner_proto, proto}};",
                f"napi_value inner_proto_set_proto_result;",
                f"NAPI_CALL(env, napi_call_function(env, global, set_proto_fn, 2, inner_proto_set_proto_args, &inner_proto_set_proto_result));",
                f"napi_value inner_ctor_set_proto_args[2] = {{inner_ctor, ctor}};",
                f"napi_value inner_ctor_set_proto_result;",
                f"NAPI_CALL(env, napi_call_function(env, global, set_proto_fn, 2, inner_ctor_set_proto_args, &inner_ctor_set_proto_result));",
            )
            if parent := iface_napi_info.dts_class_parent:
                parent_cpp_info = IfaceCppInfo.get(self.am, parent.ty.decl)
                parent_napi_info = IfaceNapiInfo.get(self.am, parent.ty.decl)
                target.add_include(parent_napi_info.decl_header)
                target.writelns(
                    f"napi_value parent_ctor;",
                    f"NAPI_CALL(env, napi_get_reference_value(env, ::taihe::into_napi_t<{parent_cpp_info.as_owner}>::ctor_ref, &parent_ctor));",
                    f"napi_value parent_proto;",
                    f'NAPI_CALL(env, napi_get_named_property(env, parent_ctor, "prototype", &parent_proto));',
                    f"napi_value proto_set_proto_args[2] = {{proto, parent_proto}};",
                    f"napi_value proto_set_proto_result;",
                    f"NAPI_CALL(env, napi_call_function(env, global, set_proto_fn, 2, proto_set_proto_args, &proto_set_proto_result));",
                    f"napi_value ctor_set_proto_args[2] = {{ctor, parent_ctor}};",
                    f"napi_value ctor_set_proto_result;",
                    f"NAPI_CALL(env, napi_call_function(env, global, set_proto_fn, 2, ctor_set_proto_args, &ctor_set_proto_result));",
                )

    def gen_iface_method_impls(
        self,
        iface: IfaceDecl,
        target: CSourceWriter,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        for name, method in iface_napi_info.methods:
            ancestor_cpp_info = IfaceCppInfo.get(self.am, method.parent_iface)
            with target.indented(
                f"namespace method {{",
                f"}}",
            ):
                with target.indented(
                    f"static napi_value {name}(napi_env env, napi_callback_info info) {{",
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
                        f"({ancestor_cpp_info.as_param})*obj_ptr",
                    )

    def gen_enum(
        self,
        enum: EnumDecl,
        target: CSourceWriter,
    ):
        with target.indented(
            f"namespace {enum.name} {{",
            f"}}",
        ):
            self.gen_enum_create(enum, target)

    def gen_enum_create(
        self,
        enum: EnumDecl,
        target: CSourceWriter,
    ):
        with target.indented(
            f"inline void create(napi_env env, [[maybe_unused]] napi_value exports) {{",
            f"}}",
        ):
            enum_napi_info = EnumNapiInfo.get(self.am, enum)
            item_ty_napi_info = TypeNapiInfo.get(self.am, enum.ty)
            item_ty_napi_info.gen_into_napi(target, "into_napi_enum_item")
            if enum_napi_info.is_literal:
                for item in enum.items:
                    value = f"value_{item.name}"
                    target.writelns(
                        f"napi_value {value} = into_napi_enum_item(env, {render_c_value(item.typed_value)});",
                    )
                    target.writelns(
                        f'NAPI_CALL(env, napi_set_named_property(env, exports, "{item.name}", {value}));',
                    )
            else:
                target.writelns(
                    f"napi_value enum_obj;",
                    f"napi_create_object(env, &enum_obj);",
                    f"napi_value key;",
                )
                for item in enum.items:
                    value = f"value_{item.name}"
                    target.writelns(
                        f"napi_value {value} = into_napi_enum_item(env, {render_c_value(item.typed_value)});",
                    )
                    target.writelns(
                        f'NAPI_CALL(env, napi_create_string_utf8(env, "{item.name}", NAPI_AUTO_LENGTH, &key));',
                        f'NAPI_CALL(env, napi_set_named_property(env, enum_obj, "{item.name}", {value}));',
                        f"NAPI_CALL(env, napi_set_property(env, enum_obj, {value}, key));",
                    )
                target.writelns(
                    f'NAPI_CALL(env, napi_set_named_property(env, exports, "{enum_napi_info.dts_type_name}", enum_obj));',
                )

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
        ) as target:
            target.add_include("taihe/platform/napi.hpp")
            target.add_include(union_cpp_info.defn_header)
            with target.indented(
                f"template<> struct ::taihe::from_napi_t<{union_cpp_info.as_owner}> {{",
                f"}};",
            ):
                target.writelns(
                    f"inline {union_cpp_info.as_owner} operator()(napi_env env, napi_value napi_obj) const;",
                )
            with target.indented(
                f"template<> struct ::taihe::into_napi_t<{union_cpp_info.as_owner}> {{",
                f"}};",
            ):
                target.writelns(
                    f"inline napi_value operator()(napi_env env, {union_cpp_info.as_param} cpp_obj) const;",
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
        ) as target:
            target.add_include(union_napi_info.decl_header)
            target.add_include(union_cpp_info.impl_header)
            self.gen_union_from_napi_func(union, target)
            self.gen_union_into_napi_func(union, target)

    def gen_union_from_napi_func(
        self,
        union: UnionDecl,
        target: CHeaderWriter,
    ):
        union_cpp_info = UnionCppInfo.get(self.am, union)
        union_napi_info = UnionNapiInfo.get(self.am, union)
        with target.indented(
            f"inline {union_cpp_info.as_owner} taihe::from_napi_t<{union_cpp_info.as_owner}>::operator()(napi_env env, napi_value napi_obj) const {{",
            f"}}",
        ):
            for i, parts in enumerate(union_napi_info.dts_final_fields):
                final = parts[-1]
                static_tags = []
                for part in parts:
                    path_cpp_info = UnionCppInfo.get(self.am, part.parent_union)
                    static_tags.append(
                        f"::taihe::static_tag<{path_cpp_info.full_name}::tag_t::{part.name}>"
                    )
                static_tags_str = ", ".join(static_tags)
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                check_napi = f"check_napi_{i}"
                type_napi_info.gen_check_napi(target, check_napi)
                with target.indented(
                    f"if ({check_napi}(env, napi_obj)) {{",
                    f"}}",
                ):
                    from_napi = f"from_napi_kind_{i}"
                    type_napi_info.gen_from_napi(target, from_napi)
                    target.writelns(
                        f"return {union_cpp_info.full_name}({static_tags_str}, {from_napi}(env, napi_obj));",
                    )

    def gen_union_into_napi_func(
        self,
        union: UnionDecl,
        target: CHeaderWriter,
    ):
        union_cpp_info = UnionCppInfo.get(self.am, union)
        with target.indented(
            f"inline napi_value taihe::into_napi_t<{union_cpp_info.as_owner}>::operator()(napi_env env, {union_cpp_info.as_param} cpp_value) const {{",
            f"}}",
        ):
            with target.indented(
                f"switch (cpp_value.get_tag()) {{",
                f"}}",
            ):
                for field in union.fields:
                    tag = f"{union_cpp_info.full_name}::tag_t::{field.name}"
                    target.write_label(f"case {tag}:")
                    with target.indented(
                        f"{{",
                        f"}}",
                    ):
                        into_napi = f"into_napi_kind_{field.name}"
                        type_napi_info = TypeNapiInfo.get(self.am, field.ty)
                        type_napi_info.gen_into_napi(target, into_napi)
                        target.writelns(
                            f"return {into_napi}(env, cpp_value.get_{field.name}_ref());",
                        )
