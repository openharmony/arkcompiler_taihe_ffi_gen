from abc import ABCMeta

from typing_extensions import override

from taihe.codegen.cpp_generator import (
    GlobFuncCppInfo,
    PackageCppInfo,
    TypeCppInfo,
    EnumCppInfo,
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
    OptionalType,
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
    ani_split_suff: list[str]
    ani_split_base: list[str]
    ani_split_type: list[str]
    ani_whole_suff: str
    ani_whole_base: str
    ani_whole_type: str

    def from_ani_whole(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    def into_ani_whole(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    def from_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    def into_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_results: list[str],
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    sts_type: str
    prx_split_type: list[str]
    prx_whole_type: str

    def into_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_result: str,
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    def from_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        prx_value: str,
        sts_result: str,
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    def into_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    def from_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        prx_values: list[str],
        sts_result: str,
    ):
        raise NotImplementedError(f"from class {self.__class__.__name__}")

    ani_array_type: str

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
        self.prx_split_type = []
        self.ani_split_type = []
        self.ani_split_suff = []
        self.ani_split_base = []
        for field in t.ty_decl.fields:
            type_ani_info = TypeANIInfo.get(am, field.ty_ref.resolved_ty)
            self.prx_split_type.extend(type_ani_info.prx_split_type)
            self.ani_split_type.extend(type_ani_info.ani_split_type)
            self.ani_split_base.extend(type_ani_info.ani_split_base)
            self.ani_split_suff.extend(type_ani_info.ani_split_suff)
        self.prx_whole_type = struct_ani_info.prx_name
        self.ani_whole_type = "ani_object"
        self.ani_whole_base = "ani_ref"
        self.ani_whole_suff = "Ref"
        self.ani_array_type = "ani_array_ref"
        self.flat_field_names = [f"_{i}" for i in range(len(self.prx_split_type))]

    @override
    def from_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        cpp_moved_partial_results = []
        for i, field in enumerate(self.t.ty_decl.fields):
            cpp_partial_result = f"{cpp_result}_field_{i}"
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            type_ani_info.from_ani_split(
                target,
                offset,
                env,
                ani_values,
                cpp_partial_result,
            )
            cpp_moved_partial_results.append(f"std::move({cpp_partial_result})")
        moved_partial_results_str = ", ".join(cpp_moved_partial_results)
        type_cpp_info = TypeCppInfo.get(self.am, self.t)
        target.write(
            f"{' ' * offset}{type_cpp_info.as_owner} {cpp_result} = {{{moved_partial_results_str}}};\n"
        )

    @override
    def from_ani_whole(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        struct_ani_info = StructANIInfo.get(self.am, self.t.ty_decl)
        ani_value_cls = f"{cpp_result}_cls"
        target.write(
            f"{' ' * offset}static ani_class {ani_value_cls} = [=] {{\n"
            f"{' ' * offset}    ani_class {ani_value_cls};\n"
            f"{' ' * offset}    {env}->FindClass(\"{struct_ani_info.cls_name}\", &{ani_value_cls});\n"
            f"{' ' * offset}    return {ani_value_cls};\n"
            f"{' ' * offset}}}();\n"
        )
        ani_values = []
        for i, (ani_type, ani_base, ani_suff, field_name) in enumerate(
            zip(
                self.ani_split_type,
                self.ani_split_base,
                self.ani_split_suff,
                self.flat_field_names,
            )
        ):
            ani_item = f"{cpp_result}_item_{i}"
            ani_field = f"{ani_item}_field"
            target.write(
                f"{' ' * offset}static ani_field {ani_field} = [=] {{\n"
                f"{' ' * offset}    ani_field {ani_field};\n"
                f"{' ' * offset}    {env}->Class_FindField({ani_value_cls}, \"{field_name}\", &{ani_field});\n"
                f"{' ' * offset}    return {ani_field};\n"
                f"{' ' * offset}}}();\n"
                f"{' ' * offset}{ani_type} {ani_item};\n"
                f"{' ' * offset}{env}->Object_GetField_{ani_suff}({ani_value}, {ani_field}, reinterpret_cast<{ani_base}*>(&{ani_item}));\n"
            )
            ani_values.append(ani_item)
        self.from_ani_split(target, offset, env, ani_values, cpp_result)

    @override
    def into_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_results: list[str],
    ):
        for i, field in enumerate(self.t.ty_decl.fields):
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            type_ani_info.into_ani_split(
                target, offset, env, f"{cpp_value}.{field.name}", ani_results
            )

    @override
    def into_ani_whole(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        ani_results = []
        ani_args = []
        for i, ani_type in enumerate(self.ani_split_type):
            ani_arg = f"{ani_result}_{i}"
            ani_results.append(ani_arg)
            ani_args.append(ani_arg)
        ani_args_str = ", ".join(ani_args)
        self.into_ani_split(target, offset, env, cpp_value, ani_results)
        struct_ani_info = StructANIInfo.get(self.am, self.t.ty_decl)
        ani_result_cls = f"{ani_result}_cls"
        ani_result_ctor = f"{ani_result}_ctor"
        target.write(
            f"{' ' * offset}static ani_class {ani_result_cls} = [=] {{\n"
            f"{' ' * offset}    ani_class {ani_result_cls};\n"
            f"{' ' * offset}    {env}->FindClass(\"{struct_ani_info.cls_name}\", &{ani_result_cls});\n"
            f"{' ' * offset}    return {ani_result_cls};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}static ani_method {ani_result_ctor} = [=] {{\n"
            f"{' ' * offset}    ani_method {ani_result_ctor};\n"
            f"{' ' * offset}    {env}->Class_FindMethod({ani_result_cls}, \"<ctor>\", nullptr, &{ani_result_ctor});\n"
            f"{' ' * offset}    return {ani_result_ctor};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}ani_object {ani_result};\n"
            f"{' ' * offset}{env}->Object_New({ani_result_cls}, {ani_result_ctor}, &{ani_result}, {ani_args_str});\n"
        )

    @override
    def into_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        for field in self.t.ty_decl.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            type_ani_info.into_prx_split(
                target, offset, f"{sts_value}.{field.name}", prx_results
            )

    @override
    def into_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_result: str,
    ):
        prx_results = []
        prx_parts = []
        for i, prx_type in enumerate(self.prx_split_type):
            prx_part = f"{prx_result}_{i}"
            prx_results.append(prx_part)
            prx_parts.append(prx_part)
        prx_parts_str = ", ".join(prx_parts)
        self.into_prx_split(target, offset, sts_value, prx_results)
        struct_ani_info = StructANIInfo.get(self.am, self.t.ty_decl)
        target.write(
            f"{' ' * offset}let {prx_result}: {self.prx_whole_type} = new {struct_ani_info.prx_name}({prx_parts_str});\n"
        )

    @override
    def from_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        prx_values: list[str],
        sts_result: str,
    ):
        sts_fields = []
        for field in self.t.ty_decl.fields:
            sts_field = f"{sts_result}_{field.name}"
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            type_ani_info.from_prx_split(target, offset, prx_values, sts_field)
            sts_fields.append(sts_field)
        sts_fields_str = ", ".join(sts_fields)
        struct_ani_info = StructANIInfo.get(self.am, self.t.ty_decl)
        target.write(
            f"{' ' * offset}let {sts_result}: {self.sts_type} = new {struct_ani_info.sts_ctor}({sts_fields_str});\n"
        )

    @override
    def from_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        prx_value: str,
        sts_result: str,
    ):
        prx_values = []
        for i, field_name in enumerate(self.flat_field_names):
            prx_values.append(f"{prx_value}.{field_name}")
        self.from_prx_split(target, offset, prx_values, sts_result)

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
            f"{' ' * offset}    {self.ani_whole_type} {ani_value};\n"
            f"{' ' * offset}    {env}->Array_Get_Ref({ani_array_value}, {i}, reinterpret_cast<ani_ref*>(&{ani_value}));\n"
        )
        self.from_ani_whole(target, offset + 4, env, ani_value, cpp_result)
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
            f"{' ' * offset}static ani_class {ani_class} = [=] {{\n"
            f"{' ' * offset}    ani_class {ani_class};\n"
            f"{' ' * offset}    {env}->FindClass(\"{struct_ani_info.cls_name}\", &{ani_class});\n"
            f"{' ' * offset}    return {ani_class};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}ani_ref undefined;\n"
            f"{' ' * offset}{env}->GetUndefined(&undefined);\n"
            f"{' ' * offset}{env}->Array_New_Ref({ani_class}, {size}, undefined, &{ani_array_result});\n"
            f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
        )
        self.into_ani_whole(
            target, offset + 4, env, f"{cpp_array_value}[{i}]", ani_result
        )
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
        ani_temp = f"{ani_result}_temp"
        self.into_ani_whole(target, offset, env, cpp_value, ani_temp)
        target.write(f"{' ' * offset}ani_object {ani_result} = {ani_temp};\n")

    @override
    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        ani_temp = f"{cpp_result}_temp"
        target.write(
            f"{' ' * offset}{self.ani_whole_type} {ani_temp} = static_cast<{self.ani_whole_type}>({ani_value});\n"
        )
        self.from_ani_whole(target, offset, env, ani_temp, cpp_result)


