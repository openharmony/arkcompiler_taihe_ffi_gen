from collections.abc import Callable
from itertools import chain
from typing import Any, TypeGuard, TypeVar

from typing_extensions import override

from taihe.semantics.attributes import AttributeRegistry, UncheckedAttribute
from taihe.semantics.declarations import (
    CallbackTypeRefDecl,
    Decl,
    DeclarationRefDecl,
    EnumDecl,
    ExplicitTypeRefDecl,
    GenericArgDecl,
    GenericTypeRefDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    IfaceParentDecl,
    LongTypeRefDecl,
    PackageDecl,
    PackageGroup,
    PackageRefDecl,
    ParamDecl,
    ShortTypeRefDecl,
    StructDecl,
    StructFieldDecl,
    TypeDecl,
    TypeRefDecl,
    UnionDecl,
    UnionFieldDecl,
)
from taihe.semantics.types import (
    BUILTIN_GENERICS,
    BUILTIN_TYPES,
    CallbackType,
    IfaceType,
    NonVoidType,
    ScalarKind,
    ScalarType,
    StringType,
    Type,
    UserType,
    VoidType,
)
from taihe.semantics.visitor import DeclVisitor, RecursiveDeclVisitor
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import (
    DeclarationNotInScopeError,
    DeclNotExistError,
    DuplicateExtendsWarn,
    EnumValueError,
    NotATypeError,
    PackageNotExistError,
    PackageNotInScopeError,
    RecursiveReferenceError,
    SymbolConflictWithNamespaceError,
    TypeUsageError,
)


def analyze_semantics(
    pg: PackageGroup,
    dm: DiagnosticsManager,
    am: AttributeRegistry,
):
    """Runs semantic analysis passes on the given package group."""
    _check_decl_confilct_with_namespace(pg, dm)
    _ResolveImportsPass(dm).handle_decl(pg)
    _ResolveTypePass(dm).handle_decl(pg)
    _CheckEnumTypePass(dm).handle_decl(pg)
    _CheckRecursiveInclusionPass(dm).handle_decl(pg)

    if dm.has_error:
        return

    _ConvertAttrPass(dm, am).handle_decl(pg)
    _CheckAttrPass(dm).handle_decl(pg)


def _check_decl_confilct_with_namespace(
    pg: PackageGroup,
    dm: DiagnosticsManager,
):
    """Checks for declarations conflicts with namespaces."""
    namespaces: dict[str, list[PackageDecl]] = {}
    for pkg in pg.packages:
        pkg_name = pkg.name
        # package "a.b.c" -> namespaces ["a.b.c", "a.b", "a"]
        while True:
            namespaces.setdefault(pkg_name, []).append(pkg)
            splited = pkg_name.rsplit(".", maxsplit=1)
            if len(splited) == 2:
                pkg_name = splited[0]
            else:
                break

    for p in pg.packages:
        for d in p.declarations:
            name = p.name + "." + d.name
            if packages := namespaces.get(name, []):
                dm.emit(SymbolConflictWithNamespaceError(d, name, packages))


class _ResolveImportsPass(RecursiveDeclVisitor):
    """Resolves imports and type references within a package group."""

    dm: DiagnosticsManager

    def __init__(self, dm: DiagnosticsManager):
        self._curr_pg = None
        self.dm = dm

    @property
    def curr_pg(self) -> PackageGroup:
        assert self._curr_pg
        return self._curr_pg

    @override
    def visit_package_group(self, g: PackageGroup) -> None:
        self._curr_pg = g
        try:
            super().visit_package_group(g)
        finally:
            self._curr_pg = None

    @override
    def visit_package_ref_decl(self, d: PackageRefDecl) -> None:
        if d.is_resolved:
            return
        d.is_resolved = True

        super().visit_package_ref_decl(d)

        pkg = self.curr_pg.lookup(d.symbol)

        if pkg is not None:
            d.resolved_pkg = pkg
            return

        self.dm.emit(PackageNotExistError(d.symbol, loc=d.loc))
        d.resolved_pkg = None
        return

    @override
    def visit_declaration_ref_decl(self, d: DeclarationRefDecl) -> None:
        if d.is_resolved:
            return
        d.is_resolved = True

        super().visit_declaration_ref_decl(d)

        pkg = d.pkg_ref.resolved_pkg

        if pkg is not None:
            decl = pkg.lookup(d.symbol)

            if decl is not None:
                d.resolved_decl = decl
                return

            self.dm.emit(DeclNotExistError(d.symbol, loc=d.loc))
            d.resolved_decl = None
            return

        # No need to repeatedly throw exceptions
        d.resolved_decl = None
        return


