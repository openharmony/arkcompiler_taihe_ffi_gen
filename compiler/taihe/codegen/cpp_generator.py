from abc import ABCMeta

from typing_extensions import override

from taihe.codegen.abi_generator import (
    EnumABIInfo,
    GlobFuncABIInfo,
    IfaceABIInfo,
    IfaceMethodABIInfo,
    PackageABIInfo,
    StructABIInfo,
    TypeABIInfo,
)
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
from taihe.utils.outputs import COutputBuffer, OutputManager


class PackageCppInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        self.header = f"{p.name}.proj.hpp"


class GlobFuncCppInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        p = f.node_parent
        assert p
        self.namespace = "::".join(p.segments)
        self.call_name = f.name
        self.full_name = "::" + self.namespace + "::" + self.call_name


class IfaceMethodCppInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, f: IfaceMethodDecl) -> None:
        # TODO: Supports projection to any C++ function name based on attributes
        self.call_name = f.name
        self.impl_name = f.name


class StructCppInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.node_parent
        assert p
        self.decl_header = f"{p.name}.{d.name}.proj.0.hpp"
        self.impl_header = f"{p.name}.{d.name}.proj.1.hpp"
        self.namespace = "::".join(p.segments)
        self.name = d.name
        self.full_name = "::" + self.namespace + "::" + self.name
        self.as_owner = self.full_name
        self.as_param = self.full_name + " const&"


class EnumCppInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.node_parent
        assert p
        self.decl_header = f"{p.name}.{d.name}.proj.0.hpp"
        self.impl_header = f"{p.name}.{d.name}.proj.1.hpp"
        self.namespace = "::".join(p.segments)
        self.name = d.name
        self.full_name = "::" + self.namespace + "::" + self.name
        self.as_owner = self.full_name
        self.as_param = self.full_name + " const&"


class IfaceCppInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.node_parent
        assert p
        self.decl_header = f"{p.name}.{d.name}.proj.0.hpp"
        self.defn_header = f"{p.name}.{d.name}.proj.1.hpp"
        self.impl_header = f"{p.name}.{d.name}.proj.2.hpp"
        self.norm_name = d.name
        self.weak_name = d.name
        self.namespace = "::".join(p.segments)
        self.weakspace = "::".join(p.segments) + "::weak"
        self.full_norm_name = "::" + self.namespace + "::" + self.norm_name
        self.full_weak_name = "::" + self.weakspace + "::" + self.weak_name
        self.as_owner = self.full_norm_name
        self.as_param = self.full_weak_name


class AbstractTypeCppInfo(metaclass=ABCMeta):
    decl_headers: list[str]
    impl_headers: list[str]
    as_owner: str
    as_param: str

    def return_from_abi(self, val):
        return f"::taihe::core::from_abi<{self.as_owner}>({val})"

    def return_into_abi(self, val):
        return f"::taihe::core::into_abi<{self.as_owner}>({val})"

    def pass_from_abi(self, val):
        return f"::taihe::core::from_abi<{self.as_param}>({val})"

    def pass_into_abi(self, val):
        return f"::taihe::core::into_abi<{self.as_param}>({val})"


