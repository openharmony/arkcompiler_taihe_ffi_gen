from typing import Any, Optional

from typing_extensions import override

from taihe.codegen.abi_generator import (
    BaseFuncDeclABIInfo,
    COutputBuffer,
    EnumDeclABIInfo,
    EnumItemDeclABIInfo,
    IfaceDeclABIInfo,
    PackageABIInfo,
    StructDeclABIInfo,
    TypeABIInfo,
)
from taihe.semantics.declarations import (
    BaseFuncDecl,
    EnumDecl,
    GlobFuncDecl,
    IfaceDecl,
    Package,
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
    U8,
    U16,
    U32,
    U64,
    ScalarType,
    SpecialType,
    Type,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager


class PackageCppProjInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        segments = p.segments
        self.header = f"{p.name}.proj.hpp"
        self.namespace = "::".join(segments)
        self.param_namespace = "::".join(["param", *segments])


class BaseFuncDeclCppProjInfo(AbstractAnalysis[BaseFuncDecl]):
    def __init__(self, am: AnalysisManager, f: BaseFuncDecl) -> None:
        self.name = f.name
        if f.return_ty_ref is None:
            self.return_ty_header_decl = None
            self.return_ty_header_defn = None
            self.return_ty_name = "void"
            self.return_from_abi = lambda val: val
            self.return_into_abi = lambda val: val
        else:
            cpp_return_ty_info = TypeCppProjInfo.get(am, f.return_ty_ref.resolved_ty)
            self.return_ty_header_decl = cpp_return_ty_info.header_decl
            self.return_ty_header_defn = cpp_return_ty_info.header_defn
            self.return_ty_name = cpp_return_ty_info.as_owner
            self.return_from_abi = cpp_return_ty_info.return_from_abi
            self.return_into_abi = cpp_return_ty_info.return_into_abi


class StructDeclCppProjInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        abi_info = StructDeclABIInfo.get(am, d)
        p = d.parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.proj.hpp"
        self.name = d.name
        self.owner_full_name = "::" + "::".join(segments)
        self.param_full_name = "::param::" + "::".join(segments)
        self.pass_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.param_full_name}, {abi_info.as_param}>({val})"
        )
        self.pass_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.param_full_name}, {abi_info.as_param}>({val})"
        )
        self.return_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.owner_full_name}, {abi_info.as_owner}>({val})"
        )
        self.return_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.owner_full_name}, {abi_info.as_owner}>({val})"
        )


class EnumDeclCppProjInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        abi_info = EnumDeclABIInfo.get(am, d)
        p = d.parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.proj.hpp"
        self.name = d.name
        self.owner_full_name = "::" + "::".join(segments)
        self.param_full_name = "::param::" + "::".join(segments)
        self.pass_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.param_full_name}, {abi_info.as_param}>({val})"
        )
        self.pass_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.param_full_name}, {abi_info.as_param}>({val})"
        )
        self.return_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.owner_full_name}, {abi_info.as_owner}>({val})"
        )
        self.return_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.owner_full_name}, {abi_info.as_owner}>({val})"
        )


class IfaceDeclCppProjInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        abi_info = IfaceDeclABIInfo.get(am, d)
        p = d.parent
        assert p
        segments = d.segments
        self.header_decl = f"{p.name}.{d.name}.proj.0.hpp"
        self.header_defn = f"{p.name}.{d.name}.proj.1.hpp"
        self.header_impl = f"{p.name}.{d.name}.proj.2.hpp"
        self.name = d.name
        self.owner_full_name = "::" + "::".join(segments)
        self.param_full_name = "::param::" + "::".join(segments)
        self.pass_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.param_full_name}, {abi_info.as_param}>({val})"
        )
        self.pass_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.param_full_name}, {abi_info.as_param}>({val})"
        )
        self.return_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.owner_full_name}, {abi_info.as_owner}>({val})"
        )
        self.return_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.owner_full_name}, {abi_info.as_owner}>({val})"
        )


