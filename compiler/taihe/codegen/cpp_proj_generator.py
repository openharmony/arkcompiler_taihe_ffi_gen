from typing import Any, Optional

from typing_extensions import override

from taihe.codegen.abi_generator import (
    ABIBaseFuncDeclInfo,
    ABIEnumDeclInfo,
    ABIEnumItemDeclInfo,
    ABIIfaceDeclInfo,
    ABIPackageInfo,
    ABIStructDeclInfo,
    COutputBuffer,
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


class CppProjPackageInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        segments = p.segments
        self.header = f"{p.name}.proj.hpp"
        self.namespace = "::".join(segments)
        self.param_namespace = "::".join(["param", *segments])


class CppProjBaseFuncDeclInfo(AbstractAnalysis[BaseFuncDecl]):
    def __init__(self, am: AnalysisManager, f: BaseFuncDecl) -> None:
        self.name = f.name

        if f.return_ty_ref is None:
            self.return_ty_header_decl = None
            self.return_ty_header_defn = None
            self.return_ty_name = "void"
            self.return_from_abi = lambda val: val
            self.return_into_abi = lambda val: val
        else:
            cpp_return_ty_info = CppProjTypeInfo.get(am, f.return_ty_ref.resolved_ty)
            self.return_ty_header_decl = cpp_return_ty_info.header_decl
            self.return_ty_header_defn = cpp_return_ty_info.header_defn
            self.return_ty_name = cpp_return_ty_info.as_owner
            self.return_from_abi = cpp_return_ty_info.return_from_abi
            self.return_into_abi = cpp_return_ty_info.return_into_abi


class CppProjStructDeclInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        abi_info = ABIStructDeclInfo.get(am, d)

        p = d.parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.proj.hpp"
        self.name = d.name
        self.owner_full_name = "::" + "::".join(segments)
        self.param_full_name = "::param::" + "::".join(segments)
        self.pass_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.param_full_name}, {abi_info.as_param}>(std::move({val}))"
        )
        self.pass_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.param_full_name}, {abi_info.as_param}>(std::move({val}))"
        )
        self.return_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.owner_full_name}, {abi_info.as_owner}>(std::move({val}))"
        )
        self.return_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.owner_full_name}, {abi_info.as_owner}>(std::move({val}))"
        )


class CppProjEnumDeclInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        abi_info = ABIEnumDeclInfo.get(am, d)

        p = d.parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.proj.hpp"
        self.name = d.name
        self.owner_full_name = "::" + "::".join(segments)
        self.param_full_name = "::param::" + "::".join(segments)
        self.pass_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.param_full_name}, {abi_info.as_param}>(std::move({val}))"
        )
        self.pass_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.param_full_name}, {abi_info.as_param}>(std::move({val}))"
        )
        self.return_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.owner_full_name}, {abi_info.as_owner}>(std::move({val}))"
        )
        self.return_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.owner_full_name}, {abi_info.as_owner}>(std::move({val}))"
        )


class CppProjIfaceDeclInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        abi_info = ABIIfaceDeclInfo.get(am, d)

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
            lambda val: f"::taihe::core::from_abi<{self.param_full_name}, {abi_info.as_param}>(std::move({val}))"
        )
        self.pass_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.param_full_name}, {abi_info.as_param}>(std::move({val}))"
        )
        self.return_from_abi = (
            lambda val: f"::taihe::core::from_abi<{self.owner_full_name}, {abi_info.as_owner}>(std::move({val}))"
        )
        self.return_into_abi = (
            lambda val: f"::taihe::core::into_abi<{self.owner_full_name}, {abi_info.as_owner}>(std::move({val}))"
        )


