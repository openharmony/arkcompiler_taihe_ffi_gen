import re
from abc import ABCMeta
from json import dumps
from typing import TYPE_CHECKING, Optional

from typing_extensions import override

from taihe.codegen.abi_generator import (
    IfaceABIInfo,
)
from taihe.codegen.cpp_generator import (
    CallbackTypeCppInfo,
    EnumCppInfo,
    GlobFuncCppInfo,
    IfaceCppInfo,
    IfaceMethodCppInfo,
    PackageCppInfo,
    StructCppInfo,
    TypeCppInfo,
    UnionCppInfo,
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
    UnionDecl,
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
    CallbackType,
    EnumType,
    IfaceType,
    MapType,
    OpaqueType,
    OptionalType,
    ScalarType,
    # SetType,
    StringType,
    StructType,
    Type,
    # VectorType,
    # CallbackType,
    UnionType,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import COutputBuffer, OutputBuffer, OutputManager

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        ParamDecl,
    )


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
ANI_ENUM_ITEM = ANIType(hint="enum_item", base=ANI_REF)
ANI_STRING = ANIType(hint="string", base=ANI_REF)
ANI_ARRAYBUFFER = ANIType(hint="arraybuffer", base=ANI_REF)


class PackageANIInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        self.header = f"{p.name}.ani.hpp"
        self.source = f"{p.name}.ani.cpp"

        self.namespace = "::".join(p.segments)

        # TODO: hack at
        assert p.loc
        self.sts = f"{p.loc.file.pkg_name}.ets"
        self.pkg_name = "/".join(p.loc.file.pkg_name.split("."))
        self.impl_desc = f"L{self.pkg_name}/ETSGLOBAL;"

        self.is_namespace = False
        if "namespace" in p.attrs:
            self.is_namespace = True
            self.ns_impl_desc = f"L{self.pkg_name};"


class GlobFuncANIInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        p = f.node_parent
        assert p
        segments = [*p.segments, f.name]
        self.mangled_name = encode(segments, DeclKind.ANI_FUNC)

        self.sts_native_name = f"{f.name}_inner"
        self.sts_on = False
        self.sts_off = False

        if static_name_attr := f.attrs.get("sts_name"):
            self.gen_global = static_name_attr.value
        else:
            self.gen_global = f.name

        if static_name_attr := f.attrs.get("static_method"):
            self.gen_static = static_name_attr.value
            self.gen_global = None
        else:
            self.gen_static = None

        if ctor_attr := f.attrs.get("ctor"):
            self.gen_ctor = ctor_attr.value
            self.gen_global = None
        else:
            self.gen_ctor = None

        if sts_async_attr := f.attrs.get("gen_async"):
            self.sts_async_name = sts_async_attr.value
        else:
            self.sts_async_name = None

        if sts_promise_attr := f.attrs.get("gen_promise"):
            self.sts_promise_name = sts_promise_attr.value
        else:
            self.sts_promise_name = None

        if sts_onoff_type := f.attrs.get("onoff"):
            assert f.name.startswith("on") or f.name.startswith("off")
            if f.name.startswith("on"):
                self.sts_on = True
            elif f.name.startswith("off"):
                self.sts_off = True
            if sts_onoff_type.value is None:
                onoff_type = re.sub(r"^(on|off)", "", f.name)
                if onoff_type:  # guaranteed to be non-empty
                    onoff_type = onoff_type[0].lower() + onoff_type[1:]
                self.sts_onoff_type = onoff_type
            else:
                self.sts_onoff_type = sts_onoff_type.value
        else:
            self.sts_onoff_type = None

        self.sts_real_params: list[ParamDecl] = []
        self.sts_native_args: list[str] = []
        for param in f.params:
            self.sts_real_params.append(param)
            self.sts_native_args.append(param.name)


class IfaceMethodANIInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, f: IfaceMethodDecl) -> None:
        d = f.node_parent
        assert d
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name, f.name]
        self.mangled_name = encode(segments, DeclKind.ANI_FUNC)
        self.sts_on = False
        self.sts_off = False

        self.sts_native_name = f"{f.name}_inner"

        if sts_name_attr := f.attrs.get("sts_name"):
            self.gen_method = sts_name_attr.value
        else:
            self.gen_method = f.name

        if sts_async_attr := f.attrs.get("gen_async"):
            self.sts_async_name = sts_async_attr.value
        else:
            self.sts_async_name = None

        if sts_promise_attr := f.attrs.get("gen_promise"):
            self.sts_promise_name = sts_promise_attr.value
        else:
            self.sts_promise_name = None

        self.gen_getter = None
        if (
            (getter_attr := f.attrs.get("getter"))
            and len(f.attrs) == 1
            and (getter_field := getter_attr.value)
        ):
            self.gen_getter = getter_field
            self.gen_method = None

        self.gen_setter = None
        if (
            (setter_attr := f.attrs.get("setter"))
            and len(f.attrs) == 1
            and (setter_field := setter_attr.value)
        ):
            self.gen_setter = setter_field
            self.gen_method = None

        if sts_onoff_type := f.attrs.get("onoff"):
            assert f.name.startswith("on") or f.name.startswith("off")
            if f.name.startswith("on"):
                self.sts_on = True
            elif f.name.startswith("off"):
                self.sts_off = True
            if sts_onoff_type.value is None:
                onoff_type = re.sub(r"^(on|off)", "", f.name)
                if onoff_type:  # guaranteed to be non-empty
                    onoff_type = onoff_type[0].lower() + onoff_type[1:]
                self.sts_onoff_type = onoff_type
            else:
                self.sts_onoff_type = sts_onoff_type.value
        else:
            self.sts_onoff_type = None

        self.sts_real_params: list[ParamDecl] = []
        self.sts_native_args: list[str] = []
        for param in f.params:
            if param.attrs.get("sts_this"):
                self.sts_native_args.append("this")
                continue
            if sts_member_attr := param.attrs.get("sts_member"):
                self.sts_native_args.append(f"this.{sts_member_attr.value}")
                continue
            self.sts_real_params.append(param)
            self.sts_native_args.append(param.name)


class EnumANIInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: UnionDecl) -> None:
        p = d.node_parent
        assert p
        self.sts_type = d.name
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.type_desc = f"L{pkg_ani_info.pkg_name}/{self.sts_type};"


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


class UnionANIInfo(AbstractAnalysis[UnionDecl]):
    def __init__(self, am: AnalysisManager, d: UnionDecl) -> None:
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name]
        self.from_ani_func_name = encode(segments, DeclKind.FROM_ANI)
        self.into_ani_func_name = encode(segments, DeclKind.INTO_ANI)
        self.decl_header = f"{p.name}.{d.name}.ani.0.h"
        self.impl_header = f"{p.name}.{d.name}.ani.1.h"


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
        if d.attrs.get("class"):
            self.sts_impl = f"{d.name}"
            self.is_calss = True
        else:
            self.sts_impl = f"{d.name}_inner"
            self.is_calss = False
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

    @property
    def type_desc_boxed(self) -> str:
        if self.ani_type.base == ANI_REF:
            return self.type_desc
        else:
            return f"Lstd/core/{self.ani_type.suffix};"

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
                f"{' ' * offset}    {env}->Class_FindMethod({ani_class}, \"<ctor>\", \"{self.type_desc}:V\", &{ani_ctor});\n"
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


