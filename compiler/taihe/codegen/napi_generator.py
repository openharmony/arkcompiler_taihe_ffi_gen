from abc import ABCMeta, abstractmethod

from typing_extensions import override

from taihe.codegen.abi_generator import COutputBuffer, IfaceDeclABIInfo
from taihe.codegen.cpp_proj_generator import (
    IfaceDeclCppProjInfo,
    PackageCppProjInfo,
    ScalarTypeCppProjInfo,
    StructDeclCppProjInfo,
    TypeCppProjInfo,
)
from taihe.semantics.declarations import (
    GlobFuncDecl,
    IfaceDecl,
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
    @abstractmethod
    def get_value_from_js(
        self,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        pass

    @abstractmethod
    def create_value_as_js(
        self,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        pass


class ScalarTypeNapiInfo(AbstractAnalysis[ScalarType], AbstractTypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        self.am = am
        self.type = t

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

    def get_value_from_js(
        self,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        scalar_cpp_info = ScalarTypeCppProjInfo.get(self.am, self.type)
        pkg_napi_target.write(
            f"{space_num * ' '}{self.as_napi_c} {result}_tmp;\n"
            f"{space_num * ' '}{self.from_js_to_c_func}(env, {value}, &{result}_tmp);\n"
            f"{space_num * ' '}{scalar_cpp_info.as_field} {result} = {result}_tmp;\n"
        )
        return

    def create_value_as_js(
        self,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        type_napi_param_info = ScalarTypeNapiInfo.get(self.am, self.type)
        pkg_napi_target.write(
            f"{space_num * ' '}napi_value {result} = nullptr;\n"
            f"{space_num * ' '}{type_napi_param_info.from_c_to_js_func}(env, {value}, &{result});\n"
        )


class SpecialTypeNapiInfo(AbstractAnalysis[SpecialType], AbstractTypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: SpecialType):
        self.am = am
        self.type = t
        if t == STRING:
            self.as_napi_c = "taihe::core::string"
            self.from_js_to_c_func = "napi_get_value_string_utf8"
            self.from_c_to_js_func = "napi_create_string_utf8"

    def get_value_from_js(
        self,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        if self.type == STRING:
            pkg_napi_target.write(
                f"{space_num * ' '}taihe::core::string {result} = get_string(env, {value});\n"
            )

    def create_value_as_js(
        self,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        if self.type == STRING:
            pkg_napi_target.write(
                f"{space_num * ' '}napi_value {result} = create_string(env, {value});\n"
            )


class StrcutTypeNapiInfo(AbstractAnalysis[StructType], AbstractTypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: StructType):
        struct_napi_info = StructDeclCppProjInfo.get(am, t.ty_decl)
        self.as_napi_c = struct_napi_info.as_field
        self.am = am
        self.type = t

    def get_value_from_js(
        self,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        struct_cpp_info = StructDeclCppProjInfo.get(self.am, self.type.ty_decl)
        pkg_napi_target.write(
            f"{space_num * ' '}{struct_cpp_info.as_field} {result} = get_{self.type.ty_decl.name}(env, {value});\n"
        )

    def create_value_as_js(
        self,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        pkg_napi_target.write(
            f"{space_num * ' '}napi_value {result} = create_{self.type.ty_decl.name}(env, std::move({value}));\n"
        )


class IfaceTypeNapiInfo(AbstractAnalysis[IfaceType], AbstractTypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        iface_napi_info = IfaceDeclCppProjInfo.get(am, t.ty_decl)
        self.as_napi_c = iface_napi_info.as_field
        self.am = am
        self.type = t

    def get_value_from_js(
        self,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        iface_cpp_info = IfaceDeclCppProjInfo.get(self.am, self.type.ty_decl)
        pkg_napi_target.write(
            f"{space_num * ' '}{iface_cpp_info.as_field} {result} = get_{self.type.ty_decl.name}(env, {value});\n"
        )

    def create_value_as_js(
        self,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        pkg_napi_target.write(
            f"{space_num * ' '}napi_value {result} = create_{self.type.ty_decl.name}(env, std::move({value}));\n"
        )


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

        self.gen_string_convert_func(pkg_napi_target)

        desc = []
        for iface in pkg.interfaces:
            self.gen_iface(pkg_napi_target, iface)
            func_desc = f'        {{"as_{iface.name}", nullptr, as_{iface.name}, nullptr, nullptr, nullptr, napi_default, nullptr}}'
            desc.append(func_desc)
            func_desc = f'        {{"impl_{iface.name}", nullptr, impl_{iface.name}, nullptr, nullptr, nullptr, napi_default, nullptr}}'
            desc.append(func_desc)
        for struct in pkg.structs:
            self.gen_struct_constructor(struct, pkg_napi_target)
            func_desc = f'        {{"make_{struct.name}", nullptr, construct_js_{struct.name}, nullptr, nullptr, nullptr, napi_default, nullptr}}'
            desc.append(func_desc)
            self.gen_struct_convert_func(struct, pkg_napi_target)
        for func in pkg.functions:
            self.gen_func(func, pkg_napi_info, pkg_napi_target)
            func_desc = f'        {{"{func.name}", nullptr, napi_{func.name}, nullptr, nullptr, nullptr, napi_default, nullptr}}'
            desc.append(func_desc)

        desc_str = ", \n".join(desc)
        self.gen_module_init(desc_str, pkg_napi_target)

    def gen_string_convert_func(self, pkg_napi_target: COutputBuffer):
        pkg_napi_target.write(
            f"inline taihe::core::string get_string(napi_env env, napi_value js_obj) {{\n"
            f"    size_t len_c_obj = 0;\n"
            f"    napi_get_value_string_utf8(env, js_obj, nullptr, 0, &len_c_obj);\n"
            f"    char char_c_obj[len_c_obj + 1];\n"
            f"    napi_get_value_string_utf8(env, js_obj, char_c_obj, len_c_obj + 1, &len_c_obj);\n"
            f"    taihe::core::string c_obj(char_c_obj);\n"
            f"    return c_obj;\n"
            f"}}\n"
        )

        pkg_napi_target.write(
            f"inline napi_value create_string(napi_env env, taihe::core::string_view c_obj) {{\n"
            f"    napi_value js_obj = nullptr;\n"
            f"    napi_create_string_utf8(env, c_obj.c_str(), c_obj.size(), &js_obj);\n"
            f"    return js_obj;\n"
            f"}}\n"
        )

    def gen_iface(self, pkg_napi_target: COutputBuffer, iface: IfaceDecl):
        iface_cpp_info = IfaceDeclCppProjInfo.get(self.am, iface)
        desc = []

        for func in iface.methods:
            self.gen_iface_method(
                func, pkg_napi_target, iface.name, iface_cpp_info.as_field
            )
            func_desc = f'        {{"{func.name}", nullptr, napi_hidden_{iface.name}_{func.name}, nullptr, nullptr, nullptr, napi_default, nullptr}}'
            desc.append(func_desc)

        iface_abi_info = IfaceDeclABIInfo.get(self.am, iface)
        for ancestor in iface_abi_info.ancestor_dict:
            if ancestor != iface:
                self.gen_iface_up_convert_func(
                    pkg_napi_target, iface.name, iface_cpp_info.as_field, ancestor.name
                )
                func_desc = f'        {{"as_{ancestor.name}", nullptr, napi_hidden_{iface.name}_as{ancestor.name}, nullptr, nullptr, nullptr, napi_default, nullptr}}'
                desc.append(func_desc)

        desc_str = ",\n".join(desc)
        self.gen_iface_convert_func(pkg_napi_target, iface, desc_str)

    def gen_iface_convert_func(
        self, pkg_napi_target: COutputBuffer, iface: IfaceDecl, desc_str: str
    ):
        iface_cpp_info = IfaceDeclCppProjInfo.get(self.am, iface)
        pkg_napi_target.write(
            f"inline {iface_cpp_info.as_field} get_{iface.name}(napi_env env, napi_value js_obj) {{\n"
            f"    {iface_cpp_info.as_field}* c_obj_;\n"
            f"    napi_unwrap(env, js_obj, reinterpret_cast<void **>(&c_obj_));\n"
            f"    {iface_cpp_info.as_field} c_obj = *c_obj_;\n"
            f"    return c_obj;\n"
            f"}}\n"
        )

        pkg_napi_target.write(
            f"inline napi_value create_{iface.name}(napi_env env, {iface_cpp_info.as_field} c_obj) {{\n"
            f"    {iface_cpp_info.as_field}* value_ptr = new {iface_cpp_info.as_field}(std::move(c_obj));\n"
            f"    napi_value js_obj = nullptr;\n"
            f"    napi_create_object(env, &js_obj);\n"
            f"    napi_property_descriptor desc[] = {{\n"
            f"{desc_str}\n"
            f"    }};\n"
            f"    napi_define_properties(env, js_obj, sizeof(desc) / sizeof(desc[0]), desc);\n"
            f"    napi_wrap(env, js_obj, value_ptr, [](napi_env env, void* finalize_data, void* finalize_hint) {{\n"
            f"      delete static_cast<{iface_cpp_info.as_field}*>(finalize_data);\n"
            f"    }}, nullptr, nullptr);\n"
            f"    return js_obj;\n"
            f"}}\n"
        )

        self.gen_iface_down_convert_func(pkg_napi_target, iface)
        self.gen_iface_impl_func(pkg_napi_target, iface)

    def gen_iface_up_convert_func(
        self,
        pkg_napi_target: COutputBuffer,
        iface_name: str,
        iface_cpp_type: str,
        base_iface_name: str,
    ):
        pkg_napi_target.write(
            f"static napi_value napi_hidden_{iface_name}_as{base_iface_name}(napi_env env, napi_callback_info info) {{\n"
            f"    napi_value thisobj;\n"
            f"    napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr);\n"
            f"    {iface_cpp_type}* value_ptr;\n"
            f"    napi_unwrap(env, thisobj, reinterpret_cast<void**>(&value_ptr));\n"
            f"    napi_value base_obj = create_{base_iface_name}(env, *value_ptr);\n"
            f"    return base_obj;\n"
            f"}}\n"
        )

    def gen_iface_down_convert_func(
        self, pkg_napi_target: COutputBuffer, iface: IfaceDecl
    ):
        iface_cpp_info = IfaceDeclCppProjInfo.get(self.am, iface)
        pkg_napi_target.write(
            f"static napi_value as_{iface.name}(napi_env env, napi_callback_info info) {{\n"
            f"    size_t argc = 1;\n"
            f"    napi_value args[1] = {{nullptr}};\n"
            f"    napi_get_cb_info(env, info, &argc, args , nullptr, nullptr);\n"
            f"    struct {{\n"
            f"        void* vtbl_ptr;\n"
            f"        ::taihe::core::data_holder holder;\n"
            f"    }}* buffer;\n"
            f"    napi_unwrap(env, args[0], reinterpret_cast<void**>(&buffer));\n"
            f"    napi_value result = nullptr;\n"
            f"    if ({iface_cpp_info.as_param} c_obj = {iface_cpp_info.as_param}(buffer->holder)) {{\n"
            f"        result = create_{iface.name}(env, c_obj);\n"
            f"        return result;\n"
            f"    }} else {{\n"
            f"        napi_get_undefined(env, &result);\n"
            f"    }}\n"
            f"    return result;\n"
            f"}}\n"
        )

    def gen_iface_impl_func(self, pkg_napi_target: COutputBuffer, iface: IfaceDecl):
        iface_cpp_info = IfaceDeclCppProjInfo.get(self.am, iface)
        iface_abi_info = IfaceDeclABIInfo.get(self.am, iface)
        pkg_napi_target.write(
            f"static napi_value impl_{iface.name}(napi_env env, napi_callback_info info) {{\n"
            f"    struct NAPI_{iface.name}Impl {{\n"
            f"        napi_env env;\n"
            f"        napi_ref ref;\n"
            f"        NAPI_{iface.name}Impl(napi_env env, napi_value value) {{\n"
            f"            this->env = env;\n"
            f"            napi_create_reference(env, value, 1, &this->ref);\n"
            f"        }}\n"
            f"        ~NAPI_{iface.name}Impl() {{\n"
            f"            napi_delete_reference(this->env, this->ref);\n"
            f"        }}\n"
        )
        for ancestor in iface_abi_info.ancestor_dict:
            for func in ancestor.methods:
                self.gen_iface_impl_struct_member_func(func, pkg_napi_target)

        pkg_napi_target.write(
            f"    }};\n"
            f"    size_t argc = 1;\n"
            f"    napi_value args[1] = {{nullptr}};\n"
            f"    napi_get_cb_info(env, info, &argc, args , nullptr, nullptr);\n"
            f"    {iface_cpp_info.as_field} res = taihe::core::make_holder<NAPI_{iface.name}Impl, {iface_cpp_info.as_field}>(env, args[0]);\n"
            f"    return create_{iface.name}(env, std::move(res));\n"
            f"}}\n"
        )

    def gen_iface_impl_struct_member_func(
        self, func: IfaceMethodDecl, pkg_napi_target: COutputBuffer
    ):
        params_cpp = []
        for param in func.params:
            type_cpp_proj_info = TypeCppProjInfo.get(self.am, param.ty_ref.resolved_ty)
            params_cpp.append(f"{type_cpp_proj_info.as_param} {param.name}")
        params_cpp_str = ", ".join(params_cpp)

        if func.return_ty_ref:
            return_ty_info = TypeCppProjInfo.get(
                self.am, func.return_ty_ref.resolved_ty
            )
            return_ty_str = return_ty_info.as_field
        else:
            return_ty_str = "void"

        pkg_napi_target.write(
            f"        {return_ty_str} {func.name}({params_cpp_str}) {{\n"
        )

        if func.params:
            pkg_napi_target.write(
                f"            napi_value args_inner[{len(func.params)}];\n"
            )
            args_inner = "args_inner"
        else:
            args_inner = "nullptr"

        for i, param in enumerate(func.params):
            self.gen_func_create_value_as_js(
                param.ty_ref.resolved_ty,
                pkg_napi_target,
                f"{param.name}",
                f"value_{i}",
                12,
            )
            pkg_napi_target.write(f"            args_inner[{i}] = value_{i};\n")

        pkg_napi_target.write(
            f"            napi_value jsObject;\n"
            f"            napi_get_reference_value(env, ref, &jsObject);\n"
            f"            napi_value {func.name}Method;\n"
            f'            napi_get_named_property(env, jsObject, "{func.name}", &{func.name}Method);\n'
            f"            napi_value jsresult;\n"
            f"            napi_call_function(env, jsObject, {func.name}Method, {len(func.params)}, {args_inner}, &jsresult);\n"
        )
        if func.return_ty_ref:
            self.gen_func_get_value_from_js(
                func.return_ty_ref.resolved_ty,
                pkg_napi_target,
                "jsresult",
                "cresult",
                12,
            )
            pkg_napi_target.write(f"            return cresult;\n")
        else:
            pkg_napi_target.write(f"            return;\n")
        pkg_napi_target.write(f"        }}\n")

    def gen_iface_method(
        self,
        func: IfaceMethodDecl,
        pkg_napi_target: COutputBuffer,
        iface_name: str,
        iface_cpp_type: str,
    ):
        pkg_napi_target.write(
            f"static napi_value napi_hidden_{iface_name}_{func.name}(napi_env env, napi_callback_info info) {{\n"
            f"    napi_value thisobj;\n"
            f"    napi_get_cb_info(env, info, nullptr, nullptr, &thisobj, nullptr);\n"
            f"    {iface_cpp_type}* value_ptr;\n"
            f"    napi_unwrap(env, thisobj, reinterpret_cast<void**>(&value_ptr));\n"
        )
        self.gen_func_content(func, pkg_napi_target, f"(*value_ptr)->{func.name}", 4)
        pkg_napi_target.write(f"}}\n")

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

    def gen_struct_convert_func(
        self, struct: StructDecl, pkg_napi_target: COutputBuffer
    ):
        struct_cpp_info = StructDeclCppProjInfo.get(self.am, struct)
        pkg_napi_target.write(
            f"inline {struct_cpp_info.as_field} get_{struct.name}(napi_env env, napi_value js_obj) {{\n"
        )
        for field in struct.fields:
            pkg_napi_target.write(
                f"    napi_value {field.name}_v = nullptr;\n"
                f'    napi_get_named_property(env, js_obj, "{field.name}", &{field.name}_v);\n'
            )
            self.gen_func_get_value_from_js(
                field.ty_ref.resolved_ty,
                pkg_napi_target,
                f"{field.name}_v",
                field.name,
                4,
            )

        pkg_napi_target.write(f"    {struct_cpp_info.as_field} c_obj = {{\n")
        for field in struct.fields:
            pkg_napi_target.write(f"        .{field.name} = std::move({field.name}),\n")
        pkg_napi_target.write(f"    }};\n" f"    return c_obj;\n" f"}}\n")

        pkg_napi_target.write(
            f"inline napi_value create_{struct.name}(napi_env env, {struct_cpp_info.as_param} c_obj) {{\n"
            f"    napi_value js_obj = nullptr;\n"
            f"    napi_create_object(env, &js_obj);\n"
        )
        for field in struct.fields:
            self.gen_func_create_value_as_js(
                field.ty_ref.resolved_ty,
                pkg_napi_target,
                f"c_obj.{field.name}",
                field.name,
                4,
            )
            pkg_napi_target.write(
                f'    napi_set_named_property(env, js_obj, "{field.name}", {field.name});\n'
            )
        pkg_napi_target.write(f"    return js_obj;\n" f"}}\n")

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
        self.gen_func_content(func, pkg_napi_target, func_name, 4)
        pkg_napi_target.write(f"}}\n")

    def gen_func_content(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
        pkg_napi_target: COutputBuffer,
        func_name: str,
        space_num: int,
    ):
        self.gen_func_get_cb_info(len(func.params), pkg_napi_target)
        args = []
        for i, param in enumerate(func.params):
            value_ty = param.ty_ref.resolved_ty
            self.gen_func_get_value_from_js(
                value_ty, pkg_napi_target, f"args[{i}]", f"value{i}", 4
            )
            args.append(f"value{i}")
        args_str = ", ".join(args)

        if return_ty_ref := func.return_ty_ref:
            value_ty = return_ty_ref.resolved_ty
            cpp_return_info = TypeCppProjInfo.get(self.am, value_ty)
            pkg_napi_target.write(
                f"    {cpp_return_info.as_field} value = {func_name}({args_str});\n"
            )
            self.gen_func_create_value_as_js(
                value_ty, pkg_napi_target, "value", "result", space_num
            )
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

    def gen_func_get_value_from_js(
        self,
        value_ty: Type | None,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        type_info = TypeNapiInfo.get(self.am, value_ty)
        type_info.get_value_from_js(pkg_napi_target, value, result, space_num)

    def gen_func_create_value_as_js(
        self,
        value_ty: Type | None,
        pkg_napi_target: COutputBuffer,
        value: str,
        result: str,
        space_num: int,
    ):
        type_info = TypeNapiInfo.get(self.am, value_ty)
        type_info.create_value_as_js(pkg_napi_target, value, result, space_num)
