"""Format the IDL files."""

from typing import TextIO

from typing_extensions import override

from taihe.semantics.declarations import (
    DeclAlike,
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    EnumItemDecl,
    FuncBaseDecl,
    IfaceDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
    PackageRefDecl,
    ParamDecl,
    StructDecl,
    StructFieldDecl,
    TypeDecl,
    TypeRefDecl,
)
from taihe.semantics.types import (
    BuiltinType,
)
from taihe.semantics.visitor import DeclVisitor, TypeVisitor


def pretty_print(x: DeclAlike, buffer: TextIO):
    printer = _PrettyPrinter(buffer)
    printer.handle_decl(x)


class _TypeNamePrinter(TypeVisitor[str]):
    @override
    def visit_type_ref_decl(self, d: TypeRefDecl):
        ref_str = (
            f"<unresolved {d.name!r}>"
            if not d.resolved
            else f"<error {d.name!r}>" if not d.ref_ty else self.handle_type(d.ref_ty)
        )
        return d.qual.describe(ref_str)

    @override
    def visit_type_decl(self, d: TypeDecl):
        if pkg := d.parent_package:
            return f"{pkg}.{d.name}"
        else:
            return f"<unknown>.{d.name}"

    @override
    def visit_builtin_type(self, t: BuiltinType):
        return t.name


class _PrettyPrinter(DeclVisitor):
    def __init__(self, buffer: TextIO):
        self.buffer = buffer
        self.indent = 0

    def get_type_ref_decl(self, d: TypeRefDecl) -> str:
        return _TypeNamePrinter().handle_type(d)

    def get_package_ref_decl(self, d: PackageRefDecl) -> str:
        return d.name

    def get_decl_ref_decl(self, d: DeclarationRefDecl) -> str:
        return d.name

    def get_param_decl(self, d: ParamDecl) -> str:
        return f"{d.name}: {self.get_type_ref_decl(d.ty)}"

    @override
    def visit_package_import_decl(self, d: PackageImportDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"use {self.get_package_ref_decl(d.pkg)}")
        if d.is_alias():
            self.buffer.write(f" as {d.name}")
        self.buffer.write(";\n")

    @override
    def visit_decl_import_decl(self, d: DeclarationImportDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(
            f"from {self.get_package_ref_decl(d.decl.pkg)} use {self.get_decl_ref_decl(d.decl)}"
        )
        if d.is_alias():
            self.buffer.write(f" as {d.name}")
        self.buffer.write(";\n")

    @override
    def visit_func_base_decl(self, d: FuncBaseDecl):
        self.buffer.write(self.indent * 2 * " ")
        fmt_args = ", ".join(self.get_param_decl(x) for x in d.params)
        if len(d.return_types) == 0:
            self.buffer.write(f"fn {d.name}({fmt_args});\n")
        elif len(d.return_types) == 1:
            fmt_ret = self.get_type_ref_decl(d.return_types[0])
            self.buffer.write(f"fn {d.name}({fmt_args}) -> {fmt_ret};\n")
        else:
            fmt_ret = ", ".join(self.get_type_ref_decl(r) for r in d.return_types)
            self.buffer.write(f"fn {d.name}({fmt_args}) -> ({fmt_ret});\n")

    @override
    def visit_struct_field_decl(self, d: StructFieldDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{d.name}: {self.get_type_ref_decl(d.ty)};\n")

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
            fmt_extends = ", ".join(self.get_type_ref_decl(e) for e in d.parents)
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
    def visit_package(self, p: Package):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"// Package {p.name}\n")
        for d in p.pkg_imports:
            self.handle_decl(d)
        for d in p.decl_imports:
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
        for p in g.packages:
            self.handle_decl(p)
