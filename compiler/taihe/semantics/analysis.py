from typing import TYPE_CHECKING, TypeVar

from typing_extensions import override

from taihe.semantics.declarations import (
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    IfaceDecl,
    NamedDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
    PackageRefDecl,
    StructDecl,
    TypeDecl,
    TypeRefDecl,
)
from taihe.semantics.visitor import DeclVisitor
from taihe.utils.diagnostics import AbstractDiagnosticsManager
from taihe.utils.exceptions import (
    DeclarationNotInScopeError,
    DeclNotExistError,
    DeclRedefDiagError,
    DuplicateExtendsWarn,
    ExtendsTypeError,
    NotATypeError,
    PackageNotExistError,
    PackageNotInScopeError,
    RecursiveExtensionError,
    RecursiveInclusionError,
    SymbolConflictWithNamespaceError,
)

if TYPE_CHECKING:
    from taihe.semantics.declarations import IfaceParentDecl, StructFieldDecl


def analyze_semantics(pg: PackageGroup, diag: AbstractDiagnosticsManager):
    """Runs semantic analysis passes on the given package group."""
    _check_decl_confilct_with_namespace(pg, diag)
    _ResolveImportsPass(diag).handle_decl(pg)
    _CheckFieldNameCollisionErrorPass(diag).handle_decl(pg)
    _CalculateEnumItemValuePass(diag).handle_decl(pg)
    _check_struct_fields(pg, diag)
    _check_iface_parents(pg, diag)


class _ResolveImportsPass(DeclVisitor):
    """Resolves imports and type references within a package group."""

    diag: AbstractDiagnosticsManager

    def __init__(self, diag: AbstractDiagnosticsManager):
        self._current_pkg_group = None
        self._current_pkg = None  # Always points to the current package.
        self.diag = diag

    @property
    def pkg(self) -> Package:
        assert self._current_pkg
        return self._current_pkg

    @property
    def pkg_group(self) -> PackageGroup:
        assert self._current_pkg_group
        return self._current_pkg_group

    @override
    def visit_package(self, p: Package):
        self._current_pkg = p
        super().visit_package(p)
        self._current_pkg = None

    @override
    def visit_package_group(self, g: PackageGroup):
        self._current_pkg_group = g
        super().visit_package_group(g)
        self._current_pkg_group = None

    @override
    def visit_package_ref_decl(self, d: PackageRefDecl):
        if d.is_resolved:
            return

        if pkg := self.pkg_group.lookup(d.symbol):
            d.resolved_pkg = pkg
        else:
            self.diag.emit(PackageNotExistError(d.symbol, loc=d.loc))
            d.resolved_pkg = None

        d.is_resolved = True

    @override
    def visit_decl_ref_decl(self, d: DeclarationRefDecl):
        if d.is_resolved:
            return

        self.handle_decl(d.pkg_ref)

        if (pkg := d.pkg_ref.resolved_pkg) is None:
            # No need to repeatedly throw exceptions for package import errors
            d.resolved_decl = None
        elif isinstance(decl := pkg.decls.get(d.symbol), TypeDecl):
            d.resolved_decl = decl
        elif decl:
            self.diag.emit(NotATypeError(d.symbol, loc=d.loc))
            d.resolved_decl = None
        else:
            self.diag.emit(DeclNotExistError(d.symbol, loc=d.loc))
            d.resolved_decl = None

        d.pkg_ref.is_resolved = True

    def visit_type_ref_decl(self, d: TypeRefDecl):
        if d.is_resolved:
            return

        xs = d.symbol.rsplit(".", maxsplit=1)

        # fn foo(x: com.example.Bar)
        if len(xs) == 2:
            pkg_name, decl_name = xs

            # Find the corresponding imported package according to the package name
            if not isinstance(
                import_pkg := self.pkg.imports.get(pkg_name), PackageImportDecl
            ):
                self.diag.emit(PackageNotInScopeError(pkg_name, loc=d.loc))
                d.resolved_ty = None
            elif (pkg := import_pkg.pkg_ref.resolved_pkg) is None:
                # No need to repeatedly throw exceptions for package import errors
                d.resolved_ty = None

            # Then find the corresponding type declaration from the package
            elif isinstance(decl := pkg.decls.get(decl_name), TypeDecl):
                d.resolved_ty = decl
            elif decl:
                self.diag.emit(NotATypeError(decl_name, loc=d.loc))
                d.resolved_ty = None
            else:
                self.diag.emit(DeclNotExistError(decl_name, loc=d.loc))
                d.resolved_ty = None

        # fn foo(x: Bar)
        elif len(xs) == 1:
            decl_name = xs[0]

            # Find types declared in the current package
            if isinstance(decl := self.pkg.decls.get(decl_name), TypeDecl):
                d.resolved_ty = decl
            elif decl:
                self.diag.emit(NotATypeError(decl_name, loc=d.loc))
                d.resolved_ty = None

            # If that fails, continue looking for imported type declarations
            elif not isinstance(
                import_decl := self.pkg.imports.get(decl_name), DeclarationImportDecl
            ):
                self.diag.emit(DeclarationNotInScopeError(decl_name, loc=d.loc))
                d.resolved_ty = None
            elif (decl := import_decl.decl_ref.resolved_decl) is None:
                # No need to repeatedly throw exceptions for declaration import errors
                d.resolved_ty = None
            else:
                d.resolved_ty = decl

        # Should not be reached
        else:
            raise ValueError("unexpected format for type reference")

        d.is_resolved = True