T = TypeVar("T", bound=Type)


class _ResolveTypePass(RecursiveDeclVisitor):
    """Resolves type references within a package group."""

    dm: DiagnosticsManager

    def __init__(self, dm: DiagnosticsManager):
        self._curr_pkg = None
        self.dm = dm

    @property
    def curr_pkg(self) -> PackageDecl:
        assert self._curr_pkg
        return self._curr_pkg

    @override
    def visit_package_decl(self, p: PackageDecl) -> None:
        self._curr_pkg = p
        try:
            super().visit_package_decl(p)
        finally:
            self._curr_pkg = None

    @override
    def visit_param_decl(self, d: ParamDecl) -> None:
        super().visit_param_decl(d)
        d.resolve_ty(self.resolve_type(d.ty_ref, NonVoidType))

    @override
    def visit_generic_arg_decl(self, d: GenericArgDecl) -> None:
        super().visit_generic_arg_decl(d)
        d.resolve_ty(self.resolve_type(d.ty_ref, Type))

    @override
    def visit_callback_type_ref_decl(self, d: CallbackTypeRefDecl) -> None:
        super().visit_callback_type_ref_decl(d)
        d.resolve_return_ty(self.resolve_type(d.return_ty_ref, Type))

    @override
    def visit_glob_func_decl(self, d: GlobFuncDecl) -> None:
        super().visit_glob_func_decl(d)
        if not isinstance(d.return_ty_ref, ExplicitTypeRefDecl):
            d.resolve_return_ty(VoidType(d.return_ty_ref))
        else:
            d.resolve_return_ty(self.resolve_type(d.return_ty_ref, Type))

    @override
    def visit_iface_func_decl(self, d: IfaceMethodDecl) -> None:
        super().visit_iface_func_decl(d)
        if not isinstance(d.return_ty_ref, ExplicitTypeRefDecl):
            d.resolve_return_ty(VoidType(d.return_ty_ref))
        else:
            d.resolve_return_ty(self.resolve_type(d.return_ty_ref, Type))

    @override
    def visit_union_field_decl(self, d: UnionFieldDecl) -> None:
        super().visit_union_field_decl(d)
        if not isinstance(d.ty_ref, ExplicitTypeRefDecl):
            d.resolve_ty(VoidType(d.ty_ref))
        else:
            d.resolve_ty(self.resolve_type(d.ty_ref, Type))

    @override
    def visit_struct_field_decl(self, d: StructFieldDecl) -> None:
        super().visit_struct_field_decl(d)
        d.resolve_ty(self.resolve_type(d.ty_ref, NonVoidType))

    @override
    def visit_iface_parent_decl(self, d: IfaceParentDecl) -> None:
        super().visit_iface_parent_decl(d)
        d.resolve_ty(self.resolve_type(d.ty_ref, IfaceType))

    @override
    def visit_enum_decl(self, d: EnumDecl) -> None:
        super().visit_enum_decl(d)
        d.resolve_ty(self.resolve_type(d.ty_ref, ScalarType, StringType))

    def resolve_type(
        self,
        ty_ref: ExplicitTypeRefDecl,
        *target: type[T],
    ) -> T | None:
        ty = _TypeResolver(self.dm, self.curr_pkg).handle_decl(ty_ref)
        if ty is None:
            return None
        if isinstance(ty, target):
            return ty
        self.dm.emit(TypeUsageError(ty_ref, ty))
        return None


