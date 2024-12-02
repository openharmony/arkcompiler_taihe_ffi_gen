from io import StringIO
from os import PathLike, makedirs, path
from pathlib import Path
from typing import Any

from typing_extensions import override

from taihe.codegen.mangle import DeclKind, encode
from taihe.semantics.declarations import (
    EnumDecl,
    EnumItemDecl,
    FuncBaseDecl,
    FuncDecl,
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
    ScalarType,
    SpecialType,
    TypeAlike,
)
from taihe.semantics.visitor import DeclVisitor, TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputBase, OutputManager


class COutputBuffer(OutputBase):
    """Represents a C or C++ target file."""

    def __init__(self, filename: str):
        super().__init__(filename)
        self.headers: set[str] = set()
        self.code = StringIO()

    @override
    def output_to(self, dst_dir: PathLike):
        dst_path = Path(dst_dir) / self.filename
        if not path.exists(dst_path.parent):
            makedirs(dst_path.parent, exist_ok=True)
        with open(dst_path, "w", encoding="utf-8") as dst:
            if self.filename.endswith((".h", ".hpp")):
                dst.write(f"#pragma once\n")
            for header in self.headers:
                dst.write(f'#include "{header}"\n')
            dst.write(self.code.getvalue())

    @override
    def show(self):
        print(f"// {self.filename}")
        if self.filename.endswith((".h", ".hpp")):
            print(f"#pragma once")
        for header in self.headers:
            print(f"#include <{header}>")
        print(self.code.getvalue())

    def write(self, code: str):
        self.code.write(code)

    def include(self, *headers: str | None):
        for header in headers:
            if isinstance(header, str):
                self.headers.add(header)


class ABIPackageInfo(AbstractAnalysis):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.abi.h"


class ABIFuncDeclInfo(AbstractAnalysis):
    def __init__(self, am: AnalysisManager, f: FuncDecl) -> None:
        p = f.parent
        assert p
        segments = [*p.name.split("."), f.name]
        self.name = encode(segments, DeclKind.FUNCTION)


class ABIIfaceMethodDeclInfo(AbstractAnalysis):
    def __init__(self, am: AnalysisManager, m: IfaceMethodDecl) -> None:
        i = m.parent
        assert i
        p = i.parent
        assert p
        segments = [*p.name.split("."), i.name, m.name]
        self.name = encode(segments, DeclKind.FUNCTION)


class ABIFuncReturnTypeInfo(AbstractAnalysis):
    def __init__(self, am: AnalysisManager, f: FuncBaseDecl) -> None:
        if len(f.return_types) == 0:
            self.header = None
            self.name = "void"
        elif len(f.return_types) == 1:
            info = ABINormalTypeRefDeclInfo.get(am, f.return_types[0])
            self.header = info.header
            self.name = info.name


class ABIEnumItemDeclInfo(AbstractAnalysis):
    def __init__(self, am: AnalysisManager, d: EnumItemDecl) -> None:
        e = d.parent
        assert e
        p = e.parent
        assert p
        segments = [*p.name.split("."), e.name, d.name]
        self.name = encode(segments, DeclKind.ENUM_ITEM)


class ABIEnumDeclInfo(AbstractAnalysis):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.parent
        assert p
        segments = [*p.name.split("."), d.name]
        self.header = f"{p.name}.{d.name}.abi.h"
        self.name = encode(segments, DeclKind.ENUM)


class ABIStructDeclInfo(AbstractAnalysis):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.parent
        assert p
        segments = [*p.name.split("."), d.name]
        self.header = f"{p.name}.{d.name}.abi.h"
        self.name = encode(segments, DeclKind.STRUCT)
        self.copy_name = encode(segments, DeclKind.COPY)
        self.drop_name = encode(segments, DeclKind.DROP)


