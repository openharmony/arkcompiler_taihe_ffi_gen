from typing_extensions import override

from taihe.semantics.declarations import (
    DeclAlike,
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    EnumItemDecl,
    FuncDecl,
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
    VOID,
    BuiltinType,
    QualifiedType,
    TypeAlike,
)
from taihe.semantics.visitor import DeclVisitor, TypeVisitor


def pretty_print(x: DeclAlike) -> str:
    p = _PrettyPrinter()
    r = x._accept(p)
    assert isinstance(r, str)
    return r


class _TypeNamePrinter(TypeVisitor):
    @override
    def visit_type_decl(self, d: TypeDecl) -> str:
        if pkg := d.parent_package:
            return f"{pkg}.{d.name}"
        else:
            return f"<unknown>.{d.name}"

    @override
    def visit_builtin_type(self, t: BuiltinType) -> str:
        return t.name

    @override
    def visit_type_ref_decl(self, d: TypeRefDecl) -> str:
        if d.ref_ty:
            return self.handle_type(d.ref_ty)
        return f"<unresolved {d.name!r}>"

    @override
    def visit_qualified_type(self, t: QualifiedType) -> str:
        tname = self.handle_type(t.inner_ty)
        assert isinstance(tname, str)
        if not t.qual:
            return tname

        # field.name is always str instead of None. Skip type checking below.
        qualname = " ".join(f.name.lower() for f in t.qual)  # type: ignore
        return f"{qualname} {tname}"


class _PrettyPrinter(DeclVisitor):
    @override
    def visit_package_ref_decl(self, d: PackageRefDecl):
        return d.name

    @override
    def visit_decl_ref_decl(self, d: DeclarationRefDecl):
        return d.name

    @override
    def visit_package_import_decl(self, d: PackageImportDecl):
        if d.is_alias():
            return f"use {self.handle_decl(d.pkg)} as {d.name};"
        else:
            return f"use {self.handle_decl(d.pkg)};"

    @override
    def visit_decl_import_decl(self, d: DeclarationImportDecl):
        if d.is_alias():
            return f"from {self.handle_decl(d.pkg)} use {self.handle_decl(d.decl)} as {d.name};"
        else:
            return f"from {self.handle_decl(d.pkg)} use {self.handle_decl(d.decl)};"

    @override
    def visit_param_decl(self, d: ParamDecl):
        return f"{d.name}: {self.handle_type(d.qual_ty)}"

    @override
    def visit_func_decl(self, d: FuncDecl):
        fmt_args = ", ".join(self.visit_param_decl(x) for x in d.params)
        fmt_ret = "" if d.return_ty is VOID else f" -> {self.handle_type(d.return_ty)}"
        return f"fn {d.name}({fmt_args}){fmt_ret};"

    @override
    def visit_struct_field_decl(self, d: StructFieldDecl):
        return f"  {d.name}: {self.handle_type(d.ty)}"

    @override
    def visit_enum_item_decl(self, d: EnumItemDecl):
        return f"  {d.name} = {d.value}; // {hex(d.value)}"

    @override
    def visit_enum_decl(self, d: EnumDecl):
        r = f"enum {d.name} {{\n"
        for i in d.items:
            r += f"{self.visit_enum_item_decl(i)}\n"
        r += "}"
        return r

    @override
    def visit_struct_decl(self, d: StructDecl):
        header = f"struct {d.name} "
        if d.fields:
            ret = header + "{\n"
            for f in d.fields:
                ret += self.visit_struct_field_decl(f) + ";\n"
            return ret + "}"
        else:
            return f"{header} {{}}"

    @override
    def visit_package(self, p: Package):
        r = f"// Package {p.name}\n"
        if p.imports:
            r += "\n".join(self.handle_decl(d) for d in p.imports.values())
            r += "\n"
        if p.decls:
            r += "\n".join(self.handle_decl(d) for d in p.decls.values())
            r += "\n"
        return r

    @override
    def visit_package_group(self, g: PackageGroup):
        return "\n".join(self.handle_decl(p) for p in g.packages)

    def handle_type(self, t: TypeAlike):
        return _TypeNamePrinter().handle_type(t)
