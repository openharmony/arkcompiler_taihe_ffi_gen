"""Defines the types for declarations."""

from abc import ABC
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Protocol

from typing_extensions import override

from taihe.semantics.types import (
    Type,
    TypeAlike,
)
from taihe.utils.exceptions import DeclRedefDiagError
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.visitor import DeclVisitor, TypeVisitor

################
# Declarations #
################


class DeclAlike(Protocol):
    """Represents classes that are similar to, but not necessarily identical to, declarations.

    This protocol defines a single method, `_accept`, which is used by `DeclVisitor` instances
    to traverse and process instances of classes conforming to this protocol.

    Notable implementors to this protocol are `Package` and `PackageGroup`.
    """

    def _accept(self, v: "DeclVisitor") -> Any: ...


class Decl(ABC, DeclAlike):
    KIND: ClassVar[str]

    name: str
    parent: Optional["Decl"] = None
    loc: Optional[SourceLocation]

    def __init__(self, name: str, loc: Optional[SourceLocation], parent: Any = None):
        assert name
        self.name = name
        self.parent = parent
        self.loc = loc

    @property
    def description(self) -> str:
        """Describes the object in a human-friendly way."""
        return f"{self.KIND} {self.name!r}"

    @property
    def parent_package(self) -> str | None:
        t = self
        while t is not None:
            if isinstance(t, Package):
                return t.name
            # All objects inherenting "Decl" must has "parent" as its field.
            t = t.parent

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}<{self.name!r} in {self.parent}>"


class TypeRefDecl(Decl, TypeAlike):
    """Repersents a reference to a `Type`.

    Each user of a `Type` must be encapsulated in a `TypeRefDecl`.
    Also, `TypeRefDecl` is NOT a `TypeDecl`.
    In other words, `TypeRefDecl` is a pointer, instead of a declaration.

    For example:
    ```
    struct Foo { ... }.     // `Foo` is a `TypeDecl`.

    fn func(foo: mut Foo);  // `mut Foo` is `TypeRefDecl(ref_ty=TypeDecl('Foo'), qual=MUT)`.
    fn func(foo: BadType);  // `BadType` is `TypeRefDecl(ref_ty=None)`.
    ```
    """

    KIND = "type reference"

    parent = None
    ref_ty: Optional[Type] = None
    resolved: bool = False

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ref_ty: Optional[Type] = None,
    ):
        super().__init__(name, loc, parent=None)
        self.ref_ty = ref_ty
        self.resolved = ref_ty is not None

    def _accept(self, v: "DeclVisitor | TypeVisitor") -> Any:
        return v.visit_type_ref_decl(self)


#######################
# Import Declarations #
#######################


class ImportDecl(Decl):
    """Represents a package or declaration import.

    Invariant: the `name` field in base class `Decl` always represents actual name of imports.

    For example:

    ```
    use foo;                 --> PackageImportDecl(
                                     name='foo',
                                     pkg=PackageRefDecl(name='foo'),
                                 )
    use foo as bar;          --> PackageImportDecl(
                                     name='bar',
                                     pkg=PackageRefDecl(name='foo'),
                                 )
    from foo use Bar;        --> DeclarationImportDecl(
                                     name='Bar',
                                     decl=DeclarationRefDecl(
                                         name='Bar',
                                         pkg=PackageRefDecl(name='foo'),
                                     ),
                                 )
    from foo use Bar as Baz; --> DeclarationImportDecl(
                                     name='Baz',
                                     decl=DeclarationRefDecl(
                                         name='Bar',
                                         pkg=PackageRefDecl(name='foo'),
                                     ),
                                 )
    ```
    """

    KIND = "<import-decl-kind>"

    parent: Optional["Package"] = None


class PackageRefDecl(Decl):
    KIND = "package reference"

    parent = None
    ref_pkg: Optional["Package"] = None
    resolved: bool = False

    def __init__(self, name: str, loc: Optional[SourceLocation]):
        super().__init__(name, loc, parent=None)

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package_ref_decl(self)


class DeclarationRefDecl(Decl):
    KIND = "package reference"

    parent = None
    ref_decl: Optional["TypeDecl"] = None
    resolved: bool = False
    pkg: PackageRefDecl

    def __init__(self, name: str, loc: Optional[SourceLocation], p: PackageRefDecl):
        super().__init__(name, loc, parent=None)
        self.pkg = p

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_decl_ref_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        v.handle_decl(self.pkg)


class PackageImportDecl(ImportDecl):
    KIND = "use of package"

    pkg: PackageRefDecl

    def __init__(
        self,
        p: PackageRefDecl,
        *,
        name: str = "",
        loc: Optional[SourceLocation] = None,
        **kwargs,
    ):
        super().__init__(name=name or p.name, loc=loc or p.loc, **kwargs)
        self.pkg = p

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package_import_decl(self)

    def is_alias(self) -> bool:
        return self.name != self.pkg.name

    def _traverse(self, v: "DeclVisitor"):
        v.handle_decl(self.pkg)


class DeclarationImportDecl(ImportDecl):
    KIND = "use of declaration"

    decl: DeclarationRefDecl

    def __init__(
        self,
        d: DeclarationRefDecl,
        *,
        name: str = "",
        loc: Optional[SourceLocation] = None,
        **kwargs,
    ):
        super().__init__(name=name or d.name, loc=loc or d.loc, **kwargs)
        self.decl = d

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_decl_import_decl(self)

    def is_alias(self) -> bool:
        return self.name != self.decl.name

    def _traverse(self, v: "DeclVisitor"):
        v.handle_decl(self.decl)


######################
# Other Declarations #
######################


class PackageLevelDecl(Decl):
    KIND = "<package-level-decl-kind>"

    parent: Optional["Package"] = None


