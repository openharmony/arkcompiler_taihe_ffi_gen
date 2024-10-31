"""Defines the types for declarations."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Protocol

from typing_extensions import override

from taihe.semantics.types import VOID, QualifiedType, Type, TypeRef
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

    def __init__(self, name: str = "", loc=None, parent=None):
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


class TypeRefDecl(Decl, TypeRef):
    """Represents a reference to type. TypeRefDecl is NOT a TypeDecl!"""

    KIND = "type reference"

    parent: Optional["Decl"] = None

    def __init__(self, name: str, ref_ty: Optional[Type] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.ref_ty = ref_ty

    def _accept(self, v: "DeclVisitor | TypeVisitor") -> Any:
        v.visiting = self
        return v.visit_type_ref_decl(self)

    def _traverse(self, v: "DeclVisitor") -> Any:
        if self.ref_ty:
            return v.handle_type(self.ref_ty)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}<{self.name!r} to {self.ref_ty}>"


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

    pkg: str
    """The target package to import into the current package."""

    def __init__(self, name: str, pkg: str, **kwargs):
        super().__init__(name=name, **kwargs)
        self.pkg = pkg

    def is_alias(self) -> bool:
        """Returns True if the import has been renamed."""
        raise NotImplementedError()


class PackageImportDecl(ImportDecl):
    KIND = "use of package"

    name: str
    """Optionally use another name for the imported package."""

    def __init__(self, pkg: str, *, alias: str = "", **kwargs):
        super().__init__(name=alias or pkg, pkg=pkg, **kwargs)

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_package_import_decl(self)

    @override
    def is_alias(self) -> bool:
        return self.name != self.pkg


class DeclarationImportDecl(ImportDecl):
    KIND = "use of declaration"

    decl: str
    """The original name for the declaration inside the target package."""

    name: str
    """Optionally use another name for the imported declaration."""

    def __init__(self, pkg: str, sym: str, *, alias: str = "", **kwargs):
        super().__init__(name=alias or sym, pkg=pkg, **kwargs)
        self.decl = sym

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_decl_import_decl(self)

    @override
    def is_alias(self) -> bool:
        return self.name != self.decl


class ParamDecl(Decl):
    KIND = "function parameter"

    qual_ty: QualifiedType
    # type: ignore (already set with Decl.__init__)
    parent: Optional["FuncDecl"]

    def __init__(self, name: str, ty: QualifiedType | TypeRef, **kwargs):
        super().__init__(name, **kwargs)
        self.qual_ty = ty if isinstance(ty, QualifiedType) else QualifiedType(ty)

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_param_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        v.handle_type(self.qual_ty)


class FuncDecl(Decl):
    KIND = "function"

    params: list[ParamDecl]
    return_ty: TypeRef
    # type: ignore (already set with Decl.__init__)
    parent: Optional["Package"]

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.params = []
        self.return_ty = TypeRef("void", VOID)

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_func_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        for p in self.params:
            v.visiting = p
            p._accept(v)
        v.handle_type(self.return_ty)

    def add_param(self, name: str, ty: QualifiedType | TypeRef, **kwargs):
        param = ParamDecl(name, ty, parent=self, **kwargs)
        self.params.append(param)


class TypeDecl(Decl, Type):
    parent: Optional["Package"] = None
    KIND = "<type-decl-kind>"

    def _accept(self, v: "DeclVisitor | TypeVisitor") -> Any:
        del v


class EnumItemDecl(Decl):
    KIND = "enum item"
    parent: Optional["EnumDecl"] = None
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
    parent: Optional["Package"] = None
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
            v.visiting = f
            f._accept(v)

    def add_item(self, name: str, value: int, **kwargs):
        f = EnumItemDecl(name, value, parent=self, **kwargs)
        self.items.append(f)


class StructFieldDecl(Decl):
    KIND = "struct field"

    ty: TypeRef
    parent: Optional["StructDecl"] = None

    def __init__(self, name: str, ty: TypeRef, **kwargs):
        super().__init__(name, **kwargs)
        self.ty = ty

    @override
    def _accept(self, v: "DeclVisitor") -> Any:
        v.visiting = self
        return v.visit_struct_field_decl(self)

    def _traverse(self, v: "DeclVisitor"):
        v.handle_type(self.ty)


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
            v.visiting = f
            f._accept(v)

    def add_field(self, name: str, ty: TypeRef, **kwargs):
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
    decls: dict[str, Decl]

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
            v.visiting = i
            i._accept(v)
        for d in self.decls.values():
            v.visiting = d
            d._accept(v)

    def _register_to_decl(self, d: Decl):
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
            v.visiting = p
            p._accept(v)

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
