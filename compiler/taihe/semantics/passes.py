from typing_extensions import override

from taihe.semantics.declarations import (
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
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import (
    DeclNotExistError,
    DeclRedefDiagError,
    NotATypeError,
    PackageNotExistError,
    QualifierError,
    RecursiveInclusionError,
    SymbolConflictWithNamespaceError,
)


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
    _imported_decls: dict[str, TypeDecl]
    diag: DiagnosticsManager

    def __init__(self, pm: PackageGroup, diag: DiagnosticsManager):
        self._pkg_group = pm
        self._current_package = None  # Always points to the current package.
        self._imported_pkgs = {}
        self._imported_decls = {}
        self.diag = diag

    @property
    def _pkg(self) -> Package:
        assert self._current_package
        return self._current_package

    @override
    def visit_package(self, p: Package):
        self._current_package = p
        return super().visit_package(p)

    @override
    def visit_package_import_decl(self, d: PackageImportDecl):
        with self.diag.capture_error():
            if pkg := self._pkg_group.lookup(d.pkg):
                self._imported_pkgs[d.name] = pkg
            else:
                raise PackageNotExistError(d.name, d.loc)

    @override
    def visit_decl_import_decl(self, d: DeclarationImportDecl):
        with self.diag.capture_error():
            if pkg := self._pkg_group.lookup(d.pkg):
                if decl := pkg.decls.get(d.decl):
                    if isinstance(decl, (StructDecl | EnumDecl)):
                        self._imported_decls[d.name] = decl
                    else:
                        raise NotATypeError(d)
                else:
                    raise DeclNotExistError(d.name, d)
            else:
                raise PackageNotExistError(d.pkg, d.pkg_loc)

    def visit_type_ref_decl(self, d: TypeRefDecl):
        if d.ref_ty:
            return

        xs = d.name.rsplit(".", maxsplit=1)
        if len(xs) == 1:
            # fn foo(x: Bar)
            pkg_name = ""
            decl_name = xs[0]
        elif len(xs) == 2:
            # fn foo(x: com.example.Bar)
            pkg_name, decl_name = xs
        else:
            raise ValueError("unexpected format for type reference")

        with self.diag.capture_error():
            if pkg_name:
                if pkg := self._imported_pkgs.get(pkg_name):
                    if (decl := pkg.decls.get(decl_name)) is None:
                        raise DeclNotExistError(d.name, d)
                else:
                    raise DeclNotExistError(d.name, d)
            else:
                decl1 = self._imported_decls.get(decl_name, None)
                decl2 = self._pkg.decls.get(decl_name, None)
                if (decl := decl1 or decl2) is None:
                    raise DeclNotExistError(d.name, d)
            if not isinstance(decl, Type):
                raise NotATypeError(d)
            d.ref_ty = decl


def pretty_print(x: DeclAlike) -> str:
    p = _PrettyPrinter()
    r = x._accept(p)
    assert isinstance(r, str)
    return r


def resolve_types(pg: PackageGroup, diag: DiagnosticsManager):
    """Replaces UnresolvedType with the corresponding type."""
    p = _ResolveImportsPass(pg, diag)
    p.handle_decl(pg)
    check_decl_redefine(pg, diag)
    check_cycle_error(pg, diag)
    check_sym_confilct_namespace(pg, diag)
    check_qualifier(pg, diag)


class CheckQualifier(DeclVisitor):
    pg: PackageGroup
    diag: DiagnosticsManager

    def __init__(self, pg: PackageGroup, diag: DiagnosticsManager):
        self.pg = pg
        self.diag = diag

    @override
    def visit_param_decl(self, d: ParamDecl):
        if d.qual_ty.qual:
            if not isinstance(d.qual_ty.inner_ty.ref_ty, StructDecl):
                self.diag.emit(QualifierError(d, d.qual_ty.inner_ty.name))


def check_qualifier(pg: PackageGroup, diag: DiagnosticsManager):
    c = CheckQualifier(pg, diag)
    c.handle_decl(pg)


def check_sym_confilct_namespace(pg: PackageGroup, diag: DiagnosticsManager):
    pkg_name = set(pg._pkgs)

    for p in pg.packages:
        for i in p.decls:
            decl_name = p.name + "." + i
            if decl_name in pkg_name:
                diag.emit(SymbolConflictWithNamespaceError(p.decls[i], p.name))


def check_decl_redefine(pg: PackageGroup, diag: DiagnosticsManager):
    for p in pg.packages:
        if redef_decls := p.imports.keys() & p.decls.keys():
            for redef_decl in redef_decls:
                diag.emit(
                    DeclRedefDiagError(p.imports[redef_decl], p.decls[redef_decl])
                )


def check_cycle_error(pg: PackageGroup, diag: DiagnosticsManager):
    struct_table = {}
    for pkg in pg.packages:
        for struct in pkg.structs:
            struct_table.setdefault(struct, [])
            for field in struct.fields:
                if isinstance(field.ty.ref_ty, StructDecl):
                    struct_table[struct].append((field, field.ty.ref_ty))

    cycles = check_cycle(struct_table)
    for cycle in cycles:
        last, *other = cycle[::-1]
        diag.emit(
            RecursiveInclusionError(
                last.loc, last.parent, [(edge.loc, edge.parent) for edge in other]
            )
        )


def check_cycle(graph):
    """Input a graph, return all the cycles in it.

    This function can be reused.
    - graph: {parent: [(edge, child), ...], ...}
    - return value: [[edge, ...], ...]
    """
    cycles = []

    visited = set()
    visiting_dict = {}
    visiting_list = []

    def visit(parent):
        if parent in visited:
            return
        idx = len(visiting_list)
        rec = visiting_dict.setdefault(parent, idx)
        if idx != rec:
            cycles.append(visiting_list[rec:])
            return
        for edge, child in graph[parent]:
            visiting_list.append(edge)
            visit(child)
            visiting_list.pop()
        visited.add(parent)

    for parent in graph:
        visit(parent)

    return cycles
