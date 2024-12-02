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


def pretty_print(x: DeclAlike) -> str:
    r = _PrettyPrinter().handle_decl(x)
    assert isinstance(r, str)
    return r


class _TypeNamePrinter(TypeVisitor):
    @override
    def visit_type_ref_decl(self, d: TypeRefDecl) -> str:
        ref_str = (
            f"<unresolved {d.name!r}>"
            if not d.resolved
            else f"<error {d.name!r}>" if not d.ref_ty else self.handle_type(d.ref_ty)
        )
        return d.qual.describe(ref_str)

    @override
    def visit_type_decl(self, d: TypeDecl) -> str:
        if pkg := d.parent_package:
            return f"{pkg}.{d.name}"
        else:
            return f"<unknown>.{d.name}"

    @override
    def visit_builtin_type(self, t: BuiltinType) -> str:
        return t.name


class _PrettyPrinter(DeclVisitor):
    @override
    def visit_package_ref_decl(self, d: PackageRefDecl):
        return d.name

    @override
    def visit_type_ref_decl(self, d: TypeRefDecl) -> str:
        return _TypeNamePrinter().handle_type(d)

    @override
    def visit_decl_ref_decl(self, d: DeclarationRefDecl):
        return d.name

    @override
    def visit_package_import_decl(self, d: PackageImportDecl):
        ret = f"use {self.handle_decl(d.pkg)}"
        if d.is_alias():
            ret += f" as {d.name}"
        ret += ";"
        return ret

    @override
    def visit_decl_import_decl(self, d: DeclarationImportDecl):
        ret = f"from {self.handle_decl(d.decl.pkg)} use {self.handle_decl(d.decl)}"
        if d.is_alias():
            ret += f" as {d.name}"
        ret += ";"
        return ret

    @override
    def visit_param_decl(self, d: ParamDecl):
        return f"{d.name}: {self.handle_decl(d.ty)}"

    @override
    def visit_func_base_decl(self, d: FuncBaseDecl):
        fmt_args = ", ".join(self.handle_decl(x) for x in d.params)
        fmt_ret = ", ".join(self.handle_decl(r) for r in d.return_types)
        return f"fn {d.name}({fmt_args}) -> ({fmt_ret});"

    @override
    def visit_struct_field_decl(self, d: StructFieldDecl):
        return f"{d.name}: {self.handle_decl(d.ty)};"

    @override
    def visit_enum_item_decl(self, d: EnumItemDecl):
        return f"{d.name} = {d.value}; // {hex(d.value)}"

    @override
    def visit_enum_decl(self, d: EnumDecl):
        r = f"enum {d.name} {{"
        r += "\n"
        for i in d.items:
            r += "  " + self.handle_decl(i) + "\n"
        r += "}"
        return r

    @override
    def visit_struct_decl(self, d: StructDecl):
        ret = f"struct {d.name} {{"
        if d.fields:
            ret += "\n"
            for f in d.fields:
                ret += "  " + self.handle_decl(f) + "\n"
        ret += "}"
        return ret

    @override
    def visit_iface_decl(self, d: IfaceDecl):
        if d.parents:
            fmt_extends = ", ".join(self.handle_decl(e) for e in d.parents)
            ret = f"interface {d.name}: {fmt_extends} {{"
        else:
            ret = f"interface {d.name} {{"
        if d.methods:
            ret += "\n"
            for f in d.methods:
                ret += "  " + self.handle_decl(f) + "\n"
        ret += "}"
        return ret

    @override
    def visit_package(self, p: Package):
        r = f"// Package {p.name}\n"
        for d in p.pkg_imports:
            r += self.handle_decl(d) + "\n"
        for d in p.decl_imports:
            r += self.handle_decl(d) + "\n"
        for d in p.structs:
            r += self.handle_decl(d) + "\n"
        for d in p.enums:
            r += self.handle_decl(d) + "\n"
        for d in p.interfaces:
            r += self.handle_decl(d) + "\n"
        for d in p.functions:
            r += self.handle_decl(d) + "\n"
        return r

    @override
    def visit_package_group(self, g: PackageGroup):
        return "\n".join(self.handle_decl(p) for p in g.packages)