class TypeCppProjInfo(AbstractAnalysis[Optional[Type]], TypeVisitor):
    def __init__(self, am: AnalysisManager, t: Optional[Type]) -> None:
        self.am = am
        self.header_decl = None
        self.header_defn = None
        self.as_owner = None
        self.as_param = None
        self.pass_from_abi = lambda val: val
        self.pass_into_abi = lambda val: val
        self.return_from_abi = lambda val: val
        self.return_into_abi = lambda val: val
        self.handle_type(t)

    @override
    def visit_enum_decl(self, d: EnumDecl) -> Any:
        enum_cpp_proj_info = EnumDeclCppProjInfo.get(self.am, d)
        self.header_decl = enum_cpp_proj_info.header
        self.header_defn = enum_cpp_proj_info.header
        self.as_owner = enum_cpp_proj_info.owner_full_name
        self.as_param = enum_cpp_proj_info.param_full_name
        self.pass_from_abi = enum_cpp_proj_info.pass_from_abi
        self.pass_into_abi = enum_cpp_proj_info.pass_into_abi
        self.return_from_abi = enum_cpp_proj_info.return_from_abi
        self.return_into_abi = enum_cpp_proj_info.return_into_abi

    @override
    def visit_struct_decl(self, d: StructDecl) -> Any:
        struct_cpp_proj_info = StructDeclCppProjInfo.get(self.am, d)
        self.header_decl = struct_cpp_proj_info.header
        self.header_defn = struct_cpp_proj_info.header
        self.as_owner = struct_cpp_proj_info.owner_full_name
        self.as_param = struct_cpp_proj_info.param_full_name
        self.pass_from_abi = struct_cpp_proj_info.pass_from_abi
        self.pass_into_abi = struct_cpp_proj_info.pass_into_abi
        self.return_from_abi = struct_cpp_proj_info.return_from_abi
        self.return_into_abi = struct_cpp_proj_info.return_into_abi

    @override
    def visit_iface_decl(self, d: IfaceDecl) -> Any:
        iface_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, d)
        self.header_decl = iface_cpp_proj_info.header_decl
        self.header_defn = iface_cpp_proj_info.header_defn
        self.as_owner = iface_cpp_proj_info.owner_full_name
        self.as_param = iface_cpp_proj_info.param_full_name
        self.pass_from_abi = iface_cpp_proj_info.pass_from_abi
        self.pass_into_abi = iface_cpp_proj_info.pass_into_abi
        self.return_from_abi = iface_cpp_proj_info.return_from_abi
        self.return_into_abi = iface_cpp_proj_info.return_into_abi

    def visit_scalar_type(self, t: ScalarType):
        res = self.as_param = self.as_owner = {
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
        self.as_param = res
        self.as_owner = res
        if res is None:
            raise ValueError

    def visit_special_type(self, t: SpecialType) -> Any:
        if t == STRING:
            self.header_decl = "core/string.hpp"
            self.header_defn = "core/string.hpp"
            self.as_owner = "::taihe::core::string"
            self.as_param = "::taihe::core::string_view"
            self.pass_from_abi = (
                lambda val: f"::taihe::core::from_abi<{self.as_param}, TString*>({val})"
            )
            self.pass_into_abi = (
                lambda val: f"::taihe::core::into_abi<{self.as_param}, TString*>({val})"
            )
            self.return_from_abi = (
                lambda val: f"::taihe::core::from_abi<{self.as_owner}, TString*>({val})"
            )
            self.return_into_abi = (
                lambda val: f"::taihe::core::into_abi<{self.as_owner}, TString*>({val})"
            )
        else:
            raise ValueError


class CppProjCodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: Package):
        pkg_cpp_proj_info = PackageCppProjInfo.get(self.am, pkg)
        pkg_cpp_proj_target = COutputBuffer.create(
            self.tm, f"include/{pkg_cpp_proj_info.header}", True
        )
        pkg_abi_info = PackageABIInfo.get(self.am, pkg)
        pkg_cpp_proj_target.include("taihe/common.hpp")
        pkg_cpp_proj_target.include(f"{pkg_abi_info.header}")
        for struct in pkg.structs:
            self.gen_struct_file(struct, pkg_cpp_proj_target, pkg_cpp_proj_info)
        for enum in pkg.enums:
            self.gen_enum_file(enum, pkg_cpp_proj_target, pkg_cpp_proj_info)
        for iface in pkg.interfaces:
            self.gen_iface_files(iface, pkg_cpp_proj_target, pkg_cpp_proj_info)
        for func in pkg.functions:
            self.gen_func(func, pkg_cpp_proj_target, pkg_cpp_proj_info)

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_cpp_proj_target: COutputBuffer,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        func_cpp_proj_info = BaseFuncDeclCppProjInfo.get(self.am, func)
        func_abi_info = BaseFuncDeclABIInfo.get(self.am, func)
        cpp_params = []
        args_into_abi = []
        for param in func.params:
            type_cpp_proj_info = TypeCppProjInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_cpp_proj_target.include(type_cpp_proj_info.header_defn)
            cpp_params.append(f"{type_cpp_proj_info.as_param} {param.name}")
            args_into_abi.append(type_cpp_proj_info.pass_into_abi(param.name))
        cpp_params_str = ", ".join(cpp_params)
        args_into_abi_str = ",".join(args_into_abi)
        pkg_cpp_proj_target.include(func_cpp_proj_info.return_ty_header_defn)
        result = func_cpp_proj_info.return_from_abi(
            f"{func_abi_info.name}({args_into_abi_str})"
        )
        pkg_cpp_proj_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"inline {func_cpp_proj_info.return_ty_name} {func_cpp_proj_info.name}({cpp_params_str}) {{\n"
            f"    return {result};\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_struct_file(
        self,
        struct: StructDecl,
        pkg_cpp_proj_target: COutputBuffer,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        struct_abi_info = StructDeclABIInfo.get(self.am, struct)
        struct_cpp_proj_info = StructDeclCppProjInfo.get(self.am, struct)
        struct_cpp_proj_target = COutputBuffer.create(
            self.tm, f"include/{struct_cpp_proj_info.header}", True
        )
        struct_cpp_proj_target.include("taihe/common.hpp")
        struct_cpp_proj_target.include(struct_abi_info.header)
        self.gen_struct_decl(
            struct,
            struct_cpp_proj_target,
            struct_cpp_proj_info,
            pkg_cpp_proj_info,
        )
        self.gen_struct_trans_func(
            struct,
            struct_cpp_proj_target,
            struct_cpp_proj_info,
            struct_abi_info,
        )
        pkg_cpp_proj_target.include(struct_cpp_proj_info.header)

    def gen_struct_decl(
        self,
        struct: StructDecl,
        struct_cpp_proj_target: COutputBuffer,
        struct_cpp_proj_info: StructDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        struct_cpp_proj_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"struct {struct_cpp_proj_info.name} {{\n"
        )
        for field in struct.fields:
            ty_info = TypeCppProjInfo.get(self.am, field.ty_ref.resolved_ty)
            struct_cpp_proj_target.include(ty_info.header_defn)
            struct_cpp_proj_target.write(f"    {ty_info.as_owner} {field.name};\n")
        struct_cpp_proj_target.write(
            f"}};\n"
            f"}}\n"
            f"namespace {pkg_cpp_proj_info.param_namespace} {{\n"
            f"using {struct_cpp_proj_info.name} = {struct_cpp_proj_info.owner_full_name} const&;\n"
            f"}}\n"
        )

    def gen_struct_trans_func(
        self,
        struct: StructDecl,
        struct_cpp_proj_target: COutputBuffer,
        struct_cpp_proj_info: StructDeclCppProjInfo,
        struct_abi_info: StructDeclABIInfo,
    ):
        struct_cpp_proj_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"inline {struct_abi_info.as_owner} into_abi({struct_cpp_proj_info.owner_full_name} val){{\n"
            f"    return {{\n"
        )
        for field in struct.fields:
            ty_cpp_proj_info = TypeCppProjInfo.get(self.am, field.ty_ref.resolved_ty)
            result = ty_cpp_proj_info.return_into_abi(f"std::move(val.{field.name})")
            struct_cpp_proj_target.write(f"        {result},\n")
        struct_cpp_proj_target.write(
            f"    }};\n"
            f"}}\n"
            f"template<>\n"
            f"inline {struct_cpp_proj_info.owner_full_name} from_abi({struct_abi_info.as_owner} val){{\n"
            f"    return {{\n"
        )
        for field in struct.fields:
            ty_cpp_proj_info = TypeCppProjInfo.get(self.am, field.ty_ref.resolved_ty)
            result = ty_cpp_proj_info.return_from_abi(f"val.{field.name}")
            struct_cpp_proj_target.write(f"        {result},\n")
        struct_cpp_proj_target.write(
            f"    }};\n"
            f"}}\n"
            f"template<>\n"
            f"inline {struct_abi_info.as_param} into_abi({struct_cpp_proj_info.param_full_name} val){{\n"
            f"    return reinterpret_cast<{struct_abi_info.as_param}>(&val);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {struct_cpp_proj_info.param_full_name} from_abi({struct_abi_info.as_param} val){{\n"
            f"    return reinterpret_cast<{struct_cpp_proj_info.param_full_name}>(*val);\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_enum_file(
        self,
        enum: EnumDecl,
        pkg_cpp_proj_target: COutputBuffer,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        enum_cpp_proj_info = EnumDeclCppProjInfo.get(self.am, enum)
        enum_abi_info = EnumDeclABIInfo.get(self.am, enum)
        enum_cpp_proj_target = COutputBuffer.create(
            self.tm, f"include/{enum_cpp_proj_info.header}", True
        )
        enum_cpp_proj_target.include("taihe/common.hpp")
        enum_cpp_proj_target.include(enum_abi_info.header)
        self.gen_enum_decl(
            enum,
            enum_cpp_proj_target,
            enum_cpp_proj_info,
            enum_abi_info,
            pkg_cpp_proj_info,
        )
        self.gen_enum_trans_func(
            enum,
            enum_cpp_proj_target,
            enum_cpp_proj_info,
            enum_abi_info,
        )
        pkg_cpp_proj_target.include(enum_cpp_proj_info.header)

    def gen_enum_decl(
        self,
        enum: EnumDecl,
        enum_cpp_proj_target: COutputBuffer,
        enum_cpp_proj_info: EnumDeclCppProjInfo,
        enum_abi_info: EnumDeclABIInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        enum_cpp_proj_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"struct {enum_cpp_proj_info.name} {{\n"
            f"    enum class TagType {{\n"
        )
        for item in enum.items:
            enum_cpp_proj_target.write(f"        {item.name} = {item.value},\n")
        enum_cpp_proj_target.write(
            "    };\n"
            "    union DataType {\n"
            "        DataType() {}\n"
            "        ~DataType() {}\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            ty_info = TypeCppProjInfo.get(self.am, item.ty_ref.resolved_ty)
            enum_cpp_proj_target.include(ty_info.header_defn)
            enum_cpp_proj_target.write(f"        {ty_info.as_owner} {item.name};\n")
        enum_cpp_proj_target.write(
            f"    }};\n"
            f"    ~{enum_cpp_proj_info.name}() {{\n"
            f"        switch (this->tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            enum_cpp_proj_target.write(
                f"        case TagType::{item.name}:\n"
                f"            this->data.{item.name}.~decltype(this->data.{item.name})();\n"
                f"            break;\n"
            )
        enum_cpp_proj_target.write(
            f"        default:\n"
            f"            break;\n"
            f"        }}\n"
            f"    }}\n"
            f"    {enum_cpp_proj_info.name}({enum_cpp_proj_info.name} const& other) : tag(other.tag) {{\n"
            f"        switch (this->tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            enum_cpp_proj_target.write(
                f"        case TagType::{item.name}:\n"
                f"            new (&this->data.{item.name}) decltype(this->data.{item.name})(other.data.{item.name});\n"
                f"            break;\n"
            )
        enum_cpp_proj_target.write(
            f"        default:\n"
            f"            break;\n"
            f"        }}\n"
            f"    }}\n"
            f"    {enum_cpp_proj_info.name}({enum_cpp_proj_info.name}&& other) : tag(other.tag) {{\n"
            f"        switch (this->tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            enum_cpp_proj_target.write(
                f"        case TagType::{item.name}:\n"
                f"            new (&this->data.{item.name}) decltype(this->data.{item.name})(std::move(other.data.{item.name}));\n"
                f"            break;\n"
            )
        enum_cpp_proj_target.write(
            f"        default:\n"
            f"            break;\n"
            f"        }}\n"
            f"    }}\n"
            f"    template<TagType tag, typename... Args>\n"
            f"    {enum_cpp_proj_info.name}(::taihe::core::ConstexprTagType<tag>, Args&&... args) : tag(tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            enum_cpp_proj_target.write(
                f"        if constexpr (tag == TagType::{item.name}) {{\n"
                f"            new (&this->data.{item.name}) decltype(this->data.{item.name})(std::forward<Args>(args)...);\n"
                f"        }}\n"
            )
        enum_cpp_proj_target.write(
            f"    }}\n"
            f"    {enum_cpp_proj_info.name} const& operator=({enum_cpp_proj_info.name} const& other) {{\n"
            f"        if (this != &other) {{\n"
            f"            this->~{enum_cpp_proj_info.name}();\n"
            f"            new (this) {enum_cpp_proj_info.name}(other);\n"
            f"        }}\n"
            f"        return *this;\n"
            f"    }}\n"
            f"    {enum_cpp_proj_info.name} const& operator=({enum_cpp_proj_info.name}&& other) {{\n"
            f"        if (this != &other) {{\n"
            f"            this->~{enum_cpp_proj_info.name}();\n"
            f"            new (this) {enum_cpp_proj_info.name}(std::move(other));\n"
            f"        }}\n"
            f"        return *this;\n"
            f"    }}\n"
            f"    template<TagType tag, typename... Args>\n"
            f"    {enum_cpp_proj_info.name} const& emplace(Args&&... args) {{\n"
            f"        this->~{enum_cpp_proj_info.name}();\n"
            f"        this->tag = tag;\n"
            f"        new (this) {enum_cpp_proj_info.name}(::taihe::core::ConstexprTag<tag>, std::forward<Args>(args)...);\n"
            f"        return *this;\n"
            f"    }}\n"
            f"    template<TagType tag>\n"
            f"    auto* get_raw_ptr() {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                enum_cpp_proj_target.write(
                    f"        if constexpr (tag == TagType::{item.name}) {{\n"
                    f"            return (void*)&this->data;\n"
                    f"        }}\n"
                )
                continue
            enum_cpp_proj_target.write(
                f"        if constexpr (tag == TagType::{item.name}) {{\n"
                f"            return &this->data.{item.name};\n"
                f"        }}\n"
            )
        enum_cpp_proj_target.write(
            "    }\n"
            "    template<TagType tag>\n"
            "    auto const* get_raw_ptr() const {\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                enum_cpp_proj_target.write(
                    f"        if constexpr (tag == TagType::{item.name}) {{\n"
                    f"            return (void const*)&this->data;\n"
                    f"        }}\n"
                )
                continue
            enum_cpp_proj_target.write(
                f"        if constexpr (tag == TagType::{item.name}) {{\n"
                f"            return &this->data.{item.name};\n"
                f"        }}\n"
            )
        enum_cpp_proj_target.write(
            f"    }}\n"
            f"    template<TagType tag>\n"
            f"    auto* get_ptr() {{\n"
            f"        return this->tag == tag ? get_raw_ptr<tag>() : nullptr;\n"
            f"    }}\n"
            f"    template<TagType tag>\n"
            f"    auto const* get_ptr() const {{\n"
            f"        return this->tag == tag ? get_raw_ptr<tag>() : nullptr;\n"
            f"    }}\n"
            f"    TagType get_tag() const {{\n"
            f"        return this->tag;\n"
            f"    }}\n"
            f"private:\n"
            f"    TagType tag;\n"
            f"    DataType data;\n"
            f"    template<typename cpp_t, typename abi_t>\n"
            f"    friend abi_t taihe::core::into_abi(cpp_t val);\n"
            f"    template<typename cpp_t, typename abi_t>\n"
            f"    friend cpp_t taihe::core::from_abi(abi_t val);\n"
            f"}};\n"
            f"}}\n"
            f"namespace {pkg_cpp_proj_info.param_namespace} {{\n"
            f"using {enum_cpp_proj_info.name} = {enum_cpp_proj_info.owner_full_name} const&;\n"
            f"}}\n"
        )

    def gen_enum_trans_func(
        self,
        enum: EnumDecl,
        enum_cpp_proj_target: COutputBuffer,
        enum_cpp_proj_info: EnumDeclCppProjInfo,
        enum_abi_info: EnumDeclABIInfo,
    ):
        enum_cpp_proj_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"inline {enum_abi_info.as_owner} into_abi({enum_cpp_proj_info.owner_full_name} val){{\n"
            f"    {enum_abi_info.as_owner} result;\n"
            f"    switch (val.tag) {{\n"
        )
        for item in enum.items:
            enum_item_abi_info = EnumItemDeclABIInfo.get(self.am, item)
            if item.ty_ref is None:
                enum_cpp_proj_target.write(
                    f"    case {enum_cpp_proj_info.owner_full_name}::TagType::{item.name}:\n"
                    f"        result.tag = {enum_item_abi_info.name};\n"
                    f"        break;\n"
                )
                continue
            ty_cpp_proj_info = TypeCppProjInfo.get(self.am, item.ty_ref.resolved_ty)
            result = ty_cpp_proj_info.return_into_abi(
                f"std::move(val.data.{item.name})"
            )
            enum_cpp_proj_target.write(
                f"    case {enum_cpp_proj_info.owner_full_name}::TagType::{item.name}:\n"
                f"        result.tag = {enum_item_abi_info.name};\n"
                f"        result.data.{item.name} = {result};\n"
                f"        break;\n"
            )
        enum_cpp_proj_target.write(
            f"    }}\n"
            f"    return result;\n"
            f"}}\n"
            f"template<>\n"
            f"inline {enum_cpp_proj_info.owner_full_name} from_abi({enum_abi_info.as_owner} val){{\n"
            f"    switch (val.tag) {{\n"
        )
        for item in enum.items:
            enum_item_abi_info = EnumItemDeclABIInfo.get(self.am, item)
            if item.ty_ref is None:
                enum_cpp_proj_target.write(
                    f"    case {enum_item_abi_info.name}:\n"
                    f"        return {enum_cpp_proj_info.owner_full_name}(::taihe::core::ConstexprTag<{enum_cpp_proj_info.owner_full_name}::TagType::{item.name}>);\n"
                )
                continue
            ty_cpp_proj_info = TypeCppProjInfo.get(self.am, item.ty_ref.resolved_ty)
            result = ty_cpp_proj_info.return_from_abi(f"val.data.{item.name}")
            enum_cpp_proj_target.write(
                f"    case {enum_item_abi_info.name}:\n"
                f"        return {enum_cpp_proj_info.owner_full_name}(::taihe::core::ConstexprTag<{enum_cpp_proj_info.owner_full_name}::TagType::{item.name}>, {result});\n"
            )
        enum_cpp_proj_target.write(
            f"    }}\n"
            f"}}\n"
            f"template<>\n"
            f"inline {enum_abi_info.as_param} into_abi({enum_cpp_proj_info.param_full_name} val){{\n"
            f"    return reinterpret_cast<{enum_abi_info.as_param}>(&val);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {enum_cpp_proj_info.param_full_name} from_abi({enum_abi_info.as_param} val){{\n"
            f"    return reinterpret_cast<{enum_cpp_proj_info.param_full_name}>(*val);\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_iface_files(
        self,
        iface: IfaceDecl,
        pkg_cpp_proj_target: COutputBuffer,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        iface_abi_info = IfaceDeclABIInfo.get(self.am, iface)
        iface_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, iface)
        self.gen_iface_decl_file(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            pkg_cpp_proj_info,
        )
        self.gen_iface_defn_file(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            pkg_cpp_proj_info,
        )
        self.gen_iface_impl_file(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            pkg_cpp_proj_info,
        )
        pkg_cpp_proj_target.include(iface_cpp_proj_info.header_impl)

    def gen_iface_decl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        iface_cpp_proj_decl_target = COutputBuffer.create(
            self.tm, f"include/{iface_cpp_proj_info.header_decl}", True
        )
        iface_cpp_proj_decl_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"struct {iface_cpp_proj_info.name};\n"
            f"}}\n"
            f"namespace {pkg_cpp_proj_info.param_namespace} {{\n"
            f"struct {iface_cpp_proj_info.name};\n"
            f"}}\n"
        )

    def gen_iface_defn_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        iface_cpp_proj_defn_target = COutputBuffer.create(
            self.tm, f"include/{iface_cpp_proj_info.header_defn}", True
        )
        iface_cpp_proj_defn_target.include("core/object.hpp")
        iface_cpp_proj_defn_target.include(iface_abi_info.header_0)
        iface_cpp_proj_defn_target.include(iface_cpp_proj_info.header_decl)
        self.gen_iface_defn_owner_decl(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            pkg_cpp_proj_info,
            iface_cpp_proj_defn_target,
        )
        self.gen_iface_defn_param_decl(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            pkg_cpp_proj_info,
            iface_cpp_proj_defn_target,
        )
        self.gen_iface_trans_funcs(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            iface_cpp_proj_defn_target,
        )

    def gen_iface_defn_owner_decl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
        iface_cpp_proj_defn_target: COutputBuffer,
    ):
        iface_cpp_proj_defn_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"struct {iface_cpp_proj_info.name} {{\n"
            f"    {iface_abi_info.as_owner} m_handle;\n"
            f"    explicit {iface_cpp_proj_info.name}({iface_abi_info.as_owner} other_handle);\n"
            f"    ~{iface_cpp_proj_info.name}();\n"
            f"    {iface_cpp_proj_info.name}({iface_cpp_proj_info.owner_full_name} const& other);\n"
            f"    {iface_cpp_proj_info.name}({iface_cpp_proj_info.owner_full_name} && other);\n"
            f"    {iface_cpp_proj_info.name}({iface_cpp_proj_info.param_full_name} const& other);\n"
            f"    operator ::taihe::core::DataOwner() const&;\n"
            f"    operator ::taihe::core::DataOwner() &&;\n"
            f"    operator ::taihe::core::DataRef() const&;\n"
            f"    explicit {iface_cpp_proj_info.name}(::taihe::core::DataOwner other);\n"
            f"    {iface_cpp_proj_info.name}& operator=({iface_cpp_proj_info.owner_full_name} other);\n"
            f"    operator bool();\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, ancestor)
            iface_cpp_proj_defn_target.include(ancestor_cpp_proj_info.header_decl)
            iface_cpp_proj_defn_target.write(
                f"    operator {ancestor_cpp_proj_info.owner_full_name}() const&;\n"
                f"    operator {ancestor_cpp_proj_info.owner_full_name}() &&;\n"
                f"    operator {ancestor_cpp_proj_info.param_full_name}() const&;\n"
            )
        for method in iface.methods:
            method_cpp_proj_info = BaseFuncDeclCppProjInfo.get(self.am, method)
            params = []
            for param in method.params:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                iface_cpp_proj_defn_target.include(type_cpp_proj_info.header_decl)
                params.append(f"{type_cpp_proj_info.as_param} {param.name}")
            params_str = ", ".join(params)
            iface_cpp_proj_defn_target.include(
                method_cpp_proj_info.return_ty_header_decl
            )
            iface_cpp_proj_defn_target.write(
                f"    {method_cpp_proj_info.return_ty_name} {method.name}({params_str});\n"
            )
        iface_cpp_proj_defn_target.write("};\n" "}\n")

    def gen_iface_defn_param_decl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
        iface_cpp_proj_defn_target: COutputBuffer,
    ):
        iface_cpp_proj_defn_target.write(
            f"namespace {pkg_cpp_proj_info.param_namespace} {{\n"
            f"struct {iface_cpp_proj_info.name} {{\n"
            f"    {iface_abi_info.as_param} m_handle;\n"
            f"    explicit {iface_cpp_proj_info.name}({iface_abi_info.as_param} other_handle);\n"
            f"    ~{iface_cpp_proj_info.name}();\n"
            f"    {iface_cpp_proj_info.name}({iface_cpp_proj_info.owner_full_name} const& other);\n"
            f"    {iface_cpp_proj_info.name}({iface_cpp_proj_info.param_full_name} const& other);\n"
            f"    operator ::taihe::core::DataOwner() const&;\n"
            f"    operator ::taihe::core::DataRef() const&;\n"
            f"    explicit {iface_cpp_proj_info.name}(::taihe::core::DataRef other);\n"
            f"    {iface_cpp_proj_info.name}& operator=({iface_cpp_proj_info.param_full_name} other);\n"
            f"    operator bool();\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, ancestor)
            iface_cpp_proj_defn_target.include(ancestor_cpp_proj_info.header_decl)
            iface_cpp_proj_defn_target.write(
                f"    operator {ancestor_cpp_proj_info.owner_full_name}() const&;\n"
                f"    operator {ancestor_cpp_proj_info.param_full_name}() const&;\n"
            )
        for method in iface.methods:
            method_cpp_proj_info = BaseFuncDeclCppProjInfo.get(self.am, method)
            params = []
            for param in method.params:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                iface_cpp_proj_defn_target.include(type_cpp_proj_info.header_decl)
                params.append(f"{type_cpp_proj_info.as_param} {param.name}")
            params_str = ", ".join(params)
            iface_cpp_proj_defn_target.include(
                method_cpp_proj_info.return_ty_header_decl
            )
            iface_cpp_proj_defn_target.write(
                f"    {method_cpp_proj_info.return_ty_name} {method.name}({params_str});\n"
            )
        iface_cpp_proj_defn_target.write("};\n" "}\n")

    def gen_iface_trans_funcs(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_impl_target: COutputBuffer,
    ):
        iface_cpp_proj_impl_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"inline {iface_abi_info.as_owner} into_abi({iface_cpp_proj_info.owner_full_name} other){{\n"
            f"    {iface_abi_info.as_owner} ret_handle = other.m_handle;\n"
            f"    other.m_handle.data_ptr = nullptr;\n"
            f"    return ret_handle;\n"
            f"}}\n"
            f"template<>\n"
            f"inline {iface_cpp_proj_info.owner_full_name} from_abi({iface_abi_info.as_owner} other_handle){{\n"
            f"    {iface_abi_info.as_owner} ret_handle = other_handle;\n"
            f"    return {iface_cpp_proj_info.owner_full_name}(ret_handle);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {iface_abi_info.as_param} into_abi({iface_cpp_proj_info.param_full_name} other){{\n"
            f"    {iface_abi_info.as_param} ret_handle = other.m_handle;\n"
            f"    return ret_handle;\n"
            f"}}\n"
            f"template<>\n"
            f"inline {iface_cpp_proj_info.param_full_name} from_abi({iface_abi_info.as_param} other_handle){{\n"
            f"    {iface_abi_info.as_owner} ret_handle = other_handle;\n"
            f"    return {iface_cpp_proj_info.param_full_name}(ret_handle);\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_iface_impl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        iface_cpp_proj_impl_target = COutputBuffer.create(
            self.tm, f"include/{iface_cpp_proj_info.header_impl}", True
        )
        iface_cpp_proj_impl_target.include(iface_abi_info.header_1)
        iface_cpp_proj_impl_target.include(iface_cpp_proj_info.header_defn)
        self.gen_iface_ftable(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            iface_cpp_proj_impl_target,
        )
        self.gen_iface_vtable(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            iface_cpp_proj_impl_target,
        )
        self.gen_iface_rtti(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            iface_cpp_proj_impl_target,
        )
        self.gen_iface_inspector(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            iface_cpp_proj_impl_target,
        )
        self.gen_iface_impl_owner_decl(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            iface_cpp_proj_impl_target,
            pkg_cpp_proj_info,
        )
        self.gen_iface_impl_param_decl(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            iface_cpp_proj_impl_target,
            pkg_cpp_proj_info,
        )

    def gen_iface_ftable(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_impl_target: COutputBuffer,
    ):
        iface_cpp_proj_impl_target.write(
            f"namespace taihe::core {{\n"
            f"template<typename Impl>\n"
            f"struct FTableImpl<{iface_abi_info.f_table}, Impl> {{\n"
            f"    struct Inner {{\n"
        )
        for method in iface.methods:
            method_abi_info = BaseFuncDeclABIInfo.get(self.am, method)
            method_cpp_proj_info = BaseFuncDeclCppProjInfo.get(self.am, method)
            params_abi = [f"{iface_abi_info.as_param} tobj"]
            args_from_abi = []
            for param in method.params:
                type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                params_abi.append(f"{type_abi_info.as_param} {param.name}")
                args_from_abi.append(type_cpp_proj_info.pass_from_abi(param.name))
            params_abi_str = ", ".join(params_abi)
            args_from_abi_str = ", ".join(args_from_abi)
            result = method_cpp_proj_info.return_into_abi(
                f"static_cast<Impl*>(static_cast<::taihe::core::WithDataBlockHead<Impl>*>(tobj.data_ptr))->{method_cpp_proj_info.name}({args_from_abi_str})"
            )
            iface_cpp_proj_impl_target.write(
                f"        static {method_abi_info.return_ty_name} {method.name}({params_abi_str}) {{\n"
                f"            return {result};\n"
                f"        }}\n"
            )
        iface_cpp_proj_impl_target.write(
            f"    }};\n" f"    static constexpr {iface_abi_info.f_table} ftbl = {{\n"
        )
        for method in iface.methods:
            method_cpp_proj_info = BaseFuncDeclCppProjInfo.get(self.am, method)
            iface_cpp_proj_impl_target.write(
                f"        .{method.name} = &Inner::{method_cpp_proj_info.name},\n"
            )
        iface_cpp_proj_impl_target.write("    };\n" "};\n" "}\n")

    def gen_iface_vtable(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_impl_target: COutputBuffer,
    ):
        iface_cpp_proj_impl_target.write(
            f"namespace taihe::core {{\n"
            f"template<typename Impl>\n"
            f"struct VTableImpl<{iface_abi_info.v_table}, Impl> {{\n"
            f"    static constexpr {iface_abi_info.v_table} vtbl = {{\n"
        )
        for ancestor_info in iface_abi_info.ancestor_list:
            ancestor_abi_info = IfaceDeclABIInfo.get(self.am, ancestor_info.iface)
            iface_cpp_proj_impl_target.write(
                f"        .{ancestor_info.ptbl_ptr} = &::taihe::core::FTableImpl<{ancestor_abi_info.f_table}, Impl>::ftbl,\n"
            )
        iface_cpp_proj_impl_target.write("    };\n" "};\n" "}\n")

    def gen_iface_rtti(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_impl_target: COutputBuffer,
    ):
        iface_cpp_proj_impl_target.write(
            f"namespace taihe::core {{\n"
            f"template<typename Impl>\n"
            f"struct RTTIImpl<{iface_abi_info.rtti}, Impl> {{\n"
            f"    static void free(DataBlockHead* data_ptr) {{\n"
            f"        delete static_cast<::taihe::core::WithDataBlockHead<Impl>*>(data_ptr);\n"
            f"    }}\n"
            f"    static constexpr {iface_abi_info.rtti} rtti = {{\n"
            f"        .version = 0,\n"
            f"        .free_ptr = &free,\n"
            f"        .len = {len(iface_abi_info.ancestor_dict)},\n"
            f"        .idmap = {{\n"
        )
        for iface in iface_abi_info.ancestor_dict:
            ancestor_abi_info = IfaceDeclABIInfo.get(self.am, iface)
            iface_cpp_proj_impl_target.include(ancestor_abi_info.header_1)
            iface_cpp_proj_impl_target.write(
                f"            {{&{ancestor_abi_info.iid}, &::taihe::core::VTableImpl<{ancestor_abi_info.v_table}, Impl>::vtbl}},\n"
            )
        iface_cpp_proj_impl_target.write("        },\n" "    };\n" "};\n" "}\n")

    def gen_iface_inspector(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_impl_target: COutputBuffer,
    ):
        iface_cpp_proj_impl_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"struct OwnerInspector<{iface_cpp_proj_info.owner_full_name}> {{\n"
            f"    using Type = void*;\n"
            f"    using RTTI = {iface_abi_info.rtti};\n"
            f"    using VTable = {iface_abi_info.v_table};\n"
            f"}};\n"
            f"}}\n"
        )

    def gen_iface_impl_owner_decl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_impl_target: COutputBuffer,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        iface_cpp_proj_impl_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_abi_info.as_owner} other_handle)\n"
            f"    : m_handle(other_handle) {{}}\n"
            f"inline {iface_cpp_proj_info.name}::~{iface_cpp_proj_info.name}() {{\n"
            f"    {iface_abi_info.drop_func}(this->m_handle);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_cpp_proj_info.owner_full_name} && other)\n"
            f"    : m_handle(other.m_handle) {{\n"
            f"    other.m_handle.data_ptr = nullptr;\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_cpp_proj_info.owner_full_name} const& other)\n"
            f"    : m_handle({iface_abi_info.copy_func}(other.m_handle)) {{}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_cpp_proj_info.param_full_name} const& other)\n"
            f"    : m_handle({iface_abi_info.copy_func}(other.m_handle)) {{}}\n"
            f"inline {iface_cpp_proj_info.name}::operator ::taihe::core::DataOwner() && {{\n"
            f"    {iface_abi_info.as_owner} ret_handle = this->m_handle;\n"
            f"    this->m_handle.data_ptr = nullptr;\n"
            f"    return ::taihe::core::DataOwner(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator ::taihe::core::DataOwner() const& {{\n"
            f"    {iface_abi_info.as_owner} ret_handle = {iface_abi_info.copy_func}(this->m_handle);\n"
            f"    return ::taihe::core::DataOwner(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator ::taihe::core::DataRef() const& {{\n"
            f"    {iface_abi_info.as_owner} ret_handle = this->m_handle;\n"
            f"    return ::taihe::core::DataRef(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}(::taihe::core::DataOwner other)\n"
            f"    : m_handle({iface_abi_info.dynamic_cast}(other.m_handle)) {{\n"
            f"    other.m_handle = nullptr;\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}& {iface_cpp_proj_info.name}::operator=({iface_cpp_proj_info.owner_full_name} other) {{\n"
            f"    std::swap(this->m_handle, other.m_handle);\n"
            f"    return *this;\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator bool() {{\n"
            f"    return this->m_handle.vtbl_ptr;\n"
            f"}}\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, ancestor)
            iface_cpp_proj_impl_target.include(ancestor_cpp_proj_info.header_defn)
            iface_cpp_proj_impl_target.write(
                f"inline {iface_cpp_proj_info.name}::operator {ancestor_cpp_proj_info.owner_full_name}() && {{\n"
                f"    {iface_abi_info.as_owner} ret_handle = this->m_handle;\n"
                f"    this->m_handle.data_ptr = nullptr;\n"
                f"    return {ancestor_cpp_proj_info.owner_full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
                f"inline {iface_cpp_proj_info.name}::operator {ancestor_cpp_proj_info.owner_full_name}() const& {{\n"
                f"    {iface_abi_info.as_owner} ret_handle = {iface_abi_info.copy_func}(this->m_handle);\n"
                f"    return {ancestor_cpp_proj_info.owner_full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
                f"inline {iface_cpp_proj_info.name}::operator {ancestor_cpp_proj_info.param_full_name}() const& {{\n"
                f"    {iface_abi_info.as_owner} ret_handle = this->m_handle;\n"
                f"    return {ancestor_cpp_proj_info.param_full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
            )
        for method in iface.methods:
            method_abi_info = BaseFuncDeclABIInfo.get(self.am, method)
            method_cpp_proj_info = BaseFuncDeclCppProjInfo.get(self.am, method)
            params = []
            args_into_abi = ["this->m_handle"]
            for param in method.params:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                iface_cpp_proj_impl_target.include(type_cpp_proj_info.header_defn)
                params.append(f"{type_cpp_proj_info.as_param} {param.name}")
                args_into_abi.append(type_cpp_proj_info.pass_into_abi(param.name))
            params_str = ", ".join(params)
            args_into_abi_str = ",".join(args_into_abi)
            iface_cpp_proj_impl_target.include(
                method_cpp_proj_info.return_ty_header_defn
            )
            result = method_cpp_proj_info.return_from_abi(
                f"{method_abi_info.name}({args_into_abi_str})"
            )
            iface_cpp_proj_impl_target.write(
                f"inline {method_cpp_proj_info.return_ty_name} {iface_cpp_proj_info.name}::{method.name}({params_str}) {{\n"
                f"    return {result};\n"
                f"}}\n"
            )
        iface_cpp_proj_impl_target.write("}\n")

    def gen_iface_impl_param_decl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_impl_target: COutputBuffer,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        iface_cpp_proj_impl_target.write(
            f"namespace {pkg_cpp_proj_info.param_namespace} {{\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_abi_info.as_param} other_handle)\n"
            f"    : m_handle(other_handle) {{}}\n"
            f"inline {iface_cpp_proj_info.name}::~{iface_cpp_proj_info.name}() {{}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_cpp_proj_info.owner_full_name} const& other)\n"
            f"    : m_handle(other.m_handle) {{}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_cpp_proj_info.param_full_name} const& other)\n"
            f"    : m_handle(other.m_handle) {{}}\n"
            f"inline {iface_cpp_proj_info.name}::operator ::taihe::core::DataOwner() const& {{\n"
            f"    {iface_abi_info.as_owner} ret_handle = {iface_abi_info.copy_func}(this->m_handle);\n"
            f"    return ::taihe::core::DataOwner(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator ::taihe::core::DataRef() const& {{\n"
            f"    {iface_abi_info.as_owner} ret_handle = this->m_handle;\n"
            f"    return ::taihe::core::DataRef(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}(::taihe::core::DataRef other)\n"
            f"    : m_handle({iface_abi_info.dynamic_cast}(other.m_handle)) {{\n"
            f"    other.m_handle = nullptr;\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}& {iface_cpp_proj_info.name}::operator=({iface_cpp_proj_info.param_full_name} other) {{\n"
            f"    std::swap(this->m_handle, other.m_handle);\n"
            f"    return *this;\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator bool() {{\n"
            f"    return this->m_handle.vtbl_ptr;\n"
            f"}}\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, ancestor)
            iface_cpp_proj_impl_target.include(ancestor_cpp_proj_info.header_defn)
            iface_cpp_proj_impl_target.write(
                f"inline {iface_cpp_proj_info.name}::operator {ancestor_cpp_proj_info.owner_full_name}() const& {{\n"
                f"    {iface_abi_info.as_owner} ret_handle = {iface_abi_info.copy_func}(this->m_handle);\n"
                f"    return {ancestor_cpp_proj_info.owner_full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
                f"inline {iface_cpp_proj_info.name}::operator {ancestor_cpp_proj_info.param_full_name}() const& {{\n"
                f"    {iface_abi_info.as_owner} ret_handle = this->m_handle;\n"
                f"    return {ancestor_cpp_proj_info.param_full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
            )
        for method in iface.methods:
            method_abi_info = BaseFuncDeclABIInfo.get(self.am, method)
            method_cpp_proj_info = BaseFuncDeclCppProjInfo.get(self.am, method)
            params = []
            args_into_abi = ["this->m_handle"]
            for param in method.params:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                iface_cpp_proj_impl_target.include(type_cpp_proj_info.header_defn)
                params.append(f"{type_cpp_proj_info.as_param} {param.name}")
                args_into_abi.append(type_cpp_proj_info.pass_into_abi(param.name))
            params_str = ", ".join(params)
            args_into_abi_str = ",".join(args_into_abi)
            iface_cpp_proj_impl_target.include(
                method_cpp_proj_info.return_ty_header_defn
            )
            result = method_cpp_proj_info.return_from_abi(
                f"{method_abi_info.name}({args_into_abi_str})"
            )
            iface_cpp_proj_impl_target.write(
                f"inline {method_cpp_proj_info.return_ty_name} {iface_cpp_proj_info.name}::{method.name}({params_str}) {{\n"
                f"    return {result};\n"
                f"}}\n"
            )
        iface_cpp_proj_impl_target.write("}\n")
