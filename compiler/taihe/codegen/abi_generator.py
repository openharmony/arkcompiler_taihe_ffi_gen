from abc import ABCMeta
from dataclasses import dataclass

from typing_extensions import override

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
    U8,
    U16,
    U32,
    U64,
    ArrayType,
    BoxType,
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
from taihe.utils.outputs import COutputBuffer, OutputManager


class PackageABIInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        self.header = f"{p.name}.abi.hpp"


class GlobFuncABIInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        p = f.node_parent
        assert p
        segments = [*p.segments, f.name]
        self.mangled_name = encode(segments, DeclKind.FUNC)


class IfaceMethodABIInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, f: IfaceMethodDecl) -> None:
        d = f.node_parent
        assert d
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name, f.name]
        self.mangled_name = encode(segments, DeclKind.FUNC)


class EnumABIInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name]
        self.decl_header = f"{p.name}.{d.name}.abi.0.hpp"
        self.defn_header = f"{p.name}.{d.name}.abi.1.hpp"
        self.tag_type = "size_t"
        self.union_name = encode(segments, DeclKind.UNION)
        self.mangled_name = encode(segments, DeclKind.TYPE)
        self.as_owner = f"struct {self.mangled_name}"
        self.as_param = f"struct {self.mangled_name} const*"
        self.has_data = any(item.ty_ref for item in d.items)


class StructABIInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name]
        self.decl_header = f"{p.name}.{d.name}.abi.0.hpp"
        self.defn_header = f"{p.name}.{d.name}.abi.1.hpp"
        self.mangled_name = encode(segments, DeclKind.TYPE)
        self.as_owner = f"struct {self.mangled_name}"
        self.as_param = f"struct {self.mangled_name} const*"


@dataclass
class AncestorItemInfo:
    iface: IfaceDecl
    ftbl_ptr: str


@dataclass
class UniqueAncestorInfo:
    offset: int
    static_cast: str
    ftbl_ptr: str


class IfaceABIInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name]
        self.decl_header = f"{p.name}.{d.name}.abi.0.hpp"
        self.defn_header = f"{p.name}.{d.name}.abi.1.hpp"
        self.impl_header = f"{p.name}.{d.name}.abi.2.hpp"
        self.src = f"{p.name}.{d.name}.cpp"
        self.mangled_name = encode(segments, DeclKind.TYPE)
        self.as_owner = f"struct {self.mangled_name}"
        self.as_param = f"struct {self.mangled_name}"
        self.copy_func = encode(segments, DeclKind.COPY)
        self.drop_func = encode(segments, DeclKind.DROP)
        self.ftable = encode(segments, DeclKind.FTABLE)
        self.vtable = encode(segments, DeclKind.VTABLE)
        self.iid = encode(segments, DeclKind.IID)
        self.dynamic_cast = encode(segments, DeclKind.DYNAMIC_CAST)
        self.ancestor_list: list[AncestorItemInfo] = []
        self.ancestor_dict: dict[IfaceDecl, UniqueAncestorInfo] = {}
        self.ancestors = [d]
        for extend in d.parents:
            ty = extend.ty_ref.resolved_ty
            assert isinstance(ty, IfaceType)
            extend_abi_info = IfaceABIInfo.get(am, ty.ty_decl)
            self.ancestors.extend(extend_abi_info.ancestors)
        for i, ancestor in enumerate(self.ancestors):
            ftbl_ptr = f"ftbl_ptr_{i}"
            self.ancestor_list.append(
                AncestorItemInfo(
                    iface=ancestor,
                    ftbl_ptr=ftbl_ptr,
                )
            )
            self.ancestor_dict.setdefault(
                ancestor,
                UniqueAncestorInfo(
                    offset=i,
                    static_cast=encode([*segments, str(i)], DeclKind.STATIC_CAST),
                    ftbl_ptr=ftbl_ptr,
                ),
            )


class AbstractTypeABIInfo(metaclass=ABCMeta):
    decl_headers: list[str]
    defn_headers: list[str]
    # type as struct field / union field / return value
    as_owner: str
    # type as parameter
    as_param: str


