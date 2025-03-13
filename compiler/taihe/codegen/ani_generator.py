from abc import ABCMeta

from typing_extensions import override

from taihe.codegen.cpp_generator import (
    EnumCppInfo,
    GlobFuncCppInfo,
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
    STRING,
    ArrayType,
    CallbackType,
    EnumType,
    IfaceType,
    MapType,
    OptionalType,
    ScalarType,
    SetType,
    StringType,
    StructType,
    Type,
    VectorType,
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
        self.src = f"{p.name}.ani.cpp"
        self.sts = f"{p.name}.ets"
        self.lib_name = (
            ani_lib_item.value if (ani_lib_item := p.attrs.get("ani_lib")) else p.name
        )
        self.cls_name = f"L{self.lib_name}/ETSGLOBAL;"


class GlobFuncANIInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        p = f.node_parent
        assert p
        segments = [*p.segments, f.name]
        self.mangled_name = encode(segments, DeclKind.ANI_FUNC)
        self.sts_name = f.name


class IfaceMethodANIInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, f: IfaceMethodDecl) -> None:
        d = f.node_parent
        assert d
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name, f.name]
        self.mangled_name = encode(segments, DeclKind.ANI_FUNC)
        self.sts_name = f.name


class StructANIInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.node_parent
        assert p
        self.sts_name = d.name
        self.sts_ctor = f"{d.name}_inner"
        self.prx_name = f"{d.name}_proxy"
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.cls_name = f"L{pkg_ani_info.lib_name}/{self.prx_name};"


class EnumANIInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.node_parent
        assert p
        self.sts_name = d.name
        self.sts_ctor = f"{d.name}_inner"
        self.prx_name = f"{d.name}_proxy"
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.cls_name = f"L{pkg_ani_info.lib_name}/{self.prx_name};"


class IfaceANIInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.node_parent
        assert p
        self.sts_name = d.name
        self.prx_name = f"{d.name}_proxy"
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.cls_name = f"L{pkg_ani_info.lib_name}/{self.prx_name};"


class AbstractTypeANIInfo(metaclass=ABCMeta):
    ani_type: ANIType
    sts_type: str

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

    def into_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        cpp_array_value: str,
        ani_array_result: str,
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
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    def into_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")


