"""Defines the types for declarations."""

from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Protocol

from typing_extensions import override

from taihe.semantics.types import (
    EnumType,
    IfaceType,
    StructType,
    Type,
    UserType,
)
from taihe.utils.exceptions import AttrRedefError, DeclRedefError
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.visitor import DeclVisitor

################
# Declarations #
################


class DeclProtocol(Protocol):
    def _accept(self, v: "DeclVisitor") -> Any: ...


class Decl(DeclProtocol, metaclass=ABCMeta):
    """Represents any declaration."""

    attrs: dict[str, "AttrItemDecl"]

    def __init__(self):
        self.attrs = {}

    def add_attr(self, i: "AttrItemDecl"):
        i.node_parent = self
        if prev := self.attrs.get(i.name, None):
            raise AttrRedefError(prev, i)
        self.attrs[i.name] = i


class NamedDecl(Decl, metaclass=ABCMeta):
    """Represents a declaration with a unique semantic identity within a PackageGroup symbol tree.

    A `NamedDecl` is defined as any declaration that:
    1. Exists as a meaningful entity in the symbol tree of a `PackageGroup`.
    2. Has a fully qualified name that allows it to be uniquely identified by traversing the symbol
       tree.

    Examples:
    - Given the file `example.package.x` containing the declaration:
      ```
      @[info = "xxx"]
      struct A {
          name: example.package.y.B;
      }
      ```
      - `StructDecl("A")` is a `NamedDecl` because it corresponds to `example.package.x.A`.
      - `StructFieldDecl("name")` is a `NamedDecl` because it corresponds to
        `example.package.x.A.name`.
      - `AttrItemDecl("info")` is **not** a `NamedDecl` because it does not correspond to
        `example.package.x.A.info`.
      - `TypeRefDecl("example.package.y.B")` is **not** a `NamedDecl` because it does not correspond
        to `example.package.x.A.example.package.y.B`.

    By adhering to the rules, `NamedDecl` ensures that all identified declarations are semantically
    meaningful and uniquely resolvable within the hierarchical structure of the symbol tree.
    """

    KIND: ClassVar[str]

    name: str
    loc: Optional[SourceLocation]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
    ):
        super().__init__()
        self.name = name
        self.loc = loc

    @property
    def description(self) -> str:
        """Describes the object in a human-friendly way."""
        return f"{self.KIND} {self.name!r}"

    def __repr__(self) -> str:
        return f"<{self.description} at {self.loc}>"


#############
# Attribute #
#############


class AttrItemDecl(Decl):
    name: str
    loc: Optional[SourceLocation]

    value: bool | int | str | None
    node_parent: Optional[Decl]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        value: bool | int | str | None = None,
    ):
        super().__init__()
        self.name = name
        self.loc = loc
        self.value = value
        self.node_parent = None

    def __repr__(self) -> str:
        return f"<attribute {self.name} of {self.node_parent} at {self.loc}>"

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_attr_item_decl(self)


###################
# Type References #
###################


class TypeRefDecl(Decl, metaclass=ABCMeta):
    """Repersents a reference to a `Type`.

    Each user of a `Type` must be encapsulated in a `TypeRefDecl`.
    Also, `TypeRefDecl` is NOT a `TypeDecl`.
    In other words, `TypeRefDecl` is a pointer, instead of a declaration.

    For example:
    ```
    struct Foo { ... }      // `Foo` is a `TypeDecl`.

    fn func(foo: Foo);      // `Foo` is `TypeRefDecl(ty=UserType(ty_decl=TypeDecl('Foo')))`.
    fn func(foo: BadType);  // `BadType` is `TypeRefDecl(ty=None)`.
    ```
    """

    loc: Optional[SourceLocation]

    resolved_ty: Optional[Type]
    is_resolved: bool

    def __init__(
        self,
        loc: Optional[SourceLocation],
        resolved_ty: Optional[Type] = None,
    ):
        super().__init__()
        self.loc = loc
        self.resolved_ty = resolved_ty
        self.is_resolved = resolved_ty is not None

    @property
    @abstractmethod
    def unresolved_name(self) -> str: ...

    def __repr__(self) -> str:
        return f"<type reference {self.unresolved_name} at {self.loc}>"


class SimpleTypeRefDecl(TypeRefDecl):
    symbol: str

    def __init__(
        self,
        symbol: str,
        loc: Optional[SourceLocation],
        resolved_ty: Optional[Type] = None,
    ):
        super().__init__(loc, resolved_ty)
        self.symbol = symbol

    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_simple_type_ref_decl(self)

    @property
    @override
    def unresolved_name(self):
        return self.symbol


