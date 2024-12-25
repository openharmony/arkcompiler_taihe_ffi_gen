from collections.abc import Iterable
from typing import TYPE_CHECKING, TypeVar

from typing_extensions import override

from taihe.semantics.declarations import (
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    FuncBaseDecl,
    IfaceDecl,
    NamedDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
    PackageRefDecl,
    StructDecl,
    TypeAliasDecl,
    TypeDecl,
    TypeRefDecl,
)
from taihe.semantics.types import BuiltinType
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
    RecursiveTypeAliasError,
    StructFieldTypeError,
    SymbolConflictWithNamespaceError,
)

if TYPE_CHECKING:
    from taihe.semantics.declarations import IfaceParentDecl, StructFieldDecl


def analyze_semantics(pg: PackageGroup, diag: AbstractDiagnosticsManager):
    """Runs semantic analysis passes on the given package group."""
    _check_decl_confilct_with_namespace(pg, diag)
    _ResolveImportsPass(diag).handle_decl(pg)
    _resolve_typedef(pg, diag)
    _CheckFieldCollisionErrorPass(diag).handle_decl(pg)
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


class _CheckFieldCollisionErrorPass(DeclVisitor):
    """Checks for name and value collisions in declarations."""

    diag: AbstractDiagnosticsManager

    def __init__(self, diag: AbstractDiagnosticsManager):
        self.diag = diag

    @override
    def visit_package(self, p: Package) -> None:
        self.check_field_name_collision(p.children)
        return super().visit_package(p)

    @override
    def visit_enum_decl(self, d: EnumDecl) -> None:
        self.check_field_name_collision(d.children)
        return super().visit_enum_decl(d)

    @override
    def visit_func_base_decl(self, d: FuncBaseDecl) -> None:
        self.check_field_name_collision(d.children)
        return super().visit_func_base_decl(d)

    @override
    def visit_struct_decl(self, d: StructDecl) -> None:
        self.check_field_name_collision(d.children)
        return super().visit_struct_decl(d)

    @override
    def visit_iface_decl(self, d: IfaceDecl) -> None:
        self.check_field_name_collision(d.children)
        return super().visit_iface_decl(d)

    def check_field_name_collision(self, items: Iterable[NamedDecl]) -> None:
        """Checks for duplicate field names in declarations."""
        symbol = {}
        for f in items:
            if (prev := symbol.setdefault(f.name, f)) != f:
                self.diag.emit(DeclRedefDiagError(prev, f))


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


def _resolve_typedef(
    pg: PackageGroup,
    diag: AbstractDiagnosticsManager,
):
    resolving_dict: dict[TypeAliasDecl, int] = {}
    resolving_list: list[TypeAliasDecl] = []

    def visit(d: TypeAliasDecl):
        if d.is_solved:
            return
        n = len(resolving_list)
        m = resolving_dict.setdefault(d, n)
        if m == n:
            resolving_list.append(d)
            i = d.ty_ref.resolved_ty
            if isinstance(i, TypeAliasDecl):
                visit(i)
                i = i.final_ty
            d.final_ty = i
            resolving_list.pop()
            resolving_dict.pop(d)
        else:
            diag.emit(
                RecursiveTypeAliasError(resolving_list[m], resolving_list[m + 1 :])
            )

        d.is_solved = True

    for pkg in pg.packages:
        for typedef in pkg.type_aliases:
            visit(typedef)


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
                parent_ty = parent.ty_ref.resolved_ty
                parent_final_ty = (
                    parent_ty.final_ty
                    if isinstance(parent_ty, TypeAliasDecl)
                    else parent_ty
                )
                if parent_final_ty is None:
                    pass
                elif not isinstance(parent_final_ty, IfaceDecl):
                    diag.emit(ExtendsTypeError(parent))
                else:
                    parent_iface_list.append((parent, parent_final_ty))
                    prev = parent_iface_dict.setdefault(parent_final_ty, parent)
                    if prev != parent:
                        diag.emit(
                            DuplicateExtendsWarn(iface, parent_final_ty, prev, parent)
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
                field_ty = field.ty_ref.resolved_ty
                field_struct = (
                    field_ty.final_ty
                    if isinstance(field_ty, TypeAliasDecl)
                    else field_ty
                )
                if field_struct is None:
                    pass
                elif not isinstance(field_struct, BuiltinType | EnumDecl | StructDecl):
                    diag.emit(StructFieldTypeError(field))
                elif isinstance(field_struct, StructDecl):
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
