from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from taihe.utils.diagnostics import DiagError, DiagNote, DiagWarn
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        Decl,
        IfaceDecl,
        IfaceParentDecl,
        Package,
        PackageLevelDecl,
        StructDecl,
        StructFieldDecl,
    )


@dataclass
class DefinitionConflictDiagNote(DiagNote):
    MSG = "previously occurred here"


@dataclass
class RecursiveExtensionNote(DiagNote):
    MSG = "the interface is extended by {iface.description}"

    iface: Optional["IfaceDecl"]

    def __init__(
        self,
        last: "IfaceParentDecl",
    ):
        self.loc = last.loc
        self.iface = last.parent


@dataclass
class RecursiveInclusionNote(DiagNote):
    MSG = "the struct is included in {struct.description}"

    struct: Optional["StructDecl"]

    def __init__(
        self,
        last: "StructFieldDecl",
    ):
        self.loc = last.loc
        self.struct = last.parent


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
class NotATypeError(DiagError):
    MSG = "{name!r} is not a type name"

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

    def __init__(self, decl: "StructFieldDecl"):
        self.loc = decl.ty.loc
        self.name = decl.ty.name


@dataclass
class ExtendsTypeError(DiagError):
    MSG = "expected an interface, got {name!r}"

    name: str

    def __init__(self, decl: "IfaceParentDecl"):
        self.loc = decl.ty.loc
        self.name = decl.ty.name


@dataclass
class DuplicateExtendsWarn(DiagWarn):
    MSG = "{iface.description} is extended multiple times"

    iface: "IfaceDecl"
    prev: "IfaceParentDecl"
    curr: "IfaceParentDecl"

    def __init__(
        self, iface: "IfaceDecl", prev: "IfaceParentDecl", curr: "IfaceParentDecl"
    ):
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

    iface: Optional["IfaceDecl"]
    other: list["IfaceParentDecl"]

    def __init__(
        self,
        last: "IfaceParentDecl",
        other: list["IfaceParentDecl"],
    ):
        self.loc = last.loc
        self.iface = last.parent
        self.other = other

    def notes(self):
        for n in self.other:
            yield RecursiveExtensionNote(n)


@dataclass
class RecursiveInclusionError(DiagError):
    MSG = "recursive inclusion is found in {struct.description}"

    struct: Optional["StructDecl"]
    other: list["StructFieldDecl"]

    def __init__(
        self,
        last: "StructFieldDecl",
        other: list["StructFieldDecl"],
    ):
        self.loc = last.loc
        self.struct = last.parent
        self.other = other

    def notes(self):
        for n in self.other:
            yield RecursiveInclusionNote(n)
