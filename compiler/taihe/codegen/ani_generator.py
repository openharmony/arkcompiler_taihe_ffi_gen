from abc import ABCMeta

from typing_extensions import override

from taihe.codegen.abi_generator import (
    IfaceABIInfo,
)
from taihe.codegen.cpp_generator import (
    EnumCppInfo,
    GlobFuncCppInfo,
    IfaceCppInfo,
    IfaceMethodCppInfo,
    PackageCppInfo,
    TypeCppInfo,
)
from taihe.codegen.mangle import DeclKind, encode
from taihe.semantics.declarations import (
    EnumDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
    StructDecl,
)
from taihe.semantics.types import (
    BOOL,
    F32,
    F64,
    I8,
    I16,
    I32,
    I64,
    U8,
    U16,
    U32,
    U64,
    ArrayType,
    # CallbackType,
    EnumType,
    IfaceType,
    # MapType,
    OpaqueType,
    OptionalType,
    ScalarType,
    # SetType,
    StringType,
    StructType,
    Type,
    # VectorType,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import COutputBuffer, OutputBuffer, OutputManager


class ANIType:
    hint: str
    base: "ANIBaseType"

    def __init__(self, hint: str, base: "ANIBaseType"):
        self.hint = hint
        self.base = base

    def __repr__(self) -> str:
        return f"ani_{self.hint}"

    @property
    def suffix(self) -> str:
        return self.base.hint[0].upper() + self.base.hint[1:]

    @property
    def array(self) -> "ANIArrayType":
        assert self.base.inner_array
        return self.base.inner_array


class ANIArrayType(ANIType):
    pass


class ANIBaseType(ANIType):
    inner_array: "ANIArrayType | None"

    def __init__(self, hint: str):
        super().__init__(hint, self)
        self.inner_array = None


ANI_REF = ANIBaseType(hint="ref")
ANI_ARRAY_REF = ANIArrayType(hint="array_ref", base=ANI_REF)
ANI_REF.inner_array = ANI_ARRAY_REF

ANI_BOOLEAN = ANIBaseType(hint="boolean")
ANI_ARRAY_BOOLEAN = ANIArrayType(hint="array_boolean", base=ANI_REF)
ANI_BOOLEAN.inner_array = ANI_ARRAY_BOOLEAN

ANI_FLOAT = ANIBaseType(hint="float")
ANI_ARRAY_FLOAT = ANIArrayType(hint="array_float", base=ANI_REF)
ANI_FLOAT.inner_array = ANI_ARRAY_FLOAT

ANI_DOUBLE = ANIBaseType(hint="double")
ANI_ARRAY_DOUBLE = ANIArrayType(hint="array_double", base=ANI_REF)
ANI_DOUBLE.inner_array = ANI_ARRAY_DOUBLE

ANI_BYTE = ANIBaseType(hint="byte")
ANI_ARRAY_BYTE = ANIArrayType(hint="array_byte", base=ANI_REF)
ANI_BYTE.inner_array = ANI_ARRAY_BYTE

ANI_SHORT = ANIBaseType(hint="short")
ANI_ARRAY_SHORT = ANIArrayType(hint="array_short", base=ANI_REF)
ANI_SHORT.inner_array = ANI_ARRAY_SHORT

ANI_INT = ANIBaseType(hint="int")
ANI_ARRAY_INT = ANIArrayType(hint="array_int", base=ANI_REF)
ANI_INT.inner_array = ANI_ARRAY_INT

ANI_LONG = ANIBaseType(hint="long")
ANI_ARRAY_LONG = ANIArrayType(hint="array_long", base=ANI_REF)
ANI_LONG.inner_array = ANI_ARRAY_LONG

ANI_OBJECT = ANIType(hint="object", base=ANI_REF)
ANI_STRING = ANIType(hint="string", base=ANI_REF)


class PackageANIInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        self.header = f"{p.name}.ani.hpp"
        self.source = f"{p.name}.ani.cpp"
        self.namespace = "::".join(p.segments)
        self.sts = f"{p.name}.ets"
        self.lib_name = (
            ani_lib_item.value if (ani_lib_item := p.attrs.get("ani_lib")) else p.name
        )
        self.impl_desc = f"L{self.lib_name}/ETSGLOBAL;"


class GlobFuncANIInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        p = f.node_parent
        assert p
        segments = [*p.segments, f.name]
        self.sts_name = f.name
        self.mangled_name = encode(segments, DeclKind.ANI_FUNC)


class IfaceMethodANIInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, f: IfaceMethodDecl) -> None:
        d = f.node_parent
        assert d
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name, f.name]
        self.sts_name = f.name
        self.mangled_name = encode(segments, DeclKind.ANI_FUNC)


class StructANIInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.node_parent
        assert p
        self.sts_type = d.name
        self.sts_impl = d.name
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.type_desc = f"L{pkg_ani_info.lib_name}/{self.sts_type};"
        self.impl_desc = f"L{pkg_ani_info.lib_name}/{self.sts_impl};"


class EnumANIInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.node_parent
        assert p
        self.sts_type = d.name
        self.sts_impl = d.name
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.type_desc = f"L{pkg_ani_info.lib_name}/{self.sts_type};"
        self.impl_desc = f"L{pkg_ani_info.lib_name}/{self.sts_impl};"


class IfaceANIInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.node_parent
        assert p
        self.sts_type = d.name
        self.sts_impl = f"{d.name}_inner"
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.type_desc = f"L{pkg_ani_info.lib_name}/{self.sts_type};"
        self.impl_desc = f"L{pkg_ani_info.lib_name}/{self.sts_impl};"


