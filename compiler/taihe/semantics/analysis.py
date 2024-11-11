from collections.abc import Sequence
from typing import Any

from typing_extensions import override

from taihe.semantics.declarations import (
    Decl,
    DeclarationImportDecl,
    EnumDecl,
    EnumItemDecl,
    FuncDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
    ParamDecl,
    StructDecl,
    TypeDecl,
    TypeRefDecl,
)
from taihe.semantics.visitor import DeclVisitor, RecursiveTypeVisitor
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import (
    DeclarationNotInScopeError,
    DeclNotExistError,
    DeclRedefDiagError,
    EnumValueCollisionError,
    NotADeclarationError,
    NotAPackageError,
    NotATypeError,
    PackageNotExistError,
    PackageNotInScopeError,
    QualifierError,
    RecursiveInclusionError,
    SymbolConflictWithNamespaceError,
)


def analyze_semantics(pg: PackageGroup, diag: DiagnosticsManager):
    """Replaces UnresolvedType with the corresponding type."""
    _ResolveImportsPass(diag).handle_decl(pg)
    check_decl_redefine(pg, diag)
    check_recursive_inclusion(pg, diag)
    check_sym_confilct_namespace(pg, diag)
    _CheckFieldCollisionErrorPass(diag).handle_decl(pg)
    _CheckQualifierErrorPass(diag).handle_decl(pg)


class _ResolveImportsPass(RecursiveTypeVisitor):
    diag: DiagnosticsManager

    def __init__(self, diag: DiagnosticsManager):
        self._current_package_group = None
        self._current_package = None  # Always points to the current package.
        self.diag = diag

    @property
    def _pkg(self) -> Package:
        assert self._current_package
        return self._current_package

    @property
    def _pkg_group(self) -> PackageGroup:
        assert self._current_package_group
        return self._current_package_group

    @override
    def visit_package(self, p: Package):
        self._current_package = p
        super().visit_package(p)
        self._current_package = None

    @override
    def visit_package_group(self, g: PackageGroup):
        self._current_package_group = g
        super().visit_package_group(g)
        self._current_package_group = None

    @override
    def visit_package_import_decl(self, d: PackageImportDecl):
        if not d.pkg.resolved:
            if pkg := self._pkg_group.lookup(d.pkg.name):
                d.pkg.ref_pkg = pkg
            else:
                self.diag.emit(PackageNotExistError(d.pkg.name, d.pkg.loc))
                d.pkg.ref_pkg = None
            d.pkg.resolved = True

    @override
    def visit_decl_import_decl(self, d: DeclarationImportDecl):
        if not d.decl.resolved:
            if not d.pkg.resolved:
                if pkg := self._pkg_group.lookup(d.pkg.name):
                    d.pkg.ref_pkg = pkg
                else:
                    self.diag.emit(PackageNotExistError(d.pkg.name, d.pkg.loc))
                    d.pkg.ref_pkg = None
                d.pkg.resolved = True
            if (pkg := d.pkg.ref_pkg) is None:
                # no need to raise error
                d.decl.ref_decl = None
            elif isinstance(decl := pkg.decls.get(d.decl.name), TypeDecl):
                d.decl.ref_decl = decl
            elif decl:
                self.diag.emit(NotATypeError(d.decl.name, d.decl.loc))
                d.decl.ref_decl = None
            else:
                self.diag.emit(DeclNotExistError(d.decl.name, d.decl.loc))
                d.decl.ref_decl = None
        d.pkg.resolved = True

    def visit_type_ref_decl(self, d: TypeRefDecl):
        if d.resolved:
            return

        xs = d.name.rsplit(".", maxsplit=1)
        if len(xs) == 2:
            # fn foo(x: com.example.Bar)
            pkg_name, decl_name = xs
            if (import_pkg := self._pkg.imports.get(pkg_name)) is None:
                self.diag.emit(PackageNotInScopeError(pkg_name, d.loc))
                d.ref_ty = None
            elif not isinstance(import_pkg, PackageImportDecl):
                self.diag.emit(NotAPackageError(pkg_name, d.loc))
                d.ref_ty = None
            elif (pkg := import_pkg.pkg.ref_pkg) is None:
                # no need to raise error
                d.ref_ty = None
            elif isinstance(decl := pkg.decls.get(decl_name), TypeDecl):
                d.ref_ty = decl
            elif decl:
                self.diag.emit(NotATypeError(decl_name, d.loc))
                d.ref_ty = None
            else:
                self.diag.emit(DeclNotExistError(decl_name, d.loc))
                d.ref_ty = None
        elif len(xs) == 1:
            # fn foo(x: Bar)
            decl_name = xs[0]
            if isinstance(decl := self._pkg.decls.get(decl_name), TypeDecl):
                d.ref_ty = decl
            elif decl:
                self.diag.emit(NotATypeError(decl_name, d.loc))
                d.ref_ty = None
            elif (import_decl := self._pkg.imports.get(decl_name)) is None:
                self.diag.emit(DeclarationNotInScopeError(decl_name, d.loc))
                d.ref_ty = None
            elif not isinstance(import_decl, DeclarationImportDecl):
                self.diag.emit(NotADeclarationError(decl_name, d.loc))
                d.ref_ty = None
            elif (decl := import_decl.decl.ref_decl) is None:
                # no need to raise error
                d.ref_ty = None
            else:
                d.ref_ty = decl
        else:
            raise ValueError("unexpected format for type reference")

        d.resolved = True


