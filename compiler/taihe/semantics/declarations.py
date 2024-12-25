"""Defines the types for declarations."""

from abc import ABCMeta
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Protocol

from typing_extensions import override

from taihe.semantics.types import Type
from taihe.utils.exceptions import DeclRedefDiagError
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.visitor import DeclVisitor, TypeVisitor

################
# Declarations #
################


class Decl(Protocol):
    """Represents any declaration."""

    def _accept(self, v: "DeclVisitor") -> Any: ...


class NamedDecl(Decl, metaclass=ABCMeta):
    KIND: ClassVar[str]

    name: str
    parent: Optional["NamedDecl"] = None
    loc: Optional[SourceLocation]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        parent: Optional["NamedDecl"] = None,
    ):
        assert name
        self.name = name
        self.parent = parent
        self.loc = loc

    @property
    def description(self) -> str:
        """Describes the object in a human-friendly way."""
        return f"{self.KIND} {self.name!r}"

    @property
    def segments(self) -> list[str]:
        t = self
        segments: list[str] = []
        while True:
            if isinstance(t, Package):
                segments = [*t.name.split("."), *segments]
                return segments
            # All objects inherenting "Decl" must has "parent" as its field.
            segments = [t.name, *segments]
            t = t.parent
            assert t

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}<{self.name!r} in {self.parent}>"


class TypeRefDecl(Decl):
    """Repersents a reference to a `Type`.

    Each user of a `Type` must be encapsulated in a `TypeRefDecl`.
    Also, `TypeRefDecl` is NOT a `TypeDecl`.
    In other words, `TypeRefDecl` is a pointer, instead of a declaration.

    For example:
    ```
    struct Foo { ... }.     // `Foo` is a `TypeDecl`.

    fn func(foo: mut Foo);  // `mut Foo` is `TypeRefDecl(ty=TypeDecl('Foo'), qual=MUT)`.
    fn func(foo: BadType);  // `BadType` is `TypeRefDecl(ty=None)`.
    ```
    """

    symbol: str
    loc: Optional[SourceLocation]

    resolved_ty: Optional[Type]
    is_resolved: bool

    def __init__(
        self,
        symbol: str,
        loc: Optional[SourceLocation],
        resolved_ty: Optional[Type] = None,
    ):
        self.symbol = symbol
        self.loc = loc
        self.resolved_ty = resolved_ty
        self.is_resolved = resolved_ty is not None

    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_type_ref_decl(self)


#######################
# Import Declarations #
#######################


class ImportDecl(NamedDecl, metaclass=ABCMeta):
    """Represents a package or declaration import.

    Invariant: the `name` field in base class `Decl` always represents actual name of imports.

    For example:

    ```
    >>> use foo;
    PackageImportDecl(name='foo', pkg_ref=PackageRefDecl(name='foo'))
    >>> use foo as bar;
    PackageImportDecl(name='bar', pkg_ref=PackageRefDecl(name='foo'))
    >>> from foo use Bar;
    DeclarationImportDecl(
        name='Bar',
        decl_ref=DeclarationRefDecl(name='Bar', pkg_ref=PackageRefDecl(name='foo')),
    )
    >>> from foo use Bar as Baz;
    DeclarationImportDecl(
        name='Baz',
        decl_ref=DeclarationRefDecl(name='Bar', pkg_ref=PackageRefDecl(name='foo')),
    )
    ```
    """

    parent: Optional["Package"] = None


class PackageRefDecl(Decl):
    symbol: str
    loc: Optional[SourceLocation]

    is_resolved: bool
    resolved_pkg: Optional["Package"]

    def __init__(
        self,
        symbol: str,
        loc: Optional[SourceLocation],
    ):
        self.symbol = symbol
        self.loc = loc
        self.is_resolved = False
        self.resolved_pkg = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package_ref_decl(self)


