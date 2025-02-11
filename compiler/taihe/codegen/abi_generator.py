from abc import ABCMeta
from dataclasses import dataclass

from typing_extensions import override

from taihe.codegen.mangle import DeclKind, encode
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
    ArrayType,
    EnumType,
    IfaceType,
    MapType,
    ScalarType,
    SetType,
    SpecialType,
    StructType,
    Type,
    VectorType,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import COutputBuffer, OutputManager


class PackageABIInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.abi.hpp"


class GlobFuncDeclABIInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        p = f.node_parent
        assert p
        segments = [*p.segments, f.name]
        self.mangled_name = encode(segments, DeclKind.FUNCTION)


class IfaceMethodDeclABIInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, f: IfaceMethodDecl) -> None:
        d = f.node_parent
        assert d
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name, f.name]
        self.mangled_name = encode(segments, DeclKind.FUNCTION)


class EnumDeclABIInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name]
        self.decl_header = f"{p.name}.{d.name}.abi.0.hpp"
        self.defn_header = f"{p.name}.{d.name}.abi.1.hpp"
        self.tag_type = "size_t"
        self.union_name = encode(segments, DeclKind.ENUM_UNION)
        self.mangled_name = encode(segments, DeclKind.ENUM_STRUCT)
        self.as_field = f"struct {self.mangled_name}"
        self.as_param = f"struct {self.mangled_name} const*"
        self.has_data = any(item.ty_ref for item in d.items)
        self.copy_func = encode(segments, DeclKind.COPY)
        self.drop_func = encode(segments, DeclKind.DROP)


class StructDeclABIInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name]
        self.decl_header = f"{p.name}.{d.name}.abi.0.hpp"
        self.defn_header = f"{p.name}.{d.name}.abi.1.hpp"
        self.mangled_name = encode(segments, DeclKind.STRUCT)
        self.as_field = f"struct {self.mangled_name}"
        self.as_param = f"struct {self.mangled_name} const*"
        self.copy_func = encode(segments, DeclKind.COPY)
        self.drop_func = encode(segments, DeclKind.DROP)


@dataclass
class AncestorItemInfo:
    iface: IfaceDecl
    ftbl_ptr: str


@dataclass
class UniqueAncestorInfo:
    offset: int
    static_cast: str
    ftbl_ptr: str


class IfaceDeclABIInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name]
        self.decl_header = f"{p.name}.{d.name}.abi.0.hpp"
        self.defn_header = f"{p.name}.{d.name}.abi.1.hpp"
        self.impl_header = f"{p.name}.{d.name}.abi.2.hpp"
        self.src = f"{p.name}.{d.name}.cpp"
        self.mangled_name = encode(segments, DeclKind.INTERFACE)
        self.as_field = f"struct {self.mangled_name}"
        self.as_param = f"struct {self.mangled_name}"
        self.copy_func = encode(segments, DeclKind.COPY)
        self.drop_func = encode(segments, DeclKind.DROP)
        self.ftable = encode(segments, DeclKind.FTABLE)
        self.vtable = encode(segments, DeclKind.VTABLE)
        self.iid = encode(segments, DeclKind.IID)
        self.dynamic_cast = f"cast_to_{self.mangled_name}"
        self.ancestor_list: list[AncestorItemInfo] = []
        self.ancestor_dict: dict[IfaceDecl, UniqueAncestorInfo] = {}
        self.ancestors = [d]
        for extend in d.parents:
            ty = extend.ty_ref.resolved_ty
            assert isinstance(ty, IfaceType)
            extend_abi_info = IfaceDeclABIInfo.get(am, ty.ty_decl)
            self.ancestors.extend(extend_abi_info.ancestors)
        for i, ancestor in enumerate(self.ancestors):
            ftbl_ptr = f"ftbl_ptr_{i}"
            self.ancestor_list.append(
                AncestorItemInfo(
                    iface=ancestor,
                    ftbl_ptr=ftbl_ptr,
                )
            )
            ancestor_abi_info = IfaceDeclABIInfo.get(am, ancestor) if i != 0 else self
            self.ancestor_dict.setdefault(
                ancestor,
                UniqueAncestorInfo(
                    offset=i,
                    static_cast=f"cast_{self.mangled_name}_to_{ancestor_abi_info.mangled_name}",
                    ftbl_ptr=ftbl_ptr,
                ),
            )


