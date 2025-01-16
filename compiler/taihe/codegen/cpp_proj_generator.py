from typing import Any, Optional

from typing_extensions import override

from taihe.codegen.abi_generator import (
    COutputBuffer,
    EnumDeclABIInfo,
    EnumItemDeclABIInfo,
    GlobFuncDeclABIInfo,
    IfaceDeclABIInfo,
    IfaceMethodDeclABIInfo,
    PackageABIInfo,
    StructDeclABIInfo,
    TypeABIInfo,
)
from taihe.semantics.declarations import (
    EnumDecl,
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
    I8,
    I16,
    I32,
    I64,
    STRING,
    U8,
    U16,
    U32,
    U64,
    EnumType,
    IfaceType,
    ScalarType,
    SpecialType,
    StructType,
    Type,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager


class PackageCppProjInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.proj.hpp"
        self.namespace = "::".join(p.segments)
        self.weakspace = "::".join(p.segments) + "::weak"


class GlobFuncDeclCppProjInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        self.name = f.name


class IfaceMethodDeclCppProjInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, f: IfaceMethodDecl) -> None:
        # TODO: Supports projection to any C++ function name based on attributes
        self.name = "operator()" if f.attrs.get("functor") else f.name


class StructDeclCppProjInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        abi_info = StructDeclABIInfo.get(am, d)
        p = d.node_parent
        assert p
        self.decl_header = f"{p.name}.{d.name}.proj.0.hpp"
        self.defn_header = f"{p.name}.{d.name}.proj.1.hpp"
        self.name = d.name
        self.full_name = "::" + "::".join(p.segments) + "::" + self.name
        self.as_owner = self.full_name
        self.as_param = self.full_name + " const&"
        self.pass_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.as_param}, {abi_info.as_param}>({val})"
        )
        self.pass_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.as_param}, {abi_info.as_param}>({val})"
        )
        self.return_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.as_owner}, {abi_info.as_field}>({val})"
        )
        self.return_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.as_owner}, {abi_info.as_field}>({val})"
        )


class EnumDeclCppProjInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        abi_info = EnumDeclABIInfo.get(am, d)
        p = d.node_parent
        assert p
        self.decl_header = f"{p.name}.{d.name}.proj.0.hpp"
        self.defn_header = f"{p.name}.{d.name}.proj.1.hpp"
        self.name = d.name
        self.full_name = "::" + "::".join(p.segments) + "::" + self.name
        self.as_owner = self.full_name
        self.as_param = self.full_name + " const&"
        self.pass_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.as_param}, {abi_info.as_param}>({val})"
        )
        self.pass_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.as_param}, {abi_info.as_param}>({val})"
        )
        self.return_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.as_owner}, {abi_info.as_field}>({val})"
        )
        self.return_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.as_owner}, {abi_info.as_field}>({val})"
        )


class IfaceDeclCppProjInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        abi_info = IfaceDeclABIInfo.get(am, d)
        p = d.node_parent
        assert p
        self.decl_header = f"{p.name}.{d.name}.proj.0.hpp"
        self.defn_header = f"{p.name}.{d.name}.proj.1.hpp"
        self.impl_header = f"{p.name}.{d.name}.proj.2.hpp"
        self.name = d.name
        self.full_name = "::" + "::".join(p.segments) + "::" + self.name
        self.weak_name = "::" + "::".join(p.segments) + "::weak::" + self.name
        self.as_owner = self.full_name
        self.as_param = self.weak_name
        self.pass_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.as_param}, {abi_info.as_param}>({val})"
        )
        self.pass_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.as_param}, {abi_info.as_param}>({val})"
        )
        self.return_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.as_owner}, {abi_info.as_field}>({val})"
        )
        self.return_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.as_owner}, {abi_info.as_field}>({val})"
        )


