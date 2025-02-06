"""Defines the types for declarations."""

from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Optional, Protocol

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


class Decl(metaclass=ABCMeta):
    """Represents any declaration."""

    loc: Optional[SourceLocation]

    attrs: dict[str, "AttrItemDecl"]

    def __init__(self, loc: Optional[SourceLocation]):
        self.loc = loc
        self.attrs = {}

    def add_attr(self, i: "AttrItemDecl"):
        i.node_parent = self
        if prev := self.attrs.get(i.name, None):
            raise AttrRedefError(prev, i)
        self.attrs[i.name] = i

    @property
    @abstractmethod
    def description(self) -> str: ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.description}>"

    @abstractmethod
    def _accept(self, v: "DeclVisitor") -> Any: ...


class NamedDecl(Decl, metaclass=ABCMeta):
    name: str

    def __init__(
        self,
        loc: Optional[SourceLocation],
        name: str,
    ):
        super().__init__(loc)
        self.name = name


#############
# Attribute #
#############


class AttrItemDecl(NamedDecl):
    value: bool | int | str | None
    node_parent: Optional[Decl]

    def __init__(
        self,
        loc: Optional[SourceLocation],
        name: str,
        value: bool | int | str | None = None,
    ):
        super().__init__(loc, name)
        self.value = value
        self.node_parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_attr_item_decl(self)

    @property
    @override
    def description(self) -> str:
        return f"attribute {self.name}"


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

    resolved_ty: Optional[Type]
    is_resolved: bool

    def __init__(
        self,
        loc: Optional[SourceLocation],
        resolved_ty: Optional[Type] = None,
    ):
        super().__init__(loc)
        self.resolved_ty = resolved_ty
        self.is_resolved = resolved_ty is not None

    @property
    @abstractmethod
    def unresolved_name(self) -> str: ...

    @property
    @override
    def description(self) -> str:
        return f"type reference {self.unresolved_name}"


class SimpleTypeRefDecl(TypeRefDecl):
    symbol: str

    def __init__(
        self,
        loc: Optional[SourceLocation],
        symbol: str,
        resolved_ty: Optional[Type] = None,
    ):
        super().__init__(loc, resolved_ty)
        self.symbol = symbol

    @override
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
        loc: Optional[SourceLocation],
        symbol: str,
        args_ty_ref: list[TypeRefDecl],
        resolved_ty: Optional[Type] = None,
    ):
        super().__init__(loc, resolved_ty)
        self.symbol = symbol
        self.args_ty_ref = args_ty_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_generic_type_ref_decl(self)

    @property
    @override
    def unresolved_name(self):
        args_fmt = ", ".join(arg.unresolved_name for arg in self.args_ty_ref)
        return f"{self.symbol}<{args_fmt}>"


class ArrayTypeRefDecl(TypeRefDecl):
    item_ty_ref: TypeRefDecl

    def __init__(
        self,
        loc: Optional[SourceLocation],
        item_ty_ref: TypeRefDecl,
        resolved_ty: Optional[Type] = None,
    ):
        super().__init__(loc, resolved_ty)
        self.item_ty_ref = item_ty_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_array_type_ref_decl(self)

    @property
    @override
    def unresolved_name(self):
        return f"{self.item_ty_ref.unresolved_name}[]"


#####################
# Import References #
#####################


class PackageRefDecl(Decl):
    symbol: str

    is_resolved: bool
    resolved_pkg: Optional["Package"]

    def __init__(
        self,
        loc: Optional[SourceLocation],
        symbol: str,
    ):
        super().__init__(loc)
        self.symbol = symbol
        self.is_resolved = False
        self.resolved_pkg = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package_ref_decl(self)

    @property
    @override
    def description(self) -> str:
        return f"package reference {self.symbol}"


