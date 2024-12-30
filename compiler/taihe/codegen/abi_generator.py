from dataclasses import dataclass
from io import StringIO
from os import makedirs, path
from pathlib import Path
from typing import Optional

from typing_extensions import override

from taihe.codegen.mangle import DeclKind, encode
from taihe.semantics.declarations import (
    BaseFuncDecl,
    EnumDecl,
    EnumItemDecl,
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
from taihe.utils.outputs import OutputBase, OutputManager


class COutputBuffer(OutputBase[bool]):
    """Represents a C or C++ target file."""

    def __init__(self, is_header: bool):
        self.is_header = is_header
        self.headers: set[str] = set()
        self.code = StringIO()

    @override
    def save_as(self, file_path: Path):
        if not path.exists(file_path.parent):
            makedirs(file_path.parent, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as dst:
            if self.is_header:
                dst.write(f"#pragma once\n")
            for header in self.headers:
                dst.write(f'#include "{header}"\n')
            dst.write(self.code.getvalue())

    def write(self, code: str):
        self.code.write(code)

    def include(self, *headers: str | None):
        for header in headers:
            if isinstance(header, str):
                self.headers.add(header)


class ABIPackageInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.abi.h"


class ABIBaseFuncDeclInfo(AbstractAnalysis[BaseFuncDecl]):
    def __init__(self, am: AnalysisManager, f: BaseFuncDecl) -> None:
        segments = f.segments
        self.name = encode(segments, DeclKind.FUNCTION)
        if f.return_ty_ref is None:
            self.return_ty_header = None
            self.return_ty_name = "void"
        else:
            ty_info = ABITypeInfo.get(am, f.return_ty_ref.resolved_ty)
            self.return_ty_header = ty_info.header
            self.return_ty_name = ty_info.as_owner


class ABIEnumItemDeclInfo(AbstractAnalysis[EnumItemDecl]):
    def __init__(self, am: AnalysisManager, d: EnumItemDecl) -> None:
        segments = d.segments
        self.name = encode(segments, DeclKind.ENUM_ITEM)


class ABIEnumDeclInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.abi.h"
        self.tag_name = encode(segments, DeclKind.ENUM_TAG)
        self.union_name = encode(segments, DeclKind.ENUM_UNION)
        self.name = encode(segments, DeclKind.ENUM_STRUCT)
        self.as_owner = encode(segments, DeclKind.OWNER_T)
        self.as_param = encode(segments, DeclKind.PARAM_T)
        self.has_data = any(item.ty_ref for item in d.items)
        self.copy_func = (
            None
            if all(
                f.ty_ref is None
                or ABITypeInfo.get(am, f.ty_ref.resolved_ty).copy_func is None
                for f in d.items
            )
            else encode(segments, DeclKind.COPY)
        )
        self.drop_func = (
            None
            if all(
                f.ty_ref is None
                or ABITypeInfo.get(am, f.ty_ref.resolved_ty).drop_func is None
                for f in d.items
            )
            else encode(segments, DeclKind.DROP)
        )


class ABIStructDeclInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.abi.h"
        self.name = encode(segments, DeclKind.STRUCT)
        self.as_owner = encode(segments, DeclKind.OWNER_T)
        self.as_param = encode(segments, DeclKind.PARAM_T)
        self.copy_func = (
            None
            if all(
                ABITypeInfo.get(am, f.ty_ref.resolved_ty).copy_func is None
                for f in d.fields
            )
            else encode(segments, DeclKind.COPY)
        )
        self.drop_func = (
            None
            if all(
                ABITypeInfo.get(am, f.ty_ref.resolved_ty).drop_func is None
                for f in d.fields
            )
            else encode(segments, DeclKind.DROP)
        )


@dataclass
class AncestorInfo:
    offset: int
    static_cast: str


class ABIIfaceDeclInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.parent
        assert p
        segments = d.segments
        self.header_0 = f"{p.name}.{d.name}.abi.0.h"
        self.header_1 = f"{p.name}.{d.name}.abi.1.h"
        self.src = f"{p.name}.{d.name}.c"
        self.name = encode(segments, DeclKind.INTERFACE)
        self.as_owner = encode(segments, DeclKind.OWNER_T)
        self.as_param = encode(segments, DeclKind.PARAM_T)
        self.copy_func = encode(segments, DeclKind.COPY)
        self.drop_func = encode(segments, DeclKind.DROP)
        self.f_table = encode(segments, DeclKind.FTABLE)
        self.v_table = encode(segments, DeclKind.VTABLE)
        self.iid = encode(segments, DeclKind.IID)
        self.dynamic_cast = f"cast_to_{self.name}"
        self.ancestor_list = [d]
        for extend in d.parents:
            iface = extend.ty_ref.resolved_ty
            assert isinstance(iface, IfaceDecl)
            abi_extend_info = ABIIfaceDeclInfo.get(am, iface)
            self.ancestor_list.extend(abi_extend_info.ancestor_list)
        self.ancestor_dict: dict[IfaceDecl, AncestorInfo] = {}
        for i, ancestor in enumerate(self.ancestor_list):
            self.ancestor_dict.setdefault(
                ancestor,
                AncestorInfo(
                    offset=i,
                    static_cast=f"cast_{self.name}_to_{ancestor.name}",
                ),
            )


class ABITypeInfo(AbstractAnalysis[Optional[Type]], TypeVisitor[None]):
    def __init__(self, am: AnalysisManager, t: Optional[Type]) -> None:
        self.am = am
        self.header = None
        self.as_owner = None
        self.as_param = None
        self.copy_func = None
        self.drop_func = None
        self.handle_type(t)

    @override
    def visit_enum_decl(self, d: EnumDecl) -> None:
        abi_enum_info = ABIEnumDeclInfo.get(self.am, d)
        self.header = abi_enum_info.header
        self.as_owner = abi_enum_info.as_owner
        self.as_param = abi_enum_info.as_param
        self.copy_func = abi_enum_info.copy_func
        self.drop_func = abi_enum_info.drop_func

    @override
    def visit_struct_decl(self, d: StructDecl) -> None:
        abi_struct_info = ABIStructDeclInfo.get(self.am, d)
        self.header = abi_struct_info.header
        self.as_owner = abi_struct_info.as_owner
        self.as_param = abi_struct_info.as_param
        self.copy_func = abi_struct_info.copy_func
        self.drop_func = abi_struct_info.drop_func

    @override
    def visit_iface_decl(self, d: IfaceDecl) -> None:
        abi_iface_info = ABIIfaceDeclInfo.get(self.am, d)
        self.header = abi_iface_info.header_0
        self.as_owner = abi_iface_info.as_owner
        self.as_param = abi_iface_info.as_param
        self.copy_func = abi_iface_info.copy_func
        self.drop_func = abi_iface_info.drop_func

    def visit_scalar_type(self, t: ScalarType):
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
        self.as_param = res
        self.as_owner = res
        if res is None:
            raise ValueError

    def visit_special_type(self, t: SpecialType) -> None:
        if t == STRING:
            self.header = "taihe/string.abi.h"
            self.as_owner = "struct TString*"
            self.as_param = "struct TString*"
            self.copy_func = "tstr_dup"
            self.drop_func = "tstr_drop"
        else:
            raise ValueError


class ABICodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: Package):
        abi_pkg_info = ABIPackageInfo.get(self.am, pkg)
        abi_pkg_target = COutputBuffer.create(
            self.tm, f"include/{abi_pkg_info.header}", True
        )

        abi_pkg_target.include("taihe/common.h")

        for struct in pkg.structs:
            self.gen_struct_file(struct, abi_pkg_target)
        for enum in pkg.enums:
            self.gen_enum_file(enum, abi_pkg_target)
        for iface in pkg.interfaces:
            self.gen_iface_files(iface, abi_pkg_target)
        for func in pkg.functions:
            self.gen_func(func, abi_pkg_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        abi_pkg_target: COutputBuffer,
    ):
        abi_func_info = ABIBaseFuncDeclInfo.get(self.am, func)

        params = []
        for param in func.params:
            abi_type_info = ABITypeInfo.get(self.am, param.ty_ref.resolved_ty)
            abi_pkg_target.include(abi_type_info.header)
            params.append(f"{abi_type_info.as_param} {param.name}")
        params_str = ", ".join(params)

        abi_pkg_target.include(abi_func_info.return_ty_header)

        abi_pkg_target.write(
            f"TH_EXPORT {abi_func_info.return_ty_name} {abi_func_info.name}({params_str});\n"
        )

    def gen_struct_file(
        self,
        struct: StructDecl,
        abi_pkg_target: COutputBuffer,
    ):
        abi_struct_info = ABIStructDeclInfo.get(self.am, struct)

        abi_struct_target = COutputBuffer.create(
            self.tm, f"include/{abi_struct_info.header}", True
        )

        abi_struct_target.include("taihe/common.h")

        self.gen_struct_decl(struct, abi_struct_target, abi_struct_info)
        self.gen_struct_copy_func(struct, abi_struct_target, abi_struct_info)
        self.gen_struct_drop_func(struct, abi_struct_target, abi_struct_info)

        abi_pkg_target.include(abi_struct_info.header)

    def gen_struct_decl(
        self,
        struct: StructDecl,
        abi_struct_target: COutputBuffer,
        abi_struct_info: ABIStructDeclInfo,
    ):
        abi_struct_target.write(f"struct {abi_struct_info.name} {{\n")
        for field in struct.fields:
            ty_info = ABITypeInfo.get(self.am, field.ty_ref.resolved_ty)
            abi_struct_target.include(ty_info.header)
            abi_struct_target.write(f"  {ty_info.as_owner} {field.name};\n")
        abi_struct_target.write(
            f"}};\n"
            f"typedef struct {abi_struct_info.name} {abi_struct_info.as_owner};\n"
            f"typedef struct {abi_struct_info.name} const* {abi_struct_info.as_param};\n"
        )

    def gen_struct_copy_func(
        self,
        struct: StructDecl,
        abi_struct_target: COutputBuffer,
        abi_struct_info: ABIStructDeclInfo,
    ):
        if abi_struct_info.copy_func is None:
            return

        abi_struct_target.write(
            f"inline struct {abi_struct_info.name} {abi_struct_info.copy_func}(struct {abi_struct_info.name} const* data_ptr) {{\n"
            f"  struct {abi_struct_info.name} result;\n"
        )
        for field in struct.fields:
            ty_info = ABITypeInfo.get(self.am, field.ty_ref.resolved_ty)
            if ty_info.copy_func is not None:
                abi_struct_target.write(
                    f"  result.{field.name} = {ty_info.copy_func}(data_ptr->{field.name});\n"
                )
            else:
                abi_struct_target.write(
                    f"  result.{field.name} = data_ptr->{field.name};\n"
                )
        abi_struct_target.write("  return result;\n" "}\n")

    def gen_struct_drop_func(
        self,
        struct: StructDecl,
        abi_struct_target: COutputBuffer,
        abi_struct_info: ABIStructDeclInfo,
    ):
        if abi_struct_info.drop_func is None:
            return

        abi_struct_target.write(
            f"inline void {abi_struct_info.drop_func}(struct {abi_struct_info.name} const *data_ptr) {{\n"
        )
        for field in struct.fields:
            ty_info = ABITypeInfo.get(self.am, field.ty_ref.resolved_ty)
            if ty_info.drop_func is not None:
                abi_struct_target.write(
                    f"  {ty_info.drop_func}(data_ptr->{field.name});\n"
                )
        abi_struct_target.write("}\n")

    def gen_enum_file(
        self,
        enum: EnumDecl,
        abi_pkg_target: COutputBuffer,
    ):
        abi_enum_info = ABIEnumDeclInfo.get(self.am, enum)

        abi_enum_target = COutputBuffer.create(
            self.tm, f"include/{abi_enum_info.header}", True
        )

        abi_enum_target.include("taihe/common.h")

        self.gen_enum_tag_decl(enum, abi_enum_target, abi_enum_info)
        self.gen_enum_union_decl(enum, abi_enum_target, abi_enum_info)
        self.gen_enum_struct_decl(enum, abi_enum_target, abi_enum_info)
        self.gen_enum_copy_func(enum, abi_enum_target, abi_enum_info)
        self.gen_enum_drop_func(enum, abi_enum_target, abi_enum_info)

        abi_pkg_target.include(abi_enum_info.header)

    def gen_enum_tag_decl(
        self,
        enum: EnumDecl,
        abi_enum_target: COutputBuffer,
        abi_enum_info: ABIEnumDeclInfo,
    ):
        abi_enum_target.write(f"enum {abi_enum_info.tag_name} {{\n")
        for item in enum.items:
            abi_enum_item_info = ABIEnumItemDeclInfo.get(self.am, item)
            abi_enum_target.write(f"  {abi_enum_item_info.name} = {item.value},\n")
        abi_enum_target.write("};\n")

    def gen_enum_union_decl(
        self,
        enum: EnumDecl,
        abi_enum_target: COutputBuffer,
        abi_enum_info: ABIEnumDeclInfo,
    ):
        if not abi_enum_info.has_data:
            return

        abi_enum_target.write(f"union {abi_enum_info.union_name} {{\n")
        for item in enum.items:
            if item.ty_ref is None:
                continue
            ty_info = ABITypeInfo.get(self.am, item.ty_ref.resolved_ty)
            abi_enum_target.include(ty_info.header)
            abi_enum_target.write(f"  {ty_info.as_owner} {item.name};\n")
        abi_enum_target.write("};\n")

    def gen_enum_struct_decl(
        self,
        enum: EnumDecl,
        abi_enum_target: COutputBuffer,
        abi_enum_info: ABIEnumDeclInfo,
    ):
        abi_enum_target.write(
            f"struct {abi_enum_info.name} {{\n"
            f"  enum {abi_enum_info.tag_name} tag;\n"
        )
        if abi_enum_info.has_data:
            abi_enum_target.write(f"  union {abi_enum_info.union_name} data;\n")
        abi_enum_target.write(
            f"}};\n"
            f"typedef struct {abi_enum_info.name} {abi_enum_info.as_owner};\n"
            f"typedef struct {abi_enum_info.name} const* {abi_enum_info.as_param};\n"
        )

    def gen_enum_copy_func(
        self,
        enum: EnumDecl,
        abi_enum_target: COutputBuffer,
        abi_enum_info: ABIEnumDeclInfo,
    ):
        if abi_enum_info.copy_func is None:
            return

        abi_enum_target.write(
            f"inline struct {abi_enum_info.name} {abi_enum_info.copy_func}(struct {abi_enum_info.name} const* data_ptr) {{\n"
            f"  struct {abi_enum_info.name} result;\n"
            f"  switch (result.tag = data_ptr->tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            ty_info = ABITypeInfo.get(self.am, item.ty_ref.resolved_ty)
            abi_enum_item_info = ABIEnumItemDeclInfo.get(self.am, item)
            if ty_info.copy_func is not None:
                abi_enum_target.write(
                    f"  case {abi_enum_item_info.name}:\n"
                    f"    result.data.{item.name} = {ty_info.copy_func}(data_ptr->data.{item.name});\n"
                    f"    break;\n"
                )
            else:
                abi_enum_target.write(
                    f"  case {abi_enum_item_info.name}:\n"
                    f"    result.data.{item.name} = data_ptr->data.{item.name};\n"
                    f"    break;\n"
                )
        abi_enum_target.write(
            "  default:\n" "    break;\n" "  }\n" "  return result;\n" "}\n"
        )

    def gen_enum_drop_func(
        self,
        enum: EnumDecl,
        abi_enum_target: COutputBuffer,
        abi_enum_info: ABIEnumDeclInfo,
    ):
        if abi_enum_info.drop_func is None:
            return

        abi_enum_target.write(
            f"inline void {abi_enum_info.drop_func}(struct {abi_enum_info.name} const* data_ptr) {{\n"
            f"  switch (data_ptr->tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            ty_info = ABITypeInfo.get(self.am, item.ty_ref.resolved_ty)
            abi_enum_item_info = ABIEnumItemDeclInfo.get(self.am, item)
            if ty_info.copy_func is not None:
                abi_enum_target.write(
                    f"  case {abi_enum_item_info.name}:\n"
                    f"    {ty_info.drop_func}(data_ptr->data.{item.name});\n"
                    f"    break;\n"
                )
        abi_enum_target.write("  default:\n" "    break;\n" "  }\n" "}\n")

    def gen_iface_files(
        self,
        iface: IfaceDecl,
        abi_pkg_target: COutputBuffer,
    ):
        abi_iface_info = ABIIfaceDeclInfo.get(self.am, iface)

        self.gen_iface_0_file(iface, abi_iface_info)
        self.gen_iface_1_file(iface, abi_iface_info)
        self.gen_iface_src_file(iface, abi_iface_info)

        abi_pkg_target.include(abi_iface_info.header_1)

    def gen_iface_0_file(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
    ):
        abi_iface_target_0 = COutputBuffer.create(
            self.tm, f"include/{abi_iface_info.header_0}", True
        )

        abi_iface_target_0.include("taihe/object.abi.h")

        abi_iface_target_0.write(
            f"struct {abi_iface_info.f_table};\n"
            f"struct {abi_iface_info.v_table};\n"
            f"struct {abi_iface_info.name} {{\n"
            f"  struct {abi_iface_info.v_table}* vtbl_ptr;\n"
            f"  struct DataBlockHead* data_ptr;\n"
            f"}};\n"
            f"typedef struct {abi_iface_info.name} {abi_iface_info.as_param};\n"
            f"typedef struct {abi_iface_info.name} {abi_iface_info.as_owner};\n"
        )

        self.gen_iface_copy_func(iface, abi_iface_target_0, abi_iface_info)
        self.gen_iface_drop_func(iface, abi_iface_target_0, abi_iface_info)

    def gen_iface_1_file(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
    ):
        abi_iface_target_1 = COutputBuffer.create(
            self.tm, f"include/{abi_iface_info.header_1}", True
        )

        abi_iface_target_1.include(abi_iface_info.header_0)

        abi_iface_target_1.write(f"TH_EXPORT void const* const {abi_iface_info.iid};\n")

        self.gen_iface_ftable(iface, abi_iface_target_1, abi_iface_info)
        self.gen_iface_vtable(iface, abi_iface_target_1, abi_iface_info)
        self.gen_iface_methods(iface, abi_iface_target_1, abi_iface_info)
        self.gen_iface_static_cast_funcs(iface, abi_iface_target_1, abi_iface_info)
        self.gen_iface_dynamic_cast_func(iface, abi_iface_target_1, abi_iface_info)

    def gen_iface_ftable(
        self,
        iface: IfaceDecl,
        abi_iface_target_1: COutputBuffer,
        abi_iface_info: ABIIfaceDeclInfo,
    ):
        abi_iface_target_1.write(f"struct {abi_iface_info.f_table} {{\n")
        for method in iface.methods:
            abi_method_info = ABIBaseFuncDeclInfo.get(self.am, method)

            params = [f"{abi_iface_info.as_param} tobj"]
            for param in method.params:
                abi_type_info = ABITypeInfo.get(self.am, param.ty_ref.resolved_ty)
                abi_iface_target_1.include(abi_type_info.header)
                params.append(f"{abi_type_info.as_param} {param.name}")
            params_str = ", ".join(params)

            abi_iface_target_1.include(abi_method_info.return_ty_header)

            abi_iface_target_1.write(
                f"  {abi_method_info.return_ty_name} (*{method.name})({params_str});\n"
            )
        abi_iface_target_1.write("};\n")

    def gen_iface_vtable(
        self,
        iface: IfaceDecl,
        abi_iface_target_1: COutputBuffer,
        abi_iface_info: ABIIfaceDeclInfo,
    ):
        abi_iface_target_1.write(f"struct {abi_iface_info.v_table} {{\n")
        for i, ancestor in enumerate(abi_iface_info.ancestor_list):
            abi_ancestor_info = ABIIfaceDeclInfo.get(self.am, ancestor)

            abi_iface_target_1.write(
                f"  struct {abi_ancestor_info.f_table}* ftbl_ptr_{i};\n"
            )
        abi_iface_target_1.write("};\n")

    def gen_iface_methods(
        self,
        iface: IfaceDecl,
        abi_iface_target_1: COutputBuffer,
        abi_iface_info: ABIIfaceDeclInfo,
    ):
        for method in iface.methods:
            abi_method_info = ABIBaseFuncDeclInfo.get(self.am, method)

            params = [f"{abi_iface_info.as_param} tobj"]
            args = ["tobj"]
            for param in method.params:
                abi_type_info = ABITypeInfo.get(self.am, param.ty_ref.resolved_ty)
                params.append(f"{abi_type_info.as_param} {param.name}")
                args.append(param.name)
            params_str = ", ".join(params)
            args_str = ", ".join(args)

            abi_iface_target_1.write(
                f"inline {abi_method_info.return_ty_name} {abi_method_info.name}({params_str}) {{\n"
                f"  return tobj.vtbl_ptr->ftbl_ptr_0->{method.name}({args_str});\n"
                f"}}\n"
            )

    def gen_iface_static_cast_funcs(
        self,
        iface: IfaceDecl,
        abi_iface_target_1: COutputBuffer,
        abi_iface_info: ABIIfaceDeclInfo,
    ):
        for ancestor, info in abi_iface_info.ancestor_dict.items():
            if info.offset == 0:
                continue

            abi_ancestor_info = ABIIfaceDeclInfo.get(self.am, ancestor)

            abi_iface_target_1.include(abi_ancestor_info.header_0)

            abi_iface_target_1.write(
                f"inline struct {abi_ancestor_info.name} {info.static_cast}(struct {abi_iface_info.name} tobj) {{\n"
                f"  struct {abi_ancestor_info.name} result;\n"
                f"  result.vtbl_ptr = (struct {abi_ancestor_info.v_table}*)(&tobj.vtbl_ptr->ftbl_ptr_0 + {info.offset});\n"
                f"  result.data_ptr = tobj.data_ptr;\n"
                f"  return result;\n"
                f"}}\n"
            )

    def gen_iface_dynamic_cast_func(
        self,
        iface: IfaceDecl,
        abi_iface_target_1: COutputBuffer,
        abi_iface_info: ABIIfaceDeclInfo,
    ):
        abi_iface_target_1.write(
            f"inline struct {abi_iface_info.name} {abi_iface_info.dynamic_cast}(struct DataBlockHead* data_ptr) {{\n"
            f"  struct TypeInfo *rtti_ptr = data_ptr->rtti_ptr;\n"
            f"  struct {abi_iface_info.name} result;\n"
            f"  for (size_t i = 0; i < rtti_ptr->len; i++) {{\n"
            f"    if (rtti_ptr->idmap[i].id == {abi_iface_info.iid}) {{\n"
            f"      result.vtbl_ptr = (struct {abi_iface_info.v_table}*)rtti_ptr->idmap[i].vtbl_ptr;\n"
            f"      result.data_ptr = data_ptr;\n"
            f"      return result;\n"
            f"    }}\n"
            f"  }}\n"
            f"  result.vtbl_ptr = NULL;\n"
            f"  result.data_ptr = NULL;\n"
            f"  return result;\n"
            f"}}\n"
        )

    def gen_iface_copy_func(
        self,
        iface: IfaceDecl,
        abi_iface_target_1: COutputBuffer,
        abi_iface_info: ABIIfaceDeclInfo,
    ):
        abi_iface_target_1.write(
            f"inline struct {abi_iface_info.name} {abi_iface_info.copy_func}(struct {abi_iface_info.name} tobj) {{\n"
            f"  struct DataBlockHead* data_ptr = tobj.data_ptr;\n"
            f"  if (data_ptr) {{\n"
            f"    tref_inc(&data_ptr->m_count);\n"
            f"  }}\n"
            f"  return tobj;\n"
            f"}}\n"
        )

    def gen_iface_drop_func(
        self,
        iface: IfaceDecl,
        abi_iface_target_1: COutputBuffer,
        abi_iface_info: ABIIfaceDeclInfo,
    ):
        abi_iface_target_1.write(
            f"inline void {abi_iface_info.drop_func}(struct {abi_iface_info.name} tobj) {{\n"
            f"  struct DataBlockHead* data_ptr = tobj.data_ptr;\n"
            f"  if (data_ptr && tref_dec(&data_ptr->m_count)) {{\n"
            f"    data_ptr->rtti_ptr->free_data(data_ptr);\n"
            f"  }}\n"
            f"}}\n"
        )

    def gen_iface_src_file(
        self,
        iface: IfaceDecl,
        abi_iface_info: ABIIfaceDeclInfo,
    ):
        abi_iface_src = COutputBuffer.create(
            self.tm, f"src/{abi_iface_info.src}", False
        )

        abi_iface_src.include(abi_iface_info.header_1)

        abi_iface_src.write(
            f"void const* const {abi_iface_info.iid} = &{abi_iface_info.iid};\n"
        )