class EnumTypeANIInfo(AbstractAnalysis[EnumType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        AbstractTypeANIInfo.__init__(self, am, t)
        self.t = t
        self.am = am
        enum_ani_info = EnumANIInfo.get(am, t.ty_decl)
        self.ani_type = ANI_ENUM_ITEM
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
        ani_index = f"{cpp_result}_ani"
        enum_cpp_info = EnumCppInfo.get(self.am, self.t.ty_decl)
        target.write(
            f"{' ' * offset}ani_size {ani_index};\n"
            f"{' ' * offset}{env}->EnumItem_GetIndex({ani_value}, &{ani_index});\n"
            f"{' ' * offset}{enum_cpp_info.full_name} {cpp_result}(({enum_cpp_info.full_name}::key_t){ani_index});\n"
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
        cls = f"{ani_result}_cls"
        target.write(
            f"{' ' * offset}ani_enum {cls};\n"
            f"{' ' * offset}{env}->FindEnum(\"{self.type_desc}\", &{cls});\n"
            f"{' ' * offset}ani_enum_item {ani_result};\n"
            f"{' ' * offset}{env}->Enum_GetEnumItemByIndex({cls}, (ani_size){cpp_value}.get_key(), &{ani_result});\n"
        )


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


class UnionTypeANIInfo(AbstractAnalysis[UnionType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: UnionType):
        AbstractTypeANIInfo.__init__(self, am, t)
        self.t = t
        self.am = am
        self.ani_type = ANI_REF
        sts_value_types = []
        for field in t.ty_decl.fields:
            if field.ty_ref is None:
                sts_value_types.append("undefined")
                continue
            ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            sts_value_types.append(f"{ty_ani_info.sts_type}")
        sts_value_types_str = " | ".join(sts_value_types)
        self.sts_type = f"({sts_value_types_str})"
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
        union_ani_info = UnionANIInfo.get(self.am, self.t.ty_decl)
        target.include(union_ani_info.impl_header)
        target.write(
            f"{' ' * offset}{self.cpp_info.as_owner} {cpp_result} = {union_ani_info.from_ani_func_name}({env}, {ani_value});\n"
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
        union_ani_info = UnionANIInfo.get(self.am, self.t.ty_decl)
        target.include(union_ani_info.impl_header)
        target.write(
            f"{' ' * offset}ani_ref {ani_result} = {union_ani_info.into_ani_func_name}({env}, {cpp_value});\n"
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
        self.ani_type = ANI_REF
        self.sts_type = "NullishType"
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


class ArrayBufferTypeANIInfo(AbstractAnalysis[ArrayType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)
        self.ani_type = ANI_ARRAYBUFFER
        self.sts_type = "ArrayBuffer"
        self.type_desc = "Lescompat/ArrayBuffer;"
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
        data_ptr = f"{cpp_result}_data"
        length = f"{cpp_result}_length"
        target.write(
            f"{' ' * offset}void* {data_ptr} = nullptr;\n"
            f"{' ' * offset}size_t {length} = 0;\n"
            f"{' ' * offset}{env}->ArrayBuffer_GetInfo(reinterpret_cast<ani_arraybuffer>({ani_value}), &{data_ptr}, &{length});\n"
        )
        target.write(
            f"{' ' * offset}taihe::core::array_view<uint8_t> {cpp_result}(reinterpret_cast<uint8_t*>({data_ptr}), {length});\n"
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
        data_ptr = f"{ani_result}_data"
        target.write(
            f"{' ' * offset}void* {data_ptr} = nullptr;\n"
            f"{' ' * offset}ani_arraybuffer {ani_result};\n"
            f"{' ' * offset}{env}->CreateArrayBuffer({cpp_value}.size(), &{data_ptr}, &{ani_result});\n"
        )
        target.write(
            f"{' ' * offset}memcpy({data_ptr}, {cpp_value}.data(), {cpp_value}.size());\n"
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


class MapTypeANIInfo(AbstractAnalysis[MapType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)
        key_ty_ani_info = TypeANIInfo.get(am, t.key_ty)
        val_ty_ani_info = TypeANIInfo.get(am, t.val_ty)
        self.ani_type = ANI_OBJECT
        self.sts_type = (
            f"Record<{key_ty_ani_info.sts_type}, {val_ty_ani_info.sts_type}>"
        )
        self.type_desc = "Lescompat/Record;"
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
        ani_ref_keys = f"{cpp_result}_keys"
        ani_key_value = f"{cpp_result}_key"
        ani_value_obj = f"{cpp_result}_val"
        key_ty_ani_info = TypeANIInfo.get(self.am, self.t.key_ty)
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.val_ty)
        target.write(
            f"{' ' * offset}ani_ref {ani_ref_keys};\n"
            f"{' ' * offset}{env}->Object_CallMethodByName_Ref({ani_value}, \"keys\", nullptr, &{ani_ref_keys});\n"
            f"{' ' * offset}{cpp_info.as_owner} {cpp_result};\n"
            f"{' ' * offset}while (true) {{\n"
            f"{' ' * offset}    ani_ref next;\n"
            f"{' ' * offset}    ani_boolean done;\n"
            f"{' ' * offset}    {env}->Object_CallMethodByName_Ref(static_cast<ani_object>({ani_ref_keys}), \"next\", nullptr, &next);\n"
            f"{' ' * offset}    {env}->Object_GetFieldByName_Boolean(static_cast<ani_object>(next), \"done\", &done);\n"
            f"{' ' * offset}    if (done) break;\n"
            f"{' ' * offset}    ani_ref {ani_key_value};\n"
            f"{' ' * offset}    {env}->Object_GetFieldByName_Ref(static_cast<ani_object>(next), \"value\", &{ani_key_value});\n"
            f"{' ' * offset}    ani_ref {ani_value_obj};\n"
            f"{' ' * offset}    {env}->Object_CallMethodByName_Ref({ani_value}, \"$_get\", nullptr, &{ani_value_obj}, {ani_key_value});\n"
        )
        key_cpp_spec = f"{cpp_result}_key_spec"
        val_cpp_spec = f"{cpp_result}_val_spec"
        key_ty_ani_info.from_ani_boxed(
            target, offset + 4, env, ani_key_value, key_cpp_spec
        )
        val_ty_ani_info.from_ani_boxed(
            target, offset + 4, env, ani_value_obj, val_cpp_spec
        )
        target.write(
            f"{' ' * offset}    {cpp_result}.emplace({key_cpp_spec}, {val_cpp_spec});\n"
            f"{' ' * offset}}}\n"
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
        key_ty_cpp_info = TypeCppInfo.get(self.am, self.t.key_ty)
        val_ty_cpp_info = TypeCppInfo.get(self.am, self.t.val_ty)
        key_ty_ani_info = TypeANIInfo.get(self.am, self.t.key_ty)
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.val_ty)
        ani_class = f"{ani_result}_class"
        ani_method = f"{ani_result}_method"
        cpp_key = f"{ani_result}_key"
        cpp_val = f"{ani_result}_val"
        target.write(
            f"{' ' * offset}ani_class {ani_class};\n"
            f"{' ' * offset}{env}->FindClass(\"{self.type_desc}\", &{ani_class});\n"
            f"{' ' * offset}ani_method {ani_method};\n"
            f"{' ' * offset}{env}->Class_FindMethod({ani_class}, \"<ctor>\", nullptr, &{ani_method});\n"
            f"{' ' * offset}ani_object {ani_result};\n"
            f"{' ' * offset}{env}->Object_New({ani_class}, {ani_method}, &{ani_result});\n"
            f"{' ' * offset}{cpp_value}.accept([=]({key_ty_cpp_info.as_param} {cpp_key}, {val_ty_cpp_info.as_param} {cpp_val}) {{\n"
        )
        key_ani_spec = f"{ani_result}_key_spec"
        val_ani_spec = f"{ani_result}_val_spec"
        key_ty_ani_info.into_ani_boxed(target, offset + 4, env, cpp_key, key_ani_spec)
        val_ty_ani_info.into_ani_boxed(target, offset + 4, env, cpp_val, val_ani_spec)
        target.write(
            f"{' ' * offset}    env->Object_CallMethodByName_Void({ani_result}, \"$_set\", nullptr, {key_ani_spec}, {val_ani_spec});\n"
            f"{' ' * offset}}});\n"
        )


# class SetTypeANIInfo(AbstractAnalysis[SetType], AbstractTypeANIInfo):
#     def __init__(self, am: AnalysisManager, t: SetType) -> None:
#         pass


class CallbackTypeANIInfo(AbstractAnalysis[CallbackType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: CallbackType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)
        self.ani_type = ANI_OBJECT
        self.am = am
        self.t = t
        params_ty_sts = []
        for index, param_ty in enumerate(self.t.params_ty):
            param_ty_sts_info = TypeANIInfo.get(self.am, param_ty)
            params_ty_sts.append(f"arg_{index}: {param_ty_sts_info.sts_type}")
        params_ty_sts_str = ", ".join(params_ty_sts)
        if self.t.return_ty:
            return_ty_sts_info = TypeANIInfo.get(self.am, self.t.return_ty)
            return_ty_sts = return_ty_sts_info.sts_type
        else:
            return_ty_sts = "void"
        self.sts_type = f"({params_ty_sts_str})=>{return_ty_sts}"
        self.type_desc = f"Lstd/core/Function{len(self.t.params_ty)};"

    @override
    def from_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        cb_cpp_info = CallbackTypeCppInfo.get(self.am, self.t)
        params_ty_as_param = []
        for index, param_ty in enumerate(self.t.params_ty):
            cpp_arg = f"cpp_arg_{index}"
            param_ty_cpp_info = TypeCppInfo.get(self.am, param_ty)
            params_ty_as_param.append(f"{param_ty_cpp_info.as_param} {cpp_arg}")
        params_str = ", ".join(params_ty_as_param)

        if self.t.return_ty:
            return_ty_cpp_info = TypeCppInfo.get(self.am, self.t.return_ty)
            return_ty_as_owner = return_ty_cpp_info.as_owner
        else:
            return_ty_as_owner = "void"

        target.write(
            f"{' ' * offset}struct cpp_impl_cb {{\n"
            f"{' ' * offset}    ani_env* env;\n"
            f"{' ' * offset}    ani_object cb_obj;\n"
            f"{' ' * offset}    cpp_impl_cb(ani_env* env, ani_object obj): env(env) {{\n"
            f"{' ' * offset}        env->GlobalReference_Create(obj, reinterpret_cast<ani_ref*>(&cb_obj));\n"
            f"{' ' * offset}    }}\n"
            f"{' ' * offset}    ~cpp_impl_cb() {{\n"
            f"{' ' * offset}        env->GlobalReference_Delete(cb_obj);\n"
            f"{' ' * offset}    }}\n"
            f"{' ' * offset}    {return_ty_as_owner} operator()({params_str}) {{\n"
        )
        cpp_args_boxed = []
        for index, param_ty in enumerate(self.t.params_ty):
            param_ty_ani_info = TypeANIInfo.get(self.am, param_ty)
            cpp_arg = f"cpp_arg_{index}"
            ani_arg = f"ani_arg_{index}"
            param_ty_ani_info.into_ani_boxed(target, offset + 8, env, cpp_arg, ani_arg)
            cpp_args_boxed.append(ani_arg)
        cpp_args_boxed_str = ", ".join(cpp_args_boxed)

        if self.t.params_ty:
            target.write(
                f"{' ' * offset}        ani_ref cb_argv[] = {{{cpp_args_boxed_str}}};\n"
            )
            cb_argv = "cb_argv"
        else:
            cb_argv = "nullptr"
        target.write(
            f"{' ' * offset}        ani_ref cb_result;\n"
            f"{' ' * offset}        this->env->FunctionalObject_Call(static_cast<ani_fn_object>(this->cb_obj), {len(cpp_args_boxed)}, {cb_argv}, &cb_result);\n"
        )

        if self.t.return_ty:
            return_ty_ani_info = TypeANIInfo.get(self.am, self.t.return_ty)
            return_ty_ani_info.from_ani_boxed(
                target, offset + 8, env, "cb_result", "cpp_cb_result"
            )
            target.write(f"{' ' * offset}        return cpp_cb_result;\n")
        else:
            target.write(f"{' ' * offset}        return;\n")

        target.write(
            f"{' ' * offset}    }}\n"
            f"{' ' * offset}}};\n"
            f"{' ' * offset}auto {cpp_result} = {cb_cpp_info.as_owner}::from<cpp_impl_cb>({env}, {ani_value});\n"
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
        target.write(f"{' ' * offset}ani_object {ani_result};\n")


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
    def visit_union_type(self, t: UnionType) -> AbstractTypeANIInfo:
        return UnionTypeANIInfo.get(self.am, t)

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
        if t.item_ty == U8:
            return ArrayBufferTypeANIInfo.get(self.am, t)
        else:
            return ArrayTypeANIInfo.get(self.am, t)

    @override
    def visit_optional_type(self, t: OptionalType) -> AbstractTypeANIInfo:
        return OptionalTypeANIInfo.get(self.am, t)

    @override
    def visit_opaque_type(self, t: OpaqueType) -> AbstractTypeANIInfo:
        return OpaqueTypeANIInfo.get(self.am, t)

    # @override
    # def visit_vector_type(self, t: VectorType) -> AbstractTypeANIInfo:
    #     return VectorTypeANIInfo.get(self.am, t)

    @override
    def visit_map_type(self, t: MapType) -> AbstractTypeANIInfo:
        return MapTypeANIInfo.get(self.am, t)

    # @override
    # def visit_set_type(self, t: SetType) -> AbstractTypeANIInfo:
    #     return SetTypeANIInfo.get(self.am, t)

    @override
    def visit_callback_type(self, t: CallbackType) -> AbstractTypeANIInfo:
        return CallbackTypeANIInfo.get(self.am, t)


class Namespace:
    def __init__(self, name: str):
        self.name: str = name
        self.children_namespaces: dict[str, Namespace] = {}
        self.cur_pkg: Optional[PackageDecl] = None

    def add_path(self, path_parts: list[str], pkg: PackageDecl):
        if not path_parts:
            self.cur_pkg = pkg
            return
        head, *tail = path_parts
        child = self.children_namespaces.setdefault(head, Namespace(head))
        child.add_path(tail, pkg)

    def display(self, level=0):
        # This function use to test NsTreeNode
        print(f"{'  ' * level}{self.name} : {self.cur_pkg if self.cur_pkg else ''}")
        for child in self.children_namespaces.values():
            child.display(level + 1)


class NsTree:
    def __init__(self, root_name: str):
        self.root = Namespace(root_name)

    def add(self, path: str, pkg_name: PackageDecl):
        parts = path.split(".")
        self.root.add_path(parts, pkg_name)

    def display(self):
        self.root.display()


class STSCodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am
        self.ns_tree_list: dict[str, NsTree] = {}
        self.generated_pkg_list: list[PackageDecl] = []

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            if "namespace" in pkg.attrs:
                attr_item = pkg.attrs["namespace"]
                root_pkg = attr_item.value[0]
                if root_pkg not in self.ns_tree_list:
                    self.ns_tree_list.setdefault(root_pkg, NsTree(root_pkg))
                self.ns_tree_list[root_pkg].add(attr_item.value[1], pkg)
            else:
                continue

        for pkg in pg.packages:
            self.gen_ns_package_file(pkg)

        for pkg in pg.packages:
            self.gen_normal_package_file(pkg)

    def gen_ns_package_file(self, pkg: PackageDecl):
        pkg_ani_info = PackageANIInfo.get(self.am, pkg)
        pkg_sts_target = OutputBuffer.create(self.tm, pkg_ani_info.sts)
        pkg_sts_target.indent_manager.level = -1

        if pkg.name in self.ns_tree_list:
            cur_ns_tree = self.ns_tree_list[pkg.name].root
            self.gen_namespace(cur_ns_tree, pkg_sts_target)

    def gen_normal_package_file(self, pkg: PackageDecl):
        pkg_ani_info = PackageANIInfo.get(self.am, pkg)
        pkg_sts_target = OutputBuffer.create(self.tm, pkg_ani_info.sts)

        if pkg not in self.generated_pkg_list:
            self.gen_package_types(pkg, pkg_sts_target)

    def gen_namespace(
        self,
        cur_ns: Namespace,
        pkg_sts_target: OutputBuffer,
    ):
        pkg = cur_ns.cur_pkg
        if pkg:
            pkg_sts_target.write(f"export namespace {cur_ns.name} {{\n")
            with pkg_sts_target.indent_manager.code_block():
                self.gen_package_types(pkg, pkg_sts_target)

        with pkg_sts_target.indent_manager.code_block():
            for child in cur_ns.children_namespaces.values():
                self.gen_namespace(child, pkg_sts_target)

        if pkg:
            pkg_sts_target.write(f"}}\n")

    def gen_package_types(
        self,
        pkg: PackageDecl,
        pkg_sts_target: OutputBuffer,
    ):
        self.generated_pkg_list.append(pkg)
        # pkg_sts_target.write(f'loadLibrary("{self.lib_name}");\n')

        static_methods: dict[str, list[tuple[str, GlobFuncDecl]]] = {}
        construct_methods: dict[str, list[GlobFuncDecl]] = {}
        on_param_map: dict[str, list[GlobFuncDecl]] = {}
        off_param_map: dict[str, list[GlobFuncDecl]] = {}

        for func in pkg.functions:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            if value := func_ani_info.gen_static:
                class_name, func_name = value
                if class_name not in static_methods:
                    static_methods[class_name] = []
                static_methods[class_name].append((func_name, func))

            if class_name := func_ani_info.gen_ctor:
                if class_name not in construct_methods:
                    construct_methods[class_name] = []
                construct_methods[class_name].append(func)

        for iface in pkg.interfaces:
            self.gen_iface_inner(
                iface, pkg_sts_target, static_methods, construct_methods
            )

        for iface in pkg.interfaces:
            self.gen_iface_interface(iface, pkg_sts_target)

        for enum in pkg.enums:
            self.gen_enum(enum, pkg_sts_target)
        for struct in pkg.structs:
            self.gen_struct(struct, pkg_sts_target)
        for union in pkg.unions:
            self.gen_union(union, pkg_sts_target)

        for func in pkg.functions:
            self.gen_func(func, pkg_sts_target)

        callback_flag = 0
        for iface in pkg.interfaces:
            for method in iface.methods:
                if method.attrs.get("gen_async"):
                    callback_flag = 1
        for func in pkg.functions:
            if func.attrs.get("gen_async"):
                callback_flag = 1

        # on/off
        for func in pkg.functions:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            if func_ani_info.sts_onoff_type:
                if func_ani_info.sts_on:
                    params_key = self.get_type_str(func)
                    on_param_map.setdefault(params_key, []).append(func)
                elif func_ani_info.sts_off:
                    params_key = self.get_type_str(func)
                    off_param_map.setdefault(params_key, []).append(func)

        for _, value in on_param_map.items():
            self.gen_onoff_func("on", value, pkg_sts_target)

        for _, value in off_param_map.items():
            self.gen_onoff_func("off", value, pkg_sts_target)

        if callback_flag:
            pkg_sts_target.write(
                f"export type AsyncCallback<T> = (err: Error, data?: T) => void;\n"
            )

    def get_type_str(
        self,
        func: GlobFuncDecl | IfaceMethodDecl,
    ) -> str:
        param_type_str = ""
        params = func.params
        for param in params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            param_type_str += type_ani_info.sts_type
        return param_type_str

    def gen_onoff_func(
        self,
        onoroff: str,
        func_list: list[GlobFuncDecl],
        pkg_sts_target: OutputBuffer,
    ):
        sts_real_params = []
        args_list = []
        params = func_list[0].params
        needAsync = 0
        async_func_list = []
        sts_real_params.append("type: string")
        for index, param in enumerate(params):
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            sts_real_params.append(f"arg{index}: {type_ani_info.sts_type}")
            args_list.append(f"arg{index}")
        sts_real_params_str = ", ".join(sts_real_params)
        args_str = ", ".join(args_list)
        if return_ty_ref := func_list[0].return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            sts_return_ty_name = type_ani_info.sts_type
        else:
            sts_return_ty_name = "void"

        pkg_sts_target.write(
            f"export function {onoroff}({sts_real_params_str}): void {{\n"
            f"    switch(type) {{"
        )
        for func in func_list:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            if func_ani_info.sts_async_name is not None:
                async_func_list.append(func)
                needAsync += 1

            pkg_sts_target.write(
                f'        case "{func_ani_info.sts_onoff_type}": {func_ani_info.sts_native_name}({args_str}); break;\n'
            )

        pkg_sts_target.write(
            f"        default: throw new Error(`Unknown type: ${type}`);\n"
            f"    }}\n"
            f"}}\n"
        )

        if needAsync == 0:
            return

        sts_real_params.append(f"callback: AsyncCallback<{sts_return_ty_name}>")
        sts_real_params_async_str = ", ".join(sts_real_params)
        args_list.append("callback")
        args_async_str = ", ".join(args_list)

        pkg_sts_target.write(
            f"export function {onoroff}({sts_real_params_async_str}): void {{\n"
            f"    switch(type) {{"
        )

        for func in func_list:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            if async_func_name := func_ani_info.sts_async_name:
                pkg_sts_target.write(
                    f'        case "{func_ani_info.sts_onoff_type}": {async_func_name}({args_async_str}); break;\n'
                )

        pkg_sts_target.write(f"    }}\n" f"}}\n")

    def gen_onoff_method(
        self,
        onoroff: str,
        method_list: list[IfaceMethodDecl],
        pkg_sts_target: OutputBuffer,
    ):
        sts_real_params = []
        args_list = []
        params = method_list[0].params
        needAsync = 0
        async_method_list = []
        sts_real_params.append("type: string")
        for index, param in enumerate(params):
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            sts_real_params.append(f"arg{index}: {type_ani_info.sts_type}")
            args_list.append(f"arg{index}")
        sts_real_params_str = ", ".join(sts_real_params)
        args_str = ", ".join(args_list)
        if return_ty_ref := method_list[0].return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            sts_return_ty_name = type_ani_info.sts_type
        else:
            sts_return_ty_name = "void"

        pkg_sts_target.write(
            f"    {onoroff}({sts_real_params_str}): void {{\n"
            f"        switch(type) {{"
        )

        for method in method_list:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            if method_ani_info.sts_async_name is not None:
                async_method_list.append(method)
                needAsync += 1

            pkg_sts_target.write(
                f'            case "{method_ani_info.sts_onoff_type}": this.{method_ani_info.sts_native_name}({args_str}); break;\n'
            )

        pkg_sts_target.write(
            f"            default: throw new Error(`Unknown type: ${type}`);\n"
            f"        }}\n"
            f"    }}\n"
        )

        if needAsync == 0:
            return

        sts_real_params.append(f"callback: AsyncCallback<{sts_return_ty_name}>")
        sts_real_params_async_str = ", ".join(sts_real_params)
        args_list.append("callback")
        args_async_str = ", ".join(args_list)

        pkg_sts_target.write(
            f"    {onoroff}({sts_real_params_async_str}): void {{\n"
            f"        switch(type) {{"
        )

        for method in method_list:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            if async_func_name := method_ani_info.sts_async_name:
                pkg_sts_target.write(
                    f'            case "{method_ani_info.sts_onoff_type}": this.{async_func_name}({args_async_str}); break;\n'
                )

        pkg_sts_target.write(f"        }}\n" f"    }}\n")

    def gen_onoff_method_decl(
        self,
        onoroff: str,
        method_list: list[IfaceMethodDecl],
        pkg_sts_target: OutputBuffer,
    ):
        sts_real_params = []
        args_list = []
        params = method_list[0].params
        needAsync = 0
        async_method_list = []
        sts_real_params.append("type: string")
        for index, param in enumerate(params):
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            sts_real_params.append(f"arg{index}: {type_ani_info.sts_type}")
            args_list.append(f"arg{index}")
        sts_real_params_str = ", ".join(sts_real_params)
        if return_ty_ref := method_list[0].return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            sts_return_ty_name = type_ani_info.sts_type
        else:
            sts_return_ty_name = "void"

        pkg_sts_target.write(f"    {onoroff}({sts_real_params_str}): void;\n")

        for method in method_list:
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            if method_ani_info.sts_async_name is not None:
                async_method_list.append(method)
                needAsync += 1

        if needAsync == 0:
            return

        sts_real_params.append(f"callback: AsyncCallback<{sts_return_ty_name}>")
        sts_real_params_async_str = ", ".join(sts_real_params)
        args_list.append("callback")

        pkg_sts_target.write(f"    {onoroff}({sts_real_params_async_str}): void;\n")

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_sts_target: OutputBuffer,
    ):
        # docstring
        if (inject_attr := func.attrs.get("inject")) is not None:
            pkg_sts_target.write(inject_attr.value)
        func_ani_info = GlobFuncANIInfo.get(self.am, func)
        # native
        sts_native_params = []
        for param in func.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            sts_native_params.append(f"{param.name}: {type_ani_info.sts_type}")
        sts_native_params_str = ", ".join(sts_native_params)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            sts_return_ty_name = type_ani_info.sts_type
        else:
            sts_return_ty_name = "void"
        pkg_sts_target.write(
            f"native function {func_ani_info.sts_native_name}({sts_native_params_str}): {sts_return_ty_name};\n"
        )
        if func_ani_info.gen_global is None:
            return
        # real
        sts_real_params = []
        for sts_real_param in func_ani_info.sts_real_params:
            type_ani_info = TypeANIInfo.get(self.am, sts_real_param.ty_ref.resolved_ty)
            sts_real_params.append(f"{sts_real_param.name}: {type_ani_info.sts_type}")
        sts_real_params_str = ", ".join(sts_real_params)
        sts_native_args_str = ", ".join(func_ani_info.sts_native_args)
        pkg_sts_target.write(
            f"export function {func_ani_info.gen_global}({sts_real_params_str}): {sts_return_ty_name} {{\n"
            f"    return {func_ani_info.sts_native_name}({sts_native_args_str});\n"
            f"}}\n"
        )
        # async
        if (async_func_name := func_ani_info.sts_async_name) is not None:
            callback = f"callback: AsyncCallback<{sts_return_ty_name}>"
            sts_real_params_with_cb = [*sts_real_params, callback]
            sts_real_params_with_cb_str = ", ".join(sts_real_params_with_cb)
            pkg_sts_target.write(
                f"export function {async_func_name}({sts_real_params_with_cb_str}): void {{\n"
                f"    (launch {func_ani_info.sts_native_name}({sts_native_args_str}))\n"
            )
            if sts_return_ty_name == "void":
                pkg_sts_target.write(
                    f"    .then((): void => {{\n"
                    f"        let error = new Error();\n"
                    f"        callback(error);\n"
                    f"    }})\n"
                )
            else:
                pkg_sts_target.write(
                    f"    .then((ret: NullishType) => {{\n"
                    f"            let retInner = ret as {sts_return_ty_name};\n"
                    f"            let error = new Error();\n"
                    f"            callback(error, retInner);\n"
                    f"    }})\n"
                )
            pkg_sts_target.write(
                f"    .catch((ret: NullishType) => {{\n"
                f"        let retError = ret as Error;\n"
                f"        callback(retError);\n"
                f"    }});\n"
                f"}}\n"
            )
        # promise
        if (promise_func_name := func_ani_info.sts_promise_name) is not None:
            pkg_sts_target.write(
                f"export function {promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}> {{\n"
                f"    return launch {func_ani_info.sts_native_name}({sts_native_args_str});\n"
                f"}}\n"
            )

    def gen_struct(
        self,
        struct: StructDecl,
        pkg_sts_target: OutputBuffer,
    ):
        # docstring
        if (inject_attr := struct.attrs.get("inject")) is not None:
            pkg_sts_target.write(inject_attr.value)
        struct_ani_info = StructANIInfo.get(self.am, struct)
        pkg_sts_target.write(f"export class {struct_ani_info.sts_impl} {{\n")
        for field in struct.fields:
            ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            pkg_sts_target.write(f"    {field.name}: {ty_ani_info.sts_type};\n")
        pkg_sts_target.write(f"    constructor(\n")
        for field in struct.fields:
            ty_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            pkg_sts_target.write(f"        {field.name}: {ty_ani_info.sts_type},\n")
        pkg_sts_target.write(f"    ) {{\n")
        for field in struct.fields:
            pkg_sts_target.write(f"        this.{field.name} = {field.name};\n")
        pkg_sts_target.write(f"    }}\n" f"}}\n")

    def gen_enum(
        self,
        enum: EnumDecl,
        pkg_sts_target: OutputBuffer,
    ):
        # docstring
        if (inject_attr := enum.attrs.get("inject")) is not None:
            pkg_sts_target.write(inject_attr.value)
        enum_ani_info = EnumANIInfo.get(self.am, enum)
        pkg_sts_target.write(f"export enum {enum_ani_info.sts_type} {{\n")
        for item in enum.items:
            pkg_sts_target.write(f"    {item.name} = {dumps(item.value)},\n")
        pkg_sts_target.write(f"}}\n")

    def gen_union(
        self,
        union: UnionDecl,
        pkg_sts_target: OutputBuffer,
    ):
        # docstring
        if (inject_attr := union.attrs.get("inject")) is not None:
            pkg_sts_target.write(inject_attr.value)

    def gen_iface_interface(
        self,
        iface: IfaceDecl,
        pkg_sts_target: OutputBuffer,
    ):
        # docstring
        on_param_map: dict[str, list[IfaceMethodDecl]] = {}
        off_param_map: dict[str, list[IfaceMethodDecl]] = {}

        if (inject_attr := iface.attrs.get("inject")) is not None:
            pkg_sts_target.write(inject_attr.value)
        iface_ani_info = IfaceANIInfo.get(self.am, iface)
        if iface_ani_info.is_calss:
            return
        pkg_sts_target.write(f"export interface {iface_ani_info.sts_type} {{\n")
        for method in iface.methods:
            # docstring
            if (inject_attr := method.attrs.get("inject")) is not None:
                pkg_sts_target.write(inject_attr.value)
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            sts_real_params = []
            for sts_real_param in method_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(
                    self.am, sts_real_param.ty_ref.resolved_ty
                )
                sts_real_params.append(
                    f"{sts_real_param.name}: {type_ani_info.sts_type}"
                )
            sts_real_params_str = ", ".join(sts_real_params)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            # getter
            if getter_field := method_ani_info.gen_getter:
                pkg_sts_target.write(
                    f"    get {getter_field}({sts_real_params_str}): {sts_return_ty_name};\n"
                )
            # setter
            if setter_field := method_ani_info.gen_setter:
                pkg_sts_target.write(
                    f"    set {setter_field}({sts_real_params_str});\n"
                )
            # real
            if real_method := method_ani_info.gen_method:
                pkg_sts_target.write(
                    f"    {real_method}({sts_real_params_str}): {sts_return_ty_name};\n"
                )
            # async
            if (async_func_name := method_ani_info.sts_async_name) is not None:
                callback = f"callback: AsyncCallback<{sts_return_ty_name}>"
                sts_real_params_with_cb = [*sts_real_params, callback]
                sts_real_params_with_cb_str = ", ".join(sts_real_params_with_cb)
                pkg_sts_target.write(
                    f"    {async_func_name}({sts_real_params_with_cb_str}): void;\n"
                )
            # promise
            if (promise_func_name := method_ani_info.sts_promise_name) is not None:
                pkg_sts_target.write(
                    f"    {promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}>;\n"
                )
            # on/off
            if method_ani_info.sts_onoff_type:
                if method_ani_info.sts_on:
                    params_key = self.get_type_str(method)
                    on_param_map.setdefault(params_key, []).append(method)
                elif method_ani_info.sts_off:
                    params_key = self.get_type_str(method)
                    off_param_map.setdefault(params_key, []).append(method)

        for _, value in on_param_map.items():
            self.gen_onoff_method_decl("on", value, pkg_sts_target)
        for _, value in off_param_map.items():
            self.gen_onoff_method_decl("off", value, pkg_sts_target)

        pkg_sts_target.write(f"}}\n")

    def gen_iface_inner(
        self,
        iface: IfaceDecl,
        pkg_sts_target: OutputBuffer,
        static_methods: dict[str, list[tuple[str, GlobFuncDecl]]],
        construct_methods: dict[str, list[GlobFuncDecl]],
    ):
        on_param_map: dict[str, list[IfaceMethodDecl]] = {}
        off_param_map: dict[str, list[IfaceMethodDecl]] = {}

        iface_ani_info = IfaceANIInfo.get(self.am, iface)
        if iface_ani_info.is_calss:
            pkg_sts_target.write(f"export class {iface_ani_info.sts_impl} {{\n")
        else:
            pkg_sts_target.write(
                f"class {iface_ani_info.sts_impl} implements {iface_ani_info.sts_type} {{\n"
            )
        pkg_sts_target.write(
            f"    private _vtbl_ptr: long;\n"
            f"    private _data_ptr: long;\n"
            f"    private constructor(_vtbl_ptr: long, _data_ptr: long) {{\n"
            f"        this._vtbl_ptr = _vtbl_ptr;\n"
            f"        this._data_ptr = _data_ptr;\n"
            f"    }}\n"
        )
        for method in iface.methods:
            if (inject_attr := method.attrs.get("class_inject")) is not None:
                pkg_sts_target.write(inject_attr.value)
            method_ani_info = IfaceMethodANIInfo.get(self.am, method)
            # native
            sts_native_params = []
            for param in method.params:
                type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
                sts_native_params.append(f"{param.name}: {type_ani_info.sts_type}")
            sts_native_params_str = ", ".join(sts_native_params)
            if return_ty_ref := method.return_ty_ref:
                type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
                sts_return_ty_name = type_ani_info.sts_type
            else:
                sts_return_ty_name = "void"
            pkg_sts_target.write(
                f"    native {method_ani_info.sts_native_name}({sts_native_params_str}): {sts_return_ty_name};\n"
            )
            sts_real_params = []
            for sts_real_param in method_ani_info.sts_real_params:
                type_ani_info = TypeANIInfo.get(
                    self.am, sts_real_param.ty_ref.resolved_ty
                )
                sts_real_params.append(
                    f"{sts_real_param.name}: {type_ani_info.sts_type}"
                )
            sts_real_params_str = ", ".join(sts_real_params)
            sts_native_args_str = ", ".join(method_ani_info.sts_native_args)
            # getter
            if getter_field := method_ani_info.gen_getter:
                pkg_sts_target.write(
                    f"    get {getter_field}({sts_real_params_str}): {sts_return_ty_name} {{\n"
                    f"        return this.{method_ani_info.sts_native_name}({sts_native_args_str});\n"
                    f"    }}\n"
                )
            # setter
            if setter_field := method_ani_info.gen_setter:
                pkg_sts_target.write(
                    f"    set {setter_field}({sts_real_params_str}) {{\n"
                    f"        this.{method_ani_info.sts_native_name}({sts_native_args_str});\n"
                    f"    }}\n"
                )
            # real
            if real_method := method_ani_info.gen_method:
                pkg_sts_target.write(
                    f"    {real_method}({sts_real_params_str}): {sts_return_ty_name} {{\n"
                    f"        return this.{method_ani_info.sts_native_name}({sts_native_args_str});\n"
                    f"    }}\n"
                )
            # async
            if (async_func_name := method_ani_info.sts_async_name) is not None:
                callback = f"callback: AsyncCallback<{sts_return_ty_name}>"
                sts_real_params_with_cb = [*sts_real_params, callback]
                sts_real_params_with_cb_str = ", ".join(sts_real_params_with_cb)
                pkg_sts_target.write(
                    f"    {async_func_name}({sts_real_params_with_cb_str}): void {{\n"
                    f"        (launch this.{method_ani_info.sts_native_name}({sts_native_args_str}))\n"
                )
                if sts_return_ty_name == "void":
                    pkg_sts_target.write(
                        f"        .then((): void => {{\n"
                        f"            let error = new Error();\n"
                        f"            callback(error);\n"
                        f"        }})\n"
                    )
                else:
                    pkg_sts_target.write(
                        f"        .then((ret: NullishType) => {{\n"
                        f"            let retInner = ret as {sts_return_ty_name};\n"
                        f"            let error = new Error();\n"
                        f"            callback(error, retInner);\n"
                        f"        }})\n"
                    )
                pkg_sts_target.write(
                    f"        .catch((ret: NullishType) => {{\n"
                    f"            let retError = ret as Error;\n"
                    f"            callback(retError);\n"
                    f"        }});\n"
                    f"    }}\n"
                )
            # promise
            if (promise_func_name := method_ani_info.sts_promise_name) is not None:
                pkg_sts_target.write(
                    f"    {promise_func_name}({sts_native_params_str}): Promise<{sts_return_ty_name}> {{\n"
                    f"        return launch this.{method_ani_info.sts_native_name}({sts_native_args_str});\n"
                    f"    }}\n"
                )

            # on/off
            if method_ani_info.sts_onoff_type:
                if method_ani_info.sts_on:
                    params_key = self.get_type_str(method)
                    on_param_map.setdefault(params_key, []).append(method)
                elif method_ani_info.sts_off:
                    params_key = self.get_type_str(method)
                    off_param_map.setdefault(params_key, []).append(method)

        for _, value in on_param_map.items():
            self.gen_onoff_method("on", value, pkg_sts_target)

        for _, value in off_param_map.items():
            self.gen_onoff_method("off", value, pkg_sts_target)

        if iface_ani_info.is_calss:
            for func in construct_methods.get(iface.name, []):
                self.gen_class_ctor(func, pkg_sts_target)

            for static_method_name, func in static_methods.get(iface.name, []):
                self.gen_class_static_method(static_method_name, func, pkg_sts_target)

        pkg_sts_target.write(f"}}\n")

    def gen_class_ctor(self, func: GlobFuncDecl, pkg_sts_target: OutputBuffer):
        func_ani_info = GlobFuncANIInfo.get(self.am, func)
        sts_real_params = []
        for sts_real_param in func_ani_info.sts_real_params:
            type_ani_info = TypeANIInfo.get(self.am, sts_real_param.ty_ref.resolved_ty)
            sts_real_params.append(f"{sts_real_param.name}: {type_ani_info.sts_type}")
        sts_real_params_str = ", ".join(sts_real_params)
        sts_native_args_str = ", ".join(func_ani_info.sts_native_args)
        pkg_sts_target.write(
            f"    constructor({sts_real_params_str}) {{\n"
            f"        let temp = {func_ani_info.sts_native_name}({sts_native_args_str});\n"
            f"        this._data_ptr = temp._data_ptr;\n"
            f"        this._vtbl_ptr = temp._vtbl_ptr;\n"
            f"    }}\n"
        )

    def gen_class_static_method(
        self, static_method_name: str, func: GlobFuncDecl, pkg_sts_target: OutputBuffer
    ):
        func_ani_info = GlobFuncANIInfo.get(self.am, func)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            sts_return_ty_name = type_ani_info.sts_type
        else:
            sts_return_ty_name = "void"
        sts_real_params = []
        for sts_real_param in func_ani_info.sts_real_params:
            type_ani_info = TypeANIInfo.get(self.am, sts_real_param.ty_ref.resolved_ty)
            sts_real_params.append(f"{sts_real_param.name}: {type_ani_info.sts_type}")
        sts_real_params_str = ", ".join(sts_real_params)
        sts_native_args_str = ", ".join(func_ani_info.sts_native_args)
        pkg_sts_target.write(
            f"    static {static_method_name}({sts_real_params_str}): {sts_return_ty_name} {{\n"
            f"        return {func_ani_info.sts_native_name}({sts_native_args_str});\n"
            f"    }}\n"
        )
        if (async_func_name := func_ani_info.sts_async_name) is not None:
            callback = f"callback: AsyncCallback<{sts_return_ty_name}>"
            sts_real_params_with_cb = [*sts_real_params, callback]
            sts_real_params_with_cb_str = ", ".join(sts_real_params_with_cb)
            pkg_sts_target.write(
                f"    static {async_func_name}({sts_real_params_with_cb_str}): void {{\n"
                f"        (launch {func_ani_info.sts_native_name}({sts_native_args_str}))\n"
            )
            if sts_return_ty_name == "void":
                pkg_sts_target.write(
                    f"        .then((): void => {{\n"
                    f"            let error = new Error();\n"
                    f"            callback(error);\n"
                    f"        }})\n"
                )
            else:
                pkg_sts_target.write(
                    f"        .then((ret: NullishType) => {{\n"
                    f"                let retInner = ret as {sts_return_ty_name};\n"
                    f"                let error = new Error();\n"
                    f"                callback(error, retInner);\n"
                    f"        }})\n"
                )
            pkg_sts_target.write(
                f"        .catch((ret: NullishType) => {{\n"
                f"            let retError = ret as Error;\n"
                f"            callback(retError);\n"
                f"        }});\n"
                f"    }}\n"
            )
        # promise
        if (promise_func_name := func_ani_info.sts_promise_name) is not None:
            pkg_sts_target.write(
                f"    static {promise_func_name}({sts_real_params_str}): Promise<{sts_return_ty_name}> {{\n"
                f"        return launch {func_ani_info.sts_native_name}({sts_native_args_str});\n"
                f"    }}\n"
            )


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
            f"ANI_EXPORT ani_status ANI_Constructor(ani_vm *vm, uint32_t *result) {{\n"
            f"    ani_env *env;\n"
            f"    if (ANI_OK != vm->GetEnv(ANI_VERSION_1, &env)) {{\n"
            f"        return ANI_ERROR;\n"
            f"    }}\n"
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
            f"    *result = ANI_VERSION_1;\n" f"    return ANI_OK;\n" f"}}\n"
        )

    def gen_package(self, pkg: PackageDecl):
        for iface in pkg.interfaces:
            self.gen_iface_file(iface)
        for struct in pkg.structs:
            self.gen_struct_file(struct)
        for union in pkg.unions:
            self.gen_union_file(union)
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
            self.gen_func(func, pkg_ani_source_target, pkg_ani_info.is_namespace)
        for iface in pkg.interfaces:
            for method in iface.methods:
                self.gen_method(iface, method, pkg_ani_source_target)
        # register infos
        register_infos: list[tuple[str, list[tuple[str, str]], bool]] = []
        impl_desc = (
            pkg_ani_info.ns_impl_desc
            if pkg_ani_info.is_namespace
            else pkg_ani_info.impl_desc
        )
        func_infos = []
        for func in pkg.functions:
            glob_func_info = GlobFuncANIInfo.get(self.am, func)
            sts_native_name = glob_func_info.sts_native_name
            mangled_name = glob_func_info.mangled_name
            func_infos.append((sts_native_name, mangled_name))
        register_infos.append((impl_desc, func_infos, pkg_ani_info.is_namespace))
        for iface in pkg.interfaces:
            iface_ani_info = IfaceANIInfo.get(self.am, iface)
            impl_desc = iface_ani_info.impl_desc
            func_infos = []
            for method in iface.methods:
                method_ani_info = IfaceMethodANIInfo.get(self.am, method)
                sts_native_name = method_ani_info.sts_native_name
                mangled_name = method_ani_info.mangled_name
                func_infos.append((sts_native_name, mangled_name))
            register_infos.append((impl_desc, func_infos, False))
        pkg_ani_source_target.write(
            f"namespace {pkg_ani_info.namespace} {{\n"
            f"ani_status ANIRegister(ani_env *env) {{\n"
        )
        for impl_desc, func_infos, is_namespace in register_infos:
            if is_namespace:
                ani_type = "ani_namespace"
                ani_find_func = "FindNamespace"
                ani_bind_func = "Namespace_BindNativeFunctions"
            else:
                ani_type = "ani_class"
                ani_find_func = "FindClass"
                ani_bind_func = "Class_BindNativeMethods"
            pkg_ani_source_target.write(
                f"    {{\n"
                f"        {ani_type} ani_env;\n"
                f'        if (ANI_OK != env->{ani_find_func}("{impl_desc}", &ani_env)) {{\n'
                f"            return ANI_ERROR;\n"
                f"        }}\n"
                f"        ani_native_function methods[] = {{\n"
            )
            for sts_native_name, mangled_name in func_infos:
                pkg_ani_source_target.write(
                    f'            {{"{sts_native_name}", nullptr, reinterpret_cast<void*>({mangled_name})}},\n'
                )

            pkg_ani_source_target.write(
                f"        }};\n"
                f"        if (ANI_OK != env->{ani_bind_func}(ani_env, methods, sizeof(methods) / sizeof(ani_native_function))) {{\n"
                f"            return ANI_ERROR;\n"
                f"        }}\n"
                f"    }}\n"
            )
        pkg_ani_source_target.write(f"    return ANI_OK;\n" f"}}\n" f"}}\n")

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_ani_source_target: COutputBuffer,
        is_namespace: bool,
    ):
        func_ani_info = GlobFuncANIInfo.get(self.am, func)
        func_cpp_info = GlobFuncCppInfo.get(self.am, func)
        if is_namespace:
            params_ani = [
                "[[maybe_unused]] ani_env *env",
            ]
        else:
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
        pkg_ani_source_target.write(f"}}\n")

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
        pkg_ani_source_target.write(f"}}\n")

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
                    args_ani.append(ani_arg_name)
                args_ani_trailing = "".join(", " + arg_ani for arg_ani in args_ani)
                ani_result = "result_ani"
                cpp_result = "result_cpp"
                if method.return_ty_ref:
                    type_ani_info = TypeANIInfo.get(
                        self.am, method.return_ty_ref.resolved_ty
                    )
                    iface_ani_impl_target.write(
                        f"            {type_ani_info.ani_type} {ani_result};\n"
                        f'            this->env->Object_CallMethodByName_{type_ani_info.ani_type.suffix}(this->ref, "{method_ani_info.sts_native_name}", nullptr, reinterpret_cast<{type_ani_info.ani_type.base}*>(&{ani_result}){args_ani_trailing});\n'
                    )
                    type_ani_info.from_ani(
                        iface_ani_impl_target, 8, "env", ani_result, cpp_result
                    )
                    iface_ani_impl_target.write(f"            return {cpp_result};\n")
                else:
                    iface_ani_impl_target.write(
                        f'            this->env->Object_CallMethodByName_Void(this->ref, "{method_ani_info.sts_native_name}", nullptr{args_ani_trailing});\n'
                    )
                iface_ani_impl_target.write(f"        }}\n")
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

    def gen_union_file(
        self,
        union: UnionDecl,
    ):
        union_cpp_info = UnionCppInfo.get(self.am, union)
        union_ani_info = UnionANIInfo.get(self.am, union)
        union_ani_decl_target = COutputBuffer.create(
            self.tm, f"include/{union_ani_info.decl_header}", True
        )
        union_ani_decl_target.include("ani.h")
        union_ani_decl_target.include(union_cpp_info.decl_header)
        union_ani_decl_target.write(
            f"{union_cpp_info.as_owner} {union_ani_info.from_ani_func_name}(ani_env* env, ani_ref ani_obj);\n"
            f"ani_ref {union_ani_info.into_ani_func_name}(ani_env* env, {union_cpp_info.as_param} cpp_obj);\n"
        )
        # implementation
        union_ani_impl_target = COutputBuffer.create(
            self.tm, f"include/{union_ani_info.impl_header}", True
        )
        union_ani_impl_target.include(union_ani_info.decl_header)
        union_ani_impl_target.include(union_cpp_info.impl_header)
        # from ani
        union_ani_impl_target.write(
            f"inline {union_cpp_info.as_owner} {union_ani_info.from_ani_func_name}(ani_env* env, ani_ref ani_value) {{\n"
        )
        for field in union.fields:
            is_field = f"is_{field.name}"
            union_ani_impl_target.write(f"    ani_boolean {is_field};\n")
            if field.ty_ref is None:
                union_ani_impl_target.write(
                    f"    env->Reference_IsUndefined(ani_value, &{is_field});\n"
                    f"    if ({is_field}) {{\n"
                    f"        return {union_cpp_info.full_name}::make_{field.name}();\n"
                    f"    }}\n"
                )
            else:
                type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
                filed_class = f"{field.name}_cls"
                union_ani_impl_target.write(
                    f"    ani_class {filed_class};\n"
                    f'    env->FindClass("{type_ani_info.type_desc_boxed}", &{filed_class});\n'
                    f"    env->Object_InstanceOf((ani_object)ani_value, {filed_class}, &{is_field});\n"
                    f"    if ({is_field}) {{\n"
                )
                cpp_result_spec = f"cpp_field_{field.name}"
                type_ani_info.from_ani_boxed(
                    union_ani_impl_target,
                    8,
                    "env",
                    "ani_value",
                    cpp_result_spec,
                )
                union_ani_impl_target.write(
                    f"        return {union_cpp_info.full_name}::make_{field.name}(std::move({cpp_result_spec}));\n"
                    f"    }}\n"
                )
        union_ani_impl_target.write(f"}}\n")
        # into ani
        union_ani_impl_target.write(
            f"inline ani_ref {union_ani_info.into_ani_func_name}(ani_env* env, {union_cpp_info.as_param} cpp_value) {{\n"
            f"    ani_ref ani_value;\n"
            f"    switch (cpp_value.get_tag()) {{\n"
        )
        for field in union.fields:
            union_ani_impl_target.write(
                f"    case {union_cpp_info.full_name}::tag_t::{field.name}: {{\n"
            )
            if field.ty_ref is None:
                union_ani_impl_target.write(f"        env->GetUndefined(&ani_value);\n")
            else:
                ani_result_spec = f"ani_field_{field.name}"
                type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
                type_ani_info.into_ani_boxed(
                    union_ani_impl_target,
                    8,
                    "env",
                    f"cpp_value.get_{field.name}_ref()",
                    ani_result_spec,
                )
                union_ani_impl_target.write(f"        ani_value = {ani_result_spec};\n")
            union_ani_impl_target.write(f"        break;\n" f"    }}\n")
        union_ani_impl_target.write(f"    }}\n")
        union_ani_impl_target.write(f"    return ani_value;\n" f"}}\n")
