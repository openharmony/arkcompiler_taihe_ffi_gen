from json import dumps

from taihe.codegen.abi.analyses import IfaceABIInfo
from taihe.codegen.abi.mangle import DeclKind, encode
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
    GlobFuncNAPIInfo,
    IfaceNAPIInfo,
    PackageNAPIInfo,
    StructNAPIInfo,
    TypeNAPIInfo,
    UnionFieldNAPIInfo,
    UnionNAPIInfo,
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
from taihe.semantics.types import ArrayType, MapType, ScalarType, StringType, Type
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

            # ctor func
            ctors_map: dict[str, GlobFuncDecl] = {}
            for func in pkg.functions:
                func_napi_info = GlobFuncNAPIInfo.get(self.am, func)
                if class_name := func_napi_info.ctor_class_name:
                    # TODO: raise special error
                    if class_name in ctors_map:
                        raise ValueError(
                            f"Error: class_name '{class_name}' already have a constructor."
                        )
                    ctors_map[class_name] = func
            for iface in pkg.interfaces:
                if ctor := ctors_map.get(iface.name):
                    iface_napi_info = IfaceNAPIInfo.get(self.am, iface)
                    iface_napi_info.ctor = ctor

            register_infos = []
            for func in pkg.functions:
                segments = [*pkg.segments, func.name]
                mangled_name = encode(segments, DeclKind.NAPI_FUNC)
                self.gen_func(func, pkg_napi_info, pkg_napi_target, mangled_name)
                register_infos.append((func.name, mangled_name))
            for enum in pkg.enums:
                self.gen_enum(enum, pkg_napi_target)
            for struct in pkg.structs:
                self.gen_struct_files(struct)
            for iface in pkg.interfaces:
                self.gen_iface_files(iface)
                self.gen_iface_method_files(iface)
            for union in pkg.unions:
                self.gen_union_files(union)
            self.gen_module_init(pkg, register_infos, pkg_napi_target)

    def gen_module_init(
        self,
        pkg: PackageDecl,
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
            struct_napi_decl_target.add_include(struct_cpp_info.defn_header)
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
            self.gen_struct_ctor_func(
                struct,
                struct_cpp_info,
                struct_napi_info,
                struct_napi_impl_target,
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
                type_napi_info = TypeNAPIInfo.get(self.am, final.ty_ref.resolved_ty)
                napi_field_value = f"napi_field_{final.name}"
                cpp_field_result = f"cpp_field_{final.name}"
                struct_napi_impl_target.writelns(
                    f"napi_value {napi_field_value} = nullptr;",
                    f'napi_get_named_property(env, napi_obj, "{final.name}", &{napi_field_value});',
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
        struct_cpp_info: StructCppInfo,
        struct_napi_info: StructNAPIInfo,
        struct_napi_impl_target: CHeaderWriter,
    ):
        with struct_napi_impl_target.indented(
            f"inline napi_value {struct_napi_info.into_napi_func_name}(napi_env env, {struct_cpp_info.as_param} cpp_obj) {{",
            f"}}",
        ):
            args = []
            for parts in struct_napi_info.sts_final_fields:
                final = parts[-1]
                napi_field_result = f"napi_field_{final.name}"
                type_napi_info = TypeNAPIInfo.get(self.am, final.ty_ref.resolved_ty)
                type_napi_info.into_napi(
                    struct_napi_impl_target,
                    ".".join(("cpp_obj", *(part.name for part in parts))),
                    napi_field_result,
                )
                args.append(napi_field_result)
            args_str = ", ".join(args)
            struct_napi_impl_target.writelns(
                f"napi_value args[{len(struct_napi_info.sts_final_fields)}] = {{{args_str}}};",
                f"napi_value napi_obj = nullptr, constructor = nullptr;",
                f"napi_get_reference_value(env, {struct_napi_info.ctor_ref_name}, &constructor);",
                f"napi_new_instance(env, constructor, {len(struct_napi_info.sts_final_fields)}, args, &napi_obj);",
                f"return napi_obj;",
            )

    def gen_struct_ctor_func(
        self,
        struct: StructDecl,
        struct_cpp_info: StructCppInfo,
        struct_napi_info: StructNAPIInfo,
        struct_napi_impl_target: CHeaderWriter,
    ):
        register_infos = []
        for parts in struct_napi_info.sts_final_fields:
            final = parts[-1]
            filed_segments = [*final.parent_pkg.segments, struct.name, final.name]
            field_getter_name = encode(filed_segments, DeclKind.GETTER)
            field_setter_name = encode(filed_segments, DeclKind.SETTER)
            register_infos.append((final.name, field_getter_name, field_setter_name))

            field_ty_napi_info = TypeNAPIInfo.get(self.am, final.ty_ref.resolved_ty)
            with struct_napi_impl_target.indented(
                f"static napi_value {field_getter_name}(napi_env env, napi_callback_info info) {{",
                f"}}",
            ):
                struct_napi_impl_target.writelns(
                    f"napi_value thisobj;",
                    f"napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr);",
                    f"{struct_cpp_info.as_owner}* cpp_ptr;",
                    f"napi_unwrap(env, thisobj, reinterpret_cast<void **>(&cpp_ptr));",
                )
                field_ty_napi_info.into_napi(
                    struct_napi_impl_target,
                    "cpp_ptr->" + ".".join(part.name for part in parts),
                    "napi_field_result",
                )
                struct_napi_impl_target.writelns(
                    f"return napi_field_result;",
                )
            with struct_napi_impl_target.indented(
                f"static napi_value {field_setter_name}(napi_env env, napi_callback_info info) {{",
                f"}}",
            ):
                struct_napi_impl_target.writelns(
                    f"size_t argc = 1;",
                    f"napi_value args[1] = {{nullptr}};",
                    f"napi_value thisobj;",
                    f"napi_get_cb_info(env, info, &argc, args, &thisobj, nullptr);",
                    f"{struct_cpp_info.as_owner}* cpp_ptr;",
                    f"napi_unwrap(env, thisobj, reinterpret_cast<void **>(&cpp_ptr));",
                )
                field_ty_napi_info.from_napi(
                    struct_napi_impl_target, "args[0]", "cpp_field_result"
                )
                struct_napi_impl_target.writelns(
                    f'cpp_ptr->{".".join(part.name for part in parts)} = cpp_field_result;',
                    f"return nullptr;",
                )

        with struct_napi_impl_target.indented(
            f"inline napi_value {struct_napi_info.constructor_func_name}(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            struct_napi_impl_target.writelns(
                f"napi_value thisobj;",
                f"size_t argc = {len(struct_napi_info.sts_final_fields)};",
                f"napi_value args[{len(struct_napi_info.sts_final_fields)}];",
                f"napi_get_cb_info(env, info, &argc, args, &thisobj, nullptr);",
            )
            cpp_field_results = []
            for i, parts in enumerate(struct_napi_info.sts_final_fields):
                final = parts[-1]
                type_napi_info = TypeNAPIInfo.get(self.am, final.ty_ref.resolved_ty)
                cpp_field_result = f"cpp_field_{final.name}"
                type_napi_info.from_napi(
                    struct_napi_impl_target, f"args[{i}]", f"cpp_field_{final.name}"
                )
                cpp_field_results.append(cpp_field_result)
            cpp_moved_fields_str = ", ".join(
                f"std::move({cpp_field_result})"
                for cpp_field_result in cpp_field_results
            )
            struct_napi_impl_target.writelns(
                f"{struct_cpp_info.as_owner}* cpp_ptr = new {struct_cpp_info.as_owner}{{{cpp_moved_fields_str}}};",
            )
            with struct_napi_impl_target.indented(
                f"napi_wrap(env, thisobj, cpp_ptr, [](napi_env env, void* finalize_data, void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                struct_napi_impl_target.writelns(
                    f"delete static_cast<{struct_cpp_info.as_owner}*>(finalize_data);",
                )
            struct_napi_impl_target.writelns(
                f"return thisobj;",
            )
        struct_napi_impl_target.writelns(
            f"static napi_ref {struct_napi_info.ctor_ref_name};"
        )
        with struct_napi_impl_target.indented(
            f"inline napi_value {struct_napi_info.create_func_name}(napi_env env, napi_value exports) {{",
            f"}}",
        ):
            struct_napi_impl_target.writelns(f"napi_value result;")
            with struct_napi_impl_target.indented(
                f"napi_property_descriptor desc[] = {{",
                f"}};",
            ):
                for field_name, field_getter, field_setter in register_infos:
                    struct_napi_impl_target.writelns(
                        f'{{"{field_name}", nullptr, nullptr, {field_getter}, {field_setter}, nullptr, napi_default, nullptr}}, ',
                    )
            struct_napi_impl_target.writelns(
                f'napi_define_class(env, "{struct.name}", NAPI_AUTO_LENGTH, {struct_napi_info.constructor_func_name}, nullptr, {len(struct_napi_info.sts_final_fields)}, desc, &result);',
                f"napi_create_reference(env, result, 1, &{struct_napi_info.ctor_ref_name});",
                f'napi_set_named_property(env, exports, "{struct.name}", result);',
                f"return exports;",
            )

    def gen_iface_files(
        self,
        iface: IfaceDecl,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNAPIInfo.get(self.am, iface)
        self.gen_iface_conv_decl_file(
            iface,
            iface_cpp_info,
            iface_napi_info,
        )
        self.gen_iface_conv_impl_file(
            iface,
            iface_cpp_info,
            iface_napi_info,
        )

    def gen_iface_conv_decl_file(
        self,
        iface: IfaceDecl,
        iface_cpp_info: IfaceCppInfo,
        iface_napi_info: IfaceNAPIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.decl_header}",
        ) as iface_napi_decl_target:
            iface_napi_decl_target.add_include("node/node_api.h")
            iface_napi_decl_target.add_include(iface_cpp_info.defn_header)
            iface_napi_decl_target.writelns(
                f"napi_value {iface_napi_info.constructor_func_name}(napi_env env, napi_callback_info info);",
                f"napi_value {iface_napi_info.create_func_name}(napi_env env);",
                f"{iface_cpp_info.as_owner} {iface_napi_info.from_napi_func_name}(napi_env env, napi_value napi_obj);",
                f"napi_value {iface_napi_info.into_napi_func_name}(napi_env env, {iface_cpp_info.as_owner} cpp_obj);",
            )

    def gen_iface_conv_impl_file(
        self,
        iface: IfaceDecl,
        iface_cpp_info: IfaceCppInfo,
        iface_napi_info: IfaceNAPIInfo,
    ):
        iface_abi_info = IfaceABIInfo.get(self.am, iface)
        with CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.impl_header}",
        ) as iface_napi_impl_target:
            iface_napi_impl_target.add_include(iface_napi_info.decl_header)
            iface_napi_impl_target.add_include(iface_cpp_info.impl_header)
            self.gen_iface_ctor_func(
                iface,
                iface_abi_info,
                iface_cpp_info,
                iface_napi_info,
                iface_napi_impl_target,
            )
            self.gen_iface_from_napi_func(
                iface,
                iface_abi_info,
                iface_cpp_info,
                iface_napi_info,
                iface_napi_impl_target,
            )
            self.gen_iface_into_napi_func(
                iface,
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
            with iface_napi_impl_target.indented(
                f"struct cpp_impl_t {{",
                f"}};",
            ):
                iface_napi_impl_target.writelns(
                    f"napi_env env;",
                    f"napi_ref ref;",
                )
                with iface_napi_impl_target.indented(
                    f"cpp_impl_t(napi_env env, napi_value callback): env(env), ref(nullptr) {{",
                    f"}}",
                ):
                    iface_napi_impl_target.writelns(
                        f"napi_create_reference(env, callback, 1, &ref);",
                    )
                with iface_napi_impl_target.indented(
                    f"~cpp_impl_t() {{",
                    f"}}",
                ):
                    with iface_napi_impl_target.indented(
                        f"if (ref) {{",
                        f"}}",
                    ):
                        iface_napi_impl_target.writelns(
                            f"napi_delete_reference(env, ref);",
                        )
                for ancestor in iface_abi_info.ancestor_dict:
                    for method in ancestor.methods:
                        self.gen_iface_napi_method(method, iface_napi_impl_target)
            iface_napi_impl_target.writelns(
                f"return taihe::make_holder<cpp_impl_t, {iface_cpp_info.as_owner}>(env, napi_obj);",
            )

    def gen_iface_napi_method(
        self,
        method: IfaceMethodDecl,
        iface_napi_impl_target: CHeaderWriter,
    ):
        params_cpp = []
        for param in method.params:
            param_cpp_type_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
            params_cpp.append(f"{param_cpp_type_info.as_param} {param.name}")
        params_cpp_str = ", ".join(params_cpp)

        if method.return_ty_ref:
            return_ty_info = TypeCppInfo.get(self.am, method.return_ty_ref.resolved_ty)
            return_ty_str = return_ty_info.as_owner
        else:
            return_ty_str = "void"

        with iface_napi_impl_target.indented(
            f"{return_ty_str} {method.name}({params_cpp_str}) {{",
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
                param_napi_type_info = TypeNAPIInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                param_napi_type_info.into_napi(
                    iface_napi_impl_target,
                    f"{param.name}",
                    f"value_{i}",
                )
                iface_napi_impl_target.writelns(
                    f"args_inner[{i}] = value_{i};",
                )

            iface_napi_impl_target.writelns(
                f"napi_value org_napi_obj;"
                f"napi_get_reference_value(env, ref, &org_napi_obj);"
                f"napi_value {method.name}_ts_method;"
                f'napi_get_named_property(env, org_napi_obj, "{method.name}", &{method.name}_ts_method);'
                f"napi_value method_result_napi;"
                f"napi_call_function(env, org_napi_obj, {method.name}_ts_method, {len(method.params)}, {args_inner}, &method_result_napi);"
            )
            if method.return_ty_ref:
                return_napi_type_info = TypeNAPIInfo.get(
                    self.am, method.return_ty_ref.resolved_ty
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

    def gen_iface_into_napi_func(
        self,
        iface: IfaceDecl,
        iface_cpp_info: IfaceCppInfo,
        iface_napi_info: IfaceNAPIInfo,
        iface_napi_impl_target: CHeaderWriter,
    ):
        with iface_napi_impl_target.indented(
            f"inline napi_value {iface_napi_info.into_napi_func_name}(napi_env env, {iface_cpp_info.as_owner} cpp_obj) {{",
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
                f"napi_get_reference_value(env, {iface_napi_info.ctor_ref_name}_inner, &constructor);",
                f"napi_new_instance(env, constructor, 2, argv, &napi_obj);",
            )
            iface_napi_impl_target.writelns(f"return napi_obj;")

    def gen_iface_ctor_func(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
        iface_napi_info: IfaceNAPIInfo,
        iface_napi_impl_target: CHeaderWriter,
    ):
        with iface_napi_impl_target.indented(
            f"inline napi_value {iface_napi_info.constructor_func_name}_inner(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            iface_napi_impl_target.writelns(
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
            with iface_napi_impl_target.indented(
                f"napi_wrap(env, thisobj, cpp_ptr, [](napi_env env, void* finalize_data, void* finalize_hint) {{",
                f"}}, nullptr, nullptr);",
            ):
                iface_napi_impl_target.writelns(
                    f"delete static_cast<{iface_cpp_info.as_owner}*>(finalize_data);",
                )
            iface_napi_impl_target.writelns(
                f"return thisobj;",
            )

        iface_napi_impl_target.writelns(
            f"static napi_ref {iface_napi_info.ctor_ref_name}_inner;"
        )

        # process ctor
        if ctor := iface_napi_info.ctor:
            with iface_napi_impl_target.indented(
                f"inline napi_value {iface_napi_info.constructor_func_name}(napi_env env, napi_callback_info info) {{",
                f"}}",
            ):
                ctor_cpp_user_info = GlobFuncCppUserInfo.get(self.am, ctor)
                iface_napi_impl_target.writelns(
                    f"napi_value thisobj;",
                    f"size_t argc = {len(ctor.params)};",
                    f"napi_value args[{len(ctor.params)}];",
                    f"napi_get_cb_info(env, info, &argc, args, &thisobj, nullptr);",
                )
                args = []
                for i, param in enumerate(ctor.params):
                    value_ty = param.ty_ref.resolved_ty
                    type_info = TypeNAPIInfo.get(self.am, value_ty)
                    type_info.from_napi(
                        iface_napi_impl_target, f"args[{i}]", f"value{i}"
                    )
                    args.append(f"value{i}")
                args_str = ", ".join(args)

                if return_ty_ref := ctor.return_ty_ref:
                    # TODO: assert the return type is the iface type
                    value_ty = return_ty_ref.resolved_ty
                    iface_napi_impl_target.writelns(
                        f"{iface_cpp_info.as_owner} value = {ctor_cpp_user_info.full_name}({args_str});",
                        f"{iface_cpp_info.as_owner}* cpp_ptr = new {iface_cpp_info.as_owner}(std::move(value));",
                    )
                    with iface_napi_impl_target.indented(
                        f"napi_wrap(env, thisobj, cpp_ptr, [](napi_env env, void* finalize_data, void* finalize_hint) {{",
                        f"}}, nullptr, nullptr);",
                    ):
                        iface_napi_impl_target.writelns(
                            f"delete static_cast<{iface_cpp_info.as_owner}*>(finalize_data);",
                        )
                    iface_napi_impl_target.writelns(
                        f"return thisobj;",
                    )
                else:
                    # TODO: special error
                    raise ValueError("constructor must have return value")
            iface_napi_impl_target.writelns(
                f"static napi_ref {iface_napi_info.ctor_ref_name};"
            )
        with iface_napi_impl_target.indented(
            f"inline napi_value {iface_napi_info.create_func_name}(napi_env env, napi_value exports) {{",
            f"}}",
        ):
            iface_napi_impl_target.writelns(f"napi_value result;")
            iface_napi_impl_target.add_include(iface_napi_info.meth_impl_header)
            with iface_napi_impl_target.indented(
                f"napi_property_descriptor desc[] = {{",
                f"}};",
            ):
                for mng_name, value in iface_napi_info.iface_register_infos.items():
                    iface_napi_impl_target.writelns(
                        f'{{"{value[0].name}", nullptr, {mng_name}, nullptr, nullptr, nullptr, napi_default, nullptr}}, ',
                    )
            if ctor := iface_napi_info.ctor:
                iface_napi_impl_target.writelns(
                    f'napi_define_class(env, "{iface.name}", NAPI_AUTO_LENGTH, {iface_napi_info.constructor_func_name}, nullptr, {len(iface_napi_info.iface_register_infos)}, desc, &result);',
                    f"napi_create_reference(env, result, 1, &{iface_napi_info.ctor_ref_name});",
                    f'napi_set_named_property(env, exports, "{iface.name}", result);',
                )
            iface_napi_impl_target.writelns(
                f'napi_define_class(env, "{iface.name}_inner", NAPI_AUTO_LENGTH, {iface_napi_info.constructor_func_name}_inner, nullptr, {len(iface_napi_info.iface_register_infos)}, desc, &result);',
                f"napi_create_reference(env, result, 1, &{iface_napi_info.ctor_ref_name}_inner);",
                f"return exports;",
            )

    def gen_iface_method_files(
        self,
        iface: IfaceDecl,
    ):
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_napi_info = IfaceNAPIInfo.get(self.am, iface)
        self.gen_iface_method_decl_file(
            iface_cpp_info,
            iface_napi_info,
        )
        self.gen_iface_method_impl_file(
            iface_cpp_info,
            iface_napi_info,
        )

    def gen_iface_method_decl_file(
        self,
        iface_cpp_info: IfaceCppInfo,
        iface_napi_info: IfaceNAPIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.meth_decl_header}",
        ) as iface_meth_napi_decl_target:
            iface_meth_napi_decl_target.add_include("node/node_api.h")
            iface_meth_napi_decl_target.add_include(iface_cpp_info.defn_header)
            for mng_name, value in iface_napi_info.iface_register_infos.items():
                iface_meth_napi_decl_target.writelns(
                    f"static napi_value {mng_name}(napi_env env, napi_callback_info info);",
                )

    def gen_iface_method_impl_file(
        self,
        iface_cpp_info: IfaceCppInfo,
        iface_napi_info: IfaceNAPIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{iface_napi_info.meth_impl_header}",
        ) as iface_meth_napi_impl_target:
            iface_meth_napi_impl_target.add_include(iface_napi_info.meth_decl_header)
            iface_meth_napi_impl_target.add_include(iface_cpp_info.impl_header)
            for mng_name, value in iface_napi_info.iface_register_infos.items():
                iface_cpp_info_ancestor = IfaceCppInfo.get(self.am, value[1])
                with iface_meth_napi_impl_target.indented(
                    f"static napi_value {mng_name}(napi_env env, napi_callback_info info) {{",
                    f"}}",
                ):
                    iface_meth_napi_impl_target.writelns(
                        f"napi_value thisobj;",
                        f"napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr);",
                        f"{iface_cpp_info.as_owner}* value_ptr;",
                        f"napi_unwrap(env, thisobj, reinterpret_cast<void**>(&value_ptr));",
                    )
                    self.gen_func_content(
                        value[0],
                        iface_meth_napi_impl_target,
                        f"(({iface_cpp_info_ancestor.as_owner})(*value_ptr))->{value[0].name}",
                    )

    def gen_enum(
        self,
        enum: EnumDecl,
        pkg_napi_target: CSourceWriter,
    ):
        with pkg_napi_target.indented(
            f"static napi_value Create{enum.name}(napi_env env) {{",
            f"}}",
        ):
            pkg_napi_target.writelns(
                f"napi_value enum_obj;",
                f"napi_create_object(env, &enum_obj);",
                f"napi_value key;",
            )
            for item in enum.items:
                item_ty_napi_info = TypeNAPIInfo.get(self.am, enum.ty_ref.resolved_ty)
                item_ty_cpp_info = TypeCppInfo.get(self.am, enum.ty_ref.resolved_ty)
                item_ty_napi_info.into_napi(
                    pkg_napi_target,
                    f"(({item_ty_cpp_info.as_owner}){dumps(item.value)})",
                    f"value_{item.name}",
                )
                pkg_napi_target.writelns(
                    f'napi_create_string_utf8(env, "{item.name}", NAPI_AUTO_LENGTH, &key);',
                    f'napi_set_named_property(env, enum_obj, "{item.name}", value_{item.name});',
                    f"napi_set_property(env, enum_obj, value_{item.name}, key);",
                )
            pkg_napi_target.writelns(
                f"return enum_obj;",
            )

    def gen_iface_register(
        self,
        iface: IfaceDecl,
        pkg_napi_target: CSourceWriter,
    ):
        iface_napi_info = IfaceNAPIInfo.get(self.am, iface)
        pkg_napi_target.add_include(iface_napi_info.impl_header)
        pkg_napi_target.writelns(
            f"{iface_napi_info.create_func_name}(env, exports);",
        )

    def gen_struct_register(
        self,
        struct: StructDecl,
        pkg_napi_target: CSourceWriter,
    ):
        struct_napi_info = StructNAPIInfo.get(self.am, struct)
        pkg_napi_target.add_include(struct_napi_info.impl_header)
        pkg_napi_target.writelns(
            f"{struct_napi_info.create_func_name}(env, exports);",
        )

    def gen_enum_register(
        self,
        enum: EnumDecl,
        pkg_napi_target: CSourceWriter,
    ):
        pkg_napi_target.writelns(
            f"napi_value enum_obj_{enum.name} = Create{enum.name}(env);",
            f'napi_set_named_property(env, exports, "{enum.name}", enum_obj_{enum.name});',
        )

    def gen_union_files(
        self,
        union: UnionDecl,
    ):
        union_cpp_info = UnionCppInfo.get(self.am, union)
        union_napi_info = UnionNAPIInfo.get(self.am, union)
        self.gen_union_conv_decl_file(
            union,
            union_cpp_info,
            union_napi_info,
        )
        self.gen_union_conv_impl_file(
            union,
            union_cpp_info,
            union_napi_info,
        )

    def gen_union_conv_decl_file(
        self,
        union: UnionDecl,
        union_cpp_info: UnionCppInfo,
        union_napi_info: UnionNAPIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{union_napi_info.decl_header}",
        ) as union_napi_decl_target:
            union_napi_decl_target.add_include(union_cpp_info.defn_header)
            union_napi_decl_target.writelns(
                f"{union_cpp_info.as_owner} {union_napi_info.from_napi_func_name}(napi_env env, napi_value napi_obj);",
                f"napi_value {union_napi_info.into_napi_func_name}(napi_env env, {union_cpp_info.as_param} cpp_obj);",
            )

    def gen_union_conv_impl_file(
        self,
        union: UnionDecl,
        union_cpp_info: UnionCppInfo,
        union_napi_info: UnionNAPIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{union_napi_info.impl_header}",
        ) as union_napi_impl_target:
            union_napi_impl_target.add_include(union_napi_info.decl_header)
            union_napi_impl_target.add_include(union_cpp_info.impl_header)
            self.gen_union_from_napi_func(
                union,
                union_cpp_info,
                union_napi_info,
                union_napi_impl_target,
            )
            self.gen_union_into_napi_func(
                union,
                union_cpp_info,
                union_napi_info,
                union_napi_impl_target,
            )

    def gen_union_from_napi_func(
        self,
        union: UnionDecl,
        union_cpp_info: UnionCppInfo,
        union_napi_info: UnionNAPIInfo,
        union_napi_impl_target: CHeaderWriter,
    ):
        with union_napi_impl_target.indented(
            f"inline {union_cpp_info.as_owner} {union_napi_info.from_napi_func_name}(napi_env env, napi_value napi_obj) {{",
            f"}}",
        ):
            union_napi_impl_target.writelns(
                f"napi_valuetype value_ty;",
                f"napi_typeof(env, napi_obj, &value_ty);",
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
                final_napi_info = UnionFieldNAPIInfo.get(self.am, final)
                if isinstance(final_ty := final_napi_info.field_ty, Type):
                    type_napi_info = TypeNAPIInfo.get(self.am, final_ty)
                    if isinstance(final_ty, ScalarType | StringType):
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
                    elif isinstance(final_ty, ArrayType):
                        union_napi_impl_target.writelns(
                            f"napi_is_array(env, napi_obj, &flag);",
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
                    elif isinstance(final_ty, MapType):
                        union_napi_impl_target.writelns(
                            f"napi_value global = nullptr, map_ctor = nullptr;",
                            f"napi_get_global(env, &global);",
                            f'napi_get_named_property(env, global, "Map", &map_ctor);',
                            f"napi_instanceof(env, napi_obj, map_ctor, &flag);",
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
                elif final_napi_info.field_ty == "null":
                    with union_napi_impl_target.indented(
                        f"if (value_ty == napi_null) {{",
                        f"}}",
                    ):
                        union_napi_impl_target.writelns(
                            f"return {union_cpp_info.full_name}({static_tags_str});",
                        )
                elif final_napi_info.field_ty == "undefined":
                    with union_napi_impl_target.indented(
                        f"if (value_ty == napi_undefined) {{",
                        f"}}",
                    ):
                        union_napi_impl_target.writelns(
                            f"return {union_cpp_info.full_name}({static_tags_str});",
                        )

    def gen_union_into_napi_func(
        self,
        union: UnionDecl,
        union_cpp_info: UnionCppInfo,
        union_napi_info: UnionNAPIInfo,
        union_napi_impl_target: CHeaderWriter,
    ):
        with union_napi_impl_target.indented(
            f"inline napi_value {union_napi_info.into_napi_func_name}(napi_env env, {union_cpp_info.as_param} cpp_value) {{",
            f"}}",
        ):
            union_napi_impl_target.writelns(
                f"napi_value napi_obj = nullptr;",
            )
            with union_napi_impl_target.indented(
                f"switch (cpp_value.get_tag()) {{",
                f"}}",
                indent="",
            ):
                for field in union.fields:
                    field_napi_info = UnionFieldNAPIInfo.get(self.am, field)
                    with union_napi_impl_target.indented(
                        f"case {union_cpp_info.full_name}::tag_t::{field.name}: {{",
                        f"}}",
                    ):
                        match field_napi_info.field_ty:
                            case "null":
                                union_napi_impl_target.writelns(
                                    f"napi_value napi_obj_field = nullptr;",
                                    f"napi_get_null(env, &napi_obj_field);",
                                )
                            case "undefined":
                                union_napi_impl_target.writelns(
                                    f"napi_value napi_obj_field = nullptr;",
                                    f"napi_get_undefined(env, &napi_obj_field);",
                                )
                            case field_ty if isinstance(field_ty, Type):
                                type_napi_info = TypeNAPIInfo.get(self.am, field_ty)
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