class _CheckQualifierErrorPass(DeclVisitor):
    diag: DiagnosticsManager

    def __init__(self, diag: DiagnosticsManager):
        self.diag = diag

    @override
    def visit_param_decl(self, d: ParamDecl):
        if d.ty.qual:
            if not isinstance(d.ty.ref_ty, StructDecl):
                self.diag.emit(QualifierError(d, d.ty.name))


class _CheckFieldCollisionErrorPass(DeclVisitor):
    diag: DiagnosticsManager

    def __init__(self, diag: DiagnosticsManager):
        self.diag = diag

    @override
    def visit_enum_decl(self, d: EnumDecl) -> Any:
        check_field_name_collision(self.diag, d.items)
        check_field_value_collision(self.diag, d.items)

    @override
    def visit_func_decl(self, d: FuncDecl) -> Any:
        check_field_name_collision(self.diag, d.params)

    @override
    def visit_struct_decl(self, d: StructDecl) -> Any:
        check_field_name_collision(self.diag, d.fields)


def check_field_name_collision(
    diag: DiagnosticsManager,
    items: Sequence[Decl],
):
    symbol = {}
    for f in items:
        if prev := symbol.get(f.name):
            diag.emit(DeclRedefDiagError(prev, f))
        else:
            symbol[f.name] = f


def check_field_value_collision(
    diag: DiagnosticsManager,
    items: Sequence[EnumItemDecl],
):
    symbol = {}
    for f in items:
        if prev := symbol.get(f.value):
            diag.emit(EnumValueCollisionError(prev, f, f.value))
        else:
            symbol[f.value] = f


def check_sym_confilct_namespace(pg: PackageGroup, diag: DiagnosticsManager):
    namespaces = set()
    for pkg_name in pg._pkgs:
        # package "a.b.c" -> namespaces ["a.b.c", "a.b", "a"]
        while True:
            namespaces.add(pkg_name)
            splited = pkg_name.rsplit(".", maxsplit=1)
            if len(splited) == 2:
                pkg_name = splited[0]
            else:
                break

    for p in pg.packages:
        for i in p.decls:
            decl_name = p.name + "." + i
            if decl_name in namespaces:
                diag.emit(SymbolConflictWithNamespaceError(p.decls[i], p.name))


def check_decl_redefine(pg: PackageGroup, diag: DiagnosticsManager):
    for p in pg.packages:
        for redef_decl in p.imports.keys() & p.decls.keys():
            diag.emit(DeclRedefDiagError(p.imports[redef_decl], p.decls[redef_decl]))


def check_recursive_inclusion(pg: PackageGroup, diag: DiagnosticsManager):
    struct_table = {}
    for pkg in pg.packages:
        for struct in pkg.structs:
            struct_table.setdefault(struct, [])
            for field in struct.fields:
                if isinstance(field.ty.ref_ty, StructDecl):
                    struct_table[struct].append((field, field.ty.ref_ty))

    cycles = detect_cycles(struct_table)
    for cycle in cycles:
        last, *other = cycle[::-1]
        diag.emit(
            RecursiveInclusionError(
                last.loc, last.parent, [(edge.loc, edge.parent) for edge in other]
            )
        )


def detect_cycles(graph):
    """Detects and returns all cycles in a directed graph.

    Example:
    -------
    >>> graph = {
            "A": [("A.b_0", "B")],
            "B": [("B.c_0", "C")],
            "C": [("C.a_0", "A"), ("C.a_1", "A")],
        }
    >>> find_cycles(graph)
    [["A.b_0", "B.c_0", "C.a_0"], ["A.b_0", "B.c_0", "C.a_1"]]
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