class StructTypeANIInfo(AbstractAnalysis[StructType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: StructType):
        self.t = t
        self.am = am
        struct_ani_info = StructANIInfo.get(am, t.ty_decl)
        self.sts_type = struct_ani_info.sts_name
        self.ani_type = ANI_OBJECT

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
        type_cpp_info = TypeCppInfo.get(self.am, self.t)
        target.write(
            f"{' ' * offset}{type_cpp_info.as_owner} {cpp_result} = {type_cpp_info.as_owner}{{{cpp_moved_fields_str}}};\n"
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
        ani_field_results_str = ", ".join(ani_field_results)
        struct_ani_info = StructANIInfo.get(self.am, self.t.ty_decl)
        ani_result_cls = f"{ani_result}_cls"
        ani_result_ctor = f"{ani_result}_ctor"
        target.write(
            f"{' ' * offset}ani_class {ani_result_cls};\n"
            f"{' ' * offset}{env}->FindClass(\"{struct_ani_info.cls_name}\", &{ani_result_cls});\n"
            f"{' ' * offset}ani_method {ani_result_ctor};\n"
            f"{' ' * offset}{env}->Class_FindMethod({ani_result_cls}, \"<ctor>\", nullptr, &{ani_result_ctor});\n"
            f"{' ' * offset}ani_object {ani_result};\n"
            f"{' ' * offset}{env}->Object_New({ani_result_cls}, {ani_result_ctor}, &{ani_result}, {ani_field_results_str});\n"
        )

    @override
    def from_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        ani_array_value: str,
        cpp_array_buffer: str,
    ):
        type_cpp_info = TypeCppInfo.get(self.am, self.t)
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
            f"{' ' * offset}    new (&{cpp_array_buffer}[{i}]) {type_cpp_info.as_owner}(std::move({cpp_result}));\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def into_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        cpp_array_value: str,
        ani_array_result: str,
    ):
        struct_ani_info = StructANIInfo.get(self.am, self.t.ty_decl)
        ani_class = f"{ani_array_result}_cls"
        ani_result = "_ani_res"
        i = "_i"
        target.write(
            f"{' ' * offset}ani_array_ref {ani_array_result};\n"
            f"{' ' * offset}ani_class {ani_class};\n"
            f"{' ' * offset}{env}->FindClass(\"{struct_ani_info.cls_name}\", &{ani_class});\n"
            f"{' ' * offset}ani_ref undefined;\n"
            f"{' ' * offset}{env}->GetUndefined(&undefined);\n"
            f"{' ' * offset}{env}->Array_New_Ref({ani_class}, {size}, undefined, &{ani_array_result});\n"
            f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
        )
        self.into_ani(target, offset + 4, env, f"{cpp_array_value}[{i}]", ani_result)
        target.write(
            f"{' ' * offset}    {env}->Array_Set_Ref({ani_array_result}, {i}, {ani_result});\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def into_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        self.into_ani(target, offset, env, cpp_value, ani_result)

    @override
    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        self.from_ani(
            target,
            offset,
            env,
            f"static_cast<{self.ani_type}>({ani_value})",
            cpp_result,
        )


class EnumTypeANIInfo(AbstractAnalysis[EnumType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        self.t = t
        self.am = am
        enum_ani_info = EnumANIInfo.get(am, t.ty_decl)
        self.sts_type = enum_ani_info.sts_name
        self.ani_type = ANI_OBJECT

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        ani_value_tag = f"{cpp_result}_tag"
        ani_value_val = f"{cpp_result}_value"
        target.write(
            f"{' ' * offset}ani_int {ani_value_tag};\n"
            f"{' ' * offset}{env}->Object_GetPropertyByName_Int({ani_value}, \"tag\", &{ani_value_tag});\n"
            f"{' ' * offset}ani_ref {ani_value_val};\n"
            f"{' ' * offset}{env}->Object_GetPropertyByName_Ref({ani_value}, \"value\", &{ani_value_val});\n"
        )
        cpp_tag = f"{cpp_result}_tag"
        enum_cpp_info = EnumCppInfo.get(self.am, self.t.ty_decl)
        type_cpp_info = TypeCppInfo.get(self.am, self.t)
        target.write(
            f"{' ' * offset}{type_cpp_info.as_owner} {cpp_result} = [=] {{\n"
            f"{' ' * offset}    {enum_cpp_info.full_name}::tag_t {cpp_tag} = ({enum_cpp_info.full_name}::tag_t){ani_value_tag};\n"
            f"{' ' * offset}    switch ({cpp_tag}) {{\n"
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
                    ani_value,
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
        enum_ani_info = EnumANIInfo.get(self.am, self.t.ty_decl)
        target.write(
            f"{' ' * offset}ani_class {ani_result_cls};\n"
            f"{' ' * offset}{env}->FindClass(\"{enum_ani_info.cls_name}\", &{ani_result_cls});\n"
            f"{' ' * offset}ani_method {ani_result_ctor};\n"
            f"{' ' * offset}{env}->Class_FindMethod({ani_result_cls}, \"<ctor>\", nullptr, &{ani_result_ctor});\n"
            f"{' ' * offset}ani_object {ani_result};\n"
            f"{' ' * offset}{env}->Object_New({ani_result_cls}, {ani_result_ctor}, &{ani_result}, {ani_result_tag}, {ani_result_val});\n"
        )

    @override
    def from_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        ani_array_value: str,
        cpp_array_buffer: str,
    ):
        type_cpp_info = TypeCppInfo.get(self.am, self.t)
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
            f"{' ' * offset}    new (&{cpp_array_buffer}[{i}]) {type_cpp_info.as_owner}(std::move({cpp_result}));\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def into_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        cpp_array_value: str,
        ani_array_result: str,
    ):
        enum_ani_info = EnumANIInfo.get(self.am, self.t.ty_decl)
        ani_class = f"{ani_array_result}_cls"
        ani_result = "_ani_res"
        i = "_i"
        target.write(
            f"{' ' * offset}ani_array_ref {ani_array_result};\n"
            f"{' ' * offset}ani_class {ani_class};\n"
            f"{' ' * offset}{env}->FindClass(\"{enum_ani_info.cls_name}\", &{ani_class});\n"
            f"{' ' * offset}ani_ref undefined;\n"
            f"{' ' * offset}{env}->GetUndefined(&undefined);\n"
            f"{' ' * offset}{env}->Array_New_Ref({ani_class}, {size}, undefined, &{ani_array_result});\n"
            f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
        )
        self.into_ani(target, offset + 4, env, f"{cpp_array_value}[{i}]", ani_result)
        target.write(
            f"{' ' * offset}    {env}->Array_Set_Ref({ani_array_result}, {i}, {ani_result});\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def into_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        self.into_ani(target, offset, env, cpp_value, ani_result)

    @override
    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        self.from_ani(
            target,
            offset,
            env,
            f"static_cast<{self.ani_type}>({ani_value})",
            cpp_result,
        )


class IfaceTypeANIInfo(AbstractAnalysis[IfaceType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        pass


class ScalarTypeANIInfo(AbstractAnalysis[ScalarType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        sts_type, ani_type = {
            BOOL: ("boolean", ANI_BOOLEAN),
            F32: ("float", ANI_FLOAT),
            F64: ("double", ANI_DOUBLE),
            I8: ("byte", ANI_BYTE),
            I16: ("short", ANI_SHORT),
            I32: ("int", ANI_INT),
            I64: ("long", ANI_LONG),
        }[t]
        self.sts_type = sts_type
        self.ani_type = ani_type
        self.cpp_info = TypeCppInfo.get(am, t)

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        target.write(f"{' ' * offset}{self.ani_type} {cpp_result} = {ani_value};\n")

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
            f"{' ' * offset}{self.cpp_info.as_owner} {ani_result} = {cpp_value};\n"
        )

    @override
    def from_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        ani_array_value: str,
        cpp_array_buffer: str,
    ):
        target.write(
            f"{' ' * offset}{env}->Array_GetRegion_{self.ani_type.suffix}({ani_array_value}, 0, {size}, {cpp_array_buffer});\n"
        )

    @override
    def into_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        cpp_array_value: str,
        ani_array_result: str,
    ):
        target.write(
            f"{' ' * offset}{self.ani_type.array} {ani_array_result};\n"
            f"{' ' * offset}{env}->Array_New_{self.ani_type.suffix}({size}, &{ani_array_result});\n"
            f"{' ' * offset}{env}->Array_SetRegion_{self.ani_type.suffix}({ani_array_result}, 0, {size}, {cpp_array_value});\n"
        )

    @override
    def into_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        ani_class = f"{ani_result}_cls"
        ani_ctor = f"{ani_result}_ctor"
        ani_value = f"{ani_result}_ani"
        target.write(
            f"{' ' * offset}ani_class {ani_class};\n"
            f"{' ' * offset}{env}->FindClass(\"Lstd/core/{self.ani_type.suffix};\", &{ani_class});\n"
            f"{' ' * offset}ani_method {ani_ctor};\n"
            f"{' ' * offset}{env}->Class_FindMethod({ani_class}, \"<ctor>\", nullptr, &{ani_ctor});\n"
            f"{' ' * offset}ani_object {ani_result};\n"
        )
        self.into_ani(target, offset, env, cpp_value, ani_value)
        target.write(
            f"{' ' * offset}{env}->Object_New({ani_class}, {ani_ctor}, &{ani_result}, {ani_value});\n"
        )

    @override
    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        ani_class = f"{cpp_result}_cls"
        ani_getter = f"{cpp_result}_get"
        ani_result = f"{cpp_result}_ani"
        target.write(
            f"{' ' * offset}ani_class {ani_class};\n"
            f"{' ' * offset}{env}->FindClass(\"Lstd/core/{self.ani_type.suffix};\", &{ani_class});\n"
            f"{' ' * offset}ani_method {ani_getter};\n"
            f"{' ' * offset}{env}->Class_FindMethod({ani_class}, \"{self.sts_type}Value\", nullptr, &{ani_getter});\n"
            f"{' ' * offset}{self.ani_type} {ani_result};\n"
            f"{' ' * offset}{env}->Object_CallMethod_{self.ani_type.suffix}((ani_object){ani_value}, {ani_getter}, &{ani_result});\n"
        )
        self.from_ani(target, offset, env, ani_result, cpp_result)


class StringTypeANIInfo(AbstractAnalysis[StringType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: StringType):
        if t != STRING:
            raise ValueError
        self.sts_type = "string"
        self.ani_type = ANI_STRING
        self.cpp_info = TypeCppInfo.get(am, t)

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

    @override
    def from_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        ani_array_value: str,
        cpp_array_buffer: str,
    ):
        ani_value = "_ani_val"
        cpp_result = "_cpp_res"
        i = "_i"
        target.write(
            f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
            f"{' ' * offset}    ani_string {ani_value};\n"
            f"{' ' * offset}    {env}->Array_Get_Ref({ani_array_value}, {i}, reinterpret_cast<ani_ref*>(&{ani_value}));\n"
        )
        self.from_ani(target, offset + 4, env, ani_value, cpp_result)
        target.write(
            f"{' ' * offset}    new (&{cpp_array_buffer}[{i}]) taihe::core::string(std::move({cpp_result}));\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def into_ani_array(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        cpp_array_value: str,
        ani_array_result: str,
    ):
        ani_class = f"{ani_array_result}_cls"
        ani_result = "_ani_res"
        i = "_i"
        target.write(
            f"{' ' * offset}ani_array_ref {ani_array_result};\n"
            f"{' ' * offset}ani_class {ani_class};\n"
            f"{' ' * offset}{env}->FindClass(\"Lstd/core/String;\", &{ani_class});\n"
            f"{' ' * offset}ani_ref undefined;\n"
            f"{' ' * offset}{env}->GetUndefined(&undefined);\n"
            f"{' ' * offset}{env}->Array_New_Ref({ani_class}, {size}, undefined, &{ani_array_result});\n"
            f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
        )
        self.into_ani(target, offset + 4, env, f"{cpp_array_value}[{i}]", ani_result)
        target.write(
            f"{' ' * offset}    {env}->Array_Set_Ref({ani_array_result}, {i}, {ani_result});\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def into_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        self.into_ani(target, offset, env, cpp_value, ani_result)

    @override
    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        self.from_ani(
            target,
            offset,
            env,
            f"static_cast<{self.ani_type}>({ani_value})",
            cpp_result,
        )


class ArrayTypeANIInfo(AbstractAnalysis[ArrayType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        item_ty_ani_info = TypeANIInfo.get(am, t.item_ty)
        self.sts_type = f"({item_ty_ani_info.sts_type}[])"
        self.ani_type = item_ty_ani_info.ani_type.array
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

    @override
    def into_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        self.into_ani(target, offset, env, cpp_value, ani_result)

    @override
    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        self.from_ani(
            target,
            offset,
            env,
            f"static_cast<{self.ani_type}>({ani_value})",
            cpp_result,
        )


class OptionalTypeANIInfo(AbstractAnalysis[OptionalType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: OptionalType) -> None:
        item_ty_ani_info = TypeANIInfo.get(am, t.item_ty)
        self.sts_type = f"({item_ty_ani_info.sts_type} | undefined)"
        self.ani_type = ANI_REF
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
            f"{' ' * offset}    *{cpp_pointer} = std::move({cpp_spec});\n"
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


class VectorTypeANIInfo(AbstractAnalysis[VectorType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: VectorType) -> None:
        pass


class MapTypeANIInfo(AbstractAnalysis[MapType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        pass


class SetTypeANIInfo(AbstractAnalysis[SetType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: SetType) -> None:
        pass


class CallbackTypeANIInfo(AbstractAnalysis[CallbackType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: CallbackType) -> None:
        pass


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

    @override
    def visit_vector_type(self, t: VectorType) -> AbstractTypeANIInfo:
        return VectorTypeANIInfo.get(self.am, t)

    @override
    def visit_map_type(self, t: MapType) -> AbstractTypeANIInfo:
        return MapTypeANIInfo.get(self.am, t)

    @override
    def visit_set_type(self, t: SetType) -> AbstractTypeANIInfo:
        return SetTypeANIInfo.get(self.am, t)

    @override
    def visit_callback_type(self, t: CallbackType) -> AbstractTypeANIInfo:
        return CallbackTypeANIInfo.get(self.am, t)


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

        for struct in pkg.structs:
            self.gen_struct_interface(struct, pkg_sts_target)
        for enum in pkg.enums:
            self.gen_enum_interface(enum, pkg_sts_target)

        for func in pkg.functions:
            self.gen_func(func, pkg_sts_target)

        for struct in pkg.structs:
            self.gen_struct_inner(struct, pkg_sts_target)
        for enum in pkg.enums:
            self.gen_enum_inner(enum, pkg_sts_target)

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

    def gen_struct_interface(
        self,
        struct: StructDecl,
        pkg_sts_target: OutputBuffer,
    ):
        struct_ani_info = StructANIInfo.get(self.am, struct)
        pkg_sts_target.write(f"export interface {struct_ani_info.sts_name} {{\n")
        for field in struct.fields:
            ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            pkg_sts_target.write(f"    {field.name}: {ty_ani_info.sts_type};\n")
        pkg_sts_target.write("}\n")

    def gen_struct_inner(
        self,
        struct: StructDecl,
        pkg_sts_target: OutputBuffer,
    ):
        struct_ani_info = StructANIInfo.get(self.am, struct)
        pkg_sts_target.write(
            f"class {struct_ani_info.sts_ctor} implements {struct_ani_info.sts_name} {{\n"
        )
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

    def gen_enum_interface(
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
            f"export interface {enum_ani_info.sts_name} {{\n"
            f"    tag: int;\n"
            f"    value: {sts_value_types_str};\n"
            f"}}\n"
        )

    def gen_enum_inner(
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
            f"class {enum_ani_info.sts_ctor} implements {enum_ani_info.sts_name} {{\n"
            f"    tag: int;\n"
            f"    value: {sts_value_types_str};\n"
            f"    constructor(tag: int, value: {sts_value_types_str}) {{\n"
            f"        this.tag = tag;\n"
            f"        this.value = value;\n"
            f"    }}\n"
            f"}}\n"
        )


class ANICodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_ani_info = PackageANIInfo.get(self.am, pkg)
        pkg_ani_target = COutputBuffer.create(self.tm, f"src/{pkg_ani_info.src}", False)
        pkg_cpp_info = PackageCppInfo.get(self.am, pkg)
        pkg_ani_target.include("ani.h")
        pkg_ani_target.include(pkg_cpp_info.header)
        for func in pkg.functions:
            self.gen_func(func, pkg_ani_target)
        pkg_ani_target.write(
            "ANI_EXPORT ani_status ANI_Constructor(ani_vm *vm, uint32_t *result) {\n"
            "    ani_env *env;\n"
            "    if (ANI_OK != vm->GetEnv(ANI_VERSION_1, &env)) {\n"
            "        return ANI_ERROR;\n"
            "    }\n"
        )
        pkg_ani_target.write(
            f"    {{\n"
            f'    static const char *className = "{pkg_ani_info.cls_name}";\n'
            f"    ani_class cls;\n"
            f"    if (ANI_OK != env->FindClass(className, &cls)) {{\n"
            f"        return ANI_ERROR;\n"
            f"    }}\n"
            f"    ani_native_function methods[] = {{\n"
        )
        for func in pkg.functions:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            pkg_ani_target.write(
                f'        {{"{func_ani_info.sts_name}", nullptr, reinterpret_cast<void*>({func_ani_info.mangled_name})}},\n'
            )
        pkg_ani_target.write(
            "    };\n"
            "    if (ANI_OK != env->Class_BindNativeMethods(cls, methods, sizeof(methods) / sizeof(ani_native_function))) {\n"
            "        return ANI_ERROR;\n"
            "    }\n"
            "    }\n"
        )
        pkg_ani_target.write(
            "    *result = ANI_VERSION_1;\n" "    return ANI_OK;\n" "}\n"
        )

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_ani_target: COutputBuffer,
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
            ani_param_name = f"ani_param_{param.name}"
            cpp_arg_name = f"cpp_arg_{param.name}"
            params_ani.append(f"{type_ani_info.ani_type} {ani_param_name}")
            ani_param_names.append(ani_param_name)
            args_cpp.append(cpp_arg_name)
        params_ani_str = ", ".join(params_ani)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            ani_return_ty_name = type_ani_info.ani_type
        else:
            ani_return_ty_name = "void"
        pkg_ani_target.write(
            f"static {ani_return_ty_name} {func_ani_info.mangled_name}({params_ani_str}) {{\n"
        )
        for param, ani_param_name, cpp_arg_name in zip(
            func.params, ani_param_names, args_cpp
        ):
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            type_ani_info.from_ani(
                pkg_ani_target, 4, "env", ani_param_name, cpp_arg_name
            )
        args_cpp_str = ", ".join(args_cpp)
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            cpp_return_ty_name = type_cpp_info.as_owner
            cpp_result = "cpp_result"
            ani_result = "ani_result"
            pkg_ani_target.write(
                f"    {cpp_return_ty_name} {cpp_result} = {func_cpp_info.full_name}({args_cpp_str});\n"
            )
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            type_ani_info.into_ani(pkg_ani_target, 4, "env", cpp_result, ani_result)
            pkg_ani_target.write(f"    return {ani_result};\n")
        else:
            pkg_ani_target.write(
                f"    {func_cpp_info.full_name}({args_cpp_str});\n" f"    return;\n"
            )
        pkg_ani_target.write("}\n")
