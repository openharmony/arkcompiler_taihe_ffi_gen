from abc import ABCMeta

from typing_extensions import override

from taihe.codegen.cpp_generator import (
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
    U16,
    ArrayType,
    BoxType,
    CallbackType,
    EnumType,
    IfaceType,
    MapType,
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
        self.prx_name = f"taihe_ani_proxy_{f.name}"
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
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.cls_name = f"L{pkg_ani_info.lib_name}/{self.sts_name};"


class EnumANIInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.node_parent
        assert p
        self.sts_name = d.name
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.cls_name = f"L{pkg_ani_info.lib_name}/{self.sts_name};"


class IfaceANIInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.node_parent
        assert p
        self.sts_name = d.name
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.cls_name = f"L{pkg_ani_info.lib_name}/{self.sts_name};"


class AbstractTypeANIInfo(metaclass=ABCMeta):
    ani_type_as_param: list[str]
    ani_type_as_owner: str

    def return_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        raise NotImplementedError

    def return_from_cpp_to_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        raise NotImplementedError

    def pass_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        raise NotImplementedError

    def pass_from_cpp_to_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_results: list[str],
    ):
        raise NotImplementedError

    sts_type: str
    prx_type_as_param: list[str]
    prx_type_as_owner: str

    def return_from_sts_to_prx(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_result: str,
    ):
        raise NotImplementedError

    def return_from_prx_to_sts(
        self,
        target: OutputBuffer,
        offset: int,
        prx_value: str,
        sts_result: str,
    ):
        raise NotImplementedError

    def pass_from_sts_to_prx(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        raise NotImplementedError

    def pass_from_prx_to_sts(
        self,
        target: OutputBuffer,
        offset: int,
        prx_values: list[str],
        sts_result: str,
    ):
        raise NotImplementedError

    ani_type_as_array: str

    def array_from_cpp_to_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        cpp_array_value: str,
        ani_array_result: str,
    ):
        pass

    def array_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        ani_array_value: str,
        cpp_array_buffer: str,
    ):
        pass