class GenericTypeRefDecl(TypeRefDecl):
    symbol: str
    args_ty_ref: list[TypeRefDecl]

    def __init__(
        self,
        symbol: str,
        loc: Optional[SourceLocation],
        args_ty_ref: list[TypeRefDecl],
        resolved_ty: Optional[Type] = None,
    ):
        super().__init__(loc, resolved_ty)
        self.symbol = symbol
        self.args_ty_ref = args_ty_ref

    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_generic_type_ref_decl(self)

    @property
    @override
    def unresolved_name(self):
        args_fmt = ", ".join(arg.unresolved_name for arg in self.args_ty_ref)
        return f"{self.symbol}<{args_fmt}>"


#####################
# Import References #
#####################


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
        super().__init__()
        self.symbol = symbol
        self.loc = loc
        self.is_resolved = False
        self.resolved_pkg = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package_ref_decl(self)

    def __repr__(self) -> str:
        return f"<package reference {self.symbol} at {self.loc}>"


class DeclarationRefDecl(Decl):
    symbol: str
    loc: Optional[SourceLocation]

    pkg_ref: PackageRefDecl

    is_resolved: bool
    resolved_decl: Optional["PackageLevelDecl"]

    def __init__(
        self,
        symbol: str,
        loc: Optional[SourceLocation],
        pkg_ref: PackageRefDecl,
    ):
        super().__init__()
        self.symbol = symbol
        self.loc = loc
        self.pkg_ref = pkg_ref
        self.is_resolved = False
        self.resolved_decl = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_decl_ref_decl(self)

    def __repr__(self) -> str:
        return f"<declaration reference {self.symbol} at {self.loc}>"


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

    node_parent: Optional["Package"] = None


class PackageImportDecl(ImportDecl):
    KIND = "package import"

    pkg_ref: PackageRefDecl

    def __init__(
        self,
        pkg_ref: PackageRefDecl,
        *,
        name: str = "",
        loc: Optional[SourceLocation] = None,
    ):
        super().__init__(
            name=name or pkg_ref.symbol,
            loc=loc or pkg_ref.loc,
        )
        self.pkg_ref = pkg_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package_import_decl(self)

    def is_alias(self) -> bool:
        return self.name != self.pkg_ref.symbol


class DeclarationImportDecl(ImportDecl):
    KIND = "package declaration"

    decl_ref: DeclarationRefDecl

    def __init__(
        self,
        decl_ref: DeclarationRefDecl,
        *,
        name: str = "",
        loc: Optional[SourceLocation] = None,
    ):
        super().__init__(
            name=name or decl_ref.symbol,
            loc=loc or decl_ref.loc,
        )
        self.decl_ref = decl_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_decl_import_decl(self)

    def is_alias(self) -> bool:
        return self.name != self.decl_ref.symbol


######################
# Other Declarations #
######################


class PackageLevelDecl(NamedDecl, metaclass=ABCMeta):
    node_parent: Optional["Package"] = None


class ParamDecl(NamedDecl):
    KIND = "function parameter"

    ty_ref: TypeRefDecl
    node_parent: Optional["BaseFuncDecl"]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
    ):
        super().__init__(name, loc)
        self.ty_ref = ty_ref
        self.node_parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_param_decl(self)


class BaseFuncDecl(NamedDecl, metaclass=ABCMeta):
    params: list[ParamDecl]
    return_ty_ref: Optional[TypeRefDecl]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        return_ty_ref: Optional[TypeRefDecl] = None,
    ):
        super().__init__(name, loc)
        self.params = []
        self.return_ty_ref = return_ty_ref

    def add_param(self, p: ParamDecl):
        p.node_parent = self
        self.params.append(p)


class GlobFuncDecl(BaseFuncDecl, PackageLevelDecl):
    KIND = "non-member function"

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_glob_func_decl(self)


#####################
# Type Declarations #
#####################


class TypeDecl(PackageLevelDecl, metaclass=ABCMeta):
    @abstractmethod
    def as_type(self) -> UserType: ...


class EnumItemDecl(NamedDecl):
    KIND = "enum item"

    ty_ref: Optional[TypeRefDecl]
    value: Optional[int]
    node_parent: Optional["EnumDecl"]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: Optional[TypeRefDecl] = None,
        value: Optional[int] = None,
    ):
        super().__init__(name, loc)
        self.ty_ref = ty_ref
        self.value = value
        self.node_parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_enum_item_decl(self)


class EnumDecl(TypeDecl):
    KIND = "enum"

    items: list[EnumItemDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation]):
        super().__init__(name, loc)
        self.items = []

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_enum_decl(self)

    def add_item(self, f: EnumItemDecl):
        f.node_parent = self
        self.items.append(f)

    @override
    def as_type(self) -> UserType:
        return EnumType(self)


