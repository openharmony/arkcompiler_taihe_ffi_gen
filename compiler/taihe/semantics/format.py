"""Format the IDL files."""

from typing import Optional, TextIO

from typing_extensions import override

from taihe.semantics.declarations import (
    Decl,
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    EnumItemDecl,
    FuncBaseDecl,
    IfaceDecl,
    IfaceParentDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
    PackageRefDecl,
    ParamDecl,
    RetvalDecl,
    StructDecl,
    StructFieldDecl,
    TypeAliasDecl,
    TypeDecl,
    TypeRefDecl,
)
from taihe.semantics.types import (
    BuiltinType,
    Type,
)
from taihe.semantics.visitor import DeclVisitor, TypeVisitor


def pretty_print(x: Decl, buffer: TextIO):
    printer = _PrettyPrinter(buffer)
    printer.handle_decl(x)


class _TypeNamePrinter(TypeVisitor[str]):
    @override
    def visit_type_decl(self, d: TypeDecl):
        return f"{pkg.name}.{d.name}" if (pkg := d.parent) else d.name

    @override
    def visit_builtin_type(self, t: BuiltinType):
        return t.name


class _PrettyPrinter(DeclVisitor):
    def __init__(self, buffer: TextIO):
        self.buffer = buffer
        self.indent = 0
        self.type_name_printer = _TypeNamePrinter()

    def get_type_ref_decl(self, d: TypeRefDecl) -> str:
        if d.is_resolved:
            return f"{d.symbol} /* {self.get_real_type(d.resolved_ty)} */"
        else:
            return d.symbol

    def get_type(self, t: Type) -> str:
        return self.type_name_printer.handle_type(t)

    def get_real_type(self, t: Optional[Type]) -> str:
        return "<error type>" if not t else self.get_type(t)

    def get_package_ref_decl(self, d: PackageRefDecl) -> str:
        return d.symbol

    def get_decl_ref_decl(self, d: DeclarationRefDecl) -> str:
        return d.symbol

    def get_parent_decl(self, d: IfaceParentDecl) -> str:
        return self.get_type_ref_decl(d.ty_ref)

    def get_return_decl(self, d: RetvalDecl) -> str:
        return self.get_type_ref_decl(d.ty_ref)

    def get_param_decl(self, d: ParamDecl) -> str:
        return f"{d.name}: {self.get_type_ref_decl(d.ty_ref)}"

    @override
    def visit_package_import_decl(self, d: PackageImportDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"use {self.get_package_ref_decl(d.pkg_ref)}")
        if d.is_alias():
            self.buffer.write(f" as {d.name}")
        self.buffer.write(";\n")

    @override
    def visit_decl_import_decl(self, d: DeclarationImportDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(
            f"from {self.get_package_ref_decl(d.decl_ref.pkg_ref)} use {self.get_decl_ref_decl(d.decl_ref)}"
        )
        if d.is_alias():
            self.buffer.write(f" as {d.name}")
        self.buffer.write(";\n")

    @override
    def visit_func_base_decl(self, d: FuncBaseDecl):
        self.buffer.write(self.indent * 2 * " ")
        fmt_args = ", ".join(self.get_param_decl(x) for x in d.params)
        if len(d.retvals) == 0:
            self.buffer.write(f"fn {d.name}({fmt_args});\n")
        elif len(d.retvals) == 1:
            fmt_ret = self.get_return_decl(d.retvals[0])
            self.buffer.write(f"fn {d.name}({fmt_args}) -> {fmt_ret};\n")
        else:
            fmt_ret = ", ".join(self.get_return_decl(r) for r in d.retvals)
            self.buffer.write(f"fn {d.name}({fmt_args}) -> ({fmt_ret});\n")

    @override
    def visit_struct_field_decl(self, d: StructFieldDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{d.name}: {self.get_type_ref_decl(d.ty_ref)};\n")

    @override
    def visit_enum_item_decl(self, d: EnumItemDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{d.name} = {d.value}; // {hex(d.value)}\n")

    @override
    def visit_enum_decl(self, d: EnumDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"enum {d.name} {{")
        if d.items:
            self.buffer.write("\n")
            self.indent += 1
            for i in d.items:
                self.handle_decl(i)
            self.indent -= 1
            self.buffer.write(self.indent * 2 * " ")
        self.buffer.write("}\n")

    @override
    def visit_struct_decl(self, d: StructDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"struct {d.name} {{")
        if d.fields:
            self.buffer.write("\n")
            self.indent += 1
            for f in d.fields:
                self.handle_decl(f)
            self.indent -= 1
            self.buffer.write(self.indent * 2 * " ")
        self.buffer.write("}\n")

    @override
    def visit_iface_decl(self, d: IfaceDecl):
        self.buffer.write(self.indent * 2 * " ")
        if d.parents:
            fmt_extends = ", ".join(self.get_parent_decl(e) for e in d.parents)
            self.buffer.write(f"interface {d.name}: {fmt_extends} {{")
        else:
            self.buffer.write(f"interface {d.name} {{")
        if d.methods:
            self.buffer.write("\n")
            self.indent += 1
            for f in d.methods:
                self.handle_decl(f)
            self.indent -= 1
            self.buffer.write(self.indent * 2 * " ")
        self.buffer.write("}\n")

    @override
    def visit_type_alias_decl(self, d: TypeAliasDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(
            f"type {d.name} = {self.get_type_ref_decl(d.ty_ref)}; // {self.get_real_type(d.final_ty)}\n"
        )

    @override
    def visit_package(self, p: Package):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"// Package {p.name}\n")
        for d in p.pkg_imports:
            self.handle_decl(d)
        for d in p.decl_imports:
            self.handle_decl(d)
        for d in p.type_aliases:
            self.handle_decl(d)
        for d in p.structs:
            self.handle_decl(d)
        for d in p.enums:
            self.handle_decl(d)
        for d in p.interfaces:
            self.handle_decl(d)
        for d in p.functions:
            self.handle_decl(d)

    @override
    def visit_package_group(self, g: PackageGroup):
        for p in g.children:
            self.handle_decl(p)
