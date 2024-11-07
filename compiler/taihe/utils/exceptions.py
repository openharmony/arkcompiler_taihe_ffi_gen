from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from taihe.utils.diagnostics import DiagError, DiagFatalError, DiagNote
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.declarations import Decl


@dataclass
class DefinitionConflictDiagNote(DiagNote):
    MSG = "previously defined here"


@dataclass
class EnumValueCollisionDiagNote(DiagNote):
    MSG = "first use"


@dataclass
class RecursiveInclusionNote(DiagNote):
    MSG = "the struct is included in {struct.name}"

    def __init__(self, loc: Optional["SourceLocation"], struct: "Decl"):
        self.loc = loc
        self.struct = struct


@dataclass
class PackageRedefDiagError(DiagError):
    MSG = "redefinition of package {pkg_name!r}"

    pkg_name: str
    prev: SourceLocation

    def notes(self):
        yield DefinitionConflictDiagNote(loc=self.prev)


@dataclass
class DeclRedefDiagError(DiagError):
    MSG = "redefinition of {current.description}"

    prev: "Decl"
    current: "Decl"

    def __init__(
        self,
        prev: "Decl",
        current: "Decl",
    ):
        self.prev = prev
        self.current = current
        self.loc = current.loc

    def notes(self):
        yield DefinitionConflictDiagNote(loc=self.prev.loc)


@dataclass
class EnumValueCollisionError(DiagError):
    MSG = "discriminant value '{value}' already exists"

    prev: "Decl"
    current: "Decl"
    value: int

    def __init__(self, prev: "Decl", current: "Decl", value: int):
        self.prev = prev
        self.current = current
        self.loc = current.loc
        self.value = value

    def notes(self):
        yield EnumValueCollisionDiagNote(loc=self.prev.loc)


@dataclass
class PackageNotExistError(DiagFatalError):
    MSG = "package {pkg!r} not found"

    pkg: str

    def __init__(
        self,
        pkg: str,
        loc: Optional["SourceLocation"],
    ):
        self.pkg = pkg
        self.loc = loc


@dataclass
class DeclNotExistError(DiagError):
    MSG = "declaration {decl!r} not found"

    decl: str

    def __init__(
        self,
        decl: str,
        loc: Optional["SourceLocation"],
    ):
        self.decl = decl
        self.loc = loc


@dataclass
class SymbolConflictWithNamespaceError(DiagError):
    MSG = "declaration of {current.description} in package {pkg_name!r} shadows a file-level declaration"

    current: "Decl"

    def __init__(self, current: "Decl", pkg_name: str):
        self.current = current
        self.loc = current.loc
        self.pkg_name = pkg_name


@dataclass
class RecursiveInclusionError(DiagError):
    MSG = "recursive inclusion is found in {struct.name}"

    def __init__(
        self,
        loc: Optional["SourceLocation"],
        struct: "Decl",
        note: list[tuple[Optional["SourceLocation"], "Decl"]],
    ):
        self.loc = loc
        self.struct = struct
        self.note = note

    def notes(self):
        for n in self.note:
            yield RecursiveInclusionNote(loc=n[0], struct=n[1])


@dataclass
class NotATypeError(DiagError):
    MSG = "{name!r} is not a type"

    decl: str

    def __init__(
        self,
        decl: str,
        loc: Optional["SourceLocation"],
    ):
        self.decl = decl
        self.loc = loc


@dataclass
class QualifierError(DiagError):
    MSG = "'mut' cannot be applied to {ty!r}"

    ty: str
    current: "Decl"

    def __init__(
        self,
        current: "Decl",
        ty: str,
    ):
        self.current = current
        self.loc = current.loc
        self.ty = ty


@dataclass
class TypeNotExistError(DiagError):
    MSG = "use of undeclared type {ty!r}"

    ty: str
