from taihe.codegen.abi.writer import CSourceWriter
from taihe.codegen.cpp.analyses import (
    PackageCppUserInfo,
    TypeCppInfo,
)
from taihe.codegen.napi.analyses import PackageNapiInfo, TypeNapiInfo
from taihe.semantics.declarations import (
    GlobFuncDecl,
    PackageDecl,
    PackageGroup,
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
        pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
        pkg_cpp_user_info = PackageCppUserInfo.get(self.am, pkg)
        with CSourceWriter(
            self.oc,
            f"src/{pkg_napi_info.source}",
        ) as pkg_napi_target:
            pkg_napi_target.add_include("node/node_api.h")
            pkg_napi_target.add_include(pkg_cpp_user_info.header)

            desc = []
            for func in pkg.functions:
                self.gen_func(func, pkg_napi_info, pkg_napi_target)
                func_desc = f'{{"{func.name}", nullptr, napi_{func.name}, nullptr, nullptr, nullptr, napi_default, nullptr}}, '
                desc.append(func_desc)
            self.gen_module_init(desc, pkg_napi_target)

    def gen_module_init(
        self,
        desc: list[str],
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
                for desc_str in desc:
                    pkg_napi_target.writelns(desc_str)
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
        pkg_napi_info: PackageNapiInfo,
        pkg_napi_target: CSourceWriter,
    ):
        with pkg_napi_target.indented(
            f"static napi_value napi_{func.name}(napi_env env, napi_callback_info info) {{",
            f"}}",
        ):
            func_name = pkg_napi_info.cpp_ns + "::" + func.name
            self.gen_func_content(func, pkg_napi_target, func_name)

    def gen_func_content(
        self,
        func: GlobFuncDecl,
        pkg_napi_target: CSourceWriter,
        func_name: str,
    ):
        self.gen_func_get_cb_info(len(func.params), pkg_napi_target)
        args = []
        for i, param in enumerate(func.params):
            value_ty = param.ty_ref.resolved_ty
            type_info = TypeNapiInfo.get(self.am, value_ty)
            type_info.from_napi(pkg_napi_target, f"args[{i}]", f"value{i}")
            args.append(f"value{i}")
        args_str = ", ".join(args)

        if return_ty_ref := func.return_ty_ref:
            value_ty = return_ty_ref.resolved_ty
            cpp_return_info = TypeCppInfo.get(self.am, value_ty)
            pkg_napi_target.writelns(
                f"{cpp_return_info.as_owner} value = {func_name}({args_str});",
            )
            type_info = TypeNapiInfo.get(self.am, value_ty)
            type_info.into_napi(pkg_napi_target, "value", "result")
        else:
            pkg_napi_target.writelns(
                f"{func_name}({args_str});",
                f"napi_value result = nullptr;",
                f"napi_get_undefined(env, &result);",
            )
        pkg_napi_target.writelns(f"return result;")

    def gen_func_get_cb_info(
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
