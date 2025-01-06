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


class PackageABIInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.abi.h"


class BaseFuncDeclABIInfo(AbstractAnalysis[BaseFuncDecl]):
    def __init__(self, am: AnalysisManager, f: BaseFuncDecl) -> None:
        segments = f.segments
        self.mangled_name = encode(segments, DeclKind.FUNCTION)
        if f.return_ty_ref is None:
            self.return_ty_header = None
            self.return_ty_name = "void"
        else:
            ty_info = TypeABIInfo.get(am, f.return_ty_ref.resolved_ty)
            self.return_ty_header = ty_info.header
            self.return_ty_name = ty_info.as_field


class EnumItemDeclABIInfo(AbstractAnalysis[EnumItemDecl]):
    def __init__(self, am: AnalysisManager, d: EnumItemDecl) -> None:
        segments = d.segments
        self.mangled_name = encode(segments, DeclKind.ENUM_ITEM)


class EnumDeclABIInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.node_parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.abi.h"
        self.tag_name = encode(segments, DeclKind.ENUM_TAG)
        self.union_name = encode(segments, DeclKind.ENUM_UNION)
        self.mangled_name = encode(segments, DeclKind.ENUM_STRUCT)
        self.as_field = f"struct {self.mangled_name}"
        self.as_param = f"struct {self.mangled_name} const*"
        self.has_data = any(item.ty_ref for item in d.items)
        self.copy_func = (
            None
            if all(
                f.ty_ref is None
                or TypeABIInfo.get(am, f.ty_ref.resolved_ty).copy_func is None
                for f in d.items
            )
            else encode(segments, DeclKind.COPY)
        )
        self.drop_func = (
            None
            if all(
                f.ty_ref is None
                or TypeABIInfo.get(am, f.ty_ref.resolved_ty).drop_func is None
                for f in d.items
            )
            else encode(segments, DeclKind.DROP)
        )


class StructDeclABIInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.node_parent
        assert p
        segments = d.segments
        self.header = f"{p.name}.{d.name}.abi.h"
        self.mangled_name = encode(segments, DeclKind.STRUCT)
        self.as_field = f"struct {self.mangled_name}"
        self.as_param = f"struct {self.mangled_name} const*"
        self.copy_func = (
            None
            if all(
                TypeABIInfo.get(am, f.ty_ref.resolved_ty).copy_func is None
                for f in d.fields
            )
            else encode(segments, DeclKind.COPY)
        )
        self.drop_func = (
            None
            if all(
                TypeABIInfo.get(am, f.ty_ref.resolved_ty).drop_func is None
                for f in d.fields
            )
            else encode(segments, DeclKind.DROP)
        )


@dataclass
class AncestorItemInfo:
    iface: IfaceDecl
    ptbl_ptr: str


@dataclass
class UniqueAncestorInfo:
    offset: int
    static_cast: str


class IfaceDeclABIInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.node_parent
        assert p
        segments = d.segments
        self.header_0 = f"{p.name}.{d.name}.abi.0.h"
        self.header_1 = f"{p.name}.{d.name}.abi.1.h"
        self.src = f"{p.name}.{d.name}.c"
        self.mangled_name = encode(segments, DeclKind.INTERFACE)
        self.as_field = f"struct {self.mangled_name}"
        self.as_param = f"struct {self.mangled_name}"
        self.copy_func = encode(segments, DeclKind.COPY)
        self.drop_func = encode(segments, DeclKind.DROP)
        self.ftable = encode(segments, DeclKind.FTABLE)
        self.vtable = encode(segments, DeclKind.VTABLE)
        self.rtti = encode(segments, DeclKind.RTTI)
        self.iid = encode(segments, DeclKind.IID)
        self.dynamic_cast = f"cast_to_{self.mangled_name}"
        self.ancestor_list: list[AncestorItemInfo] = []
        self.ancestor_dict: dict[IfaceDecl, UniqueAncestorInfo] = {}
        self.ancestors = [d]
        for extend in d.parents:
            iface = extend.ty_ref.resolved_ty
            assert isinstance(iface, IfaceDecl)
            extend_abi_info = IfaceDeclABIInfo.get(am, iface)
            self.ancestors.extend(extend_abi_info.ancestors)
        for i, ancestor in enumerate(self.ancestors):
            self.ancestor_list.append(
                AncestorItemInfo(
                    iface=ancestor,
                    ptbl_ptr=f"ftbl_ptr_{i}",
                )
            )
            self.ancestor_dict.setdefault(
                ancestor,
                UniqueAncestorInfo(
                    offset=i,
                    static_cast=f"cast_{self.mangled_name}_to_{ancestor.name}",
                ),
            )


