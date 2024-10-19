from typing_extensions import override

from taihe.semantics.declarations import (
    Decl,
    DeclAlike,
    DeclarationImportDecl,
    EnumDecl,
    EnumItemDecl,
    FuncDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
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
    Type,
    TypeAlike,
)
from taihe.semantics.visitor import DeclVisitor, RecursiveTypeVisitor, TypeVisitor


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
    def visit_package_import_decl(self, d: PackageImportDecl):
        if d.is_alias():
            return f"use {d.pkg} as {d.name};"
        else:
            return f"use {d.pkg};"

    @override
    def visit_decl_import_decl(self, d: DeclarationImportDecl):
        if d.is_alias():
            return f"from {d.pkg} use {d.decl} as {d.name};"
        else:
            return f"from {d.pkg} use {d.decl};"

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
        r += "}\n"
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


class _ResolveImportsPass(RecursiveTypeVisitor):
    _imported_pkgs: dict[str, Package]
    _imported_decls: dict[str, Decl]

    def __init__(self, pm: PackageGroup):
        self._pkg_group = pm
        self._current_package = None  # Always points to the current package.
        self._imported_pkgs = {}
        self._imported_decls = {}

    @property
    def _pkg(self) -> Package:
        assert self._current_package
        return self._current_package

    @override
    def visit_package(self, p: Package):
        self._current_package = p
        # TODO: check for conflicts between the imported and the local decl
        return super().visit_package(p)

    @override
    def visit_package_import_decl(self, d: PackageImportDecl):
        if pkg := self._pkg_group.lookup(d.pkg):
            # TODO Conflict
            self._imported_pkgs[d.name] = pkg
        else:
            raise ValueError("unknown pkg")

    @override
    def visit_decl_import_decl(self, d: DeclarationImportDecl):
        if pkg := self._pkg_group.lookup(d.pkg):
            if decl := pkg.decls.get(d.decl):
                # TODO Conflict
                self._imported_decls[d.name] = decl
            else:
                raise ValueError("unknown decl")
        else:
            raise ValueError("unknown pkg")

    def visit_type_ref_decl(self, d: TypeRefDecl):
        if d.ref_ty:
            return

        xs = d.name.rsplit(".", maxsplit=1)
        if len(xs) == 1:
            # fn foo(x: Bar)
            pkg = ""
            decl = xs[0]
        elif len(xs) == 2:
            # fn foo(x: com.example.Bar)
            pkg, decl = xs
        else:
            raise ValueError("unexpected format for type reference")

        if pkg:
            # Imports from aother package.
            # TODO handle missing packages
            pkg = self._imported_pkgs[pkg]
            decl = pkg.decls[decl]
        else:
            # TODO handle conflicts
            decl1 = self._imported_decls.get(decl, None)
            decl2 = self._pkg.decls.get(decl, None)
            decl = decl1 or decl2

        assert isinstance(decl, Type)
        d.ref_ty = decl


def pretty_print(x: DeclAlike) -> str:
    p = _PrettyPrinter()
    r = x._accept(p)
    assert isinstance(r, str)
    return r


def resolve_types(pg: PackageGroup):
    """Replaces UnresolvedType with the corresponding type."""
    p = _ResolveImportsPass(pg)
    p.handle_decl(pg)