class EnumTypeANIInfo(AbstractAnalysis[EnumType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        self.t = t
        self.am = am
        items_prx_type = ["undefined"]
        for item in t.ty_decl.items:
            if item.ty_ref is None:
                continue
            type_ani_info = TypeANIInfo.get(am, item.ty_ref.resolved_ty)
            items_prx_type.append(type_ani_info.prx_whole_type)
        items_prx_type_str = " | ".join(items_prx_type)
        enum_ani_info = EnumANIInfo.get(am, t.ty_decl)
        self.sts_type = enum_ani_info.sts_name
        self.prx_split_type = ["int", f"({items_prx_type_str})"]
        self.ani_split_type = ["ani_int", "ani_ref"]
        self.ani_split_base = ["ani_int", "ani_ref"]
        self.ani_split_suff = ["Int", "Ref"]
        self.prx_whole_type = enum_ani_info.prx_name
        self.ani_whole_type = "ani_object"
        self.ani_whole_base = "ani_ref"
        self.ani_whole_suff = "Ref"
        self.ani_array_type = "ani_array_ref"

    @override
    def from_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        ani_tag = ani_values.pop(0)
        ani_value = ani_values.pop(0)
        cpp_tag = f"{cpp_result}_tag"
        enum_cpp_info = EnumCppInfo.get(self.am, self.t.ty_decl)
        type_cpp_info = TypeCppInfo.get(self.am, self.t)
        target.write(
            f"{' ' * offset}{type_cpp_info.as_owner} {cpp_result} = [=] {{\n"
            f"{' ' * offset}    {enum_cpp_info.full_name}::tag_t {cpp_tag} = ({enum_cpp_info.full_name}::tag_t){ani_tag};\n"
            f"{' ' * offset}    switch ({cpp_tag}) {{\n"
        )
        for i, item in enumerate(self.t.ty_decl.items):
            target.write(
                f"{' ' * offset}    case {enum_cpp_info.full_name}::tag_t::{item.name}: {{\n"
            )
            if item.ty_ref is None:
                target.write(
                    f"{' ' * offset}        return {enum_cpp_info.full_name}::make_{item.name}();\n"
                )
            else:
                case_result = f"{cpp_result}_{i}"
                type_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
                type_ani_info.from_ani_boxed(
                    target,
                    offset + 8,
                    env,
                    ani_value,
                    case_result,
                )
                target.write(
                    f"{' ' * offset}        return {enum_cpp_info.full_name}::make_{item.name}(std::move({case_result}));\n"
                )
            target.write(f"{' ' * offset}    }}\n")
        target.write(f"{' ' * offset}    }}\n" f"{' ' * offset}}}();\n")

    @override
    def from_ani_whole(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        enum_ani_info = EnumANIInfo.get(self.am, self.t.ty_decl)
        ani_value_cls = f"{cpp_result}_cls"
        ani_value_tag = f"{cpp_result}_tag"
        ani_value_val = f"{cpp_result}_value"
        ani_value_tag_field = f"{ani_value_tag}_field"
        ani_value_val_field = f"{ani_value_val}_field"
        target.write(
            f"{' ' * offset}static ani_class {ani_value_cls} = [=] {{\n"
            f"{' ' * offset}    ani_class {ani_value_cls};\n"
            f"{' ' * offset}    {env}->FindClass(\"{enum_ani_info.cls_name}\", &{ani_value_cls});\n"
            f"{' ' * offset}    return {ani_value_cls};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}static ani_field {ani_value_tag_field} = [=] {{\n"
            f"{' ' * offset}    ani_field {ani_value_tag_field};\n"
            f"{' ' * offset}    {env}->Class_FindField({ani_value_cls}, \"tag\", &{ani_value_tag_field});\n"
            f"{' ' * offset}    return {ani_value_tag_field};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}ani_int {ani_value_tag};\n"
            f"{' ' * offset}{env}->Object_GetField_Int({ani_value}, {ani_value_tag_field}, &{ani_value_tag});\n"
            f"{' ' * offset}static ani_field {ani_value_val_field} = [=] {{\n"
            f"{' ' * offset}    ani_field {ani_value_val_field};\n"
            f"{' ' * offset}    {env}->Class_FindField({ani_value_cls}, \"value\", &{ani_value_val_field});\n"
            f"{' ' * offset}    return {ani_value_val_field};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}ani_ref {ani_value_val};\n"
            f"{' ' * offset}{env}->Object_GetField_Ref({ani_value}, {ani_value_val_field}, &{ani_value_val});\n"
        )
        self.from_ani_split(
            target, offset, env, [ani_value_tag, ani_value_val], cpp_result
        )

    @override
    def into_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_results: list[str],
    ):
        ani_result_tag = ani_results.pop(0)
        ani_result_value = ani_results.pop(0)
        enum_cpp_info = EnumCppInfo.get(self.am, self.t.ty_decl)
        target.write(
            f"{' ' * offset}ani_int {ani_result_tag} = (int){cpp_value}.get_tag();\n"
            f"{' ' * offset}ani_ref {ani_result_value};\n"
            f"{' ' * offset}switch ({cpp_value}.get_tag()) {{\n"
        )
        for i, item in enumerate(self.t.ty_decl.items):
            target.write(
                f"{' ' * offset}    case {enum_cpp_info.full_name}::tag_t::{item.name}: {{\n"
            )
            if item.ty_ref is None:
                target.write(
                    f"{' ' * offset}        {env}->GetUndefined(&{ani_result_value});\n"
                )
            else:
                ani_result_temp = f"{ani_result_value}_temp"
                type_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
                type_ani_info.into_ani_boxed(
                    target,
                    offset + 8,
                    env,
                    f"{cpp_value}.get_{item.name}_ref()",
                    ani_result_temp,
                )
                target.write(
                    f"{' ' * offset}        {ani_result_value} = {ani_result_temp};\n"
                )
            target.write(f"{' ' * offset}    }}\n")
        target.write(f"{' ' * offset}    }}\n")

    @override
    def into_ani_whole(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        ani_result_tag = f"{ani_result}_tag"
        ani_result_value = f"{ani_result}_value"
        self.into_ani_split(
            target, offset, "env", cpp_value, [ani_result_tag, ani_result_value]
        )
        enum_ani_info = EnumANIInfo.get(self.am, self.t.ty_decl)
        ani_result_cls = f"{ani_result}_cls"
        ani_result_ctor = f"{ani_result}_ctor"
        target.write(
            f"{' ' * offset}static ani_class {ani_result_cls} = [=] {{\n"
            f"{' ' * offset}    ani_class {ani_result_cls};\n"
            f"{' ' * offset}    {env}->FindClass(\"{enum_ani_info.cls_name}\", &{ani_result_cls});\n"
            f"{' ' * offset}    return {ani_result_cls};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}static ani_method {ani_result_ctor} = [=] {{\n"
            f"{' ' * offset}    ani_method {ani_result_ctor};\n"
            f"{' ' * offset}    {env}->Class_FindMethod({ani_result_cls}, \"<ctor>\", nullptr, &{ani_result_ctor});\n"
            f"{' ' * offset}    return {ani_result_ctor};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}ani_object {ani_result};\n"
            f"{' ' * offset}{env}->Object_New({ani_result_cls}, {ani_result_ctor}, &{ani_result}, {ani_result_tag}, {ani_result_value});\n"
        )

    @override
    def into_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        prx_result_tag = prx_results.pop(0)
        prx_result_val = prx_results.pop(0)
        target.write(
            f"{' ' * offset}let {prx_result_tag}: {self.prx_split_type[0]} = {sts_value}.tag;\n"
            f"{' ' * offset}let {prx_result_val}: {self.prx_split_type[1]};\n"
            f"{' ' * offset}switch ({sts_value}.tag) {{\n"
        )
        for i, item in enumerate(self.t.ty_decl.items):
            target.write(f"{' ' * offset}case {item.value}: {{\n")
            if item.ty_ref is None:
                target.write(f"{' ' * offset}    {prx_result_val} = undefined;\n")
            else:
                type_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
                sts_item_val = f"{prx_result_val}_sts_{i}"
                prx_item_val = f"{prx_result_val}_prx_{i}"
                target.write(
                    f"{' ' * offset}    let {sts_item_val}: {type_ani_info.sts_type} = {sts_value}.value as {type_ani_info.sts_type};\n"
                )
                type_ani_info.into_prx_whole(
                    target, offset + 4, sts_item_val, prx_item_val
                )
                target.write(f"{' ' * offset}    {prx_result_val} = {prx_item_val};\n")
            target.write(f"{' ' * offset}    break;\n" f"{' ' * offset}}}\n")
        target.write(
            f"{' ' * offset}default:\n"
            f"{' ' * offset}    throw new Error();\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def into_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_result: str,
    ):
        prx_result_tag = f"{prx_result}_tag"
        prx_result_val = f"{prx_result}_val"
        self.into_prx_split(target, offset, sts_value, [prx_result_tag, prx_result_val])
        enum_ani_info = EnumANIInfo.get(self.am, self.t.ty_decl)
        target.write(
            f"{' ' * offset}let {prx_result}: {self.prx_whole_type} = new {enum_ani_info.prx_name}({prx_result_tag}, {prx_result_val});\n"
        )

    @override
    def from_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        prx_values: list[str],
        sts_result: str,
    ):
        prx_value_tag = prx_values.pop(0)
        prx_value_val = prx_values.pop(0)
        enum_ani_info = EnumANIInfo.get(self.am, self.t.ty_decl)
        target.write(
            f"{' ' * offset}let {sts_result}: {self.sts_type};\n"
            f"{' ' * offset}switch ({prx_value_tag}) {{\n"
        )
        for i, item in enumerate(self.t.ty_decl.items):
            target.write(f"{' ' * offset}case {item.value}: {{\n")
            if item.ty_ref is None:
                target.write(
                    f"{' ' * offset}    {sts_result} = new {enum_ani_info.sts_ctor}({prx_value_tag}, undefined);\n"
                )
            else:
                prx_item_val = f"{sts_result}_prx_{i}"
                sts_item_val = f"{sts_result}_sts_{i}"
                type_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
                target.write(
                    f"{' ' * offset}    let {prx_item_val}: {type_ani_info.prx_whole_type} = {prx_value_val} as {type_ani_info.prx_whole_type};\n"
                )
                type_ani_info.from_prx_whole(
                    target, offset + 4, prx_item_val, sts_item_val
                )
                target.write(
                    f"{' ' * offset}    {sts_result} = new {enum_ani_info.sts_ctor}({prx_value_tag}, {sts_item_val});\n"
                )
            target.write(f"{' ' * offset}    break;\n" f"{' ' * offset}}}\n")
        target.write(
            f"{' ' * offset}default:\n"
            f"{' ' * offset}    throw new Error();\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def from_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        prx_value: str,
        sts_result: str,
    ):
        prx_value_tag = f"{sts_result}_tag"
        prx_value_val = f"{sts_result}_val"
        self.from_prx_split(target, offset, [prx_value_tag, prx_value_val], sts_result)

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
            f"{' ' * offset}    {self.ani_whole_type} {ani_value};\n"
            f"{' ' * offset}    {env}->Array_Get_Ref({ani_array_value}, {i}, reinterpret_cast<ani_ref*>(&{ani_value}));\n"
        )
        self.from_ani_whole(target, offset + 4, env, ani_value, cpp_result)
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
            f"{' ' * offset}static ani_class {ani_class} = [=] {{\n"
            f"{' ' * offset}    ani_class {ani_class};\n"
            f"{' ' * offset}    {env}->FindClass(\"{enum_ani_info.cls_name}\", &{ani_class});\n"
            f"{' ' * offset}    return {ani_class};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}ani_ref undefined;\n"
            f"{' ' * offset}{env}->GetUndefined(&undefined);\n"
            f"{' ' * offset}{env}->Array_New_Ref({ani_class}, {size}, undefined, &{ani_array_result});\n"
            f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
        )
        self.into_ani_whole(
            target, offset + 4, env, f"{cpp_array_value}[{i}]", ani_result
        )
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
        ani_temp = f"{ani_result}_temp"
        self.into_ani_whole(target, offset, env, cpp_value, ani_temp)
        target.write(f"{' ' * offset}ani_object {ani_result} = {ani_temp};\n")

    @override
    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        ani_temp = f"{cpp_result}_temp"
        target.write(
            f"{' ' * offset}{self.ani_whole_type} {ani_temp} = static_cast<{self.ani_whole_type}>({ani_value});\n"
        )
        self.from_ani_whole(target, offset, env, ani_temp, cpp_result)


