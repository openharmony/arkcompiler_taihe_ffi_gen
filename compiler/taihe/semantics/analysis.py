from collections.abc import Iterable
from typing import TYPE_CHECKING, TypeVar

from typing_extensions import override

from taihe.semantics.declarations import (
    CallbackTypeRefDecl,
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    GenericTypeRefDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    NamedDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
    PackageRefDecl,
    SimpleTypeRefDecl,
    StructDecl,
    TypeDecl,
)
from taihe.semantics.types import (
    BUILTIN_GENERICS,
    BUILTIN_TYPES,
    CallbackType,
    UserType,
)
from taihe.semantics.visitor import DeclVisitor
from taihe.utils.diagnostics import AbstractDiagnosticsManager
from taihe.utils.exceptions import (
    DeclarationNotInScopeError,
    DeclNotExistError,
    DeclRedefError,
    DuplicateExtendsWarn,
    EnumValueConflictError,
    ExtendsTypeError,
    GenericArgumentsError,
    NotATypeError,
    PackageNotExistError,
    PackageNotInScopeError,
    RecursiveReferenceError,
    SymbolConflictWithNamespaceError,
)

if TYPE_CHECKING:
    from taihe.semantics.declarations import IfaceParentDecl, TypeRefDecl
    from taihe.semantics.types import Type


def analyze_semantics(pg: PackageGroup, diag: AbstractDiagnosticsManager):
    """Runs semantic analysis passes on the given package group."""
    _check_decl_confilct_with_namespace(pg, diag)
    _ResolveImportsPass(diag).handle_decl(pg)
    _CheckFieldNameCollisionErrorPass(diag).handle_decl(pg)
    _CalculateEnumItemValuePass(diag).handle_decl(pg)
    _CheckRecursiveInclusionPass(diag).handle_decl(pg)


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
    def visit_package(self, p: Package) -> None:
        self._current_pkg = p
        super().visit_package(p)
        self._current_pkg = None

    @override
    def visit_package_group(self, g: PackageGroup) -> None:
        self._current_pkg_group = g
        super().visit_package_group(g)
        self._current_pkg_group = None

    @override
    def visit_package_ref_decl(self, d: PackageRefDecl) -> None:
        if d.is_resolved:
            return
        d.is_resolved = True

        if (pkg := self.pkg_group.lookup(d.symbol)) is None:
            self.diag.emit(PackageNotExistError(d.symbol, loc=d.loc))
            return

        d.resolved_pkg = pkg
        return

    @override
    def visit_decl_ref_decl(self, d: DeclarationRefDecl) -> None:
        if d.is_resolved:
            return
        d.is_resolved = True

        self.handle_decl(d.pkg_ref)

        if (pkg := d.pkg_ref.resolved_pkg) is None:
            # No need to repeatedly throw exceptions
            return

        if (decl := pkg.decls.get(d.symbol)) is None:
            self.diag.emit(DeclNotExistError(d.symbol, loc=d.loc))
            return

        d.resolved_decl = decl
        return

    @override
    def visit_simple_type_ref_decl(self, d: SimpleTypeRefDecl) -> None:
        if d.is_resolved:
            return
        d.is_resolved = True

        if len(xs := d.symbol.rsplit(".", maxsplit=1)) == 2:
            pkg_name, decl_name = xs

            # Find the corresponding imported package according to the package name
            import_pkg = self.pkg.imports.get(pkg_name)

            if not isinstance(import_pkg, PackageImportDecl):
                self.diag.emit(PackageNotInScopeError(pkg_name, loc=d.loc))
                return

            # Then find the corresponding type declaration from the package
            if (pkg := import_pkg.pkg_ref.resolved_pkg) is None:
                # No need to repeatedly throw exceptions
                return

            if (decl := pkg.decls.get(decl_name)) is None:
                self.diag.emit(DeclNotExistError(decl_name, loc=d.loc))
                return

            if not isinstance(decl, TypeDecl):
                self.diag.emit(NotATypeError(decl_name, loc=d.loc))
                return

            d.resolved_ty = decl.as_type()
            return

        decl_name = xs[0]

        # Find Builtin Types
        if decl := BUILTIN_TYPES.get(decl_name):
            d.resolved_ty = decl
            return

        # Find types declared in the current package
        if decl := self.pkg.decls.get(decl_name):
            if not isinstance(decl, TypeDecl):
                self.diag.emit(NotATypeError(decl_name, loc=d.loc))
                return

            d.resolved_ty = decl.as_type()
            return

        # Look for imported type declarations
        import_decl = self.pkg.imports.get(decl_name)

        if isinstance(import_decl, DeclarationImportDecl):
            if (decl := import_decl.decl_ref.resolved_decl) is None:
                # No need to repeatedly throw exceptions
                return

            if not isinstance(decl, TypeDecl):
                self.diag.emit(NotATypeError(decl_name, loc=d.loc))
                return

            d.resolved_ty = decl.as_type()
            return

        # Fallback
        self.diag.emit(DeclarationNotInScopeError(decl_name, loc=d.loc))
        return

    @override
    def visit_generic_type_ref_decl(self, d: GenericTypeRefDecl) -> None:
        if d.is_resolved:
            return
        d.is_resolved = True

        super().visit_generic_type_ref_decl(d)

        args_ty: list[Type] = []
        for arg_ty_ref in d.args_ty_ref:
            if (arg_ty := arg_ty_ref.resolved_ty) is None:
                # No need to repeatedly throw exceptions
                return
            args_ty.append(arg_ty)

        decl_name = d.symbol

        if generic := BUILTIN_GENERICS.get(decl_name):
            try:
                d.resolved_ty = generic(*args_ty)
            except TypeError:
                self.diag.emit(GenericArgumentsError(d.unresolved_repr, loc=d.loc))
            return

        # Fallback
        self.diag.emit(DeclarationNotInScopeError(decl_name, loc=d.loc))
        return

    @override
    def visit_callback_type_ref_decl(self, d: CallbackTypeRefDecl) -> None:
        if d.is_resolved:
            return
        d.is_resolved = True

        super().visit_callback_type_ref_decl(d)

        if d.return_ty_ref:
            if (return_ty := d.return_ty_ref.resolved_ty) is None:
                # No need to repeatedly throw exceptions
                return
        else:
            return_ty = None

        params_ty: list[Type] = []
        for param in d.params:
            if (arg_ty := param.ty_ref.resolved_ty) is None:
                # No need to repeatedly throw exceptions
                return
            params_ty.append(arg_ty)

        d.resolved_ty = CallbackType(return_ty, tuple(params_ty))