class AbstractTypeANIInfo(metaclass=ABCMeta):
    ani_type: ANIType
    sts_type: str
    type_desc: str

    def __init__(self, am: AnalysisManager, t: Type):
        self.cpp_info = TypeCppInfo.get(am, t)

    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    def into_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    def from_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        ani_array_value: str,
        cpp_array_buffer: str,
    ):
        if self.ani_type.base == ANI_REF:
            ani_value = "_ani_val"
            cpp_result = "_cpp_res"
            i = "_i"
            target.write(
                f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
                f"{' ' * offset}    {self.ani_type} {ani_value};\n"
                f"{' ' * offset}    {env}->Array_Get_Ref({ani_array_value}, {i}, reinterpret_cast<ani_ref*>(&{ani_value}));\n"
            )
            self.from_ani(target, offset + 4, env, ani_value, cpp_result)
            target.write(
                f"{' ' * offset}    new (&{cpp_array_buffer}[{i}]) {self.cpp_info.as_owner}(std::move({cpp_result}));\n"
                f"{' ' * offset}}}\n"
            )
        else:
            target.write(
                f"{' ' * offset}{env}->Array_GetRegion_{self.ani_type.suffix}({ani_array_value}, 0, {size}, reinterpret_cast<{self.ani_type}*>({cpp_array_buffer}));\n"
            )

    def into_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        cpp_array_value: str,
        ani_array_result: str,
    ):
        if self.ani_type.base == ANI_REF:
            ani_class = f"{ani_array_result}_cls"
            ani_result = "_ani_res"
            i = "_i"
            target.write(
                f"{' ' * offset}ani_array_ref {ani_array_result};\n"
                f"{' ' * offset}ani_class {ani_class};\n"
                f"{' ' * offset}{env}->FindClass(\"{self.type_desc}\", &{ani_class});\n"
                f"{' ' * offset}ani_ref undefined;\n"
                f"{' ' * offset}{env}->GetUndefined(&undefined);\n"
                f"{' ' * offset}{env}->Array_New_Ref({ani_class}, {size}, undefined, &{ani_array_result});\n"
                f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
            )
            self.into_ani(
                target, offset + 4, env, f"{cpp_array_value}[{i}]", ani_result
            )
            target.write(
                f"{' ' * offset}    {env}->Array_Set_Ref({ani_array_result}, {i}, {ani_result});\n"
                f"{' ' * offset}}}\n"
            )
        else:
            target.write(
                f"{' ' * offset}{self.ani_type.array} {ani_array_result};\n"
                f"{' ' * offset}{env}->Array_New_{self.ani_type.suffix}({size}, &{ani_array_result});\n"
                f"{' ' * offset}{env}->Array_SetRegion_{self.ani_type.suffix}({ani_array_result}, 0, {size}, reinterpret_cast<{self.ani_type} const*>({cpp_array_value}));\n"
            )

    def into_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        if self.ani_type.base == ANI_REF:
            self.into_ani(target, offset, env, cpp_value, ani_result)
        else:
            ani_class = f"{ani_result}_cls"
            ani_ctor = f"{ani_result}_ctor"
            ani_value = f"{ani_result}_ani"
            target.write(
                f"{' ' * offset}static ani_class {ani_class} = [=] {{\n"
                f"{' ' * offset}    ani_class {ani_class};\n"
                f"{' ' * offset}    {env}->FindClass(\"Lstd/core/{self.ani_type.suffix};\", &{ani_class});\n"
                f"{' ' * offset}    {env}->GlobalReference_Create({ani_class}, reinterpret_cast<ani_ref*>(&{ani_class}));\n"
                f"{' ' * offset}    return {ani_class};\n"
                f"{' ' * offset}}}();\n"
                f"{' ' * offset}static ani_method {ani_ctor} = [=] {{\n"
                f"{' ' * offset}    ani_method {ani_ctor};\n"
                f"{' ' * offset}    {env}->Class_FindMethod({ani_class}, \"<ctor>\", nullptr, &{ani_ctor});\n"
                f"{' ' * offset}    return {ani_ctor};\n"
                f"{' ' * offset}}}();\n"
                f"{' ' * offset}ani_object {ani_result};\n"
            )
            self.into_ani(target, offset, env, cpp_value, ani_value)
            target.write(
                f"{' ' * offset}{env}->Object_New({ani_class}, {ani_ctor}, &{ani_result}, {ani_value});\n"
            )

    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        if self.ani_type.base == ANI_REF:
            self.from_ani(
                target,
                offset,
                env,
                f"static_cast<{self.ani_type}>({ani_value})",
                cpp_result,
            )
        else:
            ani_class = f"{cpp_result}_cls"
            ani_getter = f"{cpp_result}_get"
            ani_result = f"{cpp_result}_ani"
            target.write(
                f"{' ' * offset}static ani_class {ani_class} = [=] {{\n"
                f"{' ' * offset}    ani_class {ani_class};\n"
                f"{' ' * offset}    {env}->FindClass(\"Lstd/core/{self.ani_type.suffix};\", &{ani_class});\n"
                f"{' ' * offset}    {env}->GlobalReference_Create({ani_class}, reinterpret_cast<ani_ref*>(&{ani_class}));\n"
                f"{' ' * offset}    return {ani_class};\n"
                f"{' ' * offset}}}();\n"
                f"{' ' * offset}static ani_method {ani_getter} = [=] {{\n"
                f"{' ' * offset}    ani_method {ani_getter};\n"
                f"{' ' * offset}    {env}->Class_FindMethod({ani_class}, \"unboxed\", nullptr, &{ani_getter});\n"
                f"{' ' * offset}    return {ani_getter};\n"
                f"{' ' * offset}}}();\n"
                f"{' ' * offset}{self.ani_type} {ani_result};\n"
                f"{' ' * offset}{env}->Object_CallMethod_{self.ani_type.suffix}((ani_object){ani_value}, {ani_getter}, &{ani_result});\n"
            )
            self.from_ani(target, offset, env, ani_result, cpp_result)