class EnumTypeCppInfo(AbstractAnalysis[EnumType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        enum_cpp_info = EnumCppInfo.get(am, t.ty_decl)
        self.decl_headers = [enum_cpp_info.decl_header]
        self.impl_headers = [enum_cpp_info.impl_header]
        self.as_owner = enum_cpp_info.as_owner
        self.as_param = enum_cpp_info.as_param


class StructTypeCppInfo(AbstractAnalysis[StructType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: StructType):
        struct_cpp_info = StructCppInfo.get(am, t.ty_decl)
        self.decl_headers = [struct_cpp_info.decl_header]
        self.impl_headers = [struct_cpp_info.impl_header]
        self.as_owner = struct_cpp_info.as_owner
        self.as_param = struct_cpp_info.as_param


class IfaceTypeCppInfo(AbstractAnalysis[IfaceType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        iface_cpp_info = IfaceCppInfo.get(am, t.ty_decl)
        self.decl_headers = [iface_cpp_info.decl_header]
        self.impl_headers = [iface_cpp_info.impl_header]
        self.as_owner = iface_cpp_info.as_owner
        self.as_param = iface_cpp_info.as_param


class ScalarTypeCppInfo(AbstractAnalysis[ScalarType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        res = {
            BOOL: "bool",
            F32: "float",
            F64: "double",
            I8: "int8_t",
            I16: "int16_t",
            I32: "int32_t",
            I64: "int64_t",
            U8: "uint8_t",
            U16: "uint16_t",
            U32: "uint32_t",
            U64: "uint64_t",
        }.get(t)
        if res is None:
            raise ValueError
        self.decl_headers = []
        self.impl_headers = []
        self.as_param = res
        self.as_owner = res


class StringTypeCppInfo(AbstractAnalysis[StringType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: StringType):
        self.decl_headers = ["core/string.hpp"]
        self.impl_headers = ["core/string.hpp"]
        self.as_owner = "::taihe::core::string"
        self.as_param = "::taihe::core::string_view"


class ArrayTypeCppInfo(AbstractAnalysis[ArrayType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        arg_ty_cpp_info = TypeCppInfo.get(am, t.item_ty)
        self.decl_headers = ["core/array.hpp", *arg_ty_cpp_info.decl_headers]
        self.impl_headers = ["core/array.hpp", *arg_ty_cpp_info.impl_headers]
        self.as_owner = f"::taihe::core::array<{arg_ty_cpp_info.as_owner}>"
        self.as_param = f"::taihe::core::array_view<{arg_ty_cpp_info.as_owner}>"


class OptionalTypeCppInfo(AbstractAnalysis[OptionalType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: OptionalType) -> None:
        arg_ty_cpp_info = TypeCppInfo.get(am, t.item_ty)
        self.decl_headers = ["core/optional.hpp", *arg_ty_cpp_info.decl_headers]
        self.impl_headers = ["core/optional.hpp", *arg_ty_cpp_info.impl_headers]
        self.as_owner = f"::taihe::core::optional<{arg_ty_cpp_info.as_owner}>"
        self.as_param = f"::taihe::core::optional_view<{arg_ty_cpp_info.as_owner}>"


class VectorTypeCppInfo(AbstractAnalysis[VectorType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: VectorType) -> None:
        val_ty_cpp_info = TypeCppInfo.get(am, t.val_ty)
        self.decl_headers = ["core/vector.hpp", *val_ty_cpp_info.decl_headers]
        self.impl_headers = ["core/vector.hpp", *val_ty_cpp_info.impl_headers]
        self.as_owner = f"::taihe::core::vector<{val_ty_cpp_info.as_owner}>"
        self.as_param = f"::taihe::core::vector_view<{val_ty_cpp_info.as_owner}>"


class MapTypeCppInfo(AbstractAnalysis[MapType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        key_ty_cpp_info = TypeCppInfo.get(am, t.key_ty)
        val_ty_cpp_info = TypeCppInfo.get(am, t.val_ty)
        self.decl_headers = [
            "core/map.hpp",
            *key_ty_cpp_info.decl_headers,
            *val_ty_cpp_info.decl_headers,
        ]
        self.impl_headers = [
            "core/map.hpp",
            *key_ty_cpp_info.impl_headers,
            *val_ty_cpp_info.impl_headers,
        ]
        self.as_owner = f"::taihe::core::map<{key_ty_cpp_info.as_owner}, {val_ty_cpp_info.as_owner}>"
        self.as_param = f"::taihe::core::map_view<{key_ty_cpp_info.as_owner}, {val_ty_cpp_info.as_owner}>"


class SetTypeCppInfo(AbstractAnalysis[SetType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: SetType) -> None:
        key_ty_cpp_info = TypeCppInfo.get(am, t.key_ty)
        self.decl_headers = ["core/set.hpp", *key_ty_cpp_info.decl_headers]
        self.impl_headers = ["core/set.hpp", *key_ty_cpp_info.impl_headers]
        self.as_owner = f"::taihe::core::set<{key_ty_cpp_info.as_owner}>"
        self.as_param = f"::taihe::core::set_view<{key_ty_cpp_info.as_owner}>"


class CallbackTypeCppInfo(AbstractAnalysis[CallbackType], AbstractTypeCppInfo):
    def __init__(self, am: AnalysisManager, t: CallbackType) -> None:
        if t.return_ty:
            return_ty_cpp_info = TypeCppInfo.get(am, t.return_ty)
            return_ty_decl_headers = return_ty_cpp_info.decl_headers
            return_ty_defn_headers = return_ty_cpp_info.impl_headers
            return_ty_as_owner = return_ty_cpp_info.as_owner
        else:
            return_ty_decl_headers = []
            return_ty_defn_headers = []
            return_ty_as_owner = "void"
        params_ty_decl_headers = []
        params_ty_defn_headers = []
        params_ty_as_param = []
        for param_ty in t.params_ty:
            param_ty_cpp_info = TypeCppInfo.get(am, param_ty)
            params_ty_decl_headers.extend(param_ty_cpp_info.decl_headers)
            params_ty_defn_headers.extend(param_ty_cpp_info.impl_headers)
            params_ty_as_param.append(param_ty_cpp_info.as_param)
        params_fmt = ", ".join(params_ty_as_param)
        self.decl_headers = [
            "core/callback.hpp",
            *return_ty_decl_headers,
            *params_ty_decl_headers,
        ]
        self.impl_headers = [
            "core/callback.hpp",
            *return_ty_defn_headers,
            *params_ty_defn_headers,
        ]
        self.as_owner = f"::taihe::core::callback<{return_ty_as_owner}({params_fmt})>"
        self.as_param = (
            f"::taihe::core::callback_view<{return_ty_as_owner}({params_fmt})>"
        )


class TypeCppInfo(TypeVisitor[AbstractTypeCppInfo]):
    def __init__(self, am: AnalysisManager):
        self.am = am

    @staticmethod
    def get(am: AnalysisManager, t: Type | None) -> AbstractTypeCppInfo:
        assert t is not None
        return TypeCppInfo(am).handle_type(t)

    @override
    def visit_enum_type(self, t: EnumType) -> AbstractTypeCppInfo:
        return EnumTypeCppInfo.get(self.am, t)

    @override
    def visit_struct_type(self, t: StructType) -> AbstractTypeCppInfo:
        return StructTypeCppInfo.get(self.am, t)

    @override
    def visit_iface_type(self, t: IfaceType) -> AbstractTypeCppInfo:
        return IfaceTypeCppInfo.get(self.am, t)

    @override
    def visit_scalar_type(self, t: ScalarType) -> AbstractTypeCppInfo:
        return ScalarTypeCppInfo.get(self.am, t)

    @override
    def visit_string_type(self, t: StringType) -> AbstractTypeCppInfo:
        return StringTypeCppInfo.get(self.am, t)

    @override
    def visit_array_type(self, t: ArrayType) -> AbstractTypeCppInfo:
        return ArrayTypeCppInfo.get(self.am, t)

    @override
    def visit_optional_type(self, t: OptionalType) -> AbstractTypeCppInfo:
        return OptionalTypeCppInfo.get(self.am, t)

    @override
    def visit_vector_type(self, t: VectorType) -> AbstractTypeCppInfo:
        return VectorTypeCppInfo.get(self.am, t)

    @override
    def visit_map_type(self, t: MapType) -> AbstractTypeCppInfo:
        return MapTypeCppInfo.get(self.am, t)

    @override
    def visit_set_type(self, t: SetType) -> AbstractTypeCppInfo:
        return SetTypeCppInfo.get(self.am, t)

    @override
    def visit_callback_type(self, t: CallbackType) -> AbstractTypeCppInfo:
        return CallbackTypeCppInfo.get(self.am, t)


class CppHeadersGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_cpp_info = PackageCppInfo.get(self.am, pkg)
        pkg_cpp_target = COutputBuffer.create(
            self.tm, f"include/{pkg_cpp_info.header}", True
        )
        pkg_abi_info = PackageABIInfo.get(self.am, pkg)
        pkg_cpp_target.include("taihe/common.hpp")
        pkg_cpp_target.include(pkg_abi_info.header)
        for struct in pkg.structs:
            self.gen_struct_files(struct, pkg_cpp_target)
        for enum in pkg.enums:
            self.gen_enum_files(enum, pkg_cpp_target)
        for iface in pkg.interfaces:
            self.gen_iface_files(iface, pkg_cpp_target)
        for func in pkg.functions:
            self.gen_func(func, pkg_cpp_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_cpp_target: COutputBuffer,
    ):
        func_cpp_info = GlobFuncCppInfo.get(self.am, func)
        func_abi_info = GlobFuncABIInfo.get(self.am, func)
        params_cpp = []
        args_into_abi = []
        for param in func.params:
            type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_cpp_target.include(*type_cpp_info.impl_headers)
            params_cpp.append(f"{type_cpp_info.as_param} {param.name}")
            args_into_abi.append(type_cpp_info.pass_into_abi(param.name))
        params_cpp_str = ", ".join(params_cpp)
        args_into_abi_str = ", ".join(args_into_abi)
        abi_result = f"{func_abi_info.mangled_name}({args_into_abi_str})"
        if return_ty_ref := func.return_ty_ref:
            type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
            pkg_cpp_target.include(*type_cpp_info.impl_headers)
            cpp_return_ty_name = type_cpp_info.as_owner
            cpp_result = type_cpp_info.return_from_abi(abi_result)
        else:
            cpp_return_ty_name = "void"
            cpp_result = abi_result
        pkg_cpp_target.write(
            f"namespace {func_cpp_info.namespace} {{\n"
            f"inline {cpp_return_ty_name} {func_cpp_info.call_name}({params_cpp_str}) {{\n"
            f"    return {cpp_result};\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_struct_files(
        self,
        struct: StructDecl,
        pkg_cpp_target: COutputBuffer,
    ):
        struct_abi_info = StructABIInfo.get(self.am, struct)
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        self.gen_struct_decl_file(
            struct,
            struct_abi_info,
            struct_cpp_info,
        )
        self.gen_struct_impl_file(
            struct,
            struct_abi_info,
            struct_cpp_info,
        )
        pkg_cpp_target.include(struct_cpp_info.impl_header)

    def gen_struct_decl_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
        struct_cpp_info: StructCppInfo,
    ):
        struct_cpp_decl_target = COutputBuffer.create(
            self.tm, f"include/{struct_cpp_info.decl_header}", True
        )
        struct_cpp_decl_target.write(
            f"namespace {struct_cpp_info.namespace} {{\n"
            f"struct {struct_cpp_info.name};\n"
            f"}}\n"
        )

    def gen_struct_impl_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
        struct_cpp_info: StructCppInfo,
    ):
        struct_cpp_defn_target = COutputBuffer.create(
            self.tm, f"include/{struct_cpp_info.impl_header}", True
        )
        struct_cpp_defn_target.include("taihe/common.hpp")
        struct_cpp_defn_target.include(struct_cpp_info.decl_header)
        struct_cpp_defn_target.include(struct_abi_info.impl_header)
        self.gen_struct_defn(
            struct,
            struct_abi_info,
            struct_cpp_info,
            struct_cpp_defn_target,
        )
        self.gen_struct_hash(
            struct,
            struct_abi_info,
            struct_cpp_info,
            struct_cpp_defn_target,
        )
        self.gen_struct_same(
            struct,
            struct_abi_info,
            struct_cpp_info,
            struct_cpp_defn_target,
        )
        self.gen_struct_type_traits(
            struct,
            struct_abi_info,
            struct_cpp_info,
            struct_cpp_defn_target,
        )

    def gen_struct_defn(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
        struct_cpp_info: StructCppInfo,
        struct_cpp_defn_target: COutputBuffer,
    ):
        struct_cpp_defn_target.write(
            f"namespace {struct_cpp_info.namespace} {{\n"
            f"struct {struct_cpp_info.name} {{\n"
        )
        for field in struct.fields:
            type_cpp_info = TypeCppInfo.get(self.am, field.ty_ref.resolved_ty)
            struct_cpp_defn_target.include(*type_cpp_info.impl_headers)
            struct_cpp_defn_target.write(
                f"    {type_cpp_info.as_owner} {field.name};\n"
            )
        # finally
        struct_cpp_defn_target.write("};\n" "}\n")

    def gen_struct_same(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
        struct_cpp_info: StructCppInfo,
        struct_cpp_defn_target: COutputBuffer,
    ):
        result = "true"
        for field in struct.fields:
            result = f"{result} && same(lhs.{field.name}, rhs.{field.name})"
        struct_cpp_defn_target.write(
            f"namespace taihe::core {{\n"
            f"inline bool same_impl(adl_helper_t, {struct_cpp_info.as_param} lhs, {struct_cpp_info.as_param} rhs) {{\n"
            f"    return {result};\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_struct_hash(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
        struct_cpp_info: StructCppInfo,
        struct_cpp_defn_target: COutputBuffer,
    ):
        struct_cpp_defn_target.write(
            f"namespace taihe::core {{\n"
            f"inline auto hash_impl(adl_helper_t, {struct_cpp_info.as_param} val) -> ::std::size_t {{\n"
            f"    ::std::size_t seed = 0;\n"
        )
        for field in struct.fields:
            struct_cpp_defn_target.write(
                f"    seed ^= hash(val.{field.name}) + 0x9e3779b9 + (seed << 6) + (seed >> 2);\n"
            )
        struct_cpp_defn_target.write("    return seed;\n" "}\n" "}\n")

    def gen_struct_type_traits(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
        struct_cpp_info: StructCppInfo,
        struct_cpp_defn_target: COutputBuffer,
    ):
        struct_cpp_defn_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"struct as_abi<{struct_cpp_info.as_owner}> {{\n"
            f"    using type = {struct_abi_info.as_owner};\n"
            f"}};\n"
            f"template<>\n"
            f"struct as_abi<{struct_cpp_info.as_param}> {{\n"
            f"    using type = {struct_abi_info.as_param};\n"
            f"}};\n"
            f"template<>\n"
            f"struct as_param<{struct_cpp_info.as_owner}> {{\n"
            f"    using type = {struct_cpp_info.as_param};\n"
            f"}};\n"
            f"}}\n"
        )

    def gen_enum_files(
        self,
        enum: EnumDecl,
        pkg_cpp_target: COutputBuffer,
    ):
        enum_cpp_info = EnumCppInfo.get(self.am, enum)
        enum_abi_info = EnumABIInfo.get(self.am, enum)
        self.gen_enum_decl_file(
            enum,
            enum_abi_info,
            enum_cpp_info,
        )
        self.gen_enum_impl_file(
            enum,
            enum_abi_info,
            enum_cpp_info,
        )
        pkg_cpp_target.include(enum_cpp_info.impl_header)

    def gen_enum_decl_file(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumABIInfo,
        enum_cpp_info: EnumCppInfo,
    ):
        enum_cpp_decl_target = COutputBuffer.create(
            self.tm, f"include/{enum_cpp_info.decl_header}", True
        )
        enum_cpp_decl_target.write(
            f"namespace {enum_cpp_info.namespace} {{\n"
            f"struct {enum_cpp_info.name};\n"
            f"}}\n"
        )

    def gen_enum_impl_file(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumABIInfo,
        enum_cpp_info: EnumCppInfo,
    ):
        enum_cpp_defn_target = COutputBuffer.create(
            self.tm, f"include/{enum_cpp_info.impl_header}", True
        )
        enum_cpp_defn_target.include("taihe/common.hpp")
        enum_cpp_defn_target.include(enum_cpp_info.decl_header)
        enum_cpp_defn_target.include(enum_abi_info.impl_header)
        self.gen_enum_defn(
            enum,
            enum_abi_info,
            enum_cpp_info,
            enum_cpp_defn_target,
        )
        self.gen_enum_same(
            enum,
            enum_abi_info,
            enum_cpp_info,
            enum_cpp_defn_target,
        )
        self.gen_enum_hash(
            enum,
            enum_abi_info,
            enum_cpp_info,
            enum_cpp_defn_target,
        )
        self.gen_enum_type_traits(
            enum,
            enum_abi_info,
            enum_cpp_info,
            enum_cpp_defn_target,
        )

    def gen_enum_defn(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumABIInfo,
        enum_cpp_info: EnumCppInfo,
        enum_cpp_defn_target: COutputBuffer,
    ):
        enum_cpp_defn_target.write(
            f"namespace {enum_cpp_info.namespace} {{\n"
            f"struct {enum_cpp_info.name} {{\n"
        )
        # tag type
        enum_cpp_defn_target.write(
            f"    enum class tag_t : {enum_abi_info.tag_type} {{\n"
        )
        for item in enum.items:
            enum_cpp_defn_target.write(f"        {item.name} = {item.value},\n")
        enum_cpp_defn_target.write("    };\n")
        # storage type
        enum_cpp_defn_target.write(
            "    union storage_t {\n"
            "        storage_t() {}\n"
            "        ~storage_t() {}\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            type_cpp_info = TypeCppInfo.get(self.am, item.ty_ref.resolved_ty)
            enum_cpp_defn_target.include(*type_cpp_info.impl_headers)
            enum_cpp_defn_target.write(
                f"        {type_cpp_info.as_owner} {item.name};\n"
            )
        enum_cpp_defn_target.write("    };\n")
        # destructor
        enum_cpp_defn_target.write(
            f"    ~{enum_cpp_info.name}() {{\n" f"        switch (m_tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            enum_cpp_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            ::std::destroy_at(&m_data.{item.name});\n"
                f"            break;\n"
            )
        enum_cpp_defn_target.write(
            "        default:\n" "            break;\n" "        }\n" "    }\n"
        )
        # copy constructor
        enum_cpp_defn_target.write(
            f"    {enum_cpp_info.name}({enum_cpp_info.name} const& other) : m_tag(other.m_tag) {{\n"
            f"        switch (m_tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            enum_cpp_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            new (&m_data.{item.name}) decltype(m_data.{item.name})(other.m_data.{item.name});\n"
                f"            break;\n"
            )
        enum_cpp_defn_target.write(
            "        default:\n" "            break;\n" "        }\n" "    }\n"
        )
        # move constructor
        enum_cpp_defn_target.write(
            f"    {enum_cpp_info.name}({enum_cpp_info.name}&& other) : m_tag(other.m_tag) {{\n"
            f"        switch (m_tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            enum_cpp_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            new (&m_data.{item.name}) decltype(m_data.{item.name})(::std::move(other.m_data.{item.name}));\n"
                f"            break;\n"
            )
        enum_cpp_defn_target.write(
            "        default:\n" "            break;\n" "        }\n" "    }\n"
        )
        # copy assignment
        enum_cpp_defn_target.write(
            f"    {enum_cpp_info.name}& operator=({enum_cpp_info.name} const& other) {{\n"
            f"        if (this != &other) {{\n"
            f"            ::std::destroy_at(this);\n"
            f"            new (this) {enum_cpp_info.name}(other);\n"
            f"        }}\n"
            f"        return *this;\n"
            f"    }}\n"
        )
        # move assignment
        enum_cpp_defn_target.write(
            f"    {enum_cpp_info.name}& operator=({enum_cpp_info.name}&& other) {{\n"
            f"        if (this != &other) {{\n"
            f"            ::std::destroy_at(this);\n"
            f"            new (this) {enum_cpp_info.name}(::std::move(other));\n"
            f"        }}\n"
            f"        return *this;\n"
            f"    }}\n"
        )
        # in place constructor
        for item in enum.items:
            if item.ty_ref is None:
                enum_cpp_defn_target.write(
                    f"    {enum_cpp_info.name}(::taihe::core::static_tag_t<tag_t::{item.name}>) : m_tag(tag_t::{item.name}) {{}}\n"
                )
            else:
                enum_cpp_defn_target.write(
                    f"    template<typename... Args>\n"
                    f"    {enum_cpp_info.name}(::taihe::core::static_tag_t<tag_t::{item.name}>, Args&&... args) : m_tag(tag_t::{item.name}) {{\n"
                    f"        new (&m_data.{item.name}) decltype(m_data.{item.name})(::std::forward<Args>(args)...);\n"
                    f"    }}\n"
                )
        # creator
        enum_cpp_defn_target.write(
            f"    template<tag_t tag, typename... Args>\n"
            f"    static {enum_cpp_info.name} make(Args&&... args) {{\n"
            f"        return {enum_cpp_info.name}(::taihe::core::static_tag<tag>, ::std::forward<Args>(args)...);\n"
            f"    }}\n"
        )
        # emplacement
        enum_cpp_defn_target.write(
            f"    template<tag_t tag, typename... Args>\n"
            f"    {enum_cpp_info.name} const& emplace(Args&&... args) {{\n"
            f"        ::std::destroy_at(this);\n"
            f"        new (this) {enum_cpp_info.name}(::taihe::core::static_tag<tag>, ::std::forward<Args>(args)...);\n"
            f"        return *this;\n"
            f"    }}\n"
        )
        # non-const getter
        enum_cpp_defn_target.write(
            "    template<tag_t tag>\n" "    auto& get_ref() {\n"
        )
        for item in enum.items:
            if item.ty_ref:
                enum_cpp_defn_target.write(
                    f"        if constexpr (tag == tag_t::{item.name}) {{\n"
                    f"            return m_data.{item.name};\n"
                    f"        }}\n"
                )
        enum_cpp_defn_target.write("    }\n")
        enum_cpp_defn_target.write(
            "    template<tag_t tag>\n"
            "    auto* get_ptr() {\n"
            "        return m_tag == tag ? &get_ref<tag>() : nullptr;\n"
            "    }\n"
        )
        # const getter
        enum_cpp_defn_target.write(
            "    template<tag_t tag>\n" "    auto const& get_ref() const {\n"
        )
        for item in enum.items:
            if item.ty_ref:
                enum_cpp_defn_target.write(
                    f"        if constexpr (tag == tag_t::{item.name}) {{\n"
                    f"            return m_data.{item.name};\n"
                    f"        }}\n"
                )
        enum_cpp_defn_target.write("    }\n")
        enum_cpp_defn_target.write(
            "    template<tag_t tag>\n"
            "    auto const* get_ptr() const {\n"
            "        return m_tag == tag ? &get_ref<tag>() : nullptr;\n"
            "    }\n"
        )
        # checker
        enum_cpp_defn_target.write(
            "    template<tag_t tag>\n"
            "    bool holds() const {\n"
            "        return m_tag == tag;\n"
            "    }\n"
            "    tag_t get_tag() const {\n"
            "        return m_tag;\n"
            "    }\n"
        )
        # named
        for item in enum.items:
            enum_cpp_defn_target.write(
                f"    template<typename... Args>\n"
                f"    static {enum_cpp_info.name} make_{item.name}(Args&&... args) {{\n"
                f"        return make<tag_t::{item.name}>(::std::forward<Args>(args)...);\n"
                f"    }}\n"
                f"    template<typename... Args>\n"
                f"    {enum_cpp_info.name} const& emplace_{item.name}(Args&&... args) {{\n"
                f"        return emplace<tag_t::{item.name}>(::std::forward<Args>(args)...);\n"
                f"    }}\n"
                f"    bool holds_{item.name}() const {{\n"
                f"        return holds<tag_t::{item.name}>();\n"
                f"    }}\n"
            )
            if item.ty_ref:
                enum_cpp_defn_target.write(
                    f"    auto* get_{item.name}_ptr() {{\n"
                    f"        return get_ptr<tag_t::{item.name}>();\n"
                    f"    }}\n"
                    f"    auto const* get_{item.name}_ptr() const {{\n"
                    f"        return get_ptr<tag_t::{item.name}>();\n"
                    f"    }}\n"
                    f"    auto& get_{item.name}_ref() {{\n"
                    f"        return get_ref<tag_t::{item.name}>();\n"
                    f"    }}\n"
                    f"    auto const& get_{item.name}_ref() const {{\n"
                    f"        return get_ref<tag_t::{item.name}>();\n"
                    f"    }}\n"
                )
        # non_const visitor
        enum_cpp_defn_target.write(
            "    template<typename Visitor>\n"
            "    auto accept_template(Visitor&& visitor) {\n"
            "        switch (m_tag) {\n"
        )
        for item in enum.items:
            result = f"::taihe::core::static_tag<tag_t::{item.name}>"
            if item.ty_ref:
                result += f", m_data.{item.name}"
            enum_cpp_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            return visitor({result});\n"
            )
        enum_cpp_defn_target.write("        }\n" "    }\n")
        enum_cpp_defn_target.write(
            "    template<typename Visitor>\n"
            "    auto accept(Visitor&& visitor) {\n"
            "        switch (m_tag) {\n"
        )
        for item in enum.items:
            result = "" if item.ty_ref is None else f"m_data.{item.name}"
            enum_cpp_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            return visitor.{item.name}({result});\n"
            )
        enum_cpp_defn_target.write("        }\n" "    }\n")
        # const visitor
        enum_cpp_defn_target.write(
            "    template<typename Visitor>\n"
            "    auto accept_template(Visitor&& visitor) const {\n"
            "        switch (m_tag) {\n"
        )
        for item in enum.items:
            result = f"::taihe::core::static_tag<tag_t::{item.name}>"
            if item.ty_ref:
                result += f", m_data.{item.name}"
            enum_cpp_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            return visitor({result});\n"
            )
        enum_cpp_defn_target.write("        }\n" "    }\n")
        enum_cpp_defn_target.write(
            "    template<typename Visitor>\n"
            "    auto accept(Visitor&& visitor) const {\n"
            "        switch (m_tag) {\n"
        )
        for item in enum.items:
            result = "" if item.ty_ref is None else f"m_data.{item.name}"
            enum_cpp_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            return visitor.{item.name}({result});\n"
            )
        enum_cpp_defn_target.write("        }\n" "    }\n")
        # finally
        enum_cpp_defn_target.write(
            "private:\n" "    tag_t m_tag;\n" "    storage_t m_data;\n" "};\n" "}\n"
        )

    def gen_enum_same(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumABIInfo,
        enum_cpp_info: EnumCppInfo,
        enum_cpp_defn_target: COutputBuffer,
    ):
        result = "false"
        for item in enum.items:
            cond = f"lhs.holds_{item.name}() && rhs.holds_{item.name}()"
            if item.ty_ref:
                cond = f"{cond} && same(lhs.get_{item.name}_ref(), rhs.get_{item.name}_ref())"
            result = f"{result} || {cond}"
        enum_cpp_defn_target.write(
            f"namespace taihe::core {{\n"
            f"inline bool same_impl(adl_helper_t, {enum_cpp_info.as_param} lhs, {enum_cpp_info.as_param} rhs) {{\n"
            f"    return {result};\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_enum_hash(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumABIInfo,
        enum_cpp_info: EnumCppInfo,
        enum_cpp_defn_target: COutputBuffer,
    ):
        enum_cpp_defn_target.write(
            f"namespace taihe::core {{\n"
            f"inline auto hash_impl(adl_helper_t, {enum_cpp_info.as_param} val) -> ::std::size_t {{\n"
            f"    switch (val.get_tag()) {{\n"
            f"        ::std::size_t seed;\n"
        )
        for item in enum.items:
            val = "0x9e3779b9 + (seed << 6) + (seed >> 2)"
            if item.ty_ref:
                val = f"{val} + hash(val.get_{item.name}_ref())"
            enum_cpp_defn_target.write(
                f"    case {enum_cpp_info.full_name}::tag_t::{item.name}:\n"
                f"        seed = (::std::size_t){enum_cpp_info.full_name}::tag_t::{item.name};\n"
                f"        return seed ^ ({val});\n"
            )
        enum_cpp_defn_target.write("    }\n" "}\n" "}\n")

    def gen_enum_type_traits(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumABIInfo,
        enum_cpp_info: EnumCppInfo,
        enum_cpp_defn_target: COutputBuffer,
    ):
        enum_cpp_defn_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"struct as_abi<{enum_cpp_info.as_owner}> {{\n"
            f"    using type = {enum_abi_info.as_owner};\n"
            f"}};\n"
            f"template<>\n"
            f"struct as_abi<{enum_cpp_info.as_param}> {{\n"
            f"    using type = {enum_abi_info.as_param};\n"
            f"}};\n"
            f"template<>\n"
            f"struct as_param<{enum_cpp_info.as_owner}> {{\n"
            f"    using type = {enum_cpp_info.as_param};\n"
            f"}};\n"
            f"}}\n"
        )

    def gen_iface_files(
        self,
        iface: IfaceDecl,
        pkg_cpp_target: COutputBuffer,
    ):
        iface_abi_info = IfaceABIInfo.get(self.am, iface)
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        self.gen_iface_decl_file(
            iface,
            iface_abi_info,
            iface_cpp_info,
        )
        self.gen_iface_defn_file(
            iface,
            iface_abi_info,
            iface_cpp_info,
        )
        self.gen_iface_impl_file(
            iface,
            iface_abi_info,
            iface_cpp_info,
        )
        pkg_cpp_target.include(iface_cpp_info.impl_header)

    def gen_iface_decl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
    ):
        iface_cpp_decl_target = COutputBuffer.create(
            self.tm, f"include/{iface_cpp_info.decl_header}", True
        )
        iface_cpp_decl_target.write(
            f"namespace {iface_cpp_info.weakspace} {{\n"
            f"struct {iface_cpp_info.weak_name};\n"
            f"}}\n"
            f"namespace {iface_cpp_info.namespace} {{\n"
            f"struct {iface_cpp_info.norm_name};\n"
            f"}}\n"
        )

    def gen_iface_defn_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
    ):
        iface_cpp_defn_target = COutputBuffer.create(
            self.tm, f"include/{iface_cpp_info.defn_header}", True
        )
        iface_cpp_defn_target.include("core/object.hpp")
        iface_cpp_defn_target.include(iface_cpp_info.decl_header)
        iface_cpp_defn_target.include(iface_abi_info.defn_header)
        self.gen_iface_view_defn(
            iface,
            iface_abi_info,
            iface_cpp_info,
            iface_cpp_defn_target,
        )
        self.gen_iface_holder_defn(
            iface,
            iface_abi_info,
            iface_cpp_info,
            iface_cpp_defn_target,
        )
        self.gen_iface_type_traits(
            iface,
            iface_abi_info,
            iface_cpp_info,
            iface_cpp_defn_target,
        )

    def gen_iface_view_defn(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
        iface_cpp_defn_target: COutputBuffer,
    ):
        iface_cpp_defn_target.write(
            f"namespace {iface_cpp_info.weakspace} {{\n"
            f"struct {iface_cpp_info.weak_name} {{\n"
            f"    static constexpr bool is_holder = false;\n"
        )
        # base infos
        iface_cpp_defn_target.write(
            f"    static constexpr void const* iid = &{iface_abi_info.iid};\n"
            f"    using vtable_t = {iface_abi_info.vtable};\n"
        )
        # user methods
        iface_cpp_defn_target.write("    struct virtual_type {\n")
        for method in iface.methods:
            method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
            params_cpp = []
            for param in method.params:
                type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
                iface_cpp_defn_target.include(*type_cpp_info.decl_headers)
                params_cpp.append(f"{type_cpp_info.as_param} {param.name}")
            params_cpp_str = ", ".join(params_cpp)
            if return_ty_ref := method.return_ty_ref:
                type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
                iface_cpp_defn_target.include(*type_cpp_info.decl_headers)
                cpp_return_ty_name = type_cpp_info.as_owner
            else:
                cpp_return_ty_name = "void"
            iface_cpp_defn_target.write(
                f"        {cpp_return_ty_name} {method_cpp_info.call_name}({params_cpp_str}) const;\n"
            )
        iface_cpp_defn_target.write("    };\n")
        # author methods
        iface_cpp_defn_target.write(
            "    template<typename Impl>\n" "    struct methods_impl {\n"
        )
        for method in iface.methods:
            params_abi = [f"{iface_abi_info.as_param} tobj"]
            for param in method.params:
                type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
                params_abi.append(f"{type_abi_info.as_param} {param.name}")
            params_abi_str = ", ".join(params_abi)
            if return_ty_ref := method.return_ty_ref:
                type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
                abi_return_ty_name = type_abi_info.as_owner
            else:
                abi_return_ty_name = "void"
            iface_cpp_defn_target.write(
                f"        static {abi_return_ty_name} {method.name}({params_abi_str});\n"
            )
        iface_cpp_defn_target.write("    };\n")
        # FTable implementation
        iface_cpp_defn_target.write(
            f"    template<typename Impl>\n"
            f"    static constexpr {iface_abi_info.ftable} ftbl_impl = {{\n"
        )
        for method in iface.methods:
            iface_cpp_defn_target.write(
                f"        .{method.name} = &methods_impl<Impl>::{method.name},\n"
            )
        iface_cpp_defn_target.write("    };\n")
        # VTable implementation
        iface_cpp_defn_target.write(
            f"    template<typename Impl>\n"
            f"    static constexpr {iface_abi_info.vtable} vtbl_impl = {{\n"
        )
        for ancestor_info in iface_abi_info.ancestor_list:
            ancestor_cpp_info = IfaceCppInfo.get(self.am, ancestor_info.iface)
            iface_cpp_defn_target.write(
                f"        .{ancestor_info.ftbl_ptr} = &{ancestor_cpp_info.full_weak_name}::template ftbl_impl<Impl>,\n"
            )
        iface_cpp_defn_target.write("    };\n")
        # IdMap implementation
        iface_cpp_defn_target.write(
            f"    template<typename Impl>\n"
            f"    static constexpr IdMapItem idmap_impl[{len(iface_abi_info.ancestor_dict)}] = {{\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            ancestor_abi_info = IfaceABIInfo.get(self.am, ancestor)
            iface_cpp_defn_target.write(
                f"        {{&{ancestor_abi_info.iid}, &vtbl_impl<Impl>.{info.ftbl_ptr}}},\n"
            )
        iface_cpp_defn_target.write("    };\n")
        # class field
        iface_cpp_defn_target.write(f"    {iface_abi_info.as_owner} m_handle;\n")
        # class methods
        iface_cpp_defn_target.write(
            "    explicit operator bool() const& {\n"
            "        return m_handle.vtbl_ptr;\n"
            "    }\n"
            "    virtual_type const& operator*() const {\n"
            "        return *reinterpret_cast<virtual_type const*>(&m_handle);\n"
            "    }\n"
            "    virtual_type const* operator->() const {\n"
            "        return reinterpret_cast<virtual_type const*>(&m_handle);\n"
            "    }\n"
        )
        # convert methods
        iface_cpp_defn_target.write(
            f"    explicit {iface_cpp_info.weak_name}({iface_abi_info.as_param} handle) : m_handle(handle) {{}}\n"
            f"    explicit {iface_cpp_info.weak_name}(::taihe::core::data_view other)\n"
            f"        : {iface_cpp_info.weak_name}({iface_abi_info.dynamic_cast}(other.data_ptr)) {{}}\n"
            f"    operator ::taihe::core::data_view() const& {{\n"
            f"        {iface_abi_info.as_owner} ret_handle = m_handle;\n"
            f"        return ::taihe::core::data_view(ret_handle.data_ptr);\n"
            f"    }}\n"
            f"    operator ::taihe::core::data_holder() const& {{\n"
            f"        {iface_abi_info.as_owner} ret_handle = {iface_abi_info.copy_func}(m_handle);\n"
            f"        return ::taihe::core::data_holder(ret_handle.data_ptr);\n"
            f"    }}\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_cpp_info = IfaceCppInfo.get(self.am, ancestor)
            iface_cpp_defn_target.include(ancestor_cpp_info.defn_header)
            iface_cpp_defn_target.write(
                f"    operator {ancestor_cpp_info.full_weak_name}() const& {{\n"
                f"        {iface_abi_info.as_owner} ret_handle = m_handle;\n"
                f"        return {ancestor_cpp_info.full_weak_name}({info.static_cast}(ret_handle));\n"
                f"    }}\n"
                f"    operator {ancestor_cpp_info.full_norm_name}() const& {{\n"
                f"        {iface_abi_info.as_owner} ret_handle = {iface_abi_info.copy_func}(m_handle);\n"
                f"        return {ancestor_cpp_info.full_norm_name}({info.static_cast}(ret_handle));\n"
                f"    }}\n"
            )
        iface_cpp_defn_target.write("};\n" "}\n")

    def gen_iface_holder_defn(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
        iface_cpp_defn_target: COutputBuffer,
    ):
        iface_cpp_defn_target.write(
            f"namespace {iface_cpp_info.namespace} {{\n"
            f"struct {iface_cpp_info.norm_name} : public {iface_cpp_info.full_weak_name} {{\n"
            f"    static constexpr bool is_holder = true;\n"
        )
        # convert methods
        iface_cpp_defn_target.write(
            f"    explicit {iface_cpp_info.norm_name}({iface_abi_info.as_owner} handle) : {iface_cpp_info.full_weak_name}(handle) {{}}\n"
            f"    {iface_cpp_info.norm_name}& operator=({iface_cpp_info.full_norm_name} other) {{\n"
            f"        ::std::swap(m_handle, other.m_handle);\n"
            f"        return *this;\n"
            f"    }}\n"
            f"    ~{iface_cpp_info.norm_name}() {{\n"
            f"        {iface_abi_info.drop_func}(m_handle);\n"
            f"    }}\n"
            f"    {iface_cpp_info.norm_name}({iface_cpp_info.full_weak_name} const& other)\n"
            f"        : {iface_cpp_info.norm_name}({iface_abi_info.copy_func}(other.m_handle)) {{}}\n"
            f"    {iface_cpp_info.norm_name}({iface_cpp_info.full_norm_name} const& other)\n"
            f"        : {iface_cpp_info.norm_name}({iface_abi_info.copy_func}(other.m_handle)) {{}}\n"
            f"    {iface_cpp_info.norm_name}({iface_cpp_info.full_norm_name} && other)\n"
            f"        : {iface_cpp_info.norm_name}(other.m_handle) {{\n"
            f"        other.m_handle.data_ptr = nullptr;\n"
            f"    }}\n"
            f"    explicit {iface_cpp_info.norm_name}(::taihe::core::data_holder other)\n"
            f"        : {iface_cpp_info.norm_name}({iface_abi_info.dynamic_cast}(other.data_ptr)) {{\n"
            f"        other.data_ptr = nullptr;\n"
            f"    }}\n"
            f"    operator ::taihe::core::data_view() const& {{\n"
            f"        {iface_abi_info.as_owner} ret_handle = m_handle;\n"
            f"        return ::taihe::core::data_view(ret_handle.data_ptr);\n"
            f"    }}\n"
            f"    operator ::taihe::core::data_holder() const& {{\n"
            f"        {iface_abi_info.as_owner} ret_handle = {iface_abi_info.copy_func}(m_handle);\n"
            f"        return ::taihe::core::data_holder(ret_handle.data_ptr);\n"
            f"    }}\n"
            f"    operator ::taihe::core::data_holder() && {{\n"
            f"        {iface_abi_info.as_owner} ret_handle = m_handle;\n"
            f"        m_handle.data_ptr = nullptr;\n"
            f"        return ::taihe::core::data_holder(ret_handle.data_ptr);\n"
            f"    }}\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_cpp_info = IfaceCppInfo.get(self.am, ancestor)
            iface_cpp_defn_target.write(
                f"    operator {ancestor_cpp_info.full_weak_name}() const& {{\n"
                f"        {iface_abi_info.as_owner} ret_handle = m_handle;\n"
                f"        return {ancestor_cpp_info.full_weak_name}({info.static_cast}(ret_handle));\n"
                f"    }}\n"
                f"    operator {ancestor_cpp_info.full_norm_name}() const& {{\n"
                f"        {iface_abi_info.as_owner} ret_handle = {iface_abi_info.copy_func}(m_handle);\n"
                f"        return {ancestor_cpp_info.full_norm_name}({info.static_cast}(ret_handle));\n"
                f"    }}\n"
                f"    operator {ancestor_cpp_info.full_norm_name}() && {{\n"
                f"        {iface_abi_info.as_owner} ret_handle = m_handle;\n"
                f"        m_handle.data_ptr = nullptr;\n"
                f"        return {ancestor_cpp_info.full_norm_name}({info.static_cast}(ret_handle));\n"
                f"    }}\n"
            )
        iface_cpp_defn_target.write("};\n" "}\n")

    def gen_iface_type_traits(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
        iface_cpp_defn_target: COutputBuffer,
    ):
        iface_cpp_defn_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"struct as_abi<{iface_cpp_info.as_owner}> {{\n"
            f"    using type = {iface_abi_info.as_owner};\n"
            f"}};\n"
            f"template<>\n"
            f"struct as_abi<{iface_cpp_info.as_param}> {{\n"
            f"    using type = {iface_abi_info.as_param};\n"
            f"}};\n"
            f"template<>\n"
            f"struct as_param<{iface_cpp_info.as_owner}> {{\n"
            f"    using type = {iface_cpp_info.as_param};\n"
            f"}};\n"
            f"}}\n"
        )

    def gen_iface_impl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
    ):
        iface_cpp_impl_target = COutputBuffer.create(
            self.tm, f"include/{iface_cpp_info.impl_header}", True
        )
        iface_cpp_impl_target.include(iface_cpp_info.defn_header)
        iface_cpp_impl_target.include(iface_abi_info.impl_header)
        self.gen_iface_user_methods(
            iface,
            iface_abi_info,
            iface_cpp_info,
            iface_cpp_impl_target,
        )
        self.gen_iface_author_methods(
            iface,
            iface_abi_info,
            iface_cpp_info,
            iface_cpp_impl_target,
        )

    def gen_iface_user_methods(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
        iface_cpp_impl_target: COutputBuffer,
    ):
        for method in iface.methods:
            method_abi_info = IfaceMethodABIInfo.get(self.am, method)
            method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
            params_cpp = []
            args_into_abi = [
                f"*reinterpret_cast<{iface_abi_info.mangled_name} const*>(this)"
            ]
            for param in method.params:
                type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
                iface_cpp_impl_target.include(*type_cpp_info.impl_headers)
                params_cpp.append(f"{type_cpp_info.as_param} {param.name}")
                args_into_abi.append(type_cpp_info.pass_into_abi(param.name))
            params_cpp_str = ", ".join(params_cpp)
            args_into_abi_str = ", ".join(args_into_abi)
            abi_result = f"{method_abi_info.mangled_name}({args_into_abi_str})"
            if return_ty_ref := method.return_ty_ref:
                type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
                iface_cpp_impl_target.include(*type_cpp_info.impl_headers)
                cpp_return_ty_name = type_cpp_info.as_owner
                cpp_result = type_cpp_info.return_from_abi(abi_result)
            else:
                cpp_return_ty_name = "void"
                cpp_result = abi_result
            iface_cpp_impl_target.write(
                f"namespace {iface_cpp_info.weakspace} {{\n"
                f"inline {cpp_return_ty_name} {iface_cpp_info.weak_name}::virtual_type::{method_cpp_info.call_name}({params_cpp_str}) const {{\n"
                f"    return {cpp_result};\n"
                f"}}\n"
                f"}}\n"
            )

    def gen_iface_author_methods(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_cpp_info: IfaceCppInfo,
        iface_cpp_impl_target: COutputBuffer,
    ):
        for method in iface.methods:
            method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
            params_abi = [f"{iface_abi_info.as_param} tobj"]
            args_from_abi = []
            for param in method.params:
                type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
                type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
                params_abi.append(f"{type_abi_info.as_param} {param.name}")
                args_from_abi.append(type_cpp_info.pass_from_abi(param.name))
            params_abi_str = ", ".join(params_abi)
            args_from_abi_str = ", ".join(args_from_abi)
            cpp_result = f"::taihe::core::cast_data_ptr<Impl>(tobj.data_ptr)->{method_cpp_info.impl_name}({args_from_abi_str})"
            if return_ty_ref := method.return_ty_ref:
                type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
                type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
                abi_return_ty_name = type_abi_info.as_owner
                abi_result = type_cpp_info.return_into_abi(cpp_result)
            else:
                abi_return_ty_name = "void"
                abi_result = cpp_result
            iface_cpp_impl_target.write(
                f"namespace {iface_cpp_info.weakspace} {{\n"
                f"template<typename Impl>\n"
                f"{abi_return_ty_name} {iface_cpp_info.weak_name}::methods_impl<Impl>::{method.name}({params_abi_str}) {{\n"
                f"    return {abi_result};\n"
                f"}}\n"
                f"}}\n"
            )