class DeclarationRefDecl(Decl):
    symbol: str
    loc: Optional[SourceLocation]

    pkg_ref: PackageRefDecl

    is_resolved: bool
    resolved_decl: Optional["TypeDecl"]

    def __init__(
        self,
        symbol: str,
        loc: Optional[SourceLocation],
        pkg_ref: PackageRefDecl,
    ):
        self.symbol = symbol
        self.loc = loc
        self.pkg_ref = pkg_ref
        self.is_resolved = False
        self.resolved_decl = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_decl_ref_decl(self)

    @property
    def children(self) -> Iterable[Decl]:
        yield self.pkg_ref


class PackageImportDecl(ImportDecl):
    KIND = "package import"

    pkg_ref: PackageRefDecl

    def __init__(
        self,
        pkg_ref: PackageRefDecl,
        *,
        name: str = "",
        loc: Optional[SourceLocation] = None,
        **kwargs,
    ):
        super().__init__(
            name=name or pkg_ref.symbol,
            loc=loc or pkg_ref.loc,
            **kwargs,
        )
        self.pkg_ref = pkg_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package_import_decl(self)

    def is_alias(self) -> bool:
        return self.name != self.pkg_ref.symbol

    @property
    def children(self) -> Iterable[Decl]:
        yield self.pkg_ref


class DeclarationImportDecl(ImportDecl):
    KIND = "package declaration"

    decl_ref: DeclarationRefDecl

    def __init__(
        self,
        decl_ref: DeclarationRefDecl,
        *,
        name: str = "",
        loc: Optional[SourceLocation] = None,
        **kwargs,
    ):
        super().__init__(
            name=name or decl_ref.symbol,
            loc=loc or decl_ref.loc,
            **kwargs,
        )
        self.decl_ref = decl_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_decl_import_decl(self)

    def is_alias(self) -> bool:
        return self.name != self.decl_ref.symbol

    @property
    def children(self) -> Iterable[Decl]:
        yield self.decl_ref


######################
# Other Declarations #
######################


class ParamDecl(NamedDecl):
    KIND = "function parameter"

    ty_ref: TypeRefDecl
    parent: Optional["FuncBaseDecl"] = None

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
        **kwargs,
    ):
        super().__init__(name, loc, **kwargs)
        self.ty_ref = ty_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_param_decl(self)

    @property
    def children(self) -> Iterable[Decl]:
        yield self.ty_ref


class RetvalDecl(NamedDecl):
    KIND = "function return type"

    ty_ref: TypeRefDecl
    parent: Optional["FuncBaseDecl"] = None

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
        **kwargs,
    ):
        super().__init__(name, loc, **kwargs)
        self.ty_ref = ty_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_retval_decl(self)

    @property
    def children(self) -> Iterable[Decl]:
        yield self.ty_ref


class FuncBaseDecl(NamedDecl, metaclass=ABCMeta):
    params: list[ParamDecl]
    retvals: list[RetvalDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation], **kwargs):
        super().__init__(name, loc, **kwargs)
        self.params = []
        self.retvals = []

    @property
    def children(self) -> Iterable[NamedDecl]:
        yield from self.params
        yield from self.retvals

    def add_param(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
        **kwargs,
    ):
        p = ParamDecl(name, loc, ty_ref, parent=self, **kwargs)
        self.params.append(p)

    def add_retval(
        self,
        ty_ref: TypeRefDecl,
        **kwargs,
    ):
        name = f"_{len(self.retvals)}"
        r = RetvalDecl(name, ty_ref.loc, ty_ref, parent=self, **kwargs)
        self.retvals.append(r)


class PackageLevelDecl(NamedDecl, metaclass=ABCMeta):
    parent: Optional["Package"] = None


class FuncDecl(FuncBaseDecl, PackageLevelDecl):
    KIND = "function"

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_func_decl(self)


class TypeDecl(PackageLevelDecl, Type, metaclass=ABCMeta):
    pass


