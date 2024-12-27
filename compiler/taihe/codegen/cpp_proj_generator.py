from typing import Any, Optional

from typing_extensions import override

from taihe.codegen.abi_generator import (
    ABIEnumDeclInfo,
    ABIFuncBaseDeclInfo,
    ABIPackageInfo,
    ABIStructDeclInfo,
    COutputBuffer,
)
from taihe.semantics.declarations import (
    EnumDecl,
    FuncBaseDecl,
    GlobFuncDecl,
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


class CppProjFuncBaseDeclInfo(AbstractAnalysis[FuncBaseDecl]):
    def __init__(self, am: AnalysisManager, f: FuncBaseDecl) -> None:
        segments = f.segments
        self.name = f.name
        self.full_name = "::" + "::".join(segments)
        if f.return_ty_ref is None:
            self.return_ty_headers = []
            self.return_ty_name = "void"
            self.return_from_abi = lambda val: val
            self.return_into_abi = lambda val: val
        else:
            cpp_return_ty_info = CppProjTypeInfo.get(am, f.return_ty_ref.resolved_ty)
            self.return_ty_headers = [cpp_return_ty_info.header]
            self.return_ty_name = cpp_return_ty_info.as_owner
            self.return_from_abi = cpp_return_ty_info.return_from_abi
            self.return_into_abi = cpp_return_ty_info.return_into_abi


class CppProjStructDeclInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.proj.hpp"
        self.name = d.name
        self.owner_full_name = "::" + "::".join(segments)
        self.param_full_name = "::param::" + "::".join(segments)


class CppProjEnumDeclInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.proj.hpp"
        self.name = d.name
        self.owner_full_name = "::" + "::".join(segments)
        self.param_full_name = "::param::" + "::".join(segments)


class CppProjTypeInfo(AbstractAnalysis[Optional[Type]], TypeVisitor):
    def __init__(self, am: AnalysisManager, t: Optional[Type]) -> None:
        self.am = am
        self.header = None
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
        abi_enum_info = ABIEnumDeclInfo.get(self.am, d)

        self.header = cpp_proj_enum_info.header
        self.as_owner = cpp_proj_enum_info.owner_full_name
        self.as_param = cpp_proj_enum_info.param_full_name
        self.pass_from_abi = (
            lambda val: f"static_cast<{cpp_proj_enum_info.param_full_name}>({val})"
        )
        self.pass_into_abi = lambda val: f"static_cast<{abi_enum_info.as_param}>({val})"
        self.return_from_abi = (
            lambda val: f"static_cast<{cpp_proj_enum_info.owner_full_name}>({val})"
        )
        self.return_into_abi = (
            lambda val: f"static_cast<{abi_enum_info.as_owner}>({val})"
        )

    @override
    def visit_struct_decl(self, d: StructDecl) -> Any:
        cpp_proj_struct_info = CppProjStructDeclInfo.get(self.am, d)
        abi_struct_info = ABIStructDeclInfo.get(self.am, d)

        self.header = cpp_proj_struct_info.header
        self.as_owner = cpp_proj_struct_info.owner_full_name
        self.as_param = cpp_proj_struct_info.param_full_name
        self.pass_from_abi = (
            lambda val: f"taihe::core::from_abi<{cpp_proj_struct_info.param_full_name}, {abi_struct_info.as_param}>(std::move({val}))"
        )
        self.pass_into_abi = (
            lambda val: f"taihe::core::into_abi<{cpp_proj_struct_info.param_full_name}, {abi_struct_info.as_param}>(std::move({val}))"
        )
        self.return_from_abi = (
            lambda val: f"taihe::core::from_abi<{cpp_proj_struct_info.owner_full_name}, {abi_struct_info.as_owner}>(std::move({val}))"
        )
        self.return_into_abi = (
            lambda val: f"taihe::core::into_abi<{cpp_proj_struct_info.owner_full_name}, {abi_struct_info.as_owner}>(std::move({val}))"
        )

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
            self.header = "core/string.hpp"
            self.as_owner = "taihe::core::string"
            self.as_param = "taihe::core::string_view"
            self.pass_from_abi = (
                lambda val: f"taihe::core::from_abi<{self.as_param}, TString*>(std::move({val}))"
            )
            self.pass_into_abi = (
                lambda val: f"taihe::core::into_abi<{self.as_param}, TString*>(std::move({val}))"
            )
            self.return_from_abi = (
                lambda val: f"taihe::core::from_abi<{self.as_owner}, TString*>(std::move({val}))"
            )
            self.return_into_abi = (
                lambda val: f"taihe::core::into_abi<{self.as_owner}, TString*>(std::move({val}))"
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
        for func in pkg.functions:
            self.gen_func(func, cpp_proj_pkg_target, cpp_proj_pkg_info)

    def gen_func(
        self,
        func: GlobFuncDecl,
        cpp_proj_pkg_target: COutputBuffer,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_func_info = CppProjFuncBaseDeclInfo.get(self.am, func)
        abi_func_info = ABIFuncBaseDeclInfo.get(self.am, func)

        cpp_proj_pkg_target.include(*cpp_proj_func_info.return_ty_headers)

        cpp_params = []
        args_into_abi = []
        for param in func.params:
            cpp_proj_type_info = CppProjTypeInfo.get(self.am, param.ty_ref.resolved_ty)
            cpp_proj_pkg_target.include(cpp_proj_type_info.header)
            cpp_params.append(f"{cpp_proj_type_info.as_param} {param.name}")
            args_into_abi.append(cpp_proj_type_info.pass_into_abi(param.name))
        cpp_params_str = ", ".join(cpp_params)
        args_into_abi_str = ",".join(args_into_abi)

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
            struct, cpp_proj_struct_target, cpp_proj_struct_info, cpp_proj_pkg_info
        )
        self.gen_struct_trans_func(
            struct, cpp_proj_struct_target, cpp_proj_struct_info, abi_struct_info
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
            cpp_proj_struct_target.include(ty_info.header)
            cpp_proj_struct_target.write(f"    {ty_info.as_owner} {field.name};\n")
        cpp_proj_struct_target.write(f"}};\n" f"}}\n")

        cpp_proj_struct_target.write(
            f"namespace {cpp_proj_pkg_info.param_namespace} {{\n"
            f"using {cpp_proj_struct_info.name} = {cpp_proj_struct_info.owner_full_name} const&;\n"
            f"}};\n"
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
            f"inline {abi_struct_info.as_owner} taihe::core::into_abi({cpp_proj_struct_info.owner_full_name}&& _val){{\n"
            f"    return {{\n"
        )
        for field in struct.fields:
            cpp_proj_ty_info = CppProjTypeInfo.get(self.am, field.ty_ref.resolved_ty)
            result = cpp_proj_ty_info.return_into_abi(f"_val.{field.name}")
            cpp_proj_struct_target.write(f"        {result},\n")
        cpp_proj_struct_target.write(f"    }};\n" f"}};\n")

        cpp_proj_struct_target.write(
            f"template<>\n"
            f"inline {cpp_proj_struct_info.owner_full_name} taihe::core::from_abi({abi_struct_info.as_owner}&& _val){{\n"
            f"    return {{\n"
        )
        for field in struct.fields:
            cpp_proj_ty_info = CppProjTypeInfo.get(self.am, field.ty_ref.resolved_ty)
            result = cpp_proj_ty_info.return_from_abi(f"_val.{field.name}")
            cpp_proj_struct_target.write(f"        {result},\n")
        cpp_proj_struct_target.write(f"    }};\n" f"}};\n")

        cpp_proj_struct_target.write(
            f"template<>\n"
            f"inline {abi_struct_info.as_param} taihe::core::into_abi({cpp_proj_struct_info.param_full_name}&& _val){{\n"
            f"    return reinterpret_cast<{abi_struct_info.as_param}>(&_val);\n"
            f"}}\n"
        )

        cpp_proj_struct_target.write(
            f"template<>\n"
            f"inline {cpp_proj_struct_info.param_full_name} taihe::core::from_abi({abi_struct_info.as_param}&& _val){{\n"
            f"    return reinterpret_cast<{cpp_proj_struct_info.param_full_name}>(*_val);\n"
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
            enum, cpp_proj_enum_target, cpp_proj_enum_info, cpp_proj_pkg_info
        )

        cpp_proj_pkg_target.include(cpp_proj_enum_info.header)

    def gen_enum_decl(
        self,
        enum: EnumDecl,
        cpp_proj_enum_target: COutputBuffer,
        cpp_proj_enum_info: CppProjEnumDeclInfo,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_enum_target.write(
            f"namespace {cpp_proj_pkg_info.namespace} {{\n"
            f"enum class {cpp_proj_enum_info.name} {{\n"
        )
        for item in enum.items:
            cpp_proj_enum_target.write(f"  {item.name} = {item.value},\n")
        cpp_proj_enum_target.write(f"}};\n" f"}}\n")