class _CalculateEnumItemValuePass(DeclVisitor):
    """Calculate Enum Values."""

    diag: AbstractDiagnosticsManager

    def __init__(self, diag: AbstractDiagnosticsManager):
        self.diag = diag

    def visit_enum_decl(self, d: EnumDecl) -> None:
        value = 0
        for i in d.items:
            if i.value is None:
                i.value = value
            else:
                value = i.value
            value += 1


class _CheckFieldNameCollisionErrorPass(DeclVisitor):
    """Check for duplicate field names in declarations and name anonymous declarations."""

    diag: AbstractDiagnosticsManager

    def __init__(self, diag: AbstractDiagnosticsManager):
        self.diag = diag

    @override
    def visit_named_decl(self, d: NamedDecl) -> None:
        symbol = {}
        for field_name, children in d.all_children.items():
            for i, f in enumerate(children):
                if not f.name:
                    f.name = f"_{field_name}_{i}"
                if (prev := symbol.setdefault(f.name, f)) != f:
                    self.diag.emit(DeclRedefDiagError(prev, f))

        return super().visit_named_decl(d)


def _check_decl_confilct_with_namespace(
    pg: PackageGroup,
    diag: AbstractDiagnosticsManager,
):
    """Checks for declarations conflicts with namespaces."""
    namespaces = set()
    for pkg_name in pg.package_dict:
        # package "a.b.c" -> namespaces ["a.b.c", "a.b", "a"]
        while True:
            namespaces.add(pkg_name)
            splited = pkg_name.rsplit(".", maxsplit=1)
            if len(splited) == 2:
                pkg_name = splited[0]
            else:
                break

    for p in pg.packages:
        for d in p.decls.values():
            name = p.name + "." + d.name
            if name in namespaces:
                diag.emit(SymbolConflictWithNamespaceError(d, p))


def _check_iface_parents(
    pg: PackageGroup,
    diag: AbstractDiagnosticsManager,
):
    """Validates interface inheritance for correctness and cycles."""
    parent_iface_table: dict[IfaceDecl, list[tuple[IfaceParentDecl, IfaceDecl]]] = {}
    for pkg in pg.packages:
        for iface in pkg.interfaces:
            parent_iface_list = parent_iface_table.setdefault(iface, [])
            parent_iface_dict = {}
            for parent in iface.parents:
                if (parent_iface := parent.ty_ref.resolved_ty) is None:
                    pass
                elif not isinstance(parent_iface, IfaceDecl):
                    diag.emit(ExtendsTypeError(parent))
                else:
                    parent_iface_list.append((parent, parent_iface))
                    prev = parent_iface_dict.setdefault(parent_iface, parent)
                    if prev != parent:
                        diag.emit(
                            DuplicateExtendsWarn(
                                iface,
                                parent_iface,
                                loc=parent.ty_ref.loc,
                                prev_loc=prev.ty_ref.loc,
                            )
                        )

    cycles = detect_cycles(parent_iface_table)
    for cycle in cycles:
        last, *other = cycle[::-1]
        diag.emit(RecursiveExtensionError(last, other))


def _check_struct_fields(
    pg: PackageGroup,
    diag: AbstractDiagnosticsManager,
):
    """Validates struct fields for type correctness and cycles."""
    field_struct_table: dict[StructDecl, list[tuple[StructFieldDecl, StructDecl]]] = {}
    for pkg in pg.packages:
        for struct in pkg.structs:
            field_struct_list = field_struct_table.setdefault(struct, [])
            for field in struct.fields:
                if isinstance((field_struct := field.ty_ref.resolved_ty), StructDecl):
                    field_struct_list.append((field, field_struct))

    cycles = detect_cycles(field_struct_table)
    for cycle in cycles:
        last, *other = cycle[::-1]
        diag.emit(RecursiveInclusionError(last, other))


V = TypeVar("V")
E = TypeVar("E")


def detect_cycles(graph: dict[V, list[tuple[E, V]]]) -> list[list[E]]:
    """Detects and returns all cycles in a directed graph.

    Example:
    -------
    >>> graph = {
            "A": [("A.b_0", "B")],
            "B": [("B.c_0", "C")],
            "C": [("C.a_0", "A"), ("C.a_1", "A")],
        }
    >>> detect_cycles(graph)
    [["A.b_0", "B.c_0", "C.a_0"], ["A.b_0", "B.c_0", "C.a_1"]]
    """
    cycles: list[list[E]] = []

    order = {point: i for i, point in enumerate(graph)}
    glist = [
        [(edge, order[child]) for edge, child in children]
        for children in graph.values()
    ]
    visited = [False for _ in glist]
    edges: list[E] = []

    def visit(i: int):
        if i < k:
            return
        if visited[i]:
            if i == k:
                cycles.append(edges.copy())
            return
        visited[i] = True
        for edge, j in glist[i]:
            edges.append(edge)
            visit(j)
            edges.pop()
        visited[i] = False

    for k in range(len(glist)):
        visit(k)

    return cycles
