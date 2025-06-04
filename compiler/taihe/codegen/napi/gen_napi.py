from taihe.codegen.abi.analyses import IfaceABIInfo
from taihe.codegen.abi.mangle import DeclKind, encode
from taihe.codegen.abi.writer import CHeaderWriter, CSourceWriter
from taihe.codegen.cpp.analyses import (
    IfaceCppInfo,
    PackageCppUserInfo,
    StructCppInfo,
    TypeCppInfo,
)
from taihe.codegen.napi.analyses import (
    IfaceNAPIInfo,
    PackageNAPIInfo,
    StructNAPIInfo,
    TypeNAPIInfo,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
    StructDecl,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputConfig


class NAPICodeGenerator:
    def __init__(self, oc: OutputConfig, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package(pkg)

    def gen_package(
        self,
        pkg: PackageDecl,
    ):
        pkg_napi_info = PackageNAPIInfo.get(self.am, pkg)
        pkg_cpp_user_info = PackageCppUserInfo.get(self.am, pkg)
        with CSourceWriter(
            self.oc,
            f"src/{pkg_napi_info.source}",
        ) as pkg_napi_target:
            pkg_napi_target.add_include("node/node_api.h")
            pkg_napi_target.add_include(pkg_cpp_user_info.header)

            for iface in pkg.interfaces:
                iface_abi_info = IfaceABIInfo.get(self.am, iface)
                iface_cpp_info = IfaceCppInfo.get(self.am, iface)
                for ancestor in iface_abi_info.ancestor_dict:
                    iface_cpp_info_ancestor = IfaceCppInfo.get(self.am, ancestor)
                    for method in ancestor.methods:
                        segments = [*iface.parent_pkg.segments, iface.name, method.name]
                        mangled_name = encode(segments, DeclKind.ANI_FUNC)
                        self.gen_iface_method(
                            method,
                            mangled_name,
                            iface_cpp_info.as_owner,
                            iface_cpp_info_ancestor.as_owner,
                            pkg_napi_target,
                        )

            register_infos = []
            for func in pkg.functions:
                segments = [*pkg.segments, func.name]
                mangled_name = encode(segments, DeclKind.NAPI_FUNC)
                self.gen_func(func, pkg_napi_info, pkg_napi_target, mangled_name)
                register_infos.append((func.name, mangled_name))
            for struct in pkg.structs:
                self.gen_struct_files(struct)
            for iface in pkg.interfaces:
                self.gen_iface_files(iface)
            self.gen_module_init(register_infos, pkg_napi_target)

    def gen_module_init(
        self,
        register_infos: list[tuple[str, str]],
        pkg_napi_target: CSourceWriter,
    ):
        pkg_napi_target.writelns(
            f"EXTERN_C_START",
        )
        with pkg_napi_target.indented(
            f"napi_value Init(napi_env env, napi_value exports) {{",
            f"}}",
        ):
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

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_napi_info: PackageNAPIInfo,
        pkg_napi_target: CSourceWriter,
        mangled_name: str,
    ):
        with pkg_napi_target.indented(
            f"static napi_value {mangled_name}(napi_env env, napi_callback_info info) {{",
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
        args = []
        for i, param in enumerate(func.params):
            value_ty = param.ty_ref.resolved_ty
            type_info = TypeNAPIInfo.get(self.am, value_ty)
            type_info.from_napi(pkg_napi_target, f"args[{i}]", f"value{i}")
            args.append(f"value{i}")
        args_str = ", ".join(args)

        if return_ty_ref := func.return_ty_ref:
            value_ty = return_ty_ref.resolved_ty
            cpp_return_info = TypeCppInfo.get(self.am, value_ty)
            pkg_napi_target.writelns(
                f"{cpp_return_info.as_owner} value = {func_cpp_name}({args_str});",
            )
            type_info = TypeNAPIInfo.get(self.am, value_ty)
            type_info.into_napi(pkg_napi_target, "value", "result")
        else:
            pkg_napi_target.writelns(
                f"{func_cpp_name}({args_str});",
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
                f"napi_get_cb_info(env, info, &argc, args , nullptr, nullptr);",
            )

    def gen_struct_files(
        self,
        struct: StructDecl,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_napi_info = StructNAPIInfo.get(self.am, struct)
        self.gen_struct_conv_decl_file(
            struct,
            struct_cpp_info,
            struct_napi_info,
        )
        self.gen_struct_conv_impl_file(
            struct,
            struct_cpp_info,
            struct_napi_info,
        )

    def gen_struct_conv_decl_file(
        self,
        struct: StructDecl,
        struct_cpp_info: StructCppInfo,
        struct_napi_info: StructNAPIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{struct_napi_info.decl_header}",
        ) as struct_napi_decl_target:
            struct_napi_decl_target.add_include("node/node_api.h")
            struct_napi_decl_target.add_include(struct_cpp_info.decl_header)
            struct_napi_decl_target.writelns(
                f"{struct_cpp_info.as_owner} {struct_napi_info.from_napi_func_name}(napi_env env, napi_value napi_obj);",
                f"napi_value {struct_napi_info.into_napi_func_name}(napi_env env, {struct_cpp_info.as_param} cpp_obj);",
            )

    def gen_struct_conv_impl_file(
        self,
        struct: StructDecl,
        struct_cpp_info: StructCppInfo,
        struct_napi_info: StructNAPIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{struct_napi_info.impl_header}",
        ) as struct_napi_impl_target:
            struct_napi_impl_target.add_include(struct_napi_info.decl_header)
            struct_napi_impl_target.add_include(struct_cpp_info.impl_header)
            # TODO: ignore compiler warning
            struct_napi_impl_target.writelns(
                '#pragma clang diagnostic ignored "-Wmissing-braces"',
            )
            self.gen_struct_from_napi_func(
                struct,
                struct_cpp_info,
                struct_napi_info,
                struct_napi_impl_target,
            )
            self.gen_struct_into_napi_func(
                struct,
                struct_cpp_info,
                struct_napi_info,
                struct_napi_impl_target,
            )

    def gen_struct_from_napi_func(
        self,
        struct: StructDecl,
        struct_cpp_info: StructCppInfo,
        struct_napi_info: StructNAPIInfo,
        struct_napi_impl_target: CHeaderWriter,
    ):
        with struct_napi_impl_target.indented(
            f"inline {struct_cpp_info.as_owner} {struct_napi_info.from_napi_func_name}(napi_env env, napi_value napi_obj) {{",
            f"}}",
        ):
            cpp_field_results = []
            for parts in struct_napi_info.sts_final_fields:
                final = parts[-1]
                type_ani_info = TypeNAPIInfo.get(self.am, final.ty_ref.resolved_ty)
                napi_field_value = f"napi_field_{final.name}"
                cpp_field_result = f"cpp_field_{final.name}"
                struct_napi_impl_target.writelns(
                    f"napi_value {napi_field_value} = nullptr;",
                    f'napi_get_named_property(env, napi_obj, "{final.name}", &{napi_field_value});',
                )
                type_ani_info.from_napi(
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
        struct_cpp_info: StructCppInfo,
        struct_napi_info: StructNAPIInfo,
        struct_napi_impl_target: CHeaderWriter,
    ):
        with struct_napi_impl_target.indented(
            f"inline napi_value {struct_napi_info.into_napi_func_name}(napi_env env, {struct_cpp_info.as_param} cpp_obj) {{",
            f"}}",
        ):
            struct_napi_impl_target.writelns(
                f"napi_value napi_obj = nullptr;",
                f"napi_create_object(env, &napi_obj);",
            )
            for parts in struct_napi_info.sts_final_fields:
                final = parts[-1]
                napi_field_result = f"napi_field_{final.name}"
                type_napi_info = TypeNAPIInfo.get(self.am, final.ty_ref.resolved_ty)
                type_napi_info.into_napi(
                    struct_napi_impl_target,
                    ".".join(("cpp_obj", *(part.name for part in parts))),
                    napi_field_result,
                )
                struct_napi_impl_target.writelns(
                    f'napi_set_named_property(env, napi_obj, "{final.name}", {napi_field_result});',
                )
            struct_napi_impl_target.writelns(
                f"return napi_obj;",
            )

    def gen_iface_files(
        self,
        iface: IfaceDecl,
    ):
        iface_abi_info = IfaceABIInfo.get(self.am, iface)
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNAPIInfo.get(self.am, iface)
        self.gen_iface_conv_decl_file(
            iface,
            iface_abi_info,
            iface_cpp_info,
            iface_napi_info,
        )
        self.gen_iface_conv_impl_file(
            iface,
            iface_abi_info,
            iface_cpp_info,
            iface_napi_info,
        )

    def gen_iface_conv_decl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
        iface_napi_info: IfaceNAPIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.decl_header}",
        ) as iface_napi_decl_target:
            iface_napi_decl_target.add_include("node/node_api.h")
            iface_napi_decl_target.add_include(iface_cpp_info.decl_header)
            iface_napi_decl_target.writelns(
                f"{iface_cpp_info.as_owner} {iface_napi_info.from_napi_func_name}(napi_env env, napi_value napi_obj);",
                f"napi_value {iface_napi_info.into_napi_func_name}(napi_env env, {iface_cpp_info.as_owner} cpp_obj);",
            )

    def gen_iface_conv_impl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
        iface_napi_info: IfaceNAPIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.impl_header}",
        ) as iface_napi_impl_target:
            iface_napi_impl_target.add_include(iface_napi_info.decl_header)
            iface_napi_impl_target.add_include(iface_cpp_info.impl_header)
            self.gen_iface_from_napi_func(
                iface,
                iface_abi_info,
                iface_cpp_info,
                iface_napi_info,
                iface_napi_impl_target,
            )
            self.gen_iface_into_napi_func(
                iface,
                iface_abi_info,
                iface_cpp_info,
                iface_napi_info,
                iface_napi_impl_target,
            )

    def gen_iface_from_napi_func(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
        iface_napi_info: IfaceNAPIInfo,
        iface_napi_impl_target: CHeaderWriter,
    ):
        with iface_napi_impl_target.indented(
            f"inline {iface_cpp_info.as_owner} {iface_napi_info.from_napi_func_name}(napi_env env, napi_value napi_obj) {{",
            f"}}",
        ):
            iface_napi_impl_target.writelns(
                f"{iface_cpp_info.as_owner}* cpp_ptr;",
                f"napi_unwrap(env, napi_obj, reinterpret_cast<void **>(&cpp_ptr));",
                f"{iface_cpp_info.as_owner} cpp_obj = *cpp_ptr;",
                f"return cpp_obj;",
            )

    def gen_iface_into_napi_func(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
        iface_napi_info: IfaceNAPIInfo,
        iface_napi_impl_target: CHeaderWriter,
    ):
        with iface_napi_impl_target.indented(
            f"inline napi_value {iface_napi_info.into_napi_func_name}(napi_env env, {iface_cpp_info.as_owner} cpp_obj) {{",
            f"}}",
        ):
            iface_napi_impl_target.writelns(
                f"{iface_cpp_info.as_owner}* cpp_ptr = new {iface_cpp_info.as_owner}(std::move(cpp_obj));",
                f"napi_value napi_obj = nullptr;",
                f"napi_create_object(env, &napi_obj);",
            )
            with iface_napi_impl_target.indented(
                f"napi_wrap(env, napi_obj, cpp_ptr, [](napi_env env, void* finalize_data, void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                iface_napi_impl_target.writelns(
                    f"delete static_cast<{iface_cpp_info.as_owner}*>(finalize_data);",
                )
            iface_napi_impl_target.writelns(f"return napi_obj;")

    def gen_iface_method(
        self,
        method: IfaceMethodDecl,
        mangled_name: str,
        iface_cpp_type_now: str,
        iface_cpp_type_real: str,
        pkg_napi_target: CSourceWriter,
    ):
        with pkg_napi_target.indented(
            f"static napi_value {mangled_name}(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            pkg_napi_target.writelns(
                f"napi_value thisobj;",
                f"napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr);",
                f"{iface_cpp_type_now}* value_ptr;",
                f"napi_unwrap(env, thisobj, reinterpret_cast<void**>(&value_ptr));",
            )
            self.gen_func_content(
                method,
                pkg_napi_target,
                f"(({iface_cpp_type_real})(*value_ptr))->{method.name}",
            )
