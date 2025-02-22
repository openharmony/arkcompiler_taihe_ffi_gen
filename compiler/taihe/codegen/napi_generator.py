from typing_extensions import override
from abc import ABCMeta

from taihe.codegen.abi_generator import (
    COutputBuffer,
    IfaceDeclABIInfo
)
from taihe.codegen.cpp_proj_generator import (
    TypeCppProjInfo,
    ScalarTypeCppProjInfo,
    IfaceDeclCppProjInfo,
    PackageCppProjInfo,
    StructDeclCppProjInfo,
)
from taihe.semantics.declarations import (
    IfaceDecl,
    GlobFuncDecl,
    IfaceMethodDecl,
    Package,
    PackageGroup,
    StructDecl,
)
from taihe.semantics.types import (
    BOOL,
    F32,
    F64,
    I32,
    I64,
    STRING,
    U32,
    IfaceType,
    ScalarType,
    SpecialType,
    StructType,
    Type,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager


class PackageNapiInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.napi.cpp"
        self.kn_header = f"kn_{p.name}.napi.cpp"
        self.full_name = "::".join(p.segments)


class AbstractTypeNapiInfo(metaclass=ABCMeta):
    pass


class ScalarTypeNapiInfo(AbstractAnalysis[ScalarType], AbstractTypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        as_napi = {
            BOOL: "bool",
            F32: "double",
            F64: "double",
            I32: "int32",
            I64: "int64",
            U32: "uint32",
        }[t]

        self.as_napi_c = {
            BOOL: "bool",
            F32: "double",
            F64: "double",
            I32: "int32_t",
            I64: "int64_t",
            U32: "uint32_t",
        }[t]

        self.from_js_to_c_func = f"napi_get_value_{as_napi}"
        if t == BOOL:
            self.from_c_to_js_func = f"napi_get_boolean"
        else:
            self.from_c_to_js_func = f"napi_create_{as_napi}"
        if as_napi is None or self.as_napi_c is None:
            raise ValueError


class SpecialTypeNapiInfo(AbstractAnalysis[SpecialType], AbstractTypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: SpecialType):
        if t == STRING:
            self.as_napi_c = "taihe::core::string"
            self.from_js_to_c_func = "napi_get_value_string_utf8"
            self.from_c_to_js_func = "napi_create_string_utf8"


class StrcutTypeNapiInfo(AbstractAnalysis[StructType], AbstractTypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: StructType):
        struct_napi_info = StructDeclCppProjInfo.get(am, t.ty_decl)
        self.as_napi_c = struct_napi_info.as_field


class IfaceTypeNapiInfo(AbstractAnalysis[IfaceType], AbstractTypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        iface_napi_info = IfaceDeclCppProjInfo.get(am, t.ty_decl)
        self.as_napi_c = iface_napi_info.as_field


class TypeNapiInfo(TypeVisitor[AbstractTypeNapiInfo]):
    def __init__(self, am: AnalysisManager):
        self.am = am

    @staticmethod
    def get(am: AnalysisManager, t: Type | None):
        assert t is not None
        return TypeNapiInfo(am).handle_type(t)

    @override
    def visit_struct_type(self, t: StructType) -> AbstractTypeNapiInfo:
        return StrcutTypeNapiInfo.get(self.am, t)

    @override
    def visit_iface_type(self, t: IfaceType) -> AbstractTypeNapiInfo:
        return IfaceTypeNapiInfo.get(self.am, t)

    @override
    def visit_scalar_type(self, t: ScalarType) -> AbstractTypeNapiInfo:
        return ScalarTypeNapiInfo.get(self.am, t)

    @override
    def visit_special_type(self, t: SpecialType) -> AbstractTypeNapiInfo:
        return SpecialTypeNapiInfo.get(self.am, t)


class NapiCodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup, kn: bool = False):
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

        self.gen_special_type_func(pkg_napi_target)

        desc = []
        for iface in pkg.interfaces:
            self.gen_iface(pkg_napi_target, iface)
        for struct in pkg.structs:
            self.gen_struct_constructor(struct, pkg_napi_target)
            func_desc = f'        {{"make_{struct.name}", nullptr, construct_js_{struct.name}, nullptr, nullptr, nullptr, napi_default, nullptr}}'
            desc.append(func_desc)
        for func in pkg.functions:
            self.gen_func(func, pkg_napi_info, pkg_napi_target)
            func_desc = f'        {{"{func.name}", nullptr, napi_{func.name}, nullptr, nullptr, nullptr, napi_default, nullptr}}'
            desc.append(func_desc)

        desc_str = ", \n".join(desc)
        self.gen_module_init(desc_str, pkg_napi_target)

    def gen_special_type_func(self, pkg_napi_target: COutputBuffer):
        pkg_napi_target.write(
            f"inline taihe::core::string get_special_type(napi_env env, napi_value js_obj) {{\n"
            f"    size_t len_c_obj = 0;\n"
            f"    napi_get_value_string_utf8(env, js_obj, nullptr, 0, &len_c_obj);\n"
            f"    char char_c_obj[len_c_obj + 1];\n"
            f"    napi_get_value_string_utf8(env, js_obj, char_c_obj, len_c_obj + 1, &len_c_obj);\n"
            f"    taihe::core::string c_obj(char_c_obj);\n"
            f"    return c_obj;\n"
            f"}}\n"
        )

        pkg_napi_target.write(
            f"inline napi_value create_special_type(napi_env env, taihe::core::string_view c_obj) {{\n"
            f"    napi_value js_obj = nullptr;\n"
            f"    napi_create_string_utf8(env, c_obj.c_str(), c_obj.size(), &js_obj);\n"
            f"    return js_obj;\n"
            f"}}\n"
        )

    def gen_iface(self, pkg_napi_target: COutputBuffer, iface: IfaceDecl):
        iface_cpp_info = IfaceDeclCppProjInfo.get(self.am, iface)
        pkg_napi_target.write(
            f"inline {iface_cpp_info.as_field} get_{iface.name}(napi_env env, napi_value js_obj) {{\n"
            f"    struct {{\n"
            f"        void* vtbl_ptr;\n"
            f"        ::taihe::core::data_holder holder;\n"
            f"    }}* buffer;\n"
            f"    napi_unwrap(env, js_obj, reinterpret_cast<void **>(&buffer));\n"
            f"    {iface_cpp_info.as_field} c_obj = {iface_cpp_info.as_field}(buffer->holder);\n"
            f"    return c_obj;\n"
            f"}}\n"
        )

        pkg_napi_target.write(
            f"inline napi_value create_{iface.name}(napi_env env, {iface_cpp_info.as_param} c_obj) {{\n"
            f"    {iface_cpp_info.as_field}* value_ptr = new {iface_cpp_info.as_field}(c_obj);\n"
            f"    napi_value js_obj = nullptr;\n"
            f"    napi_create_object(env, &js_obj);\n\n"
        )

        iface_abi_info = IfaceDeclABIInfo.get(self.am, iface)
        for ancestor in iface_abi_info.ancestor_dict:
            iface_ance_cpp_info = IfaceDeclCppProjInfo.get(self.am, ancestor)
            for func in ancestor.methods:
                self.gen_iface_func(func, pkg_napi_target, iface.name, iface_cpp_info.as_field, iface_ance_cpp_info.as_param)

        pkg_napi_target.write(
            f"    napi_wrap(env, js_obj, value_ptr, [](napi_env env, void* finalize_data, void* finalize_hint) {{\n"
            f"      delete static_cast<{iface_cpp_info.as_field}*>(finalize_data);\n"
            f"    }}, nullptr, nullptr);\n"
            f"    return js_obj;\n"
            f"}}\n"
        )

    def gen_iface_func(self, func: IfaceMethodDecl, pkg_napi_target: COutputBuffer, iface_name: str, iface_cpp_type: str, iface_ancest_cpp_type: str):
        pkg_napi_target.write(
            f"    napi_value {iface_name}_{func.name};\n"
            f'    napi_create_function(env, "{func.name}", NAPI_AUTO_LENGTH, \n'
            f"      [](napi_env env, napi_callback_info info) -> napi_value {{\n"
            f"    napi_value thisobj;\n"
            f"    napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr);\n"
            f"    {iface_cpp_type}* value_ptr;\n"
            f"    napi_unwrap(env, thisobj, reinterpret_cast<void**>(&value_ptr));\n"
        )
        self.gen_func_content(func, pkg_napi_target, f"{iface_ancest_cpp_type}(*value_ptr)->{func.name}")
        pkg_napi_target.write(
            f"    }}, nullptr, &{iface_name}_{func.name});\n"
            f'    napi_set_named_property(env, js_obj, "{func.name}", {iface_name}_{func.name});\n\n'
        )

    def gen_module_init(self, desc_str: str, pkg_napi_target: COutputBuffer):
        pkg_napi_target.write(
            f"EXTERN_C_START\n"
            f"napi_value Init(napi_env env, napi_value exports) {{\n"
            f"    napi_property_descriptor desc[] = {{\n"
            f"{desc_str}\n"
            f"    }};\n"
            f"    napi_define_properties(env, exports, sizeof(desc) / sizeof(desc[0]), desc);\n"
            f"    return exports;\n"
            f"}}\n"
            f"EXTERN_C_END\n"
            f"static napi_module demoModule = {{\n"
            f"    .nm_version = 1,\n"
            f"    .nm_flags = 0,\n"
            f"    .nm_filename = nullptr,\n"
            f"    .nm_register_func = Init,\n"
            f'    .nm_modname = "entry",\n'
            f"    .nm_priv = ((void*)0),\n"
            f"    .reserved = {{ 0 }},\n"
            f"}};\n"
            f'extern "C" __attribute__((constructor)) void RegisterEntryModule(void)\n'
            f"{{\n"
            f"    napi_module_register(&demoModule);\n"
            f"}}\n"
        )

    def gen_struct_constructor(
        self, struct: StructDecl, pkg_napi_target: COutputBuffer
    ):
        pkg_napi_target.write(
            f"static napi_value construct_js_{struct.name}(napi_env env, napi_callback_info info) {{\n"
            f"    napi_value obj = nullptr;\n"
            f"    napi_create_object(env, &obj);\n"
        )
        self.gen_func_get_cb_info(len(struct.fields), pkg_napi_target)
        for i, field in enumerate(struct.fields):
            pkg_napi_target.write(
                f'    napi_set_named_property(env, obj, "{field.name}", args[{i}]);\n'
            )
        pkg_napi_target.write(f"    return obj;\n" f"}}\n")

        struct_cpp_info = StructDeclCppProjInfo.get(self.am, struct)
        pkg_napi_target.write(
            f"inline {struct_cpp_info.as_field} get_{struct.name}(napi_env env, napi_value js_obj) {{\n"
        )
        for field in struct.fields:
            pkg_napi_target.write(
                f"    napi_value {field.name}_v = nullptr;\n"
                f'    napi_get_named_property(env, js_obj, "{field.name}", &{field.name}_v);\n'
            )
            self.gen_func_get_value(
                field.ty_ref.resolved_ty,
                pkg_napi_target,
                f"{field.name}_v",
                field.name,
            )
        pkg_napi_target.write(f"    {struct_cpp_info.as_field} c_obj = {{\n")
        for field in struct.fields:
            pkg_napi_target.write(
                f"        .{field.name} = std::move({field.name}),\n"
            )
        pkg_napi_target.write(
            f"    }};\n"
            f"    return c_obj;\n"
            f"}}\n"
        )

        pkg_napi_target.write(
            f"inline napi_value create_{struct.name}(napi_env env, {struct_cpp_info.as_param} c_obj) {{\n"
            f"    napi_value js_obj = nullptr;\n"
            f"    napi_create_object(env, &js_obj);\n"
        )
        for field in struct.fields:
            self.gen_func_return_value(
                field.ty_ref.resolved_ty,
                pkg_napi_target,
                f"c_obj.{field.name}",
                field.name,
            )
            pkg_napi_target.write(
                f'    napi_set_named_property(env, js_obj, "{field.name}", {field.name});\n'
            )
        pkg_napi_target.write(
            f"    return js_obj;\n"
            f"}}\n"
        )

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_napi_info: PackageNapiInfo,
        pkg_napi_target: COutputBuffer,
    ):
        pkg_napi_target.write(
            f"static napi_value napi_{func.name}(napi_env env, napi_callback_info info)\n"
            f"{{\n"
        )
        func_name = pkg_napi_info.full_name + "::" + func.name
        self.gen_func_content(func, pkg_napi_target, func_name)
        pkg_napi_target.write(f"}}\n")

    def gen_func_content(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        pkg_napi_target: COutputBuffer,
        func_name: str,
    ):
        self.gen_func_get_cb_info(len(func.params), pkg_napi_target)
        args = []
        for i, param in enumerate(func.params):
            value_ty = param.ty_ref.resolved_ty
            self.gen_func_get_value(
                value_ty, pkg_napi_target, f"args[{i}]", f"value{i}"
            )
            args.append(f"value{i}")
        args_str = ", ".join(args)

        if return_ty_ref := func.return_ty_ref:
            value_ty = return_ty_ref.resolved_ty
            cpp_return_info = TypeCppProjInfo.get(self.am, value_ty)
            pkg_napi_target.write(
                f"    {cpp_return_info.as_field} value = {func_name}({args_str});\n"
            )
            self.gen_func_return_value(value_ty, pkg_napi_target, "value", "result")
        else:
            pkg_napi_target.write(
                f"    {func_name}({args_str});\n"
                f"    napi_value result = nullptr;\n"
                f"    napi_get_undefined(env, &result);\n"
            )
        pkg_napi_target.write(f"    return result;\n")

    def gen_func_get_cb_info(self, params_num: int, pkg_napi_target: COutputBuffer):
        if params_num:
            pkg_napi_target.write(
                f"    size_t argc = {params_num};\n"
                f"    napi_value args[{params_num}] = {{nullptr}};\n"
                f"    napi_get_cb_info(env, info, &argc, args , nullptr, nullptr);\n"
            )

    def gen_func_get_value(
        self,
        value_ty: Type | None,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
    ):
        if isinstance(value_ty, ScalarType):
            self.gen_func_get_js_scalar_value(value_ty, pkg_napi_target, value, result)
        if isinstance(value_ty, SpecialType):
            self.gen_func_get_js_special_value(value_ty, pkg_napi_target, value, result)
        if isinstance(value_ty, StructType):
            self.gen_func_get_js_struct_value(value_ty, pkg_napi_target, value, result)
        if isinstance(value_ty, IfaceType):
            self.gen_func_get_js_iface_value(value_ty, pkg_napi_target, value, result)

    def gen_func_get_js_struct_value(
        self,
        value_ty: StructType,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
    ):
        struct_cpp_info = StructDeclCppProjInfo.get(self.am, value_ty.ty_decl)
        pkg_napi_target.write(
            f"    {struct_cpp_info.as_field} {result} = get_{value_ty.ty_decl.name}(env, {value});\n"
        )

    def gen_func_get_js_scalar_value(
        self,
        value_ty: ScalarType,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
    ):
        scalar_napi_info = ScalarTypeNapiInfo.get(self.am, value_ty)
        scalar_cpp_info = ScalarTypeCppProjInfo.get(self.am, value_ty)
        pkg_napi_target.write(
            f"    {scalar_napi_info.as_napi_c} {result}_;\n"
            f"    {scalar_napi_info.from_js_to_c_func}(env, {value}, &{result}_);\n"
            f"    {scalar_cpp_info.as_field} {result} = {result}_;\n"
        )

    def gen_func_get_js_special_value(
        self,
        value_ty: SpecialType,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
    ):
        if value_ty == STRING:
            pkg_napi_target.write(
            f"    taihe::core::string {result} = get_special_type(env, {value});\n"
            )
        else:
            raise ValueError(value_ty)

    def gen_func_get_js_iface_value(
        self,
        value_ty: IfaceType,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
    ):
        iface_cpp_info = IfaceDeclCppProjInfo.get(self.am, value_ty.ty_decl)
        pkg_napi_target.write(
            f"    {iface_cpp_info.as_field} {result} = get_{value_ty.ty_decl.name}(env, {value});\n"
        )

    def gen_func_return_value(
        self,
        value_ty: Type | None,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
    ):
        if isinstance(value_ty, ScalarType):
            self.gen_func_create_js_scalar_value(
                value_ty, pkg_napi_target, value, result
            )
        if isinstance(value_ty, SpecialType):
            self.gen_func_create_js_special_value(
                value_ty, pkg_napi_target, value, result
            )
        if isinstance(value_ty, StructType):
            self.gen_func_create_js_struct_value(
                value_ty, pkg_napi_target, value, result
            )
        if isinstance(value_ty, IfaceType):
            self.gen_func_create_js_iface_value(
                value_ty, pkg_napi_target, value, result
            )

    def gen_func_create_js_struct_value(
        self,
        value_ty: StructType,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
    ):
        pkg_napi_target.write(
            f"    napi_value {result} = create_{value_ty.ty_decl.name}(env, {value});\n"
        )

    def gen_func_create_js_scalar_value(
        self,
        value_ty: ScalarType,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
    ):
        type_napi_param_info = ScalarTypeNapiInfo.get(self.am, value_ty)
        pkg_napi_target.write(
            f"    napi_value {result} = nullptr;\n"
            f"    {type_napi_param_info.from_c_to_js_func}(env, {value}, &{result});\n"
        )

    def gen_func_create_js_special_value(
        self,
        value_ty: SpecialType,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
    ):
        if value_ty == STRING:
            pkg_napi_target.write(
                f"    napi_value {result} = create_special_type(env, {value});\n"
            )
        else:
            raise ValueError(value_ty)

    def gen_func_create_js_iface_value(
        self,
        value_ty: IfaceType,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
    ):
        pkg_napi_target.write(
            f"    napi_value {result} = create_{value_ty.ty_decl.name}(env, {value});\n"
        )
