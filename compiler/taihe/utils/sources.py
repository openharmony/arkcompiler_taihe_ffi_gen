"""Manages source files."""

from collections.abc import Iterable
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path

from taihe.utils.diagnostics import DiagnosticsManager


@dataclass(frozen=True)
class SourceBase:
    """Base class reprensenting all kinds of source code."""

    source_identifier: str
    pkg_name: str

    def __str__(self) -> str:
        return f"Package {self.pkg_name} (in {self.source_identifier})"

    def read(self) -> list[str]:
        return ["<remember to implement SourceBase.read()!>"]


@dataclass(frozen=True)
class SourceFile(SourceBase):
    """Represents a file-based source code."""

    def read(self) -> list[str]:
        with open(self.source_identifier) as f:
            return f.readlines()


@dataclass(frozen=True)
class SourceBuffer(SourceBase):
    """Represents a string-based source code."""

    buf: str

    def read(self) -> list[str]:
        return self.buf.splitlines()


class SourceManager:
    """Manages all input files throughout the compilation."""

    _pkg_to_source: dict[str, SourceBase]

    def __init__(self):
        self._pkg_to_source = {}

    def _add(self, sb: SourceBase):
        # Avoid circular import
        from taihe.utils.exceptions import PackageRedefDiagError

        if prev := self._pkg_to_source.get(sb.pkg_name, None):
            raise PackageRedefDiagError(
                sb.pkg_name, prev=SourceLocation(prev), loc=SourceLocation(sb)
            )
        else:
            self._pkg_to_source[sb.pkg_name] = sb

    def add_buffer(self, pkg_name: str, buf: str, source_identifier: str = ""):
        sid = source_identifier or f"<source-buffer-{pkg_name}>"
        self._add(SourceBuffer(sid, pkg_name, buf))

    def add_file(self, path: PathLike):
        p = Path(path)
        pkg_name = p.stem
        self._add(SourceFile(str(p), pkg_name))

    def add_directory(self, path: PathLike, diag: DiagnosticsManager):
        """Adds all `.taihe` files inside a directory. Subdirectories are ignored."""
        d = Path(path)
        files = d.glob("*.taihe")
        diag.for_each(files, lambda f: self.add_file(f))

    def lookup(self, pkg_name: str) -> SourceBase | None:
        return self._pkg_to_source.get(pkg_name, None)

    @property
    def sources(self) -> Iterable[SourceBase]:
        return self._pkg_to_source.values()


@dataclass(slots=True)
class SourceLocation:
    """Represents a location (either a position or a region) within a file."""

    file: SourceBase
    """Required: The source file associated with the location."""

    line: int = 0
    """Optional: The line number (1-based). Use 0 if unavailable."""

    column: int = 0
    """Optional: The column number (1-based). Use 0 if unavailable."""

    span: int = field(kw_only=True, default=0)
    """Optional: The number of characters in the region.
    Use 0 if the location does not represent a region.

    This region is defined as `[column, column + span)` within the current line.
    Note that the region must NOT span multiple lines.
    """

    def __str__(self) -> str:
        r = self.file.source_identifier
        if self.line != 0:
            r = f"{r}:{self.line}"
            if self.column != 0:
                r = f"{r}:{self.column}"

        return r