class _TypeResolver(DeclVisitor[Type | None]):
    """A visitor that resolves types in declarations."""

    dm: DiagnosticsManager

    def __init__(
        self,
        dm: DiagnosticsManager,
        curr_pkg: PackageDecl,
    ):
        self.dm = dm
        self.curr_pkg = curr_pkg

    @override
    def visit_long_type_ref_decl(self, d: LongTypeRefDecl) -> Type | None:
        # Look for imported package declarations
        pkg_import = self.curr_pkg.lookup_pkg_import(d.pkname)

        if pkg_import is not None:
            pkg = pkg_import.pkg_ref.resolved_pkg

            if pkg is not None:
                decl = pkg.lookup(d.symbol)

                if decl is not None:
                    if isinstance(decl, TypeDecl):
                        return decl.as_type(d)

                    self.dm.emit(NotATypeError(d.symbol, loc=d.loc))
                    return None

                self.dm.emit(DeclNotExistError(d.symbol, loc=d.loc))
                return None

            # No need to repeatedly throw exceptions
            return None

        self.dm.emit(PackageNotInScopeError(d.pkname, loc=d.loc))
        return None

    @override
    def visit_short_type_ref_decl(self, d: ShortTypeRefDecl) -> Type | None:
        # Find Builtin Types
        builtin_type = BUILTIN_TYPES.get(d.symbol)

        if builtin_type is not None:
            return builtin_type(d)

        # Find types declared in the current package
        decl = self.curr_pkg.lookup(d.symbol)

        if decl is not None:
            if isinstance(decl, TypeDecl):
                return decl.as_type(d)

            self.dm.emit(NotATypeError(d.symbol, loc=d.loc))
            return None

        # Look for imported type declarations
        decl_import = self.curr_pkg.lookup_decl_import(d.symbol)

        if decl_import is not None:
            decl = decl_import.decl_ref.resolved_decl

            if decl is not None:
                if isinstance(decl, TypeDecl):
                    return decl.as_type(d)

                self.dm.emit(NotATypeError(d.symbol, loc=d.loc))
                return None

            # No need to repeatedly throw exceptions
            return None

        self.dm.emit(DeclarationNotInScopeError(d.symbol, loc=d.loc))
        return None

    @override
    def visit_generic_type_ref_decl(self, d: GenericTypeRefDecl) -> Type | None:
        # Find Builtin Generics
        builtin_generic = BUILTIN_GENERICS.get(d.symbol)

        if builtin_generic is not None:
            args: list[GenericArgDecl] = []
            for arg in d.args:
                if arg.ty_resolved is None:
                    return None
                args.append(arg)

            return builtin_generic.try_construct(d, *args, dm=self.dm)

        self.dm.emit(DeclarationNotInScopeError(d.symbol, loc=d.loc))
        return None

    @override
    def visit_callback_type_ref_decl(self, d: CallbackTypeRefDecl) -> Type | None:
        for param in d.params:
            if param.ty_resolved is None:
                return None
        if d.return_ty_resolved is None:
            return None
        return CallbackType(d)


