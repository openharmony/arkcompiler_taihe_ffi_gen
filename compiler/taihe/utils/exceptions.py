from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from taihe.utils.diagnostics import DiagError, DiagNote, DiagWarn
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        Decl,
        IfaceDecl,
        Package,
        PackageLevelDecl,
        StructDecl,
        StructFieldDecl,
        TypeRefDecl,
    )


@dataclass
class DefinitionConflictDiagNote(DiagNote):
    MSG = "previously occurred here"


@dataclass
class EnumValueCollisionDiagNote(DiagNote):
    MSG = "first use"


@dataclass
class RecursiveExtensionNote(DiagNote):
    MSG = "the interface is extended by {iface.description}"

    iface: "IfaceDecl"

    def __init__(
        self,
        last: tuple["IfaceDecl", "TypeRefDecl"],
    ):
        self.loc = last[1].loc
        self.iface = last[0]


@dataclass
class RecursiveInclusionNote(DiagNote):
    MSG = "the struct is included in {struct.description}"

    struct: "StructDecl"

    def __init__(
        self,
        last: tuple["StructDecl", "StructFieldDecl"],
    ):
        self.loc = last[1].loc
        self.struct = last[0]


@dataclass
class PackageRedefDiagError(DiagError):
    MSG = "package name {pkg!r} is duplicated"

    pkg_name: str
    prev_loc: Optional[SourceLocation] = field(kw_only=True)

    def notes(self):
        if self.prev_loc:
            yield DefinitionConflictDiagNote(loc=self.prev_loc)


@dataclass
class DeclRedefDiagError(DiagError):
    MSG = "redefinition of {current.description}"

    prev: "Decl"
    current: "Decl"

    def __init__(self, prev: "Decl", current: "Decl"):
        self.prev = prev
        self.current = current
        self.loc = current.loc

    def notes(self):
        if self.prev.loc:
            yield DefinitionConflictDiagNote(loc=self.prev.loc)


@dataclass
class EnumValueCollisionError(DiagError):
    MSG = "discriminant value {value} already exists"

    prev: "Decl"
    current: "Decl"
    value: int

    def __init__(self, prev: "Decl", current: "Decl", value: int):
        self.prev = prev
        self.current = current
        self.loc = current.loc
        self.value = value

    def notes(self):
        if self.prev.loc:
            yield EnumValueCollisionDiagNote(loc=self.prev.loc)


@dataclass
class IDLSyntaxError(DiagError):
    MSG = "unexpected {token!r}"

    token: str


@dataclass
class PackageNotExistError(DiagError):
    MSG = "package {name!r} not exist"

    name: str


@dataclass
class DeclNotExistError(DiagError):
    MSG = "declaration {name!r} not exist"

    name: str


@dataclass
class DeclarationNotInScopeError(DiagError):
    MSG = "declaration name {name!r} is not declared or imported in this scope"

    name: str


@dataclass
class PackageNotInScopeError(DiagError):
    MSG = "package name {name!r} is not imported in this scope"

    name: str


@dataclass
class NotATypeError(DiagError):
    MSG = "{name!r} is not a type name"

    name: str


@dataclass
class NotAPackageError(DiagError):
    MSG = "{name!r} is not a package name"

    name: str


@dataclass
class NotADeclarationError(DiagError):
    MSG = "{name!r} is not a declaration name"

    name: str


@dataclass
class SymbolConflictWithNamespaceError(DiagError):
    MSG = "declaration of {decl.description} in {pkg.description} shadows a file-level declaration"

    decl: "PackageLevelDecl"
    pkg: "Package"

    def __init__(self, decl: "PackageLevelDecl", pkg: "Package"):
        self.decl = decl
        self.loc = decl.loc
        self.pkg = pkg


@dataclass
class StructFieldTypeError(DiagError):
    MSG = "expected built-in/struct/enum type, got {name!r}"

    name: str

    def __init__(self, ty: "TypeRefDecl"):
        self.loc = ty.loc
        self.name = ty.name


@dataclass
class ExtendsTypeError(DiagError):
    MSG = "expected an interface, got {name!r}"

    name: str

    def __init__(self, ty: "TypeRefDecl"):
        self.loc = ty.loc
        self.name = ty.name


@dataclass
class DuplicateExtendsWarn(DiagWarn):
    MSG = "{iface.description} is extended multiple times"

    iface: "IfaceDecl"
    prev: "TypeRefDecl"
    curr: "TypeRefDecl"

    def __init__(self, iface: "IfaceDecl", prev: "TypeRefDecl", curr: "TypeRefDecl"):
        self.loc = curr.loc
        self.iface = iface
        self.curr = curr
        self.prev = prev

    def notes(self):
        if self.prev.loc:
            yield DefinitionConflictDiagNote(loc=self.prev.loc)


@dataclass
class RecursiveExtensionError(DiagError):
    MSG = "recursive extension is found in {iface.description}"

    iface: "IfaceDecl"
    other: list[tuple["IfaceDecl", "TypeRefDecl"]]

    def __init__(
        self,
        last: tuple["IfaceDecl", "TypeRefDecl"],
        other: list[tuple["IfaceDecl", "TypeRefDecl"]],
    ):
        self.loc = last[1].loc
        self.iface = last[0]
        self.other = other

    def notes(self):
        for n in self.other:
            yield RecursiveExtensionNote(n)


@dataclass
class RecursiveInclusionError(DiagError):
    MSG = "recursive inclusion is found in {struct.description}"

    struct: "StructDecl"
    other: list[tuple["StructDecl", "StructFieldDecl"]]

    def __init__(
        self,
        last: tuple["StructDecl", "StructFieldDecl"],
        other: list[tuple["StructDecl", "StructFieldDecl"]],
    ):
        self.loc = last[1].loc
        self.struct = last[0]
        self.other = other

    def notes(self):
        for n in self.other:
            yield RecursiveInclusionNote(n)


@dataclass
class QualifierError(DiagError):
    MSG = "qualifier {qual!r} cannot be applied to {name!r}"

    name: str
    qual: str

    def __init__(self, ty: "TypeRefDecl"):
        self.loc = ty.loc
        self.name = ty.name
        self.qual = ty.qual.describe()