class TypeAliasDecl(TypeDecl):
    KIND = "type alias"

    ty_ref: TypeRefDecl
    final_ty: Optional[Type] = None
    is_solved: bool = False

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
        **kwargs,
    ):
        super().__init__(name, loc, **kwargs)
        self.ty_ref = ty_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_type_alias_decl(self)

    @property
    def children(self) -> Iterable[Decl]:
        yield self.ty_ref


class EnumItemDecl(NamedDecl):
    KIND = "enum item"

    parent: Optional["EnumDecl"] = None
    value: int

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        value: int,
        **kwargs,
    ):
        super().__init__(name, loc, **kwargs)
        self.value = value

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_enum_item_decl(self)


class EnumDecl(TypeDecl):
    KIND = "enum"

    items: list[EnumItemDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation], **kwargs):
        super().__init__(name, loc, **kwargs)
        self.items = []

    @override
    def _accept(self, v: "DeclVisitor | TypeVisitor") -> Any:
        return v.visit_enum_decl(self)

    @property
    def children(self) -> Iterable[NamedDecl]:
        yield from self.items

    def add_item(
        self,
        name: str,
        loc: Optional[SourceLocation],
        value: int,
        **kwargs,
    ):
        f = EnumItemDecl(name, loc, value, parent=self, **kwargs)
        self.items.append(f)


class StructFieldDecl(NamedDecl):
    KIND = "struct field"

    ty_ref: TypeRefDecl
    parent: Optional["StructDecl"] = None

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
        **kwargs,
    ):
        super().__init__(name, loc, **kwargs)
        self.ty_ref = ty_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_struct_field_decl(self)

    @property
    def children(self) -> Iterable[Decl]:
        yield self.ty_ref


class StructDecl(TypeDecl):
    KIND = "struct"

    fields: list[StructFieldDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation], **kwargs):
        super().__init__(name, loc, **kwargs)
        self.fields = []

    @override
    def _accept(self, v: "TypeVisitor | DeclVisitor") -> Any:
        return v.visit_struct_decl(self)

    @property
    def children(self) -> Iterable[NamedDecl]:
        yield from self.fields

    def add_field(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
        **kwargs,
    ):
        f = StructFieldDecl(name, loc, ty_ref, parent=self, **kwargs)
        self.fields.append(f)


class IfaceParentDecl(NamedDecl):
    KIND = "function return type"

    ty_ref: TypeRefDecl
    parent: Optional["IfaceDecl"] = None

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
        **kwargs,
    ):
        super().__init__(name, loc, **kwargs)
        self.ty_ref = ty_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_parent_decl(self)

    @property
    def children(self) -> Iterable[Decl]:
        yield self.ty_ref


class IfaceMethodDecl(FuncBaseDecl):
    KIND = "interface method"

    parent: Optional["IfaceDecl"] = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_method_decl(self)


class IfaceDecl(TypeDecl):
    KIND = "interface"

    methods: list[IfaceMethodDecl]
    parents: list[IfaceParentDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation], **kwargs):
        super().__init__(name, loc, **kwargs)
        self.methods = []
        self.parents = []

    @override
    def _accept(self, v: "TypeVisitor | DeclVisitor") -> Any:
        return v.visit_iface_decl(self)

    @property
    def children(self) -> Iterable[NamedDecl]:
        yield from self.methods
        yield from self.parents

    def add_method(self, f: IfaceMethodDecl):
        f.parent = self
        self.methods.append(f)

    def add_parent(
        self,
        ty_ref: TypeRefDecl,
        **kwargs,
    ):
        name = f"_{len(self.parents)}"
        p = IfaceParentDecl(name, ty_ref.loc, ty_ref, parent=self, **kwargs)
        self.parents.append(p)


######################
# The main container #
######################


