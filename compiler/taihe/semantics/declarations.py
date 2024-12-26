"""Defines the types for declarations."""

from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Protocol

from typing_extensions import override

from taihe.semantics.types import Type
from taihe.utils.exceptions import AttrRedefDiagError, DeclRedefDiagError
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.visitor import DeclVisitor, TypeVisitor

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
        i.parent = self
        if prev := self.attrs.get(i.name, None):
            raise AttrRedefDiagError(prev, i)
        else:
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

    @property
    @abstractmethod
    def segments(self) -> list[str]: ...

    @property
    @abstractmethod
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]: ...

    def __repr__(self) -> str:
        return f"<{self.description} at {self.loc}>"


#############
# Attribute #
#############


class AttrItemDecl(Decl):
    name: str
    loc: Optional[SourceLocation]

    value: bool | int | str | None
    parent: Optional[Decl]

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
        self.parent = None

    @property
    def description(self) -> str:
        """Describes the object in a human-friendly way."""
        return f"attribute {self.name!r}"

    def __repr__(self) -> str:
        return f"<{self.description} of {self.parent} at {self.loc}>"

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_attr_item_decl(self)


##############
# References #
##############


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
        super().__init__()
        self.symbol = symbol
        self.loc = loc
        self.resolved_ty = resolved_ty
        self.is_resolved = resolved_ty is not None

    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_type_ref_decl(self)

    def __repr__(self) -> str:
        return f"<type reference {self.symbol} at {self.loc}>"


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
    resolved_decl: Optional["TypeDecl"]

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

    parent: Optional["Package"] = None

    @property
    @override
    def segments(self) -> list[str]:
        assert self.parent
        return [*self.parent.segments, self.name]


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

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {}

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

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {}

    def is_alias(self) -> bool:
        return self.name != self.decl_ref.symbol


######################
# Other Declarations #
######################


class PackageLevelDecl(NamedDecl, metaclass=ABCMeta):
    parent: Optional["Package"] = None

    @property
    @override
    def segments(self) -> list[str]:
        assert self.parent
        return [*self.parent.segments, self.name]


class ParamDecl(NamedDecl):
    KIND = "function parameter"

    ty_ref: TypeRefDecl
    parent: Optional["FuncBaseDecl"]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
    ):
        super().__init__(name, loc)
        self.ty_ref = ty_ref
        self.parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_param_decl(self)

    @property
    @override
    def segments(self) -> list[str]:
        assert self.parent
        return [*self.parent.segments, self.name]

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {}


class RetvalDecl(NamedDecl):
    KIND = "function return type"

    ty_ref: TypeRefDecl
    parent: Optional["FuncBaseDecl"]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
    ):
        super().__init__(name, loc)
        self.ty_ref = ty_ref
        self.parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_retval_decl(self)

    @property
    @override
    def segments(self) -> list[str]:
        assert self.parent
        return [*self.parent.segments, self.name]

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {}


class FuncBaseDecl(NamedDecl, metaclass=ABCMeta):
    params: list[ParamDecl]
    retvals: list[RetvalDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation]):
        super().__init__(name, loc)
        self.params = []
        self.retvals = []

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {
            "param": self.params,
            "retval": self.retvals,
        }

    def add_param(self, p: ParamDecl):
        p.parent = self
        self.params.append(p)

    def add_retval(self, r: RetvalDecl):
        r.parent = self
        self.retvals.append(r)


class GlobFuncDecl(FuncBaseDecl, PackageLevelDecl):
    KIND = "non-member function"

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_glob_func_decl(self)


class TypeDecl(PackageLevelDecl, Type, metaclass=ABCMeta):
    pass


class TypeAliasDecl(TypeDecl):
    KIND = "type alias"

    ty_ref: TypeRefDecl
    final_ty: Optional[Type] = None
    is_solved: bool = False

    def __init__(self, name: str, loc: Optional[SourceLocation], ty_ref: TypeRefDecl):
        super().__init__(name, loc)
        self.ty_ref = ty_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_type_alias_decl(self)

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {}