class StructTypeANIInfo(AbstractAnalysis[StructType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: StructType):
        self.t = t
        self.am = am
        struct_ani_info = StructANIInfo.get(am, t.ty_decl)
        self.sts_type = struct_ani_info.sts_name
        self.prx_type_as_owner = struct_ani_info.sts_name
        self.prx_type_as_param = []
        self.ani_type_as_owner = "ani_object"
        self.ani_type_as_param = []
        self.ani_type_as_array = "ani_array_ref"
        for field in t.ty_decl.fields:
            type_ani_info = TypeANIInfo.get(am, field.ty_ref.resolved_ty)
            self.prx_type_as_param.extend(type_ani_info.prx_type_as_param)
            self.ani_type_as_param.extend(type_ani_info.ani_type_as_param)

    @override
    def pass_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        moved_partial_results = []
        for i, field in enumerate(self.t.ty_decl.fields):
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            partial_result = f"{cpp_result}_{i}"
            type_ani_info.pass_from_ani_to_cpp(
                target,
                offset,
                env,
                ani_values,
                partial_result,
            )
            moved_partial_results.append(f"std::move({partial_result})")
        moved_partial_results_str = ", ".join(moved_partial_results)
        type_cpp_info = TypeCppInfo.get(self.am, self.t)
        target.write(
            f"{' ' * offset}{type_cpp_info.as_owner} {cpp_result} = {{{moved_partial_results_str}}};\n"
        )

    @override
    def pass_from_sts_to_prx(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        for field in self.t.ty_decl.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            type_ani_info.pass_from_sts_to_prx(
                target,
                offset,
                f"{sts_value}.{field.name}",
                prx_results,
            )


class EnumTypeANIInfo(AbstractAnalysis[EnumType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        enum_ani_info = EnumANIInfo.get(am, t.ty_decl)
        self.sts_type = enum_ani_info.sts_name
        self.ani_type = "ani_object"


class IfaceTypeANIInfo(AbstractAnalysis[IfaceType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        iface_ani_info = IfaceANIInfo.get(am, t.ty_decl)
        self.sts_type = iface_ani_info.sts_name
        self.ani_type = "ani_object"


class ScalarTypeANIInfo(AbstractAnalysis[ScalarType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        sts_type = {
            BOOL: "boolean",
            F32: "float",
            F64: "double",
            I8: "byte",
            I16: "short",
            I32: "int",
            I64: "long",
            U16: "char",
        }.get(t)
        if sts_type is None:
            raise ValueError
        self.sts_type = sts_type
        self.prx_type_as_param = [sts_type]
        self.prx_type_as_owner = sts_type
        self.ani_type_as_param = [f"ani_{sts_type}"]
        self.ani_type_as_owner = f"ani_{sts_type}"
        self.ani_type_as_array = f"ani_array_{sts_type}"
        self.cpp_info = TypeCppInfo.get(am, t)

    @override
    def pass_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        ani_value = ani_values.pop(0)
        target.write(
            f"{' ' * offset}{self.cpp_info.as_param} {cpp_result} = {ani_value};\n"
        )

    @override
    def pass_from_cpp_to_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_results: list[str],
    ):
        ani_result = ani_results.pop(0)
        target.write(
            f"{' ' * offset}{self.ani_type_as_param} {ani_result} = {cpp_value};\n"
        )

    @override
    def return_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        target.write(
            f"{' ' * offset}{self.ani_type_as_owner} {cpp_result} = {ani_value};\n"
        )

    @override
    def return_from_cpp_to_ani(
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
    def pass_from_prx_to_sts(
        self,
        target: OutputBuffer,
        offset: int,
        prx_values: list[str],
        sts_result: str,
    ):
        prx_value = prx_values.pop(0)
        target.write(
            f"{' ' * offset}let {sts_result}: {self.sts_type} = {prx_value};\n"
        )

    @override
    def pass_from_sts_to_prx(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        prx_result = prx_results.pop(0)
        target.write(
            f"{' ' * offset}let {prx_result}: {self.sts_type} = {sts_value};\n"
        )

    @override
    def return_from_prx_to_sts(
        self,
        target: OutputBuffer,
        offset: int,
        prx_value: str,
        sts_result: str,
    ):
        target.write(
            f"{' ' * offset}let {sts_result}: {self.sts_type} = {prx_value};\n"
        )

    @override
    def return_from_sts_to_prx(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_result: str,
    ):
        target.write(
            f"{' ' * offset}let {prx_result}: {self.sts_type} = {sts_value};\n"
        )

    @override
    def array_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        ani_array_value: str,
        cpp_array_buffer: str,
    ):
        suffix = self.sts_type[0].upper() + self.sts_type[1:]
        target.write(
            f"{' ' * offset}{env}->Array_GetRegion_{suffix}({ani_array_value}, 0, {size}, {cpp_array_buffer});\n"
        )

    @override
    def array_from_cpp_to_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        cpp_array_value: str,
        ani_array_result: str,
    ):
        suffix = self.sts_type[0].upper() + self.sts_type[1:]
        target.write(
            f"{' ' * offset}{self.ani_type_as_array} {ani_array_result};\n"
            f"{' ' * offset}{env}->Array_New_{suffix}({size}, &{ani_array_result});\n"
            f"{' ' * offset}{env}->Array_SetRegion_{suffix}({ani_array_result}, 0, {size}, {cpp_array_value});\n"
        )


class SpecialTypeANIInfo(AbstractAnalysis[StringType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: StringType):
        if t != STRING:
            raise ValueError
        self.sts_type = "string"
        self.prx_type_as_param = ["string"]
        self.prx_type_as_owner = "string"
        self.ani_type_as_param = ["ani_string"]
        self.ani_type_as_owner = "ani_string"
        self.ani_type_as_array = "ani_array_ref"
        self.cpp_info = TypeCppInfo.get(am, t)

    @override
    def pass_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        ani_value = ani_values.pop(0)
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
    def pass_from_cpp_to_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_results: list[str],
    ):
        ani_result = ani_results.pop(0)
        target.write(
            f"{' ' * offset}ani_string {ani_result};\n"
            f"{' ' * offset}{env}->String_NewUTF8({cpp_value}.c_str(), {cpp_value}.size(), &{ani_result});\n"
        )

    @override
    def return_from_ani_to_cpp(
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
    def return_from_cpp_to_ani(
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
    def pass_from_prx_to_sts(
        self,
        target: OutputBuffer,
        offset: int,
        prx_values: list[str],
        sts_result: str,
    ):
        prx_value = prx_values.pop(0)
        target.write(
            f"{' ' * offset}let {sts_result}: {self.sts_type} = {prx_value};\n"
        )

    @override
    def pass_from_sts_to_prx(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        prx_result = prx_results.pop(0)
        target.write(
            f"{' ' * offset}let {prx_result}: {self.prx_type_as_owner} = {sts_value};\n"
        )

    @override
    def return_from_prx_to_sts(
        self,
        target: OutputBuffer,
        offset: int,
        prx_value: str,
        sts_result: str,
    ):
        target.write(
            f"{' ' * offset}let {sts_result}: {self.sts_type} = {prx_value};\n"
        )

    @override
    def return_from_sts_to_prx(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_result: str,
    ):
        target.write(
            f"{' ' * offset}let {prx_result}: {self.prx_type_as_owner} = {sts_value};\n"
        )

    @override
    def array_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        ani_array_value: str,
        cpp_array_buffer: str,
    ):
        ani_value = "_str"
        length = "_len"
        tstr = "_tstr"
        buffer = "_buf"
        i = "_i"
        target.write(
            f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
            f"{' ' * offset}    ani_string {ani_value};\n"
            f"{' ' * offset}    {env}->Array_Get_Ref({ani_array_value}, {i}, reinterpret_cast<ani_ref*>(&{ani_value}));\n"
            f"{' ' * offset}    ani_size {length};\n"
            f"{' ' * offset}    {env}->String_GetUTF8Size({ani_value}, &{length});\n"
            f"{' ' * offset}    TString {tstr};\n"
            f"{' ' * offset}    char* {buffer} = tstr_initialize(&{tstr}, {length} + 1);\n"
            f"{' ' * offset}    {env}->String_GetUTF8({ani_value}, {buffer}, {length} + 1, &{length});\n"
            f"{' ' * offset}    {buffer}[{length}] = '\\0';\n"
            f"{' ' * offset}    {tstr}.length = {length};\n"
            f"{' ' * offset}    new (&{cpp_array_buffer}[{i}]) taihe::core::string({tstr});\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def array_from_cpp_to_ani(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        size: str,
        cpp_array_value: str,
        ani_array_result: str,
    ):
        ani_value = "_str"
        i = "_i"
        target.write(
            f"{' ' * offset}{self.ani_type_as_array} {ani_array_result};\n"
            f"{' ' * offset}{env}->Array_New_Ref({size}, &{ani_array_result});\n"
            f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
            f"{' ' * offset}    ani_string {ani_value};\n"
            f"{' ' * offset}    {env}->String_NewUTF8({cpp_array_value}[{i}].c_str(), {cpp_array_value}[{i}].size(), &{ani_value});\n"
            f"{' ' * offset}    {env}->Array_Set_Ref({ani_array_result}, {i}, {ani_value});\n"
            f"{' ' * offset}}}\n"
        )


class ArrayTypeANIInfo(AbstractAnalysis[ArrayType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        item_ty_ani_info = TypeANIInfo.get(am, t.item_ty)
        self.sts_type = f"({item_ty_ani_info.sts_type})[]"
        self.prx_type_as_param = [f"({item_ty_ani_info.sts_type})[]"]
        self.prx_type_as_owner = f"({item_ty_ani_info.sts_type})[]"
        self.ani_type_as_param = [item_ty_ani_info.ani_type_as_array]
        self.ani_type_as_owner = item_ty_ani_info.ani_type_as_array
        self.ani_type_as_array = "ani_array_ref"
        self.am = am
        self.t = t

    @override
    def pass_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        cpp_info = TypeCppInfo.get(self.am, self.t)
        ani_value = ani_values.pop(0)
        size = f"{cpp_result}_size"
        buffer = f"{cpp_result}_buffer"
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        target.write(
            f"{' ' * offset}size_t {size};\n"
            f"{' ' * offset}{env}->Array_GetLength({ani_value}, &{size});\n"
            f"{' ' * offset}{item_ty_cpp_info.as_owner}* {buffer} = ({item_ty_cpp_info.as_owner}*)malloc({size} * sizeof({item_ty_cpp_info.as_owner}));\n"
        )
        item_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        item_ty_ani_info.array_from_ani_to_cpp(
            target, offset, env, size, ani_value, buffer
        )
        target.write(
            f"{' ' * offset}{cpp_info.as_owner} {cpp_result}({buffer}, {size});\n"
        )

    @override
    def pass_from_sts_to_prx(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        prx_result = prx_results.pop(0)
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        if val_ty_ani_info.prx_type_as_owner == val_ty_ani_info.sts_type:
            target.write(
                f"{' ' * offset}let {prx_result}: {val_ty_ani_info.prx_type_as_owner}[] = {sts_value};\n"
            )
        else:
            target.write(
                f"{' ' * offset}let {prx_result}: {val_ty_ani_info.prx_type_as_owner}[] = new {val_ty_ani_info.prx_type_as_owner}[{sts_value}.length];\n"
                f"{' ' * offset}for (let i = 0; i < {sts_value}.length; i++) {{\n"
            )
            val_ty_ani_info.return_from_sts_to_prx(
                target, offset + 4, f"{sts_value}[i]", "item"
            )
            target.write(
                f"{' ' * offset}    {prx_result}[i] = item;\n" f"{' ' * offset}}}\n"
            )


class BoxTypeANIInfo(AbstractAnalysis[BoxType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: BoxType) -> None:
        pass


class VectorTypeANIInfo(AbstractAnalysis[VectorType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: VectorType) -> None:
        val_ty_ani_info = TypeANIInfo.get(am, t.val_ty)
        self.sts_type = f"Array<{val_ty_ani_info.sts_type}>"
        self.prx_type_as_param = [f"({val_ty_ani_info.sts_type})[]"]
        self.prx_type_as_owner = f"({val_ty_ani_info.sts_type})[]"
        self.ani_type_as_param = [val_ty_ani_info.ani_type_as_array]
        self.ani_type_as_owner = val_ty_ani_info.ani_type_as_array
        self.ani_type_as_array = "ani_array_ref"
        self.am = am
        self.t = t

    @override
    def pass_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        cpp_info = TypeCppInfo.get(self.am, self.t)
        ani_value = ani_values.pop(0)
        size = f"{cpp_result}_size"
        buffer = f"{cpp_result}_buffer"
        cpp_ty_ani_info = TypeCppInfo.get(self.am, self.t.val_ty)
        target.write(
            f"{' ' * offset}size_t {size};\n"
            f"{' ' * offset}{env}->Array_GetLength({ani_value}, &{size});\n"
            f"{' ' * offset}{cpp_ty_ani_info.as_owner}* {buffer} = ({cpp_ty_ani_info.as_owner}*)malloc({size} * sizeof({cpp_ty_ani_info.as_owner}));\n"
        )
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.val_ty)
        val_ty_ani_info.array_from_ani_to_cpp(
            target, offset, env, size, ani_value, buffer
        )
        i = "_i"
        target.write(
            f"{' ' * offset}{cpp_info.as_owner} {cpp_result}({size});\n"
            f"{' ' * offset}for (int {i} = 0; {i} < {size}; {i}++) {{\n"
            f"{' ' * offset}    {cpp_result}.emplace_back(std::move({buffer}[{i}]));\n"
            f"{' ' * offset}}}\n"
            f"{' ' * offset}free({buffer});\n"
        )

    @override
    def pass_from_sts_to_prx(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        prx_result = prx_results.pop(0)
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.val_ty)
        target.write(
            f"{' ' * offset}let {prx_result}: {val_ty_ani_info.prx_type_as_owner}[] = new {val_ty_ani_info.prx_type_as_owner}[{sts_value}.length];\n"
            f"{' ' * offset}for (let i = 0; i < {sts_value}.length; i++) {{\n"
        )
        val_ty_ani_info.return_from_sts_to_prx(
            target, offset + 4, f"{sts_value}[i]", "val"
        )
        target.write(
            f"{' ' * offset}    {prx_result}[i] = val;\n" f"{' ' * offset}}}\n"
        )


class MapTypeANIInfo(AbstractAnalysis[MapType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        val_ty_ani_info = TypeANIInfo.get(am, t.val_ty)
        self.sts_type = f"Array<{val_ty_ani_info.sts_type}>"
        self.prx_type_as_param = [f"({val_ty_ani_info.sts_type})[]"]
        self.prx_type_as_owner = f"({val_ty_ani_info.sts_type})[]"
        self.ani_type_as_param = [val_ty_ani_info.ani_type_as_array]
        self.ani_type_as_owner = val_ty_ani_info.ani_type_as_array
        self.ani_type_as_array = "ani_array_ref"
        self.am = am
        self.t = t

    @override
    def pass_from_ani_to_cpp(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        cpp_info = TypeCppInfo.get(self.am, self.t)
        ani_value = ani_values.pop(0)
        size = f"{cpp_result}_size"
        buffer = f"{cpp_result}_buffer"
        cpp_ty_ani_info = TypeCppInfo.get(self.am, self.t.val_ty)
        target.write(
            f"{' ' * offset}size_t {size};\n"
            f"{' ' * offset}{env}->Array_GetLength({ani_value}, &{size});\n"
            f"{' ' * offset}{cpp_ty_ani_info.as_owner}* {buffer} = ({cpp_ty_ani_info.as_owner}*)malloc({size} * sizeof({cpp_ty_ani_info.as_owner}));\n"
        )
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.val_ty)
        val_ty_ani_info.array_from_ani_to_cpp(
            target, offset, env, size, ani_value, buffer
        )
        i = "_i"
        target.write(
            f"{' ' * offset}{cpp_info.as_owner} {cpp_result}({size});\n"
            f"{' ' * offset}for (int {i} = 0; {i} < {size}; {i}++) {{\n"
            f"{' ' * offset}    {cpp_result}.emplace_back(std::move({buffer}[{i}]));\n"
            f"{' ' * offset}}}\n"
            f"{' ' * offset}free({buffer});\n"
        )

    @override
    def pass_from_sts_to_prx(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        prx_result = prx_results.pop(0)
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.val_ty)
        target.write(
            f"{' ' * offset}let {prx_result}: {val_ty_ani_info.prx_type_as_owner}[] = new {val_ty_ani_info.prx_type_as_owner}[{sts_value}.length];\n"
            f"{' ' * offset}for (let i = 0; i < {sts_value}.length; i++) {{\n"
        )
        val_ty_ani_info.return_from_sts_to_prx(
            target, offset + 4, f"{sts_value}[i]", "val"
        )
        target.write(
            f"{' ' * offset}    {prx_result}[i] = val;\n" f"{' ' * offset}}}\n"
        )


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
        return SpecialTypeANIInfo.get(self.am, t)

    @override
    def visit_array_type(self, t: ArrayType) -> AbstractTypeANIInfo:
        return ArrayTypeANIInfo.get(self.am, t)

    @override
    def visit_box_type(self, t: BoxType) -> AbstractTypeANIInfo:
        return BoxTypeANIInfo.get(self.am, t)

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
        pkg_sts_target = OutputBuffer.create(self.tm, f"{pkg_ani_info.sts}")
        pkg_sts_target.write(f'loadLibrary("{pkg_ani_info.lib_name}");\n')
        for func in pkg.functions:
            self.gen_func_proxy(func, pkg_sts_target)
        for func in pkg.functions:
            self.gen_func_impl(func, pkg_sts_target)

    def gen_func_proxy(
        self,
        func: GlobFuncDecl,
        pkg_sts_target: OutputBuffer,
    ):
        func_ani_info = GlobFuncANIInfo.get(self.am, func)
        params_prx = []
        for param in func.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            for i, prx_type in enumerate(type_ani_info.prx_type_as_param):
                param_prx = f"{param.name}_proxy_{i}"
                params_prx.append(f"{param_prx}: {prx_type}")
        params_prx_str = ", ".join(params_prx)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            pxy_return_ty_name = type_ani_info.prx_type_as_owner
        else:
            pxy_return_ty_name = "void"
        pkg_sts_target.write(
            f"native function {func_ani_info.prx_name}({params_prx_str}): {pxy_return_ty_name};\n"
        )

    def gen_func_impl(
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
            f"function {func_ani_info.sts_name}({params_sts_str}): {sts_return_ty_name} {{\n"
        )
        params_prx = []
        for param in func.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            param_prx_results = []
            for i, prx_type in enumerate(type_ani_info.prx_type_as_param):
                param_prx = f"{param.name}_proxy_{i}"
                param_prx_results.append(param_prx)
                params_prx.append(param_prx)
            type_ani_info.pass_from_sts_to_prx(
                pkg_sts_target, 4, param.name, param_prx_results
            )
        params_prx_str = ", ".join(params_prx)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            result_prx_value = "result_proxy"
            result_sts_result = "result"
            pkg_sts_target.write(
                f"    let {result_prx_value} = {func_ani_info.prx_name}({params_prx_str});\n"
            )
            type_ani_info.return_from_prx_to_sts(
                pkg_sts_target, 4, result_prx_value, result_sts_result
            )
            pkg_sts_target.write(f"    return {result_sts_result};\n")
        else:
            pkg_sts_target.write(f"    {func_ani_info.prx_name}({params_prx_str});\n")
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
        pkg_ani_target = COutputBuffer.create(self.tm, f"{pkg_ani_info.src}", False)
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
                f'        {{"{func_ani_info.prx_name}", nullptr, reinterpret_cast<void*>({func_ani_info.mangled_name})}},\n'
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
        params_values_list = []
        for param in func.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            param_ani_values = []
            for i, ani_type in enumerate(type_ani_info.ani_type_as_param):
                param_ani = f"{param.name}_proxy_{i}"
                param_ani_values.append(param_ani)
                params_ani.append(f"{ani_type} {param_ani}")
            params_values_list.append(param_ani_values)
        params_ani_str = ", ".join(params_ani)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            ani_return_ty_name = type_ani_info.ani_type_as_owner
        else:
            ani_return_ty_name = "void"
        pkg_ani_target.write(
            f"static {ani_return_ty_name} {func_ani_info.mangled_name}({params_ani_str}) {{\n"
        )
        args_cpp = []
        for param, param_ani_values in zip(func.params, params_values_list):
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            type_ani_info.pass_from_ani_to_cpp(
                pkg_ani_target, 4, "env", param_ani_values, param.name
            )
            args_cpp.append(param.name)
        args_cpp_str = ", ".join(args_cpp)
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            cpp_return_ty_name = type_cpp_info.as_owner
            result_cpp_value = "result"
            result_ani_result = "result_proxy"
            pkg_ani_target.write(
                f"    {cpp_return_ty_name} {result_cpp_value} = {func_cpp_info.full_name}({args_cpp_str});\n"
            )
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            type_ani_info.return_from_cpp_to_ani(
                pkg_ani_target, 4, "env", result_cpp_value, result_ani_result
            )
            pkg_ani_target.write(f"    return {result_ani_result};\n")
        else:
            pkg_ani_target.write(
                f"    {func_cpp_info.full_name}({args_cpp_str});\n" f"    return;\n"
            )
        pkg_ani_target.write("}\n")
