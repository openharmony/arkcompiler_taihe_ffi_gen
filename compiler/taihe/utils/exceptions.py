from dataclasses import dataclass
from typing import TYPE_CHECKING

from taihe.utils.diagnostics import DiagError, DiagNote
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.declarations import Decl


@dataclass
class DefinitionConflictDiagNote(DiagNote):
    MSG = "previously defined here"


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
class TypeNotExistError(DiagError):
    MSG = "use of undeclared type {ty!r}"

    ty: str