class _CalculateEnumItemValuePass(DeclVisitor):
    """Calculate Enum Values."""

    diag: AbstractDiagnosticsManager

    def __init__(self, diag: AbstractDiagnosticsManager):
        self.diag = diag

    def visit_enum_decl(self, d: EnumDecl) -> None:
        values = {}
        value = 0
        for i in d.items:
            if i.value is None:
                i.value = value
            else:
                value = i.value
            if (prev := values.setdefault(value, i)) != i:
                self.diag.emit(EnumValueConflictError(prev, i))
            value += 1


class _CheckFieldNameCollisionErrorPass(DeclVisitor):
    """Check for duplicate field names in declarations and name anonymous declarations."""

    diag: AbstractDiagnosticsManager

    def __init__(self, diag: AbstractDiagnosticsManager):
        self.diag = diag

    @override
    def visit_glob_func_decl(self, d: GlobFuncDecl) -> None:
        self.check_collision_helper(d.params)
        return super().visit_glob_func_decl(d)

    @override
    def visit_iface_func_decl(self, d: IfaceMethodDecl) -> None:
        self.check_collision_helper(d.params)
        return super().visit_iface_func_decl(d)

    @override
    def visit_struct_decl(self, d: StructDecl) -> None:
        self.check_collision_helper(d.fields)
        return super().visit_struct_decl(d)

    @override
    def visit_enum_decl(self, d: EnumDecl) -> None:
        self.check_collision_helper(d.items)
        return super().visit_enum_decl(d)

    @override
    def visit_iface_decl(self, d: IfaceDecl) -> None:
        self.check_collision_helper(d.methods)
        return super().visit_iface_decl(d)

    @override
    def visit_package(self, p: Package) -> None:
        self.check_collision_helper(p.children)
        return super().visit_package(p)

    def check_collision_helper(self, children: Iterable[NamedDecl]):
        names = {}
        for f in children:
            assert f.name
            if (prev := names.setdefault(f.name, f)) != f:
                self.diag.emit(DeclRedefError(prev, f))


class _CheckRecursiveInclusionPass(DeclVisitor):
    """Validates struct fields for type correctness and cycles."""

    diag: AbstractDiagnosticsManager

    def __init__(self, diag: AbstractDiagnosticsManager):
        self.diag = diag
        self.type_table: dict[
            TypeDecl,
            list[tuple[tuple[TypeDecl, TypeRefDecl], TypeDecl]],
        ] = {}

    def visit_package_group(self, g: PackageGroup) -> None:
        self.type_table = {}
        super().visit_package_group(g)
        cycles = detect_cycles(self.type_table)
        for cycle in cycles:
            last, *other = cycle[::-1]
            self.diag.emit(RecursiveReferenceError(last, other))

    def visit_data_type_decl(self, d: TypeDecl) -> None:
        raise NotImplementedError()

    def visit_iface_decl(self, d: IfaceDecl) -> None:
        parent_iface_list = self.type_table.setdefault(d, [])
        parent_iface_dict: dict[IfaceDecl, IfaceParentDecl] = {}
        for parent in d.parents:
            if (parent_ty := parent.ty_ref.resolved_ty) is None:
                continue
            if not isinstance(parent_ty, UserType) or not isinstance(
                parent_iface := parent_ty.ty_decl, IfaceDecl
            ):
                self.diag.emit(ExtendsTypeError(parent, parent_ty))
                continue
            parent_iface_list.append(((d, parent.ty_ref), parent_iface))
            prev = parent_iface_dict.setdefault(parent_iface, parent)
            if prev != parent:
                self.diag.emit(
                    DuplicateExtendsWarn(
                        d,
                        parent_iface,
                        loc=parent.ty_ref.loc,
                        prev_loc=prev.ty_ref.loc,
                    )
                )

    def visit_struct_decl(self, d: StructDecl) -> None:
        type_list = self.type_table.setdefault(d, [])
        for f in d.fields:
            if isinstance(ty := f.ty_ref.resolved_ty, UserType) and isinstance(
                decl := ty.ty_decl, TypeDecl
            ):
                type_list.append(((d, f.ty_ref), decl))

    def visit_enum_decl(self, d: EnumDecl) -> None:
        type_list = self.type_table.setdefault(d, [])
        for i in d.items:
            if i.ty_ref is None:
                continue
            if isinstance(ty := i.ty_ref.resolved_ty, UserType) and isinstance(
                decl := ty.ty_decl, TypeDecl
            ):
                type_list.append(((d, i.ty_ref), decl))


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
