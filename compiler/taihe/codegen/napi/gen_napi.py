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

from json import dumps

from taihe.codegen.abi.analyses import (
    GlobFuncAbiInfo,
    IfaceAbiInfo,
    IfaceMethodAbiInfo,
)
from taihe.codegen.abi.writer import CHeaderWriter, CSourceWriter
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
        self.gen_utils_file()

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
                        self.gen_func(func, pkg_napi_info, pkg_napi_target, func.name)
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

    def gen_utils_file(self):
        """Generate util functions for main thread."""
        with CHeaderWriter(
            self.oc,
            f"include/napi_utils.hpp",
            group=None,
        ) as target:
            target.add_include("taihe/array.hpp")
            target.add_include("mutex")
            target.add_include("condition_variable")
            target.add_include("pthread.h")
            target.writelns(
                f"namespace taihe {{",
                f"class ThreadContext {{",
                f"public:",
                f"    static ThreadContext& get_instance() {{",
                f"        static ThreadContext instance;",
                f"        return instance;",
                f"    }}",
                f"    void init_main_thread_id() {{",
                f"        static std::once_flag flag;",
                f"        std::call_once(flag, [this]() {{",
                f"            main_thread_id_ = pthread_self();",
                f"            initialized_ = true;",
                f"        }});",
                f"    }}",
                f"    bool _is_main_thread() const {{",
                f"        if (!initialized_) {{",
                f"            return false;",
                f"        }}",
                f"        return pthread_equal(pthread_self(), main_thread_id_) != 0;",
                f"    }}",
                f"    ThreadContext(const ThreadContext&) = delete;",
                f"    ThreadContext& operator=(const ThreadContext&) = delete;",
                f"private:",
                f"    ThreadContext() = default;",
                f"    pthread_t main_thread_id_;",
                f"    bool initialized_ = false;",
                f"}};",
                f"inline bool _is_main_thread() {{",
                f"    return ThreadContext::get_instance()._is_main_thread();",
                f"}}",
                f"inline void _init_main_thread() {{",
                f"    ThreadContext::get_instance().init_main_thread_id();",
                f"}}",
                f"inline bool _get_bigint_msb(uint64_t dig) {{",
                f"    return dig >> (sizeof(uint64_t) * 8 - 1) != 0;",
                f"}}",
                f"inline bool _get_bigint_sign(taihe::array_view<uint64_t> num) {{",
                f"    return _get_bigint_msb(num[num.size() - 1]);",
                f"}}",
                f"inline std::pair<bool, taihe::array<uint64_t>> _get_bigint_sign_and_abs(taihe::array_view<uint64_t> num) {{",
                f"    uint64_t *buf = reinterpret_cast<uint64_t *>(malloc(num.size() * sizeof(uint64_t)));",
                f"    bool sign = _get_bigint_msb(num[num.size() - 1]);",
                f"    if (sign) {{",
                f"        bool carry = true;",
                f"        for (std::size_t i = 0; i < num.size(); i++) {{",
                f"            buf[i] = ~num[i] + carry;",
                f"            carry = carry && (buf[i] == 0);",
                f"        }}",
                f"    }} else {{",
                f"        for (std::size_t i = 0; i < num.size(); i++) {{",
                f"            buf[i] = num[i];",
                f"        }}",
                f"    }}",
                f"    std::size_t size = num.size();",
                f"    while (size > 0 && buf[size - 1] == 0) {{",
                f"        size--;",
                f"    }}",
                f"    return {{sign, taihe::array<uint64_t>(buf, size)}};",
                f"}}",
                f"inline taihe::array<uint64_t> _taihe_build_num(bool sign, taihe::array_view<uint64_t> abs) {{",
                f"    uint64_t *buf = reinterpret_cast<uint64_t *>(malloc((abs.size() + 1) * sizeof(uint64_t)));",
                f"    if (sign) {{",
                f"        bool carry = true;",
                f"        for (std::size_t i = 0; i < abs.size(); i++) {{",
                f"            buf[i] = ~abs[i] + carry;",
                f"            carry = carry && (buf[i] == 0);",
                f"        }}",
                f"        buf[abs.size()] = carry - 1;",
                f"    }} else {{",
                f"        for (std::size_t i = 0; i < abs.size(); i++) {{",
                f"            buf[i] = abs[i];",
                f"        }}",
                f"        buf[abs.size()] = 0;",
                f"    }}",
                f"    std::size_t size = abs.size() + 1;",
                f"    while (size >= 2 && ((buf[size - 1] == 0 && _get_bigint_msb(buf[size - 2]) == 0) ||",
                f"                        (buf[size - 1] == static_cast<uint64_t>(-1) && _get_bigint_msb(buf[size - 2]) == 1))) {{",
                f"        size--;",
                f"    }}",
                f"    return taihe::array<uint64_t>(buf, size);",
                f"}}",
                f"}}",
            )

    def gen_napi_header_file(self, pkg_napi_info: PackageNapiInfo):
        with CHeaderWriter(
            self.oc,
            f"include/{pkg_napi_info.header}",
            group=None,
        ) as target:
            target.add_include("taihe/runtime_napi.hpp")
            target.add_include("napi_utils.hpp")
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
        obj_ptr: str | None = None,
    ):
        if isinstance(func, IfaceMethodDecl):
            func_napi_info = IfaceMethodNapiInfo.get(self.am, func)
            func_abi_info = IfaceMethodAbiInfo.get(self.am, func)
        else:
            func_napi_info = GlobFuncNapiInfo.get(self.am, func)
            func_abi_info = GlobFuncAbiInfo.get(self.am, func)

        if isinstance(return_ty := func.return_ty, NonVoidType):
            value_ty = return_ty
            cpp_return_info = TypeCppInfo.get(self.am, value_ty)
            return_ty_cpp_name = cpp_return_info.as_owner
        else:
            return_ty_cpp_name = "void"
        return_ty_cpp_name_expected = (
            f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
        )
        result_cpp = "cpp_result"
        result_napi = "napi_result"
        result_expected = "expected_result"
        result_error = "error_result"
        if func_abi_info.is_noexcept:
            if func_napi_info.async_name is not None:
                pkg_napi_target.writelns(
                    f"size_t argc = {len(func.params) + 1};",
                    f"napi_value args[{len(func.params) + 1}] = {{nullptr}};",
                    f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args , nullptr, nullptr));",
                )
                cpp_args = []
                values = []
                for i, param in enumerate(func.params):
                    value_ty = param.ty
                    param_ty_napi_info = TypeNapiInfo.get(self.am, value_ty)
                    param_ty_napi_info.from_napi(
                        pkg_napi_target, f"args[{i}]", f"value{i}"
                    )
                    param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                    cpp_args.append(
                        f"std::forward<{param_ty_cpp_info.as_param}>(value{i})"
                    )
                    values.append(f"value{i}")
                cpp_args_str = ", ".join(cpp_args)

                cpp_async_data_ctx = f"async_data_ctx"
                napi_resname = f"napi_resname"
                cpp_inputs = []
                pkg_napi_target.add_include("optional")
                with pkg_napi_target.indented(
                    f"struct {cpp_async_data_ctx} {{",
                    f"}};",
                ):
                    pkg_napi_target.writelns(
                        f"napi_async_work work = nullptr;",
                        f"napi_ref cb_ref = nullptr;",
                    )
                    if obj_ptr:
                        pkg_napi_target.writelns(
                            f"napi_ref this_ref = nullptr;",
                            f"{obj_ptr}* obj_ptr;",
                        )
                    for index, param in enumerate(func.params):
                        param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                        cpp_input = f"cpp_input_{index}"
                        pkg_napi_target.writelns(
                            f"std::optional<{param_ty_cpp_info.as_owner}> {cpp_input};",
                        )
                        cpp_inputs.append(cpp_input)
                    if isinstance(return_ty := func.return_ty, NonVoidType):
                        return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                        pkg_napi_target.writelns(
                            f"std::optional<{return_ty_cpp_info.as_owner}> cpp_result;",
                        )

                pkg_napi_target.writelns(
                    f"{cpp_async_data_ctx}* cb_data = new {cpp_async_data_ctx}();",
                    f"NAPI_CALL(env, napi_create_reference(env, args[{len(func.params)}], 1, &cb_data->cb_ref));",
                    f"napi_value {napi_resname};",
                    f'NAPI_CALL(env, napi_create_string_utf8(env, "AsyncCallback", NAPI_AUTO_LENGTH, &{napi_resname}));',
                )
                inner_args = []
                for index, param in enumerate(func.params):
                    inner_arg = f"cb_data->{cpp_inputs[index]}"
                    pkg_napi_target.writelns(
                        f"{inner_arg} = {values[index]};",
                    )
                    inner_args.append(f"{inner_arg}.value()")
                inner_args_str = ", ".join(inner_args)
                if obj_ptr:
                    pkg_napi_target.writelns(
                        f"cb_data->obj_ptr = obj_ptr;",
                        f"NAPI_CALL(env, napi_create_reference(env, thisobj, 1, &cb_data->this_ref));",
                    )
                with pkg_napi_target.indented(
                    f"napi_create_async_work(",
                    f");",
                ):
                    pkg_napi_target.writelns(
                        f"env,",
                        f"nullptr,",
                        f"{napi_resname},",
                    )
                    with pkg_napi_target.indented(
                        f"[]([[maybe_unused]] napi_env env, void* data) {{",
                        f"}},",
                    ):
                        pkg_napi_target.writelns(
                            f"{cpp_async_data_ctx} *cb_data = reinterpret_cast<{cpp_async_data_ctx} *>(data);",
                        )
                        if isinstance(return_ty := func.return_ty, NonVoidType):
                            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                            if obj_ptr:
                                pkg_napi_target.writelns(
                                    f"cb_data->cpp_result = (({obj_ptr})(*cb_data->obj_ptr))->{func.name}({inner_args_str});",
                                )
                            else:
                                pkg_napi_target.writelns(
                                    f"cb_data->cpp_result = {func_cpp_name}({inner_args_str});",
                                )

                    with pkg_napi_target.indented(
                        f"[](napi_env env, napi_status status, void* data) {{",
                        f"}},",
                    ):
                        pkg_napi_target.writelns(
                            f"{cpp_async_data_ctx} *cb_data = reinterpret_cast<{cpp_async_data_ctx} *>(data);",
                            f"napi_value js_cb;",
                            f"NAPI_CALL(env, napi_get_reference_value(env, cb_data->cb_ref, &js_cb));",
                            f"napi_value undefined_value;",
                            f"NAPI_CALL(env, napi_get_undefined(env, &undefined_value));",
                        )
                        if obj_ptr:
                            pkg_napi_target.writelns(
                                f"napi_value thisobj;",
                                f"NAPI_CALL(env, napi_get_reference_value(env, cb_data->this_ref, &thisobj));",
                            )
                        with pkg_napi_target.indented(
                            f"if (status == napi_pending_exception) {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"napi_value error_obj;",
                                f"napi_get_and_clear_last_exception(env, &error_obj);",
                                f"napi_value argv[1] = {{ error_obj }};",
                                f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 1, argv, nullptr));",
                            )
                        with pkg_napi_target.indented(
                            f"else if (status == napi_cancelled) {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"napi_value error;",
                                f'napi_create_string_utf8(env, "Async operation was cancelled", NAPI_AUTO_LENGTH, &error);',
                                f"napi_value error_obj;",
                                f"napi_create_error(env, nullptr, error, &error_obj);",
                                f"napi_value argv[1] = {{ error_obj }};",
                                f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 1, argv, nullptr));",
                            )
                        with pkg_napi_target.indented(
                            f"else {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"napi_value null_value;",
                                f"napi_get_null(env, &null_value);",
                            )
                            if isinstance(return_ty := func.return_ty, NonVoidType):
                                return_ty_napi_info = TypeNapiInfo.get(
                                    self.am, return_ty
                                )
                                return_ty_napi_info.into_napi(
                                    pkg_napi_target,
                                    "cb_data->cpp_result.value().value()",
                                    "napi_result",
                                )
                                pkg_napi_target.writelns(
                                    f"napi_value argv[2] = {{ null_value, napi_result}};",
                                    f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 2, argv, nullptr));",
                                )
                            else:
                                pkg_napi_target.writelns(
                                    f"napi_value argv[1] = {{ null_value }};",
                                    f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 1, argv, nullptr));",
                                )

                        if obj_ptr:
                            with pkg_napi_target.indented(
                                f"if (cb_data->this_ref != nullptr) {{",
                                f"}}",
                            ):
                                pkg_napi_target.writelns(
                                    f"NAPI_CALL(env, napi_delete_reference(env, cb_data->this_ref));",
                                )
                        with pkg_napi_target.indented(
                            f"if (cb_data->cb_ref != nullptr) {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"NAPI_CALL(env, napi_delete_reference(env, cb_data->cb_ref));",
                            )
                        pkg_napi_target.writelns(
                            f"napi_delete_async_work(env, cb_data->work);",
                            f"delete cb_data;",
                        )
                    pkg_napi_target.writelns(
                        f"cb_data,",
                        f"&cb_data->work",
                    )
                pkg_napi_target.writelns(
                    f"NAPI_CALL(env, napi_queue_async_work(env, cb_data->work));",
                    f"return nullptr;",
                )
            elif func_napi_info.promise_name is not None:
                if len(func.params):
                    pkg_napi_target.writelns(
                        f"size_t argc = {len(func.params)};",
                        f"napi_value args[{len(func.params)}] = {{nullptr}};",
                        f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args , nullptr, nullptr));",
                    )
                cpp_args = []
                values = []
                for i, param in enumerate(func.params):
                    value_ty = param.ty
                    param_ty_napi_info = TypeNapiInfo.get(self.am, value_ty)
                    param_ty_napi_info.from_napi(
                        pkg_napi_target, f"args[{i}]", f"value{i}"
                    )
                    param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                    cpp_args.append(
                        f"std::forward<{param_ty_cpp_info.as_param}>(value{i})"
                    )
                    values.append(f"value{i}")
                cpp_args_str = ", ".join(cpp_args)

                cpp_async_data_ctx = f"async_data_ctx"
                napi_resname = f"napi_resname"
                cpp_inputs = []
                pkg_napi_target.add_include("optional")
                with pkg_napi_target.indented(
                    f"struct {cpp_async_data_ctx} {{",
                    f"}};",
                ):
                    pkg_napi_target.writelns(
                        f"napi_async_work work = nullptr;",
                        f"napi_deferred defer = nullptr;",
                        f"napi_ref cb = nullptr;",
                    )
                    if obj_ptr:
                        pkg_napi_target.writelns(
                            f"{obj_ptr}* obj_ptr;",
                        )
                    for index, param in enumerate(func.params):
                        param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                        cpp_input = f"cpp_input_{index}"
                        pkg_napi_target.writelns(
                            f"std::optional<{param_ty_cpp_info.as_owner}> {cpp_input};",
                        )
                        cpp_inputs.append(cpp_input)
                    if isinstance(return_ty := func.return_ty, NonVoidType):
                        return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                        pkg_napi_target.writelns(
                            f"std::optional<{return_ty_cpp_info.as_owner}> cpp_result;",
                        )
                pkg_napi_target.writelns(
                    f"napi_value promise = nullptr;",
                    f"napi_deferred deferred = nullptr;",
                    f"napi_create_promise(env, &deferred, &promise);",
                    f"{cpp_async_data_ctx}* cb_data = new {cpp_async_data_ctx}();",
                    f"cb_data->defer = deferred;",
                    f"napi_value {napi_resname};",
                    f'NAPI_CALL(env, napi_create_string_utf8(env, "AsyncCallback", NAPI_AUTO_LENGTH, &{napi_resname}));',
                )
                inner_args = []
                for index, param in enumerate(func.params):
                    inner_arg = f"cb_data->{cpp_inputs[index]}"
                    pkg_napi_target.writelns(
                        f"{inner_arg} = {values[index]};",
                    )
                    inner_args.append(f"{inner_arg}.value()")
                inner_args_str = ", ".join(inner_args)
                if obj_ptr:
                    pkg_napi_target.writelns(
                        f"cb_data->obj_ptr = obj_ptr;",
                    )
                with pkg_napi_target.indented(
                    f"napi_create_async_work(",
                    f");",
                ):
                    pkg_napi_target.writelns(
                        f"env,",
                        f"nullptr,",
                        f"{napi_resname},",
                    )
                    with pkg_napi_target.indented(
                        f"[]([[maybe_unused]] napi_env env, void* data) {{",
                        f"}},",
                    ):
                        pkg_napi_target.writelns(
                            f"{cpp_async_data_ctx} *cb_data = reinterpret_cast<{cpp_async_data_ctx} *>(data);",
                        )
                        if isinstance(return_ty := func.return_ty, NonVoidType):
                            if obj_ptr:
                                pkg_napi_target.writelns(
                                    f"cb_data->cpp_result = (({obj_ptr})(*cb_data->obj_ptr))->{func.name}({inner_args_str});",
                                )
                            else:
                                pkg_napi_target.writelns(
                                    f"cb_data->cpp_result = {func_cpp_name}({inner_args_str});",
                                )
                    with pkg_napi_target.indented(
                        f"[](napi_env env, napi_status status, void* data) {{",
                        f"}},",
                    ):
                        pkg_napi_target.writelns(
                            f"{cpp_async_data_ctx} *cb_data = reinterpret_cast<{cpp_async_data_ctx} *>(data);",
                        )
                        with pkg_napi_target.indented(
                            f"if (status == napi_pending_exception) {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"napi_value error_obj;",
                                f"napi_get_and_clear_last_exception(env, &error_obj);",
                                f"napi_reject_deferred(env, cb_data->defer, error_obj);",
                            )
                        with pkg_napi_target.indented(
                            f"else {{",
                            f"}}",
                        ):
                            if isinstance(return_ty := func.return_ty, NonVoidType):
                                return_ty_napi_info = TypeNapiInfo.get(
                                    self.am, return_ty
                                )
                                return_ty_napi_info.into_napi(
                                    pkg_napi_target,
                                    "cb_data->cpp_result.value().value()",
                                    "napi_result",
                                )
                                pkg_napi_target.writelns(
                                    f"napi_resolve_deferred(env, cb_data->defer, napi_result);",
                                )
                            else:
                                pkg_napi_target.writelns(
                                    f"napi_value undefined_value;",
                                    f"napi_get_undefined(env, &undefined_value);",
                                    f"napi_resolve_deferred(env, cb_data->defer, undefined_value);",
                                )
                        pkg_napi_target.writelns(
                            f"napi_delete_async_work(env, cb_data->work);",
                            f"delete cb_data;",
                        )
                    pkg_napi_target.writelns(
                        f"cb_data,",
                        f"&cb_data->work",
                    )
                pkg_napi_target.writelns(
                    f"napi_queue_async_work(env, cb_data->work);",
                    f"return promise;",
                )
            else:
                if len(func.params):
                    pkg_napi_target.writelns(
                        f"size_t argc = {len(func.params)};",
                        f"napi_value args[{len(func.params)}] = {{nullptr}};",
                        f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args , nullptr, nullptr));",
                    )
                cpp_args = []
                values = []
                for i, param in enumerate(func.params):
                    value_ty = param.ty
                    param_ty_napi_info = TypeNapiInfo.get(self.am, value_ty)
                    param_ty_napi_info.from_napi(
                        pkg_napi_target, f"args[{i}]", f"value{i}"
                    )
                    param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                    cpp_args.append(
                        f"std::forward<{param_ty_cpp_info.as_param}>(value{i})"
                    )
                    values.append(f"value{i}")
                cpp_args_str = ", ".join(cpp_args)
                if isinstance(return_ty := func.return_ty, NonVoidType):
                    pkg_napi_target.writelns(
                        f"{return_ty_cpp_name} {result_cpp} = {func_cpp_name}({cpp_args_str});",
                    )
                    return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
                    return_ty_napi_info.into_napi(
                        pkg_napi_target, result_cpp, result_napi
                    )
                    pkg_napi_target.writelns(
                        f"return {result_napi};",
                    )
                else:
                    pkg_napi_target.writelns(
                        f"{func_cpp_name}({cpp_args_str});",
                        f"return nullptr;",
                    )

        else:
            if func_napi_info.async_name is not None:
                pkg_napi_target.writelns(
                    f"size_t argc = {len(func.params) + 1};",
                    f"napi_value args[{len(func.params) + 1}] = {{nullptr}};",
                    f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args , nullptr, nullptr));",
                )
                cpp_args = []
                values = []
                for i, param in enumerate(func.params):
                    value_ty = param.ty
                    param_ty_napi_info = TypeNapiInfo.get(self.am, value_ty)
                    param_ty_napi_info.from_napi(
                        pkg_napi_target, f"args[{i}]", f"value{i}"
                    )
                    param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                    cpp_args.append(
                        f"std::forward<{param_ty_cpp_info.as_param}>(value{i})"
                    )
                    values.append(f"value{i}")
                cpp_args_str = ", ".join(cpp_args)

                cpp_async_data_ctx = f"async_data_ctx"
                napi_resname = f"napi_resname"
                cpp_inputs = []
                pkg_napi_target.add_include("optional")
                with pkg_napi_target.indented(
                    f"struct {cpp_async_data_ctx} {{",
                    f"}};",
                ):
                    pkg_napi_target.writelns(
                        f"napi_async_work work = nullptr;",
                        f"napi_ref cb_ref = nullptr;",
                    )
                    if obj_ptr:
                        pkg_napi_target.writelns(
                            f"napi_ref this_ref = nullptr;",
                            f"{obj_ptr}* obj_ptr;",
                        )
                    for index, param in enumerate(func.params):
                        param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                        cpp_input = f"cpp_input_{index}"
                        pkg_napi_target.writelns(
                            f"std::optional<{param_ty_cpp_info.as_owner}> {cpp_input};",
                        )
                        cpp_inputs.append(cpp_input)
                    if isinstance(return_ty := func.return_ty, NonVoidType):
                        return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                        return_ty_cpp_name = return_ty_cpp_info.as_owner
                    else:
                        return_ty_cpp_name = "void"
                    return_ty_expected_name = (
                        f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
                    )
                    pkg_napi_target.writelns(
                        f"std::optional<{return_ty_expected_name}> cpp_result;",
                    )
                pkg_napi_target.writelns(
                    f"{cpp_async_data_ctx}* cb_data = new {cpp_async_data_ctx}();",
                    f"NAPI_CALL(env, napi_create_reference(env, args[{len(func.params)}], 1, &cb_data->cb_ref));",
                    f"napi_value {napi_resname};",
                    f'NAPI_CALL(env, napi_create_string_utf8(env, "AsyncCallback", NAPI_AUTO_LENGTH, &{napi_resname}));',
                )
                inner_args = []
                for index, param in enumerate(func.params):
                    inner_arg = f"cb_data->{cpp_inputs[index]}"
                    pkg_napi_target.writelns(
                        f"{inner_arg} = {values[index]};",
                    )
                    inner_args.append(f"{inner_arg}.value()")
                inner_args_str = ", ".join(inner_args)
                if obj_ptr:
                    pkg_napi_target.writelns(
                        f"cb_data->obj_ptr = obj_ptr;",
                        f"NAPI_CALL(env, napi_create_reference(env, thisobj, 1, &cb_data->this_ref));",
                    )
                with pkg_napi_target.indented(
                    f"napi_create_async_work(",
                    f");",
                ):
                    pkg_napi_target.writelns(
                        f"env,",
                        f"nullptr,",
                        f"{napi_resname},",
                    )
                    with pkg_napi_target.indented(
                        f"[]([[maybe_unused]] napi_env env, void* data) {{",
                        f"}},",
                    ):
                        pkg_napi_target.writelns(
                            f"{cpp_async_data_ctx} *cb_data = reinterpret_cast<{cpp_async_data_ctx} *>(data);",
                        )
                        if obj_ptr:
                            pkg_napi_target.writelns(
                                f"cb_data->cpp_result = (({obj_ptr})(*cb_data->obj_ptr))->{func.name}({inner_args_str});",
                            )
                        else:
                            pkg_napi_target.writelns(
                                f"cb_data->cpp_result = {func_cpp_name}({inner_args_str});",
                            )
                    with pkg_napi_target.indented(
                        f"[](napi_env env, napi_status status, void* data) {{",
                        f"}},",
                    ):
                        pkg_napi_target.writelns(
                            f"{cpp_async_data_ctx} *cb_data = reinterpret_cast<{cpp_async_data_ctx} *>(data);",
                            f"napi_value js_cb;",
                            f"NAPI_CALL(env, napi_get_reference_value(env, cb_data->cb_ref, &js_cb));",
                            f"napi_value undefined_value;",
                            f"NAPI_CALL(env, napi_get_undefined(env, &undefined_value));",
                        )
                        if obj_ptr:
                            pkg_napi_target.writelns(
                                f"napi_value thisobj;",
                                f"NAPI_CALL(env, napi_get_reference_value(env, cb_data->this_ref, &thisobj));",
                            )
                        with pkg_napi_target.indented(
                            f"if (status == napi_pending_exception) {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"napi_value error_obj;",
                                f"napi_get_and_clear_last_exception(env, &error_obj);",
                                f"napi_value argv[1] = {{ error_obj }};",
                                f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 1, argv, nullptr));",
                            )
                        with pkg_napi_target.indented(
                            f"else if (status == napi_cancelled) {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"napi_value error;",
                                f'napi_create_string_utf8(env, "Async operation was cancelled", NAPI_AUTO_LENGTH, &error);',
                                f"napi_value error_obj;",
                                f"napi_create_error(env, nullptr, error, &error_obj);",
                                f"napi_value argv[1] = {{ error_obj }};",
                                f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 1, argv, nullptr));",
                            )
                        with pkg_napi_target.indented(
                            f"else {{",
                            f"}}",
                        ):
                            with pkg_napi_target.indented(
                                f"if (cb_data->cpp_result.value().has_value()) {{",
                                f"}}",
                            ):
                                pkg_napi_target.writelns(
                                    f"napi_value null_value;",
                                    f"napi_get_null(env, &null_value);",
                                )
                                if isinstance(return_ty := func.return_ty, NonVoidType):
                                    return_ty_napi_info = TypeNapiInfo.get(
                                        self.am, return_ty
                                    )
                                    return_ty_napi_info.into_napi(
                                        pkg_napi_target,
                                        "cb_data->cpp_result.value().value()",
                                        "napi_result",
                                    )
                                    pkg_napi_target.writelns(
                                        f"napi_value argv[2] = {{ null_value, napi_result}};",
                                        f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 2, argv, nullptr));",
                                    )
                                else:
                                    pkg_napi_target.writelns(
                                        f"napi_value argv[1] = {{ null_value }};",
                                        f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 1, argv, nullptr));",
                                    )
                            with pkg_napi_target.indented(
                                f"else {{",
                                f"}}",
                            ):
                                pkg_napi_target.writelns(
                                    f"::taihe::error {result_error} = cb_data->cpp_result.value().error();",
                                    f"napi_value errorMessage;",
                                    f"napi_create_string_utf8(env, {result_error}.message().c_str(), NAPI_AUTO_LENGTH, &errorMessage);",
                                    f"napi_value error_obj = nullptr;",
                                )
                                with pkg_napi_target.indented(
                                    f"if ({result_error}.code() == 0) {{",
                                    f"}}",
                                ):
                                    pkg_napi_target.writelns(
                                        f"napi_create_error(env, nullptr, errorMessage, &error_obj);",
                                    )
                                with pkg_napi_target.indented(
                                    f"else {{",
                                    f"}}",
                                ):
                                    pkg_napi_target.writelns(
                                        f"char const *code = std::to_string({result_error}.code()).c_str();",
                                        f"napi_value errorCode;",
                                        f"napi_create_string_utf8(env, code, NAPI_AUTO_LENGTH, &errorCode);",
                                        f"napi_create_error(env, errorCode, errorMessage, &error_obj);",
                                    )
                                pkg_napi_target.writelns(
                                    f"napi_value argv[1] = {{ error_obj }};",
                                    f"NAPI_CALL(env, napi_call_function(env, undefined_value, js_cb, 1, argv, nullptr));",
                                )
                        if obj_ptr:
                            with pkg_napi_target.indented(
                                f"if (cb_data->this_ref != nullptr) {{",
                                f"}}",
                            ):
                                pkg_napi_target.writelns(
                                    f"NAPI_CALL(env, napi_delete_reference(env, cb_data->this_ref));",
                                )
                        with pkg_napi_target.indented(
                            f"if (cb_data->cb_ref != nullptr) {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"NAPI_CALL(env, napi_delete_reference(env, cb_data->cb_ref));",
                            )
                        pkg_napi_target.writelns(
                            f"napi_delete_async_work(env, cb_data->work);",
                            f"delete cb_data;",
                        )
                    pkg_napi_target.writelns(
                        f"cb_data,",
                        f"&cb_data->work",
                    )
                pkg_napi_target.writelns(
                    f"NAPI_CALL(env, napi_queue_async_work(env, cb_data->work));",
                    f"return nullptr;",
                )
            elif func_napi_info.promise_name is not None:
                if len(func.params):
                    pkg_napi_target.writelns(
                        f"size_t argc = {len(func.params)};",
                        f"napi_value args[{len(func.params)}] = {{nullptr}};",
                        f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args , nullptr, nullptr));",
                    )
                cpp_args = []
                values = []
                for i, param in enumerate(func.params):
                    value_ty = param.ty
                    param_ty_napi_info = TypeNapiInfo.get(self.am, value_ty)
                    param_ty_napi_info.from_napi(
                        pkg_napi_target, f"args[{i}]", f"value{i}"
                    )
                    param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                    cpp_args.append(
                        f"std::forward<{param_ty_cpp_info.as_param}>(value{i})"
                    )
                    values.append(f"value{i}")
                cpp_args_str = ", ".join(cpp_args)

                cpp_async_data_ctx = f"async_data_ctx"
                napi_resname = f"napi_resname"
                cpp_inputs = []
                pkg_napi_target.add_include("optional")
                with pkg_napi_target.indented(
                    f"struct {cpp_async_data_ctx} {{",
                    f"}};",
                ):
                    pkg_napi_target.writelns(
                        f"napi_async_work work = nullptr;",
                        f"napi_deferred defer = nullptr;",
                        f"napi_ref cb = nullptr;",
                    )
                    if obj_ptr:
                        pkg_napi_target.writelns(
                            f"{obj_ptr}* obj_ptr;",
                        )
                    for index, param in enumerate(func.params):
                        param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                        cpp_input = f"cpp_input_{index}"
                        pkg_napi_target.writelns(
                            f"std::optional<{param_ty_cpp_info.as_owner}> {cpp_input};",
                        )
                        cpp_inputs.append(cpp_input)
                    if isinstance(return_ty := func.return_ty, NonVoidType):
                        return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                        return_ty_cpp_name = return_ty_cpp_info.as_owner
                    else:
                        return_ty_cpp_name = "void"
                    return_ty_expected_name = (
                        f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
                    )
                    pkg_napi_target.writelns(
                        f"std::optional<{return_ty_expected_name}> cpp_result;",
                    )
                pkg_napi_target.writelns(
                    f"napi_value promise = nullptr;",
                    f"napi_deferred deferred = nullptr;",
                    f"napi_create_promise(env, &deferred, &promise);",
                    f"{cpp_async_data_ctx}* cb_data = new {cpp_async_data_ctx}();",
                    f"cb_data->defer = deferred;",
                    f"napi_value {napi_resname};",
                    f'NAPI_CALL(env, napi_create_string_utf8(env, "AsyncCallback", NAPI_AUTO_LENGTH, &{napi_resname}));',
                )
                inner_args = []
                for index, param in enumerate(func.params):
                    inner_arg = f"cb_data->{cpp_inputs[index]}"
                    pkg_napi_target.writelns(
                        f"{inner_arg} = {values[index]};",
                    )
                    inner_args.append(f"{inner_arg}.value()")
                inner_args_str = ", ".join(inner_args)
                if obj_ptr:
                    pkg_napi_target.writelns(
                        f"cb_data->obj_ptr = obj_ptr;",
                    )
                with pkg_napi_target.indented(
                    f"napi_create_async_work(",
                    f");",
                ):
                    pkg_napi_target.writelns(
                        f"env,",
                        f"nullptr,",
                        f"{napi_resname},",
                    )
                    with pkg_napi_target.indented(
                        f"[]([[maybe_unused]] napi_env env, void* data) {{",
                        f"}},",
                    ):
                        pkg_napi_target.writelns(
                            f"{cpp_async_data_ctx} *cb_data = reinterpret_cast<{cpp_async_data_ctx} *>(data);",
                        )
                        if obj_ptr:
                            pkg_napi_target.writelns(
                                f"cb_data->cpp_result = (({obj_ptr})(*cb_data->obj_ptr))->{func.name}({inner_args_str});",
                            )
                        else:
                            pkg_napi_target.writelns(
                                f"cb_data->cpp_result = {func_cpp_name}({inner_args_str});",
                            )
                    with pkg_napi_target.indented(
                        f"[](napi_env env, napi_status status, void* data) {{",
                        f"}},",
                    ):
                        pkg_napi_target.writelns(
                            f"{cpp_async_data_ctx} *cb_data = reinterpret_cast<{cpp_async_data_ctx} *>(data);",
                        )
                        with pkg_napi_target.indented(
                            f"if (status == napi_pending_exception) {{",
                            f"}}",
                        ):
                            pkg_napi_target.writelns(
                                f"napi_value error_obj;",
                                f"napi_get_and_clear_last_exception(env, &error_obj);",
                                f"napi_reject_deferred(env, cb_data->defer, error_obj);",
                            )
                        with pkg_napi_target.indented(
                            f"else {{",
                            f"}}",
                        ):
                            with pkg_napi_target.indented(
                                f"if (cb_data->cpp_result.value().has_value()) {{",
                                f"}}",
                            ):
                                if isinstance(return_ty := func.return_ty, NonVoidType):
                                    return_ty_napi_info = TypeNapiInfo.get(
                                        self.am, return_ty
                                    )
                                    return_ty_napi_info.into_napi(
                                        pkg_napi_target,
                                        "cb_data->cpp_result.value().value()",
                                        "napi_result",
                                    )
                                    pkg_napi_target.writelns(
                                        f"napi_resolve_deferred(env, cb_data->defer, napi_result);",
                                    )
                                else:
                                    pkg_napi_target.writelns(
                                        f"napi_value undefined_value;",
                                        f"napi_get_undefined(env, &undefined_value);",
                                        f"napi_resolve_deferred(env, cb_data->defer, undefined_value);",
                                    )
                            with pkg_napi_target.indented(
                                f"else {{",
                                f"}}",
                            ):
                                pkg_napi_target.writelns(
                                    f"::taihe::error {result_error} = cb_data->cpp_result.value().error();",
                                    f"napi_value errorMessage;",
                                    f"napi_create_string_utf8(env, {result_error}.message().c_str(), NAPI_AUTO_LENGTH, &errorMessage);",
                                    f"napi_value error_obj = nullptr;",
                                )
                                with pkg_napi_target.indented(
                                    f"if ({result_error}.code() == 0) {{",
                                    f"}}",
                                ):
                                    pkg_napi_target.writelns(
                                        f"napi_create_error(env, nullptr, errorMessage, &error_obj);",
                                    )
                                with pkg_napi_target.indented(
                                    f"else {{",
                                    f"}}",
                                ):
                                    pkg_napi_target.writelns(
                                        f"char const *code = std::to_string({result_error}.code()).c_str();",
                                        f"napi_value errorCode;",
                                        f"napi_create_string_utf8(env, code, NAPI_AUTO_LENGTH, &errorCode);",
                                        f"napi_create_error(env, errorCode, errorMessage, &error_obj);",
                                    )
                                pkg_napi_target.writelns(
                                    f"napi_reject_deferred(env, cb_data->defer, error_obj);",
                                )
                        pkg_napi_target.writelns(
                            f"napi_delete_async_work(env, cb_data->work);",
                            f"delete cb_data;",
                        )
                    pkg_napi_target.writelns(
                        f"cb_data,",
                        f"&cb_data->work",
                    )
                pkg_napi_target.writelns(
                    f"napi_queue_async_work(env, cb_data->work);",
                    f"return promise;",
                )
            else:
                if len(func.params):
                    pkg_napi_target.writelns(
                        f"size_t argc = {len(func.params)};",
                        f"napi_value args[{len(func.params)}] = {{nullptr}};",
                        f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args , nullptr, nullptr));",
                    )
                cpp_args = []
                values = []
                for i, param in enumerate(func.params):
                    value_ty = param.ty
                    param_ty_napi_info = TypeNapiInfo.get(self.am, value_ty)
                    param_ty_napi_info.from_napi(
                        pkg_napi_target, f"args[{i}]", f"value{i}"
                    )
                    param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                    cpp_args.append(
                        f"std::forward<{param_ty_cpp_info.as_param}>(value{i})"
                    )
                    values.append(f"value{i}")
                cpp_args_str = ", ".join(cpp_args)
                pkg_napi_target.writelns(
                    f"{return_ty_cpp_name_expected} {result_expected} = {func_cpp_name}({cpp_args_str});",
                )
                with pkg_napi_target.indented(
                    f"if ({result_expected}) {{",
                    f"}}",
                ):
                    if isinstance(return_ty := func.return_ty, NonVoidType):
                        pkg_napi_target.writelns(
                            f"{return_ty_cpp_name} {result_cpp} = {result_expected}.value();",
                        )
                        return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
                        return_ty_napi_info.into_napi(
                            pkg_napi_target, result_cpp, result_napi
                        )
                        pkg_napi_target.writelns(
                            f"return {result_napi};",
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

    def gen_struct(
        self,
        struct: StructDecl,
        pkg_napi_target: CSourceWriter,
    ):
        self.gen_struct_conv_decl_file(struct, pkg_napi_target)
        self.gen_struct_conv_impl_file(struct, pkg_napi_target)
        with pkg_napi_target.indented(
            f"namespace {struct.name} {{",
            f"}}",
        ):
            self.gen_struct_ctor_func(struct, pkg_napi_target)
            self.gen_struct_create_func(struct, pkg_napi_target)

    def gen_struct_conv_decl_file(
        self,
        struct: StructDecl,
        pkg_napi_target: CSourceWriter,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        with CHeaderWriter(
            self.oc,
            f"include/{struct_napi_info.decl_header}",
            group=None,
        ) as struct_napi_decl_target:
            struct_napi_decl_target.add_include("napi_utils.hpp")
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
        pkg_napi_target: CSourceWriter,
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
                    type_info = TypeNapiInfo.get(self.am, value_ty)
                    type_info.from_napi(pkg_napi_target, f"args[{i}]", f"value{i}")
                    args.append(f"value{i}")
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
        self.gen_iface_files(iface, pkg_napi_target)
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

    def gen_iface_files(
        self,
        iface: IfaceDecl,
        pkg_napi_target: CSourceWriter,
    ):
        self.gen_iface_conv_decl_file(iface, pkg_napi_target)
        self.gen_iface_conv_impl_file(iface, pkg_napi_target)

    def gen_iface_conv_decl_file(
        self,
        iface: IfaceDecl,
        pkg_napi_target: CSourceWriter,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        with CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.decl_header}",
            group=None,
        ) as iface_napi_decl_target:
            iface_napi_decl_target.add_include("napi_utils.hpp")
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
        pkg_napi_target: CSourceWriter,
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
            base_tsfn_data_type = "tsfn_callback"
            destruct_data_type = "destruct_data"

            iface_napi_impl_target.add_include("optional")
            with iface_napi_impl_target.indented(
                f"struct {base_tsfn_data_type} {{",
                f"}};",
            ):
                iface_napi_impl_target.writelns(
                    f"virtual void operator()(napi_env env) = 0;",
                    f"virtual ~{base_tsfn_data_type}() {{}};",
                )

            napi_resname = f"napi_resname"
            with iface_napi_impl_target.indented(
                f"struct cpp_impl_t {{",
                f"}};",
            ):
                iface_napi_impl_target.writelns(
                    f"napi_env env;",
                    f"napi_ref _ref;",
                    f"napi_threadsafe_function _tsfn;",
                )
                with iface_napi_impl_target.indented(
                    f"cpp_impl_t(napi_env env, napi_value callback): env(env), _ref(nullptr), _tsfn(nullptr) {{",
                    f"}}",
                ):
                    iface_napi_impl_target.writelns(
                        f"NAPI_CALL(env, napi_create_reference(env, callback, 1, &_ref));",
                        f"napi_value {napi_resname};",
                        f'NAPI_CALL(env, napi_create_string_utf8(env, "MyWorkResource", NAPI_AUTO_LENGTH, &{napi_resname}));',
                    )
                    with iface_napi_impl_target.indented(
                        f"NAPI_CALL(env, napi_create_threadsafe_function(",
                        f"));",
                    ):
                        iface_napi_impl_target.writelns(
                            f"env,",
                            f"nullptr,",
                            f"nullptr,",
                            f"{napi_resname},",
                            f"0,",
                            f"1,",
                            f"nullptr,",
                            f"nullptr,",
                            f"nullptr,",
                        )
                        with iface_napi_impl_target.indented(
                            f"[](napi_env env, napi_value js_cb, [[maybe_unused]] void* context, void* data) {{",
                            f"}},",
                        ):
                            iface_napi_impl_target.writelns(
                                f"{base_tsfn_data_type}* cpp_cb =static_cast<{base_tsfn_data_type}*>(data);",
                                f"(*cpp_cb)(env);",
                            )
                        iface_napi_impl_target.writelns(
                            f"&_tsfn",
                        )
                    iface_napi_impl_target.writelns(
                        f"napi_unref_threadsafe_function(env, _tsfn);",
                    )
                with iface_napi_impl_target.indented(
                    f"~cpp_impl_t() {{",
                    f"}}",
                ):
                    with iface_napi_impl_target.indented(
                        f"if (_ref) {{",
                        f"}}",
                    ):
                        with iface_napi_impl_target.indented(
                            f"if (::taihe::_is_main_thread()) {{",
                            f"}}",
                        ):
                            iface_napi_impl_target.writelns(
                                f"NAPI_CALL(env, napi_delete_reference(env, _ref));",
                            )
                        with iface_napi_impl_target.indented(
                            f"else {{",
                            f"}}",
                        ):
                            with iface_napi_impl_target.indented(
                                f"struct {destruct_data_type}: {base_tsfn_data_type} {{",
                                f"}};",
                            ):
                                iface_napi_impl_target.writelns(
                                    f"bool completed = false;",
                                    f"std::mutex mutex;",
                                    f"std::condition_variable cv;",
                                    f"napi_ref ref;",
                                )
                                with iface_napi_impl_target.indented(
                                    f"void operator()(napi_env env) override {{",
                                    f"}}",
                                ):
                                    iface_napi_impl_target.writelns(
                                        f"NAPI_CALL(env, napi_delete_reference(env, this->ref));",
                                        f"this->completed = true;",
                                        f"this->cv.notify_one();",
                                    )
                            iface_napi_impl_target.writelns(
                                f"{destruct_data_type} del_ref_data;",
                                f"del_ref_data.ref = _ref;",
                            )
                            with iface_napi_impl_target.indented(
                                f"NAPI_CALL(env, napi_call_threadsafe_function(",
                                f"));",
                            ):
                                iface_napi_impl_target.writelns(
                                    f"_tsfn,",
                                    f"static_cast<{base_tsfn_data_type}*>(&del_ref_data),",
                                    f"napi_tsfn_blocking",
                                )
                            iface_napi_impl_target.writelns(
                                f"std::unique_lock<std::mutex> lock(del_ref_data.mutex);",
                                f"del_ref_data.cv.wait(lock, [&del_ref_data] {{ return del_ref_data.completed; }});",
                            )

                    with iface_napi_impl_target.indented(
                        f"if (_tsfn) {{",
                        f"}}",
                    ):
                        iface_napi_impl_target.writelns(
                            f"NAPI_CALL(env, napi_release_threadsafe_function(_tsfn, napi_tsfn_release));",
                        )

                for ancestor in iface_abi_info.ancestor_infos:
                    for method in ancestor.methods:
                        self.gen_iface_napi_method(
                            method, base_tsfn_data_type, iface_napi_impl_target
                        )
            iface_napi_impl_target.writelns(
                f"return taihe::make_holder<cpp_impl_t, {iface_cpp_info.as_owner}>(env, napi_obj);",
            )

    def gen_iface_napi_method(
        self,
        method: IfaceMethodDecl,
        base_tsfn_data_type: str,
        iface_napi_impl_target: CHeaderWriter,
    ):
        iface_method_data_type = "iface_method_data_type"
        iface_method_data = "iface_method_data"
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
        if method_abi_info.is_noexcept:
            with iface_napi_impl_target.indented(
                f"{return_ty_cpp_name} {method_napi_info.norm_name}({params_cpp_str}) {{",
                f"}}",
            ):
                with iface_napi_impl_target.indented(
                    f"if (::taihe::_is_main_thread()) {{",
                    f"}}",
                ):
                    if method.params:
                        iface_napi_impl_target.writelns(
                            f"napi_value args_inner[{len(method.params)}];",
                        )
                        args_inner = "args_inner"
                    else:
                        args_inner = "nullptr"

                    for i, param in enumerate(method.params):
                        param_napi_type_info = TypeNapiInfo.get(self.am, param.ty)
                        param_napi_type_info.into_napi(
                            iface_napi_impl_target,
                            f"{param.name}",
                            f"value_{i}",
                        )
                        iface_napi_impl_target.writelns(
                            f"args_inner[{i}] = value_{i};",
                        )

                    iface_napi_impl_target.writelns(
                        f"napi_value org_napi_obj;",
                        f"NAPI_CALL(env, napi_get_reference_value(env, _ref, &org_napi_obj));",
                        f"napi_value {method_napi_info.norm_name}_ts_method;",
                        f'NAPI_CALL(env, napi_get_named_property(env, org_napi_obj, "{method_napi_info.norm_name}", &{method_napi_info.norm_name}_ts_method));',
                        f"napi_value method_result_napi;",
                        f"NAPI_CALL(env, napi_call_function(env, org_napi_obj, {method_napi_info.norm_name}_ts_method, {len(method.params)}, {args_inner}, &method_result_napi));",
                    )
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
                            f"return;",
                        )
                with iface_napi_impl_target.indented(
                    f"else {{",
                    f"}}",
                ):
                    cpp_inputs = []
                    with iface_napi_impl_target.indented(
                        f"struct {iface_method_data_type}: {base_tsfn_data_type} {{",
                        f"}};",
                    ):
                        iface_napi_impl_target.writelns(
                            f"bool completed = false;",
                            f"std::mutex mutex;",
                            f"std::condition_variable cv;",
                            f"napi_ref ref;",
                        )
                        for index, param in enumerate(method.params):
                            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                            cpp_input = f"cpp_input_{index}"
                            iface_napi_impl_target.writelns(
                                f"std::optional<{param_ty_cpp_info.as_owner}> {cpp_input};",
                            )
                            cpp_inputs.append(cpp_input)
                        if isinstance(return_ty := method.return_ty, NonVoidType):
                            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                            iface_napi_impl_target.writelns(
                                f"std::optional<{return_ty_cpp_info.as_owner}> cpp_result;",
                            )
                        with iface_napi_impl_target.indented(
                            f"void operator()(napi_env env) override {{",
                            f"}}",
                        ):
                            iface_napi_impl_target.writelns(
                                f"napi_value global = nullptr;",
                                f"NAPI_CALL(env, napi_get_global(env, &global));",
                            )
                            inner_napi_args = []
                            for index, param in enumerate(method.params):
                                param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
                                inner_napi_arg = f"napi_arg_{index}"
                                inner_napi_args.append(inner_napi_arg)
                                param_ty_napi_info.into_napi(
                                    iface_napi_impl_target,
                                    f"(*(this->{cpp_inputs[index]}))",
                                    inner_napi_arg,
                                )
                            inner_napi_args_str = ", ".join(inner_napi_args)
                            if len(method.params) != 0:
                                iface_napi_impl_target.writelns(
                                    f"napi_value napi_argv[{len(method.params)}] = {{{inner_napi_args_str}}};",
                                )
                            else:
                                iface_napi_impl_target.writelns(
                                    f"napi_value napi_argv[] = {{}};",
                                )
                            inner_napi_res = "napi_result"
                            inner_cpp_res = "cpp_result"
                            iface_napi_impl_target.writelns(
                                f"napi_value {inner_napi_res} = nullptr;",
                                f"napi_value cb = nullptr;",
                                f"NAPI_CALL(env, napi_get_reference_value(env, this->ref, &cb));",
                                f"NAPI_CALL(env, napi_call_function(env, global, cb, {len(method.params)}, napi_argv, &{inner_napi_res}));",
                            )
                            if isinstance(return_ty := method.return_ty, NonVoidType):
                                return_ty_napi_info = TypeNapiInfo.get(
                                    self.am, return_ty
                                )
                                return_ty_napi_info.from_napi(
                                    iface_napi_impl_target,
                                    inner_napi_res,
                                    inner_cpp_res,
                                )
                                iface_napi_impl_target.writelns(
                                    f"this->cpp_result = {inner_cpp_res};",
                                )
                            iface_napi_impl_target.writelns(
                                f"this->completed = true;",
                                f"this->cv.notify_one();",
                            )

                    iface_napi_impl_target.writelns(
                        f"{iface_method_data_type} {iface_method_data};",
                        f"{iface_method_data}.ref = _ref;",
                    )
                    for index, param in enumerate(method.params):
                        iface_napi_impl_target.writelns(
                            f"{iface_method_data}.{cpp_inputs[index]} = {param.name};",
                        )
                    with iface_napi_impl_target.indented(
                        f"NAPI_CALL(env, napi_call_threadsafe_function(",
                        f"));",
                    ):
                        iface_napi_impl_target.writelns(
                            f"_tsfn,",
                            f"&{iface_method_data},",
                            f"napi_tsfn_blocking",
                        )
                    iface_napi_impl_target.writelns(
                        f"std::unique_lock<std::mutex> lock({iface_method_data}.mutex);",
                        f"{iface_method_data}.cv.wait(lock, [&{iface_method_data}] {{ return {iface_method_data}.completed; }});",
                    )
                    if isinstance(return_ty := method.return_ty, NonVoidType):
                        iface_napi_impl_target.writelns(
                            f"return *{iface_method_data}.cpp_result;",
                        )
                    else:
                        iface_napi_impl_target.writelns(
                            f"return;",
                        )
        else:
            with iface_napi_impl_target.indented(
                f"{return_ty_expected_name} {method_napi_info.norm_name}({params_cpp_str}) {{",
                f"}}",
            ):
                with iface_napi_impl_target.indented(
                    f"if (::taihe::_is_main_thread()) {{",
                    f"}}",
                ):
                    if method.params:
                        iface_napi_impl_target.writelns(
                            f"napi_value args_inner[{len(method.params)}];",
                        )
                        args_inner = "args_inner"
                    else:
                        args_inner = "nullptr"

                    for i, param in enumerate(method.params):
                        param_napi_type_info = TypeNapiInfo.get(self.am, param.ty)
                        param_napi_type_info.into_napi(
                            iface_napi_impl_target,
                            f"{param.name}",
                            f"value_{i}",
                        )
                        iface_napi_impl_target.writelns(
                            f"args_inner[{i}] = value_{i};",
                        )

                    iface_napi_impl_target.writelns(
                        f"napi_value org_napi_obj;",
                        f"NAPI_CALL(env, napi_get_reference_value(env, _ref, &org_napi_obj));",
                        f"napi_value {method_napi_info.norm_name}_ts_method;",
                        f'NAPI_CALL(env, napi_get_named_property(env, org_napi_obj, "{method_napi_info.norm_name}", &{method_napi_info.norm_name}_ts_method));',
                        f"napi_value method_result_napi;",
                        f"NAPI_CALL(env, napi_call_function(env, org_napi_obj, {method_napi_info.norm_name}_ts_method, {len(method.params)}, {args_inner}, &method_result_napi));",
                    )
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
                with iface_napi_impl_target.indented(
                    f"else {{",
                    f"}}",
                ):
                    cpp_inputs = []
                    with iface_napi_impl_target.indented(
                        f"struct {iface_method_data_type}: {base_tsfn_data_type} {{",
                        f"}};",
                    ):
                        iface_napi_impl_target.writelns(
                            f"bool completed = false;",
                            f"std::mutex mutex;",
                            f"std::condition_variable cv;",
                            f"napi_ref ref;",
                        )
                        for index, param in enumerate(method.params):
                            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                            cpp_input = f"cpp_input_{index}"
                            iface_napi_impl_target.writelns(
                                f"std::optional<{param_ty_cpp_info.as_owner}> {cpp_input};",
                            )
                            cpp_inputs.append(cpp_input)
                        if isinstance(return_ty := method.return_ty, NonVoidType):
                            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                            return_ty_cpp_name = return_ty_cpp_info.as_owner
                        else:
                            return_ty_cpp_name = "void"
                        return_ty_expected_name = (
                            f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
                        )
                        iface_napi_impl_target.writelns(
                            f"std::optional<{return_ty_expected_name}> cpp_result;",
                        )

                        with iface_napi_impl_target.indented(
                            f"void operator()(napi_env env) override {{",
                            f"}}",
                        ):
                            iface_napi_impl_target.writelns(
                                f"napi_value global = nullptr;",
                                f"NAPI_CALL(env, napi_get_global(env, &global));",
                            )
                            inner_napi_args = []
                            for index, param in enumerate(method.params):
                                param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
                                inner_napi_arg = f"napi_arg_{index}"
                                inner_napi_args.append(inner_napi_arg)
                                param_ty_napi_info.into_napi(
                                    iface_napi_impl_target,
                                    f"(*(this->{cpp_inputs[index]}))",
                                    inner_napi_arg,
                                )
                            inner_napi_args_str = ", ".join(inner_napi_args)
                            if len(method.params) != 0:
                                iface_napi_impl_target.writelns(
                                    f"napi_value napi_argv[{len(method.params)}] = {{{inner_napi_args_str}}};",
                                )
                            else:
                                iface_napi_impl_target.writelns(
                                    f"napi_value napi_argv[] = {{}};",
                                )
                            inner_napi_res = "napi_result"
                            inner_cpp_res = "cpp_result"
                            iface_napi_impl_target.writelns(
                                f"napi_value {inner_napi_res} = nullptr;",
                                f"napi_value cb = nullptr;",
                                f"NAPI_CALL(env, napi_get_reference_value(env, this->ref, &cb));",
                                f"NAPI_CALL(env, napi_call_function(env, global, cb, {len(method.params)}, napi_argv, &{inner_napi_res}));",
                            )
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
                                    f"this->cpp_result = ::taihe::unexpected<::taihe::error>(::taihe::from_napi_error(env, exception));",
                                )
                            with iface_napi_impl_target.indented(
                                f"else {{",
                                f"}}",
                            ):
                                if isinstance(
                                    return_ty := method.return_ty, NonVoidType
                                ):
                                    return_ty_napi_info = TypeNapiInfo.get(
                                        self.am, return_ty
                                    )
                                    return_ty_napi_info.from_napi(
                                        iface_napi_impl_target,
                                        inner_napi_res,
                                        inner_cpp_res,
                                    )
                                    iface_napi_impl_target.writelns(
                                        f"this->cpp_result = {inner_cpp_res};",
                                    )
                            iface_napi_impl_target.writelns(
                                f"this->completed = true;",
                                f"this->cv.notify_one();",
                            )

                    iface_napi_impl_target.writelns(
                        f"{iface_method_data_type} {iface_method_data};",
                        f"{iface_method_data}.ref = _ref;",
                    )
                    for index, param in enumerate(method.params):
                        iface_napi_impl_target.writelns(
                            f"{iface_method_data}.{cpp_inputs[index]} = {param.name};",
                        )
                    with iface_napi_impl_target.indented(
                        f"NAPI_CALL(env, napi_call_threadsafe_function(",
                        f"));",
                    ):
                        iface_napi_impl_target.writelns(
                            f"_tsfn,",
                            f"&{iface_method_data},",
                            f"napi_tsfn_blocking",
                        )
                    iface_napi_impl_target.writelns(
                        f"std::unique_lock<std::mutex> lock({iface_method_data}.mutex);",
                        f"{iface_method_data}.cv.wait(lock, [&{iface_method_data}] {{ return {iface_method_data}.completed; }});",
                    )
                    if isinstance(return_ty := method.return_ty, NonVoidType):
                        iface_napi_impl_target.writelns(
                            f"return *{iface_method_data}.cpp_result;",
                        )
                    else:
                        iface_napi_impl_target.writelns(
                            f"return;",
                        )

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
                    type_info = TypeNapiInfo.get(self.am, value_ty)
                    type_info.from_napi(pkg_napi_target, f"args[{i}]", f"value{i}")
                    args.append(f"value{i}")
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
                        f"(({iface_cpp_info_ancestor.as_owner})(*obj_ptr))->{method.name}",
                        iface_cpp_info_ancestor.as_owner,
                    )

    def gen_enum(
        self,
        enum: EnumDecl,
        pkg_napi_target: CSourceWriter,
    ):
        enum_napi_info = EnumNapiInfo.get(self.am, enum)
        with pkg_napi_target.indented(
            f"namespace {enum.name} {{",
            f"}}",
        ):
            with pkg_napi_target.indented(
                f"inline void create(napi_env env, [[maybe_unused]] napi_value exports) {{",
                f"}}",
            ):
                if enum_napi_info.is_literal:
                    for item in enum.items:
                        item_ty_napi_info = TypeNapiInfo.get(self.am, enum.ty)
                        item_ty_cpp_info = TypeCppInfo.get(self.am, enum.ty)
                        item_ty_napi_info.into_napi(
                            pkg_napi_target,
                            f"(({item_ty_cpp_info.as_owner}){dumps(item.value)})",
                            f"value_{item.name}",
                        )
                        pkg_napi_target.writelns(
                            f'NAPI_CALL(env, napi_set_named_property(env, exports, "{item.name}", value_{item.name}));',
                        )

                else:
                    pkg_napi_target.writelns(
                        f"napi_value enum_obj;",
                        f"napi_create_object(env, &enum_obj);",
                        f"napi_value key;",
                    )
                    for item in enum.items:
                        item_ty_napi_info = TypeNapiInfo.get(self.am, enum.ty)
                        item_ty_cpp_info = TypeCppInfo.get(self.am, enum.ty)
                        item_ty_napi_info.into_napi(
                            pkg_napi_target,
                            f"(({item_ty_cpp_info.as_owner}){dumps(item.value)})",
                            f"value_{item.name}",
                        )
                        pkg_napi_target.writelns(
                            f'NAPI_CALL(env, napi_create_string_utf8(env, "{item.name}", NAPI_AUTO_LENGTH, &key));',
                            f'NAPI_CALL(env, napi_set_named_property(env, enum_obj, "{item.name}", value_{item.name}));',
                            f"NAPI_CALL(env, napi_set_property(env, enum_obj, value_{item.name}, key));",
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
            union_napi_decl_target.add_include("napi_utils.hpp")
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