class Package(NamedDecl):
    """A collection of named identities sharing the same scope."""

    KIND = "package"

    parent = None

    # Symbols
    imports: dict[str, ImportDecl]
    decls: dict[str, PackageLevelDecl]

    # Imports
    pkg_imports: list[PackageImportDecl]
    decl_imports: list[DeclarationImportDecl]

    # Things that the package contains.
    functions: list[FuncDecl]
    structs: list[StructDecl]
    enums: list[EnumDecl]
    interfaces: list[IfaceDecl]
    type_aliases: list[TypeAliasDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation]):
        super().__init__(name, loc, parent=None)

        self.imports = {}
        self.decls = {}

        self.pkg_imports = []
        self.decl_imports = []

        self.functions = []
        self.structs = []
        self.enums = []
        self.interfaces = []
        self.type_aliases = []

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}<{self.name!r}>"

    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package(self)

    @property
    def children(self) -> Iterable[NamedDecl]:
        yield from self.pkg_imports
        yield from self.decl_imports

        yield from self.functions
        yield from self.structs
        yield from self.enums
        yield from self.interfaces
        yield from self.type_aliases

    def _register_to_decl(self, d: PackageLevelDecl):
        if prev := self.decls.get(d.name, None):
            raise DeclRedefDiagError(prev, d)
        else:
            self.decls[d.name] = d

    def add_function(self, f: FuncDecl):
        f.parent = self
        self.functions.append(f)
        self._register_to_decl(f)

    def add_struct(self, s: StructDecl):
        s.parent = self
        self.structs.append(s)
        self._register_to_decl(s)

    def add_enum(self, e: EnumDecl):
        e.parent = self
        self.enums.append(e)
        self._register_to_decl(e)

    def add_interface(self, i: IfaceDecl):
        i.parent = self
        self.interfaces.append(i)
        self._register_to_decl(i)

    def add_type_alias(self, d: TypeAliasDecl):
        d.parent = self
        self.type_aliases.append(d)
        self._register_to_decl(d)

    def add_declaration(self, d: PackageLevelDecl):
        if isinstance(d, FuncDecl):
            self.add_function(d)
        elif isinstance(d, StructDecl):
            self.add_struct(d)
        elif isinstance(d, EnumDecl):
            self.add_enum(d)
        elif isinstance(d, IfaceDecl):
            self.add_interface(d)
        elif isinstance(d, TypeAliasDecl):
            self.add_type_alias(d)
        else:
            raise NotImplementedError(f"unexpected declaration {d.description}")

    def _register_to_import(self, i: ImportDecl):
        if prev := self.imports.get(i.name, None):
            raise DeclRedefDiagError(prev, i)
        else:
            self.imports[i.name] = i

    def add_decl_import(self, i: DeclarationImportDecl):
        i.parent = self
        self.decl_imports.append(i)
        self._register_to_import(i)

    def add_pkg_import(self, i: PackageImportDecl):
        i.parent = self
        self.pkg_imports.append(i)
        self._register_to_import(i)

    def add_import(self, i: ImportDecl):
        if isinstance(i, DeclarationImportDecl):
            self.add_decl_import(i)
        elif isinstance(i, PackageImportDecl):
            self.add_pkg_import(i)
        else:
            raise NotImplementedError(f"unexpected import {i.description}")


class PackageGroup(Decl):
    """Stores all known packages for a compilation instance."""

    package_dict: dict[str, Package]

    def __init__(self):
        self.package_dict = {}

    def _accept(self, v: "DeclVisitor"):
        return v.visit_package_group(self)

    @property
    def children(self) -> Iterable[NamedDecl]:
        yield from self.packages

    def lookup(self, name: str) -> Optional["Package"]:
        return self.package_dict.get(name, None)

    def add(self, pkg: Package):
        assert pkg.name not in self.package_dict
        self.package_dict[pkg.name] = pkg

    @property
    def packages(self) -> Iterable[Package]:
        return self.package_dict.values()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({', '.join(repr(x) for x in self.package_dict)})"
