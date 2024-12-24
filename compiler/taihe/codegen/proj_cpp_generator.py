from typing import Any

from typing_extensions import override

from taihe.codegen.generator import (
    ABIEnumDeclInfo,
    ABIFuncBaseDeclInfo,
    ABINormalTypeRefDeclInfo,
    ABIPackageInfo,
    ABIStructDeclInfo,
    COutputBuffer,
)
from taihe.semantics.declarations import (
    EnumDecl,
    FuncBaseDecl,
    FuncDecl,
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
    TypeAlike,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager


class CppProjPackageInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.proj.hpp"
        self.full_name = p.name.replace(".", "::")


class CppProjFuncBaseDeclInfo(AbstractAnalysis[FuncBaseDecl]):
    def __init__(self, am: AnalysisManager, f: FuncBaseDecl) -> None:
        segments = f.segments
        self.name = f.name
        self.full_name = "::" + "::".join(segments)
        if len(f.retvals) == 0:
            self.return_ty_header = None
            self.return_ty_name = "void"
            self.return_ty_struct_name = None
            self.return_from_abi = ""
            self.return_into_abi = ""
        elif len(f.retvals) == 1:
            cpp_retval_info = CppProjNormalTypeRefDeclInfo.get(am, f.retvals[0].ty)
            abi_func_info = ABIFuncBaseDeclInfo.get(am, f)
            self.return_ty_header = cpp_retval_info.header
            self.return_ty_name = cpp_retval_info.name
            self.return_ty_struct_name = None
            self.return_from_abi = f"taihe::core::from_abi<{self.return_ty_name}, {abi_func_info.return_ty_name}>"
            self.return_into_abi = f"taihe::core::into_abi<{self.return_ty_name}, {abi_func_info.return_ty_name}>"
        else:
            abi_func_info = ABIFuncBaseDeclInfo.get(am, f)
            self.return_ty_header = None
            self.return_ty_struct_name = f.name + "__return_t"
            self.cpp_retval_parts = []
            self.abi_retval_parts = []
            self.cpp_retval_headers = []
            for return_type in f.retvals:
                cpp_retval_info = CppProjNormalTypeRefDeclInfo.get(am, return_type.ty)
                self.cpp_retval_parts.append(cpp_retval_info.name)
                abi_retval_info = ABINormalTypeRefDeclInfo.get(am, return_type.ty)
                self.abi_retval_parts.append(abi_retval_info.name)
                self.cpp_retval_headers.append(cpp_retval_info.header)
            self.return_ty_name = f"std::tuple<{', '.join(self.cpp_retval_parts)}>"
            self.return_from_abi = f"taihe::core::from_abi<{self.return_ty_name}, {abi_func_info.return_ty_struct_name}>"
            self.return_into_abi = f"taihe::core::into_abi<{self.return_ty_name}, {abi_func_info.return_ty_struct_name}>"


class CppProjStructDeclInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.abi.hpp"
        self.name = d.name
        self.full_name = "::" + "::".join(segments)


class CppProjEnumDeclInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.abi.hpp"
        self.name = d.name
        self.full_name = "::" + "::".join(segments)


class CppProjNormalTypeRefDeclInfo(AbstractAnalysis[TypeAlike], TypeVisitor):
    def __init__(self, am: AnalysisManager, t: TypeAlike) -> None:
        self.am = am
        self.header = None
        self.name = None
        self.copy_func = lambda a: a
        self.drop_func = lambda _: None
        self.handle_type(t)

    @override
    def visit_enum_decl(self, d: EnumDecl) -> Any:
        cpp_proj_enum_info = CppProjEnumDeclInfo.get(self.am, d)
        self.header = cpp_proj_enum_info.header
        self.name = cpp_proj_enum_info.full_name

    @override
    def visit_struct_decl(self, d: StructDecl) -> Any:
        cpp_proj_struct_info = CppProjStructDeclInfo.get(self.am, d)
        self.header = cpp_proj_struct_info.header
        self.name = cpp_proj_struct_info.full_name

    def visit_scalar_type(self, t: ScalarType):
        self.name = {
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
        if self.name is None:
            raise ValueError

    def visit_special_type(self, t: SpecialType) -> Any:
        if t == STRING:
            self.header = "core/string.hpp"
            self.name = "taihe::core::string"
        else:
            raise ValueError


class CppProjParamTypeRefDeclInfo(CppProjNormalTypeRefDeclInfo):
    @override
    def visit_struct_decl(self, d: StructDecl) -> Any:
        cpp_proj_struct_info = CppProjStructDeclInfo.get(self.am, d)
        self.header = cpp_proj_struct_info.header
        self.name = f"const {cpp_proj_struct_info.full_name}&"

    @override
    def visit_special_type(self, t: SpecialType) -> Any:
        if t == STRING:
            self.header = "core/string.hpp"
            self.name = "taihe::core::string_view"
        else:
            raise ValueError


class CppProjGenerator:
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
            self.gen_return_ty(func, cpp_proj_pkg_target)
        for func in pkg.functions:
            self.gen_func(func, cpp_proj_pkg_target, cpp_proj_pkg_info)

    def gen_func(
        self,
        func: FuncDecl,
        cpp_proj_pkg_target: COutputBuffer,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_func_info = CppProjFuncBaseDeclInfo.get(self.am, func)
        abi_func_info = ABIFuncBaseDeclInfo.get(self.am, func)

        cpp_proj_pkg_target.include(cpp_proj_func_info.return_ty_header)

        cpp_params = []
        args_into_abi = []
        for param in func.params:
            cpp_proj_param_type_info = CppProjParamTypeRefDeclInfo.get(
                self.am, param.ty
            )
            abi_param_type_info = ABINormalTypeRefDeclInfo.get(self.am, param.ty)
            cpp_proj_pkg_target.include(cpp_proj_param_type_info.header)
            cpp_params.append(f"{cpp_proj_param_type_info.name} {param.name}")
            args_into_abi.append(
                f"taihe::core::into_abi<{cpp_proj_param_type_info.name}, {abi_param_type_info.name}>(static_cast<std::add_rvalue_reference_t<{cpp_proj_param_type_info.name}>>({param.name}))"
            )
        cpp_params_str = ", ".join(cpp_params)
        args_into_abi_str = ",".join(args_into_abi)

        cpp_proj_pkg_target.write(
            f"namespace {cpp_proj_pkg_info.full_name} {{\n"
            f"inline {cpp_proj_func_info.return_ty_name} {cpp_proj_func_info.name}({cpp_params_str}) {{\n"
            f"    return {cpp_proj_func_info.return_from_abi}({abi_func_info.name}({args_into_abi_str}));\n"
            f"}}\n"
            f"}}\n"
        )

    def gen_return_ty(
        self,
        func: FuncBaseDecl,
        cpp_proj_pkg_target: COutputBuffer,
    ):
        cpp_proj_func_info = CppProjFuncBaseDeclInfo.get(self.am, func)
        abi_func_info = ABIFuncBaseDeclInfo.get(self.am, func)

        if abi_func_info.return_ty_struct_name is None:
            return

        cpp_proj_pkg_target.write(
            f"template<>\n"
            f"inline {cpp_proj_func_info.return_ty_name} taihe::core::from_abi(std::add_rvalue_reference_t<{abi_func_info.return_ty_name}> _val) {{\n"
            f"    return {{\n"
        )
        for i, (cpp_return_part, abi_return_part, cpp_header) in enumerate(
            zip(
                cpp_proj_func_info.cpp_retval_parts,
                cpp_proj_func_info.abi_retval_parts,
                cpp_proj_func_info.cpp_retval_headers,
                strict=True,
            )
        ):
            cpp_proj_pkg_target.include(cpp_header)
            cpp_proj_pkg_target.write(
                f"        taihe::core::from_abi<{cpp_return_part}, {abi_return_part}>(static_cast<std::add_rvalue_reference_t<{abi_return_part}>>(_val._{i})),\n"
            )
        cpp_proj_pkg_target.write(f"    }};\n")
        cpp_proj_pkg_target.write(f"}};\n")

    def gen_struct_file(
        self,
        struct: StructDecl,
        cpp_proj_pkg_target: COutputBuffer,
        cpp_proj_pkg_info: CppProjPackageInfo,
    ):
        cpp_proj_struct_info = CppProjStructDeclInfo.get(self.am, struct)
        abi_struct_info = ABIStructDeclInfo.get(self.am, struct)

        cpp_proj_struct_target = COutputBuffer.create(
            self.tm, f"include/{cpp_proj_struct_info.header}", True
        )

        cpp_proj_struct_target.include("taihe/common.h")
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
            f"namespace {cpp_proj_pkg_info.full_name} {{\n"
            f"struct {cpp_proj_struct_info.name} {{\n"
        )
        for field in struct.fields:
            ty_info = ABINormalTypeRefDeclInfo.get(self.am, field.ty)
            cpp_proj_struct_target.include(ty_info.header)
            cpp_proj_struct_target.write(f"  {ty_info.name} {field.name};\n")
        cpp_proj_struct_target.write(f"}};\n" f"}}\n")

    def gen_struct_trans_func(
        self,
        struct: StructDecl,
        cpp_proj_struct_target: COutputBuffer,
        cpp_proj_struct_info: CppProjStructDeclInfo,
        abi_struct_info: ABIStructDeclInfo,
    ):
        cpp_proj_struct_target.write(
            f"template<>\n"
            f"inline {abi_struct_info.name} taihe::core::into_abi(std::add_rvalue_reference_t<{cpp_proj_struct_info.full_name}> _val){{\n"
            f"    return {{\n"
        )
        for field in struct.fields:
            abi_ty_info = ABINormalTypeRefDeclInfo.get(self.am, field.ty)
            cpp_proj_ty_info = CppProjNormalTypeRefDeclInfo.get(self.am, field.ty)
            cpp_proj_struct_target.write(
                f"    taihe::core::into_abi<{cpp_proj_ty_info.name}, {abi_ty_info.name}>(static_cast<std::add_rvalue_reference_t<{cpp_proj_ty_info.name}>>(_val.{field.name})),\n"
            )

        cpp_proj_struct_target.write(f"    }};\n" f"}};\n")

        cpp_proj_struct_target.write(
            f"template<>\n"
            f"inline {cpp_proj_struct_info.name} taihe::core::from_abi(std::add_rvalue_reference_t<{abi_struct_info.name}> _val){{\n"
            f"    return {{\n"
        )
        for field in struct.fields:
            abi_ty_info = ABINormalTypeRefDeclInfo.get(self.am, field.ty)
            cpp_proj_ty_info = CppProjNormalTypeRefDeclInfo.get(self.am, field.ty)
            cpp_proj_struct_target.write(
                f"    taihe::core::from_abi<{cpp_proj_ty_info.name}, {abi_ty_info.name}>(static_cast<std::add_rvalue_reference_t<{abi_ty_info.name}>>(_val.{field.name})),\n"
            )

        cpp_proj_struct_target.write(f"    }};\n" f"}};\n")
        cpp_proj_struct_target.write(
            f"template<>\n"
            f"inline {abi_struct_info.name} *taihe::core::into_abi(std::add_rvalue_reference_t<{cpp_proj_struct_info.name} &> _val){{\n"
            f"    return reinterpret_cast<{abi_struct_info.name} *>(&_val);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {cpp_proj_struct_info.name} &taihe::core::from_abi(std::add_rvalue_reference_t<{abi_struct_info.name} *> _val){{\n"
            f"    return reinterpret_cast<{cpp_proj_struct_info.name} *>(*_val);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {abi_struct_info.name} const *taihe::core::into_abi(std::add_rvalue_reference_t<{cpp_proj_struct_info.name} const &> _val){{\n"
            f"    return reinterpret_cast<{abi_struct_info.name} const *>(&_val);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {cpp_proj_struct_info.name} *taihe::core::from_abi(std::add_rvalue_reference_t<{abi_struct_info.name} const *> _val){{\n"
            f"    return reinterpret_cast<{cpp_proj_struct_info.name} const &>(*_val);\n"
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
        self.gen_enum_trans_func(
            cpp_proj_enum_target, cpp_proj_enum_info, abi_enum_info
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
            f"namespace {cpp_proj_pkg_info.full_name} {{\n"
            f"enum class {cpp_proj_enum_info.name} {{\n"
        )
        for item in enum.items:
            cpp_proj_enum_target.write(f"  {item.name} = {item.value},\n")
        cpp_proj_enum_target.write(f"}};\n" f"}}\n")

    def gen_enum_trans_func(
        self,
        cpp_proj_enum_target: COutputBuffer,
        cpp_proj_enum_info: CppProjEnumDeclInfo,
        abi_enum_info: ABIEnumDeclInfo,
    ):
        cpp_proj_enum_target.write(
            f"template<>\n"
            f"inline {abi_enum_info.name} taihe::core::into_abi(std::add_rvalue_reference_t<{cpp_proj_enum_info.full_name}> _val){{\n"
            f"    return static_cast<{abi_enum_info.name}>(_val);\n"
            f"}}\n"
            f"template<>\n"
            f"inline {cpp_proj_enum_info.full_name} taihe::core::from_abi(std::add_rvalue_reference_t<{abi_enum_info.name}> _val){{\n"
            f"    return static_cast<{cpp_proj_enum_info.full_name}>(_val);\n"
            f"}}\n"
        )
