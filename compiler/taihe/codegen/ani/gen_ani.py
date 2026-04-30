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

from taihe.codegen.abi.analyses import (
    GlobFuncAbiInfo,
    IfaceAbiInfo,
    IfaceMethodAbiInfo,
)
from taihe.codegen.abi.writer import CHeaderWriter, CSourceWriter
from taihe.codegen.ani.analyses import (
    ArkTsModuleOrNamespace,
    EnumAniInfo,
    EnumConstAniInfo,
    EnumObjectAniInfo,
    GlobFuncAniInfo,
    IfaceAniInfo,
    IfaceMethodAniInfo,
    IfaceThunkAniInfo,
    IfaceThunkKey,
    PackageAniInfo,
    StructAniInfo,
    StructFieldAniInfo,
    StructObjectAniInfo,
    StructTupleAniInfo,
    TypeAniInfo,
    UnionAniInfo,
)
from taihe.codegen.cpp.analyses import (
    EnumCppInfo,
    IfaceCppInfo,
    IfaceMethodCppInfo,
    PackageCppUserInfo,
    StructCppInfo,
    TypeCppInfo,
    UnionCppInfo,
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
from taihe.semantics.types import NonVoidType
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import GEN_CXX_SRC_GROUP, OutputManager


class AniCodeGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.iterate():
            for iface in pkg.interfaces:
                AniIfaceDeclGenerator(self.om, self.am, iface).gen_iface_decl_file()
                AniIfaceImplGenerator(self.om, self.am, iface).gen_iface_impl_file()
            for struct in pkg.structs:
                AniStructDeclGenerator(self.om, self.am, struct).gen_struct_decl_file()
                AniStructImplGenerator(self.om, self.am, struct).gen_struct_impl_file()
            for union in pkg.unions:
                AniUnionDeclGenerator(self.om, self.am, union).gen_union_decl_file()
                AniUnionImplGenerator(self.om, self.am, union).gen_union_impl_file()
            for enum in pkg.enums:
                AniEnumImplGenerator(self.om, self.am, enum).gen_enum_impl_file()
            AniPackageHeaderGenerator(self.om, self.am, pkg).gen_package_header()
            AniPackageSourceGenerator(self.om, self.am, pkg).gen_package_source()
        AniConstructorGenerator(self.om, self.am, pg).gen_constructor()


class AniConstructorGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, pg: PackageGroup):
        self.om = om
        self.am = am
        self.pg = pg
        self.target = CSourceWriter(
            self.om,
            f"temp/ani_constructor.cpp",
            group=None,
            is_template=True,
        )

    def gen_constructor(self):
        with self.target:
            self.target.writelns(
                f"#if __has_include(<ani.h>)",
                f"#include <ani.h>",
                f"#elif __has_include(<ani/ani.h>)",
                f"#include <ani/ani.h>",
                f"#else",
                f'#error "ani.h not found. Please ensure the Ani SDK is correctly installed."',
                f"#endif",
            )
            with self.target.indented(
                f"ANI_EXPORT ani_status ANI_Constructor(ani_vm *vm, uint32_t *result) {{",
                f"}}",
            ):
                self.target.writelns(
                    # f"::taihe::set_vm(vm);",
                    f"ani_env *env;",
                )
                with self.target.indented(
                    f"if (ANI_OK != vm->GetEnv(ANI_VERSION_1, &env)) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"return ANI_ERROR;",
                    )
                self.target.writelns(
                    f"ani_status status = ANI_OK;",
                )
                for pkg in self.pg.iterate():
                    pkg_ani_info = PackageAniInfo.get(self.am, pkg)
                    self.target.add_include(pkg_ani_info.header)
                    with self.target.indented(
                        f"if (ANI_OK != {pkg_ani_info.cpp_ns}::ANIRegister(env)) {{",
                        f"}}",
                    ):
                        self.target.writelns(
                            f'std::cerr << "Error from {pkg_ani_info.cpp_ns}::ANIRegister" << std::endl;',
                            f"status = ANI_ERROR;",
                        )
                self.target.writelns(
                    f"*result = ANI_VERSION_1;",
                    f"return status;",
                )


class AniPackageHeaderGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, pkg: PackageDecl):
        self.om = om
        self.am = am
        self.pkg = pkg
        pkg_ani_info = PackageAniInfo.get(self.am, self.pkg)
        self.target = CHeaderWriter(
            self.om,
            f"include/{pkg_ani_info.header}",
            group=None,
        )

    def gen_package_header(self):
        pkg_ani_info = PackageAniInfo.get(self.am, self.pkg)
        with self.target:
            self.target.add_include("taihe/platform/ani.hpp")
            with self.target.indented(
                f"namespace {pkg_ani_info.cpp_ns} {{",
                f"}}",
                indent="",
            ):
                self.target.writelns(
                    f"TH_VISIBLE ani_status ANIRegister(ani_env *env);",
                )


class AniPackageSourceGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, pkg: PackageDecl):
        self.om = om
        self.am = am
        self.pkg = pkg
        pkg_ani_info = PackageAniInfo.get(self.am, self.pkg)
        self.target = CSourceWriter(
            self.om,
            f"src/{pkg_ani_info.source}",
            group=GEN_CXX_SRC_GROUP,
        )

    def gen_package_source(self):
        with self.target:
            pkg_ani_info = PackageAniInfo.get(self.am, self.pkg)
            pkg_cpp_user_info = PackageCppUserInfo.get(self.am, self.pkg)
            self.target.add_include(pkg_ani_info.header)
            self.target.add_include(pkg_cpp_user_info.header)

            subregisters: list[str] = []

            self.gen_utils_bindings(subregisters)
            self.gen_funcs_bindings(subregisters)
            self.gen_methods_bindings(subregisters)

            self.gen_package_register(subregisters)

    def gen_package_register(self, subregisters: list[str]):
        pkg_ani_info = PackageAniInfo.get(self.am, self.pkg)

        with self.target.indented(
            f"namespace {pkg_ani_info.cpp_ns} {{",
            f"}}",
            indent="",
        ):
            with self.target.indented(
                f"ani_status ANIRegister(ani_env *env) {{",
                f"}}",
            ):
                # TODO: set_vm in constructor
                with self.target.indented(
                    f"if (::taihe::get_vm() == nullptr) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"ani_vm *vm;",
                    )
                    with self.target.indented(
                        f"if (ANI_OK != env->GetVM(&vm)) {{",
                        f"}}",
                    ):
                        self.target.writelns(
                            f"return ANI_ERROR;",
                        )
                    self.target.writelns(
                        f"::taihe::set_vm(vm);",
                    )
                self.target.writelns(
                    f"ani_status status = ANI_OK;",
                )
                for subregister in subregisters:
                    with self.target.indented(
                        f"if (ani_status ret = {subregister}(env); ret != ANI_OK && ret != ANI_ALREADY_BINDED) {{",
                        f"}}",
                    ):
                        self.target.writelns(
                            f'std::cerr << "Error from {subregister}, code: " << ret << std::endl;',
                            f"status = ANI_ERROR;",
                        )
                self.target.writelns(
                    f"return status;",
                )

    def gen_utils_bindings(self, subregisters: list[str]):
        pkg_ani_info = PackageAniInfo.get(self.am, self.pkg)

        mod_member_infos: dict[str, str] = {}
        utils_ns = "local::utils"
        utils_register_ns = "local"
        utils_register_name = "ANIUtilsRegister"
        with self.target.indented(
            f"namespace {utils_ns} {{",
            f"}}",
            indent="",
        ):
            obj_drop_cpp_name = "obj_drop"
            self.gen_obj_drop(obj_drop_cpp_name)
            mod_member_infos.setdefault(
                pkg_ani_info.ns.mod.obj_drop,
                f"{utils_ns}::{obj_drop_cpp_name}",
            )
            obj_dup_cpp_name = "obj_dup"
            self.gen_obj_dup(obj_dup_cpp_name)
            mod_member_infos.setdefault(
                pkg_ani_info.ns.mod.obj_dup,
                f"{utils_ns}::{obj_dup_cpp_name}",
            )
            callback_invoke_cpp_name = "callback_invoke"
            self.gen_callback_invoke(callback_invoke_cpp_name)
            mod_member_infos.setdefault(
                pkg_ani_info.ns.mod.callback_invoke,
                f"{utils_ns}::{callback_invoke_cpp_name}",
            )
            async_handler_on_fulfilled_cpp_name = "async_handler_on_fulfilled"
            self.gen_async_handler_on_fulfilled(async_handler_on_fulfilled_cpp_name)
            mod_member_infos.setdefault(
                pkg_ani_info.ns.mod.async_handler_on_fulfilled,
                f"{utils_ns}::{async_handler_on_fulfilled_cpp_name}",
            )
            async_handler_on_rejected_cpp_name = "async_handler_on_rejected"
            self.gen_async_handler_on_rejected(async_handler_on_rejected_cpp_name)
            mod_member_infos.setdefault(
                pkg_ani_info.ns.mod.async_handler_on_rejected,
                f"{utils_ns}::{async_handler_on_rejected_cpp_name}",
            )
            async_handler_drop_cpp_name = "async_handler_drop"
            self.gen_async_handler_drop(async_handler_drop_cpp_name)
            mod_member_infos.setdefault(
                pkg_ani_info.ns.mod.async_handler_drop,
                f"{utils_ns}::{async_handler_drop_cpp_name}",
            )
        with self.target.indented(
            f"namespace {utils_register_ns} {{",
            f"}}",
            indent="",
        ):
            self.gen_subregister(
                utils_register_name,
                ns=pkg_ani_info.ns.mod,
                member_infos=mod_member_infos,
            )
            subregisters.append(f"{utils_register_ns}::{utils_register_name}")

    def gen_funcs_bindings(self, subregisters: list[str]):
        pkg_ani_info = PackageAniInfo.get(self.am, self.pkg)

        pkg_member_infos: dict[str, str] = {}
        funcs_ns = "local::funcs"
        funcs_register_ns = "local"
        funcs_register_name = "ANIFuncsRegister"
        with self.target.indented(
            f"namespace {funcs_ns} {{",
            f"}}",
            indent="",
        ):
            for func in self.pkg.functions:
                func_nat_info = GlobFuncAniInfo.get(self.am, func)
                self.gen_native_func(func.name, func, func_nat_info)
                pkg_member_infos.setdefault(
                    func_nat_info.sts_native,
                    f"{funcs_ns}::{func.name}",
                )
        with self.target.indented(
            f"namespace {funcs_register_ns} {{",
            f"}}",
            indent="",
        ):
            self.gen_subregister(
                funcs_register_name,
                ns=pkg_ani_info.ns,
                member_infos=pkg_member_infos,
            )
            subregisters.append(f"{funcs_register_ns}::{funcs_register_name}")

    def gen_methods_bindings(self, subregisters: list[str]):
        pkg_ani_info = PackageAniInfo.get(self.am, self.pkg)

        for iface in self.pkg.interfaces:
            iface_member_infos: dict[str, str] = {}
            methods_ns = f"local::interfaces::{iface.name}::methods"
            methods_register_ns = f"local::interfaces::{iface.name}"
            methods_register_name = "ANIMethodsRegister"
            with self.target.indented(
                f"namespace {methods_ns} {{",
                f"}}",
                indent="",
            ):
                iface_abi_info = IfaceAbiInfo.get(self.am, iface)
                for ancestor in iface_abi_info.ancestor_infos:
                    for method in ancestor.methods:
                        method_nat_info = IfaceThunkAniInfo.get(self.am, IfaceThunkKey(iface, method))  # fmt: skip
                        self.gen_native_func(method.name, method, method_nat_info)
                        iface_member_infos.setdefault(
                            method_nat_info.sts_native,
                            f"{methods_ns}::{method.name}",
                        )
            with self.target.indented(
                f"namespace {methods_register_ns} {{",
                f"}}",
                indent="",
            ):
                self.gen_subregister(
                    methods_register_name,
                    ns=pkg_ani_info.ns,
                    member_infos=iface_member_infos,
                )
                subregisters.append(f"{methods_register_ns}::{methods_register_name}")

    def gen_subregister(
        self,
        register_name: str,
        ns: ArkTsModuleOrNamespace,
        member_infos: dict[str, str],
    ):
        with self.target.indented(
            f"static ani_status {register_name}(ani_env *env) {{",
            f"}}",
        ):
            self.target.writelns(
                f"{ns.scope} scope;",
            )
            with self.target.indented(
                f'if (ANI_OK != env->Find{ns.scope.suffix}("{ns.impl_desc}", &scope)) {{',
                f"}}",
            ):
                self.target.writelns(
                    f"return ANI_ERROR;",
                )
            with self.target.indented(
                f"ani_native_function methods[] = {{",
                f"}};",
            ):
                for sts_name, cpp_name in member_infos.items():
                    self.target.writelns(
                        f'{{"{sts_name}", nullptr, reinterpret_cast<void*>({cpp_name})}},',
                    )
            self.target.writelns(
                f"return env->{ns.scope.suffix}_BindNativeFunctions(scope, methods, sizeof(methods) / sizeof(ani_native_function));",
            )

    def gen_native_func(
        self,
        name: str,
        func: IfaceMethodDecl | GlobFuncDecl,
        func_nat_info: IfaceThunkAniInfo | GlobFuncAniInfo,
    ):
        if isinstance(func, GlobFuncDecl):
            func_abi_info = GlobFuncAbiInfo.get(self.am, func)
        else:
            func_abi_info = IfaceMethodAbiInfo.get(self.am, func)
        params_ani = [
            "[[maybe_unused]] ani_env *env",
            *func_nat_info.c_native_base_params,
        ]
        args_ani = []
        for param in func.params:
            param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
            arg_ani = f"ani_arg_{param.name}"
            param_ty_ani_name = param_ty_ani_info.ani_type
            params_ani.append(f"{param_ty_ani_name} {arg_ani}")
            args_ani.append(arg_ani)
        params_ani_str = ", ".join(params_ani)
        if isinstance(return_ty := func.return_ty, NonVoidType):
            return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
            return_ty_ani_name = return_ty_ani_info.ani_type
        else:
            return_ty_ani_name = "void"
        with self.target.indented(
            f"static {return_ty_ani_name} {name}({params_ani_str}) {{",
            f"}}",
        ):
            args_cpp = []
            for param, arg_ani in zip(func.params, args_ani, strict=True):
                param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
                param_from_ani = f"from_ani_{param.name}"
                param_ty_ani_info.gen_from_ani(self.target, param_from_ani)
                args_cpp.append(f"{param_from_ani}(env, {arg_ani})")
            args_cpp_str = ", ".join(args_cpp)
            method_call = f"{func_nat_info.c_native_call}({args_cpp_str})"
            if isinstance(return_ty := func.return_ty, NonVoidType):
                return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                return_ty_cpp_name = return_ty_cpp_info.as_owner
            else:
                return_ty_cpp_name = "void"
            if func_abi_info.is_noexcept:
                if isinstance(return_ty := func.return_ty, NonVoidType):
                    self.target.writelns(
                        f"{return_ty_cpp_name} cpp_result = {method_call};",
                        f"if (::taihe::has_error()) {{ return {{}}; }}",
                    )
                    return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
                    return_ty_ani_info.gen_into_ani(self.target, "result_into_ani")
                    self.target.writelns(
                        f"return result_into_ani(env, std::move(cpp_result));",
                    )
                else:
                    self.target.writelns(
                        f"{method_call};",
                        f"if (::taihe::has_error()) {{ return; }}",
                        f"return;",
                    )
            else:
                exp_ty_cpp_name = f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"  # fmt: skip
                self.target.writelns(
                    f"{exp_ty_cpp_name} cpp_expected = {method_call};",
                )
                if isinstance(return_ty := func.return_ty, NonVoidType):
                    self.target.writelns(
                        f"if (::taihe::has_error()) {{ return {{}}; }}",
                        f"if (not cpp_expected) {{ ::taihe::throw_ani_taihe_error(env, std::move(cpp_expected.error())); return {{}}; }}",
                    )
                    return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
                    return_ty_ani_info.gen_into_ani(self.target, "result_into_ani")
                    self.target.writelns(
                        f"return result_into_ani(env, std::move(cpp_expected.value()));",
                    )
                else:
                    self.target.writelns(
                        f"if (::taihe::has_error()) {{ return; }}",
                        f"if (not cpp_expected) {{ ::taihe::throw_ani_taihe_error(env, std::move(cpp_expected.error())); return; }}",
                        f"return;",
                    )

    def gen_obj_drop(self, name: str):
        with self.target.indented(
            f"static void {name}([[maybe_unused]] ani_env *env, ani_long data_ptr) {{",
            f"}}",
        ):
            self.target.writelns(
                f"tobj_drop(reinterpret_cast<DataBlockHead*>(data_ptr));",
            )

    def gen_obj_dup(self, name: str):
        with self.target.indented(
            f"static ani_long {name}([[maybe_unused]] ani_env *env, ani_long data_ptr) {{",
            f"}}",
        ):
            self.target.writelns(
                f"return reinterpret_cast<ani_long>(tobj_dup(reinterpret_cast<DataBlockHead*>(data_ptr)));",
            )

    def gen_callback_invoke(self, name: str):
        params_ani = []
        args_ani = []
        for i in range(16):
            arg_ani = f"arg_{i}"
            param_ty_ani_name = "ani_ref"
            params_ani.append(f"{param_ty_ani_name} {arg_ani}")
            args_ani.append(arg_ani)
        params_ani_str = ", ".join(params_ani)
        args_ani_str = ", ".join(args_ani)
        return_ty_ani_name = "ani_ref"
        with self.target.indented(
            f"static {return_ty_ani_name} {name}([[maybe_unused]] ani_env *env, ani_long ani_invoke_ptr, ani_long ani_vtbl_ptr, ani_long ani_data_ptr, {params_ani_str}) {{",
            f"}}",
        ):
            self.target.writelns(
                f"return reinterpret_cast<{return_ty_ani_name} (*)(ani_env *env, ani_long ani_vtbl_ptr, ani_long ani_data_ptr, {params_ani_str})>(ani_invoke_ptr)(env, ani_vtbl_ptr, ani_data_ptr, {args_ani_str});",
            )

    def gen_async_handler_on_fulfilled(self, name: str):
        with self.target.indented(
            f"static void {name}([[maybe_unused]] ani_env *env, ani_long ani_on_fulfilled_ptr, ani_long ani_context_ptr, ani_ref data) {{",
            f"}}",
        ):
            self.target.writelns(
                f"reinterpret_cast<void (*)(ani_env *env, ani_long ani_context_ptr, ani_ref data)>(ani_on_fulfilled_ptr)(env, ani_context_ptr, data);",
            )

    def gen_async_handler_on_rejected(self, name: str):
        with self.target.indented(
            f"static void {name}([[maybe_unused]] ani_env *env, ani_long ani_on_rejected_ptr, ani_long ani_context_ptr, ani_ref data) {{",
            f"}}",
        ):
            self.target.writelns(
                f"reinterpret_cast<void (*)(ani_env *env, ani_long ani_context_ptr, ani_ref data)>(ani_on_rejected_ptr)(env, ani_context_ptr, data);",
            )

    def gen_async_handler_drop(self, name: str):
        with self.target.indented(
            f"static void {name}([[maybe_unused]] ani_env *env, ani_long ani_free_ptr, ani_long ani_context_ptr) {{",
            f"}}",
        ):
            self.target.writelns(
                f"reinterpret_cast<void (*)(ani_env *env, ani_long ani_context_ptr)>(ani_free_ptr)(env, ani_context_ptr);",
            )


class AniEnumImplGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, enum: EnumDecl):
        self.om = om
        self.am = am
        self.enum = enum
        enum_ani_info = EnumAniInfo.get(self.am, self.enum)
        self.target = CHeaderWriter(
            self.om,
            f"include/{enum_ani_info.impl_header}",
            group=None,
        )

    def gen_enum_impl_file(self):
        enum_ani_info = EnumAniInfo.get(self.am, self.enum)
        enum_cpp_info = EnumCppInfo.get(self.am, self.enum)
        with self.target:
            self.target.add_include("taihe/platform/ani.hpp")
            self.target.add_include(enum_cpp_info.defn_header)
            with self.target.indented(
                f"template<> struct ::taihe::from_ani_t<{enum_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline {enum_cpp_info.as_owner} operator()(ani_env* env, {enum_ani_info.ani_type} ani_obj) const;",
                )
            with self.target.indented(
                f"template<> struct ::taihe::into_ani_t<{enum_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline {enum_ani_info.ani_type} operator()(ani_env* env, {enum_cpp_info.as_owner} cpp_obj) const;",
                )
            self.gen_enum_from_ani_func()
            self.gen_enum_into_ani_func()

    def gen_enum_from_ani_func(self):
        enum_ani_info = EnumAniInfo.get(self.am, self.enum)
        if isinstance(enum_ani_info, EnumObjectAniInfo):
            self.gen_enum_object_from_ani_func(enum_ani_info)
        elif isinstance(enum_ani_info, EnumConstAniInfo):
            self.gen_enum_const_from_ani_func(enum_ani_info)

    def gen_enum_into_ani_func(self):
        enum_ani_info = EnumAniInfo.get(self.am, self.enum)
        if isinstance(enum_ani_info, EnumObjectAniInfo):
            self.gen_enum_object_into_ani_func(enum_ani_info)
        elif isinstance(enum_ani_info, EnumConstAniInfo):
            self.gen_enum_const_into_ani_func(enum_ani_info)

    def gen_enum_object_from_ani_func(self, enum_ani_info: EnumObjectAniInfo):
        enum_cpp_info = EnumCppInfo.get(self.am, self.enum)
        with self.target.indented(
            f"inline {enum_cpp_info.as_owner} taihe::from_ani_t<{enum_cpp_info.as_owner}>::operator()(ani_env* env, {enum_ani_info.ani_type} ani_obj) const {{",
            f"}}",
        ):
            self.target.writelns(
                f"ani_size ani_index = {{}};",
                f"env->EnumItem_GetIndex(ani_obj, &ani_index);",
                f"return {enum_cpp_info.full_name}(static_cast<{enum_cpp_info.full_name}::key_t>(ani_index));",
            )

    def gen_enum_object_into_ani_func(self, enum_ani_info: EnumObjectAniInfo):
        enum_cpp_info = EnumCppInfo.get(self.am, self.enum)
        with self.target.indented(
            f"inline {enum_ani_info.ani_type} taihe::into_ani_t<{enum_cpp_info.as_owner}>::operator()(ani_env* env, {enum_cpp_info.as_owner} cpp_obj) const {{",
            f"}}",
        ):
            self.target.writelns(
                f"ani_enum_item ani_result = {{}};",
                f'env->Enum_GetEnumItemByIndex(TH_ANI_FIND_ENUM(env, "{enum_ani_info.type_desc}"), static_cast<ani_size>(cpp_obj.get_key()), &ani_result);',
                f"return ani_result;",
            )

    def gen_enum_const_from_ani_func(self, enum_ani_info: EnumConstAniInfo):
        enum_cpp_info = EnumCppInfo.get(self.am, self.enum)
        with self.target.indented(
            f"inline {enum_cpp_info.as_owner} taihe::from_ani_t<{enum_cpp_info.as_owner}>::operator()(ani_env* env, {enum_ani_info.ani_type} ani_obj) const {{",
            f"}}",
        ):
            enum_ty_ani_info = TypeAniInfo.get(self.am, self.enum.ty)
            enum_ty_ani_info.gen_from_ani(self.target, "value_from_ani")
            self.target.writelns(
                f"return {enum_cpp_info.full_name}::from_value(value_from_ani(env, ani_obj));",
            )

    def gen_enum_const_into_ani_func(self, enum_ani_info: EnumConstAniInfo):
        enum_cpp_info = EnumCppInfo.get(self.am, self.enum)
        with self.target.indented(
            f"inline {enum_ani_info.ani_type} taihe::into_ani_t<{enum_cpp_info.as_owner}>::operator()(ani_env* env, {enum_cpp_info.as_owner} cpp_obj) const {{",
            f"}}",
        ):
            enum_ty_ani_info = TypeAniInfo.get(self.am, self.enum.ty)
            enum_ty_ani_info.gen_into_ani(self.target, "value_into_ani")
            self.target.writelns(
                f"return value_into_ani(env, cpp_obj.get_value());",
            )


class AniIfaceDeclGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, iface: IfaceDecl):
        self.om = om
        self.am = am
        self.iface = iface
        iface_ani_info = IfaceAniInfo.get(self.am, self.iface)
        self.target = CHeaderWriter(
            self.om,
            f"include/{iface_ani_info.decl_header}",
            group=None,
        )

    def gen_iface_decl_file(self):
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        iface_ani_info = IfaceAniInfo.get(self.am, self.iface)
        with self.target:
            self.target.add_include("taihe/platform/ani.hpp")
            self.target.add_include(iface_cpp_info.defn_header)
            with self.target.indented(
                f"template<> struct ::taihe::from_ani_t<{iface_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline {iface_cpp_info.as_owner} operator()(ani_env* env, {iface_ani_info.ani_type} ani_obj) const;",
                )
            with self.target.indented(
                f"template<> struct ::taihe::into_ani_t<{iface_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline {iface_ani_info.ani_type} operator()(ani_env* env, {iface_cpp_info.as_owner} cpp_obj) const;",
                )


class AniIfaceImplGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, iface: IfaceDecl):
        self.om = om
        self.am = am
        self.iface = iface
        iface_ani_info = IfaceAniInfo.get(self.am, self.iface)
        self.target = CHeaderWriter(
            self.om,
            f"include/{iface_ani_info.impl_header}",
            group=None,
        )

    def gen_iface_impl_file(self):
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        iface_ani_info = IfaceAniInfo.get(self.am, self.iface)
        with self.target:
            self.target.add_include(iface_ani_info.decl_header)
            self.target.add_include(iface_cpp_info.impl_header)
            self.gen_iface_from_ani_func()
            self.gen_iface_into_ani_func()

    def gen_iface_from_ani_func(self):
        iface_abi_info = IfaceAbiInfo.get(self.am, self.iface)
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        iface_ani_info = IfaceAniInfo.get(self.am, self.iface)
        with self.target.indented(
            f"inline {iface_cpp_info.as_owner} taihe::from_ani_t<{iface_cpp_info.as_owner}>::operator()(ani_env* env, {iface_ani_info.ani_type} ani_obj) const {{",
            f"}}",
        ):
            with self.target.indented(
                f"struct impl_t : ::taihe::dref_guard {{",
                f"}};",
            ):
                self.target.writelns(
                    f"impl_t(ani_env* env, ani_ref val) : ::taihe::dref_guard(env, val) {{}}",
                )
                for ancestor in iface_abi_info.ancestor_infos:
                    for method in ancestor.methods:
                        self.gen_iface_method(method)
                with self.target.indented(
                    f"uintptr_t getGlobalReference() const {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"return reinterpret_cast<uintptr_t>(this->ref);",
                    )
            self.target.writelns(
                f"return ::taihe::make_holder<impl_t, {iface_cpp_info.as_owner}, ::taihe::platform::ani::AniObject>(env, ani_obj);",
            )

    def gen_iface_method(self, method: IfaceMethodDecl):
        method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
        method_ani_info = IfaceMethodAniInfo.get(self.am, method)
        method_abi_info = IfaceMethodAbiInfo.get(self.am, method)
        params_cpp = []
        args_cpp = []
        for param in method.params:
            arg_cpp = f"cpp_arg_{param.name}"
            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
            param_ty_cpp_name = param_ty_cpp_info.as_param
            params_cpp.append(f"{param_ty_cpp_name} {arg_cpp}")
            args_cpp.append(arg_cpp)
        params_cpp_str = ", ".join(params_cpp)
        if isinstance(return_ty := method.return_ty, NonVoidType):
            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
            return_ty_cpp_name = return_ty_cpp_info.as_owner
        else:
            return_ty_cpp_name = "void"
        pkg_ani_info = PackageAniInfo.get(self.am, method.parent_pkg)
        function = f'TH_ANI_FIND_{pkg_ani_info.ns.scope.upper}_FUNCTION(env, "{pkg_ani_info.ns.impl_desc}", "{method_ani_info.sts_reverse}", nullptr)'
        if method_abi_info.is_noexcept:
            with self.target.indented(
                f"{return_ty_cpp_name} {method_cpp_info.impl_name}({params_cpp_str}) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"::taihe::env_guard guard;",
                    f"ani_env *env = guard.get_env();",
                )
                args_ani = []
                for param, arg_cpp in zip(method.params, args_cpp, strict=True):
                    param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
                    param_into_ani = f"into_ani_{param.name}"
                    param_ty_ani_info.gen_into_ani(self.target, param_into_ani)
                    args_ani.append(f"{param_into_ani}(env, {arg_cpp})")
                args_ani_sum = "".join(", " + arg_ani for arg_ani in args_ani)
                if isinstance(return_ty := method.return_ty, NonVoidType):
                    return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
                    self.target.writelns(
                        f"{return_ty_ani_info.ani_type} ani_result = {{}};",
                        f"env->Function_Call_{return_ty_ani_info.ani_type.suffix}({function}, reinterpret_cast<{return_ty_ani_info.ani_type.base}*>(&ani_result), static_cast<ani_object>(this->ref){args_ani_sum});",
                    )
                else:
                    self.target.writelns(
                        f"env->Function_Call_Void({function}, static_cast<ani_object>(this->ref){args_ani_sum});",
                    )
                if isinstance(return_ty := method.return_ty, NonVoidType):
                    return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
                    return_ty_ani_info.gen_from_ani(self.target, "result_from_ani")
                    self.target.writelns(
                        f"return result_from_ani(env, ani_result);",
                    )
                else:
                    self.target.writelns(
                        f"return;",
                    )
        else:
            exp_ty_cpp_name = f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
            with self.target.indented(
                f"{exp_ty_cpp_name} {method_cpp_info.impl_name}({params_cpp_str}) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"::taihe::env_guard guard;",
                    f"ani_env *env = guard.get_env();",
                )
                args_ani = []
                for param, arg_cpp in zip(method.params, args_cpp, strict=True):
                    param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
                    param_into_ani = f"into_ani_{param.name}"
                    param_ty_ani_info.gen_into_ani(self.target, param_into_ani)
                    args_ani.append(f"{param_into_ani}(env, {arg_cpp})")
                args_ani_sum = "".join(", " + arg_ani for arg_ani in args_ani)
                if isinstance(return_ty := method.return_ty, NonVoidType):
                    return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
                    self.target.writelns(
                        f"{return_ty_ani_info.ani_type} ani_result = {{}};",
                        f"ani_status ani_ret = env->Function_Call_{return_ty_ani_info.ani_type.suffix}({function}, reinterpret_cast<{return_ty_ani_info.ani_type.base}*>(&ani_result), static_cast<ani_object>(this->ref){args_ani_sum});",
                    )
                else:
                    self.target.writelns(
                        f"ani_status ani_ret = env->Function_Call_Void({function}, static_cast<ani_object>(this->ref){args_ani_sum});",
                    )
                with self.target.indented(
                    f"if (ani_ret == ANI_PENDING_ERROR) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"return ::taihe::unexpected<::taihe::error>(::taihe::catch_ani_taihe_error(env));",
                    )
                if isinstance(return_ty := method.return_ty, NonVoidType):
                    return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
                    return_ty_ani_info.gen_from_ani(self.target, "result_from_ani")
                    self.target.writelns(
                        f"return result_from_ani(env, ani_result);",
                    )
                else:
                    self.target.writelns(
                        f"return {{}};",
                    )

    def gen_iface_into_ani_func(self):
        iface_cpp_info = IfaceCppInfo.get(self.am, self.iface)
        iface_ani_info = IfaceAniInfo.get(self.am, self.iface)
        with self.target.indented(
            f"inline {iface_ani_info.ani_type} taihe::into_ani_t<{iface_cpp_info.as_owner}>::operator()(ani_env* env, {iface_cpp_info.as_owner} cpp_obj) const {{",
            f"}}",
        ):
            self.target.writelns(
                f"ani_object ani_obj;",
                f"auto wrapper = ::taihe::platform::ani::weak::AniObject(cpp_obj);",
            )
            with self.target.indented(
                f"if (!wrapper.is_error()) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"ani_ref global_ref = reinterpret_cast<ani_ref>(wrapper->getGlobalReference());",
                    f"ani_wref wref = {{}};",
                    f"env->WeakReference_Create(global_ref, &wref);",
                    f"ani_boolean released = {{}};",
                    f"env->WeakReference_GetReference(wref, &released, reinterpret_cast<ani_ref*>(&ani_obj));",
                )
            with self.target.indented(
                f"else {{",
                f"}}",
            ):
                self.target.writelns(
                    f"ani_long ani_vtbl_ptr = reinterpret_cast<ani_long>(cpp_obj.m_handle.vtbl_ptr);",
                    f"ani_long ani_data_ptr = reinterpret_cast<ani_long>(cpp_obj.m_handle.data_ptr);",
                    f"cpp_obj.m_handle.data_ptr = nullptr;",
                    f'env->Function_Call_Ref(TH_ANI_FIND_{iface_ani_info.parent_ns.scope.upper}_FUNCTION(env, "{iface_ani_info.parent_ns.impl_desc}", "{iface_ani_info.sts_factory}", nullptr), reinterpret_cast<ani_ref*>(&ani_obj), ani_vtbl_ptr, ani_data_ptr);',
                )
            self.target.writelns(
                f"return ani_obj;",
            )


class AniStructDeclGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, struct: StructDecl):
        self.om = om
        self.am = am
        self.struct = struct
        struct_ani_info = StructAniInfo.get(self.am, self.struct)
        self.target = CHeaderWriter(
            self.om,
            f"include/{struct_ani_info.decl_header}",
            group=None,
        )

    def gen_struct_decl_file(self):
        struct_cpp_info = StructCppInfo.get(self.am, self.struct)
        struct_ani_info = StructAniInfo.get(self.am, self.struct)
        with self.target:
            self.target.add_include("taihe/platform/ani.hpp")
            self.target.add_include(struct_cpp_info.defn_header)
            with self.target.indented(
                f"template<> struct ::taihe::from_ani_t<{struct_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline {struct_cpp_info.as_owner} operator()(ani_env* env, {struct_ani_info.ani_type} ani_obj) const;",
                )
            with self.target.indented(
                f"template<> struct ::taihe::into_ani_t<{struct_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline {struct_ani_info.ani_type} operator()(ani_env* env, {struct_cpp_info.as_owner} cpp_obj) const;",
                )


class AniStructImplGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, struct: StructDecl):
        self.om = om
        self.am = am
        self.struct = struct
        struct_ani_info = StructAniInfo.get(self.am, self.struct)
        self.target = CHeaderWriter(
            self.om,
            f"include/{struct_ani_info.impl_header}",
            group=None,
        )

    def gen_struct_impl_file(self):
        struct_cpp_info = StructCppInfo.get(self.am, self.struct)
        struct_ani_info = StructAniInfo.get(self.am, self.struct)
        with self.target:
            self.target.add_include(struct_ani_info.decl_header)
            self.target.add_include(struct_cpp_info.impl_header)
            self.gen_struct_from_ani_func()
            self.gen_struct_into_ani_func()

    def gen_struct_from_ani_func(self):
        struct_ani_info = StructAniInfo.get(self.am, self.struct)
        if isinstance(struct_ani_info, StructObjectAniInfo):
            self.gen_struct_object_from_ani_func(struct_ani_info)
        elif isinstance(struct_ani_info, StructTupleAniInfo):
            self.gen_struct_tuple_from_ani_func(struct_ani_info)

    def gen_struct_into_ani_func(self):
        struct_ani_info = StructAniInfo.get(self.am, self.struct)
        if isinstance(struct_ani_info, StructObjectAniInfo):
            self.gen_struct_object_into_ani_func(struct_ani_info)
        elif isinstance(struct_ani_info, StructTupleAniInfo):
            self.gen_struct_tuple_into_ani_func(struct_ani_info)

    def gen_struct_object_from_ani_func(self, struct_ani_info: StructObjectAniInfo):
        struct_cpp_info = StructCppInfo.get(self.am, self.struct)
        with self.target.indented(
            f"inline {struct_cpp_info.as_owner} taihe::from_ani_t<{struct_cpp_info.as_owner}>::operator()(ani_env* env, {struct_ani_info.ani_type} ani_obj) const {{",
            f"}}",
        ):
            finals_cpp = []
            for i, parts in enumerate(struct_ani_info.sts_all_fields):
                final = parts[-1]
                final_ani_info = StructFieldAniInfo.get(self.am, final)
                final_ty_ani_info = TypeAniInfo.get(self.am, final.ty)
                final_ani = f"ani_field_{i}"
                self.target.writelns(
                    f"{final_ty_ani_info.ani_type} {final_ani} = {{}};",
                )
                if struct_ani_info.is_class():
                    self.target.writelns(
                        f'env->Object_GetField_{final_ty_ani_info.ani_type.suffix}(ani_obj, TH_ANI_FIND_CLASS_FIELD(env, "{struct_ani_info.type_desc}", "{final_ani_info.sts_name}"), reinterpret_cast<{final_ty_ani_info.ani_type.base}*>(&{final_ani}));',
                    )
                else:
                    self.target.writelns(
                        f'env->Object_CallMethod_{final_ty_ani_info.ani_type.suffix}(ani_obj, TH_ANI_FIND_CLASS_METHOD(env, "{struct_ani_info.type_desc}", "%%get-{final_ani_info.sts_name}", nullptr), reinterpret_cast<{final_ty_ani_info.ani_type.base}*>(&{final_ani}));',
                    )
                final_from_ani = f"from_ani_{i}"
                final_ty_ani_info.gen_from_ani(self.target, final_from_ani)
                finals_cpp.append(f"{final_from_ani}(env, {final_ani})")
            finals_cpp_str = ", ".join(final_cpp for final_cpp in finals_cpp)
            self.target.writelns(
                f"return {struct_cpp_info.as_owner}{{{finals_cpp_str}}};",
            )

    def gen_struct_object_into_ani_func(self, struct_ani_info: StructObjectAniInfo):
        struct_cpp_info = StructCppInfo.get(self.am, self.struct)
        with self.target.indented(
            f"inline {struct_ani_info.ani_type} taihe::into_ani_t<{struct_cpp_info.as_owner}>::operator()(ani_env* env, {struct_cpp_info.as_owner} cpp_obj) const {{",
            f"}}",
        ):
            finals_ani = []
            for i, parts in enumerate(struct_ani_info.sorted_sts_all_fields):
                final = parts[-1]
                final_ty_ani_info = TypeAniInfo.get(self.am, final.ty)
                final_into_ani = f"into_ani_{i}"
                final_ty_ani_info.gen_into_ani(self.target, final_into_ani)
                finals_ani.append(f"{final_into_ani}(env, std::move(cpp_obj).{'.'.join(part.name for part in parts)})")  # fmt: skip
            finals_ani_sum = "".join(", " + final_ani for final_ani in finals_ani)
            self.target.writelns(
                f"ani_object ani_obj = {{}};",
                f'env->Function_Call_Ref(TH_ANI_FIND_{struct_ani_info.parent_ns.scope.upper}_FUNCTION(env, "{struct_ani_info.parent_ns.impl_desc}", "{struct_ani_info.sts_factory}", nullptr), reinterpret_cast<ani_ref*>(&ani_obj){finals_ani_sum});',
                f"return ani_obj;",
            )

    def gen_struct_tuple_from_ani_func(self, struct_ani_info: StructTupleAniInfo):
        struct_cpp_info = StructCppInfo.get(self.am, self.struct)
        with self.target.indented(
            f"inline {struct_cpp_info.as_owner} taihe::from_ani_t<{struct_cpp_info.as_owner}>::operator()(ani_env* env, {struct_ani_info.ani_type} ani_obj) const {{",
            f"}}",
        ):
            fields_cpp = []
            for i, field in enumerate(self.struct.fields):
                field_ty_ani_info = TypeAniInfo.get(self.am, field.ty)
                field_ani = f"ani_field_{field.name}"
                self.target.writelns(
                    f"ani_ref {field_ani} = {{}};",
                    f'env->Object_GetField_Ref(ani_obj, TH_ANI_FIND_CLASS_FIELD(env, "{struct_ani_info.type_desc}", "${i}"), &{field_ani});',
                )
                field_from_ani = f"from_ani_{field.name}"
                field_ty_ani_info.gen_from_ani_ref(self.target, field_from_ani)
                fields_cpp.append(f"{field_from_ani}(env, {field_ani})")
            fields_cpp_str = ", ".join(
                f"std::move({field_cpp})" for field_cpp in fields_cpp
            )
            self.target.writelns(
                f"return {struct_cpp_info.as_owner}{{{fields_cpp_str}}};",
            )

    def gen_struct_tuple_into_ani_func(self, struct_ani_info: StructTupleAniInfo):
        struct_cpp_info = StructCppInfo.get(self.am, self.struct)
        with self.target.indented(
            f"inline {struct_ani_info.ani_type} taihe::into_ani_t<{struct_cpp_info.as_owner}>::operator()(ani_env* env, {struct_cpp_info.as_owner} cpp_obj) const {{",
            f"}}",
        ):
            fields_ani = []
            for field in self.struct.fields:
                field_ty_ani_info = TypeAniInfo.get(self.am, field.ty)
                field_into_ani = f"into_ani_{field.name}"
                field_ty_ani_info.gen_into_ani_ref(self.target, field_into_ani)
                fields_ani.append(f"{field_into_ani}(env, std::move(cpp_obj).{field.name})")  # fmt: skip
            fields_ani_sum = "".join(", " + field_ani for field_ani in fields_ani)
            self.target.writelns(
                f"ani_object ani_obj = {{}};",
                f'env->Object_New(TH_ANI_FIND_CLASS(env, "{struct_ani_info.type_desc}"), TH_ANI_FIND_CLASS_METHOD(env, "{struct_ani_info.type_desc}", "<ctor>", nullptr), &ani_obj{fields_ani_sum});',
                f"return ani_obj;",
            )


class AniUnionDeclGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, union: UnionDecl):
        self.om = om
        self.am = am
        self.union = union
        union_ani_info = UnionAniInfo.get(self.am, self.union)
        self.target = CHeaderWriter(
            self.om,
            f"include/{union_ani_info.decl_header}",
            group=None,
        )

    def gen_union_decl_file(self):
        union_cpp_info = UnionCppInfo.get(self.am, self.union)
        union_ani_info = UnionAniInfo.get(self.am, self.union)
        with self.target:
            self.target.add_include("taihe/platform/ani.hpp")
            self.target.add_include(union_cpp_info.defn_header)
            with self.target.indented(
                f"template<> struct ::taihe::from_ani_t<{union_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline {union_cpp_info.as_owner} operator()(ani_env* env, {union_ani_info.ani_type} ani_value) const;",
                )
            with self.target.indented(
                f"template<> struct ::taihe::into_ani_t<{union_cpp_info.as_owner}> {{",
                f"}};",
            ):
                self.target.writelns(
                    f"inline {union_ani_info.ani_type} operator()(ani_env* env, {union_cpp_info.as_owner} cpp_value) const;",
                )


class AniUnionImplGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager, union: UnionDecl):
        self.om = om
        self.am = am
        self.union = union
        union_ani_info = UnionAniInfo.get(self.am, self.union)
        self.target = CHeaderWriter(
            self.om,
            f"include/{union_ani_info.impl_header}",
            group=None,
        )

    def gen_union_impl_file(self):
        union_cpp_info = UnionCppInfo.get(self.am, self.union)
        union_ani_info = UnionAniInfo.get(self.am, self.union)
        with self.target:
            self.target.add_include(union_ani_info.decl_header)
            self.target.add_include(union_cpp_info.impl_header)
            self.gen_union_from_ani_func()
            self.gen_union_into_ani_func()

    def gen_union_from_ani_func(self):
        union_cpp_info = UnionCppInfo.get(self.am, self.union)
        union_ani_info = UnionAniInfo.get(self.am, self.union)
        with self.target.indented(
            f"inline {union_cpp_info.as_owner} taihe::from_ani_t<{union_cpp_info.as_owner}>::operator()(ani_env* env, {union_ani_info.ani_type} ani_value) const {{",
            f"}}",
        ):
            for i, parts in enumerate(union_ani_info.sts_all_fields):
                final = parts[-1]
                static_tags = []
                for part in parts:
                    path_cpp_info = UnionCppInfo.get(self.am, part.parent_union)
                    static_tags.append(
                        f"::taihe::static_tag<{path_cpp_info.full_name}::tag_t::{part.name}>"
                    )
                static_tags_str = ", ".join(static_tags)
                final_ty_ani_info = TypeAniInfo.get(self.am, final.ty)
                final_check_type = f"check_type_{i}"
                final_ty_ani_info.gen_check_ani_ref(self.target, final_check_type)
                with self.target.indented(
                    f"if ({final_check_type}(env, ani_value)) {{",
                    f"}}",
                ):
                    final_from_ani = f"from_ani_{i}"
                    final_ty_ani_info.gen_from_ani_ref(self.target, final_from_ani)
                    self.target.writelns(
                        f"return {union_cpp_info.full_name}({static_tags_str}, {final_from_ani}(env, ani_value));",
                    )
            self.target.writelns(
                f"__builtin_unreachable();",
            )

    def gen_union_into_ani_func(self):
        union_cpp_info = UnionCppInfo.get(self.am, self.union)
        union_ani_info = UnionAniInfo.get(self.am, self.union)
        with self.target.indented(
            f"inline {union_ani_info.ani_type} taihe::into_ani_t<{union_cpp_info.as_owner}>::operator()(ani_env* env, {union_cpp_info.as_owner} cpp_value) const {{",
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
                        field_ty_ani_info = TypeAniInfo.get(self.am, field.ty)
                        field_into_ani = f"into_ani_{field.name}"
                        field_ty_ani_info.gen_into_ani_ref(self.target, field_into_ani)
                        self.target.writelns(
                            f"return {field_into_ani}(env, std::move(cpp_value).get_{field.name}_ref());",
                        )