class StructFieldDecl(NamedDecl):
    KIND = "struct field"

    ty_ref: TypeRefDecl
    node_parent: Optional["StructDecl"]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
    ):
        super().__init__(name, loc)
        self.ty_ref = ty_ref
        self.node_parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_struct_field_decl(self)


class StructDecl(TypeDecl):
    KIND = "struct"

    fields: list[StructFieldDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation]):
        super().__init__(name, loc)
        self.fields = []

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_struct_decl(self)

    def add_field(self, f: StructFieldDecl):
        f.node_parent = self
        self.fields.append(f)

    @override
    def as_type(self) -> UserType:
        return StructType(self)


class IfaceParentDecl(NamedDecl):
    KIND = "function return type"

    ty_ref: TypeRefDecl
    node_parent: Optional["IfaceDecl"]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
    ):
        super().__init__(name, loc)
        self.ty_ref = ty_ref
        self.node_parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_parent_decl(self)


class IfaceMethodDecl(BaseFuncDecl):
    KIND = "interface method"

    node_parent: Optional["IfaceDecl"] = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_func_decl(self)


class IfaceDecl(TypeDecl):
    KIND = "interface"

    methods: list[IfaceMethodDecl]
    parents: list[IfaceParentDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation]):
        super().__init__(name, loc)
        self.methods = []
        self.parents = []

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_decl(self)

    def add_method(self, f: IfaceMethodDecl):
        f.node_parent = self
        self.methods.append(f)

    def add_parent(self, p: IfaceParentDecl):
        p.node_parent = self
        self.parents.append(p)

    @override
    def as_type(self) -> UserType:
        return IfaceType(self)


######################
# The main container #
######################


class Package(NamedDecl):
    """A collection of named identities sharing the same scope."""

    KIND = "package"

    # Symbols
    imports: dict[str, ImportDecl]
    decls: dict[str, PackageLevelDecl]

    # Imports
    pkg_imports: list[PackageImportDecl]
    decl_imports: list[DeclarationImportDecl]

    # Things that the package contains.
    functions: list[GlobFuncDecl]
    structs: list[StructDecl]
    enums: list[EnumDecl]
    interfaces: list[IfaceDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation]):
        super().__init__(name, loc)

        self.imports = {}
        self.decls = {}

        self.pkg_imports = []
        self.decl_imports = []

        self.functions = []
        self.structs = []
        self.enums = []
        self.interfaces = []

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}<{self.name!r}>"

    @property
    def segments(self) -> list[str]:
        return self.name.split(".")

    @property
    def children(self) -> Iterable[NamedDecl]:
        yield from self.pkg_imports
        yield from self.decl_imports

        yield from self.functions
        yield from self.structs
        yield from self.enums
        yield from self.interfaces

    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package(self)

    def _register_to_decl(self, d: PackageLevelDecl):
        if prev := self.decls.get(d.name, None):
            raise DeclRedefError(prev, d)
        self.decls[d.name] = d

    def add_function(self, f: GlobFuncDecl):
        f.node_parent = self
        self.functions.append(f)
        self._register_to_decl(f)

    def add_struct(self, s: StructDecl):
        s.node_parent = self
        self.structs.append(s)
        self._register_to_decl(s)

    def add_enum(self, e: EnumDecl):
        e.node_parent = self
        self.enums.append(e)
        self._register_to_decl(e)

    def add_interface(self, i: IfaceDecl):
        i.node_parent = self
        self.interfaces.append(i)
        self._register_to_decl(i)

    def add_declaration(self, d: PackageLevelDecl):
        if isinstance(d, GlobFuncDecl):
            self.add_function(d)
        elif isinstance(d, StructDecl):
            self.add_struct(d)
        elif isinstance(d, EnumDecl):
            self.add_enum(d)
        elif isinstance(d, IfaceDecl):
            self.add_interface(d)
        else:
            raise NotImplementedError(f"unexpected declaration {d.description}")

    def _register_to_import(self, i: ImportDecl):
        if prev := self.imports.get(i.name, None):
            raise DeclRedefError(prev, i)
        self.imports[i.name] = i

    def add_decl_import(self, i: DeclarationImportDecl):
        i.node_parent = self
        self.decl_imports.append(i)
        self._register_to_import(i)

    def add_pkg_import(self, i: PackageImportDecl):
        i.node_parent = self
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
        super().__init__()
        self.package_dict = {}

    def _accept(self, v: "DeclVisitor"):
        return v.visit_package_group(self)

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
