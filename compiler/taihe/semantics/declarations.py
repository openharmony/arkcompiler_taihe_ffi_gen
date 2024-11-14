"""Defines the types for declarations."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Protocol

from typing_extensions import override

from taihe.semantics.types import (
    Type,
    TypeAlike,
    TypeQualifier,
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
    parent: Any
    loc: Optional[SourceLocation]

    def __init__(self, name: str, loc=None, parent=None):
        assert name
        self.name = name
        self.parent = parent
        self.loc = loc

    @abstractmethod
    def _accept(self, v: "DeclVisitor") -> Any:
        pass

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

    fn func(foo: mut Foo);  // `Foo` is `TypeRefDecl(ref_ty=TypeDecl('Foo'), qual=MUT)`.
    fn func(foo: BadType);  // `BadType` is `TypeRefDecl(ref_ty=None)`.
    ```
    """

    KIND = "type reference"
    qual: TypeQualifier
    ref_ty: Optional[Type] = None
    resolved: bool = False

    def __init__(
        self,
        name: str,
        loc: Optional[SourceLocation],
        ref_ty: Optional[Type] = None,
        qual: TypeQualifier = TypeQualifier.NONE,
    ):
        super().__init__(name, loc, parent=None)
        self.ref_ty = ref_ty
        self.resolved = ref_ty is not None
        self.qual = qual

    def _accept(self, v: "DeclVisitor | TypeVisitor") -> Any:
        v.visiting = self
        return v.visit_type_ref_decl(self)

    def __repr__(self) -> str:
        ref_str = repr(self.ref_ty) if self.ref_ty else f"??? {self.name!r}"
        return f"<type-ref to {self.qual.describe(ref_str)}>"


#######################
# Import Declarations #
#######################


class ImportDecl(Decl):
    """Represents a package or declaration import.

    Invariant: the `name` field in base class `Decl` always represents actual name of imports.

    For example:

    use foo;                 -->     PackageImportDecl(pkg='foo', name='foo')
    use foo as bar;          -->     PackageImportDecl(pkg='foo', name='bar')
    from foo use Bar;        --> DeclarationImportDecl(pkg='foo', symbol='Bar', name='Bar')
    from foo use Bar as Baz; --> DeclarationImportDecl(pkg='foo', symbol='Bar', name='Baz')
    """

    KIND = "<import-decl-kind>"
    parent: Optional["Package"]


class PackageRefDecl(Decl):
    KIND = "package reference"

    ref_pkg: Optional["Package"] = None
    resolved: bool = False

    def __init__(self, name: str, loc):
        super().__init__(name, loc, parent=None)

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_package_ref_decl(self)


class DeclarationRefDecl(Decl):
    KIND = "package reference"

    ref_decl: Optional["TypeDecl"] = None
    resolved: bool = False

    pkg: PackageRefDecl

    def __init__(self, p: PackageRefDecl, name: str, loc):
        super().__init__(name, loc, parent=None)
        self.pkg = p

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_decl_ref_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        v.handle_decl(self.pkg)


class PackageImportDecl(ImportDecl):
    KIND = "use of package"

    name: str
    """Optionally use another name for the imported package."""

    pkg: PackageRefDecl

    def __init__(self, p: PackageRefDecl, *, name: str = "", loc=None, **kwargs):
        super().__init__(name=name or p.name, loc=loc or p.loc, **kwargs)
        self.pkg = p

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_package_import_decl(self)

    def is_alias(self) -> bool:
        return self.name != self.pkg.name

    def _traverse(self, v: "DeclVisitor"):
        v.handle_decl(self.pkg)


class DeclarationImportDecl(ImportDecl):
    KIND = "use of declaration"

    name: str
    """Optionally use another name for the imported declaration."""

    decl: DeclarationRefDecl

    def __init__(self, d: DeclarationRefDecl, *, name: str = "", loc=None, **kwargs):
        super().__init__(name=name or d.name, loc=loc or d.loc, **kwargs)
        self.decl = d

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
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
    parent: Optional["Package"]


class ParamDecl(Decl):
    KIND = "function parameter"

    ty: TypeRefDecl
    # type: ignore (already set with Decl.__init__)
    parent: Optional["FuncDecl"]

    def __init__(self, name: str, ty: TypeRefDecl, **kwargs):
        super().__init__(name, **kwargs)
        self.ty = ty

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_param_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        v.handle_decl(self.ty)