class ABIIfaceDeclInfo(AbstractAnalysis):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.parent
        assert p
        segments = [*p.name.split("."), d.name]
        self.header_0 = f"{p.name}.{d.name}.abi.0.h"
        self.header_1 = f"{p.name}.{d.name}.abi.1.h"
        self.src = f"{p.name}.{d.name}.c"
        self.name = encode(segments, DeclKind.INTERFACE)
        self.copy_name = encode(segments, DeclKind.COPY)
        self.drop_name = encode(segments, DeclKind.DROP)
        self.f_table = encode(segments, DeclKind.FTABLE)
        self.v_table = encode(segments, DeclKind.VTABLE)
        self.iid = encode(segments, DeclKind.IID)
        self.ancestors = [d]
        for extend in d.parents:
            iface = extend.ref_ty
            assert isinstance(iface, IfaceDecl)
            abi_extend_info = ABIIfaceDeclInfo.get(am, iface)
            self.ancestors.extend(abi_extend_info.ancestors)
        self.offsets: dict[IfaceDecl, int] = {}
        for i, ancestor in enumerate(self.ancestors):
            self.offsets.setdefault(ancestor, i)


class ABINormalTypeRefDeclInfo(AbstractAnalysis, TypeVisitor):
    def __init__(self, am: AnalysisManager, t: TypeAlike) -> None:
        self.am = am
        self.header = None
        self.name = None
        self.copy_func = lambda a: a
        self.drop_func = lambda _: None
        self.handle_type(t)

    @override
    def visit_enum_decl(self, d: EnumDecl) -> Any:
        abi_enum_info = ABIEnumDeclInfo.get(self.am, d)
        self.header = abi_enum_info.header
        self.name = f"enum {abi_enum_info.name}"

    @override
    def visit_struct_decl(self, d: StructDecl) -> Any:
        abi_struct_info = ABIStructDeclInfo.get(self.am, d)
        self.header = abi_struct_info.header
        self.name = f"struct {abi_struct_info.name}"
        self.copy_func = lambda a: f"{abi_struct_info.copy_name}({a})"
        self.drop_func = lambda a: f"{abi_struct_info.drop_name}({a})"

    @override
    def visit_iface_decl(self, d: IfaceDecl) -> Any:
        abi_iface_info = ABIIfaceDeclInfo.get(self.am, d)
        self.header = abi_iface_info.header_0
        self.name = f"struct {abi_iface_info.name}"
        self.copy_func = lambda a: f"{abi_iface_info.copy_name}({a})"
        self.drop_func = lambda a: f"{abi_iface_info.drop_name}({a})"

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
            self.header = "taihe/string.abi.h"
            self.name = "struct TString*"
            self.copy_func = lambda a: f"tstr_dup({a})"
            self.copy_func = lambda a: f"tstr_drop({a})"
        else:
            raise ValueError


class ABIParamTypeRefDeclInfo(ABINormalTypeRefDeclInfo):
    @override
    def visit_struct_decl(self, d: StructDecl) -> Any:
        abi_struct_info = ABIStructDeclInfo.get(self.am, d)
        self.header = abi_struct_info.header
        self.name = f"struct {abi_struct_info.name} const*"