class CppProjTypeInfo(AbstractAnalysis[Optional[Type]], TypeVisitor):
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
        cpp_proj_enum_info = CppProjEnumDeclInfo.get(self.am, d)

        self.header_decl = cpp_proj_enum_info.header
        self.header_defn = cpp_proj_enum_info.header
        self.as_owner = cpp_proj_enum_info.owner_full_name
        self.as_param = cpp_proj_enum_info.param_full_name
        self.pass_from_abi = cpp_proj_enum_info.pass_from_abi
        self.pass_into_abi = cpp_proj_enum_info.pass_into_abi
        self.return_from_abi = cpp_proj_enum_info.return_from_abi
        self.return_into_abi = cpp_proj_enum_info.return_into_abi

    @override
    def visit_struct_decl(self, d: StructDecl) -> Any:
        cpp_proj_struct_info = CppProjStructDeclInfo.get(self.am, d)

        self.header_decl = cpp_proj_struct_info.header
        self.header_defn = cpp_proj_struct_info.header
        self.as_owner = cpp_proj_struct_info.owner_full_name
        self.as_param = cpp_proj_struct_info.param_full_name
        self.pass_from_abi = cpp_proj_struct_info.pass_from_abi
        self.pass_into_abi = cpp_proj_struct_info.pass_into_abi
        self.return_from_abi = cpp_proj_struct_info.return_from_abi
        self.return_into_abi = cpp_proj_struct_info.return_into_abi

    @override
    def visit_iface_decl(self, d: IfaceDecl) -> Any:
        cpp_proj_iface_info = CppProjIfaceDeclInfo.get(self.am, d)

        self.header_decl = cpp_proj_iface_info.header_decl
        self.header_defn = cpp_proj_iface_info.header_defn
        self.as_owner = cpp_proj_iface_info.owner_full_name
        self.as_param = cpp_proj_iface_info.param_full_name
        self.pass_from_abi = cpp_proj_iface_info.pass_from_abi
        self.pass_into_abi = cpp_proj_iface_info.pass_into_abi
        self.return_from_abi = cpp_proj_iface_info.return_from_abi
        self.return_into_abi = cpp_proj_iface_info.return_into_abi

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
                lambda val: f"::taihe::core::from_abi<{self.as_param}, TString*>(std::move({val}))"
            )
            self.pass_into_abi = (
                lambda val: f"::taihe::core::into_abi<{self.as_param}, TString*>(std::move({val}))"
            )
            self.return_from_abi = (
                lambda val: f"::taihe::core::from_abi<{self.as_owner}, TString*>(std::move({val}))"
            )
            self.return_into_abi = (
                lambda val: f"::taihe::core::into_abi<{self.as_owner}, TString*>(std::move({val}))"
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
        cpp_proj_pkg_info = CppProjPackageInfo.get(self.am, pkg)
        cpp_proj_pkg_target = COutputBuffer.create(
            self.tm, f"include/{cpp_proj_pkg_info.header}", True
        )
        abi_pkg_info = ABIPackageInfo.get(self.am, pkg)

        cpp_proj_pkg_target.include("taihe/common.hpp")
        cpp_proj_pkg_target.include(f"{abi_pkg_info.header}")

        for struct in pkg.structs:
            self.gen_struct_file(struct, cpp_proj_pkg_target, cpp_proj_pkg_info)
        for enum in pkg.enums:
            self.gen_enum_file(enum, cpp_proj_pkg_target, cpp_proj_pkg_info)
        for iface in pkg.interfaces:
            self.gen_iface_files(iface, cpp_proj_pkg_target, cpp_proj_pkg_info)
        for func in pkg.functions:
            self.gen_func(func, cpp_proj_pkg_target, cpp_proj_pkg_info)

    def gen_func(
        self,
        func: GlobFuncDecl,
        cpp_proj_pkg_target: COutputBuffer,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_func_info = CppProjBaseFuncDeclInfo.get(self.am, func)
        abi_func_info = ABIBaseFuncDeclInfo.get(self.am, func)

        cpp_params = []
        args_into_abi = []
        for param in func.params:
            cpp_proj_type_info = CppProjTypeInfo.get(self.am, param.ty_ref.resolved_ty)
            cpp_proj_pkg_target.include(cpp_proj_type_info.header_defn)
            cpp_params.append(f"{cpp_proj_type_info.as_param} {param.name}")
            args_into_abi.append(cpp_proj_type_info.pass_into_abi(param.name))
        cpp_params_str = ", ".join(cpp_params)
        args_into_abi_str = ",".join(args_into_abi)

        cpp_proj_pkg_target.include(cpp_proj_func_info.return_ty_header_defn)
        result = cpp_proj_func_info.return_from_abi(
            f"{abi_func_info.name}({args_into_abi_str})"
        )
        cpp_proj_pkg_target.write(
            f"namespace {cpp_proj_pkg_info.namespace} {{\n"
            f"inline {cpp_proj_func_info.return_ty_name} {cpp_proj_func_info.name}({cpp_params_str}) {{\n"
            f"    return {result};\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_struct_file(
        self,
        struct: StructDecl,
        cpp_proj_pkg_target: COutputBuffer,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        abi_struct_info = ABIStructDeclInfo.get(self.am, struct)
        cpp_proj_struct_info = CppProjStructDeclInfo.get(self.am, struct)

        cpp_proj_struct_target = COutputBuffer.create(
            self.tm, f"include/{cpp_proj_struct_info.header}", True
        )

        cpp_proj_struct_target.include("taihe/common.hpp")
        cpp_proj_struct_target.include(abi_struct_info.header)

        self.gen_struct_decl(
            struct,
            cpp_proj_struct_target,
            cpp_proj_struct_info,
            cpp_proj_pkg_info,
        )
        self.gen_struct_trans_func(
            struct,
            cpp_proj_struct_target,
            cpp_proj_struct_info,
            abi_struct_info,
        )

        cpp_proj_pkg_target.include(cpp_proj_struct_info.header)

    def gen_struct_decl(
        self,
        struct: StructDecl,
        cpp_proj_struct_target: COutputBuffer,
        cpp_proj_struct_info: CppProjStructDeclInfo,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_struct_target.write(
            f"namespace {cpp_proj_pkg_info.namespace} {{\n"
            f"struct {cpp_proj_struct_info.name} {{\n"
        )
        for field in struct.fields:
            ty_info = CppProjTypeInfo.get(self.am, field.ty_ref.resolved_ty)
            cpp_proj_struct_target.include(ty_info.header_defn)
            cpp_proj_struct_target.write(f"    {ty_info.as_owner} {field.name};\n")
        cpp_proj_struct_target.write(f"}};\n" f"}}\n")

        cpp_proj_struct_target.write(
            f"namespace {cpp_proj_pkg_info.param_namespace} {{\n"
            f"using {cpp_proj_struct_info.name} = {cpp_proj_struct_info.owner_full_name} const&;\n"
            f"}}\n"
        )

    def gen_struct_trans_func(
        self,
        struct: StructDecl,
        cpp_proj_struct_target: COutputBuffer,
        cpp_proj_struct_info: CppProjStructDeclInfo,
        abi_struct_info: ABIStructDeclInfo,
    ):
        cpp_proj_struct_target.write(
            f"template<>\n"
            f"inline {abi_struct_info.as_owner} taihe::core::into_abi({cpp_proj_struct_info.owner_full_name}&& val){{\n"
            f"    return {{\n"
        )
        for field in struct.fields:
            cpp_proj_ty_info = CppProjTypeInfo.get(self.am, field.ty_ref.resolved_ty)
            result = cpp_proj_ty_info.return_into_abi(f"val.{field.name}")
            cpp_proj_struct_target.write(f"        {result},\n")
        cpp_proj_struct_target.write(f"    }};\n" f"}}\n")

        cpp_proj_struct_target.write(
            f"template<>\n"
            f"inline {cpp_proj_struct_info.owner_full_name} taihe::core::from_abi({abi_struct_info.as_owner}&& val){{\n"
            f"    return {{\n"
        )
        for field in struct.fields:
            cpp_proj_ty_info = CppProjTypeInfo.get(self.am, field.ty_ref.resolved_ty)
            result = cpp_proj_ty_info.return_from_abi(f"val.{field.name}")
            cpp_proj_struct_target.write(f"        {result},\n")
        cpp_proj_struct_target.write(f"    }};\n" f"}}\n")

        cpp_proj_struct_target.write(
            f"template<>\n"
            f"inline {abi_struct_info.as_param} taihe::core::into_abi({cpp_proj_struct_info.param_full_name}&& val){{\n"
            f"    return reinterpret_cast<{abi_struct_info.as_param}>(&val);\n"
            f"}}\n"
        )

        cpp_proj_struct_target.write(
            f"template<>\n"
            f"inline {cpp_proj_struct_info.param_full_name} taihe::core::from_abi({abi_struct_info.as_param}&& val){{\n"
            f"    return reinterpret_cast<{cpp_proj_struct_info.param_full_name}>(*val);\n"
            f"}}\n"
        )

    def gen_enum_file(
        self,
        enum: EnumDecl,
        cpp_proj_pkg_target: COutputBuffer,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_enum_info = CppProjEnumDeclInfo.get(self.am, enum)
        abi_enum_info = ABIEnumDeclInfo.get(self.am, enum)

        cpp_proj_enum_target = COutputBuffer.create(
            self.tm, f"include/{cpp_proj_enum_info.header}", True
        )

        cpp_proj_enum_target.include("taihe/common.hpp")
        cpp_proj_enum_target.include(abi_enum_info.header)

        self.gen_enum_decl(
            enum,
            cpp_proj_enum_target,
            cpp_proj_enum_info,
            abi_enum_info,
            cpp_proj_pkg_info,
        )
        self.gen_enum_trans_func(
            enum,
            cpp_proj_enum_target,
            cpp_proj_enum_info,
            abi_enum_info,
        )

        cpp_proj_pkg_target.include(cpp_proj_enum_info.header)

    def gen_enum_decl(
        self,
        enum: EnumDecl,
        cpp_proj_enum_target: COutputBuffer,
        cpp_proj_enum_info: CppProjEnumDeclInfo,
        abi_enum_info: ABIEnumDeclInfo,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_enum_target.write(
            f"namespace {cpp_proj_pkg_info.namespace} {{\n"
            f"struct {cpp_proj_enum_info.name} {{\n"
        )

        cpp_proj_enum_target.write("    enum class Tag {\n")
        for item in enum.items:
            cpp_proj_enum_target.write(f"        {item.name} = {item.value},\n")
        cpp_proj_enum_target.write("    } tag;\n")

        cpp_proj_enum_target.write("    struct ConstexprTagType {\n")
        for item in enum.items:
            cpp_proj_enum_target.write(
                f"        struct {item.name} {{\n"
                f"            static constexpr Tag tag = Tag::{item.name};\n"
                f"        }};\n"
            )
        cpp_proj_enum_target.write("    };\n")

        cpp_proj_enum_target.write("    struct ConstexprTag {\n")
        for item in enum.items:
            cpp_proj_enum_target.write(
                f"        static constexpr ConstexprTagType::{item.name} {item.name};\n"
            )
        cpp_proj_enum_target.write("    };\n")

        cpp_proj_enum_target.write(
            "    union Data {\n" "        Data() {}\n" "        ~Data() {}\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                owner_type = "std::monostate"
            else:
                ty_info = CppProjTypeInfo.get(self.am, item.ty_ref.resolved_ty)
                cpp_proj_enum_target.include(ty_info.header_defn)
                owner_type = ty_info.as_owner
            cpp_proj_enum_target.write(
                f"        {owner_type} {item.name};\n"
                f"        template<typename... Args>\n"
                f"        void ctor(ConstexprTagType::{item.name}, Args&&... args) {{\n"
                f"            new (this) decltype({item.name})(std::forward<Args>(args)...);\n"
                f"        }}\n"
                f"        auto get(ConstexprTagType::{item.name}) {{\n"
                f"            return &{item.name};\n"
                f"        }}\n"
                f"        void dtor(ConstexprTagType::{item.name}) {{\n"
                f"            {item.name}.~decltype({item.name})();\n"
                f"        }}\n"
            )
        cpp_proj_enum_target.write("    } data;\n")

        cpp_proj_enum_target.write(
            f"    {cpp_proj_enum_info.name}({cpp_proj_enum_info.name} const& other) : tag(other.tag) {{\n"
            f"        switch(tag) {{\n"
        )
        for item in enum.items:
            cpp_proj_enum_target.write(
                f"        case Tag::{item.name}:\n"
                f"            data.ctor(ConstexprTag::{item.name}, other.data);\n"
                f"            break;\n"
            )
        cpp_proj_enum_target.write(
            "        default:\n" "            break;\n" "        }\n" "    }\n"
        )

        cpp_proj_enum_target.write(
            f"    {cpp_proj_enum_info.name}({cpp_proj_enum_info.name}&& other) : tag(other.tag) {{\n"
            f"        switch(tag) {{\n"
        )
        for item in enum.items:
            cpp_proj_enum_target.write(
                f"        case Tag::{item.name}:\n"
                f"            data.ctor(ConstexprTag::{item.name}, std::move(other.data));\n"
                f"            break;\n"
            )
        cpp_proj_enum_target.write(
            "        default:\n" "            break;\n" "        }\n" "    }\n"
        )

        cpp_proj_enum_target.write(
            f"    ~{cpp_proj_enum_info.name}() {{\n" f"        switch(tag) {{\n"
        )
        for item in enum.items:
            cpp_proj_enum_target.write(
                f"        case Tag::{item.name}:\n"
                f"            data.dtor(ConstexprTag::{item.name});\n"
                f"            break;\n"
            )
        cpp_proj_enum_target.write(
            "        default:\n" "            break;\n" "        }\n" "    }\n"
        )

        cpp_proj_enum_target.write(
            f"    template<typename T, typename... Args>\n"
            f"    {cpp_proj_enum_info.name}(T t, Args&&... args) : tag(T::tag) {{\n"
            f"        this->data.ctor(t, std::forward<Args>(args)...);\n"
            f"    }}\n"
            f"    template<typename T, typename... Args>\n"
            f"    void emplace(T t, Args&&... args) {{\n"
            f"        this->~{cpp_proj_enum_info.name}();\n"
            f"        this->tag = T::tag;\n"
            f"        this->data.ctor(t, std::forward<Args>(args)...);\n"
            f"    }}\n"
            f"    template<typename T>\n"
            f"    auto get_ptr(T t) {{\n"
            f"        return tag == T::tag ? data.get(t) : nullptr;\n"
            f"    }}\n"
            f"    {cpp_proj_enum_info.name} const& operator=({cpp_proj_enum_info.name} const& other) {{\n"
            f"        if (this != &other) {{\n"
            f"            this->~{cpp_proj_enum_info.name}();\n"
            f"            new (this) {cpp_proj_enum_info.name}(other);\n"
            f"        }}\n"
            f"        return *this;\n"
            f"    }}\n"
            f"    {cpp_proj_enum_info.name} const& operator=({cpp_proj_enum_info.name}&& other) {{\n"
            f"        if (this != &other) {{\n"
            f"            this->~{cpp_proj_enum_info.name}();\n"
            f"            new (this) {cpp_proj_enum_info.name}(std::move(other));\n"
            f"        }}\n"
            f"        return *this;\n"
            f"    }}\n"
        )

        cpp_proj_enum_target.write(f"}};\n" f"}}\n")

        cpp_proj_enum_target.write(
            f"namespace {cpp_proj_pkg_info.param_namespace} {{\n"
            f"using {cpp_proj_enum_info.name} = {cpp_proj_enum_info.owner_full_name} const&;\n"
            f"}}\n"
        )

    def gen_enum_trans_func(
        self,
        enum: EnumDecl,
        cpp_proj_enum_target: COutputBuffer,
        cpp_proj_enum_info: CppProjEnumDeclInfo,
        abi_enum_info: ABIEnumDeclInfo,
    ):
        cpp_proj_enum_target.write(
            f"template<>\n"
            f"inline {abi_enum_info.as_owner} taihe::core::into_abi({cpp_proj_enum_info.owner_full_name}&& val){{\n"
            f"    {abi_enum_info.as_owner} result;\n"
            f"    switch (val.tag) {{\n"
        )
        for item in enum.items:
            abi_enum_item_info = ABIEnumItemDeclInfo.get(self.am, item)
            if item.ty_ref is None:
                cpp_proj_enum_target.write(
                    f"    case {cpp_proj_enum_info.owner_full_name}::Tag::{item.name}:\n"
                    f"        result.tag = {abi_enum_item_info.name};\n"
                    f"        break;\n"
                )
            else:
                cpp_proj_ty_info = CppProjTypeInfo.get(self.am, item.ty_ref.resolved_ty)
                result = cpp_proj_ty_info.return_into_abi(f"val.data.{item.name}")
                cpp_proj_enum_target.write(
                    f"    case {cpp_proj_enum_info.owner_full_name}::Tag::{item.name}:\n"
                    f"        result.tag = {abi_enum_item_info.name};\n"
                    f"        result.data.{item.name} = {result};\n"
                    f"        break;\n"
                )
        cpp_proj_enum_target.write(f"    }}\n" f"    return result;\n" f"}}\n")

        cpp_proj_enum_target.write(
            f"template<>\n"
            f"inline {cpp_proj_enum_info.owner_full_name} taihe::core::from_abi({abi_enum_info.as_owner}&& val){{\n"
            f"    switch (val.tag) {{\n"
        )
        for item in enum.items:
            abi_enum_item_info = ABIEnumItemDeclInfo.get(self.am, item)
            if item.ty_ref is None:
                cpp_proj_enum_target.write(
                    f"    case {abi_enum_item_info.name}:\n"
                    f"        return {cpp_proj_enum_info.owner_full_name}({cpp_proj_enum_info.owner_full_name}::ConstexprTag::{item.name});\n"
                )
            else:
                cpp_proj_ty_info = CppProjTypeInfo.get(self.am, item.ty_ref.resolved_ty)
                result = cpp_proj_ty_info.return_from_abi(f"val.data.{item.name}")
                cpp_proj_enum_target.write(
                    f"    case {abi_enum_item_info.name}:\n"
                    f"        return {cpp_proj_enum_info.owner_full_name}({cpp_proj_enum_info.owner_full_name}::ConstexprTag::{item.name}, {result});\n"
                )
        cpp_proj_enum_target.write(f"    }}\n" f"}}\n")

        cpp_proj_enum_target.write(
            f"template<>\n"
            f"inline {abi_enum_info.as_param} taihe::core::into_abi({cpp_proj_enum_info.param_full_name}&& val){{\n"
            f"    return reinterpret_cast<{abi_enum_info.as_param}>(&val);\n"
            f"}}\n"
        )

        cpp_proj_enum_target.write(
            f"template<>\n"
            f"inline {cpp_proj_enum_info.param_full_name} taihe::core::from_abi({abi_enum_info.as_param}&& val){{\n"
            f"    return reinterpret_cast<{cpp_proj_enum_info.param_full_name}>(*val);\n"
            f"}}\n"
        )

    def gen_iface_files(
        self,
        iface: IfaceDecl,
        cpp_proj_pkg_target: COutputBuffer,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        abi_iface_info = ABIIfaceDeclInfo.get(self.am, iface)
        cpp_proj_iface_info = CppProjIfaceDeclInfo.get(self.am, iface)

        self.gen_iface_decl_file(
            iface,
            abi_iface_info,
            cpp_proj_iface_info,
            cpp_proj_pkg_info,
        )
        self.gen_iface_defn_file(
            iface,
            abi_iface_info,
            cpp_proj_iface_info,
            cpp_proj_pkg_info,
        )
        self.gen_iface_impl_file(
            iface,
            abi_iface_info,
            cpp_proj_iface_info,
            cpp_proj_pkg_info,
        )

        cpp_proj_pkg_target.include(cpp_proj_iface_info.header_impl)

    def gen_iface_decl_file(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
        cpp_proj_iface_info: CppProjIfaceDeclInfo,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_iface_decl_target = COutputBuffer.create(
            self.tm, f"include/{cpp_proj_iface_info.header_decl}", True
        )

        cpp_proj_iface_decl_target.write(
            f"namespace {cpp_proj_pkg_info.namespace} {{\n"
            f"struct {cpp_proj_iface_info.name};\n"
            f"}}\n"
            f"namespace {cpp_proj_pkg_info.param_namespace} {{\n"
            f"struct {cpp_proj_iface_info.name};\n"
            f"}}\n"
        )

    def gen_iface_defn_file(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
        cpp_proj_iface_info: CppProjIfaceDeclInfo,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_iface_defn_target = COutputBuffer.create(
            self.tm, f"include/{cpp_proj_iface_info.header_defn}", True
        )

        cpp_proj_iface_defn_target.include("core/object.hpp")
        cpp_proj_iface_defn_target.include(abi_iface_info.header_0)
        cpp_proj_iface_defn_target.include(cpp_proj_iface_info.header_decl)

        self.gen_iface_defn_owner_decl(
            iface,
            abi_iface_info,
            cpp_proj_iface_info,
            cpp_proj_pkg_info,
            cpp_proj_iface_defn_target,
        )
        self.gen_iface_defn_param_decl(
            iface,
            abi_iface_info,
            cpp_proj_iface_info,
            cpp_proj_pkg_info,
            cpp_proj_iface_defn_target,
        )

    def gen_iface_defn_owner_decl(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
        cpp_proj_iface_info: CppProjIfaceDeclInfo,
        cpp_proj_pkg_info: CppProjPackageInfo,
        cpp_proj_iface_defn_target: COutputBuffer,
    ):
        cpp_proj_iface_defn_target.write(
            f"namespace {cpp_proj_pkg_info.namespace} {{\n"
            f"struct {cpp_proj_iface_info.name} {{\n"
            f"    {abi_iface_info.as_owner} m_handle;\n"
            f"    {cpp_proj_iface_info.name}({abi_iface_info.as_owner} other_handle);\n"
            f"    ~{cpp_proj_iface_info.name}();\n"
            f"    {cpp_proj_iface_info.name}({cpp_proj_iface_info.owner_full_name} const& other);\n"
            f"    {cpp_proj_iface_info.name}({cpp_proj_iface_info.owner_full_name} && other);\n"
            f"    {cpp_proj_iface_info.name}({cpp_proj_iface_info.param_full_name} const& other);\n"
            f"    operator ::taihe::core::DataOwner() const&;\n"
            f"    operator ::taihe::core::DataOwner() &&;\n"
            f"    operator ::taihe::core::DataRef() const&;\n"
            f"    {cpp_proj_iface_info.name}(::taihe::core::DataOwner other);\n"
            f"    {cpp_proj_iface_info.name} &operator=({cpp_proj_iface_info.owner_full_name} other);\n"
            f"    operator bool();\n"
        )

        for ancestor, info in abi_iface_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            cpp_proj_ancestor_info = CppProjIfaceDeclInfo.get(self.am, ancestor)
            cpp_proj_iface_defn_target.include(cpp_proj_ancestor_info.header_decl)
            cpp_proj_iface_defn_target.write(
                f"    operator {cpp_proj_ancestor_info.owner_full_name}() const&;\n"
                f"    operator {cpp_proj_ancestor_info.owner_full_name}() &&;\n"
                f"    operator {cpp_proj_ancestor_info.param_full_name}() const&;\n"
            )

        for method in iface.methods:
            cpp_proj_method_info = CppProjBaseFuncDeclInfo.get(self.am, method)

            params = []
            for param in method.params:
                cpp_proj_type_info = CppProjTypeInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                cpp_proj_iface_defn_target.include(cpp_proj_type_info.header_decl)
                params.append(f"{cpp_proj_type_info.as_param} {param.name}")
            params_str = ", ".join(params)

            cpp_proj_iface_defn_target.include(
                cpp_proj_method_info.return_ty_header_decl
            )

            cpp_proj_iface_defn_target.write(
                f"    {cpp_proj_method_info.return_ty_name} {method.name}({params_str});\n"
            )

        cpp_proj_iface_defn_target.write("};\n" "}\n")

    def gen_iface_defn_param_decl(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
        cpp_proj_iface_info: CppProjIfaceDeclInfo,
        cpp_proj_pkg_info: CppProjPackageInfo,
        cpp_proj_iface_defn_target: COutputBuffer,
    ):
        cpp_proj_iface_defn_target.write(
            f"namespace {cpp_proj_pkg_info.param_namespace} {{\n"
            f"struct {cpp_proj_iface_info.name} {{\n"
            f"    {abi_iface_info.as_param} m_handle;\n"
            f"    {cpp_proj_iface_info.name}({abi_iface_info.as_param} other_handle);\n"
            f"    ~{cpp_proj_iface_info.name}();\n"
            f"    {cpp_proj_iface_info.name}({cpp_proj_iface_info.owner_full_name} const& other);\n"
            f"    {cpp_proj_iface_info.name}({cpp_proj_iface_info.param_full_name} const& other);\n"
            f"    operator ::taihe::core::DataOwner() const&;\n"
            f"    operator ::taihe::core::DataRef() const&;\n"
            f"    {cpp_proj_iface_info.name}(::taihe::core::DataRef other);\n"
            f"    {cpp_proj_iface_info.name}& operator=({cpp_proj_iface_info.param_full_name} other);\n"
            f"    operator bool();\n"
        )

        for ancestor, info in abi_iface_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            cpp_proj_ancestor_info = CppProjIfaceDeclInfo.get(self.am, ancestor)
            cpp_proj_iface_defn_target.include(cpp_proj_ancestor_info.header_decl)
            cpp_proj_iface_defn_target.write(
                f"    operator {cpp_proj_ancestor_info.owner_full_name}() const&;\n"
                f"    operator {cpp_proj_ancestor_info.param_full_name}() const&;\n"
            )

        for method in iface.methods:
            cpp_proj_method_info = CppProjBaseFuncDeclInfo.get(self.am, method)

            params = []
            for param in method.params:
                cpp_proj_type_info = CppProjTypeInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                cpp_proj_iface_defn_target.include(cpp_proj_type_info.header_decl)
                params.append(f"{cpp_proj_type_info.as_param} {param.name}")
            params_str = ", ".join(params)

            cpp_proj_iface_defn_target.include(
                cpp_proj_method_info.return_ty_header_decl
            )

            cpp_proj_iface_defn_target.write(
                f"    {cpp_proj_method_info.return_ty_name} {method.name}({params_str});\n"
            )

        cpp_proj_iface_defn_target.write("};\n" "}\n")

    def gen_iface_impl_file(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
        cpp_proj_iface_info: CppProjIfaceDeclInfo,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_iface_impl_target = COutputBuffer.create(
            self.tm, f"include/{cpp_proj_iface_info.header_impl}", True
        )

        cpp_proj_iface_impl_target.include(abi_iface_info.header_1)
        cpp_proj_iface_impl_target.include(cpp_proj_iface_info.header_defn)

        self.gen_iface_impl_owner_decl(
            iface,
            abi_iface_info,
            cpp_proj_iface_info,
            cpp_proj_iface_impl_target,
            cpp_proj_pkg_info,
        )
        self.gen_iface_impl_param_decl(
            iface,
            abi_iface_info,
            cpp_proj_iface_info,
            cpp_proj_iface_impl_target,
            cpp_proj_pkg_info,
        )
        self.gen_iface_trans_funcs(
            iface,
            abi_iface_info,
            cpp_proj_iface_info,
            cpp_proj_iface_impl_target,
        )

    def gen_iface_impl_owner_decl(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
        cpp_proj_iface_info: CppProjIfaceDeclInfo,
        cpp_proj_iface_impl_target: COutputBuffer,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_iface_impl_target.write(
            f"namespace {cpp_proj_pkg_info.namespace} {{\n"
        )

        cpp_proj_iface_impl_target.write(
            f"inline {cpp_proj_iface_info.name}::{cpp_proj_iface_info.name}({abi_iface_info.as_owner} other_handle)\n"
            f"    : m_handle(other_handle) {{}}\n"
            f"inline {cpp_proj_iface_info.name}::~{cpp_proj_iface_info.name}() {{\n"
            f"    {abi_iface_info.drop_func}(this->m_handle);\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}::{cpp_proj_iface_info.name}({cpp_proj_iface_info.owner_full_name} && other)\n"
            f"    : m_handle(other.m_handle) {{\n"
            f"    other.m_handle.data_ptr = nullptr;\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}::{cpp_proj_iface_info.name}({cpp_proj_iface_info.owner_full_name} const& other)\n"
            f"    : m_handle({abi_iface_info.copy_func}(other.m_handle)) {{}}\n"
            f"inline {cpp_proj_iface_info.name}::{cpp_proj_iface_info.name}({cpp_proj_iface_info.param_full_name} const& other)\n"
            f"    : m_handle({abi_iface_info.copy_func}(other.m_handle)) {{}}\n"
            f"inline {cpp_proj_iface_info.name}::operator ::taihe::core::DataOwner() && {{\n"
            f"    {abi_iface_info.as_owner} ret_handle = this->m_handle;\n"
            f"    this->m_handle.data_ptr = nullptr;\n"
            f"    return ::taihe::core::DataOwner(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}::operator ::taihe::core::DataOwner() const& {{\n"
            f"    {abi_iface_info.as_owner} ret_handle = {abi_iface_info.copy_func}(this->m_handle);\n"
            f"    return ::taihe::core::DataOwner(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}::operator ::taihe::core::DataRef() const& {{\n"
            f"    {abi_iface_info.as_owner} ret_handle = this->m_handle;\n"
            f"    return ::taihe::core::DataRef(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}::{cpp_proj_iface_info.name}(::taihe::core::DataOwner other)\n"
            f"    : m_handle({abi_iface_info.dynamic_cast}(other.m_handle)) {{\n"
            f"    other.m_handle = nullptr;\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}& {cpp_proj_iface_info.name}::operator=({cpp_proj_iface_info.owner_full_name} other) {{\n"
            f"    std::swap(this->m_handle, other.m_handle);\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}::operator bool() {{\n"
            f"    return this->m_handle.vtbl_ptr;\n"
            f"}}\n"
        )

        for ancestor, info in abi_iface_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            cpp_proj_ancestor_info = CppProjIfaceDeclInfo.get(self.am, ancestor)
            cpp_proj_iface_impl_target.include(cpp_proj_ancestor_info.header_defn)
            cpp_proj_iface_impl_target.write(
                f"inline {cpp_proj_iface_info.name}::operator {cpp_proj_ancestor_info.owner_full_name}() && {{\n"
                f"    {abi_iface_info.as_owner} ret_handle = this->m_handle;\n"
                f"    this->m_handle.data_ptr = nullptr;\n"
                f"    return {cpp_proj_ancestor_info.owner_full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
                f"inline {cpp_proj_iface_info.name}::operator {cpp_proj_ancestor_info.owner_full_name}() const& {{\n"
                f"    {abi_iface_info.as_owner} ret_handle = {abi_iface_info.copy_func}(this->m_handle);\n"
                f"    return {cpp_proj_ancestor_info.owner_full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
                f"inline {cpp_proj_iface_info.name}::operator {cpp_proj_ancestor_info.param_full_name}() const& {{\n"
                f"    {abi_iface_info.as_owner} ret_handle = this->m_handle;\n"
                f"    return {cpp_proj_ancestor_info.param_full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
            )

        for method in iface.methods:
            abi_method_info = ABIBaseFuncDeclInfo.get(self.am, method)
            cpp_proj_method_info = CppProjBaseFuncDeclInfo.get(self.am, method)

            params = []
            args_into_abi = ["this->m_handle"]
            for param in method.params:
                cpp_proj_type_info = CppProjTypeInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                cpp_proj_iface_impl_target.include(cpp_proj_type_info.header_defn)
                params.append(f"{cpp_proj_type_info.as_param} {param.name}")
                args_into_abi.append(cpp_proj_type_info.pass_into_abi(param.name))
            params_str = ", ".join(params)
            args_into_abi_str = ",".join(args_into_abi)

            cpp_proj_iface_impl_target.include(
                cpp_proj_method_info.return_ty_header_defn
            )

            result = cpp_proj_method_info.return_from_abi(
                f"{abi_method_info.name}({args_into_abi_str})"
            )

            cpp_proj_iface_impl_target.write(
                f"inline {cpp_proj_method_info.return_ty_name} {cpp_proj_iface_info.name}::{method.name}({params_str}) {{\n"
                f"    return {result};\n"
                f"}}\n"
            )

        cpp_proj_iface_impl_target.write("}\n")

    def gen_iface_impl_param_decl(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
        cpp_proj_iface_info: CppProjIfaceDeclInfo,
        cpp_proj_iface_impl_target: COutputBuffer,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_iface_impl_target.write(
            f"namespace {cpp_proj_pkg_info.param_namespace} {{\n"
        )

        cpp_proj_iface_impl_target.write(
            f"inline {cpp_proj_iface_info.name}::{cpp_proj_iface_info.name}({abi_iface_info.as_param} other_handle)\n"
            f"    : m_handle(other_handle) {{}}\n"
            f"inline {cpp_proj_iface_info.name}::~{cpp_proj_iface_info.name}() {{}}\n"
            f"inline {cpp_proj_iface_info.name}::{cpp_proj_iface_info.name}({cpp_proj_iface_info.owner_full_name} const& other)\n"
            f"    : m_handle(other.m_handle) {{}}\n"
            f"inline {cpp_proj_iface_info.name}::{cpp_proj_iface_info.name}({cpp_proj_iface_info.owner_full_name} const& other)\n"
            f"    : m_handle(other.m_handle) {{}}\n"
            f"inline {cpp_proj_iface_info.name}::operator ::taihe::core::DataOwner() const& {{\n"
            f"    {abi_iface_info.as_owner} ret_handle = {abi_iface_info.copy_func}(this->m_handle);\n"
            f"    return ::taihe::core::DataOwner(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}::operator ::taihe::core::DataRef() const& {{\n"
            f"    {abi_iface_info.as_owner} ret_handle = this->m_handle;\n"
            f"    return ::taihe::core::DataRef(ret_handle.data_ptr);\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}::{cpp_proj_iface_info.name}(::taihe::core::DataRef other)\n"
            f"    : m_handle({abi_iface_info.dynamic_cast}(other.m_handle)) {{\n"
            f"    other.m_handle = nullptr;\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}& {cpp_proj_iface_info.name}::operator=({cpp_proj_iface_info.param_full_name} other) {{\n"
            f"    std::swap(this->m_handle, other.m_handle);\n"
            f"}}\n"
            f"inline {cpp_proj_iface_info.name}::operator bool() {{\n"
            f"    return this->m_handle.vtbl_ptr;\n"
            f"}}\n"
        )

        for ancestor, info in abi_iface_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            cpp_proj_ancestor_info = CppProjIfaceDeclInfo.get(self.am, ancestor)
            cpp_proj_iface_impl_target.include(cpp_proj_ancestor_info.header_defn)
            cpp_proj_iface_impl_target.write(
                f"inline {cpp_proj_iface_info.name}::operator {cpp_proj_ancestor_info.owner_full_name}() const& {{\n"
                f"    {abi_iface_info.as_owner} ret_handle = {abi_iface_info.copy_func}(this->m_handle);\n"
                f"    return {cpp_proj_ancestor_info.owner_full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
                f"inline {cpp_proj_iface_info.name}::operator {cpp_proj_ancestor_info.param_full_name}() const& {{\n"
                f"    {abi_iface_info.as_owner} ret_handle = this->m_handle;\n"
                f"    return {cpp_proj_ancestor_info.param_full_name}({info.static_cast}(ret_handle));\n"
                f"}}\n"
            )

        for method in iface.methods:
            abi_method_info = ABIBaseFuncDeclInfo.get(self.am, method)
            cpp_proj_method_info = CppProjBaseFuncDeclInfo.get(self.am, method)

            params = []
            args_into_abi = ["this->m_handle"]
            for param in method.params:
                cpp_proj_type_info = CppProjTypeInfo.get(
                    self.am, param.ty_ref.resolved_ty
                )
                cpp_proj_iface_impl_target.include(cpp_proj_type_info.header_defn)
                params.append(f"{cpp_proj_type_info.as_param} {param.name}")
                args_into_abi.append(cpp_proj_type_info.pass_into_abi(param.name))
            params_str = ", ".join(params)
            args_into_abi_str = ",".join(args_into_abi)

            cpp_proj_iface_impl_target.include(
                cpp_proj_method_info.return_ty_header_defn
            )

            result = cpp_proj_method_info.return_from_abi(
                f"{abi_method_info.name}({args_into_abi_str})"
            )

            cpp_proj_iface_impl_target.write(
                f"inline {cpp_proj_method_info.return_ty_name} {cpp_proj_iface_info.name}::{method.name}({params_str}) {{\n"
                f"    return {result};\n"
                f"}}\n"
            )

        cpp_proj_iface_impl_target.write("}\n")

    def gen_iface_trans_funcs(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
        cpp_proj_iface_info: CppProjIfaceDeclInfo,
        cpp_proj_iface_impl_target: COutputBuffer,
    ):
        cpp_proj_iface_impl_target.write(
            f"template<>\n"
            f"inline {abi_iface_info.as_owner} taihe::core::into_abi({cpp_proj_iface_info.owner_full_name}&& other){{\n"
            f"    {abi_iface_info.as_owner} ret_handle = other.m_handle;\n"
            f"    other.m_handle.data_ptr = nullptr;\n"
            f"    return ret_handle;\n"
            f"}}\n"
            f"template<>\n"
            f"inline {cpp_proj_iface_info.owner_full_name} taihe::core::from_abi({abi_iface_info.as_owner}&& other_handle){{\n"
            f"    {abi_iface_info.as_owner} ret_handle = other_handle;\n"
            f"    other_handle.data_ptr = nullptr;\n"
            f"    return {cpp_proj_iface_info.owner_full_name}(ret_handle);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {abi_iface_info.as_param} taihe::core::into_abi({cpp_proj_iface_info.param_full_name}&& other){{\n"
            f"    {abi_iface_info.as_param} ret_handle = other.m_handle;\n"
            f"    return ret_handle;\n"
            f"}}\n"
            f"template<>\n"
            f"inline {cpp_proj_iface_info.param_full_name} taihe::core::from_abi({abi_iface_info.as_param}&& other_handle){{\n"
            f"    {abi_iface_info.as_owner} ret_handle = other_handle;\n"
            f"    return {cpp_proj_iface_info.param_full_name}(ret_handle);\n"
            f"}}\n"
        )