class TypeABIInfo(AbstractAnalysis[Optional[Type]], TypeVisitor[None]):
    def __init__(self, am: AnalysisManager, t: Optional[Type]) -> None:
        self.am = am
        self.header = None
        self.as_field = None # type as struct field / union field / return value
        self.as_param = None # type as parameter
        self.copy_func = None
        self.drop_func = None
        self.handle_type(t)

    @override
    def visit_enum_decl(self, d: EnumDecl) -> None:
        enum_abi_info = EnumDeclABIInfo.get(self.am, d)
        self.header = enum_abi_info.header
        self.as_field = enum_abi_info.as_field
        self.as_param = enum_abi_info.as_param
        self.copy_func = enum_abi_info.copy_func
        self.drop_func = enum_abi_info.drop_func

    @override
    def visit_struct_decl(self, d: StructDecl) -> None:
        struct_abi_info = StructDeclABIInfo.get(self.am, d)
        self.header = struct_abi_info.header
        self.as_field = struct_abi_info.as_field
        self.as_param = struct_abi_info.as_param
        self.copy_func = struct_abi_info.copy_func
        self.drop_func = struct_abi_info.drop_func

    @override
    def visit_iface_decl(self, d: IfaceDecl) -> None:
        iface_abi_info = IfaceDeclABIInfo.get(self.am, d)
        self.header = iface_abi_info.header_0
        self.as_field = iface_abi_info.as_field
        self.as_param = iface_abi_info.as_param
        self.copy_func = iface_abi_info.copy_func
        self.drop_func = iface_abi_info.drop_func

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
        self.as_field = res
        if res is None:
            raise ValueError

    def visit_special_type(self, t: SpecialType) -> None:
        if t == STRING:
            self.header = "taihe/string.abi.h"
            self.as_field = "struct TString*"
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
        pkg_abi_info = PackageABIInfo.get(self.am, pkg)
        pkg_abi_target = COutputBuffer.create(
            self.tm, f"include/{pkg_abi_info.header}", True
        )
        pkg_abi_target.include("taihe/common.h")
        for struct in pkg.structs:
            self.gen_struct_file(struct, pkg_abi_target)
        for enum in pkg.enums:
            self.gen_enum_file(enum, pkg_abi_target)
        for iface in pkg.interfaces:
            self.gen_iface_files(iface, pkg_abi_target)
        for func in pkg.functions:
            self.gen_func(func, pkg_abi_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_abi_target: COutputBuffer,
    ):
        func_abi_info = BaseFuncDeclABIInfo.get(self.am, func)
        params = []
        for param in func.params:
            type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_abi_target.include(type_abi_info.header)
            params.append(f"{type_abi_info.as_param} {param.name}")
        params_str = ", ".join(params)
        pkg_abi_target.include(func_abi_info.return_ty_header)
        pkg_abi_target.write(
            f"TH_EXPORT {func_abi_info.return_ty_name} {func_abi_info.mangled_name}({params_str});\n"
        )

    def gen_struct_file(
        self,
        struct: StructDecl,
        pkg_abi_target: COutputBuffer,
    ):
        struct_abi_info = StructDeclABIInfo.get(self.am, struct)
        struct_abi_target = COutputBuffer.create(
            self.tm, f"include/{struct_abi_info.header}", True
        )
        struct_abi_target.include("taihe/common.h")
        self.gen_struct_decl(struct, struct_abi_target, struct_abi_info)
        self.gen_struct_copy_func(struct, struct_abi_target, struct_abi_info)
        self.gen_struct_drop_func(struct, struct_abi_target, struct_abi_info)
        pkg_abi_target.include(struct_abi_info.header)

    def gen_struct_decl(
        self,
        struct: StructDecl,
        struct_abi_target: COutputBuffer,
        struct_abi_info: StructDeclABIInfo,
    ):
        struct_abi_target.write(f"struct {struct_abi_info.mangled_name} {{\n")
        for field in struct.fields:
            ty_info = TypeABIInfo.get(self.am, field.ty_ref.resolved_ty)
            struct_abi_target.include(ty_info.header)
            struct_abi_target.write(f"  {ty_info.as_field} {field.name};\n")
        struct_abi_target.write("};\n")

    def gen_struct_copy_func(
        self,
        struct: StructDecl,
        struct_abi_target: COutputBuffer,
        struct_abi_info: StructDeclABIInfo,
    ):
        if struct_abi_info.copy_func is None:
            return
        struct_abi_target.write(
            f"TH_INLINE struct {struct_abi_info.mangled_name} {struct_abi_info.copy_func}(struct {struct_abi_info.mangled_name} data) {{\n"
            f"  struct {struct_abi_info.mangled_name} result;\n"
        )
        for field in struct.fields:
            ty_info = TypeABIInfo.get(self.am, field.ty_ref.resolved_ty)
            if ty_info.copy_func is not None:
                struct_abi_target.write(
                    f"  result.{field.name} = {ty_info.copy_func}(data.{field.name});\n"
                )
            else:
                struct_abi_target.write(f"  result.{field.name} = data.{field.name};\n")
        struct_abi_target.write("  return result;\n" "}\n")

    def gen_struct_drop_func(
        self,
        struct: StructDecl,
        struct_abi_target: COutputBuffer,
        struct_abi_info: StructDeclABIInfo,
    ):
        if struct_abi_info.drop_func is None:
            return
        struct_abi_target.write(
            f"TH_INLINE void {struct_abi_info.drop_func}(struct {struct_abi_info.mangled_name} data) {{\n"
        )
        for field in struct.fields:
            ty_info = TypeABIInfo.get(self.am, field.ty_ref.resolved_ty)
            if ty_info.drop_func is not None:
                struct_abi_target.write(f"  {ty_info.drop_func}(data.{field.name});\n")
        struct_abi_target.write("}\n")

    def gen_enum_file(
        self,
        enum: EnumDecl,
        pkg_abi_target: COutputBuffer,
    ):
        enum_abi_info = EnumDeclABIInfo.get(self.am, enum)
        enum_abi_target = COutputBuffer.create(
            self.tm, f"include/{enum_abi_info.header}", True
        )
        enum_abi_target.include("taihe/common.h")
        self.gen_enum_tag_decl(enum, enum_abi_target, enum_abi_info)
        self.gen_enum_union_decl(enum, enum_abi_target, enum_abi_info)
        self.gen_enum_struct_decl(enum, enum_abi_target, enum_abi_info)
        self.gen_enum_copy_func(enum, enum_abi_target, enum_abi_info)
        self.gen_enum_drop_func(enum, enum_abi_target, enum_abi_info)
        pkg_abi_target.include(enum_abi_info.header)

    def gen_enum_tag_decl(
        self,
        enum: EnumDecl,
        enum_abi_target: COutputBuffer,
        enum_abi_info: EnumDeclABIInfo,
    ):
        enum_abi_target.write(f"enum {enum_abi_info.tag_name} {{\n")
        for item in enum.items:
            enum_item_abi_info = EnumItemDeclABIInfo.get(self.am, item)
            enum_abi_target.write(
                f"  {enum_item_abi_info.mangled_name} = {item.value},\n"
            )
        enum_abi_target.write("};\n")

    def gen_enum_union_decl(
        self,
        enum: EnumDecl,
        enum_abi_target: COutputBuffer,
        enum_abi_info: EnumDeclABIInfo,
    ):
        enum_abi_target.write(f"union {enum_abi_info.union_name} {{\n")
        for item in enum.items:
            if item.ty_ref is None:
                continue
            ty_info = TypeABIInfo.get(self.am, item.ty_ref.resolved_ty)
            enum_abi_target.include(ty_info.header)
            enum_abi_target.write(f"  {ty_info.as_field} {item.name};\n")
        enum_abi_target.write("};\n")

    def gen_enum_struct_decl(
        self,
        enum: EnumDecl,
        enum_abi_target: COutputBuffer,
        enum_abi_info: EnumDeclABIInfo,
    ):
        enum_abi_target.write(
            f"struct {enum_abi_info.mangled_name} {{\n"
            f"  enum {enum_abi_info.tag_name} tag;\n"
            f"  union {enum_abi_info.union_name} data;\n"
            f"}};\n"
        )

    def gen_enum_copy_func(
        self,
        enum: EnumDecl,
        enum_abi_target: COutputBuffer,
        enum_abi_info: EnumDeclABIInfo,
    ):
        if enum_abi_info.copy_func is None:
            return
        enum_abi_target.write(
            f"TH_INLINE struct {enum_abi_info.mangled_name} {enum_abi_info.copy_func}(struct {enum_abi_info.mangled_name} data) {{\n"
            f"  struct {enum_abi_info.mangled_name} result;\n"
            f"  switch (result.tag = data.tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            ty_info = TypeABIInfo.get(self.am, item.ty_ref.resolved_ty)
            enum_item_abi_info = EnumItemDeclABIInfo.get(self.am, item)
            if ty_info.copy_func is not None:
                enum_abi_target.write(
                    f"  case {enum_item_abi_info.mangled_name}:\n"
                    f"    result.data.{item.name} = {ty_info.copy_func}(data.data.{item.name});\n"
                    f"    return result;\n"
                )
            else:
                enum_abi_target.write(
                    f"  case {enum_item_abi_info.mangled_name}:\n"
                    f"    result.data.{item.name} = data.data.{item.name};\n"
                    f"    return result;\n"
                )
        enum_abi_target.write("  default:\n" "    return result;\n" "  }\n" "}\n")

    def gen_enum_drop_func(
        self,
        enum: EnumDecl,
        enum_abi_target: COutputBuffer,
        enum_abi_info: EnumDeclABIInfo,
    ):
        if enum_abi_info.drop_func is None:
            return
        enum_abi_target.write(
            f"TH_INLINE void {enum_abi_info.drop_func}(struct {enum_abi_info.mangled_name} data) {{\n"
            f"  switch (data.tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            ty_info = TypeABIInfo.get(self.am, item.ty_ref.resolved_ty)
            enum_item_abi_info = EnumItemDeclABIInfo.get(self.am, item)
            if ty_info.copy_func is not None:
                enum_abi_target.write(
                    f"  case {enum_item_abi_info.mangled_name}:\n"
                    f"    {ty_info.drop_func}(data.data.{item.name});\n"
                    f"    break;\n"
                )
        enum_abi_target.write("  default:\n" "    break;\n" "  }\n" "}\n")

    def gen_iface_files(
        self,
        iface: IfaceDecl,
        pkg_abi_target: COutputBuffer,
    ):
        iface_abi_info = IfaceDeclABIInfo.get(self.am, iface)
        self.gen_iface_0_file(iface, iface_abi_info)
        self.gen_iface_1_file(iface, iface_abi_info)
        self.gen_iface_src_file(iface, iface_abi_info)
        pkg_abi_target.include(iface_abi_info.header_1)

    def gen_iface_0_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_target_0 = COutputBuffer.create(
            self.tm, f"include/{iface_abi_info.header_0}", True
        )
        iface_abi_target_0.include("taihe/object.abi.h")
        iface_abi_target_0.write(
            f"struct {iface_abi_info.ftable};\n"
            f"struct {iface_abi_info.vtable};\n"
            f"struct {iface_abi_info.mangled_name} {{\n"
            f"  struct {iface_abi_info.vtable} const* vtbl_ptr;\n"
            f"  struct DataBlockHead* data_ptr;\n"
            f"}};\n"
        )
        self.gen_iface_copy_func(iface, iface_abi_target_0, iface_abi_info)
        self.gen_iface_drop_func(iface, iface_abi_target_0, iface_abi_info)

    def gen_iface_1_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_1_target = COutputBuffer.create(
            self.tm, f"include/{iface_abi_info.header_1}", True
        )
        iface_abi_1_target.include(iface_abi_info.header_0)
        iface_abi_1_target.write(f"TH_EXPORT void const* const {iface_abi_info.iid};\n")
        self.gen_iface_ftable(iface, iface_abi_1_target, iface_abi_info)
        self.gen_iface_vtable(iface, iface_abi_1_target, iface_abi_info)
        self.gen_iface_rtti(iface, iface_abi_1_target, iface_abi_info)
        self.gen_iface_methods(iface, iface_abi_1_target, iface_abi_info)
        self.gen_iface_static_cast_funcs(iface, iface_abi_1_target, iface_abi_info)
        self.gen_iface_dynamic_cast_func(iface, iface_abi_1_target, iface_abi_info)

    def gen_iface_ftable(
        self,
        iface: IfaceDecl,
        iface_abi_1_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_1_target.write(f"struct {iface_abi_info.ftable} {{\n")
        for method in iface.methods:
            method_abi_info = BaseFuncDeclABIInfo.get(self.am, method)
            params = [f"{iface_abi_info.as_param} tobj"]
            for param in method.params:
                type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
                iface_abi_1_target.include(type_abi_info.header)
                params.append(f"{type_abi_info.as_param} {param.name}")
            params_str = ", ".join(params)
            iface_abi_1_target.include(method_abi_info.return_ty_header)
            iface_abi_1_target.write(
                f"  {method_abi_info.return_ty_name} (*{method.name})({params_str});\n"
            )
        iface_abi_1_target.write("};\n")

    def gen_iface_vtable(
        self,
        iface: IfaceDecl,
        iface_abi_1_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_1_target.write(f"struct {iface_abi_info.vtable} {{\n")
        for ancestor_item_info in iface_abi_info.ancestor_list:
            ancestor_abi_info = IfaceDeclABIInfo.get(self.am, ancestor_item_info.iface)
            iface_abi_1_target.write(
                f"  struct {ancestor_abi_info.ftable} const* {ancestor_item_info.ptbl_ptr};\n"
            )
        iface_abi_1_target.write("};\n")

    def gen_iface_rtti(
        self,
        iface: IfaceDecl,
        iface_abi_1_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_1_target.write(
            f"struct {iface_abi_info.rtti} {{\n"
            f"  uint64_t version;\n"
            f"  void (*free_ptr)(struct DataBlockHead*);\n"
            f"  uint64_t len;\n"
            f"  struct IdMapItem idmap[{len(iface_abi_info.ancestor_dict)}];\n"
            f"}};\n"
        )

    def gen_iface_methods(
        self,
        iface: IfaceDecl,
        iface_abi_1_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        for method in iface.methods:
            method_abi_info = BaseFuncDeclABIInfo.get(self.am, method)
            params = [f"{iface_abi_info.as_param} tobj"]
            args = ["tobj"]
            for param in method.params:
                type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
                params.append(f"{type_abi_info.as_param} {param.name}")
                args.append(param.name)
            params_str = ", ".join(params)
            args_str = ", ".join(args)
            iface_abi_1_target.write(
                f"TH_INLINE {method_abi_info.return_ty_name} {method_abi_info.mangled_name}({params_str}) {{\n"
                f"  return tobj.vtbl_ptr->ftbl_ptr_0->{method.name}({args_str});\n"
                f"}}\n"
            )

    def gen_iface_static_cast_funcs(
        self,
        iface: IfaceDecl,
        iface_abi_1_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if info.offset == 0:
                continue
            ancestor_abi_info = IfaceDeclABIInfo.get(self.am, ancestor)
            iface_abi_1_target.include(ancestor_abi_info.header_0)
            iface_abi_1_target.write(
                f"TH_INLINE struct {ancestor_abi_info.mangled_name} {info.static_cast}(struct {iface_abi_info.mangled_name} tobj) {{\n"
                f"  struct {ancestor_abi_info.mangled_name} result;\n"
                f"  result.vtbl_ptr = (struct {ancestor_abi_info.vtable}*)(&tobj.vtbl_ptr->ftbl_ptr_0 + {info.offset});\n"
                f"  result.data_ptr = tobj.data_ptr;\n"
                f"  return result;\n"
                f"}}\n"
            )

    def gen_iface_dynamic_cast_func(
        self,
        iface: IfaceDecl,
        iface_abi_1_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_1_target.write(
            f"TH_INLINE struct {iface_abi_info.mangled_name} {iface_abi_info.dynamic_cast}(struct DataBlockHead* data_ptr) {{\n"
            f"  struct TypeInfo const* rtti_ptr = data_ptr->rtti_ptr;\n"
            f"  struct {iface_abi_info.mangled_name} result;\n"
            f"  result.data_ptr = data_ptr;"
            f"  for (size_t i = 0; i < rtti_ptr->len; i++) {{\n"
            f"    if (rtti_ptr->idmap[i].id == {iface_abi_info.iid}) {{\n"
            f"      result.vtbl_ptr = (struct {iface_abi_info.vtable}*)rtti_ptr->idmap[i].vtbl_ptr;\n"
            f"      return result;\n"
            f"    }}\n"
            f"  }}\n"
            f"  result.vtbl_ptr = NULL;\n"
            f"  return result;\n"
            f"}}\n"
        )

    def gen_iface_copy_func(
        self,
        iface: IfaceDecl,
        iface_abi_1_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_1_target.write(
            f"TH_INLINE struct {iface_abi_info.mangled_name} {iface_abi_info.copy_func}(struct {iface_abi_info.mangled_name} tobj) {{\n"
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
        iface_abi_1_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_1_target.write(
            f"TH_INLINE void {iface_abi_info.drop_func}(struct {iface_abi_info.mangled_name} tobj) {{\n"
            f"  struct DataBlockHead* data_ptr = tobj.data_ptr;\n"
            f"  if (data_ptr && tref_dec(&data_ptr->m_count)) {{\n"
            f"    data_ptr->rtti_ptr->free_ptr(data_ptr);\n"
            f"  }}\n"
            f"}}\n"
        )

    def gen_iface_src_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        abi_iface_src_target = COutputBuffer.create(
            self.tm, f"src/{iface_abi_info.src}", False
        )
        abi_iface_src_target.include(iface_abi_info.header_1)
        abi_iface_src_target.write(
            f"void const* const {iface_abi_info.iid} = &{iface_abi_info.iid};\n"
        )