class ABICodeGenerator(DeclVisitor):
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self._current_package_group = None
        self._current_package = None
        self._current_abi_target = None
        self.tm = tm
        self.am = am

    @property
    def _pkg(self) -> Package:
        assert self._current_package
        return self._current_package

    @property
    def _pkg_group(self) -> PackageGroup:
        assert self._current_package_group
        return self._current_package_group

    @override
    def visit_package_group(self, g: PackageGroup):
        self._current_package_group = g
        super().visit_package_group(g)
        self._current_package_group = None

    @property
    def _abi_target(self) -> COutputBuffer:
        assert self._current_abi_target
        return self._current_abi_target

    @override
    def visit_package(self, p: Package):
        abi_pkg_info = ABIPackageInfo.get(self.am, p)
        self._current_abi_target = COutputBuffer(f"include/{abi_pkg_info.header}")
        self.tm.add(self._current_abi_target)

        self._current_abi_target.include("taihe/common.h")

        self._current_package = p
        super().visit_package(p)
        self._current_package = None

        self._current_abi_target = None

    @override
    def visit_func_decl(self, d: FuncDecl) -> Any:
        abi_func_info = ABIFuncDeclInfo.get(self.am, d)
        abi_return_t_info = ABIFuncReturnTypeInfo.get(self.am, d)

        params = []
        for param in d.params:
            abi_param_type_info = ABIParamTypeRefDeclInfo.get(self.am, param.ty)
            self._abi_target.include(abi_param_type_info.header)
            params.append(f"{abi_param_type_info.name} {param.name}")
        params_str = ", ".join(params)
        self._abi_target.write(
            f"TH_EXPORT {abi_return_t_info.name} {abi_func_info.name}({params_str});\n"
        )

    @override
    def visit_enum_decl(self, d: EnumDecl) -> Any:
        abi_enum_info = ABIEnumDeclInfo.get(self.am, d)

        abi_enum_target = COutputBuffer(f"include/{abi_enum_info.header}")
        self.tm.add(abi_enum_target)

        abi_enum_target.include("taihe/common.h")

        abi_enum_target.write(f"enum {abi_enum_info.name} {{\n")
        for item in d.items:
            abi_enum_item_info = ABIEnumItemDeclInfo.get(self.am, item)
            abi_enum_target.write(f"  {abi_enum_item_info.name} = {item.value},\n")
        abi_enum_target.write("};\n")

        self._abi_target.include(abi_enum_info.header)

    @override
    def visit_struct_decl(self, d: StructDecl) -> Any:
        abi_struct_info = ABIStructDeclInfo.get(self.am, d)

        abi_struct_target = COutputBuffer(f"include/{abi_struct_info.header}")
        self.tm.add(abi_struct_target)

        abi_struct_target.include("taihe/common.h")

        abi_struct_target.write(f"struct {abi_struct_info.name} {{\n")
        for field in d.fields:
            ty_info = ABINormalTypeRefDeclInfo.get(self.am, field.ty)
            abi_struct_target.include(ty_info.header)
            abi_struct_target.write(f"  {ty_info.name} {field.name};\n")
        abi_struct_target.write("};\n")

        abi_struct_target.write(
            f"inline struct {abi_struct_info.name} {abi_struct_info.copy_name}(struct {abi_struct_info.name} data) {{\n"
            f"  struct {abi_struct_info.name} result = {{\n"
        )
        for field in d.fields:
            ty_info = ABINormalTypeRefDeclInfo.get(self.am, field.ty)
            abi_struct_target.include(ty_info.header)
            copied = ty_info.copy_func(f"data.{field.name}")
            abi_struct_target.write(f"    {copied},\n")
        abi_struct_target.write("  };\n" "  return result;\n" "}\n")

        abi_struct_target.write(
            f"inline void {abi_struct_info.drop_name}(struct {abi_struct_info.name} data) {{\n"
        )
        for field in d.fields:
            ty_info = ABINormalTypeRefDeclInfo.get(self.am, field.ty)
            abi_struct_target.include(ty_info.header)
            dropping = ty_info.drop_func(f"data.{field.name}")
            if dropping:
                abi_struct_target.write(f"  {dropping};\n")
        abi_struct_target.write("}\n")

        self._abi_target.include(abi_struct_info.header)

    @override
    def visit_iface_decl(self, d: IfaceDecl) -> Any:
        abi_iface_info = ABIIfaceDeclInfo.get(self.am, d)

        abi_iface_target_0 = COutputBuffer(f"include/{abi_iface_info.header_0}")
        self.tm.add(abi_iface_target_0)

        abi_iface_target_0.include("taihe/object.abi.h")

        abi_iface_target_0.write(
            f"struct {abi_iface_info.f_table};\n"
            f"struct {abi_iface_info.v_table};\n"
            f"struct {abi_iface_info.name} {{\n"
            f"  struct {abi_iface_info.v_table}* vtbl_ptr;\n"
            f"  struct DataBlockHead* data_ptr;\n"
            f"}};\n"
        )

        abi_iface_target_1 = COutputBuffer(f"include/{abi_iface_info.header_1}")
        self.tm.add(abi_iface_target_1)

        abi_iface_target_1.include(abi_iface_info.header_0)

        abi_iface_target_1.write(f"TH_EXPORT void const* const {abi_iface_info.iid};\n")

        abi_iface_target_1.write(f"struct {abi_iface_info.f_table} {{\n")
        for method in d.methods:
            abi_return_t_info = ABIFuncReturnTypeInfo.get(self.am, method)

            params = ["struct DataBlockHead* data_ptr"]
            for param in method.params:
                abi_param_type_info = ABIParamTypeRefDeclInfo.get(self.am, param.ty)
                abi_iface_target_1.include(abi_param_type_info.header)
                params.append(f"{abi_param_type_info.name} {param.name}")
            params_str = ", ".join(params)
            abi_iface_target_1.write(
                f"  {abi_return_t_info.name} (*{method.name})({params_str});\n"
            )
        abi_iface_target_1.write("};\n")

        abi_iface_target_1.write(f"struct {abi_iface_info.v_table} {{\n")
        for i, ancestor in enumerate(abi_iface_info.ancestors):
            abi_ancestor_info = ABIIfaceDeclInfo.get(self.am, ancestor)
            abi_iface_target_1.write(
                f"  struct {abi_ancestor_info.f_table}* ftbl_ptr_{i};\n"
            )
        abi_iface_target_1.write("};\n")

        for method in d.methods:
            abi_method_info = ABIIfaceMethodDeclInfo.get(self.am, method)
            abi_return_t_info = ABIFuncReturnTypeInfo.get(self.am, method)

            params = [f"struct {abi_iface_info.name} tobj"]
            args = ["tobj.data_ptr"]
            for param in method.params:
                abi_param_type_info = ABIParamTypeRefDeclInfo.get(self.am, param.ty)
                params.append(f"{abi_param_type_info.name} {param.name}")
                args.append(param.name)
            params_str = ", ".join(params)
            args_str = ", ".join(args)
            abi_iface_target_1.write(
                f"inline {abi_return_t_info.name} {abi_method_info.name}({params_str}) {{\n"
                f"  return tobj.vtbl_ptr->ftbl_ptr_0->{method.name}({args_str});\n"
                f"}}\n"
            )

        for ancestor, i in abi_iface_info.offsets.items():
            if i == 0:
                continue
            abi_ancestor_info = ABIIfaceDeclInfo.get(self.am, ancestor)
            abi_iface_target_1.include(abi_ancestor_info.header_0)
            abi_iface_target_1.write(
                f"inline struct {abi_ancestor_info.name} convert_{abi_iface_info.name}_to_{abi_ancestor_info.name}(struct {abi_iface_info.name} tobj) {{\n"
                f"  struct {abi_ancestor_info.name} result = {{\n"
                f"     (struct {abi_ancestor_info.v_table}*)(&tobj.vtbl_ptr->ftbl_ptr_0 + {i}),\n"
                f"     tobj.data_ptr,\n"
                f"  }};\n"
                f"  return result;\n"
                f"}}\n"
            )

        abi_iface_target_1.write(
            f"inline struct {abi_iface_info.name} dynamic_cast_to_{abi_iface_info.name}(struct DataBlockHead* data_ptr) {{\n"
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

        abi_iface_target_1.write(
            f"inline struct {abi_iface_info.name} {abi_iface_info.copy_name}(struct {abi_iface_info.name} tobj) {{\n"
            f"  struct DataBlockHead* data_ptr = tobj.data_ptr;\n"
            f"  if (data_ptr) {{\n"
            f"    tref_inc(&data_ptr->m_count);\n"
            f"  }}\n"
            f"  return tobj;\n"
            f"}}\n"
        )

        abi_iface_target_1.write(
            f"inline void {abi_iface_info.drop_name}(struct {abi_iface_info.name} tobj) {{\n"
            f"  struct DataBlockHead* data_ptr = tobj.data_ptr;\n"
            f"  if (data_ptr && tref_dec(&data_ptr->m_count)) {{\n"
            f"    data_ptr->rtti_ptr->free_data(data_ptr);\n"
            f"  }}\n"
            f"}}\n"
        )

        abi_iface_src = COutputBuffer(f"src/{abi_iface_info.src}")
        self.tm.add(abi_iface_src)

        abi_iface_src.include(abi_iface_info.header_1)

        abi_iface_src.write(
            f"void const* const {abi_iface_info.iid} = &{abi_iface_info.iid};\n"
        )

        self._abi_target.include(abi_iface_info.header_1)