class StructTypeANIInfo(AbstractAnalysis[StructType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: StructType):
        AbstractTypeANIInfo.__init__(self, am, t)
        self.t = t
        self.am = am
        struct_ani_info = StructANIInfo.get(am, t.ty_decl)
        self.ani_type = ANI_OBJECT
        self.sts_type = struct_ani_info.sts_type
        self.type_desc = struct_ani_info.type_desc
        self.impl_desc = struct_ani_info.impl_desc

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        cpp_field_results = []
        for field in self.t.ty_decl.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            ani_field_value = f"{cpp_result}_{field.name}_ani"
            cpp_field_result = f"{cpp_result}_{field.name}_cpp"
            target.write(
                f"{' ' * offset}{type_ani_info.ani_type} {ani_field_value};\n"
                f"{' ' * offset}{env}->Object_GetPropertyByName_{type_ani_info.ani_type.suffix}({ani_value}, \"{field.name}\", reinterpret_cast<{type_ani_info.ani_type.base}*>(&{ani_field_value}));\n"
            )
            type_ani_info.from_ani(
                target, offset, env, ani_field_value, cpp_field_result
            )
            cpp_field_results.append(cpp_field_result)
        cpp_moved_fields_str = ", ".join(
            f"std::move({cpp_field_result})" for cpp_field_result in cpp_field_results
        )
        target.write(
            f"{' ' * offset}{self.cpp_info.as_owner} {cpp_result} = {self.cpp_info.as_owner}{{{cpp_moved_fields_str}}};\n"
        )

    @override
    def into_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        ani_field_results = []
        for field in self.t.ty_decl.fields:
            ani_field_result = f"{ani_result}_{field.name}_ani"
            ani_field_results.append(ani_field_result)
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            type_ani_info.into_ani(
                target, offset, env, f"{cpp_value}.{field.name}", ani_field_result
            )
        ani_field_results_trailing = "".join(
            f", {ani_field_result}" for ani_field_result in ani_field_results
        )
        ani_result_cls = f"{ani_result}_cls"
        ani_result_ctor = f"{ani_result}_ctor"
        target.write(
            f"{' ' * offset}ani_class {ani_result_cls};\n"
            f"{' ' * offset}{env}->FindClass(\"{self.impl_desc}\", &{ani_result_cls});\n"
            f"{' ' * offset}ani_method {ani_result_ctor};\n"
            f"{' ' * offset}{env}->Class_FindMethod({ani_result_cls}, \"<ctor>\", nullptr, &{ani_result_ctor});\n"
            f"{' ' * offset}ani_object {ani_result};\n"
            f"{' ' * offset}{env}->Object_New({ani_result_cls}, {ani_result_ctor}, &{ani_result}, {ani_field_results_trailing});\n"
        )


class EnumTypeANIInfo(AbstractAnalysis[EnumType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        AbstractTypeANIInfo.__init__(self, am, t)
        self.t = t
        self.am = am
        enum_ani_info = EnumANIInfo.get(am, t.ty_decl)
        self.ani_type = ANI_OBJECT
        self.sts_type = enum_ani_info.sts_type
        self.type_desc = enum_ani_info.type_desc
        self.impl_desc = enum_ani_info.impl_desc

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        ani_value_tag = f"{cpp_result}_ani_tag"
        ani_value_val = f"{cpp_result}_ani_value"
        target.write(
            f"{' ' * offset}ani_int {ani_value_tag};\n"
            f"{' ' * offset}{env}->Object_GetPropertyByName_Int({ani_value}, \"tag\", &{ani_value_tag});\n"
            f"{' ' * offset}ani_ref {ani_value_val};\n"
            f"{' ' * offset}{env}->Object_GetPropertyByName_Ref({ani_value}, \"value\", &{ani_value_val});\n"
        )
        cpp_value_tag = f"{cpp_result}_tag"
        enum_cpp_info = EnumCppInfo.get(self.am, self.t.ty_decl)
        target.write(
            f"{' ' * offset}{self.cpp_info.as_owner} {cpp_result} = [=] {{\n"
            f"{' ' * offset}    {enum_cpp_info.full_name}::tag_t {cpp_value_tag} = ({enum_cpp_info.full_name}::tag_t){ani_value_tag};\n"
            f"{' ' * offset}    switch ({cpp_value_tag}) {{\n"
        )
        for item in self.t.ty_decl.items:
            target.write(
                f"{' ' * offset}    case {enum_cpp_info.full_name}::tag_t::{item.name}: {{\n"
            )
            if item.ty_ref is None:
                target.write(
                    f"{' ' * offset}        return {enum_cpp_info.full_name}::make_{item.name}();\n"
                )
            else:
                cpp_result_spec = f"{cpp_result}_{item.name}"
                type_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
                type_ani_info.from_ani_boxed(
                    target,
                    offset + 8,
                    env,
                    ani_value_val,
                    cpp_result_spec,
                )
                target.write(
                    f"{' ' * offset}        return {enum_cpp_info.full_name}::make_{item.name}(std::move({cpp_result_spec}));\n"
                )
            target.write(f"{' ' * offset}    }}\n")
        target.write(f"{' ' * offset}    }}\n" f"{' ' * offset}}}();\n")

    @override
    def into_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        ani_result_tag = f"{ani_result}_tag"
        ani_result_val = f"{ani_result}_value"
        enum_cpp_info = EnumCppInfo.get(self.am, self.t.ty_decl)
        target.write(
            f"{' ' * offset}ani_int {ani_result_tag} = (int){cpp_value}.get_tag();\n"
            f"{' ' * offset}ani_ref {ani_result_val};\n"
            f"{' ' * offset}switch ({cpp_value}.get_tag()) {{\n"
        )
        for item in self.t.ty_decl.items:
            target.write(
                f"{' ' * offset}    case {enum_cpp_info.full_name}::tag_t::{item.name}: {{\n"
            )
            if item.ty_ref is None:
                target.write(
                    f"{' ' * offset}        {env}->GetUndefined(&{ani_result_val});\n"
                )
            else:
                ani_result_spec = f"{ani_result_val}_{item.name}"
                type_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
                type_ani_info.into_ani_boxed(
                    target,
                    offset + 8,
                    env,
                    f"{cpp_value}.get_{item.name}_ref()",
                    ani_result_spec,
                )
                target.write(
                    f"{' ' * offset}        {ani_result_val} = {ani_result_spec};\n"
                )
            target.write(f"{' ' * offset}        break;\n" f"{' ' * offset}    }}\n")
        target.write(f"{' ' * offset}    }}\n")
        ani_result_cls = f"{ani_result}_cls"
        ani_result_ctor = f"{ani_result}_ctor"
        target.write(
            f"{' ' * offset}ani_class {ani_result_cls};\n"
            f"{' ' * offset}{env}->FindClass(\"{self.impl_desc}\", &{ani_result_cls});\n"
            f"{' ' * offset}ani_method {ani_result_ctor};\n"
            f"{' ' * offset}{env}->Class_FindMethod({ani_result_cls}, \"<ctor>\", nullptr, &{ani_result_ctor});\n"
            f"{' ' * offset}ani_object {ani_result};\n"
            f"{' ' * offset}{env}->Object_New({ani_result_cls}, {ani_result_ctor}, &{ani_result}, {ani_result_tag}, {ani_result_val});\n"
        )


class IfaceTypeANIInfo(AbstractAnalysis[IfaceType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        AbstractTypeANIInfo.__init__(self, am, t)
        self.t = t
        self.am = am
        iface_ani_info = IfaceANIInfo.get(am, t.ty_decl)
        self.ani_type = ANI_OBJECT
        self.sts_type = iface_ani_info.sts_type
        self.type_desc = iface_ani_info.type_desc
        self.impl_desc = iface_ani_info.impl_desc

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        cpp_iface_name = f"{cpp_result}_impl"
        target.write(
            f"{' ' * offset}struct {cpp_iface_name} {{\n"
            f"{' ' * offset}    ani_env* env;\n"
            f"{' ' * offset}    ani_object ref;\n"
            f"{' ' * offset}    {cpp_iface_name}(ani_env* env, ani_object obj) {{\n"
            f"{' ' * offset}        env->GlobalReference_Create(obj, &reinterpret_cast<ani_ref*>(&ref));\n"
            f"{' ' * offset}    }}\n"
            f"{' ' * offset}    ~{cpp_iface_name}() {{\n"
            f"{' ' * offset}        env->GlobalReference_Delete(ref);\n"
            f"{' ' * offset}    }}\n"
        )
        iface_abi_info = IfaceABIInfo.get(self.am, self.t.ty_decl)
        for ancestor in iface_abi_info.ancestor_dict:
            for method in ancestor.methods:
                method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
                method_ani_info = IfaceMethodANIInfo.get(self.am, method)
                cpp_param_pairs = []
                cpp_param_names = []
                ani_arg_names = []
                for param in method.params:
                    cpp_param_name = f"{param.name}_cpp"
                    ani_arg_name = f"{param.name}_ani"
                    type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
                    cpp_param_pairs.append(f"{type_cpp_info.as_param} {cpp_param_name}")
                    cpp_param_names.append(cpp_param_name)
                    ani_arg_names.append(ani_arg_name)
                params_cpp_str = ", ".join(cpp_param_pairs)
                if method.return_ty_ref:
                    type_cpp_info = TypeCppInfo.get(
                        self.am, method.return_ty_ref.resolved_ty
                    )
                    cpp_return_ty_name = type_cpp_info.as_owner
                else:
                    cpp_return_ty_name = "void"
                target.write(
                    f"{' ' * offset}    {cpp_return_ty_name} {method_cpp_info.impl_name}({params_cpp_str}) {{\n"
                )
                args_ani = []
                for param, cpp_param_name, ani_arg_name in zip(
                    method.params, cpp_param_names, ani_arg_names, strict=False
                ):
                    type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
                    type_ani_info.into_ani(
                        target, offset + 8, env, cpp_param_name, ani_arg_name
                    )
                args_ani_trailing = "".join(f", {arg_ani}" for arg_ani in args_ani)
                result_ani_name = "result_ani"
                result_cpp_name = "result_cpp"
                if method.return_ty_ref:
                    type_ani_info = TypeANIInfo.get(
                        self.am, method.return_ty_ref.resolved_ty
                    )
                    target.write(
                        f"{' ' * offset}        {type_ani_info.ani_type} {result_ani_name};\n"
                        f"{' ' * offset}        this->env.Object_CallMethod_{type_ani_info.ani_type.suffix}(this->ref, \"{method_ani_info.sts_name}\", nullptr, &{result_ani_name}{args_ani_trailing});\n"
                    )
                    type_ani_info.from_ani(
                        target, offset + 8, env, result_ani_name, result_cpp_name
                    )
                    target.write(f"{' ' * offset}        return {result_cpp_name};\n")
                else:
                    target.write(
                        f"{' ' * offset}        this->env.Object_CallMethod_Void(this->ref, \"{method_ani_info.sts_name}\", nullptr{args_ani_trailing});\n"
                    )
                target.write(f"{' ' * offset}    }}\n")
        target.write(f"{' ' * offset}}};\n")
        target.write(
            f"{' ' * offset}{self.cpp_info.as_owner} {cpp_result} = taihe::core::make_holder<{cpp_iface_name}, {self.cpp_info.as_owner}>({env}, {ani_value});\n"
        )

    @override
    def into_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        cpp_value_copy = f"{ani_result}_cpp"
        ani_result_cls = f"{ani_result}_cls"
        ani_result_vtbl_ptr = f"{ani_result}_vtbl_ptr"
        ani_result_data_ptr = f"{ani_result}_data_ptr"
        ani_result_ctor = f"{ani_result}_ctor"
        target.write(
            f"{' ' * offset}{self.cpp_info.as_owner} {cpp_value_copy} = {cpp_value};\n"
            f"{' ' * offset}ani_long {ani_result_vtbl_ptr} = reinterpret_cast<ani_long>({cpp_value_copy}.m_handle.vtbl_ptr);\n"
            f"{' ' * offset}ani_long {ani_result_vtbl_ptr} = reinterpret_cast<ani_long>({cpp_value_copy}.m_handle.data_ptr);\n"
            f"{' ' * offset}{cpp_value_copy}.m_handle.data_ptr = nullptr;\n"
            f"{' ' * offset}ani_class {ani_result_cls};\n"
            f"{' ' * offset}{env}->FindClass(\"{self.impl_desc}\", &{ani_result_cls});\n"
            f"{' ' * offset}ani_method {ani_result_ctor};\n"
            f"{' ' * offset}{env}->Class_FindMethod({ani_result_cls}, \"<ctor>\", nullptr, &{ani_result_ctor});\n"
            f"{' ' * offset}ani_object {ani_result};\n"
            f"{' ' * offset}{env}->Object_New({ani_result_cls}, {ani_result_ctor}, &{ani_result}, {ani_result_vtbl_ptr}, {ani_result_data_ptr});\n"
        )


class ScalarTypeANIInfo(AbstractAnalysis[ScalarType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        AbstractTypeANIInfo.__init__(self, am, t)
        sts_type, ani_type, type_desc = {
            BOOL: ("boolean", ANI_BOOLEAN, "Z"),
            F32: ("float", ANI_FLOAT, "F"),
            F64: ("double", ANI_DOUBLE, "D"),
            I8: ("byte", ANI_BYTE, "B"),
            I16: ("short", ANI_SHORT, "S"),
            I32: ("int", ANI_INT, "I"),
            I64: ("long", ANI_LONG, "J"),
            U8: ("byte", ANI_BYTE, "B"),
            U16: ("short", ANI_SHORT, "S"),
            U32: ("int", ANI_INT, "I"),
            U64: ("long", ANI_LONG, "J"),
        }[t]
        self.ani_type = ani_type
        self.sts_type = sts_type
        self.type_desc = type_desc

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        target.write(
            f"{' ' * offset}{self.cpp_info.as_owner} {cpp_result} = ({self.cpp_info.as_owner}){ani_value};\n"
        )

    @override
    def into_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        target.write(
            f"{' ' * offset}{self.ani_type} {ani_result} = ({self.cpp_info.as_owner}){cpp_value};\n"
        )


class OpaqueTypeANIInfo(AbstractAnalysis[OpaqueType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: OpaqueType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)
        self.ani_type = ANI_OBJECT
        self.sts_type = "Object"
        self.type_desc = "Lstd/core/Object;"

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        target.write(
            f"{' ' * offset}{self.cpp_info.as_owner} {cpp_result} = ({self.cpp_info.as_owner}){ani_value};\n"
        )

    @override
    def into_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        target.write(
            f"{' ' * offset}{self.ani_type} {ani_result} = ({self.ani_type}){cpp_value};\n"
        )


class StringTypeANIInfo(AbstractAnalysis[StringType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: StringType):
        AbstractTypeANIInfo.__init__(self, am, t)
        self.ani_type = ANI_STRING
        self.sts_type = "string"
        self.type_desc = "Lstd/core/String;"

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        length = f"{cpp_result}_len"
        tstr = f"{cpp_result}_tstr"
        buffer = f"{cpp_result}_buf"
        target.write(
            f"{' ' * offset}ani_size {length};\n"
            f"{' ' * offset}{env}->String_GetUTF8Size({ani_value}, &{length});\n"
            f"{' ' * offset}TString {tstr};\n"
            f"{' ' * offset}char* {buffer} = tstr_initialize(&{tstr}, {length} + 1);\n"
            f"{' ' * offset}{env}->String_GetUTF8({ani_value}, {buffer}, {length} + 1, &{length});\n"
            f"{' ' * offset}{buffer}[{length}] = '\\0';\n"
            f"{' ' * offset}{tstr}.length = {length};\n"
            f"{' ' * offset}taihe::core::string {cpp_result} = taihe::core::string({tstr});\n"
        )

    @override
    def into_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        target.write(
            f"{' ' * offset}ani_string {ani_result};\n"
            f"{' ' * offset}{env}->String_NewUTF8({cpp_value}.c_str(), {cpp_value}.size(), &{ani_result});\n"
        )


class ArrayTypeANIInfo(AbstractAnalysis[ArrayType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)
        item_ty_ani_info = TypeANIInfo.get(am, t.item_ty)
        self.ani_type = item_ty_ani_info.ani_type.array
        self.sts_type = f"({item_ty_ani_info.sts_type}[])"
        self.type_desc = f"[{item_ty_ani_info.type_desc}"
        self.am = am
        self.t = t

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        cpp_info = TypeCppInfo.get(self.am, self.t)
        size = f"{cpp_result}_size"
        buffer = f"{cpp_result}_buffer"
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        target.write(
            f"{' ' * offset}size_t {size};\n"
            f"{' ' * offset}{env}->Array_GetLength({ani_value}, &{size});\n"
            f"{' ' * offset}{item_ty_cpp_info.as_owner}* {buffer} = ({item_ty_cpp_info.as_owner}*)malloc({size} * sizeof({item_ty_cpp_info.as_owner}));\n"
        )
        item_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        item_ty_ani_info.from_ani_array(target, offset, env, size, ani_value, buffer)
        target.write(
            f"{' ' * offset}{cpp_info.as_owner} {cpp_result}({buffer}, {size});\n"
        )

    @override
    def into_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        item_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        size = f"{ani_result}_size"
        target.write(f"{' ' * offset}size_t {size} = {cpp_value}.size();\n")
        item_ty_ani_info.into_ani_array(
            target, offset, env, size, f"{cpp_value}.data()", ani_result
        )


class OptionalTypeANIInfo(AbstractAnalysis[OptionalType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: OptionalType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)
        item_ty_ani_info = TypeANIInfo.get(am, t.item_ty)
        self.ani_type = ANI_REF
        self.sts_type = f"({item_ty_ani_info.sts_type} | undefined)"
        self.type_desc = item_ty_ani_info.type_desc
        self.am = am
        self.t = t

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        ani_is_undefined = f"{cpp_result}_flag"
        cpp_pointer = f"{cpp_result}_ptr"
        cpp_spec = f"{cpp_result}_spec"
        cpp_info = TypeCppInfo.get(self.am, self.t)
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        target.write(
            f"{' ' * offset}ani_boolean {ani_is_undefined};\n"
            f"{' ' * offset}{item_ty_cpp_info.as_owner}* {cpp_pointer} = nullptr;\n"
            f"{' ' * offset}{env}->Reference_IsUndefined({ani_value}, &{ani_is_undefined});\n"
            f"{' ' * offset}if (!{ani_is_undefined}) {{\n"
        )
        item_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        item_ty_ani_info.from_ani_boxed(target, offset + 4, env, ani_value, cpp_spec)
        target.write(
            f"{' ' * offset}    {cpp_pointer} = new {item_ty_cpp_info.as_owner}(std::move({cpp_spec}));\n"
            f"{' ' * offset}}};\n"
            f"{' ' * offset}{cpp_info.as_owner} {cpp_result}({cpp_pointer});\n"
        )

    @override
    def into_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        ani_result_spec = f"{ani_result}_spec"
        target.write(
            f"{' ' * offset}ani_ref {ani_result};\n"
            f"{' ' * offset}if (!{cpp_value}) {{\n"
            f"{' ' * offset}    {env}->GetUndefined(&{ani_result});\n"
            f"{' ' * offset}}} else {{\n"
        )
        item_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        item_ty_ani_info.into_ani_boxed(
            target, offset + 4, env, f"(*{cpp_value})", ani_result_spec
        )
        target.write(
            f"{' ' * offset}    {ani_result} = {ani_result_spec};\n"
            f"{' ' * offset}}}\n"
        )


# class VectorTypeANIInfo(AbstractAnalysis[VectorType], AbstractTypeANIInfo):
#     def __init__(self, am: AnalysisManager, t: VectorType) -> None:
#         pass


# class MapTypeANIInfo(AbstractAnalysis[MapType], AbstractTypeANIInfo):
#     def __init__(self, am: AnalysisManager, t: MapType) -> None:
#         pass


# class SetTypeANIInfo(AbstractAnalysis[SetType], AbstractTypeANIInfo):
#     def __init__(self, am: AnalysisManager, t: SetType) -> None:
#         pass


# class CallbackTypeANIInfo(AbstractAnalysis[CallbackType], AbstractTypeANIInfo):
#     def __init__(self, am: AnalysisManager, t: CallbackType) -> None:
#         pass


class TypeANIInfo(TypeVisitor[AbstractTypeANIInfo]):
    def __init__(self, am: AnalysisManager):
        self.am = am

    @staticmethod
    def get(am: AnalysisManager, t: Type | None) -> AbstractTypeANIInfo:
        assert t is not None
        return TypeANIInfo(am).handle_type(t)

    @override
    def visit_enum_type(self, t: EnumType) -> AbstractTypeANIInfo:
        return EnumTypeANIInfo.get(self.am, t)

    @override
    def visit_struct_type(self, t: StructType) -> AbstractTypeANIInfo:
        return StructTypeANIInfo.get(self.am, t)

    @override
    def visit_iface_type(self, t: IfaceType) -> AbstractTypeANIInfo:
        return IfaceTypeANIInfo.get(self.am, t)

    @override
    def visit_scalar_type(self, t: ScalarType) -> AbstractTypeANIInfo:
        return ScalarTypeANIInfo.get(self.am, t)

    @override
    def visit_string_type(self, t: StringType) -> AbstractTypeANIInfo:
        return StringTypeANIInfo.get(self.am, t)

    @override
    def visit_array_type(self, t: ArrayType) -> AbstractTypeANIInfo:
        return ArrayTypeANIInfo.get(self.am, t)

    @override
    def visit_optional_type(self, t: OptionalType) -> AbstractTypeANIInfo:
        return OptionalTypeANIInfo.get(self.am, t)

    # @override
    # def visit_vector_type(self, t: VectorType) -> AbstractTypeANIInfo:
    #     return VectorTypeANIInfo.get(self.am, t)

    # @override
    # def visit_map_type(self, t: MapType) -> AbstractTypeANIInfo:
    #     return MapTypeANIInfo.get(self.am, t)

    # @override
    # def visit_set_type(self, t: SetType) -> AbstractTypeANIInfo:
    #     return SetTypeANIInfo.get(self.am, t)

    # @override
    # def visit_callback_type(self, t: CallbackType) -> AbstractTypeANIInfo:
    #     return CallbackTypeANIInfo.get(self.am, t)


class STSCodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_ani_info = PackageANIInfo.get(self.am, pkg)
        pkg_sts_target = OutputBuffer.create(self.tm, pkg_ani_info.sts)

        pkg_sts_target.write(f'loadLibrary("{pkg_ani_info.lib_name}");\n')

        # for struct in pkg.structs:
        #     self.gen_struct_inner(struct, pkg_sts_target)
        # for enum in pkg.enums:
        #     self.gen_enum_inner(enum, pkg_sts_target)
        for iface in pkg.interfaces:
            self.gen_iface_inner(iface, pkg_sts_target)

        # for struct in pkg.structs:
        #     self.gen_struct_interface(struct, pkg_sts_target)
        # for enum in pkg.enums:
        #     self.gen_enum_interface(enum, pkg_sts_target)
        for iface in pkg.interfaces:
            self.gen_iface_interface(iface, pkg_sts_target)

        for struct in pkg.structs:
            self.gen_struct(struct, pkg_sts_target)
        for enum in pkg.enums:
            self.gen_enum(enum, pkg_sts_target)

        for func in pkg.functions:
            self.gen_func(func, pkg_sts_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_sts_target: OutputBuffer,
    ):
        func_ani_info = GlobFuncANIInfo.get(self.am, func)
        params_sts = []
        for param in func.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            params_sts.append(f"{param.name}: {type_ani_info.sts_type}")
        params_sts_str = ", ".join(params_sts)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            sts_return_ty_name = type_ani_info.sts_type
        else:
            sts_return_ty_name = "void"
        pkg_sts_target.write(
            f"export native function {func_ani_info.sts_name}({params_sts_str}): {sts_return_ty_name};\n"
        )

    # def gen_struct_interface(
    #     self,
    #     struct: StructDecl,
    #     pkg_sts_target: OutputBuffer,
    # ):
    #     struct_ani_info = StructANIInfo.get(self.am, struct)
    #     pkg_sts_target.write(f"export interface {struct_ani_info.sts_type} {{\n")
    #     for field in struct.fields:
    #         ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
    #         pkg_sts_target.write(f"    {field.name}: {ty_ani_info.sts_type};\n")
    #     pkg_sts_target.write("}\n")

    # def gen_struct_inner(
    #     self,
    #     struct: StructDecl,
    #     pkg_sts_target: OutputBuffer,
    # ):
    #     struct_ani_info = StructANIInfo.get(self.am, struct)
    #     pkg_sts_target.write(
    #         f"class {struct_ani_info.sts_impl} implements {struct_ani_info.sts_type} {{\n"
    #     )
    #     for field in struct.fields:
    #         ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
    #         pkg_sts_target.write(f"    {field.name}: {ty_ani_info.sts_type};\n")
    #     pkg_sts_target.write("    constructor(\n")
    #     for field in struct.fields:
    #         ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
    #         pkg_sts_target.write(f"        {field.name}: {ty_ani_info.sts_type},\n")
    #     pkg_sts_target.write("    ) {\n")
    #     for field in struct.fields:
    #         pkg_sts_target.write(f"        this.{field.name} = {field.name};\n")
    #     pkg_sts_target.write("    }\n" "}\n")

    def gen_struct(
        self,
        struct: StructDecl,
        pkg_sts_target: OutputBuffer,
    ):
        struct_ani_info = StructANIInfo.get(self.am, struct)
        pkg_sts_target.write(f"export class {struct_ani_info.sts_impl} {{\n")
        for field in struct.fields:
            ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            pkg_sts_target.write(f"    {field.name}: {ty_ani_info.sts_type};\n")
        pkg_sts_target.write("    constructor(\n")
        for field in struct.fields:
            ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            pkg_sts_target.write(f"        {field.name}: {ty_ani_info.sts_type},\n")
        pkg_sts_target.write("    ) {\n")
        for field in struct.fields:
            pkg_sts_target.write(f"        this.{field.name} = {field.name};\n")
        pkg_sts_target.write("    }\n" "}\n")

    # def gen_enum_interface(
    #     self,
    #     enum: EnumDecl,
    #     pkg_sts_target: OutputBuffer,
    # ):
    #     enum_ani_info = EnumANIInfo.get(self.am, enum)
    #     sts_value_types = []
    #     for item in enum.items:
    #         if item.ty_ref is None:
    #             sts_value_types.append("undefined")
    #             continue
    #         ty_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
    #         sts_value_types.append(f"{ty_ani_info.sts_type}")
    #     sts_value_types_str = " | ".join(sts_value_types)
    #     pkg_sts_target.write(
    #         f"export interface {enum_ani_info.sts_type} {{\n"
    #         f"    tag: int;\n"
    #         f"    value: {sts_value_types_str};\n"
    #         f"}}\n"
    #     )

    # def gen_enum_inner(
    #     self,
    #     enum: EnumDecl,
    #     pkg_sts_target: OutputBuffer,
    # ):
    #     enum_ani_info = EnumANIInfo.get(self.am, enum)
    #     sts_value_types = []
    #     for item in enum.items:
    #         if item.ty_ref is None:
    #             sts_value_types.append("undefined")
    #             continue
    #         ty_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
    #         sts_value_types.append(f"{ty_ani_info.sts_type}")
    #     sts_value_types_str = " | ".join(sts_value_types)
    #     pkg_sts_target.write(
    #         f"class {enum_ani_info.sts_impl} implements {enum_ani_info.sts_type} {{\n"
    #         f"    tag: int;\n"
    #         f"    value: {sts_value_types_str};\n"
    #         f"    constructor(tag: int, value: {sts_value_types_str}) {{\n"
    #         f"        this.tag = tag;\n"
    #         f"        this.value = value;\n"
    #         f"    }}\n"
    #         f"}}\n"
    #     )

    def gen_enum(
        self,
        enum: EnumDecl,
        pkg_sts_target: OutputBuffer,
    ):
        enum_ani_info = EnumANIInfo.get(self.am, enum)
        sts_value_types = []
        for item in enum.items:
            if item.ty_ref is None:
                sts_value_types.append("undefined")
                continue
            ty_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
            sts_value_types.append(f"{ty_ani_info.sts_type}")
        sts_value_types_str = " | ".join(sts_value_types)
        pkg_sts_target.write(
            f"export class {enum_ani_info.sts_impl} {{\n"
            f"    tag: int;\n"
            f"    value: {sts_value_types_str};\n"
            f"    constructor(tag: int, value: {sts_value_types_str}) {{\n"
            f"        this.tag = tag;\n"
            f"        this.value = value;\n"
            f"    }}\n"
            f"}}\n"
        )

    def gen_iface_interface(
        self,
        iface: IfaceDecl,
        pkg_sts_target: OutputBuffer,
    ):
        iface_ani_info = IfaceANIInfo.get(self.am, iface)
        pkg_sts_target.write(f"export interface {iface_ani_info.sts_type} {{\n")
        for method in iface.methods:
            params_sts = []
            for param in method.params:
                type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
                params_sts.append(f"{param.name}: {type_ani_info.sts_type}")
            params_sts_str = ", ".join(params_sts)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            pkg_sts_target.write(
                f"    {method.name}({params_sts_str}): {sts_return_ty_name};\n"
            )
        pkg_sts_target.write("}\n")

    def gen_iface_inner(
        self,
        iface: IfaceDecl,
        pkg_sts_target: OutputBuffer,
    ):
        iface_ani_info = IfaceANIInfo.get(self.am, iface)
        pkg_sts_target.write(
            f"class {iface_ani_info.sts_impl} implements {iface_ani_info.sts_type} {{\n"
            f"    _vtbl_ptr: long;\n"
            f"    _data_ptr: long;\n"
            f"    constructor(_vtbl_ptr: long, _data_ptr: long) {{\n"
            f"        this._vtbl_ptr = _vtbl_ptr;\n"
            f"        this._data_ptr = _data_ptr;\n"
            f"    }}\n"
        )
        for method in iface.methods:
            params_sts = []
            for param in method.params:
                type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
                params_sts.append(f"{param.name}: {type_ani_info.sts_type}")
            params_sts_str = ", ".join(params_sts)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            pkg_sts_target.write(
                f"    native {method.name}({params_sts_str}): {sts_return_ty_name};\n"
            )
        pkg_sts_target.write("}\n")


class ANICodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_ani_info = PackageANIInfo.get(self.am, pkg)
        pkg_cpp_info = PackageCppInfo.get(self.am, pkg)
        pkg_ani_header_target = COutputBuffer.create(
            self.tm, f"include/{pkg_ani_info.header}", True
        )
        pkg_ani_header_target.include("core/runtime.hpp")
        pkg_ani_header_target.write(
            f"namespace {pkg_ani_info.namespace} {{\n"
            f"ani_status ANIRegister(ani_env *env);\n"
            f"}}\n"
        )
        pkg_ani_source_target = COutputBuffer.create(
            self.tm, f"src/{pkg_ani_info.source}", False
        )
        pkg_ani_source_target.include(pkg_cpp_info.header)
        pkg_ani_source_target.include(pkg_ani_info.header)
        for func in pkg.functions:
            self.gen_func(func, pkg_ani_source_target)
        for iface in pkg.interfaces:
            for method in iface.methods:
                self.gen_method(iface, method, pkg_ani_source_target)
        # register infos
        register_infos: list[tuple[str, list[tuple[str, str]]]] = []
        impl_desc = pkg_ani_info.impl_desc
        func_infos = []
        for func in pkg.functions:
            glob_func_info = GlobFuncANIInfo.get(self.am, func)
            sts_name = glob_func_info.sts_name
            mangled_name = glob_func_info.mangled_name
            func_infos.append((sts_name, mangled_name))
        register_infos.append((impl_desc, func_infos))
        for iface in pkg.interfaces:
            iface_ani_info = IfaceANIInfo.get(self.am, iface)
            impl_desc = iface_ani_info.impl_desc
            func_infos = []
            for method in iface.methods:
                method_ani_info = IfaceMethodANIInfo.get(self.am, method)
                sts_name = method_ani_info.sts_name
                mangled_name = method_ani_info.mangled_name
                func_infos.append((sts_name, mangled_name))
            register_infos.append((impl_desc, func_infos))
        pkg_ani_source_target.write(
            f"namespace {pkg_ani_info.namespace} {{\n"
            f"ani_status ANIRegister(ani_env *env) {{\n"
        )
        for impl_desc, func_infos in register_infos:
            pkg_ani_source_target.write(
                f"    {{\n"
                f"        ani_class cls;\n"
                f'        if (ANI_OK != env->FindClass("{impl_desc}", &cls)) {{\n'
                f"            return ANI_ERROR;\n"
                f"        }}\n"
                f"        ani_native_function methods[] = {{\n"
            )
            for sts_name, mangled_name in func_infos:
                pkg_ani_source_target.write(
                    f'            {{"{sts_name}", nullptr, reinterpret_cast<void*>({mangled_name})}},\n'
                )
            pkg_ani_source_target.write(
                "        };\n"
                "        if (ANI_OK != env->Class_BindNativeMethods(cls, methods, sizeof(methods) / sizeof(ani_native_function))) {\n"
                "            return ANI_ERROR;\n"
                "        }\n"
                "    }\n"
            )
        pkg_ani_source_target.write("    return ANI_OK;\n" "}\n" "}\n")

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_ani_source_target: COutputBuffer,
    ):
        func_ani_info = GlobFuncANIInfo.get(self.am, func)
        func_cpp_info = GlobFuncCppInfo.get(self.am, func)
        params_ani = [
            "[[maybe_unused]] ani_env *env",
            "[[maybe_unused]] ani_object object",
        ]
        ani_param_names = []
        args_cpp = []
        for param in func.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            ani_param_name = f"{param.name}_ani"
            cpp_arg_name = f"{param.name}_cpp"
            params_ani.append(f"{type_ani_info.ani_type} {ani_param_name}")
            ani_param_names.append(ani_param_name)
            args_cpp.append(cpp_arg_name)
        params_ani_str = ", ".join(params_ani)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            ani_return_ty_name = type_ani_info.ani_type
        else:
            ani_return_ty_name = "void"
        pkg_ani_source_target.write(
            f"static {ani_return_ty_name} {func_ani_info.mangled_name}({params_ani_str}) {{\n"
        )
        for param, ani_param_name, cpp_arg_name in zip(
            func.params, ani_param_names, args_cpp, strict=True
        ):
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            type_ani_info.from_ani(
                pkg_ani_source_target, 4, "env", ani_param_name, cpp_arg_name
            )
        args_cpp_str = ", ".join(args_cpp)
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            cpp_return_ty_name = type_cpp_info.as_owner
            cpp_result = "cpp_result"
            ani_result = "ani_result"
            pkg_ani_source_target.write(
                f"    {cpp_return_ty_name} {cpp_result} = {func_cpp_info.full_name}({args_cpp_str});\n"
            )
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            type_ani_info.into_ani(
                pkg_ani_source_target, 4, "env", cpp_result, ani_result
            )
            pkg_ani_source_target.write(f"    return {ani_result};\n")
        else:
            pkg_ani_source_target.write(
                f"    {func_cpp_info.full_name}({args_cpp_str});\n" f"    return;\n"
            )
        pkg_ani_source_target.write("}\n")

    def gen_method(
        self,
        iface: IfaceDecl,
        method: IfaceMethodDecl,
        pkg_ani_source_target: COutputBuffer,
    ):
        method_ani_info = IfaceMethodANIInfo.get(self.am, method)
        method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_abi_info = IfaceABIInfo.get(self.am, iface)
        params_ani = [
            "[[maybe_unused]] ani_env *env",
            "[[maybe_unused]] ani_object object",
        ]
        ani_param_names = []
        args_cpp = []
        for param in method.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            ani_param_name = f"ani_param_{param.name}"
            cpp_arg_name = f"cpp_arg_{param.name}"
            params_ani.append(f"{type_ani_info.ani_type} {ani_param_name}")
            ani_param_names.append(ani_param_name)
            args_cpp.append(cpp_arg_name)
        params_ani_str = ", ".join(params_ani)
        if return_ty_ref := method.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            ani_return_ty_name = type_ani_info.ani_type
        else:
            ani_return_ty_name = "void"
        pkg_ani_source_target.write(
            f"static {ani_return_ty_name} {method_ani_info.mangled_name}({params_ani_str}) {{\n"
        )
        for param, ani_param_name, cpp_arg_name in zip(
            method.params, ani_param_names, args_cpp, strict=False
        ):
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            type_ani_info.from_ani(
                pkg_ani_source_target, 4, "env", ani_param_name, cpp_arg_name
            )
        args_cpp_str = ", ".join(args_cpp)
        pkg_ani_source_target.write(
            f"    ani_long ani_data_ptr;\n"
            f'    env->Object_GetPropertyByName_Long(object, "_data_ptr", reinterpret_cast<ani_long*>(&ani_data_ptr));\n'
            f"    ani_long ani_vtbl_ptr;\n"
            f'    env->Object_GetPropertyByName_Long(object, "_vtbl_ptr", reinterpret_cast<ani_long*>(&ani_vtbl_ptr));\n'
            f"    DataBlockHead* cpp_data_ptr = reinterpret_cast<DataBlockHead*>(ani_data_ptr);\n"
            f"    {iface_abi_info.vtable}* cpp_vtbl_ptr = reinterpret_cast<{iface_abi_info.vtable}*>(ani_vtbl_ptr);\n"
            f"    {iface_cpp_info.full_weak_name} cpp_iface = {iface_cpp_info.full_weak_name}({{cpp_vtbl_ptr, cpp_data_ptr}});\n"
        )
        if return_ty_ref := method.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            cpp_return_ty_name = type_cpp_info.as_owner
            cpp_result = "cpp_result"
            ani_result = "ani_result"
            pkg_ani_source_target.write(
                f"    {cpp_return_ty_name} {cpp_result} = cpp_iface->{method_cpp_info.call_name}({args_cpp_str});\n"
            )
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            type_ani_info.into_ani(
                pkg_ani_source_target, 4, "env", cpp_result, ani_result
            )
            pkg_ani_source_target.write(f"    return {ani_result};\n")
        else:
            pkg_ani_source_target.write(
                f"    cpp_iface->{method_cpp_info.call_name}({args_cpp_str});\n"
                f"    return;\n"
            )
        pkg_ani_source_target.write("}\n")