class _CheckEnumTypePass(RecursiveDeclVisitor):
    """Validated enum item types."""

    dm: DiagnosticsManager

    def __init__(self, dm: DiagnosticsManager):
        self.dm = dm

    def visit_enum_decl(self, d: EnumDecl) -> None:
        if d.ty_resolved is None:
            return

        if isinstance(d.ty_resolved, StringType):
            for item in d.items:
                if item.value is None:
                    item.value = item.name
                elif not isinstance(item.value, str):
                    self.dm.emit(EnumValueError(item, d))
                    item.value = item.name
            return

        def is_int(val: Any) -> TypeGuard[int]:
            return not isinstance(val, bool) and isinstance(val, int)

        default: Any
        deduce: Callable[[Any], Any]
        is_valid: Callable[[Any], bool]

        match d.ty_resolved.kind:
            case ScalarKind.I8:
                default = 0
                deduce = lambda prev: prev + 1 if prev + 1 < 2**7 else -(2**7)
                is_valid = lambda val: is_int(val) and -(2**7) <= val < 2**7
            case ScalarKind.I16:
                default = 0
                deduce = lambda prev: prev + 1 if prev + 1 < 2**15 else -(2**15)
                is_valid = lambda val: is_int(val) and -(2**15) <= val < 2**15
            case ScalarKind.I32:
                default = 0
                deduce = lambda prev: prev + 1 if prev + 1 < 2**31 else -(2**31)
                is_valid = lambda val: is_int(val) and -(2**31) <= val < 2**31
            case ScalarKind.I64:
                default = 0
                deduce = lambda prev: prev + 1 if prev + 1 < 2**63 else -(2**63)
                is_valid = lambda val: is_int(val) and -(2**63) <= val < 2**63
            case ScalarKind.U8:
                default = 0
                deduce = lambda prev: prev + 1 if prev + 1 < 2**8 else 0
                is_valid = lambda val: is_int(val) and 0 <= val < 2**8
            case ScalarKind.U16:
                default = 0
                deduce = lambda prev: prev + 1 if prev + 1 < 2**16 else 0
                is_valid = lambda val: is_int(val) and 0 <= val < 2**16
            case ScalarKind.U32:
                default = 0
                deduce = lambda prev: prev + 1 if prev + 1 < 2**32 else 0
                is_valid = lambda val: is_int(val) and 0 <= val < 2**32
            case ScalarKind.U64:
                default = 0
                deduce = lambda prev: prev + 1 if prev + 1 < 2**64 else 0
                is_valid = lambda val: is_int(val) and 0 <= val < 2**64
            case ScalarKind.BOOL:
                default = False
                deduce = lambda prev: False
                is_valid = lambda val: isinstance(val, bool)
            case ScalarKind.F32:
                default = 0.0
                deduce = lambda prev: 0.0
                is_valid = lambda val: isinstance(val, float)
            case ScalarKind.F64:
                default = 0.0
                deduce = lambda prev: 0.0
                is_valid = lambda val: isinstance(val, float)

        prev = None
        for item in d.items:
            if item.value is None:
                item.value = default if prev is None else deduce(prev)
            elif not is_valid(item.value):
                self.dm.emit(EnumValueError(item, d))
                item.value = default
            prev = item.value


class _CheckRecursiveInclusionPass(RecursiveDeclVisitor):
    """Validates struct fields for type correctness and cycles."""

    dm: DiagnosticsManager

    def __init__(self, dm: DiagnosticsManager):
        self.dm = dm
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
            self.dm.emit(RecursiveReferenceError(last, other))

    def visit_enum_decl(self, d: EnumDecl) -> None:
        self.type_table[d] = []

    def visit_iface_decl(self, d: IfaceDecl) -> None:
        parent_iface_list = self.type_table.setdefault(d, [])
        parent_iface_dict: dict[IfaceDecl, IfaceParentDecl] = {}
        for parent in d.parents:
            if (parent_ty := parent.ty_resolved) is None:
                continue
            parent_iface = parent_ty.ty_decl
            parent_iface_list.append(((d, parent.ty_ref), parent_iface))
            prev = parent_iface_dict.setdefault(parent_iface, parent)
            if prev != parent:
                self.dm.emit(DuplicateExtendsWarn(prev, parent, d, parent_iface))

    def visit_struct_decl(self, d: StructDecl) -> None:
        type_list = self.type_table.setdefault(d, [])
        for f in d.fields:
            if isinstance(ty := f.ty_resolved, UserType):
                type_list.append(((d, f.ty_ref), ty.ty_decl))

    def visit_union_decl(self, d: UnionDecl) -> None:
        type_list = self.type_table.setdefault(d, [])
        for i in d.fields:
            if isinstance(ty := i.ty_resolved, UserType):
                type_list.append(((d, i.ty_ref), ty.ty_decl))


class _ConvertAttrPass(RecursiveDeclVisitor):
    dm: DiagnosticsManager
    am: AttributeRegistry

    def __init__(self, dm: DiagnosticsManager, am: AttributeRegistry):
        self.dm = dm
        self.am = am

    def visit_decl(self, d: Decl) -> None:
        for unchecked_attr in UncheckedAttribute.consume(d):
            if (checked_attr := self.am.attach(unchecked_attr, self.dm)) is not None:
                d.add_attribute(checked_attr)


class _CheckAttrPass(RecursiveDeclVisitor):
    dm: DiagnosticsManager

    def __init__(self, dm: DiagnosticsManager):
        self.dm = dm

    def visit_decl(self, d: Decl) -> None:
        for attr in chain(*d.attributes.values()):
            attr.check_context(d, self.dm)


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
