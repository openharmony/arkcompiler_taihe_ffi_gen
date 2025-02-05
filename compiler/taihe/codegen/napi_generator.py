from typing import Optional

from taihe.codegen.abi_generator import (
    COutputBuffer,
)
from taihe.codegen.cpp_proj_generator import PackageCppProjInfo
from taihe.semantics.declarations import (
    GlobFuncDecl,
    Package,
    PackageGroup,
)
from taihe.semantics.types import (
    BOOL,
    F32,
    F64,
    I32,
    I64,
    STRING,
    U32,
    Any,
    ScalarType,
    SpecialType,
    Type,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager


class PackageNapiInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.napi.cpp"
        self.full_name = "::".join(p.segments)


class TypeNapiInfo(AbstractAnalysis[Optional[Type]], TypeVisitor[None]):
    def __init__(self, am: AnalysisManager, t: Optional[Type]) -> None:
        self.am = am
        self.as_c = None
        self.from_c_to_js_func = None
        self.from_js_to_c_func = None
        self.from_c_to_js_param = None
        self.handle_type(t)

    def visit_scalar_type(self, t: ScalarType):
        as_napi = {
            BOOL: "bool",
            F32: "double",
            F64: "double",
            I32: "int32",
            I64: "int64",
            U32: "uint32",
        }.get(t)

        as_c = {
            BOOL: "bool",
            F32: "double",
            F64: "double",
            I32: "int32_t",
            I64: "int64_t",
            U32: "uint32_t",
        }.get(t)
        self.as_c = as_c
        self.from_js_to_c_func = f"napi_get_value_{as_napi}"
        if t == BOOL:
            self.from_c_to_js_func = f"napi_get_boolean"
        else:
            self.from_c_to_js_func = f"napi_create_{as_napi}"
        self.from_c_to_js_param = "env, value, &result"
        if as_napi is None or as_c is None:
            raise ValueError

    def visit_special_type(self, t: SpecialType) -> Any:
        if t == STRING:
            self.as_c = "taihe::core::string"
            self.from_js_to_c_func = "napi_get_value_string_utf8"
            self.from_c_to_js_func = "napi_create_string_utf8"
            self.from_c_to_js_param = "env, value.c_str(), value.size(), &result"


class NapiCodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: Package):
        pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
        pkg_cpp_proj_info = PackageCppProjInfo.get(self.am, pkg)
        pkg_napi_target = COutputBuffer.create(
            self.tm, f"{pkg_napi_info.header}", False
        )
        pkg_napi_target.include("node/node_api.h")
        pkg_napi_target.include(pkg_cpp_proj_info.header)

        desc = []
        for func in pkg.functions:
            self.gen_func(func, pkg_napi_info, pkg_napi_target)
            func_desc = f'        {{"{func.name}", nullptr, napi_{func.name}, nullptr, nullptr, nullptr, napi_default, nullptr}}'
            desc.append(func_desc)

        desc_str = ", \n".join(desc)
        pkg_napi_target.write(
            f"napi_value module_init(napi_env env, napi_value exports) {{\n"
            f"    napi_property_descriptor desc[] = {{\n"
            f"{desc_str}\n"
            f"    }};\n"
            f"    napi_define_properties(env, exports, sizeof(desc) / sizeof(desc[0]), desc);\n"
            f"    return exports;\n"
            f"}}\n"
            f"NAPI_MODULE(my_api, module_init);"
        )

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_napi_info: PackageNapiInfo,
        pkg_napi_target: COutputBuffer,
    ):
        pkg_napi_target.write(
            f"napi_value napi_{func.name}(napi_env env, napi_callback_info info)\n"
            f"{{\n"
            f"    size_t argc = {len(func.params)};\n"
            f"    napi_value args[{len(func.params)}] = {{nullptr}};\n"
            f"    napi_get_cb_info(env, info, &argc, args , nullptr, nullptr);\n"
        )
        args = []
        for i, param in enumerate(func.params):
            if param.ty_ref.resolved_ty == STRING:
                pkg_napi_target.write(
                    f"    size_t length{i} = 0;\n"
                    f"    napi_get_value_string_utf8(env, args[{i}], nullptr, 0, &length{i});\n"
                    f"    char value{i}[length{i} + 1];\n"
                    f"    napi_get_value_string_utf8(env, args[{i}], value{i}, length{i} + 1, &length{i});\n"
                    f"    taihe::core::string_view th_value{i}(value{i});\n"
                )
                args.append(f"th_value{i}")
                continue
            type_napi_param_info = TypeNapiInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_napi_target.write(
                f"    {type_napi_param_info.as_c} value{i};\n"
                f"    {type_napi_param_info.from_js_to_c_func}(env, args[{i}], &value{i});\n"
            )
            args.append(f"value{i}")
        args_str = ", ".join(args)
        full_func_name = pkg_napi_info.full_name + "::" + func.name
        if func.return_ty_ref:
            type_napi_return_info = TypeNapiInfo.get(
                self.am, func.return_ty_ref.resolved_ty
            )
            pkg_napi_target.write(
                f"    {type_napi_return_info.as_c} value = {full_func_name}({args_str});\n"
                f"    napi_value result;\n"
                f"    {type_napi_return_info.from_c_to_js_func}({type_napi_return_info.from_c_to_js_param});\n"
                f"    return result;\n"
                f"}}\n"
            )
        else:
            pkg_napi_target.write(
                f"    {full_func_name}({args_str});\n"
                f"    napi_value result;\n"
                f"    napi_get_undefined(env, &result);\n"
                f"    return result;\n"
                f"}}\n"
            )
