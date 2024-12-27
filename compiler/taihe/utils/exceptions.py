from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from taihe.utils.diagnostics import DiagError, DiagNote, DiagWarn
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        AttrItemDecl,
        DataTypeDecl,
        EnumItemDecl,
        IfaceDecl,
        IfaceParentDecl,
        NamedDecl,
        Package,
        PackageLevelDecl,
        TypeAliasDecl,
        TypeRefDecl,
    )


@dataclass
class PackageRedefNote(DiagNote):
    MSG = "previously occurred here"


@dataclass
class PackageRedefError(DiagError):
    MSG = "package name {pkg!r} is duplicated"

    pkg_name: str
    prev_loc: Optional[SourceLocation] = field(kw_only=True)

    def notes(self):
        if self.prev_loc:
            yield PackageRedefNote(loc=self.prev_loc)


@dataclass
class DeclRedefNote(DiagNote):
    MSG = "conflict with {prev.description}"

    prev: "NamedDecl"

    def __init__(self, prev: "NamedDecl"):
        self.prev = prev
        self.loc = prev.loc


@dataclass
class DeclRedefError(DiagError):
    MSG = "redefinition of {current.description}"

    prev: "NamedDecl"
    current: "NamedDecl"

    def __init__(self, prev: "NamedDecl", current: "NamedDecl"):
        self.prev = prev
        self.current = current
        self.loc = current.loc

    def notes(self):
        if self.prev.loc:
            yield DeclRedefNote(self.prev)


@dataclass
class EnumValueConflictNote(DiagNote):
    MSG = "conflict with {prev.description}"

    prev: "EnumItemDecl"

    def __init__(self, prev: "EnumItemDecl"):
        self.prev = prev
        self.loc = prev.loc


@dataclass
class EnumValueConflictError(DiagError):
    MSG = "value {current.value} of {current.description} is repeated"

    prev: "EnumItemDecl"
    current: "EnumItemDecl"

    def __init__(self, prev: "EnumItemDecl", current: "EnumItemDecl"):
        self.prev = prev
        self.current = current
        self.loc = current.loc

    def notes(self):
        if self.prev.loc:
            yield DeclRedefNote(self.prev)


@dataclass
class AttrRedefNote(DiagNote):
    MSG = "conflict with {prev.description}"

    prev: "AttrItemDecl"

    def __init__(self, prev: "AttrItemDecl"):
        self.prev = prev
        self.loc = prev.loc


@dataclass
class AttrRedefError(DiagError):
    MSG = "duplicate {current.description}"

    prev: "AttrItemDecl"
    current: "AttrItemDecl"

    def __init__(self, prev: "AttrItemDecl", current: "AttrItemDecl"):
        self.prev = prev
        self.current = current
        self.loc = current.loc

    def notes(self):
        if self.prev.loc:
            yield AttrRedefNote(self.prev)


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
class ExtendsTypeError(DiagError):
    MSG = "expected an interface, got {name!r}"

    name: str

    def __init__(self, decl: "IfaceParentDecl"):
        self.loc = decl.ty_ref.loc
        self.name = decl.ty_ref.symbol


@dataclass
class DuplicateExtendsNote(DiagNote):
    MSG = "previously extended here"


@dataclass
class DuplicateExtendsWarn(DiagWarn):
    MSG = "{parent_iface.description} is extended multiple times by {iface.description}"

    iface: "IfaceDecl"
    parent_iface: "IfaceDecl"
    prev_loc: Optional["SourceLocation"]

    def notes(self):
        if self.prev_loc:
            yield DuplicateExtendsNote(loc=self.prev_loc)


@dataclass
class RecursiveExtensionNote(DiagNote):
    MSG = "extended by {iface.description}"

    iface: "IfaceDecl"

    def __init__(
        self,
        last: tuple["IfaceDecl", "TypeRefDecl"],
    ):
        self.loc = last[1].loc
        self.iface = last[0]


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
class RecursiveInclusionNote(DiagNote):
    MSG = "referenced by {decl.description}"

    decl: "DataTypeDecl"

    def __init__(
        self,
        last: tuple["DataTypeDecl", "TypeRefDecl"],
    ):
        self.loc = last[1].loc
        self.decl = last[0]


@dataclass
class RecursiveInclusionError(DiagError):
    MSG = "cycle detected in {decl.description}"

    decl: "DataTypeDecl"
    other: list[tuple["DataTypeDecl", "TypeRefDecl"]]

    def __init__(
        self,
        last: tuple["DataTypeDecl", "TypeRefDecl"],
        other: list[tuple["DataTypeDecl", "TypeRefDecl"]],
    ):
        self.loc = last[1].loc
        self.decl = last[0]
        self.other = other

    def notes(self):
        for n in self.other:
            yield RecursiveInclusionNote(n)


@dataclass
class RecursiveTypeAliasNote(DiagNote):
    MSG = "from here"

    def __init__(
        self,
        last: "TypeAliasDecl",
    ):
        self.loc = last.ty_ref.loc


@dataclass
class RecursiveTypeAliasError(DiagError):
    MSG = "recursive typedef"

    other: list["TypeAliasDecl"]

    def __init__(
        self,
        last: "TypeAliasDecl",
        other: list["TypeAliasDecl"],
    ):
        self.loc = last.ty_ref.loc
        self.other = other

    def notes(self):
        for n in self.other:
            yield RecursiveTypeAliasNote(n)