class EnumItemDecl(NamedDecl):
    KIND = "enum item"

    value: Optional[int]
    parent: Optional["EnumDecl"]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        value: Optional[int] = None,
    ):
        super().__init__(name, loc)
        self.value = value
        self.parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_enum_item_decl(self)

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {}

    @property
    @override
    def segments(self) -> list[str]:
        assert self.parent
        return [*self.parent.segments, self.name]


class EnumDecl(TypeDecl):
    KIND = "enum"

    items: list[EnumItemDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation]):
        super().__init__(name, loc)
        self.items = []

    @override
    def _accept(self, v: "DeclVisitor | TypeVisitor") -> Any:
        return v.visit_enum_decl(self)

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {"item": self.items}

    def add_item(self, f: EnumItemDecl):
        f.parent = self
        self.items.append(f)


class StructFieldDecl(NamedDecl):
    KIND = "struct field"

    ty_ref: TypeRefDecl
    parent: Optional["StructDecl"]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
    ):
        super().__init__(name, loc)
        self.ty_ref = ty_ref
        self.parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_struct_field_decl(self)

    @property
    @override
    def segments(self) -> list[str]:
        assert self.parent
        return [*self.parent.segments, self.name]

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {}


class StructDecl(TypeDecl):
    KIND = "struct"

    fields: list[StructFieldDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation]):
        super().__init__(name, loc)
        self.fields = []

    @override
    def _accept(self, v: "TypeVisitor | DeclVisitor") -> Any:
        return v.visit_struct_decl(self)

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {"field": self.fields}

    def add_field(self, f: StructFieldDecl):
        f.parent = self
        self.fields.append(f)


class IfaceParentDecl(NamedDecl):
    KIND = "function return type"

    ty_ref: TypeRefDecl
    parent: Optional["IfaceDecl"]

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
    ):
        super().__init__(name, loc)
        self.ty_ref = ty_ref
        self.parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_parent_decl(self)

    @property
    @override
    def segments(self) -> list[str]:
        assert self.parent
        return [*self.parent.segments, self.name]

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {}


class IfaceMethodDecl(FuncBaseDecl):
    KIND = "interface method"

    parent: Optional["IfaceDecl"] = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_method_decl(self)

    @property
    @override
    def segments(self) -> list[str]:
        assert self.parent
        return [*self.parent.segments, self.name]


class IfaceDecl(TypeDecl):
    KIND = "interface"

    methods: list[IfaceMethodDecl]
    parents: list[IfaceParentDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation]):
        super().__init__(name, loc)
        self.methods = []
        self.parents = []

    @override
    def _accept(self, v: "TypeVisitor | DeclVisitor") -> Any:
        return v.visit_iface_decl(self)

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {
            "method": self.methods,
            "parent": self.parents,
        }

    def add_method(self, f: IfaceMethodDecl):
        f.parent = self
        self.methods.append(f)

    def add_parent(self, p: IfaceParentDecl):
        p.parent = self
        self.parents.append(p)


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
    type_aliases: list[TypeAliasDecl]

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
        self.type_aliases = []

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}<{self.name!r}>"

    @property
    @override
    def segments(self) -> list[str]:
        return self.name.split(".")

    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package(self)

    @property
    @override
    def all_children(self) -> dict[str, Iterable["NamedDecl"]]:
        return {
            "pkg_imports": self.pkg_imports,
            "decl_imports": self.decl_imports,
            "functions": self.functions,
            "structs": self.structs,
            "enums": self.enums,
            "interfaces": self.interfaces,
            "type_aliases": self.type_aliases,
        }

    def _register_to_decl(self, d: PackageLevelDecl):
        if prev := self.decls.get(d.name, None):
            raise DeclRedefDiagError(prev, d)
        else:
            self.decls[d.name] = d

    def add_function(self, f: GlobFuncDecl):
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
        if isinstance(d, GlobFuncDecl):
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
