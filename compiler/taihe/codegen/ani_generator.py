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
    StructCppInfo,
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
        self.pkg_name = (
            ani_lib_item.value
            if (ani_lib_item := p.attrs.get("ani_lib"))
            else "/".join(p.segments)
        )
        self.impl_desc = f"L{self.pkg_name}/ETSGLOBAL;"


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
        segments = [*p.segments, d.name]
        self.from_ani_func_name = encode(segments, DeclKind.FROM_ANI)
        self.into_ani_func_name = encode(segments, DeclKind.INTO_ANI)
        self.decl_header = f"{p.name}.{d.name}.ani.0.h"
        self.impl_header = f"{p.name}.{d.name}.ani.1.h"

        self.sts_type = d.name
        self.sts_impl = d.name
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.type_desc = f"L{pkg_ani_info.pkg_name}/{self.sts_type};"
        self.impl_desc = f"L{pkg_ani_info.pkg_name}/{self.sts_impl};"


class EnumANIInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name]
        self.from_ani_func_name = encode(segments, DeclKind.FROM_ANI)
        self.into_ani_func_name = encode(segments, DeclKind.INTO_ANI)
        self.decl_header = f"{p.name}.{d.name}.ani.0.h"
        self.impl_header = f"{p.name}.{d.name}.ani.1.h"

        self.sts_type = d.name
        self.sts_impl = d.name
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.type_desc = f"L{pkg_ani_info.pkg_name}/{self.sts_type};"
        self.impl_desc = f"L{pkg_ani_info.pkg_name}/{self.sts_impl};"


class IfaceANIInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name]
        self.from_ani_func_name = encode(segments, DeclKind.FROM_ANI)
        self.into_ani_func_name = encode(segments, DeclKind.INTO_ANI)
        self.decl_header = f"{p.name}.{d.name}.ani.0.h"
        self.impl_header = f"{p.name}.{d.name}.ani.1.h"

        self.sts_type = d.name
        self.sts_impl = f"{d.name}_inner"
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.type_desc = f"L{pkg_ani_info.pkg_name}/{self.sts_type};"
        self.impl_desc = f"L{pkg_ani_info.pkg_name}/{self.sts_impl};"


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

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        struct_ani_info = StructANIInfo.get(self.am, self.t.ty_decl)
        target.include(struct_ani_info.impl_header)
        target.write(
            f"{' ' * offset}{self.cpp_info.as_owner} {cpp_result} = {struct_ani_info.from_ani_func_name}({env}, {ani_value});\n"
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
        struct_ani_info = StructANIInfo.get(self.am, self.t.ty_decl)
        target.include(struct_ani_info.impl_header)
        target.write(
            f"{' ' * offset}ani_object {ani_result} = {struct_ani_info.into_ani_func_name}({env}, {cpp_value});\n"
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

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        enum_ani_info = EnumANIInfo.get(self.am, self.t.ty_decl)
        target.include(enum_ani_info.impl_header)
        target.write(
            f"{' ' * offset}{self.cpp_info.as_owner} {cpp_result} = {enum_ani_info.from_ani_func_name}({env}, {ani_value});\n"
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
        enum_ani_info = EnumANIInfo.get(self.am, self.t.ty_decl)
        target.include(enum_ani_info.impl_header)
        target.write(
            f"{' ' * offset}ani_object {ani_result} = {enum_ani_info.into_ani_func_name}({env}, {cpp_value});\n"
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

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        iface_ani_info = IfaceANIInfo.get(self.am, self.t.ty_decl)
        target.include(iface_ani_info.impl_header)
        target.write(
            f"{' ' * offset}{self.cpp_info.as_owner} {cpp_result} = {iface_ani_info.from_ani_func_name}({env}, {ani_value});\n"
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
        iface_ani_info = IfaceANIInfo.get(self.am, self.t.ty_decl)
        target.include(iface_ani_info.impl_header)
        target.write(
            f"{' ' * offset}ani_object {ani_result} = {iface_ani_info.into_ani_func_name}({env}, {cpp_value});\n"
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


class Namespace:
    def __init__(self, name: str):
        self.name: str = name
        self.children_namespaces: dict[str, Namespace] = {}
        self.pkgs: list[PackageDecl] = []

    def add_path(self, path_parts: list[str], pkg: PackageDecl):
        if not path_parts:
            self.pkgs.append(pkg)
            return
        head, *tail = path_parts
        child = self.children_namespaces.setdefault(head, Namespace(head))
        child.add_path(tail, pkg)

    def display(self, level=0):
        # This function use to test NsTreeNode
        print(f"{'  ' * level}{self.name} : {self.pkgs if self.pkgs else ''}")
        for child in self.children_namespaces.values():
            child.display(level + 1)


class NsTree:
    def __init__(self):
        self.root = Namespace("root")

    def add(self, path: str, pkg_name: PackageDecl):
        parts = path.split(".")
        self.root.add_path(parts, pkg_name)

    def display(self):
        self.root.display()


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

        # pkg_sts_target.write(f'loadLibrary("{self.lib_name}");\n')

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
        callback_flag = 0
        for iface in pkg.interfaces:
            self.gen_iface_interface(iface, pkg_sts_target)
            for method in iface.methods:
                if method.attrs.get("gen_async"):
                    callback_flag = 1

        for struct in pkg.structs:
            self.gen_struct(struct, pkg_sts_target)
        for enum in pkg.enums:
            self.gen_enum(enum, pkg_sts_target)

        for func in pkg.functions:
            self.gen_func(func, pkg_sts_target)
            if func.attrs.get("gen_async"):
                callback_flag = 1
        if callback_flag:
            pkg_sts_target.write(
                f"export type AsyncCallback<T> = (err: Error, data?: T) => void;\n"
            )

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_sts_target: OutputBuffer,
    ):
        func_ani_info = GlobFuncANIInfo.get(self.am, func)
        params_sts = []
        params_name = []
        for param in func.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            params_sts.append(f"{param.name}: {type_ani_info.sts_type}")
            params_name.append(param.name)
        params_sts_str = ", ".join(params_sts)
        params_name_str = ", ".join(params_name)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            sts_return_ty_name = type_ani_info.sts_type
        else:
            sts_return_ty_name = "void"
        pkg_sts_target.write(
            f"export native function {func_ani_info.sts_name}({params_sts_str}): {sts_return_ty_name};\n"
        )

        if async_func := func.attrs.get("gen_async"):
            params_sts.append(f"callback: AsyncCallback<{sts_return_ty_name}>")
            params_sts_str_call_method = ", ".join(params_sts)
            async_func_name = async_func.value
            pkg_sts_target.write(
                f"export function {async_func_name}({params_sts_str_call_method}): void {{\n"
                f"    let p1 = launch {func_ani_info.sts_name}({params_name_str});\n"
            )
            if sts_return_ty_name == "void":
                pkg_sts_target.write(
                    f"    p1.then((): void => {{\n"
                    f"        let error = new Error();\n"
                    f"        callback(error);\n"
                )
            else:
                pkg_sts_target.write(
                    f"    p1.then((ret: NullishType) => {{\n"
                    f"            let retInner = ret as {sts_return_ty_name};\n"
                    f"            let error = new Error();\n"
                    f"            callback(error, retInner);\n"
                )
            pkg_sts_target.write(
                f"    }})\n"
                f"    .catch((ret: NullishType) => {{\n"
                f"        let retError = ret as Error;\n"
                f"        callback(retError);\n"
                f"    }});\n"
                f"}}\n"
            )

        if promise_func := func.attrs.get("gen_promise"):
            promise_func_name = promise_func.value
            pkg_sts_target.write(
                f"export function {promise_func_name}({params_sts_str}): Promise<{sts_return_ty_name}> {{\n"
                f"    return launch {func_ani_info.sts_name}({params_name_str});\n"
                f"}}\n"
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
            iface_method_info = IfaceMethodANIInfo.get(self.am, method)
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
                f"    {iface_method_info.sts_name}({params_sts_str}): {sts_return_ty_name};\n"
            )

            if async_func := method.attrs.get("gen_async"):
                params_sts.append(f"callback: AsyncCallback<{sts_return_ty_name}>")
                params_sts_str_with_call = ", ".join(params_sts)
                async_func_name = async_func.value
                pkg_sts_target.write(
                    f"    {async_func_name}({params_sts_str_with_call}): void;\n"
                )

            if promise_func := method.attrs.get("gen_promise"):
                promise_func_name = promise_func.value
                pkg_sts_target.write(
                    f"    {promise_func_name}({params_sts_str}): Promise<{sts_return_ty_name}>;\n"
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
            iface_method_info = IfaceMethodANIInfo.get(self.am, method)
            params_sts = []
            params_name = []
            for param in method.params:
                type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
                params_sts.append(f"{param.name}: {type_ani_info.sts_type}")
                params_name.append(param.name)
            params_sts_str = ", ".join(params_sts)
            params_name_str = ", ".join(params_name)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            pkg_sts_target.write(
                f"    native {iface_method_info.sts_name}({params_sts_str}): {sts_return_ty_name};\n"
            )

            params_sts.append(f"callback: AsyncCallback<{sts_return_ty_name}>")
            params_sts_str_with_call = ", ".join(params_sts)
            if async_func := method.attrs.get("gen_async"):
                async_func_name = async_func.value
                pkg_sts_target.write(
                    f"    {async_func_name}({params_sts_str_with_call}): void {{\n"
                    f"        let p1 = launch this.{iface_method_info.sts_name}({params_name_str});\n"
                )
                if sts_return_ty_name == "void":
                    pkg_sts_target.write(
                        f"        p1.then((): void => {{\n"
                        f"            let error = new Error();\n"
                        f"            callback(error);\n"
                    )
                else:
                    pkg_sts_target.write(
                        f"        p1.then((ret: NullishType) => {{\n"
                        f"            let retInner = ret as {sts_return_ty_name};\n"
                        f"            let error = new Error();\n"
                        f"            callback(error, retInner);\n"
                    )
                pkg_sts_target.write(
                    f"        }})\n"
                    f"        .catch((ret: NullishType) => {{\n"
                    f"            let retError = ret as Error;\n"
                    f"            callback(retError);\n"
                    f"        }});\n"
                    f"    }}\n"
                )
            if promise_func := method.attrs.get("gen_promise"):
                promise_func_name = promise_func.value
                pkg_sts_target.write(
                    f"    {promise_func_name}({params_sts_str}): Promise<{sts_return_ty_name}> {{\n"
                    f"        return launch this.{iface_method_info.sts_name}({params_name_str});\n"
                    f"    }}\n"
                )
        pkg_sts_target.write("}\n")


class ANICodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package(pkg)
        self.gen_constructor(pg)

    def gen_constructor(self, pg: PackageGroup):
        constructor_file = "ani_constructor.cpp"
        constructor_target = COutputBuffer.create(
            self.tm, f"src/{constructor_file}", False
        )
        constructor_target.write(
            "ANI_EXPORT ani_status ANI_Constructor(ani_vm *vm, uint32_t *result) {\n"
            "    ani_env *env;\n"
            "    if (ANI_OK != vm->GetEnv(ANI_VERSION_1, &env)) {\n"
            "        return ANI_ERROR;\n"
            "    }\n"
        )
        for pkg in pg.packages:
            pkg_ani_info = PackageANIInfo.get(self.am, pkg)
            constructor_target.include(pkg_ani_info.header)
            constructor_target.write(
                f"    if (ANI_OK != {pkg_ani_info.namespace}::ANIRegister(env)) {{\n"
                f"        return ANI_ERROR;\n"
                f"    }}\n"
            )
        constructor_target.write(
            "    *result = ANI_VERSION_1;\n" "    return ANI_OK;\n" "}\n"
        )

    def gen_package(self, pkg: PackageDecl):
        for iface in pkg.interfaces:
            self.gen_iface_file(iface)
        for struct in pkg.structs:
            self.gen_struct_file(struct)
        for enum in pkg.enums:
            self.gen_enum_file(enum)
        pkg_ani_info = PackageANIInfo.get(self.am, pkg)
        pkg_cpp_info = PackageCppInfo.get(self.am, pkg)
        self.gen_package_header(pkg, pkg_ani_info, pkg_cpp_info)
        self.gen_package_source(pkg, pkg_ani_info, pkg_cpp_info)

    def gen_package_header(
        self,
        pkg: PackageDecl,
        pkg_ani_info: PackageANIInfo,
        pkg_cpp_info: PackageCppInfo,
    ):
        pkg_ani_header_target = COutputBuffer.create(
            self.tm, f"include/{pkg_ani_info.header}", True
        )
        pkg_ani_header_target.include("core/runtime.hpp")
        pkg_ani_header_target.write(
            f"namespace {pkg_ani_info.namespace} {{\n"
            f"ani_status ANIRegister(ani_env *env);\n"
            f"}}\n"
        )

    def gen_package_source(
        self,
        pkg: PackageDecl,
        pkg_ani_info: PackageANIInfo,
        pkg_cpp_info: PackageCppInfo,
    ):
        pkg_ani_source_target = COutputBuffer.create(
            self.tm, f"src/{pkg_ani_info.source}", False
        )
        pkg_ani_source_target.include(pkg_cpp_info.header)
        pkg_ani_source_target.include(pkg_ani_info.header)
        # generate functions
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
            f"    taihe::core::set_env(env);\n"
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
            ani_param_name = f"{param.name}_ani"
            cpp_arg_name = f"{param.name}_cpp"
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
            f"    taihe::core::set_env(env);\n"
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

    def gen_iface_file(
        self,
        iface: IfaceDecl,
    ):
        iface_abi_info = IfaceABIInfo.get(self.am, iface)
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_ani_info = IfaceANIInfo.get(self.am, iface)
        # declaration
        iface_ani_decl_target = COutputBuffer.create(
            self.tm, f"include/{iface_ani_info.decl_header}", True
        )
        iface_ani_decl_target.include("ani.h")
        iface_ani_decl_target.include(iface_cpp_info.decl_header)
        iface_ani_decl_target.write(
            f"{iface_cpp_info.as_owner} {iface_ani_info.from_ani_func_name}(ani_env* env, ani_object ani_obj);\n"
            f"ani_object {iface_ani_info.into_ani_func_name}(ani_env* env, {iface_cpp_info.as_owner} cpp_obj);\n"
        )
        # implementation
        iface_ani_impl_target = COutputBuffer.create(
            self.tm, f"include/{iface_ani_info.impl_header}", True
        )
        iface_ani_impl_target.include(iface_ani_info.decl_header)
        iface_ani_impl_target.include(iface_cpp_info.impl_header)
        # from ani
        iface_ani_impl_target.write(
            f"inline {iface_cpp_info.as_owner} {iface_ani_info.from_ani_func_name}(ani_env* env, ani_object ani_obj) {{\n"
            f"    struct cpp_impl_t {{\n"
            f"        ani_env* env;\n"
            f"        ani_object ref;\n"
            f"        cpp_impl_t(ani_env* env, ani_object obj) : env(env) {{\n"
            f"            env->GlobalReference_Create(obj, reinterpret_cast<ani_ref*>(&ref));\n"
            f"        }}\n"
            f"        ~cpp_impl_t() {{\n"
            f"            env->GlobalReference_Delete(ref);\n"
            f"        }}\n"
        )
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
                iface_ani_impl_target.write(
                    f"        {cpp_return_ty_name} {method_cpp_info.impl_name}({params_cpp_str}) {{\n"
                )
                args_ani = []
                for param, cpp_param_name, ani_arg_name in zip(
                    method.params, cpp_param_names, ani_arg_names, strict=False
                ):
                    type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
                    type_ani_info.into_ani(
                        iface_ani_impl_target, 8, "env", cpp_param_name, ani_arg_name
                    )
                args_ani_trailing = "".join(", " + arg_ani for arg_ani in args_ani)
                ani_result = "result_ani"
                cpp_result = "result_cpp"
                if method.return_ty_ref:
                    type_ani_info = TypeANIInfo.get(
                        self.am, method.return_ty_ref.resolved_ty
                    )
                    iface_ani_impl_target.write(
                        f"            {type_ani_info.ani_type} {ani_result};\n"
                        f'            this->env->Object_CallMethodByName_{type_ani_info.ani_type.suffix}(this->ref, "{method_ani_info.sts_name}", nullptr, reinterpret_cast<{type_ani_info.ani_type.base}*>(&{ani_result}){args_ani_trailing});\n'
                    )
                    type_ani_info.from_ani(
                        iface_ani_impl_target, 8, "env", ani_result, cpp_result
                    )
                    iface_ani_impl_target.write(f"            return {cpp_result};\n")
                else:
                    iface_ani_impl_target.write(
                        f'            this->env->Object_CallMethodByName_Void(this->ref, "{method_ani_info.sts_name}", nullptr{args_ani_trailing});\n'
                    )
                iface_ani_impl_target.write("        }\n")
        iface_ani_impl_target.write(
            f"    }};\n"
            f"    return taihe::core::make_holder<cpp_impl_t, {iface_cpp_info.as_owner}>(env, ani_obj);\n"
            f"}}\n"
        )
        # into ani
        iface_ani_impl_target.write(
            f"inline ani_object {iface_ani_info.into_ani_func_name}(ani_env* env, {iface_cpp_info.as_owner} cpp_obj) {{\n"
            f"    ani_long ani_vtbl_ptr = reinterpret_cast<ani_long>(cpp_obj.m_handle.vtbl_ptr);\n"
            f"    ani_long ani_data_ptr = reinterpret_cast<ani_long>(cpp_obj.m_handle.data_ptr);\n"
            f"    cpp_obj.m_handle.data_ptr = nullptr;\n"
            f"    ani_class ani_obj_cls;\n"
            f'    env->FindClass("{iface_ani_info.impl_desc}", &ani_obj_cls);\n'
            f"    ani_method ani_obj_ctor;\n"
            f'    env->Class_FindMethod(ani_obj_cls, "<ctor>", nullptr, &ani_obj_ctor);\n'
            f"    ani_object ani_obj;\n"
            f"    env->Object_New(ani_obj_cls, ani_obj_ctor, &ani_obj, ani_vtbl_ptr, ani_data_ptr);\n"
            f"    return ani_obj;\n"
            f"}}\n"
        )

    def gen_struct_file(
        self,
        struct: StructDecl,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_ani_info = StructANIInfo.get(self.am, struct)
        # declaration
        struct_ani_decl_target = COutputBuffer.create(
            self.tm, f"include/{struct_ani_info.decl_header}", True
        )
        struct_ani_decl_target.include("ani.h")
        struct_ani_decl_target.include(struct_cpp_info.decl_header)
        struct_ani_decl_target.write(
            f"{struct_cpp_info.as_owner} {struct_ani_info.from_ani_func_name}(ani_env* env, ani_object ani_obj);\n"
            f"ani_object {struct_ani_info.into_ani_func_name}(ani_env* env, {struct_cpp_info.as_param} cpp_obj);\n"
        )
        # implementation
        struct_ani_impl_target = COutputBuffer.create(
            self.tm, f"include/{struct_ani_info.impl_header}", True
        )
        struct_ani_impl_target.include(struct_ani_info.decl_header)
        struct_ani_impl_target.include(struct_cpp_info.impl_header)
        # from ani
        struct_ani_impl_target.write(
            f"inline {struct_cpp_info.as_owner} {struct_ani_info.from_ani_func_name}(ani_env* env, ani_object ani_obj) {{\n"
        )
        cpp_field_results = []
        for field in struct.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            ani_field_value = f"ani_field_{field.name}"
            cpp_field_result = f"cpp_field_{field.name}"
            struct_ani_impl_target.write(
                f"    {type_ani_info.ani_type} {ani_field_value};\n"
                f'    env->Object_GetPropertyByName_{type_ani_info.ani_type.suffix}(ani_obj, "{field.name}", reinterpret_cast<{type_ani_info.ani_type.base}*>(&{ani_field_value}));\n'
            )
            type_ani_info.from_ani(
                struct_ani_impl_target, 4, "env", ani_field_value, cpp_field_result
            )
            cpp_field_results.append(cpp_field_result)
        cpp_moved_fields_str = ", ".join(
            f"    std::move({cpp_field_result})"
            for cpp_field_result in cpp_field_results
        )
        struct_ani_impl_target.write(
            f"    return {struct_cpp_info.as_owner}{{{cpp_moved_fields_str}}};\n"
            f"}}\n"
        )
        # into ani
        struct_ani_impl_target.write(
            f"inline ani_object {struct_ani_info.into_ani_func_name}(ani_env* env, {struct_cpp_info.as_param} cpp_obj) {{\n"
        )
        ani_field_results = []
        for field in struct.fields:
            ani_field_result = f"ani_field_{field.name}"
            ani_field_results.append(ani_field_result)
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            type_ani_info.into_ani(
                struct_ani_impl_target,
                4,
                "env",
                f"cpp_obj.{field.name}",
                ani_field_result,
            )
        ani_field_results_trailing = "".join(
            ", " + ani_field_result for ani_field_result in ani_field_results
        )
        struct_ani_impl_target.write(
            f"    ani_class ani_obj_cls;\n"
            f'    env->FindClass("{struct_ani_info.impl_desc}", &ani_obj_cls);\n'
            f"    ani_method ani_obj_ctor;\n"
            f'    env->Class_FindMethod(ani_obj_cls, "<ctor>", nullptr, &ani_obj_ctor);\n'
            f"    ani_object ani_obj;\n"
            f"    env->Object_New(ani_obj_cls, ani_obj_ctor, &ani_obj{ani_field_results_trailing});\n"
            f"    return ani_obj;\n"
            f"}}\n"
        )

    def gen_enum_file(
        self,
        enum: EnumDecl,
    ):
        enum_cpp_info = EnumCppInfo.get(self.am, enum)
        enum_ani_info = EnumANIInfo.get(self.am, enum)
        enum_ani_decl_target = COutputBuffer.create(
            self.tm, f"include/{enum_ani_info.decl_header}", True
        )
        enum_ani_decl_target.include("ani.h")
        enum_ani_decl_target.include(enum_cpp_info.decl_header)
        enum_ani_decl_target.write(
            f"{enum_cpp_info.as_owner} {enum_ani_info.from_ani_func_name}(ani_env* env, ani_object ani_obj);\n"
            f"ani_object {enum_ani_info.into_ani_func_name}(ani_env* env, {enum_cpp_info.as_param} cpp_obj);\n"
        )
        # implementation
        enum_ani_impl_target = COutputBuffer.create(
            self.tm, f"include/{enum_ani_info.impl_header}", True
        )
        enum_ani_impl_target.include(enum_ani_info.decl_header)
        enum_ani_impl_target.include(enum_cpp_info.impl_header)
        # from ani
        enum_ani_impl_target.write(
            f"inline {enum_cpp_info.as_owner} {enum_ani_info.from_ani_func_name}(ani_env* env, ani_object ani_obj) {{\n"
            f"    ani_int ani_tag;\n"
            f'    env->Object_GetPropertyByName_Int(ani_obj, "tag", &ani_tag);\n'
            f"    ani_ref ani_value;\n"
            f'    env->Object_GetPropertyByName_Ref(ani_obj, "value", &ani_value);\n'
            f"    {enum_cpp_info.full_name}::tag_t cpp_tag = ({enum_cpp_info.full_name}::tag_t)ani_tag;\n"
            f"    switch (cpp_tag) {{\n"
        )
        for item in enum.items:
            enum_ani_impl_target.write(
                f"    case {enum_cpp_info.full_name}::tag_t::{item.name}: {{\n"
            )
            if item.ty_ref is None:
                enum_ani_impl_target.write(
                    f"        return {enum_cpp_info.full_name}::make_{item.name}();\n"
                )
            else:
                cpp_result_spec = f"cpp_item_{item.name}"
                type_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
                type_ani_info.from_ani_boxed(
                    enum_ani_impl_target,
                    8,
                    "env",
                    "ani_value",
                    cpp_result_spec,
                )
                enum_ani_impl_target.write(
                    f"        return {enum_cpp_info.full_name}::make_{item.name}(std::move({cpp_result_spec}));\n"
                )
            enum_ani_impl_target.write("    }\n")
        enum_ani_impl_target.write("    }\n" "}\n")
        # into ani
        enum_ani_impl_target.write(
            f"inline ani_object {enum_ani_info.into_ani_func_name}(ani_env* env, {enum_cpp_info.as_param} cpp_obj) {{\n"
            f"    ani_int ani_tag = (int)cpp_obj.get_tag();\n"
            f"    ani_ref ani_value;\n"
            f"    switch (cpp_obj.get_tag()) {{\n"
        )
        for item in enum.items:
            enum_ani_impl_target.write(
                f"    case {enum_cpp_info.full_name}::tag_t::{item.name}: {{\n"
            )
            if item.ty_ref is None:
                enum_ani_impl_target.write("        env->GetUndefined(&ani_value);\n")
            else:
                ani_result_spec = f"ani_item_{item.name}"
                type_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
                type_ani_info.into_ani_boxed(
                    enum_ani_impl_target,
                    8,
                    "env",
                    f"cpp_obj.get_{item.name}_ref()",
                    ani_result_spec,
                )
                enum_ani_impl_target.write(f"        ani_value = {ani_result_spec};\n")
            enum_ani_impl_target.write("        break;\n" "    }\n")
        enum_ani_impl_target.write("    }\n")
        enum_ani_impl_target.write(
            f"    ani_class ani_obj_cls;\n"
            f'    env->FindClass("{enum_ani_info.impl_desc}", &ani_obj_cls);\n'
            f"    ani_method ani_obj_ctor;\n"
            f'    env->Class_FindMethod(ani_obj_cls, "<ctor>", nullptr, &ani_obj_ctor);\n'
            f"    ani_object ani_obj;\n"
            f"    env->Object_New(ani_obj_cls, ani_obj_ctor, &ani_obj, ani_tag, ani_value);\n"
            f"    return ani_obj;\n"
            f"}}\n"
        )