class FuncDecl(PackageLevelDecl):
    KIND = "function"

    params: list[ParamDecl]
    return_types: list[TypeRefDecl]

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.params = []
        self.return_types = []

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_func_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        for p in self.params:
            v.handle_decl(p)
        for r in self.return_types:
            v.handle_decl(r)

    def add_param(self, name: str, ty: TypeRefDecl, **kwargs):
        param = ParamDecl(name, ty, parent=self, **kwargs)
        self.params.append(param)

    def add_return_ty(self, ty: TypeRefDecl):
        self.return_types.append(ty)


class TypeDecl(PackageLevelDecl, Type):
    parent: Optional["Package"]
    KIND = "<type-decl-kind>"


class EnumItemDecl(Decl):
    KIND = "enum item"
    parent: Optional["EnumDecl"]
    # type:ignore (already set with Decl.__init__)
    value: int

    def __init__(self, name: str, value: int, **kwargs):
        super().__init__(name, **kwargs)
        self.value = value

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_enum_item_decl(self)


class EnumDecl(TypeDecl):
    KIND = "enum"
    items: list[EnumItemDecl]

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.items = []

    @override
    def _accept(self, v: "DeclVisitor | TypeVisitor") -> Any:
        v.visiting = self
        return v.visit_enum_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        for f in self.items:
            v.handle_decl(f)

    def add_item(self, name: str, value: int, **kwargs):
        f = EnumItemDecl(name, value, parent=self, **kwargs)
        self.items.append(f)


class StructFieldDecl(Decl):
    KIND = "struct field"

    ty: TypeRefDecl
    parent: Optional["StructDecl"]

    def __init__(self, name: str, ty: TypeRefDecl, **kwargs):
        super().__init__(name, **kwargs)
        self.ty = ty

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_struct_field_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        v.handle_decl(self.ty)


class StructDecl(TypeDecl):
    KIND = "struct"
    fields: list[StructFieldDecl]

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.fields = []

    @override
    def _accept(self, v: "TypeVisitor | DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_struct_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        for f in self.fields:
            v.handle_decl(f)

    def add_field(self, name: str, ty: TypeRefDecl, **kwargs):
        f = StructFieldDecl(name, ty, parent=self, **kwargs)
        self.fields.append(f)


######################
# The main container #
######################


class Package:
    """A collection of named identities sharing the same scope."""

    parent: ClassVar = None

    # Metadata about the package itself.
    name: str
    # Symbols
    imports: dict[str, ImportDecl]
    decls: dict[str, PackageLevelDecl]

    # Things that the package contains.
    functions: list[FuncDecl]
    structs: list[StructDecl]
    enums: list[EnumDecl]

    def __init__(self, name: str):
        self.name = name
        self.imports = {}
        self.decls = {}

        self.functions = []
        self.structs = []
        self.enums = []

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}<{self.name!r}>"

    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_package(self)

    def _traverse(self, v: "DeclVisitor"):
        for i in self.imports.values():
            v.handle_decl(i)
        for d in self.decls.values():
            v.handle_decl(d)

    def _register_to_decl(self, d: PackageLevelDecl):
        if prev := self.decls.get(d.name, None):
            raise DeclRedefDiagError(prev, d)
        else:
            self.decls[d.name] = d
        d.parent = self

    def add_import(self, i: ImportDecl):
        if prev := self.imports.get(i.name, None):
            raise DeclRedefDiagError(prev, i)
        else:
            self.imports[i.name] = i
        i.parent = self

    def add_function(self, f: FuncDecl):
        self._register_to_decl(f)
        self.functions.append(f)

    def add_struct(self, s: StructDecl):
        self._register_to_decl(s)
        self.structs.append(s)

    def add_enum(self, e: EnumDecl):
        self._register_to_decl(e)
        self.enums.append(e)

    def add_declaration(self, d: Decl):
        if isinstance(d, FuncDecl):
            self.add_function(d)
        elif isinstance(d, StructDecl):
            self.add_struct(d)
        elif isinstance(d, EnumDecl):
            self.add_enum(d)
        else:
            raise NotImplementedError(f"unexpected declaration {type(d)}")


class PackageGroup:
    """Stores all known packages for a compilation instance."""

    _pkgs: dict[str, Package]

    def __init__(self):
        self._pkgs = {}

    def _accept(self, v: "DeclVisitor"):
        v.visiting = self
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
