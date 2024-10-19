from dataclasses import dataclass

from taihe.utils.diagnostics import DiagError, DiagNote
from taihe.utils.sources import SourceLocation


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