class DeclarationRefDecl(Decl):
    symbol: str

    pkg_ref: PackageRefDecl

    is_resolved: bool
    resolved_decl: Optional["PackageLevelDecl"]

    def __init__(
        self,
        loc: Optional[SourceLocation],
        symbol: str,
        pkg_ref: PackageRefDecl,
    ):
        super().__init__(loc)
        self.symbol = symbol
        self.pkg_ref = pkg_ref
        self.is_resolved = False
        self.resolved_decl = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_decl_ref_decl(self)

    @property
    @override
    def description(self) -> str:
        return f"type reference {self.symbol}"


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
    pkg_ref: PackageRefDecl

    def __init__(
        self,
        pkg_ref: PackageRefDecl,
        *,
        loc: Optional[SourceLocation] = None,
        name: str = "",
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

    @property
    @override
    def description(self) -> str:
        return f"package import {self.name}"


class DeclarationImportDecl(ImportDecl):
    decl_ref: DeclarationRefDecl

    def __init__(
        self,
        decl_ref: DeclarationRefDecl,
        *,
        loc: Optional[SourceLocation] = None,
        name: str = "",
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

    @property
    @override
    def description(self) -> str:
        return f"declaration import {self.name}"


######################
# Other Declarations #
######################


class ParamDecl(NamedDecl):
    ty_ref: TypeRefDecl

    def __init__(
        self,
        loc: Optional[SourceLocation],
        name: str,
        ty_ref: TypeRefDecl,
    ):
        super().__init__(loc, name)
        self.ty_ref = ty_ref

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_param_decl(self)

    @property
    @override
    def description(self) -> str:
        return f"parameter {self.name}"


class EnumItemDecl(NamedDecl):
    ty_ref: Optional[TypeRefDecl]
    value: Optional[int]
    node_parent: Optional["EnumDecl"]

    def __init__(
        self,
        loc: Optional[SourceLocation],
        name: str,
        ty_ref: Optional[TypeRefDecl] = None,
        value: Optional[int] = None,
    ):
        super().__init__(loc, name)
        self.ty_ref = ty_ref
        self.value = value
        self.node_parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_enum_item_decl(self)

    @property
    @override
    def description(self) -> str:
        return f"enum item {self.name}"


class StructFieldDecl(NamedDecl):
    ty_ref: TypeRefDecl
    node_parent: Optional["StructDecl"]

    def __init__(
        self,
        loc: Optional[SourceLocation],
        name: str,
        ty_ref: TypeRefDecl,
    ):
        super().__init__(loc, name)
        self.ty_ref = ty_ref
        self.node_parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_struct_field_decl(self)

    @property
    @override
    def description(self) -> str:
        return f"struct field {self.name}"


class IfaceParentDecl(Decl):
    ty_ref: TypeRefDecl
    node_parent: Optional["IfaceDecl"]

    def __init__(
        self,
        loc: Optional[SourceLocation],
        ty_ref: TypeRefDecl,
    ):
        super().__init__(loc)
        self.ty_ref = ty_ref
        self.node_parent = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_parent_decl(self)

    @property
    @override
    def description(self) -> str:
        return f"interface parent ({self.ty_ref.description})"


class IfaceMethodDecl(NamedDecl):
    node_parent: Optional["IfaceDecl"] = None
    params: list[ParamDecl]
    return_ty_ref: Optional[TypeRefDecl]

    def __init__(
        self,
        loc: Optional[SourceLocation],
        name: str,
        return_ty_ref: Optional[TypeRefDecl] = None,
    ):
        super().__init__(loc, name)
        self.params = []
        self.return_ty_ref = return_ty_ref

    def add_param(self, p: ParamDecl):
        self.params.append(p)

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_func_decl(self)

    @property
    @override
    def description(self) -> str:
        return f"interface method {self.name}"


##############################
# Package Level Declarations #
##############################


class PackageLevelDecl(NamedDecl, metaclass=ABCMeta):
    node_parent: Optional["Package"] = None

    @property
    def full_name(self):
        return f"{self.node_parent.name}.{self.name}" if self.node_parent else self.name


class GlobFuncDecl(PackageLevelDecl):
    params: list[ParamDecl]
    return_ty_ref: Optional[TypeRefDecl]

    def __init__(
        self,
        loc: Optional[SourceLocation],
        name: str,
        return_ty_ref: Optional[TypeRefDecl] = None,
    ):
        super().__init__(loc, name)
        self.params = []
        self.return_ty_ref = return_ty_ref

    def add_param(self, p: ParamDecl):
        self.params.append(p)

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_glob_func_decl(self)

    @property
    @override
    def description(self) -> str:
        return f"function {self.name}"


#####################
# Type Declarations #
#####################


class TypeDecl(PackageLevelDecl, metaclass=ABCMeta):
    @abstractmethod
    def as_type(self) -> UserType: ...


class EnumDecl(TypeDecl):
    items: list["EnumItemDecl"]

    def __init__(self, loc: Optional[SourceLocation], name: str):
        super().__init__(loc, name)
        self.items = []

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_enum_decl(self)

    def add_item(self, f: "EnumItemDecl"):
        f.node_parent = self
        self.items.append(f)

    @override
    def as_type(self) -> UserType:
        return EnumType(self)

    @property
    @override
    def description(self) -> str:
        return f"enum {self.name}"


class StructDecl(TypeDecl):
    fields: list["StructFieldDecl"]

    def __init__(self, loc: Optional[SourceLocation], name: str):
        super().__init__(loc, name)
        self.fields = []

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_struct_decl(self)

    def add_field(self, f: "StructFieldDecl"):
        f.node_parent = self
        self.fields.append(f)

    @override
    def as_type(self) -> UserType:
        return StructType(self)

    @property
    @override
    def description(self) -> str:
        return f"struct {self.name}"


class IfaceDecl(TypeDecl):
    methods: list["IfaceMethodDecl"]
    parents: list["IfaceParentDecl"]

    def __init__(self, loc: Optional[SourceLocation], name: str):
        super().__init__(loc, name)
        self.methods = []
        self.parents = []

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_decl(self)

    def add_method(self, f: "IfaceMethodDecl"):
        f.node_parent = self
        self.methods.append(f)

    def add_parent(self, p: "IfaceParentDecl"):
        p.node_parent = self
        self.parents.append(p)

    @override
    def as_type(self) -> UserType:
        return IfaceType(self)

    @property
    @override
    def description(self) -> str:
        return f"interface {self.name}"


######################
# The main container #
######################


class Package(NamedDecl):
    """A collection of named identities sharing the same scope."""

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
        super().__init__(loc, name)

        self.imports = {}
        self.decls = {}

        self.pkg_imports = []
        self.decl_imports = []

        self.functions = []
        self.structs = []
        self.enums = []
        self.interfaces = []

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

    @override
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

    @property
    @override
    def description(self) -> str:
        return f"package {self.name}"


class PackageGroup:
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
