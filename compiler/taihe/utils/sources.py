"""Manages source files."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from taihe.utils.diagnostics import DiagnosticsManager


@dataclass(frozen=True)
class SourceBase(ABC):
    """Base class reprensenting all kinds of source code."""

    source_identifier: str
    pkg_name: str

    def __str__(self) -> str:
        return f"Package {self.pkg_name} (in {self.source_identifier})"

    @abstractmethod
    def read(self) -> list[str]: ...


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
                sb.pkg_name, loc=SourceLocation(sb), prev_loc=SourceLocation(prev)
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


@dataclass
class SourceLocation:
    """Represents a location (either a position or a region) within a file."""

    file: SourceBase
    """Required: The source file associated with the location."""

    has_pos: bool

    start_row: int
    """Optional: The start line number (1-based)."""

    start_col: int
    """Optional: The start column number (1-based)."""

    stop_row: int
    """Optional: The stop line number (1-based)."""

    stop_col: int
    """Optional: The stop column number (1-based)."""

    def __init__(self, file: SourceBase, *pos: int):
        self.file = file

        if len(pos) == 4:
            self.start_row, self.start_col, self.stop_row, self.stop_col = pos
            self.has_pos = True
        elif len(pos) == 0:
            self.start_row, self.start_col, self.stop_row, self.stop_col = 0, 0, 0, 0
            self.has_pos = False
        else:
            raise ValueError()

    def __str__(self) -> str:
        r = self.file.source_identifier
        if self.has_pos:
            r = f"{r}:{self.start_row}:{self.start_col}"

        return r