class TypeCppProjInfo(AbstractAnalysis[Optional[Type]], TypeVisitor):
    def __init__(self, am: AnalysisManager, t: Optional[Type]) -> None:
        self.am = am
        self.decl_headers: list[str] = []
        self.defn_headers: list[str] = []
        # type as holder struct field / holder union field / return value
        self.as_owner = None
        # type as parameter
        self.as_param = None
        self.pass_from_abi = lambda val: val
        self.pass_into_abi = lambda val: val
        self.return_from_abi = lambda val: val
        self.return_into_abi = lambda val: val
        self.handle_type(t)

    @override
    def visit_enum_type(self, t: EnumType) -> Any:
        enum_cpp_proj_info = EnumDeclCppProjInfo.get(self.am, t.ty_decl)
        self.decl_headers = [enum_cpp_proj_info.decl_header]
        self.defn_headers = [enum_cpp_proj_info.defn_header]
        self.as_owner = enum_cpp_proj_info.as_owner
        self.as_param = enum_cpp_proj_info.as_param
        self.pass_from_abi = enum_cpp_proj_info.pass_from_abi
        self.pass_into_abi = enum_cpp_proj_info.pass_into_abi
        self.return_from_abi = enum_cpp_proj_info.return_from_abi
        self.return_into_abi = enum_cpp_proj_info.return_into_abi

    @override
    def visit_struct_type(self, t: StructType) -> Any:
        struct_cpp_proj_info = StructDeclCppProjInfo.get(self.am, t.ty_decl)
        self.decl_headers = [struct_cpp_proj_info.decl_header]
        self.defn_headers = [struct_cpp_proj_info.defn_header]
        self.as_owner = struct_cpp_proj_info.as_owner
        self.as_param = struct_cpp_proj_info.as_param
        self.pass_from_abi = struct_cpp_proj_info.pass_from_abi
        self.pass_into_abi = struct_cpp_proj_info.pass_into_abi
        self.return_from_abi = struct_cpp_proj_info.return_from_abi
        self.return_into_abi = struct_cpp_proj_info.return_into_abi

    @override
    def visit_iface_type(self, t: IfaceType) -> Any:
        iface_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, t.ty_decl)
        self.decl_headers = [iface_cpp_proj_info.decl_header]
        self.defn_headers = [iface_cpp_proj_info.defn_header]
        self.as_owner = iface_cpp_proj_info.as_owner
        self.as_param = iface_cpp_proj_info.as_param
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
            self.decl_headers = ["core/string.hpp"]
            self.defn_headers = ["core/string.hpp"]
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
            self.gen_struct_files(struct, pkg_cpp_proj_target, pkg_cpp_proj_info)
        for enum in pkg.enums:
            self.gen_enum_files(enum, pkg_cpp_proj_target, pkg_cpp_proj_info)
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
        func_cpp_proj_info = GlobFuncDeclCppProjInfo.get(self.am, func)
        func_abi_info = GlobFuncDeclABIInfo.get(self.am, func)
        params_cpp = []
        args_into_abi = []
        for param in func.params:
            type_cpp_proj_info = TypeCppProjInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_cpp_proj_target.include(*type_cpp_proj_info.defn_headers)
            params_cpp.append(f"{type_cpp_proj_info.as_param} {param.name}")
            args_into_abi.append(type_cpp_proj_info.pass_into_abi(param.name))
        params_cpp_str = ", ".join(params_cpp)
        args_into_abi_str = ", ".join(args_into_abi)
        abi_result = f"{func_abi_info.mangled_name}({args_into_abi_str})"
        if return_ty_ref := func.return_ty_ref:
            type_cpp_proj_info = TypeCppProjInfo.get(self.am, return_ty_ref.resolved_ty)
            pkg_cpp_proj_target.include(*type_cpp_proj_info.defn_headers)
            cpp_return_ty_name = type_cpp_proj_info.as_owner
            cpp_result = type_cpp_proj_info.return_from_abi(abi_result)
        else:
            cpp_return_ty_name = "void"
            cpp_result = abi_result
        pkg_cpp_proj_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"inline {cpp_return_ty_name} {func_cpp_proj_info.name}({params_cpp_str}) {{\n"
            f"    return {cpp_result};\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_struct_files(
        self,
        struct: StructDecl,
        pkg_cpp_proj_target: COutputBuffer,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        struct_abi_info = StructDeclABIInfo.get(self.am, struct)
        struct_cpp_proj_info = StructDeclCppProjInfo.get(self.am, struct)
        self.gen_struct_decl_file(
            struct,
            struct_abi_info,
            struct_cpp_proj_info,
            pkg_cpp_proj_info,
        )
        self.gen_struct_defn_file(
            struct,
            struct_abi_info,
            struct_cpp_proj_info,
            pkg_cpp_proj_info,
        )
        pkg_cpp_proj_target.include(struct_cpp_proj_info.defn_header)

    def gen_struct_decl_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructDeclABIInfo,
        struct_cpp_proj_info: StructDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        struct_cpp_proj_decl_target = COutputBuffer.create(
            self.tm, f"include/{struct_cpp_proj_info.decl_header}", True
        )
        struct_cpp_proj_decl_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"struct {struct_cpp_proj_info.name};\n"
            f"}}\n"
        )

    def gen_struct_defn_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructDeclABIInfo,
        struct_cpp_proj_info: StructDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        struct_cpp_proj_defn_target = COutputBuffer.create(
            self.tm, f"include/{struct_cpp_proj_info.defn_header}", True
        )
        struct_cpp_proj_defn_target.include("taihe/common.hpp")
        struct_cpp_proj_defn_target.include(struct_cpp_proj_info.decl_header)
        struct_cpp_proj_defn_target.include(struct_abi_info.defn_header)
        self.gen_struct_defn(
            struct,
            struct_cpp_proj_defn_target,
            struct_cpp_proj_info,
            pkg_cpp_proj_info,
        )
        self.gen_struct_trans_func(
            struct,
            struct_cpp_proj_defn_target,
            struct_cpp_proj_info,
            struct_abi_info,
        )

    def gen_struct_defn(
        self,
        struct: StructDecl,
        struct_cpp_proj_defn_target: COutputBuffer,
        struct_cpp_proj_info: StructDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        struct_cpp_proj_defn_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"struct {struct_cpp_proj_info.name} {{\n"
        )
        for field in struct.fields:
            ty_info = TypeCppProjInfo.get(self.am, field.ty_ref.resolved_ty)
            struct_cpp_proj_defn_target.include(*ty_info.defn_headers)
            struct_cpp_proj_defn_target.write(f"    {ty_info.as_owner} {field.name};\n")
        struct_cpp_proj_defn_target.write("};\n" "}\n")

    def gen_struct_trans_func(
        self,
        struct: StructDecl,
        struct_cpp_proj_defn_target: COutputBuffer,
        struct_cpp_proj_info: StructDeclCppProjInfo,
        struct_abi_info: StructDeclABIInfo,
    ):
        struct_cpp_proj_defn_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"inline {struct_abi_info.as_field} into_abi({struct_cpp_proj_info.as_owner} val){{\n"
            f"    return {{\n"
        )
        for field in struct.fields:
            ty_cpp_proj_info = TypeCppProjInfo.get(self.am, field.ty_ref.resolved_ty)
            result = ty_cpp_proj_info.return_into_abi(f"::std::move(val.{field.name})")
            struct_cpp_proj_defn_target.write(f"        {result},\n")
        struct_cpp_proj_defn_target.write(
            f"    }};\n"
            f"}}\n"
            f"template<>\n"
            f"inline {struct_cpp_proj_info.as_owner} from_abi({struct_abi_info.as_field} val){{\n"
            f"    return {{\n"
        )
        for field in struct.fields:
            ty_cpp_proj_info = TypeCppProjInfo.get(self.am, field.ty_ref.resolved_ty)
            result = ty_cpp_proj_info.return_from_abi(f"val.{field.name}")
            struct_cpp_proj_defn_target.write(f"        {result},\n")
        struct_cpp_proj_defn_target.write(
            f"    }};\n"
            f"}}\n"
            f"template<>\n"
            f"inline {struct_abi_info.as_param} into_abi({struct_cpp_proj_info.as_param} val){{\n"
            f"    return reinterpret_cast<{struct_abi_info.as_param}>(&val);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {struct_cpp_proj_info.as_param} from_abi({struct_abi_info.as_param} val){{\n"
            f"    return reinterpret_cast<{struct_cpp_proj_info.as_param}>(*val);\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_enum_files(
        self,
        enum: EnumDecl,
        pkg_cpp_proj_target: COutputBuffer,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        enum_cpp_proj_info = EnumDeclCppProjInfo.get(self.am, enum)
        enum_abi_info = EnumDeclABIInfo.get(self.am, enum)
        self.gen_enum_decl_file(
            enum,
            enum_abi_info,
            enum_cpp_proj_info,
            pkg_cpp_proj_info,
        )
        self.gen_enum_defn_file(
            enum,
            enum_abi_info,
            enum_cpp_proj_info,
            pkg_cpp_proj_info,
        )
        pkg_cpp_proj_target.include(enum_cpp_proj_info.defn_header)

    def gen_enum_decl_file(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumDeclABIInfo,
        enum_cpp_proj_info: EnumDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        enum_cpp_proj_decl_target = COutputBuffer.create(
            self.tm, f"include/{enum_cpp_proj_info.decl_header}", True
        )
        enum_cpp_proj_decl_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"struct {enum_cpp_proj_info.name};\n"
            f"}}\n"
        )

    def gen_enum_defn_file(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumDeclABIInfo,
        enum_cpp_proj_info: EnumDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        enum_cpp_proj_defn_target = COutputBuffer.create(
            self.tm, f"include/{enum_cpp_proj_info.defn_header}", True
        )
        enum_cpp_proj_defn_target.include("taihe/common.hpp")
        enum_cpp_proj_defn_target.include(enum_cpp_proj_info.decl_header)
        enum_cpp_proj_defn_target.include(enum_abi_info.defn_header)
        self.gen_enum_defn(
            enum,
            enum_cpp_proj_defn_target,
            enum_cpp_proj_info,
            enum_abi_info,
            pkg_cpp_proj_info,
        )
        self.gen_enum_trans_func(
            enum,
            enum_cpp_proj_defn_target,
            enum_cpp_proj_info,
            enum_abi_info,
        )

    def gen_enum_defn(
        self,
        enum: EnumDecl,
        enum_cpp_proj_defn_target: COutputBuffer,
        enum_cpp_proj_info: EnumDeclCppProjInfo,
        enum_abi_info: EnumDeclABIInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        enum_cpp_proj_defn_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"struct {enum_cpp_proj_info.name} {{\n"
        )
        # tag type
        enum_cpp_proj_defn_target.write("    enum class tag_t {\n")
        for item in enum.items:
            enum_cpp_proj_defn_target.write(f"        {item.name} = {item.value},\n")
        enum_cpp_proj_defn_target.write("    };\n")
        # storage type
        enum_cpp_proj_defn_target.write(
            "    union storage_t {\n"
            "        storage_t() {}\n"
            "        ~storage_t() {}\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            ty_info = TypeCppProjInfo.get(self.am, item.ty_ref.resolved_ty)
            enum_cpp_proj_defn_target.include(*ty_info.defn_headers)
            enum_cpp_proj_defn_target.write(
                f"        {ty_info.as_owner} {item.name};\n"
            )
        enum_cpp_proj_defn_target.write("    };\n")
        # destructor
        enum_cpp_proj_defn_target.write(
            f"    ~{enum_cpp_proj_info.name}() {{\n" f"        switch (this->tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            enum_cpp_proj_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            ::std::destroy_at(&this->data.{item.name});\n"
                f"            break;\n"
            )
        enum_cpp_proj_defn_target.write(
            "        default:\n" "            break;\n" "        }\n" "    }\n"
        )
        # copy constructor
        enum_cpp_proj_defn_target.write(
            f"    {enum_cpp_proj_info.name}({enum_cpp_proj_info.name} const& other) : tag(other.tag) {{\n"
            f"        switch (this->tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            enum_cpp_proj_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            new (&this->data.{item.name}) decltype(this->data.{item.name})(other.data.{item.name});\n"
                f"            break;\n"
            )
        enum_cpp_proj_defn_target.write(
            "        default:\n" "            break;\n" "        }\n" "    }\n"
        )
        # move constructor
        enum_cpp_proj_defn_target.write(
            f"    {enum_cpp_proj_info.name}({enum_cpp_proj_info.name}&& other) : tag(other.tag) {{\n"
            f"        switch (this->tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            enum_cpp_proj_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            new (&this->data.{item.name}) decltype(this->data.{item.name})(::std::move(other.data.{item.name}));\n"
                f"            break;\n"
            )
        enum_cpp_proj_defn_target.write(
            "        default:\n" "            break;\n" "        }\n" "    }\n"
        )
        # copy assignment
        enum_cpp_proj_defn_target.write(
            f"    {enum_cpp_proj_info.name} const& operator=({enum_cpp_proj_info.name} const& other) {{\n"
            f"        if (this != &other) {{\n"
            f"            ::std::destroy_at(this);\n"
            f"            new (this) {enum_cpp_proj_info.name}(other);\n"
            f"        }}\n"
            f"        return *this;\n"
            f"    }}\n"
        )
        # move assignment
        enum_cpp_proj_defn_target.write(
            f"    {enum_cpp_proj_info.name} const& operator=({enum_cpp_proj_info.name}&& other) {{\n"
            f"        if (this != &other) {{\n"
            f"            ::std::destroy_at(this);\n"
            f"            new (this) {enum_cpp_proj_info.name}(::std::move(other));\n"
            f"        }}\n"
            f"        return *this;\n"
            f"    }}\n"
        )
        # in place constructor
        for item in enum.items:
            if item.ty_ref is None:
                enum_cpp_proj_defn_target.write(
                    f"    {enum_cpp_proj_info.name}(::taihe::core::static_tag_t<tag_t::{item.name}>) : tag(tag_t::{item.name}) {{}}\n"
                )
            else:
                enum_cpp_proj_defn_target.write(
                    f"    template<typename... Args>\n"
                    f"    {enum_cpp_proj_info.name}(::taihe::core::static_tag_t<tag_t::{item.name}>, Args&&... args) : tag(tag_t::{item.name}) {{\n"
                    f"        new (&this->data.{item.name}) decltype(this->data.{item.name})(::std::forward<Args>(args)...);\n"
                    f"    }}\n"
                )
        # creator
        enum_cpp_proj_defn_target.write(
            f"    template<tag_t tag, typename... Args>\n"
            f"    static {enum_cpp_proj_info.name} make(Args&&... args) {{\n"
            f"        return {enum_cpp_proj_info.name}(::taihe::core::static_tag<tag>, ::std::forward<Args>(args)...);\n"
            f"    }}\n"
        )
        # emplacement
        enum_cpp_proj_defn_target.write(
            f"    template<tag_t tag, typename... Args>\n"
            f"    {enum_cpp_proj_info.name} const& emplace(Args&&... args) {{\n"
            f"        ::std::destroy_at(this);\n"
            f"        this->tag = tag;\n"
            f"        new (this) {enum_cpp_proj_info.name}(::taihe::core::static_tag<tag>, ::std::forward<Args>(args)...);\n"
            f"        return *this;\n"
            f"    }}\n"
        )
        # non-const getter
        enum_cpp_proj_defn_target.write(
            "    template<tag_t tag>\n" "    auto* unsafe_get_ptr() {\n"
        )
        for item in enum.items:
            result = (
                "(void*)&this->data"
                if item.ty_ref is None
                else f"&this->data.{item.name}"
            )
            enum_cpp_proj_defn_target.write(
                f"        if constexpr (tag == tag_t::{item.name}) {{\n"
                f"            return {result};\n"
                f"        }}\n"
            )
        enum_cpp_proj_defn_target.write("    }\n")
        enum_cpp_proj_defn_target.write(
            "    template<tag_t tag>\n"
            "    auto* get_ptr() {\n"
            "        return this->tag == tag ? unsafe_get_ptr<tag>() : nullptr;\n"
            "    }\n"
        )
        # const getter
        enum_cpp_proj_defn_target.write(
            "    template<tag_t tag>\n" "    auto const* unsafe_get_ptr() const {\n"
        )
        for item in enum.items:
            result = (
                "(void const*)&this->data"
                if item.ty_ref is None
                else f"&this->data.{item.name}"
            )
            enum_cpp_proj_defn_target.write(
                f"        if constexpr (tag == tag_t::{item.name}) {{\n"
                f"            return {result};\n"
                f"        }}\n"
            )
        enum_cpp_proj_defn_target.write("    }\n")
        enum_cpp_proj_defn_target.write(
            "    template<tag_t tag>\n"
            "    auto const* get_ptr() const {\n"
            "        return this->tag == tag ? unsafe_get_ptr<tag>() : nullptr;\n"
            "    }\n"
        )
        # checker
        enum_cpp_proj_defn_target.write(
            "    template<tag_t tag>\n"
            "    bool holds() const {\n"
            "        return this->tag == tag;\n"
            "    }\n"
            "    tag_t get_tag() const {\n"
            "        return this->tag;\n"
            "    }\n"
        )
        # named
        for item in enum.items:
            enum_cpp_proj_defn_target.write(
                f"    template<typename... Args>\n"
                f"    static {enum_cpp_proj_info.name} make_{item.name}(Args&&... args) {{\n"
                f"        return make<tag_t::{item.name}>(std::forward<Args>(args)...);\n"
                f"    }}\n"
                f"    template<typename... Args>\n"
                f"    {enum_cpp_proj_info.name} const& emplace_{item.name}(Args&&... args) {{\n"
                f"        return this->emplace<tag_t::{item.name}>(std::forward<Args>(args)...);\n"
                f"    }}\n"
                f"    auto* get_{item.name}_ptr() {{\n"
                f"        return this->get_ptr<tag_t::{item.name}>();\n"
                f"    }}\n"
                f"    auto const* get_{item.name}_ptr() const {{\n"
                f"        return this->get_ptr<tag_t::{item.name}>();\n"
                f"    }}\n"
                f"    auto* unsafe_get_{item.name}_ptr() {{\n"
                f"        return this->unsafe_get_ptr<tag_t::{item.name}>();\n"
                f"    }}\n"
                f"    auto const* unsafe_get_{item.name}_ptr() const {{\n"
                f"        return this->unsafe_get_ptr<tag_t::{item.name}>();\n"
                f"    }}\n"
                f"    bool holds_{item.name}() const {{\n"
                f"        return this->holds<tag_t::{item.name}>();\n"
                f"    }}\n"
            )
        # non_const visitor
        enum_cpp_proj_defn_target.write(
            "    template<typename Visitor>\n"
            "    auto accept_template(Visitor&& visitor) {\n"
            "        switch (this->tag) {\n"
        )
        for item in enum.items:
            result = f"::taihe::core::static_tag<tag_t::{item.name}>"
            if item.ty_ref:
                result += f", this->data.{item.name}"
            enum_cpp_proj_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            return visitor({result});\n"
            )
        enum_cpp_proj_defn_target.write("        }\n" "    }\n")
        enum_cpp_proj_defn_target.write(
            "    template<typename Visitor>\n"
            "    auto accept(Visitor&& visitor) {\n"
            "        switch (this->tag) {\n"
        )
        for item in enum.items:
            result = "" if item.ty_ref is None else f"this->data.{item.name}"
            enum_cpp_proj_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            return visitor.{item.name}({result});\n"
            )
        enum_cpp_proj_defn_target.write("        }\n" "    }\n")
        # const visitor
        enum_cpp_proj_defn_target.write(
            "    template<typename Visitor>\n"
            "    auto accept_template(Visitor&& visitor) const {\n"
            "        switch (this->tag) {\n"
        )
        for item in enum.items:
            result = f"::taihe::core::static_tag<tag_t::{item.name}>"
            if item.ty_ref:
                result += f", this->data.{item.name}"
            enum_cpp_proj_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            return visitor({result});\n"
            )
        enum_cpp_proj_defn_target.write("        }\n" "    }\n")
        enum_cpp_proj_defn_target.write(
            "    template<typename Visitor>\n"
            "    auto accept(Visitor&& visitor) const {\n"
            "        switch (this->tag) {\n"
        )
        for item in enum.items:
            result = "" if item.ty_ref is None else f"this->data.{item.name}"
            enum_cpp_proj_defn_target.write(
                f"        case tag_t::{item.name}:\n"
                f"            return visitor.{item.name}({result});\n"
            )
        enum_cpp_proj_defn_target.write("        }\n" "    }\n")
        enum_cpp_proj_defn_target.write(
            "private:\n"
            "    tag_t tag;\n"
            "    storage_t data;\n"
            "    template<typename cpp_t, typename abi_t>\n"
            "    friend abi_t taihe::core::into_abi(cpp_t val);\n"
            "    template<typename cpp_t, typename abi_t>\n"
            "    friend cpp_t taihe::core::from_abi(abi_t val);\n"
            "};\n"
            "}\n"
        )

    def gen_enum_trans_func(
        self,
        enum: EnumDecl,
        enum_cpp_proj_defn_target: COutputBuffer,
        enum_cpp_proj_info: EnumDeclCppProjInfo,
        enum_abi_info: EnumDeclABIInfo,
    ):
        enum_cpp_proj_defn_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"inline {enum_abi_info.as_field} into_abi({enum_cpp_proj_info.as_owner} val){{\n"
            f"    {enum_abi_info.as_field} result;\n"
            f"    switch (val.tag) {{\n"
        )
        for item in enum.items:
            enum_item_abi_info = EnumItemDeclABIInfo.get(self.am, item)
            if item.ty_ref is None:
                enum_cpp_proj_defn_target.write(
                    f"    case {enum_cpp_proj_info.full_name}::tag_t::{item.name}:\n"
                    f"        result.tag = {enum_item_abi_info.mangled_name};\n"
                    f"        break;\n"
                )
                continue
            ty_cpp_proj_info = TypeCppProjInfo.get(self.am, item.ty_ref.resolved_ty)
            result = ty_cpp_proj_info.return_into_abi(
                f"::std::move(val.data.{item.name})"
            )
            enum_cpp_proj_defn_target.write(
                f"    case {enum_cpp_proj_info.full_name}::tag_t::{item.name}:\n"
                f"        result.tag = {enum_item_abi_info.mangled_name};\n"
                f"        result.data.{item.name} = {result};\n"
                f"        break;\n"
            )
        enum_cpp_proj_defn_target.write(
            f"    }}\n"
            f"    return result;\n"
            f"}}\n"
            f"template<>\n"
            f"inline {enum_cpp_proj_info.as_owner} from_abi({enum_abi_info.as_field} val){{\n"
            f"    switch (val.tag) {{\n"
        )
        for item in enum.items:
            enum_item_abi_info = EnumItemDeclABIInfo.get(self.am, item)
            if item.ty_ref is None:
                enum_cpp_proj_defn_target.write(
                    f"    case {enum_item_abi_info.mangled_name}:\n"
                    f"        return {enum_cpp_proj_info.as_owner}(::taihe::core::static_tag<{enum_cpp_proj_info.full_name}::tag_t::{item.name}>);\n"
                )
                continue
            ty_cpp_proj_info = TypeCppProjInfo.get(self.am, item.ty_ref.resolved_ty)
            result = ty_cpp_proj_info.return_from_abi(f"val.data.{item.name}")
            enum_cpp_proj_defn_target.write(
                f"    case {enum_item_abi_info.mangled_name}:\n"
                f"        return {enum_cpp_proj_info.as_owner}(::taihe::core::static_tag<{enum_cpp_proj_info.full_name}::tag_t::{item.name}>, {result});\n"
            )
        enum_cpp_proj_defn_target.write(
            f"    }}\n"
            f"}}\n"
            f"template<>\n"
            f"inline {enum_abi_info.as_param} into_abi({enum_cpp_proj_info.as_param} val){{\n"
            f"    return reinterpret_cast<{enum_abi_info.as_param}>(&val);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {enum_cpp_proj_info.as_param} from_abi({enum_abi_info.as_param} val){{\n"
            f"    return reinterpret_cast<{enum_cpp_proj_info.as_param}>(*val);\n"
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
        pkg_cpp_proj_target.include(iface_cpp_proj_info.impl_header)

    def gen_iface_decl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        iface_cpp_proj_decl_target = COutputBuffer.create(
            self.tm, f"include/{iface_cpp_proj_info.decl_header}", True
        )
        iface_cpp_proj_decl_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"struct {iface_cpp_proj_info.name};\n"
            f"}}\n"
            f"namespace {pkg_cpp_proj_info.weakspace} {{\n"
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
            self.tm, f"include/{iface_cpp_proj_info.defn_header}", True
        )
        iface_cpp_proj_defn_target.include("core/object.hpp")
        iface_cpp_proj_defn_target.include(iface_cpp_proj_info.decl_header)
        iface_cpp_proj_defn_target.include(iface_abi_info.defn_header)
        self.gen_iface_owner_defn(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            pkg_cpp_proj_info,
            iface_cpp_proj_defn_target,
        )
        self.gen_iface_param_defn(
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

    def gen_iface_owner_defn(
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
            f"    {iface_abi_info.as_field} m_handle;\n"
            f"    explicit {iface_cpp_proj_info.name}({iface_abi_info.as_field} other_handle);\n"
            f"    ~{iface_cpp_proj_info.name}();\n"
            f"    {iface_cpp_proj_info.name}({iface_cpp_proj_info.full_name} const& other);\n"
            f"    {iface_cpp_proj_info.name}({iface_cpp_proj_info.full_name} && other);\n"
            f"    operator {iface_cpp_proj_info.weak_name} () const&;\n"
            f"    operator ::taihe::core::data_holder() const&;\n"
            f"    operator ::taihe::core::data_holder() &&;\n"
            f"    operator ::taihe::core::data_view() const&;\n"
            f"    explicit {iface_cpp_proj_info.name}(::taihe::core::data_holder other);\n"
            f"    {iface_cpp_proj_info.name}& operator=({iface_cpp_proj_info.full_name} other);\n"
            f"    operator bool() const&;\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, ancestor)
            iface_cpp_proj_defn_target.include(ancestor_cpp_proj_info.defn_header)
            iface_cpp_proj_defn_target.write(
                f"    operator {ancestor_cpp_proj_info.full_name}() const&;\n"
                f"    operator {ancestor_cpp_proj_info.full_name}() &&;\n"
                f"    operator {ancestor_cpp_proj_info.weak_name}() const&;\n"
            )
        for method in iface.methods:
            method_cpp_proj_info = IfaceMethodDeclCppProjInfo.get(self.am, method)
            params_cpp = []
            for param in method.params:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                iface_cpp_proj_defn_target.include(*type_cpp_proj_info.decl_headers)
                params_cpp.append(f"{type_cpp_proj_info.as_param} {param.name}")
            params_cpp_str = ", ".join(params_cpp)
            if return_ty_ref := method.return_ty_ref:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, return_ty_ref.resolved_ty
                )
                iface_cpp_proj_defn_target.include(*type_cpp_proj_info.decl_headers)
                cpp_return_ty_name = type_cpp_proj_info.as_owner
            else:
                cpp_return_ty_name = "void"
            iface_cpp_proj_defn_target.write(
                f"    {cpp_return_ty_name} {method_cpp_proj_info.name}({params_cpp_str}) const;\n"
            )
        iface_cpp_proj_defn_target.write("};\n" "}\n")

    def gen_iface_param_defn(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        pkg_cpp_proj_info: PackageCppProjInfo,
        iface_cpp_proj_defn_target: COutputBuffer,
    ):
        iface_cpp_proj_defn_target.write(
            f"namespace {pkg_cpp_proj_info.weakspace} {{\n"
            f"struct {iface_cpp_proj_info.name} {{\n"
            f"    {iface_abi_info.as_param} m_handle;\n"
            f"    explicit {iface_cpp_proj_info.name}({iface_abi_info.as_param} other_handle);\n"
            f"    ~{iface_cpp_proj_info.name}();\n"
            f"    {iface_cpp_proj_info.name}({iface_cpp_proj_info.weak_name} const& other);\n"
            f"    operator {iface_cpp_proj_info.full_name} () const&;\n"
            f"    operator ::taihe::core::data_holder() const&;\n"
            f"    operator ::taihe::core::data_view() const&;\n"
            f"    explicit {iface_cpp_proj_info.name}(::taihe::core::data_view other);\n"
            f"    {iface_cpp_proj_info.name}& operator=({iface_cpp_proj_info.weak_name} other);\n"
            f"    operator bool() const&;\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, ancestor)
            iface_cpp_proj_defn_target.include(ancestor_cpp_proj_info.defn_header)
            iface_cpp_proj_defn_target.write(
                f"    operator {ancestor_cpp_proj_info.full_name}() const&;\n"
                f"    operator {ancestor_cpp_proj_info.weak_name}() const&;\n"
            )
        for method in iface.methods:
            method_cpp_proj_info = IfaceMethodDeclCppProjInfo.get(self.am, method)
            params_cpp = []
            for param in method.params:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                iface_cpp_proj_defn_target.include(*type_cpp_proj_info.decl_headers)
                params_cpp.append(f"{type_cpp_proj_info.as_param} {param.name}")
            params_cpp_str = ", ".join(params_cpp)
            if return_ty_ref := method.return_ty_ref:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, return_ty_ref.resolved_ty
                )
                iface_cpp_proj_defn_target.include(*type_cpp_proj_info.decl_headers)
                cpp_return_ty_name = type_cpp_proj_info.as_owner
            else:
                cpp_return_ty_name = "void"
            iface_cpp_proj_defn_target.write(
                f"    {cpp_return_ty_name} {method_cpp_proj_info.name}({params_cpp_str}) const;\n"
            )
        iface_cpp_proj_defn_target.write("};\n" "}\n")

    def gen_iface_trans_funcs(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_defn_target: COutputBuffer,
    ):
        iface_cpp_proj_defn_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"inline {iface_abi_info.as_field} into_abi({iface_cpp_proj_info.as_owner} other){{\n"
            f"    {iface_abi_info.as_field} ret_handle = other.m_handle;\n"
            f"    other.m_handle.data_ptr = nullptr;\n"
            f"    return ret_handle;\n"
            f"}}\n"
            f"template<>\n"
            f"inline {iface_cpp_proj_info.as_owner} from_abi({iface_abi_info.as_field} other_handle){{\n"
            f"    {iface_abi_info.as_field} ret_handle = other_handle;\n"
            f"    return {iface_cpp_proj_info.as_owner}(ret_handle);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {iface_abi_info.as_param} into_abi({iface_cpp_proj_info.as_param} other){{\n"
            f"    {iface_abi_info.as_param} ret_handle = other.m_handle;\n"
            f"    return ret_handle;\n"
            f"}}\n"
            f"template<>\n"
            f"inline {iface_cpp_proj_info.as_param} from_abi({iface_abi_info.as_param} other_handle){{\n"
            f"    {iface_abi_info.as_field} ret_handle = other_handle;\n"
            f"    return {iface_cpp_proj_info.as_param}(ret_handle);\n"
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
            self.tm, f"include/{iface_cpp_proj_info.impl_header}", True
        )
        iface_cpp_proj_impl_target.include(iface_abi_info.impl_header)
        iface_cpp_proj_impl_target.include(iface_cpp_proj_info.defn_header)
        self.gen_iface_owner_impl(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            iface_cpp_proj_impl_target,
            pkg_cpp_proj_info,
        )
        self.gen_iface_param_impl(
            iface,
            iface_abi_info,
            iface_cpp_proj_info,
            iface_cpp_proj_impl_target,
            pkg_cpp_proj_info,
        )
        self.gen_iface_infos(
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

    def gen_iface_owner_impl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_impl_target: COutputBuffer,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        iface_cpp_proj_impl_target.write(
            f"namespace {pkg_cpp_proj_info.namespace} {{\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_abi_info.as_field} other_handle)\n"
            f"    : m_handle(other_handle) {{}}\n"
            f"inline {iface_cpp_proj_info.name}::~{iface_cpp_proj_info.name}() {{\n"
            f"    {iface_abi_info.drop_func}(this->m_handle);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_cpp_proj_info.full_name} && other)\n"
            f"    : m_handle(other.m_handle) {{\n"
            f"    other.m_handle.data_ptr = nullptr;\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_cpp_proj_info.full_name} const& other)\n"
            f"    : m_handle({iface_abi_info.copy_func}(other.m_handle)) {{}}\n"
            f"inline {iface_cpp_proj_info.name}::operator {iface_cpp_proj_info.weak_name} () const& {{\n"
            f"    {iface_abi_info.as_field} ret_handle = this->m_handle;\n"
            f"    return {iface_cpp_proj_info.full_name}(ret_handle);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator ::taihe::core::data_holder() && {{\n"
            f"    {iface_abi_info.as_field} ret_handle = this->m_handle;\n"
            f"    this->m_handle.data_ptr = nullptr;\n"
            f"    return ::taihe::core::data_holder(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator ::taihe::core::data_holder() const& {{\n"
            f"    {iface_abi_info.as_field} ret_handle = {iface_abi_info.copy_func}(this->m_handle);\n"
            f"    return ::taihe::core::data_holder(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator ::taihe::core::data_view() const& {{\n"
            f"    {iface_abi_info.as_field} ret_handle = this->m_handle;\n"
            f"    return ::taihe::core::data_view(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}(::taihe::core::data_holder other)\n"
            f"    : m_handle({iface_abi_info.dynamic_cast}(other.m_handle)) {{\n"
            f"    other.m_handle = nullptr;\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}& {iface_cpp_proj_info.name}::operator=({iface_cpp_proj_info.full_name} other) {{\n"
            f"    ::std::swap(this->m_handle, other.m_handle);\n"
            f"    return *this;\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator bool() const& {{\n"
            f"    return this->m_handle.vtbl_ptr;\n"
            f"}}\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, ancestor)
            iface_cpp_proj_impl_target.include(ancestor_cpp_proj_info.impl_header)
            iface_cpp_proj_impl_target.write(
                f"inline {iface_cpp_proj_info.name}::operator {ancestor_cpp_proj_info.full_name}() && {{\n"
                f"    {iface_abi_info.as_field} ret_handle = this->m_handle;\n"
                f"    this->m_handle.data_ptr = nullptr;\n"
                f"    return {ancestor_cpp_proj_info.full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
                f"inline {iface_cpp_proj_info.name}::operator {ancestor_cpp_proj_info.full_name}() const& {{\n"
                f"    {iface_abi_info.as_field} ret_handle = {iface_abi_info.copy_func}(this->m_handle);\n"
                f"    return {ancestor_cpp_proj_info.full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
                f"inline {iface_cpp_proj_info.name}::operator {ancestor_cpp_proj_info.weak_name}() const& {{\n"
                f"    {iface_abi_info.as_field} ret_handle = this->m_handle;\n"
                f"    return {ancestor_cpp_proj_info.weak_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
            )
        for method in iface.methods:
            method_abi_info = IfaceMethodDeclABIInfo.get(self.am, method)
            method_cpp_proj_info = IfaceMethodDeclCppProjInfo.get(self.am, method)
            params_cpp = []
            args_into_abi = ["this->m_handle"]
            for param in method.params:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                iface_cpp_proj_impl_target.include(*type_cpp_proj_info.defn_headers)
                params_cpp.append(f"{type_cpp_proj_info.as_param} {param.name}")
                args_into_abi.append(type_cpp_proj_info.pass_into_abi(param.name))
            params_cpp_str = ", ".join(params_cpp)
            args_into_abi_str = ", ".join(args_into_abi)
            abi_result = f"{method_abi_info.mangled_name}({args_into_abi_str})"
            if return_ty_ref := method.return_ty_ref:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, return_ty_ref.resolved_ty
                )
                iface_cpp_proj_impl_target.include(*type_cpp_proj_info.defn_headers)
                cpp_return_ty_name = type_cpp_proj_info.as_owner
                cpp_result = type_cpp_proj_info.return_from_abi(abi_result)
            else:
                cpp_return_ty_name = "void"
                cpp_result = abi_result
            iface_cpp_proj_impl_target.write(
                f"inline {cpp_return_ty_name} {iface_cpp_proj_info.name}::{method_cpp_proj_info.name}({params_cpp_str}) const {{\n"
                f"    return {cpp_result};\n"
                f"}}\n"
            )
        iface_cpp_proj_impl_target.write("}\n")

    def gen_iface_param_impl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_impl_target: COutputBuffer,
        pkg_cpp_proj_info: PackageCppProjInfo,
    ):
        iface_cpp_proj_impl_target.write(
            f"namespace {pkg_cpp_proj_info.weakspace} {{\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_abi_info.as_param} other_handle)\n"
            f"    : m_handle(other_handle) {{}}\n"
            f"inline {iface_cpp_proj_info.name}::~{iface_cpp_proj_info.name}() {{}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}({iface_cpp_proj_info.weak_name} const& other)\n"
            f"    : m_handle(other.m_handle) {{}}\n"
            f"inline {iface_cpp_proj_info.name}::operator {iface_cpp_proj_info.full_name} () const& {{\n"
            f"    {iface_abi_info.as_field} ret_handle = {iface_abi_info.copy_func}(this->m_handle);\n"
            f"    return {iface_cpp_proj_info.full_name}(ret_handle);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator ::taihe::core::data_holder() const& {{\n"
            f"    {iface_abi_info.as_field} ret_handle = {iface_abi_info.copy_func}(this->m_handle);\n"
            f"    return ::taihe::core::data_holder(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator ::taihe::core::data_view() const& {{\n"
            f"    {iface_abi_info.as_field} ret_handle = this->m_handle;\n"
            f"    return ::taihe::core::data_view(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::{iface_cpp_proj_info.name}(::taihe::core::data_view other)\n"
            f"    : m_handle({iface_abi_info.dynamic_cast}(other.m_handle)) {{\n"
            f"    other.m_handle = nullptr;\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}& {iface_cpp_proj_info.name}::operator=({iface_cpp_proj_info.weak_name} other) {{\n"
            f"    ::std::swap(this->m_handle, other.m_handle);\n"
            f"    return *this;\n"
            f"}}\n"
            f"inline {iface_cpp_proj_info.name}::operator bool() const& {{\n"
            f"    return this->m_handle.vtbl_ptr;\n"
            f"}}\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_cpp_proj_info = IfaceDeclCppProjInfo.get(self.am, ancestor)
            iface_cpp_proj_impl_target.include(ancestor_cpp_proj_info.impl_header)
            iface_cpp_proj_impl_target.write(
                f"inline {iface_cpp_proj_info.name}::operator {ancestor_cpp_proj_info.weak_name}() const& {{\n"
                f"    {iface_abi_info.as_field} ret_handle = this->m_handle;\n"
                f"    return {ancestor_cpp_proj_info.weak_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
                f"inline {iface_cpp_proj_info.name}::operator {ancestor_cpp_proj_info.full_name}() const& {{\n"
                f"    {iface_abi_info.as_field} ret_handle = {iface_abi_info.copy_func}(this->m_handle);\n"
                f"    return {ancestor_cpp_proj_info.full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
            )
        for method in iface.methods:
            method_abi_info = IfaceMethodDeclABIInfo.get(self.am, method)
            method_cpp_proj_info = IfaceMethodDeclCppProjInfo.get(self.am, method)
            params_cpp = []
            args_into_abi = ["this->m_handle"]
            for param in method.params:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                iface_cpp_proj_impl_target.include(*type_cpp_proj_info.defn_headers)
                params_cpp.append(f"{type_cpp_proj_info.as_param} {param.name}")
                args_into_abi.append(type_cpp_proj_info.pass_into_abi(param.name))
            params_cpp_str = ", ".join(params_cpp)
            args_into_abi_str = ", ".join(args_into_abi)
            abi_result = f"{method_abi_info.mangled_name}({args_into_abi_str})"
            if return_ty_ref := method.return_ty_ref:
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, return_ty_ref.resolved_ty
                )
                iface_cpp_proj_impl_target.include(*type_cpp_proj_info.defn_headers)
                cpp_return_ty_name = type_cpp_proj_info.as_owner
                cpp_result = type_cpp_proj_info.return_from_abi(abi_result)
            else:
                cpp_return_ty_name = "void"
                cpp_result = abi_result
            iface_cpp_proj_impl_target.write(
                f"inline {cpp_return_ty_name} {iface_cpp_proj_info.name}::{method_cpp_proj_info.name}({params_cpp_str}) const {{\n"
                f"    return {cpp_result};\n"
                f"}}\n"
            )
        iface_cpp_proj_impl_target.write("}\n")

    def gen_iface_infos(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
        iface_cpp_proj_info: IfaceDeclCppProjInfo,
        iface_cpp_proj_impl_target: COutputBuffer,
    ):
        iface_cpp_proj_impl_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"struct info_container<{iface_abi_info.mangled_name}> {{\n"
            f"    template<typename Impl>\n"
            f"    struct ftable_space {{\n"
            f"        struct method_table {{\n"
        )
        for method in iface.methods:
            method_cpp_proj_info = IfaceMethodDeclCppProjInfo.get(self.am, method)
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
            cpp_result = f"static_cast<Impl*>(static_cast<::taihe::core::data_block_impl<Impl>*>(tobj.data_ptr))->{method_cpp_proj_info.name}({args_from_abi_str})"
            if return_ty_ref := method.return_ty_ref:
                type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
                type_cpp_proj_info = TypeCppProjInfo.get(
                    self.am, return_ty_ref.resolved_ty
                )
                abi_return_ty_name = type_abi_info.as_field
                abi_result = type_cpp_proj_info.return_into_abi(cpp_result)
            else:
                abi_return_ty_name = "void"
                abi_result = cpp_result
            iface_cpp_proj_impl_target.write(
                f"            static {abi_return_ty_name} {method.name}({params_abi_str}) {{\n"
                f"                return {abi_result};\n"
                f"            }}\n"
            )
        iface_cpp_proj_impl_target.write(
            f"        }};\n"
            f"        static constexpr {iface_abi_info.ftable} ftbl = {{\n"
        )
        for method in iface.methods:
            method_cpp_proj_info = IfaceMethodDeclCppProjInfo.get(self.am, method)
            iface_cpp_proj_impl_target.write(
                f"            .{method.name} = &method_table::{method.name},\n"
            )
        iface_cpp_proj_impl_target.write(
            f"        }};\n"
            f"    }};\n"
            f"    using vtable_t = {iface_abi_info.vtable};\n"
            f"    static constexpr void const* iid = &{iface_abi_info.iid};\n"
            f"    static constexpr uint64_t list_len = {len(iface_abi_info.ancestor_list)};\n"
            f"    static constexpr uint64_t dict_len = {len(iface_abi_info.ancestor_dict)};\n"
            f"    template<typename Impl>\n"
            f"    struct typeinfo_space {{\n"
            f"        static constexpr {iface_abi_info.vtable} vtbl = {{\n"
        )
        for ancestor_info in iface_abi_info.ancestor_list:
            ancestor_abi_info = IfaceDeclABIInfo.get(self.am, ancestor_info.iface)
            iface_cpp_proj_impl_target.write(
                f"            .{ancestor_info.ftbl_ptr} = &::taihe::core::info_container<{ancestor_abi_info.mangled_name}>::template ftable_space<Impl>::ftbl,\n"
            )
        iface_cpp_proj_impl_target.write(
            f"        }};\n"
            f"        static constexpr IdMapItem idmap[{len(iface_abi_info.ancestor_dict)}] = {{\n"
        )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            ancestor_abi_info = IfaceDeclABIInfo.get(self.am, ancestor)
            iface_cpp_proj_impl_target.write(
                f"            {{&{ancestor_abi_info.iid}, &vtbl.{info.ftbl_ptr}}},\n"
            )
        iface_cpp_proj_impl_target.write("        };\n" "    };\n" "};\n" "}\n")

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
            f"struct interface_holder_traits<{iface_cpp_proj_info.full_name}> {{\n"
            f"    using type = void*;\n"
            f"    using info_container = ::taihe::core::info_container<{iface_abi_info.mangled_name}>;\n"
            f"}};\n"
            f"template<>\n"
            f"struct interface_view_traits<{iface_cpp_proj_info.weak_name}> {{\n"
            f"    using type = void*;\n"
            f"    using info_container = ::taihe::core::info_container<{iface_abi_info.mangled_name}>;\n"
            f"}};\n"
            f"}}\n"
        )