class IfaceTypeANIInfo(AbstractAnalysis[IfaceType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        pass


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
        }.get(t)
        if sts_type is None:
            raise ValueError
        self.sts_type = sts_type
        self.prx_split_type = [sts_type]
        self.ani_split_type = [f"ani_{sts_type}"]
        self.ani_split_base = [f"ani_{sts_type}"]
        self.ani_split_suff = [sts_type[0].upper() + sts_type[1:]]
        self.prx_whole_type = sts_type
        self.ani_whole_type = f"ani_{sts_type}"
        self.ani_whole_base = f"ani_{sts_type}"
        self.ani_whole_suff = sts_type[0].upper() + sts_type[1:]
        self.ani_array_type = f"ani_array_{sts_type}"
        self.cpp_info = TypeCppInfo.get(am, t)

    @override
    def from_ani_split(
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
    def into_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_results: list[str],
    ):
        ani_result = ani_results.pop(0)
        target.write(
            f"{' ' * offset}{self.ani_whole_type} {ani_result} = {cpp_value};\n"
        )

    @override
    def from_ani_whole(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        target.write(
            f"{' ' * offset}{self.ani_whole_type} {cpp_result} = {ani_value};\n"
        )

    @override
    def into_ani_whole(
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
    def from_prx_split(
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
    def into_prx_split(
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
    def from_prx_whole(
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
    def into_prx_whole(
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
            f"{' ' * offset}{env}->Array_GetRegion_{self.ani_whole_suff}({ani_array_value}, 0, {size}, {cpp_array_buffer});\n"
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
            f"{' ' * offset}{self.ani_array_type} {ani_array_result};\n"
            f"{' ' * offset}{env}->Array_New_{self.ani_whole_suff}({size}, &{ani_array_result});\n"
            f"{' ' * offset}{env}->Array_SetRegion_{self.ani_whole_suff}({ani_array_result}, 0, {size}, {cpp_array_value});\n"
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
            f"{' ' * offset}static ani_class {ani_class} = [=] {{\n"
            f"{' ' * offset}    ani_class {ani_class};\n"
            f"{' ' * offset}    {env}->FindClass(\"Lstd/core/{self.ani_whole_suff};\", &{ani_class});\n"
            f"{' ' * offset}    return {ani_class};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}static ani_method {ani_ctor} = [=] {{\n"
            f"{' ' * offset}    ani_method {ani_ctor};\n"
            f"{' ' * offset}    {env}->Class_FindMethod({ani_class}, \"<ctor>\", nullptr, &{ani_ctor});\n"
            f"{' ' * offset}    return {ani_ctor};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}ani_object {ani_result};\n"
        )
        self.into_ani_whole(target, offset, env, cpp_value, ani_value)
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
            f"{' ' * offset}static ani_class {ani_class} = [=] {{\n"
            f"{' ' * offset}    ani_class {ani_class};\n"
            f"{' ' * offset}    {env}->FindClass(\"Lstd/core/{self.ani_whole_suff};\", &{ani_class});\n"
            f"{' ' * offset}    return {ani_class};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}static ani_method {ani_getter} = [=] {{\n"
            f"{' ' * offset}    ani_method {ani_getter};\n"
            f"{' ' * offset}    {env}->Class_FindMethod({ani_class}, \"{self.sts_type}Value\", nullptr, &{ani_getter});\n"
            f"{' ' * offset}    return {ani_getter};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}{self.ani_whole_type} {ani_result};\n"
            f"{' ' * offset}{env}->Object_CallMethod_{self.ani_whole_suff}((ani_object){ani_value}, {ani_getter}, &{ani_result});\n"
        )
        self.from_ani_whole(target, offset, env, ani_result, cpp_result)


class StringTypeANIInfo(AbstractAnalysis[StringType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: StringType):
        if t != STRING:
            raise ValueError
        self.sts_type = "string"
        self.prx_split_type = ["string"]
        self.ani_split_type = ["ani_string"]
        self.ani_split_base = ["ani_ref"]
        self.ani_split_suff = ["Ref"]
        self.prx_whole_type = "string"
        self.ani_whole_type = "ani_string"
        self.ani_whole_base = "ani_ref"
        self.ani_whole_suff = "Ref"
        self.ani_array_type = "ani_array_ref"
        self.cpp_info = TypeCppInfo.get(am, t)

    @override
    def from_ani_whole(
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
    def from_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        ani_value = ani_values.pop(0)
        self.from_ani_whole(target, offset, env, ani_value, cpp_result)

    @override
    def into_ani_whole(
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
    def into_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_results: list[str],
    ):
        ani_result = ani_results.pop(0)
        self.into_ani_whole(target, offset, env, cpp_value, ani_result)

    @override
    def from_prx_whole(
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
    def from_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        prx_values: list[str],
        sts_result: str,
    ):
        prx_value = prx_values.pop(0)
        self.from_prx_whole(target, offset, prx_value, sts_result)

    @override
    def into_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_result: str,
    ):
        target.write(
            f"{' ' * offset}let {prx_result}: {self.prx_whole_type} = {sts_value};\n"
        )

    @override
    def into_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        prx_result = prx_results.pop(0)
        self.into_prx_whole(target, offset, sts_value, prx_result)

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
        self.from_ani_whole(target, offset + 4, env, ani_value, cpp_result)
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
            f"{' ' * offset}static ani_class {ani_class} = [=] {{\n"
            f"{' ' * offset}    ani_class {ani_class};\n"
            f"{' ' * offset}    {env}->FindClass(\"Lstd/core/String;\", &{ani_class});\n"
            f"{' ' * offset}    return {ani_class};\n"
            f"{' ' * offset}}}();\n"
            f"{' ' * offset}ani_ref undefined;\n"
            f"{' ' * offset}{env}->GetUndefined(&undefined);\n"
            f"{' ' * offset}{env}->Array_New_Ref({ani_class}, {size}, undefined, &{ani_array_result});\n"
            f"{' ' * offset}for (size_t {i} = 0; {i} < {size}; {i}++) {{\n"
        )
        self.into_ani_whole(
            target, offset + 4, env, f"{cpp_array_value}[{i}]", ani_result
        )
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
        ani_temp = f"{ani_result}_temp"
        self.into_ani_whole(target, offset, env, cpp_value, ani_temp)
        target.write(f"{' ' * offset}ani_object {ani_result} = {ani_temp};\n")

    @override
    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        ani_temp = f"{cpp_result}_temp"
        target.write(
            f"{' ' * offset}{self.ani_whole_type} {ani_temp} = static_cast<{self.ani_whole_type}>({ani_value});\n"
        )
        self.from_ani_whole(target, offset, env, ani_temp, cpp_result)


class ArrayTypeANIInfo(AbstractAnalysis[ArrayType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        item_ty_ani_info = TypeANIInfo.get(am, t.item_ty)
        self.sts_type = f"({item_ty_ani_info.sts_type}[])"
        self.prx_split_type = [f"({item_ty_ani_info.prx_whole_type}[])"]
        self.ani_split_type = [item_ty_ani_info.ani_array_type]
        self.ani_split_base = ["ani_ref"]
        self.ani_split_suff = ["Ref"]
        self.prx_whole_type = f"({item_ty_ani_info.prx_whole_type}[])"
        self.ani_whole_type = item_ty_ani_info.ani_array_type
        self.ani_whole_base = "ani_ref"
        self.ani_whole_suff = "Ref"
        self.ani_array_type = "ani_array_ref"
        self.am = am
        self.t = t

    @override
    def into_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_result: str,
    ):
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        if val_ty_ani_info.prx_whole_type == val_ty_ani_info.sts_type:
            target.write(
                f"{' ' * offset}let {prx_result}: {val_ty_ani_info.prx_whole_type}[] = {sts_value};\n"
            )
            return
        sts_item = "sts_item"
        prx_item = "prx_item"
        target.write(
            f"{' ' * offset}let {prx_result}: {val_ty_ani_info.prx_whole_type}[] = new {val_ty_ani_info.prx_whole_type}[{sts_value}.length];\n"
            f"{' ' * offset}for (let i = 0; i < {sts_value}.length; i++) {{\n"
            f"{' ' * offset}    let {sts_item}: {val_ty_ani_info.sts_type} = {sts_value}[i];\n"
        )
        val_ty_ani_info.into_prx_whole(target, offset + 4, sts_item, prx_item)
        target.write(
            f"{' ' * offset}    {prx_result}[i] = {prx_item};\n" f"{' ' * offset}}}\n"
        )

    @override
    def into_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        prx_result = prx_results.pop(0)
        self.into_prx_whole(target, offset, sts_value, prx_result)

    @override
    def from_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        prx_value: str,
        sts_result: str,
    ):
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        if val_ty_ani_info.prx_whole_type == val_ty_ani_info.sts_type:
            target.write(
                f"{' ' * offset}let {sts_result}: {val_ty_ani_info.sts_type}[] = {prx_value};\n"
            )
            return
        prx_item = "prx_item"
        sts_item = "sts_item"
        target.write(
            f"{' ' * offset}let {sts_result}: {val_ty_ani_info.sts_type}[] = new {val_ty_ani_info.sts_type}[{prx_value}.length];\n"
            f"{' ' * offset}for (let i = 0; i < {prx_value}.length; i++) {{\n"
            f"{' ' * offset}    let {prx_item}: {val_ty_ani_info.prx_whole_type} = {prx_value}[i];\n"
        )
        val_ty_ani_info.from_prx_whole(target, offset + 4, prx_item, sts_item)
        target.write(
            f"{' ' * offset}    {sts_result}[i] = {sts_item};\n" f"{' ' * offset}}}\n"
        )

    @override
    def from_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        prx_values: list[str],
        sts_result: str,
    ):
        prx_value = prx_values.pop(0)
        self.from_prx_whole(target, offset, prx_value, sts_result)

    @override
    def from_ani_whole(
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
    def from_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        ani_value = ani_values.pop(0)
        self.from_ani_whole(target, offset, env, ani_value, cpp_result)

    @override
    def into_ani_whole(
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
    def into_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_results: list[str],
    ):
        ani_result = ani_results.pop(0)
        self.into_ani_whole(target, offset, env, cpp_value, ani_result)

    @override
    def into_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        ani_temp = f"{ani_result}_temp"
        self.into_ani_whole(target, offset, env, cpp_value, ani_temp)
        target.write(f"{' ' * offset}ani_object {ani_result} = {ani_temp};\n")

    @override
    def from_ani_boxed(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        ani_temp = f"{cpp_result}_temp"
        target.write(
            f"{' ' * offset}{self.ani_whole_type} {ani_temp} = static_cast<{self.ani_whole_type}>({ani_value});\n"
        )
        self.from_ani_whole(target, offset, env, ani_temp, cpp_result)


class OptionalTypeANIInfo(AbstractAnalysis[OptionalType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: OptionalType) -> None:
        item_ty_ani_info = TypeANIInfo.get(am, t.item_ty)
        self.sts_type = f"({item_ty_ani_info.sts_type} | undefined)"
        self.prx_split_type = [f"({item_ty_ani_info.prx_whole_type} | undefined)"]
        self.ani_split_type = ["ani_ref"]
        self.ani_split_base = ["ani_ref"]
        self.ani_split_suff = ["Ref"]
        self.prx_whole_type = f"({item_ty_ani_info.prx_whole_type} | undefined)"
        self.ani_whole_type = "ani_ref"
        self.ani_whole_base = "ani_ref"
        self.ani_whole_suff = "Ref"
        self.ani_array_type = "ani_array_ref"
        self.am = am
        self.t = t

    @override
    def from_ani_whole(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_value: str,
        cpp_result: str,
    ):
        ani_is_undefined = f"{cpp_result}_flag"
        cpp_pointer = f"{cpp_result}_ptr"
        cpp_inner = f"{cpp_result}_inner"
        cpp_info = TypeCppInfo.get(self.am, self.t)
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        target.write(
            f"{' ' * offset}ani_boolean {ani_is_undefined};\n"
            f"{' ' * offset}{item_ty_cpp_info.as_owner}* {cpp_pointer} = nullptr;\n"
            f"{' ' * offset}{env}->Reference_IsUndefined({ani_value}, &{ani_is_undefined});\n"
            f"{' ' * offset}if (!{ani_is_undefined}) {{\n"
        )
        item_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        item_ty_ani_info.from_ani_boxed(target, offset + 4, env, ani_value, cpp_inner)
        target.write(
            f"{' ' * offset}    *{cpp_pointer} = std::move({cpp_inner});\n"
            f"{' ' * offset}}};\n"
            f"{' ' * offset}{cpp_info.as_owner} {cpp_result}({cpp_pointer});\n"
        )

    @override
    def from_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        ani_values: list[str],
        cpp_result: str,
    ):
        ani_value = ani_values.pop(0)
        self.from_ani_whole(target, offset, env, ani_value, cpp_result)

    @override
    def into_ani_whole(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_result: str,
    ):
        ani_result_real = f"{ani_result}_real"
        target.write(
            f"{' ' * offset}ani_ref {ani_result};\n"
            f"{' ' * offset}if (!{cpp_value}) {{\n"
            f"{' ' * offset}    {env}->GetUndefined(&{ani_result});\n"
            f"{' ' * offset}}} else {{\n"
        )
        item_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        item_ty_ani_info.into_ani_boxed(
            target, offset + 4, env, f"(*{cpp_value})", ani_result_real
        )
        target.write(
            f"{' ' * offset}    {ani_result} = {ani_result_real};\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def into_ani_split(
        self,
        target: COutputBuffer,
        offset: int,
        env: str,
        cpp_value: str,
        ani_results: list[str],
    ):
        ani_result = ani_results.pop(0)
        self.into_ani_whole(target, offset, env, cpp_value, ani_result)

    @override
    def into_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_result: str,
    ):
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        if val_ty_ani_info.prx_whole_type == val_ty_ani_info.sts_type:
            target.write(
                f"{' ' * offset}let {prx_result}: {val_ty_ani_info.prx_whole_type} | undefined = {sts_value};\n"
            )
            return
        sts_inner_real = f"{prx_result}_sts_real"
        prx_inner_real = f"{prx_result}_prx_real"
        target.write(
            f"{' ' * offset}let {prx_result}: {self.prx_whole_type};\n"
            f"{' ' * offset}if ({sts_value} === undefined) {{\n"
            f"{' ' * offset}    {prx_result} = undefined;\n"
            f"{' ' * offset}}} else {{\n"
            f"{' ' * offset}    let {sts_inner_real}: {self.sts_type} = {sts_value} as {self.sts_type};\n"
        )
        val_ty_ani_info.into_prx_whole(
            target, offset + 4, sts_inner_real, prx_inner_real
        )
        target.write(
            f"{' ' * offset}    {prx_result} = {prx_inner_real};\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def into_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        sts_value: str,
        prx_results: list[str],
    ):
        prx_result = prx_results.pop(0)
        self.into_prx_whole(target, offset, sts_value, prx_result)

    @override
    def from_prx_whole(
        self,
        target: OutputBuffer,
        offset: int,
        prx_value: str,
        sts_result: str,
    ):
        val_ty_ani_info = TypeANIInfo.get(self.am, self.t.item_ty)
        if val_ty_ani_info.prx_whole_type == val_ty_ani_info.sts_type:
            target.write(
                f"{' ' * offset}let {sts_result}: {val_ty_ani_info.sts_type} | undefined = {prx_value};\n"
            )
            return
        prx_inner_real = f"{sts_result}_prx_real"
        sts_inner_real = f"{sts_result}_sts_real"
        target.write(
            f"{' ' * offset}let {sts_result}: {self.sts_type};\n"
            f"{' ' * offset}if ({prx_value} === undefined) {{\n"
            f"{' ' * offset}    {sts_result} = undefined;\n"
            f"{' ' * offset}}} else {{\n"
            f"{' ' * offset}    let {prx_inner_real}: {self.prx_whole_type} = {prx_value} as {self.prx_whole_type};\n"
        )
        val_ty_ani_info.from_prx_whole(
            target, offset + 4, prx_inner_real, sts_inner_real
        )
        target.write(
            f"{' ' * offset}    {sts_result} = {sts_inner_real};\n"
            f"{' ' * offset}}}\n"
        )

    @override
    def from_prx_split(
        self,
        target: OutputBuffer,
        offset: int,
        prx_values: list[str],
        sts_result: str,
    ):
        prx_value = prx_values.pop(0)
        self.from_prx_whole(target, offset, prx_value, sts_result)


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
            self.gen_struct_proxy(struct, pkg_sts_target)
        for enum in pkg.enums:
            self.gen_enum_proxy(enum, pkg_sts_target)
        for func in pkg.functions:
            self.gen_func_proxy(func, pkg_sts_target)

        for struct in pkg.structs:
            self.gen_struct_inner(struct, pkg_sts_target)
        for enum in pkg.enums:
            self.gen_enum_inner(enum, pkg_sts_target)

        for struct in pkg.structs:
            self.gen_struct_interface(struct, pkg_sts_target)
        for enum in pkg.enums:
            self.gen_enum_interface(enum, pkg_sts_target)
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
            for i, prx_type in enumerate(type_ani_info.prx_split_type):
                param_prx = f"{param.name}_proxy_{i}"
                params_prx.append(f"{param_prx}: {prx_type}")
        params_prx_str = ", ".join(params_prx)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            pxy_return_ty_name = type_ani_info.prx_whole_type
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
            f"export function {func_ani_info.sts_name}({params_sts_str}): {sts_return_ty_name} {{\n"
        )
        params_prx = []
        for param in func.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            param_prx_results = []
            for i, prx_type in enumerate(type_ani_info.prx_split_type):
                param_prx = f"{param.name}_proxy_{i}"
                param_prx_results.append(param_prx)
                params_prx.append(param_prx)
            type_ani_info.into_prx_split(
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
            type_ani_info.from_prx_whole(
                pkg_sts_target, 4, result_prx_value, result_sts_result
            )
            pkg_sts_target.write(f"    return {result_sts_result};\n")
        else:
            pkg_sts_target.write(f"    {func_ani_info.prx_name}({params_prx_str});\n")
        pkg_sts_target.write("}\n")

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

    def gen_struct_proxy(
        self,
        struct: StructDecl,
        pkg_sts_target: OutputBuffer,
    ):
        struct_ani_info = StructANIInfo.get(self.am, struct)
        type_ani_info = StructTypeANIInfo.get(self.am, struct.as_type())
        pkg_sts_target.write(f"class {struct_ani_info.prx_name} {{\n")
        for flat_field_name, prx_type in zip(
            type_ani_info.flat_field_names, type_ani_info.prx_split_type
        ):
            pkg_sts_target.write(f"    {flat_field_name}: {prx_type};\n")
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
        pkg_sts_target.write("}\n")

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

    def gen_enum_proxy(
        self,
        enum: EnumDecl,
        pkg_sts_target: OutputBuffer,
    ):
        enum_ani_info = EnumANIInfo.get(self.am, enum)
        type_ani_info = EnumTypeANIInfo.get(self.am, enum.as_type())
        pkg_sts_target.write(
            f"class {enum_ani_info.prx_name} {{\n"
            f"    tag: {type_ani_info.prx_split_type[0]};\n"
            f"    value: {type_ani_info.prx_split_type[1]};\n"
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
            for i, ani_type in enumerate(type_ani_info.ani_split_type):
                param_ani = f"{param.name}_proxy_{i}"
                param_ani_values.append(param_ani)
                params_ani.append(f"{ani_type} {param_ani}")
            params_values_list.append(param_ani_values)
        params_ani_str = ", ".join(params_ani)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            ani_return_ty_name = type_ani_info.ani_whole_type
        else:
            ani_return_ty_name = "void"
        pkg_ani_target.write(
            f"static {ani_return_ty_name} {func_ani_info.mangled_name}({params_ani_str}) {{\n"
        )
        args_cpp = []
        for param, param_ani_values in zip(func.params, params_values_list):
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            type_ani_info.from_ani_split(
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
            type_ani_info.into_ani_whole(
                pkg_ani_target, 4, "env", result_cpp_value, result_ani_result
            )
            pkg_ani_target.write(f"    return {result_ani_result};\n")
        else:
            pkg_ani_target.write(
                f"    {func_cpp_info.full_name}({args_cpp_str});\n" f"    return;\n"
            )
        pkg_ani_target.write("}\n")