class ParamDecl(Decl):
    KIND = "function parameter"

    ty: TypeRefDecl
    parent: Optional["FuncBaseDecl"] = None

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty: TypeRefDecl,
        **kwargs,
    ):
        super().__init__(name, loc, **kwargs)
        self.ty = ty

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_param_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        v.handle_decl(self.ty)


class FuncBaseDecl(Decl):
    KIND = "<func-decl-kind>"

    params: list[ParamDecl]
    return_types: list[TypeRefDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation], **kwargs):
        super().__init__(name, loc, **kwargs)
        self.params = []
        self.return_types = []

    def _traverse(self, v: "DeclVisitor"):
        for p in self.params:
            v.handle_decl(p)
        for r in self.return_types:
            v.handle_decl(r)

    def add_param(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty: TypeRefDecl,
        **kwargs,
    ):
        param = ParamDecl(name, loc, ty, parent=self, **kwargs)
        self.params.append(param)

    def add_return_ty(self, ty: TypeRefDecl):
        self.return_types.append(ty)


class FuncDecl(FuncBaseDecl, PackageLevelDecl):
    KIND = "function"

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_func_decl(self)


class TypeDecl(PackageLevelDecl, Type):
    KIND = "<type-decl-kind>"


class EnumItemDecl(Decl):
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

    def _traverse(self, v: "DeclVisitor"):
        for f in self.items:
            v.handle_decl(f)

    def add_item(
        self,
        name: str,
        loc: Optional[SourceLocation],
        value: int,
        **kwargs,
    ):
        f = EnumItemDecl(name, loc, value, parent=self, **kwargs)
        self.items.append(f)


class StructFieldDecl(Decl):
    KIND = "struct field"

    ty: TypeRefDecl
    parent: Optional["StructDecl"] = None

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty: TypeRefDecl,
        **kwargs,
    ):
        super().__init__(name, loc, **kwargs)
        self.ty = ty

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_struct_field_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        v.handle_decl(self.ty)


class StructDecl(TypeDecl):
    KIND = "struct"

    fields: list[StructFieldDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation], **kwargs):
        super().__init__(name, loc, **kwargs)
        self.fields = []

    @override
    def _accept(self, v: "TypeVisitor | DeclVisitor") -> Any:
        return v.visit_struct_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        for f in self.fields:
            v.handle_decl(f)

    def add_field(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ty: TypeRefDecl,
        **kwargs,
    ):
        f = StructFieldDecl(name, loc, ty, parent=self, **kwargs)
        self.fields.append(f)


class IfaceMethodDecl(FuncBaseDecl):
    KIND = "interface method"

    parent: Optional["IfaceDecl"] = None

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_iface_method_decl(self)


class IfaceDecl(TypeDecl):
    KIND = "struct"

    methods: list[IfaceMethodDecl]
    parents: list[TypeRefDecl]

    def __init__(self, name: str, loc: Optional[SourceLocation], **kwargs):
        super().__init__(name, loc, **kwargs)
        self.methods = []
        self.parents = []

    @override
    def _accept(self, v: "TypeVisitor | DeclVisitor") -> Any:
        return v.visit_iface_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        for f in self.methods:
            v.handle_decl(f)
        for e in self.parents:
            v.handle_decl(e)

    def add_function(self, f: IfaceMethodDecl):
        f.parent = self
        self.methods.append(f)

    def add_parent(self, d: TypeRefDecl):
        self.parents.append(d)


######################
# The main container #
######################


class Package(Decl):
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

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}<{self.name!r}>"

    def _accept(self, v: "DeclVisitor") -> Any:
        return v.visit_package(self)

    def _traverse(self, v: "DeclVisitor"):
        for i in self.pkg_imports:
            v.handle_decl(i)
        for i in self.decl_imports:
            v.handle_decl(i)
        for d in self.functions:
            v.handle_decl(d)
        for d in self.structs:
            v.handle_decl(d)
        for d in self.enums:
            v.handle_decl(d)
        for d in self.interfaces:
            v.handle_decl(d)

    def _register_to_decl(self, d: PackageLevelDecl):
        if prev := self.decls.get(d.name, None):
            raise DeclRedefDiagError(prev, d)
        else:
            self.decls[d.name] = d

    def _register_to_import(self, i: ImportDecl):
        if prev := self.imports.get(i.name, None):
            raise DeclRedefDiagError(prev, i)
        else:
            self.imports[i.name] = i

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

    def add_declaration(self, d: Decl):
        if isinstance(d, FuncDecl):
            self.add_function(d)
        elif isinstance(d, StructDecl):
            self.add_struct(d)
        elif isinstance(d, EnumDecl):
            self.add_enum(d)
        elif isinstance(d, IfaceDecl):
            self.add_interface(d)
        else:
            raise NotImplementedError(f"unexpected declaration {type(d)}")

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
            raise NotImplementedError(f"unexpected import {type(i)}")


class PackageGroup(DeclAlike):
    """Stores all known packages for a compilation instance."""

    _pkgs: dict[str, Package]

    def __init__(self):
        self._pkgs = {}

    def _accept(self, v: "DeclVisitor"):
        return v.visit_package_group(self)

    def _traverse(self, v: "DeclVisitor"):
        for p in self.packages:
            v.handle_decl(p)

    def lookup(self, name: str) -> Optional["Package"]:
        return self._pkgs.get(name, None)

    def add(self, pkg: Package):
        assert pkg.name not in self._pkgs
        self._pkgs[pkg.name] = pkg

    @property
    def packages(self) -> Iterable[Package]:
        return self._pkgs.values()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}({', '.join(repr(x) for x in self._pkgs)})"
        )