class EnumTypeABIInfo(AbstractAnalysis[EnumType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        enum_abi_info = EnumABIInfo.get(am, t.ty_decl)
        self.decl_headers = [enum_abi_info.decl_header]
        self.defn_headers = [enum_abi_info.defn_header]
        self.as_owner = enum_abi_info.as_owner
        self.as_param = enum_abi_info.as_param


class StructTypeABIInfo(AbstractAnalysis[StructType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: StructType) -> None:
        struct_abi_info = StructABIInfo.get(am, t.ty_decl)
        self.decl_headers = [struct_abi_info.decl_header]
        self.defn_headers = [struct_abi_info.defn_header]
        self.as_owner = struct_abi_info.as_owner
        self.as_param = struct_abi_info.as_param


class IfaceTypeABIInfo(AbstractAnalysis[IfaceType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType) -> None:
        iface_abi_info = IfaceABIInfo.get(am, t.ty_decl)
        self.decl_headers = [iface_abi_info.decl_header]
        self.defn_headers = [iface_abi_info.defn_header]
        self.as_owner = iface_abi_info.as_owner
        self.as_param = iface_abi_info.as_param


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
        self.as_owner = res


class StringTypeABIInfo(AbstractAnalysis[StringType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: StringType) -> None:
        self.decl_headers = ["taihe/string.abi.h"]
        self.defn_headers = ["taihe/string.abi.h"]
        self.as_owner = "struct TString"
        self.as_param = "struct TString"


class ArrayTypeABIInfo(AbstractAnalysis[ArrayType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        self.decl_headers = ["taihe/array.abi.h"]
        self.defn_headers = ["taihe/array.abi.h"]
        self.as_owner = "struct TArray"
        self.as_param = "struct TArray"


class BoxTypeABIInfo(AbstractAnalysis[BoxType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: BoxType) -> None:
        self.decl_headers = ["taihe/box.abi.h"]
        self.defn_headers = ["taihe/box.abi.h"]
        self.as_owner = "struct TBox"
        self.as_param = "struct TBox"


class CallbackTypeABIInfo(AbstractAnalysis[CallbackType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: CallbackType) -> None:
        self.decl_headers = []
        self.defn_headers = []
        self.as_owner = "void*"
        self.as_param = "void*"


class VectorTypeABIInfo(AbstractAnalysis[VectorType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: VectorType) -> None:
        self.decl_headers = []
        self.defn_headers = []
        self.as_owner = "void*"
        self.as_param = "void*"


class MapTypeABIInfo(AbstractAnalysis[MapType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        self.decl_headers = []
        self.defn_headers = []
        self.as_owner = "void*"
        self.as_param = "void*"


class SetTypeABIInfo(AbstractAnalysis[SetType], AbstractTypeABIInfo):
    def __init__(self, am: AnalysisManager, t: SetType) -> None:
        self.decl_headers = []
        self.defn_headers = []
        self.as_owner = "void*"
        self.as_param = "void*"


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
    def visit_string_type(self, t: StringType) -> AbstractTypeABIInfo:
        return StringTypeABIInfo.get(self.am, t)

    @override
    def visit_array_type(self, t: ArrayType) -> AbstractTypeABIInfo:
        return ArrayTypeABIInfo.get(self.am, t)

    @override
    def visit_vector_type(self, t: VectorType) -> AbstractTypeABIInfo:
        return VectorTypeABIInfo.get(self.am, t)

    @override
    def visit_box_type(self, t: BoxType) -> AbstractTypeABIInfo:
        return BoxTypeABIInfo.get(self.am, t)

    @override
    def visit_map_type(self, t: MapType) -> AbstractTypeABIInfo:
        return MapTypeABIInfo.get(self.am, t)

    @override
    def visit_set_type(self, t: SetType) -> AbstractTypeABIInfo:
        return SetTypeABIInfo.get(self.am, t)

    @override
    def visit_callback_type(self, t: CallbackType) -> AbstractTypeABIInfo:
        return CallbackTypeABIInfo.get(self.am, t)


class ABICodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
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
        func_abi_info = GlobFuncABIInfo.get(self.am, func)
        params = []
        for param in func.params:
            type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_abi_target.include(*type_abi_info.decl_headers)
            params.append(f"{type_abi_info.as_param} {param.name}")
        params_str = ", ".join(params)
        if return_ty_ref := func.return_ty_ref:
            type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
            pkg_abi_target.include(*type_abi_info.decl_headers)
            return_ty_name = type_abi_info.as_owner
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
        struct_abi_info = StructABIInfo.get(self.am, struct)
        self.gen_struct_decl_file(struct, struct_abi_info)
        self.gen_struct_defn_file(struct, struct_abi_info)
        pkg_abi_target.include(struct_abi_info.defn_header)

    def gen_struct_decl_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
    ):
        struct_abi_decl_target = COutputBuffer.create(
            self.tm, f"include/{struct_abi_info.decl_header}", True
        )
        struct_abi_decl_target.write(f"struct {struct_abi_info.mangled_name};\n")

    def gen_struct_defn_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
    ):
        struct_abi_defn_target = COutputBuffer.create(
            self.tm, f"include/{struct_abi_info.defn_header}", True
        )
        struct_abi_defn_target.include("taihe/common.h")
        struct_abi_defn_target.include(struct_abi_info.decl_header)
        self.gen_struct_defn(struct, struct_abi_info, struct_abi_defn_target)

    def gen_struct_defn(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
        struct_abi_defn_target: COutputBuffer,
    ):
        struct_abi_defn_target.write(f"struct {struct_abi_info.mangled_name} {{\n")
        for field in struct.fields:
            type_abi_info = TypeABIInfo.get(self.am, field.ty_ref.resolved_ty)
            struct_abi_defn_target.include(*type_abi_info.defn_headers)
            struct_abi_defn_target.write(f"  {type_abi_info.as_owner} {field.name};\n")
        struct_abi_defn_target.write("};\n")

    def gen_enum_files(
        self,
        enum: EnumDecl,
        pkg_abi_target: COutputBuffer,
    ):
        enum_abi_info = EnumABIInfo.get(self.am, enum)
        self.gen_enum_decl_file(enum, enum_abi_info)
        self.gen_enum_defn_file(enum, enum_abi_info)
        pkg_abi_target.include(enum_abi_info.defn_header)

    def gen_enum_decl_file(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumABIInfo,
    ):
        enum_abi_decl_target = COutputBuffer.create(
            self.tm, f"include/{enum_abi_info.decl_header}", True
        )
        enum_abi_decl_target.write(f"struct {enum_abi_info.mangled_name};\n")

    def gen_enum_defn_file(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumABIInfo,
    ):
        enum_abi_defn_target = COutputBuffer.create(
            self.tm, f"include/{enum_abi_info.defn_header}", True
        )
        enum_abi_defn_target.include("taihe/common.h")
        enum_abi_defn_target.include(enum_abi_info.decl_header)
        self.gen_enum_defn(enum, enum_abi_info, enum_abi_defn_target)

    def gen_enum_defn(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumABIInfo,
        enum_abi_defn_target: COutputBuffer,
    ):
        enum_abi_defn_target.write(f"union {enum_abi_info.union_name} {{\n")
        for item in enum.items:
            if item.ty_ref is None:
                enum_abi_defn_target.write(f"  // {item.value}\n")
                continue
            type_abi_info = TypeABIInfo.get(self.am, item.ty_ref.resolved_ty)
            enum_abi_defn_target.include(*type_abi_info.defn_headers)
            enum_abi_defn_target.write(
                f"  {type_abi_info.as_owner} {item.name}; // {item.value}\n"
            )
        enum_abi_defn_target.write(
            f"}};\n"
            f"struct {enum_abi_info.mangled_name} {{\n"
            f"  {enum_abi_info.tag_type} m_tag;\n"
            f"  union {enum_abi_info.union_name} m_data;\n"
            f"}};\n"
        )

    def gen_iface_files(
        self,
        iface: IfaceDecl,
        pkg_abi_target: COutputBuffer,
    ):
        iface_abi_info = IfaceABIInfo.get(self.am, iface)
        self.gen_iface_decl_file(iface, iface_abi_info)
        self.gen_iface_defn_file(iface, iface_abi_info)
        self.gen_iface_impl_file(iface, iface_abi_info)
        self.gen_iface_src_file(iface, iface_abi_info)
        pkg_abi_target.include(iface_abi_info.defn_header)

    def gen_iface_decl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
    ):
        iface_abi_decl_target = COutputBuffer.create(
            self.tm, f"include/{iface_abi_info.decl_header}", True
        )
        iface_abi_decl_target.write(f"struct {iface_abi_info.mangled_name};\n")

    def gen_iface_defn_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
    ):
        iface_abi_defn_target = COutputBuffer.create(
            self.tm, f"include/{iface_abi_info.defn_header}", True
        )
        iface_abi_defn_target.include("taihe/object.abi.h")
        iface_abi_defn_target.include(iface_abi_info.decl_header)
        iface_abi_defn_target.write(
            f"TH_EXPORT void const* const {iface_abi_info.iid};\n"
        )
        self.gen_iface_ftable(iface, iface_abi_info, iface_abi_defn_target)
        self.gen_iface_vtable(iface, iface_abi_info, iface_abi_defn_target)
        self.gen_iface_defn(iface, iface_abi_info, iface_abi_defn_target)
        self.gen_iface_static_cast_funcs(iface, iface_abi_info, iface_abi_defn_target)
        self.gen_iface_dynamic_cast_func(iface, iface_abi_info, iface_abi_defn_target)
        self.gen_iface_copy_func(iface, iface_abi_info, iface_abi_defn_target)
        self.gen_iface_drop_func(iface, iface_abi_info, iface_abi_defn_target)

    def gen_iface_ftable(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: COutputBuffer,
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
                return_ty_name = type_abi_info.as_owner
            else:
                return_ty_name = "void"
            iface_abi_defn_target.write(
                f"  {return_ty_name} (*{method.name})({params_str});\n"
            )
        iface_abi_defn_target.write("};\n")

    def gen_iface_vtable(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: COutputBuffer,
    ):
        iface_abi_defn_target.write(f"struct {iface_abi_info.vtable} {{\n")
        for ancestor_item_info in iface_abi_info.ancestor_list:
            ancestor_abi_info = IfaceABIInfo.get(self.am, ancestor_item_info.iface)
            iface_abi_defn_target.write(
                f"  struct {ancestor_abi_info.ftable} const* {ancestor_item_info.ftbl_ptr};\n"
            )
        iface_abi_defn_target.write("};\n")

    def gen_iface_defn(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: COutputBuffer,
    ):
        iface_abi_defn_target.write(
            f"struct {iface_abi_info.mangled_name} {{\n"
            f"  struct {iface_abi_info.vtable} const* vtbl_ptr;\n"
            f"  struct DataBlockHead* data_ptr;\n"
            f"}};\n"
        )

    def gen_iface_static_cast_funcs(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: COutputBuffer,
    ):
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if ancestor is iface:
                continue
            ancestor_abi_info = IfaceABIInfo.get(self.am, ancestor)
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
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: COutputBuffer,
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
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: COutputBuffer,
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
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: COutputBuffer,
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
        iface_abi_info: IfaceABIInfo,
    ):
        iface_abi_impl_target = COutputBuffer.create(
            self.tm, f"include/{iface_abi_info.impl_header}", True
        )
        iface_abi_impl_target.include(iface_abi_info.defn_header)
        self.gen_iface_methods(iface, iface_abi_info, iface_abi_impl_target)

    def gen_iface_methods(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_impl_target: COutputBuffer,
    ):
        for method in iface.methods:
            method_abi_info = IfaceMethodABIInfo.get(self.am, method)
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
                return_ty_name = type_abi_info.as_owner
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
        iface_abi_info: IfaceABIInfo,
    ):
        abi_iface_src_target = COutputBuffer.create(
            self.tm, f"src/{iface_abi_info.src}", False
        )
        abi_iface_src_target.include(iface_abi_info.defn_header)
        abi_iface_src_target.write(
            f"void const* const {iface_abi_info.iid} = &{iface_abi_info.iid};\n"
        )