class AbstractTypeABIInfo(metaclass=ABCMeta):
    decl_headers: list[str]
    defn_headers: list[str]
    # type as struct field / union field / return value
    as_field: str
    # type as parameter
    as_param: str
    copy_func: str | None
    drop_func: str | None


class EnumTypeABIInfo(AbstractAnalysis[EnumType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        enum_abi_info = EnumDeclABIInfo.get(am, t.ty_decl)
        self.decl_headers = [enum_abi_info.decl_header]
        self.defn_headers = [enum_abi_info.defn_header]
        self.as_field = enum_abi_info.as_field
        self.as_param = enum_abi_info.as_param
        self.copy_func = enum_abi_info.copy_func
        self.drop_func = enum_abi_info.drop_func


class StructTypeABIInfo(AbstractAnalysis[StructType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: StructType) -> None:
        struct_abi_info = StructDeclABIInfo.get(am, t.ty_decl)
        self.decl_headers = [struct_abi_info.decl_header]
        self.defn_headers = [struct_abi_info.defn_header]
        self.as_field = struct_abi_info.as_field
        self.as_param = struct_abi_info.as_param
        self.copy_func = struct_abi_info.copy_func
        self.drop_func = struct_abi_info.drop_func


class IfaceTypeABIInfo(AbstractAnalysis[IfaceType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType) -> None:
        iface_abi_info = IfaceDeclABIInfo.get(am, t.ty_decl)
        self.decl_headers = [iface_abi_info.decl_header]
        self.defn_headers = [iface_abi_info.defn_header]
        self.as_field = iface_abi_info.as_field
        self.as_param = iface_abi_info.as_param
        self.copy_func = iface_abi_info.copy_func
        self.drop_func = iface_abi_info.drop_func


class ScalarTypeABIInfo(AbstractAnalysis[ScalarType], AbstractTypeABIInfo):
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
        self.decl_headers = ["taihe/string.abi.h"]
        self.defn_headers = ["taihe/string.abi.h"]
        self.as_param = res
        self.as_field = res
        self.copy_func = None
        self.drop_func = None


class SpecialTypeABIInfo(AbstractAnalysis[SpecialType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: SpecialType) -> None:
        if t != STRING:
            raise ValueError
        self.decl_headers = ["taihe/string.abi.h"]
        self.defn_headers = ["taihe/string.abi.h"]
        self.as_field = "struct TString"
        self.as_param = "struct TString"
        self.copy_func = "tstr_dup"
        self.drop_func = "tstr_drop"


class ArrayTypeABIInfo(AbstractAnalysis[ArrayType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        arg_ty_abi_info = TypeABIInfo.get(am, t.item_ty)
        self.decl_headers = ["core/array.hpp", *arg_ty_abi_info.decl_headers]
        self.defn_headers = ["core/array.hpp", *arg_ty_abi_info.decl_headers]
        self.as_field = f"TArray<{arg_ty_abi_info.as_field}>"
        self.as_param = f"TArray<{arg_ty_abi_info.as_field}>"
        self.copy_func = "tarr_dup"
        self.drop_func = "tarr_drop"


class VectorTypeABIInfo(AbstractAnalysis[VectorType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: VectorType) -> None:
        val_ty_abi_info = TypeABIInfo.get(am, t.val_ty)
        self.decl_headers = ["core/vector.hpp", *val_ty_abi_info.decl_headers]
        self.defn_headers = ["core/vector.hpp", *val_ty_abi_info.decl_headers]
        self.as_field = f"TVectorData<{val_ty_abi_info.as_field}>*"
        self.as_param = f"TVectorData<{val_ty_abi_info.as_field}>* const*"
        self.copy_func = "tvec_dup"
        self.drop_func = "tvec_drop"


class MapTypeABIInfo(AbstractAnalysis[MapType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        key_ty_abi_info = TypeABIInfo.get(am, t.key_ty)
        val_ty_abi_info = TypeABIInfo.get(am, t.val_ty)
        self.decl_headers = [
            "core/map.hpp",
            *key_ty_abi_info.decl_headers,
            *val_ty_abi_info.decl_headers,
        ]
        self.defn_headers = [
            "core/map.hpp",
            *key_ty_abi_info.decl_headers,
            *val_ty_abi_info.decl_headers,
        ]
        self.as_field = (
            f"TMapData<{key_ty_abi_info.as_field}, {val_ty_abi_info.as_field}>*"
        )
        self.as_param = (
            f"TMapData<{key_ty_abi_info.as_field}, {val_ty_abi_info.as_field}>* const*"
        )
        self.copy_func = "tmap_dup"
        self.drop_func = "tmap_drop"


class SetTypeABIInfo(AbstractAnalysis[SetType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: SetType) -> None:
        key_ty_abi_info = TypeABIInfo.get(am, t.key_ty)
        val_ty_abi_info = TypeABIInfo.get(am, BOOL)
        self.decl_headers = [
            "core/map.hpp",
            *key_ty_abi_info.decl_headers,
            *val_ty_abi_info.decl_headers,
        ]
        self.defn_headers = [
            "core/map.hpp",
            *key_ty_abi_info.decl_headers,
            *val_ty_abi_info.decl_headers,
        ]
        self.as_field = (
            f"TMapData<{key_ty_abi_info.as_field}, {val_ty_abi_info.as_field}>*"
        )
        self.as_param = (
            f"TMapData<{key_ty_abi_info.as_field}, {val_ty_abi_info.as_field}>* const*"
        )
        self.copy_func = "tmap_dup"
        self.drop_func = "tmap_drop"


class TypeABIInfo(TypeVisitor[AbstractTypeABIInfo]):
    def __init__(self, am: AnalysisManager):
        self.am = am

    @staticmethod
    def get(am: AnalysisManager, t: Type | None):
        assert t is not None
        return TypeABIInfo(am).handle_type(t)

    @override
    def visit_enum_type(self, t: EnumType) -> AbstractTypeABIInfo:
        return EnumTypeABIInfo.get(self.am, t)

    @override
    def visit_struct_type(self, t: StructType) -> AbstractTypeABIInfo:
        return StructTypeABIInfo.get(self.am, t)

    @override
    def visit_iface_type(self, t: IfaceType) -> AbstractTypeABIInfo:
        return IfaceTypeABIInfo.get(self.am, t)

    @override
    def visit_scalar_type(self, t: ScalarType) -> AbstractTypeABIInfo:
        return ScalarTypeABIInfo.get(self.am, t)

    @override
    def visit_special_type(self, t: SpecialType) -> AbstractTypeABIInfo:
        return SpecialTypeABIInfo.get(self.am, t)

    @override
    def visit_array_type(self, t: ArrayType) -> AbstractTypeABIInfo:
        return ArrayTypeABIInfo.get(self.am, t)

    @override
    def visit_vector_type(self, t: VectorType) -> AbstractTypeABIInfo:
        return VectorTypeABIInfo.get(self.am, t)

    @override
    def visit_map_type(self, t: MapType) -> AbstractTypeABIInfo:
        return MapTypeABIInfo.get(self.am, t)

    @override
    def visit_set_type(self, t: SetType) -> AbstractTypeABIInfo:
        return SetTypeABIInfo.get(self.am, t)


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
            self.gen_struct_files(struct, pkg_abi_target)
        for enum in pkg.enums:
            self.gen_enum_files(enum, pkg_abi_target)
        for iface in pkg.interfaces:
            self.gen_iface_files(iface, pkg_abi_target)
        for func in pkg.functions:
            self.gen_func(func, pkg_abi_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_abi_target: COutputBuffer,
    ):
        func_abi_info = GlobFuncDeclABIInfo.get(self.am, func)
        params = []
        for param in func.params:
            type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_abi_target.include(*type_abi_info.decl_headers)
            params.append(f"{type_abi_info.as_param} {param.name}")
        params_str = ", ".join(params)
        if return_ty_ref := func.return_ty_ref:
            type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
            pkg_abi_target.include(*type_abi_info.decl_headers)
            return_ty_name = type_abi_info.as_field
        else:
            return_ty_name = "void"
        pkg_abi_target.write(
            f"TH_EXPORT {return_ty_name} {func_abi_info.mangled_name}({params_str});\n"
        )

    def gen_struct_files(
        self,
        struct: StructDecl,
        pkg_abi_target: COutputBuffer,
    ):
        struct_abi_info = StructDeclABIInfo.get(self.am, struct)
        self.gen_struct_decl_file(struct, struct_abi_info)
        self.gen_struct_defn_file(struct, struct_abi_info)
        pkg_abi_target.include(struct_abi_info.defn_header)

    def gen_struct_decl_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructDeclABIInfo,
    ):
        struct_abi_decl_target = COutputBuffer.create(
            self.tm, f"include/{struct_abi_info.decl_header}", True
        )
        struct_abi_decl_target.write(f"struct {struct_abi_info.mangled_name};\n")

    def gen_struct_defn_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructDeclABIInfo,
    ):
        struct_abi_defn_target = COutputBuffer.create(
            self.tm, f"include/{struct_abi_info.defn_header}", True
        )
        struct_abi_defn_target.include("taihe/common.h")
        struct_abi_defn_target.include(struct_abi_info.decl_header)
        self.gen_struct_type_defn(struct, struct_abi_defn_target, struct_abi_info)
        self.gen_struct_copy_func(struct, struct_abi_defn_target, struct_abi_info)
        self.gen_struct_drop_func(struct, struct_abi_defn_target, struct_abi_info)

    def gen_struct_type_defn(
        self,
        struct: StructDecl,
        struct_abi_defn_target: COutputBuffer,
        struct_abi_info: StructDeclABIInfo,
    ):
        struct_abi_defn_target.write(f"struct {struct_abi_info.mangled_name} {{\n")
        for field in struct.fields:
            ty_info = TypeABIInfo.get(self.am, field.ty_ref.resolved_ty)
            struct_abi_defn_target.include(*ty_info.defn_headers)
            struct_abi_defn_target.write(f"  {ty_info.as_field} {field.name};\n")
        struct_abi_defn_target.write("};\n")

    def gen_struct_copy_func(
        self,
        struct: StructDecl,
        struct_abi_defn_target: COutputBuffer,
        struct_abi_info: StructDeclABIInfo,
    ):
        struct_abi_defn_target.write(
            f"TH_INLINE struct {struct_abi_info.mangled_name} {struct_abi_info.copy_func}(struct {struct_abi_info.mangled_name} data) {{\n"
            f"  struct {struct_abi_info.mangled_name} result;\n"
        )
        for field in struct.fields:
            ty_info = TypeABIInfo.get(self.am, field.ty_ref.resolved_ty)
            if ty_info.copy_func is not None:
                struct_abi_defn_target.write(
                    f"  result.{field.name} = {ty_info.copy_func}(data.{field.name});\n"
                )
            else:
                struct_abi_defn_target.write(
                    f"  result.{field.name} = data.{field.name};\n"
                )
        struct_abi_defn_target.write("  return result;\n" "}\n")

    def gen_struct_drop_func(
        self,
        struct: StructDecl,
        struct_abi_defn_target: COutputBuffer,
        struct_abi_info: StructDeclABIInfo,
    ):
        struct_abi_defn_target.write(
            f"TH_INLINE void {struct_abi_info.drop_func}(struct {struct_abi_info.mangled_name} data) {{\n"
        )
        for field in struct.fields:
            ty_info = TypeABIInfo.get(self.am, field.ty_ref.resolved_ty)
            if ty_info.drop_func is not None:
                struct_abi_defn_target.write(
                    f"  {ty_info.drop_func}(data.{field.name});\n"
                )
        struct_abi_defn_target.write("}\n")

    def gen_enum_files(
        self,
        enum: EnumDecl,
        pkg_abi_target: COutputBuffer,
    ):
        enum_abi_info = EnumDeclABIInfo.get(self.am, enum)
        self.gen_enum_decl_file(enum, enum_abi_info)
        self.gen_enum_defn_file(enum, enum_abi_info)
        pkg_abi_target.include(enum_abi_info.defn_header)

    def gen_enum_decl_file(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumDeclABIInfo,
    ):
        enum_abi_decl_target = COutputBuffer.create(
            self.tm, f"include/{enum_abi_info.decl_header}", True
        )
        enum_abi_decl_target.write(f"struct {enum_abi_info.mangled_name};\n")

    def gen_enum_defn_file(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumDeclABIInfo,
    ):
        enum_abi_defn_target = COutputBuffer.create(
            self.tm, f"include/{enum_abi_info.defn_header}", True
        )
        enum_abi_defn_target.include("taihe/common.h")
        enum_abi_defn_target.include(enum_abi_info.decl_header)
        self.gen_enum_union_defn(enum, enum_abi_defn_target, enum_abi_info)
        self.gen_enum_copy_func(enum, enum_abi_defn_target, enum_abi_info)
        self.gen_enum_drop_func(enum, enum_abi_defn_target, enum_abi_info)

    def gen_enum_union_defn(
        self,
        enum: EnumDecl,
        enum_abi_defn_target: COutputBuffer,
        enum_abi_info: EnumDeclABIInfo,
    ):
        enum_abi_defn_target.write(f"union {enum_abi_info.union_name} {{\n")
        for item in enum.items:
            if item.ty_ref is None:
                enum_abi_defn_target.write(f"  // {item.value}\n")
                continue
            ty_info = TypeABIInfo.get(self.am, item.ty_ref.resolved_ty)
            enum_abi_defn_target.include(*ty_info.defn_headers)
            enum_abi_defn_target.write(
                f"  {ty_info.as_field} {item.name}; // {item.value}\n"
            )
        enum_abi_defn_target.write(
            f"}};\n"
            f"struct {enum_abi_info.mangled_name} {{\n"
            f"  {enum_abi_info.tag_type} tag;\n"
            f"  union {enum_abi_info.union_name} data;\n"
            f"}};\n"
        )

    def gen_enum_copy_func(
        self,
        enum: EnumDecl,
        enum_abi_defn_target: COutputBuffer,
        enum_abi_info: EnumDeclABIInfo,
    ):
        enum_abi_defn_target.write(
            f"TH_INLINE struct {enum_abi_info.mangled_name} {enum_abi_info.copy_func}(struct {enum_abi_info.mangled_name} data) {{\n"
            f"  struct {enum_abi_info.mangled_name} result;\n"
            f"  switch (result.tag = data.tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            ty_info = TypeABIInfo.get(self.am, item.ty_ref.resolved_ty)
            if ty_info.copy_func is not None:
                enum_abi_defn_target.write(
                    f"  case {item.value}:\n"
                    f"    result.data.{item.name} = {ty_info.copy_func}(data.data.{item.name});\n"
                    f"    return result;\n"
                )
            else:
                enum_abi_defn_target.write(
                    f"  case {item.value}:\n"
                    f"    result.data.{item.name} = data.data.{item.name};\n"
                    f"    return result;\n"
                )
        enum_abi_defn_target.write("  default:\n" "    return result;\n" "  }\n" "}\n")

    def gen_enum_drop_func(
        self,
        enum: EnumDecl,
        enum_abi_defn_target: COutputBuffer,
        enum_abi_info: EnumDeclABIInfo,
    ):
        enum_abi_defn_target.write(
            f"TH_INLINE void {enum_abi_info.drop_func}(struct {enum_abi_info.mangled_name} data) {{\n"
            f"  switch (data.tag) {{\n"
        )
        for item in enum.items:
            if item.ty_ref is None:
                continue
            ty_info = TypeABIInfo.get(self.am, item.ty_ref.resolved_ty)
            if ty_info.copy_func is not None:
                enum_abi_defn_target.write(
                    f"  case {item.value}:\n"
                    f"    {ty_info.drop_func}(data.data.{item.name});\n"
                    f"    break;\n"
                )
        enum_abi_defn_target.write("  default:\n" "    break;\n" "  }\n" "}\n")

    def gen_iface_files(
        self,
        iface: IfaceDecl,
        pkg_abi_target: COutputBuffer,
    ):
        iface_abi_info = IfaceDeclABIInfo.get(self.am, iface)
        self.gen_iface_decl__file(iface, iface_abi_info)
        self.gen_iface_defn_file(iface, iface_abi_info)
        self.gen_iface_impl_file(iface, iface_abi_info)
        self.gen_iface_src_file(iface, iface_abi_info)
        pkg_abi_target.include(iface_abi_info.defn_header)

    def gen_iface_decl__file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_decl_target = COutputBuffer.create(
            self.tm, f"include/{iface_abi_info.decl_header}", True
        )
        iface_abi_decl_target.write(f"struct {iface_abi_info.mangled_name};\n")

    def gen_iface_defn_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_defn_target = COutputBuffer.create(
            self.tm, f"include/{iface_abi_info.defn_header}", True
        )
        iface_abi_defn_target.include("taihe/object.abi.h")
        iface_abi_defn_target.include(iface_abi_info.decl_header)
        iface_abi_defn_target.write(
            f"struct {iface_abi_info.ftable};\n"
            f"struct {iface_abi_info.vtable};\n"
            f"struct {iface_abi_info.mangled_name} {{\n"
            f"  struct {iface_abi_info.vtable} const* vtbl_ptr;\n"
            f"  struct DataBlockHead* data_ptr;\n"
            f"}};\n"
            f"TH_EXPORT void const* const {iface_abi_info.iid};\n"
        )
        self.gen_iface_ftable(iface, iface_abi_defn_target, iface_abi_info)
        self.gen_iface_vtable(iface, iface_abi_defn_target, iface_abi_info)
        self.gen_iface_static_cast_funcs(iface, iface_abi_defn_target, iface_abi_info)
        self.gen_iface_dynamic_cast_func(iface, iface_abi_defn_target, iface_abi_info)
        self.gen_iface_copy_func(iface, iface_abi_defn_target, iface_abi_info)
        self.gen_iface_drop_func(iface, iface_abi_defn_target, iface_abi_info)

    def gen_iface_ftable(
        self,
        iface: IfaceDecl,
        iface_abi_defn_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_defn_target.write(f"struct {iface_abi_info.ftable} {{\n")
        for method in iface.methods:
            params = [f"{iface_abi_info.as_param} tobj"]
            for param in method.params:
                type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
                iface_abi_defn_target.include(*type_abi_info.decl_headers)
                params.append(f"{type_abi_info.as_param} {param.name}")
            params_str = ", ".join(params)
            if return_ty_ref := method.return_ty_ref:
                type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
                iface_abi_defn_target.include(*type_abi_info.decl_headers)
                return_ty_name = type_abi_info.as_field
            else:
                return_ty_name = "void"
            iface_abi_defn_target.write(
                f"  {return_ty_name} (*{method.name})({params_str});\n"
            )
        iface_abi_defn_target.write("};\n")

    def gen_iface_vtable(
        self,
        iface: IfaceDecl,
        iface_abi_defn_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_defn_target.write(f"struct {iface_abi_info.vtable} {{\n")
        for ancestor_item_info in iface_abi_info.ancestor_list:
            ancestor_abi_info = IfaceDeclABIInfo.get(self.am, ancestor_item_info.iface)
            iface_abi_defn_target.write(
                f"  struct {ancestor_abi_info.ftable} const* {ancestor_item_info.ftbl_ptr};\n"
            )
        iface_abi_defn_target.write("};\n")

    def gen_iface_static_cast_funcs(
        self,
        iface: IfaceDecl,
        iface_abi_defn_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if ancestor is iface:
                continue
            ancestor_abi_info = IfaceDeclABIInfo.get(self.am, ancestor)
            iface_abi_defn_target.include(ancestor_abi_info.defn_header)
            iface_abi_defn_target.write(
                f"TH_INLINE struct {ancestor_abi_info.mangled_name} {info.static_cast}(struct {iface_abi_info.mangled_name} tobj) {{\n"
                f"  struct {ancestor_abi_info.mangled_name} result;\n"
                f"  result.vtbl_ptr = (struct {ancestor_abi_info.vtable} const*)((void* const*)tobj.vtbl_ptr + {info.offset});\n"
                f"  result.data_ptr = tobj.data_ptr;\n"
                f"  return result;\n"
                f"}}\n"
            )

    def gen_iface_dynamic_cast_func(
        self,
        iface: IfaceDecl,
        iface_abi_defn_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_defn_target.write(
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
        iface_abi_defn_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_defn_target.write(
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
        iface_abi_defn_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_defn_target.write(
            f"TH_INLINE void {iface_abi_info.drop_func}(struct {iface_abi_info.mangled_name} tobj) {{\n"
            f"  struct DataBlockHead* data_ptr = tobj.data_ptr;\n"
            f"  if (data_ptr && tref_dec(&data_ptr->m_count)) {{\n"
            f"    data_ptr->rtti_ptr->free(data_ptr);\n"
            f"  }}\n"
            f"}}\n"
        )

    def gen_iface_impl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        iface_abi_impl_target = COutputBuffer.create(
            self.tm, f"include/{iface_abi_info.impl_header}", True
        )
        iface_abi_impl_target.include(iface_abi_info.defn_header)
        self.gen_iface_methods(iface, iface_abi_impl_target, iface_abi_info)

    def gen_iface_methods(
        self,
        iface: IfaceDecl,
        iface_abi_impl_target: COutputBuffer,
        iface_abi_info: IfaceDeclABIInfo,
    ):
        for method in iface.methods:
            method_abi_info = IfaceMethodDeclABIInfo.get(self.am, method)
            params = [f"{iface_abi_info.as_param} tobj"]
            args = ["tobj"]
            for param in method.params:
                type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
                iface_abi_impl_target.include(*type_abi_info.defn_headers)
                params.append(f"{type_abi_info.as_param} {param.name}")
                args.append(param.name)
            params_str = ", ".join(params)
            args_str = ", ".join(args)
            if return_ty_ref := method.return_ty_ref:
                type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
                iface_abi_impl_target.include(*type_abi_info.defn_headers)
                return_ty_name = type_abi_info.as_field
            else:
                return_ty_name = "void"
            iface_abi_impl_target.write(
                f"TH_INLINE {return_ty_name} {method_abi_info.mangled_name}({params_str}) {{\n"
                f"  return tobj.vtbl_ptr->{iface_abi_info.ancestor_dict[iface].ftbl_ptr}->{method.name}({args_str});\n"
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
        abi_iface_src_target.include(iface_abi_info.defn_header)
        abi_iface_src_target.write(
            f"void const* const {iface_abi_info.iid} = &{iface_abi_info.iid};\n"
        )
