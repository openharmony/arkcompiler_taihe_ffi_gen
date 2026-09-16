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
)
from taihe.codegen.cpp.analyses import (
    EnumCppInfo,
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
                NapiStructDeclGenerator(
                    self.oc, self.am, struct
                ).gen_struct_conv_decl_file()
                NapiStructImplGenerator(
                    self.oc, self.am, struct
                ).gen_struct_conv_impl_file()
            for iface in pkg.interfaces:
                NapiIfaceDeclGenerator(
                    self.oc, self.am, iface
                ).gen_iface_conv_decl_file()
                NapiIfaceImplGenerator(
                    self.oc, self.am, iface
                ).gen_iface_conv_impl_file()
            for union in pkg.unions:
                NapiUnionDeclGenerator(
                    self.oc, self.am, union
                ).gen_union_conv_decl_file()
                NapiUnionImplGenerator(
                    self.oc, self.am, union
                ).gen_union_conv_impl_file()
            NapiPackageHeaderGenerator(self.oc, self.am, pkg).gen_package_header()
            NapiPackageSourceGenerator(self.oc, self.am, pkg).gen_package_source()
        pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
        for module, ns in pg_napi_info.module_dict.items():
            NapiModuleRegisterGenerator(self.oc, self.am, module, ns).gen_register()


class NapiModuleRegisterGenerator:
    def __init__(
        self,
        oc: OutputManager,
        am: AnalysisManager,
        module: str,
        ns: Namespace,
    ):
        self.oc = oc
        self.am = am
        self.module = module
        self.ns = ns
        self.target = CSourceWriter(
            self.oc,
            f"temp/{self.module}.napi_register.cpp",
            group=None,
            is_template=True,
        )

    def gen_register(self):
        with self.target:
            with self.target.indented(
                f"napi_value Init(napi_env env, napi_value exports) {{",
                f"}}",
            ):
                self.gen_ns_register(self.ns, "exports")
                self.target.writelns(
                    f"return exports;",
                )
            self.target.writelns(
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

    def gen_ns_register(self, ns: Namespace, reg_obj: str):
        for child_ns_name, child_ns in ns.children.items():
            child_reg_obj = f"{reg_obj}_{child_ns_name}"
            self.target.writelns(
                f"napi_value {child_reg_obj};",
                f"napi_create_object(env, &{child_reg_obj});",
            )
            self.gen_ns_register(child_ns, child_reg_obj)
            self.target.writelns(
                f'napi_set_named_property(env, {reg_obj}, "{child_ns_name}", {child_reg_obj});',
            )
        for pkg in self.ns.packages:
            pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
            self.target.add_include(pkg_napi_info.header)
            self.target.writelns(
                f"{pkg_napi_info.cpp_ns}::NapiInit(env, {reg_obj});",
            )


class NapiPackageHeaderGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager, pkg: PackageDecl):
        self.oc = oc
        self.am = am
        self.pkg = pkg
        pkg_napi_info = PackageNapiInfo.get(self.am, self.pkg)
        self.target = CHeaderWriter(
            self.oc,
            f"include/{pkg_napi_info.header}",
            group=None,
        )

    def gen_package_header(self):
        pkg_napi_info = PackageNapiInfo.get(self.am, self.pkg)
        with self.target:
            self.target.add_include("taihe/runtime_napi.hpp")
            self.target.add_include("taihe/platform/napi.hpp")
            self.target.writelns(
                f"#if __has_include(<napi/native_api.h>)",
                f"#include <napi/native_api.h>",
                f"#elif __has_include(<node/node_api.h>)",
                f"#include <node/node_api.h>",
                f"#else",
                f'#error "Please ensure the napi is correctly installed."',
                f"#endif",
            )
            with self.target.indented(
                f"namespace {pkg_napi_info.cpp_ns} {{",
                f"}}",
                indent="",
            ):
                self.target.writelns(
                    f"TH_VISIBLE napi_value NapiInit(napi_env env, napi_value exports);",
                )


class NapiPackageSourceGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager, pkg: PackageDecl):
        self.oc = oc
        self.am = am
        self.pkg = pkg
        pkg_napi_info = PackageNapiInfo.get(self.am, self.pkg)
        self.target = CSourceWriter(
            self.oc,
            f"src/{pkg_napi_info.source}",
            group=GEN_CXX_SRC_GROUP,
        )

    def gen_package_source(self):
        pkg_napi_info = PackageNapiInfo.get(self.am, self.pkg)
        pkg_cpp_user_info = PackageCppUserInfo.get(self.am, self.pkg)
        with self.target:
            self.target.add_include(pkg_napi_info.header)
            self.target.add_include(pkg_cpp_user_info.header)

            self.gen_func_impls()
            self.gen_type_impls()

            with self.target.indented(
                f"namespace {pkg_napi_info.cpp_ns} {{",
                f"}}",
                indent="",
            ):
                with self.target.indented(
                    f"napi_value NapiInit(napi_env env, napi_value exports) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"if (::taihe::get_env() == nullptr) {{",
                        f"    ::taihe::set_env(env);",
                        f"}}",
                        f"taihe::_init_main_thread();",
                    )
                    for iface in self.pkg.interfaces:
                        self.target.writelns(
                            f"::local::{iface.name}::create(env, exports);",
                        )
                    for struct in self.pkg.structs:
                        self.target.writelns(
                            f"::local::{struct.name}::create(env, exports);",
                        )
                    for enum in self.pkg.enums:
                        self.target.writelns(
                            f"::local::{enum.name}::create(env, exports);",
                        )
                    with self.target.indented(
                        f"napi_property_descriptor desc[] = {{",
                        f"}};",
                    ):
                        for attribute_name, (
                            method,
                            getter,
                            setter,
                        ) in pkg_napi_info.global_register_infos.items():
                            self.target.writelns(
                                f'{{"{attribute_name}", nullptr, {method}, {getter}, {setter}, nullptr, napi_default, nullptr}}, ',
                            )
                    self.target.writelns(
                        f"napi_define_properties(env, exports, {len(pkg_napi_info.global_register_infos)}, desc);",
                        f"return exports;",
                    )

    def gen_type_impls(self):
        with self.target.indented(
            f"namespace local {{",
            f"}}",
            indent="",
        ):
            for enum in self.pkg.enums:
                self.gen_enum(enum)
            for struct in self.pkg.structs:
                self.gen_struct(struct)
            for iface in self.pkg.interfaces:
                self.gen_iface(iface)

    def gen_func_impls(self):
        pkg_napi_info = PackageNapiInfo.get(self.am, self.pkg)
        with self.target.indented(
            f"namespace method {{",
            f"}}",
            indent="",
        ):
            for func in pkg_napi_info.non_ctor_funcs:
                with self.target.indented(
                    f"static napi_value {func.name}(napi_env env, [[maybe_unused]] napi_callback_info info) {{",
                    f"}}",
                ):
                    self.gen_func_content(
                        func,
                    )

    def gen_func_content(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        obj_ptr: str | None = None,
    ):
        if isinstance(func, IfaceMethodDecl):
            func_napi_info = IfaceMethodNapiInfo.get(self.am, func)
            func_abi_info = IfaceMethodAbiInfo.get(self.am, func)
        else:
            func_napi_info = GlobFuncNapiInfo.get(self.am, func)
            func_abi_info = GlobFuncAbiInfo.get(self.am, func)
        if func_napi_info.async_name is not None:
            self.gen_async_func_content(
                func,
                obj_ptr,
                is_noexcept=func_abi_info.is_noexcept,
                is_promise=False,
            )
        elif func_napi_info.promise_name is not None:
            self.gen_async_func_content(
                func,
                obj_ptr,
                is_noexcept=func_abi_info.is_noexcept,
                is_promise=True,
            )
        else:
            self.gen_sync_func_content(
                func,
                obj_ptr,
                is_noexcept=func_abi_info.is_noexcept,
            )

    def get_cpp_func_invoke(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        obj_ptr: str | None,
        cpp_exprs: list[str],
    ) -> str:
        if obj_ptr:
            name = f"({obj_ptr})->{func.name}"
        else:
            assert isinstance(func, GlobFuncDecl)
            name = GlobFuncCppUserInfo.get(self.am, func).full_name
        cpp_exprs_str = ", ".join(cpp_exprs)
        return f"{name}({cpp_exprs_str})"

    def get_cpp_result_type(
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

    def gen_read_func_params(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        args: str,
    ) -> list[str]:
        cpp_exprs = []
        for index, param in enumerate(func.params):
            from_napi = f"from_napi_arg_{param.name}"
            param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
            param_ty_napi_info.gen_from_napi(self.target, from_napi)
            cpp_exprs.append(f"TH_TRY_INTO_NAPI(env, {from_napi}(env, {args}[{index}]))")  # fmt: skip
        return cpp_exprs

    def gen_sync_func_content(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        obj_ptr: str | None,
        *,
        is_noexcept: bool,
    ):
        argc = len(func.params)
        self.target.writelns(
            f"size_t argc = {argc};",
            f"napi_value args[{argc}] = {{}};",
            f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
        )
        cpp_exprs = self.gen_read_func_params(func, "args")
        cpp_result_type = self.get_cpp_result_type(func, is_noexcept)
        func_invoke = self.get_cpp_func_invoke(func, obj_ptr, cpp_exprs)
        result = "cpp_result"
        if cpp_result_type == "void":
            self.target.writelns(
                f"{func_invoke};",
            )
        else:
            self.target.writelns(
                f"{cpp_result_type} {result} = {func_invoke};",
            )
        if not is_noexcept:
            with self.target.indented(
                f"if (not {result}.has_value()) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"::taihe::throw_napi_exception(env, {result}.error());",
                    f"return nullptr;",
                )
            result = f"{result}.value()"
        if isinstance(return_ty := func.return_ty, NonVoidType):
            return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
            return_ty_napi_info.gen_into_napi(self.target, "into_napi_result")
            self.target.writelns(
                f"return into_napi_result(env, std::move({result}));",
            )
        else:
            self.target.writelns(
                f"return nullptr;",
            )

    def gen_async_func_content(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        obj_ptr: str | None,
        *,
        is_noexcept: bool,
        is_promise: bool,
    ):
        argc = len(func.params)
        if not is_promise:
            argc += 1
        self.target.writelns(
            f"size_t argc = {argc};",
            f"napi_value args[{argc}] = {{}};",
            f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
        )
        cpp_exprs = self.gen_read_func_params(func, "args")
        cpp_result_type = self.get_cpp_result_type(func, is_noexcept)
        obj_field = None
        cpp_inputs = []
        result_storage = None
        self.target.add_include("optional")
        with self.target.indented(
            f"struct async_data_ctx {{",
            f"}};",
        ):
            self.target.writelns(
                f"napi_async_work work = nullptr;",
            )
            if is_promise:
                self.target.writelns(
                    f"napi_deferred defer = nullptr;",
                )
            else:
                self.target.writelns(
                    f"napi_ref cb_ref = nullptr;",
                )
            if obj_ptr:
                obj_field = "obj_ptr"
                self.target.writelns(
                    f"decltype({obj_ptr}) {obj_field};",
                )
            for param, cpp_expr in zip(func.params, cpp_exprs, strict=True):
                cpp_input = f"cpp_input_{param.name}"
                cpp_inputs.append(cpp_input)
                self.target.writelns(
                    f"decltype({cpp_expr}) {cpp_input};",
                )
            if cpp_result_type != "void":
                result_storage = "cpp_result"
                self.target.writelns(
                    f"std::optional<{cpp_result_type}> {result_storage};",
                )
        with self.target.indented(
            f"async_data_ctx *cb_data = new async_data_ctx{{",
            f"}};",
        ):
            if obj_field:
                self.target.writelns(
                    f".{obj_field} = {obj_ptr},",
                )
            for cpp_input, cpp_expr in zip(cpp_inputs, cpp_exprs, strict=True):
                self.target.writelns(
                    f".{cpp_input} = {cpp_expr},",
                )
        if is_promise:
            self.target.writelns(
                f"napi_value promise = nullptr;",
                f"TH_NAPI_ASSUME_CALL(env, napi_create_promise(env, &cb_data->defer, &promise));",
            )
        else:
            self.target.writelns(
                f"TH_NAPI_ASSUME_CALL(env, napi_create_reference(env, args[{len(func.params)}], 1, &cb_data->cb_ref));",
            )
        self.target.writelns(
            f"napi_value napi_resname;",
            f'TH_NAPI_ASSUME_CALL(env, napi_create_string_utf8(env, "AsyncCallback", NAPI_AUTO_LENGTH, &napi_resname));',
        )
        with self.target.indented(
            f"TH_NAPI_ASSUME_CALL(env, napi_create_async_work(",
            f"));",
        ):
            self.target.writelns(
                f"env,",
                f"nullptr,",
                f"napi_resname,",
            )
            self.gen_async_func_execute(
                func,
                obj_field,
                cpp_inputs,
                result_storage,
            )
            self.gen_async_func_complete(
                func,
                result_storage,
                is_noexcept=is_noexcept,
                is_promise=is_promise,
            )
            self.target.writelns(
                f"cb_data,",
                f"&cb_data->work",
            )
        self.target.writelns(
            f"TH_NAPI_ASSUME_CALL(env, napi_queue_async_work(env, cb_data->work));",
        )
        if is_promise:
            self.target.writelns(
                f"return promise;",
            )
        else:
            self.target.writelns(
                f"return nullptr;",
            )

    def gen_async_func_execute(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        obj_field: str | None,
        cpp_inputs: list[str],
        result_storage: str | None,
    ):
        with self.target.indented(
            f"[]([[maybe_unused]] napi_env env, void* data) {{",
            f"}},",
        ):
            self.target.writelns(
                f"async_data_ctx *cb_data = reinterpret_cast<async_data_ctx *>(data);",
            )
            obj_ptr = f"cb_data->{obj_field}" if obj_field else None
            cpp_exprs = [
                f"std::forward<decltype(cb_data->{cpp_input})>(cb_data->{cpp_input})"
                for cpp_input in cpp_inputs
            ]
            func_invoke = self.get_cpp_func_invoke(func, obj_ptr, cpp_exprs)
            if result_storage is None:
                self.target.writelns(
                    f"{func_invoke};",
                )
            else:
                self.target.writelns(
                    f"cb_data->{result_storage}.emplace({func_invoke});",
                )

    def gen_async_func_complete(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        result_storage: str | None,
        *,
        is_noexcept: bool,
        is_promise: bool,
    ):
        with self.target.indented(
            f"[](napi_env env, napi_status status, void* data) {{",
            f"}},",
        ):
            self.target.writelns(
                f"async_data_ctx *cb_data = reinterpret_cast<async_data_ctx *>(data);",
            )
            if is_promise:
                reject = lambda error: self.target.writelns(
                    f"TH_NAPI_ASSUME_CALL(env, napi_reject_deferred(env, cb_data->defer, {error}));",
                )
                resolve = lambda value: self.target.writelns(
                    f"TH_NAPI_ASSUME_CALL(env, napi_resolve_deferred(env, cb_data->defer, {value}));",
                )
            else:
                reject = lambda error: self.target.writelns(
                    f"napi_value js_cb;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_get_reference_value(env, cb_data->cb_ref, &js_cb));",
                    f"napi_value undefined_value;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_get_undefined(env, &undefined_value));",
                    f"napi_value argv[1] = {{ {error} }};",
                    f"TH_NAPI_ASSUME_CALL(env, napi_call_function(env, undefined_value, js_cb, 1, argv, nullptr));",
                    f"TH_NAPI_ASSUME_CALL(env, napi_delete_reference(env, cb_data->cb_ref));",
                )
                resolve = lambda value: self.target.writelns(
                    f"napi_value js_cb;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_get_reference_value(env, cb_data->cb_ref, &js_cb));",
                    f"napi_value undefined_value;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_get_undefined(env, &undefined_value));",
                    f"napi_value null_value;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_get_null(env, &null_value));",
                    f"napi_value argv[2] = {{ null_value, {value} }};",
                    f"TH_NAPI_ASSUME_CALL(env, napi_call_function(env, undefined_value, js_cb, 2, argv, nullptr));",
                    f"TH_NAPI_ASSUME_CALL(env, napi_delete_reference(env, cb_data->cb_ref));",
                )
            with self.target.indented(
                f"do {{",
                f"}} while (false);",
            ):
                with self.target.indented(
                    f"if (status == napi_cancelled) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"napi_value error;",
                        f'TH_NAPI_ASSUME_CALL(env, napi_create_string_utf8(env, "Async operation was cancelled", NAPI_AUTO_LENGTH, &error));',
                        f"napi_value error_obj;",
                        f"TH_NAPI_ASSUME_CALL(env, napi_create_error(env, nullptr, error, &error_obj));",
                    )
                    reject("error_obj")
                    self.target.writelns(
                        f"break;",
                    )
                with self.target.indented(
                    f"if (status != napi_ok) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"napi_value error;",
                        f'TH_NAPI_ASSUME_CALL(env, napi_create_string_utf8(env, "Async operation failed", NAPI_AUTO_LENGTH, &error));',
                        f"napi_value error_obj;",
                        f"TH_NAPI_ASSUME_CALL(env, napi_create_error(env, nullptr, error, &error_obj));",
                    )
                    reject("error_obj")
                    self.target.writelns(
                        f"break;",
                    )
                result = f"cb_data->{result_storage}.value()"
                if not is_noexcept:
                    with self.target.indented(
                        f"if (not {result}.has_value()) {{",
                        f"}}",
                    ):
                        self.target.writelns(
                            f"napi_value error_obj = taihe::into_napi_exception(env, {result}.error());",
                        )
                        reject("error_obj")
                        self.target.writelns(
                            f"break;",
                        )
                    result = f"{result}.value()"
                if isinstance(return_ty := func.return_ty, NonVoidType):
                    return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
                    return_ty_napi_info.gen_into_napi(self.target, "into_napi_result")
                    self.target.writelns(
                        f"napi_value napi_result = into_napi_result(env, std::move({result}));",
                    )
                else:
                    self.target.writelns(
                        f"napi_value napi_result;",
                        f"TH_NAPI_ASSUME_CALL(env, napi_get_undefined(env, &napi_result));",
                    )
                resolve("napi_result")
            self.target.writelns(
                f"TH_NAPI_ASSUME_CALL(env, napi_delete_async_work(env, cb_data->work));",
                f"delete cb_data;",
            )

    def gen_struct(self, struct: StructDecl):
        with self.target.indented(
            f"namespace {struct.name} {{",
            f"}}",
        ):
            self.gen_struct_attributes(struct)
            self.gen_struct_inner_constructor(struct)
            self.gen_struct_constructor(struct)
            self.gen_struct_create(struct)

    def gen_struct_attributes(self, struct: StructDecl):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with self.target.indented(
            f"namespace getter {{",
            f"}}",
        ):
            for i, (getter, parts) in enumerate(struct_napi_info.getters):
                field = parts[-1]
                field_ty_napi_info = TypeNapiInfo.get(self.am, field.ty)
                with self.target.indented(
                    f"static napi_value {getter}(napi_env env, napi_callback_info info) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"napi_value thisobj;",
                        f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                        f"{struct_cpp_info.as_owner}* cpp_ptr;",
                        f"TH_NAPI_ASSUME_CALL(env, napi_unwrap(env, thisobj, reinterpret_cast<void **>(&cpp_ptr)));",
                    )
                    field_into_napi = f"into_napi_field_{i}"
                    field_ty_napi_info.gen_into_napi(self.target, field_into_napi)
                    self.target.writelns(
                        f"return {field_into_napi}(env, cpp_ptr->{'.'.join(part.name for part in parts)});",
                    )
        with self.target.indented(
            f"namespace setter {{",
            f"}}",
        ):
            for i, (setter, parts) in enumerate(struct_napi_info.setters):
                field = parts[-1]
                field_ty_napi_info = TypeNapiInfo.get(self.am, field.ty)
                with self.target.indented(
                    f"static napi_value {setter}(napi_env env, napi_callback_info info) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"size_t argc = 1;",
                        f"napi_value args[1] = {{nullptr}};",
                        f"napi_value thisobj;",
                        f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, &argc, args, &thisobj, nullptr));",
                        f"{struct_cpp_info.as_owner}* cpp_ptr;",
                        f"TH_NAPI_ASSUME_CALL(env, napi_unwrap(env, thisobj, reinterpret_cast<void **>(&cpp_ptr)));",
                    )
                    field_from_napi = f"from_napi_field_{i}"
                    field_ty_napi_info.gen_from_napi(self.target, field_from_napi)
                    self.target.writelns(
                        f"cpp_ptr->{'.'.join(part.name for part in parts)} = TH_TRY_INTO_NAPI(env, {field_from_napi}(env, args[0]));",
                        f"return nullptr;",
                    )

    def gen_struct_inner_constructor(self, struct: StructDecl):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with self.target.indented(
            f"inline napi_value inner_constructor(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            argc = len(struct_napi_info.dts_final_fields)
            self.target.writelns(
                f"size_t argc = {argc};",
                f"napi_value args[{argc}];",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
            )
            cpp_exprs = []
            for i, parts in enumerate(struct_napi_info.dts_final_fields):
                final = parts[-1]
                from_napi = f"from_napi_field_{i}"
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                type_napi_info.gen_from_napi(self.target, from_napi)
                cpp_exprs.append(f"TH_TRY_INTO_NAPI(env, {from_napi}(env, args[{i}]))")
            cpp_exprs_str = ", ".join(cpp_exprs)
            self.target.writelns(
                f"napi_value thisobj;",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                f"auto* cpp_ptr = new {struct_cpp_info.as_owner}{{{cpp_exprs_str}}};",
            )
            with self.target.indented(
                f"napi_status status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                self.target.writelns(
                    f"delete static_cast<{struct_cpp_info.as_owner}*>(finalize_data);",
                )
            with self.target.indented(
                f"if (status != napi_ok) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"delete cpp_ptr;",
                    f'TH_NAPI_ASSUME_CALL(env, napi_throw_error(env, nullptr, ("Native object wrapping failed (status " + std::to_string(status) + ")").c_str()));',
                    f"return nullptr;",
                )
            self.target.writelns(
                f"return thisobj;",
            )

    def gen_struct_constructor(self, struct: StructDecl):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with self.target.indented(
            f"inline napi_value constructor(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            if (ctor := struct_napi_info.ctor) is None:
                self.target.writelns(
                    f'TH_NAPI_ASSUME_CALL(env, napi_throw_error(env, nullptr, "Constructor does not exist for class {struct_napi_info.dts_type_name}"));',
                    f"return nullptr;",
                )
                return
            ctor_abi_info = GlobFuncAbiInfo.get(self.am, ctor)
            ctor_cpp_user_info = GlobFuncCppUserInfo.get(self.am, ctor)
            argc = len(ctor.params)
            self.target.writelns(
                f"size_t argc = {argc};",
                f"napi_value args[{argc}];",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
            )
            cpp_exprs = self.gen_read_func_params(ctor, "args")
            cpp_result_type = self.get_cpp_result_type(ctor, ctor_abi_info.is_noexcept)
            cpp_exprs_str = ", ".join(cpp_exprs)
            result = "cpp_result"
            self.target.writelns(
                f"{cpp_result_type} {result} = {ctor_cpp_user_info.full_name}({cpp_exprs_str});",
            )
            if not ctor_abi_info.is_noexcept:
                with self.target.indented(
                    f"if (!{result}) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"::taihe::throw_napi_exception(env, {result}.error());",
                        f"return nullptr;",
                    )
                result = f"{result}.value()"
            self.target.writelns(
                f"napi_value thisobj;",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                f"auto* cpp_ptr = new {struct_cpp_info.as_owner}(std::move({result}));",
            )
            with self.target.indented(
                f"napi_status status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                self.target.writelns(
                    f"delete static_cast<{struct_cpp_info.as_owner}*>(finalize_data);",
                )
            with self.target.indented(
                f"if (status != napi_ok) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"delete cpp_ptr;",
                    f'TH_NAPI_ASSUME_CALL(env, napi_throw_error(env, nullptr, ("Native object wrapping failed (status " + std::to_string(status) + ")").c_str()));',
                    f"return nullptr;",
                )
            self.target.writelns(
                f"return thisobj;",
            )

    def gen_struct_create(self, struct: StructDecl):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        # create function
        with self.target.indented(
            f"inline void create(napi_env env, [[maybe_unused]] napi_value exports) {{",
            f"}}",
        ):
            self.target.add_include(struct_napi_info.decl_header)
            with self.target.indented(
                f"napi_property_descriptor desc[] = {{",
                f"}};",
            ):
                for attribute_name, (
                    method,
                    getter,
                    setter,
                ) in struct_napi_info.register_infos.items():
                    self.target.writelns(
                        f'{{"{attribute_name}", nullptr, {method}, {getter}, {setter}, nullptr, napi_default, nullptr}}, ',
                    )
                for attribute_name, (
                    method,
                    getter,
                    setter,
                ) in struct_napi_info.static_register_infos.items():
                    self.target.writelns(
                        f'{{"{attribute_name}", nullptr, {method}, {getter}, {setter}, nullptr, napi_static, nullptr}}, ',
                    )
            self.target.writelns(
                f"napi_value global;",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_global(env, &global));",
                f"napi_value object_ctor;",
                f'TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, global, "Object", &object_ctor));',
                f"napi_value set_proto_fn;",
                f'TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, object_ctor, "setPrototypeOf", &set_proto_fn));',
            )
            self.target.writelns(
                f"napi_value ctor = nullptr;",
                f'TH_NAPI_ASSUME_CALL(env, napi_define_class(env, "{struct_napi_info.dts_type_name}", NAPI_AUTO_LENGTH, constructor, nullptr, {len(struct_napi_info.register_infos) + len(struct_napi_info.static_register_infos)}, desc, &ctor));',
                f"TH_NAPI_ASSUME_CALL(env, napi_create_reference(env, ctor, 1, &::taihe::into_napi_t<{struct_cpp_info.as_owner}>::ctor_ref));",
            )
            if struct_napi_info.is_class():
                self.target.writelns(
                    f'TH_NAPI_ASSUME_CALL(env, napi_set_named_property(env, exports, "{struct_napi_info.dts_type_name}", ctor));',
                )
            self.target.writelns(
                f"napi_value inner_ctor = nullptr;",
                f'TH_NAPI_ASSUME_CALL(env, napi_define_class(env, "{struct_napi_info.dts_type_name}", NAPI_AUTO_LENGTH, inner_constructor, nullptr, 0, nullptr, &inner_ctor));',
                f"TH_NAPI_ASSUME_CALL(env, napi_create_reference(env, inner_ctor, 1, &::taihe::into_napi_t<{struct_cpp_info.as_owner}>::inner_ctor_ref));",
                f"napi_value proto;",
                f'TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, ctor, "prototype", &proto));',
                f"napi_value inner_proto;",
                f'TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, inner_ctor, "prototype", &inner_proto));',
                f"napi_value inner_proto_set_proto_args[2] = {{inner_proto, proto}};",
                f"napi_value inner_proto_set_proto_result;",
                f"TH_NAPI_ASSUME_CALL(env, napi_call_function(env, global, set_proto_fn, 2, inner_proto_set_proto_args, &inner_proto_set_proto_result));",
                f"napi_value inner_ctor_set_proto_args[2] = {{inner_ctor, ctor}};",
                f"napi_value inner_ctor_set_proto_result;",
                f"TH_NAPI_ASSUME_CALL(env, napi_call_function(env, global, set_proto_fn, 2, inner_ctor_set_proto_args, &inner_ctor_set_proto_result));",
            )
            if parent := struct_napi_info.dts_class_parent:
                parent_cpp_info = StructCppInfo.get(self.am, parent.ty.decl)  # type: ignore
                parent_napi_info = StructNapiInfo.get(self.am, parent.ty.decl)  # type: ignore
                self.target.add_include(parent_napi_info.decl_header)
                self.target.writelns(
                    f"napi_value parent_ctor;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_get_reference_value(env, ::taihe::into_napi_t<{parent_cpp_info.as_owner}>::ctor_ref, &parent_ctor));",
                    f"napi_value parent_proto;",
                    f'TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, parent_ctor, "prototype", &parent_proto));',
                    f"napi_value proto_set_proto_args[2] = {{proto, parent_proto}};",
                    f"napi_value proto_set_proto_result;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_call_function(env, global, set_proto_fn, 2, proto_set_proto_args, &proto_set_proto_result));",
                    f"napi_value ctor_set_proto_args[2] = {{ctor, parent_ctor}};",
                    f"napi_value ctor_set_proto_result;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_call_function(env, global, set_proto_fn, 2, ctor_set_proto_args, &ctor_set_proto_result));",
                )

    def gen_iface(self, iface: IfaceDecl):
        with self.target.indented(
            f"namespace {iface.name} {{",
            f"}}",
        ):
            self.gen_iface_method_impls(iface)
            self.gen_iface_inner_constructor(iface)
            self.gen_iface_constructor(iface)
            self.gen_iface_create(iface)

    def gen_iface_inner_constructor(self, iface: IfaceDecl):
        iface_abi_info = IfaceAbiInfo.get(self.am, iface)
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        with self.target.indented(
            f"inline napi_value inner_constructor(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            argc = 2
            self.target.writelns(
                f"size_t argc = {argc};",
                f"napi_value args[{argc}];",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
            )
            self.target.writelns(
                f"int64_t vtbl_ptr;",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_value_int64(env, args[0], &vtbl_ptr));",
                f"{iface_abi_info.vtable}* cpp_vtbl_ptr = reinterpret_cast<{iface_abi_info.vtable}*>(vtbl_ptr);",
                f"int64_t data_ptr;",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_value_int64(env, args[1], &data_ptr));",
                f"DataBlockHead* cpp_data_ptr = reinterpret_cast<DataBlockHead*>(data_ptr);",
            )
            self.target.writelns(
                f"napi_value thisobj;",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                f"auto* cpp_ptr = new {iface_cpp_info.as_owner}({{cpp_vtbl_ptr, cpp_data_ptr}});",
            )
            with self.target.indented(
                f"napi_status status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                self.target.writelns(
                    f"delete static_cast<{iface_cpp_info.as_owner}*>(finalize_data);",
                )
            with self.target.indented(
                f"if (status != napi_ok) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"delete cpp_ptr;",
                    f'TH_NAPI_ASSUME_CALL(env, napi_throw_error(env, nullptr, ("Native object wrapping failed (status " + std::to_string(status) + ")").c_str()));',
                    f"return nullptr;",
                )
            self.target.writelns(
                f"return thisobj;",
            )

    def gen_iface_constructor(self, iface: IfaceDecl):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        with self.target.indented(
            f"inline napi_value constructor(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            if (ctor := iface_napi_info.ctor) is None:
                self.target.writelns(
                    f'TH_NAPI_ASSUME_CALL(env, napi_throw_error(env, nullptr, "Constructor does not exist for class {iface_napi_info.dts_type_name}"));',
                    f"return nullptr;",
                )
                return
            ctor_abi_info = GlobFuncAbiInfo.get(self.am, ctor)
            ctor_cpp_user_info = GlobFuncCppUserInfo.get(self.am, ctor)
            argc = len(ctor.params)
            self.target.writelns(
                f"size_t argc = {argc};",
                f"napi_value args[{argc}];",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
            )
            cpp_exprs = self.gen_read_func_params(ctor, "args")
            cpp_result_type = self.get_cpp_result_type(ctor, ctor_abi_info.is_noexcept)
            cpp_exprs_str = ", ".join(cpp_exprs)
            result = "cpp_result"
            self.target.writelns(
                f"{cpp_result_type} {result} = {ctor_cpp_user_info.full_name}({cpp_exprs_str});",
            )
            if not ctor_abi_info.is_noexcept:
                with self.target.indented(
                    f"if (!{result}) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"::taihe::throw_napi_exception(env, {result}.error());",
                        f"return nullptr;",
                    )
                result = f"{result}.value()"
            self.target.writelns(
                f"napi_value thisobj;",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                f"auto* cpp_ptr = new {iface_cpp_info.as_owner}(std::move({result}));",
            )
            with self.target.indented(
                f"napi_status status = napi_wrap(env, thisobj, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                self.target.writelns(
                    f"delete static_cast<{iface_cpp_info.as_owner}*>(finalize_data);",
                )
            with self.target.indented(
                f"if (status != napi_ok) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"delete cpp_ptr;",
                    f'TH_NAPI_ASSUME_CALL(env, napi_throw_error(env, nullptr, ("Native object wrapping failed (status " + std::to_string(status) + ")").c_str()));',
                    f"return nullptr;",
                )
            self.target.writelns(
                f"return thisobj;",
            )

    def gen_iface_create(self, iface: IfaceDecl):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        # create function
        with self.target.indented(
            f"inline void create(napi_env env, [[maybe_unused]] napi_value exports) {{",
            f"}}",
        ):
            self.target.add_include(iface_napi_info.decl_header)
            with self.target.indented(
                f"napi_property_descriptor desc[] = {{",
                f"}};",
            ):
                for attribute_name, (
                    method,
                    getter,
                    setter,
                ) in iface_napi_info.register_infos.items():
                    self.target.writelns(
                        f'{{"{attribute_name}", nullptr, {method}, {getter}, {setter}, nullptr, napi_default, nullptr}}, '
                    )
                for attribute_name, (
                    method,
                    getter,
                    setter,
                ) in iface_napi_info.static_register_infos.items():
                    self.target.writelns(
                        f'{{"{attribute_name}", nullptr, {method}, {getter}, {setter}, nullptr, napi_static, nullptr}}, ',
                    )
            self.target.writelns(
                f"napi_value global;",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_global(env, &global));",
                f"napi_value object_ctor;",
                f'TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, global, "Object", &object_ctor));',
                f"napi_value set_proto_fn;",
                f'TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, object_ctor, "setPrototypeOf", &set_proto_fn));',
            )
            self.target.writelns(
                f"napi_value ctor = nullptr;",
                f'TH_NAPI_ASSUME_CALL(env, napi_define_class(env, "{iface_napi_info.dts_type_name}", NAPI_AUTO_LENGTH, constructor, nullptr, {len(iface_napi_info.register_infos) + len(iface_napi_info.static_register_infos)}, desc, &ctor));',
                f"TH_NAPI_ASSUME_CALL(env, napi_create_reference(env, ctor, 1, &::taihe::into_napi_t<{iface_cpp_info.as_owner}>::ctor_ref));",
            )
            if iface_napi_info.is_class():
                self.target.writelns(
                    f'TH_NAPI_ASSUME_CALL(env, napi_set_named_property(env, exports, "{iface_napi_info.dts_type_name}", ctor));',
                )
            self.target.writelns(
                f"napi_value inner_ctor = nullptr;",
                f'TH_NAPI_ASSUME_CALL(env, napi_define_class(env, "{iface_napi_info.dts_type_name}", NAPI_AUTO_LENGTH, inner_constructor, nullptr, 0, nullptr, &inner_ctor));',
                f"TH_NAPI_ASSUME_CALL(env, napi_create_reference(env, inner_ctor, 1, &::taihe::into_napi_t<{iface_cpp_info.as_owner}>::inner_ctor_ref));",
                f"napi_value proto;",
                f'TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, ctor, "prototype", &proto));',
                f"napi_value inner_proto;",
                f'TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, inner_ctor, "prototype", &inner_proto));',
                f"napi_value inner_proto_set_proto_args[2] = {{inner_proto, proto}};",
                f"napi_value inner_proto_set_proto_result;",
                f"TH_NAPI_ASSUME_CALL(env, napi_call_function(env, global, set_proto_fn, 2, inner_proto_set_proto_args, &inner_proto_set_proto_result));",
                f"napi_value inner_ctor_set_proto_args[2] = {{inner_ctor, ctor}};",
                f"napi_value inner_ctor_set_proto_result;",
                f"TH_NAPI_ASSUME_CALL(env, napi_call_function(env, global, set_proto_fn, 2, inner_ctor_set_proto_args, &inner_ctor_set_proto_result));",
            )
            if parent := iface_napi_info.dts_class_parent:
                parent_cpp_info = IfaceCppInfo.get(self.am, parent.ty.decl)
                parent_napi_info = IfaceNapiInfo.get(self.am, parent.ty.decl)
                self.target.add_include(parent_napi_info.decl_header)
                self.target.writelns(
                    f"napi_value parent_ctor;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_get_reference_value(env, ::taihe::into_napi_t<{parent_cpp_info.as_owner}>::ctor_ref, &parent_ctor));",
                    f"napi_value parent_proto;",
                    f'TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, parent_ctor, "prototype", &parent_proto));',
                    f"napi_value proto_set_proto_args[2] = {{proto, parent_proto}};",
                    f"napi_value proto_set_proto_result;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_call_function(env, global, set_proto_fn, 2, proto_set_proto_args, &proto_set_proto_result));",
                    f"napi_value ctor_set_proto_args[2] = {{ctor, parent_ctor}};",
                    f"napi_value ctor_set_proto_result;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_call_function(env, global, set_proto_fn, 2, ctor_set_proto_args, &ctor_set_proto_result));",
                )

    def gen_iface_method_impls(self, iface: IfaceDecl):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        with self.target.indented(
            f"namespace method {{",
            f"}}",
        ):
            for name, method in iface_napi_info.methods:
                ancestor_cpp_info = IfaceCppInfo.get(self.am, method.parent_iface)
                with self.target.indented(
                    f"static napi_value {name}(napi_env env, napi_callback_info info) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"napi_value thisobj;",
                        f"TH_NAPI_ASSUME_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr));",
                        f"{iface_cpp_info.as_owner}* obj_ptr;",
                        f"TH_NAPI_ASSUME_CALL(env, napi_unwrap(env, thisobj, reinterpret_cast<void**>(&obj_ptr)));",
                    )
                    self.gen_func_content(
                        method,
                        f"({ancestor_cpp_info.as_param})*obj_ptr",
                    )

    def gen_enum(self, enum: EnumDecl):
        with self.target.indented(
            f"namespace {enum.name} {{",
            f"}}",
        ):
            self.gen_enum_create(enum)

    def gen_enum_create(self, enum: EnumDecl):
        with self.target.indented(
            f"inline void create(napi_env env, [[maybe_unused]] napi_value exports) {{",
            f"}}",
        ):
            enum_cpp_info = EnumCppInfo.get(self.am, enum)
            enum_napi_info = EnumNapiInfo.get(self.am, enum)
            item_ty_napi_info = TypeNapiInfo.get(self.am, enum.ty)
            item_ty_napi_info.gen_into_napi(self.target, "into_napi_enum_item")
            if enum_napi_info.is_literal:
                for item in enum.items:
                    value = f"value_{item.name}"
                    self.target.writelns(
                        f"napi_value {value} = into_napi_enum_item(env, {enum_cpp_info.full_name}({enum_cpp_info.full_name}::key_t::{item.name}).get_owner());",
                    )
                    self.target.writelns(
                        f'TH_NAPI_ASSUME_CALL(env, napi_set_named_property(env, exports, "{item.name}", {value}));',
                    )
            else:
                self.target.writelns(
                    f"napi_value enum_obj;",
                    f"TH_NAPI_ASSUME_CALL(env, napi_create_object(env, &enum_obj));",
                    f"napi_value key;",
                )
                for item in enum.items:
                    value = f"value_{item.name}"
                    self.target.writelns(
                        f"napi_value {value} = into_napi_enum_item(env, {enum_cpp_info.full_name}({enum_cpp_info.full_name}::key_t::{item.name}).get_owner());",
                    )
                    self.target.writelns(
                        f'TH_NAPI_ASSUME_CALL(env, napi_create_string_utf8(env, "{item.name}", NAPI_AUTO_LENGTH, &key));',
                        f'TH_NAPI_ASSUME_CALL(env, napi_set_named_property(env, enum_obj, "{item.name}", {value}));',
                        f"TH_NAPI_ASSUME_CALL(env, napi_set_property(env, enum_obj, {value}, key));",
                    )
                self.target.writelns(
                    f'TH_NAPI_ASSUME_CALL(env, napi_set_named_property(env, exports, "{enum_napi_info.dts_type_name}", enum_obj));',
                )


class NapiStructDeclGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager, struct: StructDecl):
        self.oc = oc
        self.am = am
        self.struct = struct
        struct_napi_info = StructNapiInfo.get(self.am, self.struct)
        self.target = CHeaderWriter(
            self.oc,
            f"include/{struct_napi_info.decl_header}",
            group=None,
        )

    def gen_struct_conv_decl_file(self):
        struct_cpp_info = StructCppInfo.get(self.am, self.struct)
        with self.target:
            self.target.add_include("taihe/platform/napi.hpp")
            self.target.add_include("taihe/runtime_napi.hpp")
            self.target.add_include(struct_cpp_info.defn_header)
            with self.target.indented(
                f"template<> struct ::taihe::from_napi_t<{struct_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline ::taihe::expected<{struct_cpp_info.as_owner}, ::taihe::error> operator()(napi_env env, napi_value napi_obj) const;",
                )
            with self.target.indented(
                f"template<> struct ::taihe::into_napi_t<{struct_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"static inline napi_ref ctor_ref = nullptr;",
                    f"static inline napi_ref inner_ctor_ref = nullptr;",
                    f"inline napi_value operator()(napi_env env, {struct_cpp_info.as_param} cpp_obj) const;",
                )


class NapiStructImplGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager, struct: StructDecl):
        self.oc = oc
        self.am = am
        self.struct = struct
        struct_napi_info = StructNapiInfo.get(self.am, self.struct)
        self.target = CHeaderWriter(
            self.oc,
            f"include/{struct_napi_info.impl_header}",
            group=None,
        )

    def gen_struct_conv_impl_file(self):
        struct_cpp_info = StructCppInfo.get(self.am, self.struct)
        struct_napi_info = StructNapiInfo.get(self.am, self.struct)
        with self.target:
            self.target.add_include(struct_napi_info.decl_header)
            self.target.add_include(struct_cpp_info.impl_header)
            self.gen_struct_from_napi_func()
            self.gen_struct_into_napi_func()

    def gen_struct_from_napi_func(self):
        struct_cpp_info = StructCppInfo.get(self.am, self.struct)
        struct_napi_info = StructNapiInfo.get(self.am, self.struct)
        with self.target.indented(
            f"inline ::taihe::expected<{struct_cpp_info.as_owner}, ::taihe::error> taihe::from_napi_t<{struct_cpp_info.as_owner}>::operator()(napi_env env, napi_value napi_obj) const {{",
            f"}}",
        ):
            cpp_fields = []
            for i, parts in enumerate(struct_napi_info.dts_final_fields):
                final = parts[-1]
                napi_field = f"napi_field_{i}"
                self.target.writelns(
                    f"napi_value {napi_field} = nullptr;",
                    f'TH_NAPI_TRY_CALL(env, napi_get_named_property(env, napi_obj, "{final.name}", &{napi_field}));',
                )
                from_napi = f"from_napi_field_{i}"
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                type_napi_info.gen_from_napi(self.target, from_napi)
                cpp_fields.append(f"TH_TRY({from_napi}(env, {napi_field}))")
            cpp_fields_str = ", ".join(cpp_fields)
            self.target.writelns(
                f"return {struct_cpp_info.as_owner}{{{cpp_fields_str}}};",
            )

    def gen_struct_into_napi_func(self):
        struct_cpp_info = StructCppInfo.get(self.am, self.struct)
        struct_napi_info = StructNapiInfo.get(self.am, self.struct)
        with self.target.indented(
            f"inline napi_value taihe::into_napi_t<{struct_cpp_info.as_owner}>::operator()(napi_env env, {struct_cpp_info.as_param} cpp_obj) const {{",
            f"}}",
        ):
            argc = len(struct_napi_info.dts_final_fields)
            self.target.writelns(
                f"napi_value args[{argc}];",
            )
            for i, parts in enumerate(struct_napi_info.dts_final_fields):
                final = parts[-1]
                into_napi = f"into_napi_field_{i}"
                type_napi_info = TypeNapiInfo.get(self.am, final.ty)
                type_napi_info.gen_into_napi(self.target, into_napi)
                self.target.writelns(
                    f"args[{i}] = {into_napi}(env, cpp_obj.{'.'.join(part.name for part in parts)});",
                )
            self.target.writelns(
                f"napi_value napi_obj = nullptr;",
                f"napi_value inner_ctor = nullptr;",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_reference_value(env, inner_ctor_ref, &inner_ctor));",
                f"TH_NAPI_ASSUME_CALL(env, napi_new_instance(env, inner_ctor, {argc}, args, &napi_obj));",
                f"return napi_obj;",
            )


class NapiUnionDeclGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager, union: UnionDecl):
        self.oc = oc
        self.am = am
        self.union = union
        union_napi_info = UnionNapiInfo.get(self.am, self.union)
        self.target = CHeaderWriter(
            self.oc,
            f"include/{union_napi_info.decl_header}",
            group=None,
        )

    def gen_union_conv_decl_file(self):
        union_cpp_info = UnionCppInfo.get(self.am, self.union)
        with self.target:
            self.target.add_include("taihe/platform/napi.hpp")
            self.target.add_include(union_cpp_info.defn_header)
            with self.target.indented(
                f"template<> struct ::taihe::from_napi_t<{union_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline ::taihe::expected<{union_cpp_info.as_owner}, ::taihe::error> operator()(napi_env env, napi_value napi_obj) const;",
                )
            with self.target.indented(
                f"template<> struct ::taihe::into_napi_t<{union_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline napi_value operator()(napi_env env, {union_cpp_info.as_param} cpp_obj) const;",
                )


class NapiUnionImplGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager, union: UnionDecl):
        self.oc = oc
        self.am = am
        self.union = union
        union_napi_info = UnionNapiInfo.get(self.am, self.union)
        self.target = CHeaderWriter(
            self.oc,
            f"include/{union_napi_info.impl_header}",
            group=None,
        )

    def gen_union_conv_impl_file(self):
        union_cpp_info = UnionCppInfo.get(self.am, self.union)
        union_napi_info = UnionNapiInfo.get(self.am, self.union)
        with self.target:
            self.target.add_include(union_napi_info.decl_header)
            self.target.add_include(union_cpp_info.impl_header)
            self.gen_union_from_napi_func()
            self.gen_union_into_napi_func()

    def gen_union_from_napi_func(self):
        union_cpp_info = UnionCppInfo.get(self.am, self.union)
        union_napi_info = UnionNapiInfo.get(self.am, self.union)
        with self.target.indented(
            f"inline ::taihe::expected<{union_cpp_info.as_owner}, ::taihe::error> taihe::from_napi_t<{union_cpp_info.as_owner}>::operator()(napi_env env, napi_value napi_obj) const {{",
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
                type_napi_info.gen_check_napi(self.target, check_napi)
                with self.target.indented(
                    f"if ({check_napi}(env, napi_obj)) {{",
                    f"}}",
                ):
                    from_napi = f"from_napi_kind_{i}"
                    type_napi_info.gen_from_napi(self.target, from_napi)
                    self.target.writelns(
                        f"return {union_cpp_info.full_name}({static_tags_str}, TH_TRY({from_napi}(env, napi_obj)));",
                    )

    def gen_union_into_napi_func(self):
        union_cpp_info = UnionCppInfo.get(self.am, self.union)
        with self.target.indented(
            f"inline napi_value taihe::into_napi_t<{union_cpp_info.as_owner}>::operator()(napi_env env, {union_cpp_info.as_param} cpp_value) const {{",
            f"}}",
        ):
            with self.target.indented(
                f"switch (cpp_value.get_tag()) {{",
                f"}}",
            ):
                for field in self.union.fields:
                    tag = f"{union_cpp_info.full_name}::tag_t::{field.name}"
                    self.target.write_label(f"case {tag}:")
                    with self.target.indented(
                        f"{{",
                        f"}}",
                    ):
                        into_napi = f"into_napi_kind_{field.name}"
                        type_napi_info = TypeNapiInfo.get(self.am, field.ty)
                        type_napi_info.gen_into_napi(self.target, into_napi)
                        self.target.writelns(
                            f"return {into_napi}(env, cpp_value.get_{field.name}_ref());",
                        )


class NapiIfaceDeclGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager, iface: IfaceDecl):
        self.oc = oc
        self.am = am
        self.iface = iface
        iface_napi_info = IfaceNapiInfo.get(self.am, self.iface)
        self.target = CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.decl_header}",
            group=None,
        )

    def gen_iface_conv_decl_file(self):
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        with self.target:
            self.target.add_include("taihe/platform/napi.hpp")
            self.target.add_include("taihe/runtime_napi.hpp")
            self.target.add_include(iface_cpp_info.defn_header)
            with self.target.indented(
                f"template<> struct ::taihe::from_napi_t<{iface_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline ::taihe::expected<{iface_cpp_info.as_owner}, ::taihe::error> operator()(napi_env env, napi_value napi_obj) const;",
                )
            with self.target.indented(
                f"template<> struct ::taihe::into_napi_t<{iface_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"static inline napi_ref ctor_ref = nullptr;",
                    f"static inline napi_ref inner_ctor_ref = nullptr;",
                    f"inline napi_value operator()(napi_env env, {iface_cpp_info.as_owner} cpp_obj) const;",
                )


class NapiIfaceImplGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager, iface: IfaceDecl):
        self.oc = oc
        self.am = am
        self.iface = iface
        iface_napi_info = IfaceNapiInfo.get(self.am, self.iface)
        self.target = CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.impl_header}",
            group=None,
        )

    def gen_iface_conv_impl_file(self):
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, self.iface)
        with self.target:
            self.target.add_include(iface_napi_info.decl_header)
            self.target.add_include(iface_cpp_info.impl_header)
            self.gen_iface_from_napi_func()
            self.gen_iface_into_napi_func()

    def gen_iface_from_napi_func(self):
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        iface_abi_info = IfaceAbiInfo.get(self.am, self.iface)
        with self.target.indented(
            f"inline ::taihe::expected<{iface_cpp_info.as_owner}, ::taihe::error> taihe::from_napi_t<{iface_cpp_info.as_owner}>::operator()(napi_env env, napi_value napi_obj) const {{",
            f"}}",
        ):
            with self.target.indented(
                f"struct cpp_impl_t: ::taihe::napi_ref_guard {{",
                f"}};",
            ):
                self.target.writelns(
                    f"using ::taihe::napi_ref_guard::napi_ref_guard;",
                )
                for ancestor in iface_abi_info.ancestor_infos:
                    for method in ancestor.methods:
                        self.gen_iface_method_from_napi(method)
            self.target.writelns(
                f"return taihe::make_holder<cpp_impl_t, {iface_cpp_info.as_owner}, ::taihe::platform::napi::NapiObject>(env, napi_obj);",
            )

    def gen_iface_method_from_napi(self, method: IfaceMethodDecl):
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
        with self.target.indented(
            f"{return_ty_cpp_name} {method_cpp_info.impl_name}({method_params_str}) {{",
            f"}}",
        ):
            method_napi_info = IfaceMethodNapiInfo.get(self.am, method)
            if (napi_name := method_napi_info.norm_name) is None:
                # TODO: support generating reverse call for getter/setter/async method
                self.target.writelns(
                    f'TH_THROW(std::runtime_error, "not supported");',
                )
                return
            with self.target.indented(
                f"return this->sync_call(",
                f");",
            ):
                self.write_sync_call_lambda(method, napi_name)
                for method_arg in method_args:
                    self.target.writelns(
                        f", std::forward<decltype({method_arg})>({method_arg})",
                    )

    def write_sync_call_lambda(self, method: IfaceMethodDecl, napi_name: str):
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
        with self.target.indented(
            f"[]({method_params_str}) -> {return_ty_cpp_name} {{",
            f"}}",
        ):
            self.target.writelns(
                f"napi_value args[{len(method.params)}];",
            )
            for index, (param, method_arg) in enumerate(
                zip(method.params, method_args, strict=True)
            ):
                param_napi_type_info = TypeNapiInfo.get(self.am, param.ty)
                into_napi = f"into_napi_arg_{param.name}"
                param_napi_type_info.gen_into_napi(self.target, into_napi)
                self.target.writelns(
                    f"args[{index}] = {into_napi}(env, std::forward<decltype({method_arg})>({method_arg}));",
                )
            if method_abi_info.is_noexcept:
                napi_call_macro = "TH_NAPI_ASSUME_CALL"
                return_macro = "TH_NAPI_ASSUME"
            else:
                napi_call_macro = "TH_NAPI_TRY_CALL"
                return_macro = "TH_TRY"
            self.target.writelns(
                f"napi_value org_napi_obj;",
                f"{napi_call_macro}(env, napi_get_reference_value(env, ref, &org_napi_obj));",
                f"napi_value ts_method;",
                f'{napi_call_macro}(env, napi_get_named_property(env, org_napi_obj, "{napi_name}", &ts_method));',
                f"napi_value method_result_napi;",
                f"{napi_call_macro}(env, napi_call_function(env, org_napi_obj, ts_method, {len(method.params)}, args, &method_result_napi));",
            )
            if isinstance(return_ty := method.return_ty, NonVoidType):
                return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
                return_ty_napi_info.gen_from_napi(self.target, "from_napi_result")
                self.target.writelns(
                    f"return {return_macro}(from_napi_result(env, method_result_napi));",
                )
            elif not method_abi_info.is_noexcept:
                self.target.writelns(
                    f"return {{}};",
                )
            else:
                self.target.writelns(
                    f"return;",
                )

    def gen_iface_into_napi_func(self):
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        with self.target.indented(
            f"inline napi_value taihe::into_napi_t<{iface_cpp_info.as_owner}>::operator()(napi_env env, {iface_cpp_info.as_owner} cpp_obj) const {{",
            f"}}",
        ):
            argc = 2
            self.target.writelns(
                f"napi_value args[{argc}];",
            )
            self.target.writelns(
                f"int64_t cpp_vtbl_ptr = reinterpret_cast<int64_t>(cpp_obj.m_handle.vtbl_ptr);",
                f"int64_t cpp_data_ptr = reinterpret_cast<int64_t>(cpp_obj.m_handle.data_ptr);",
                f"cpp_obj.m_handle.data_ptr = nullptr;",
                f"TH_NAPI_ASSUME_CALL(env, napi_create_int64(env, cpp_vtbl_ptr, &args[0]));",
                f"TH_NAPI_ASSUME_CALL(env, napi_create_int64(env, cpp_data_ptr, &args[1]));",
            )
            self.target.writelns(
                f"napi_value napi_obj = nullptr;",
                f"napi_value inner_ctor = nullptr;",
                f"TH_NAPI_ASSUME_CALL(env, napi_get_reference_value(env, inner_ctor_ref, &inner_ctor));",
                f"TH_NAPI_ASSUME_CALL(env, napi_new_instance(env, inner_ctor, {argc}, args, &napi_obj));",
                f"return napi_obj;",
            )
