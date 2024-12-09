"""Manages diagnostics messages such as semantic errors."""

from collections.abc import Callable, Iterable
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import IntEnum
from sys import stderr
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Optional,
    TextIO,
    TypeVar,
)

if TYPE_CHECKING:
    from taihe.utils.sources import SourceLocation


T = TypeVar("T")


class AnsiStyle:
    RED = "\033[31m"
    GREEN = "\033[32m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

    RESET = "\033[39m"
    BRIGHT = "\033[1m"
    RESET_ALL = "\033[0m"


def _passthrough(x):
    return x


def _discard(x):
    del x
    return ""


FilterT = Callable[[str], str]


###################
# The Basic Types #
###################


class Level(IntEnum):
    NOTE = 0
    WARN = 1
    ERROR = 2
    FATAL = 3


@dataclass
class DiagBase:
    """The base class for diagnostic messages."""

    LEVEL: ClassVar[Level] = Level.ERROR
    LEVEL_DESC: ClassVar[str] = "<todo-diagbase-desc>"
    STYLE = AnsiStyle.CYAN

    MSG: ClassVar[str] = "<todo-diagbase-msg>"
    """The template for generating diagnostic message."""

    loc: Optional["SourceLocation"] = field(kw_only=True)
    """The source location where the diagnostic refers to."""

    def format_msg(self) -> str:
        """Returns the rendered diagnostic mesasge."""
        return self.MSG.format(**self.__dict__)

    def notes(self) -> Iterable["DiagNote"]:
        """Returns the associated notes."""
        return ()

    def _format(self, f: FilterT) -> str:
        return (
            f"{f(AnsiStyle.BRIGHT)}{self.loc or '???'}: "  # "example.taihe:7:20: "
            f"{f(self.STYLE)}{self.LEVEL_DESC}{f(AnsiStyle.RESET)}: "  # "error: "
            f"{self.format_msg()}{f(AnsiStyle.RESET_ALL)}"  # "redefinition of ..."
        )

    def __str__(self) -> str:
        return self._format(_discard)


######################################
# Base classes with different levels #
######################################


@dataclass
class DiagNote(DiagBase):
    LEVEL = Level.NOTE
    LEVEL_DESC = "note"
    STYLE = AnsiStyle.CYAN


@dataclass
class DiagWarn(DiagBase):
    LEVEL = Level.WARN
    LEVEL_DESC = "warning"
    STYLE = AnsiStyle.MAGENTA


@dataclass
class DiagError(DiagBase, Exception):
    LEVEL = Level.ERROR
    LEVEL_DESC = "error"
    STYLE = AnsiStyle.RED


@dataclass
class DiagFatalError(DiagError):
    LEVEL = Level.FATAL
    LEVEL_DESC = "fatal"


########################


@dataclass
class AdhocDiagNote(DiagNote):
    """Helper for constructing an ad-hoc DiagNote."""

    msg: str

    def format_msg(self) -> str:
        return self.msg


class DiagnosticsManager:
    """Manages diagnostic messages."""

    current_max_level: Level

    def __init__(self, out: TextIO = stderr):
        self.current_max_level = Level.NOTE
        self._out = out
        if self._out.isatty():
            self._color_filter_fn = _passthrough
        else:
            self._color_filter_fn = _discard

    def _write(self, s: str):
        self._out.write(s)

    def _flush(self):
        self._out.flush()

    # TODO: could be slow.
    def _render_source_location(self, loc: "SourceLocation"):
        MAX_LINE_NO_SPACE = 5
        if loc.line == 0:
            return

        line_contents = loc.file.read()
        if loc.line - 1 >= len(line_contents):
            line = len(line_contents)
            line_content = line_contents[line - 1].rstrip("\n")
            col_begin = len(line_content)
            col_end = len(line_content) + 1
        else:
            line = loc.line
            line_content = line_contents[line - 1].rstrip("\n")
            col_begin = min(loc.column - 1, len(line_content))
            col_end = min(loc.column - 1 + max(loc.span, 1), len(line_content) + 1)

        # The first line: content.
        self._write(f"{line:{MAX_LINE_NO_SPACE}} | {line_content}\n")

        # The second line: marker.
        markers = "^" * (col_end - col_begin)
        c = self._color_filter_fn
        self._write(
            f"{'':{MAX_LINE_NO_SPACE}} | "
            f"{c(AnsiStyle.GREEN + AnsiStyle.BRIGHT)}"
            f"{'':{col_begin}}{markers}{c(AnsiStyle.RESET_ALL)}\n"
        )

    def _render(self, d: DiagBase):
        self._write(f"{d._format(self._color_filter_fn)}\n")
        if d.loc:
            self._render_source_location(d.loc)

    def emit(self, diag: DiagBase):
        """Emits a new diagnostic message."""
        self.current_max_level = max(self.current_max_level, diag.LEVEL)
        self._render(diag)
        for n in diag.notes():
            self._render(n)
        stderr.flush()

    @contextmanager
    def capture_error(self):
        """Captures "error" and "fatal" diagnostics using context manager.

        Example:
        ```
        # Emit the error and prevent its propogation
        with diag_mgr.capture_error():
            foo();
            raise DiagError(...)
            bar();

        # Equivalent to:
        try:
            foo();
            raise DiagError(...)
            bar();
        except DiagError as e:
            diag_mgr.emit(e)
        ```
        """
        try:
            yield None
        except DiagError as e:
            self.emit(e)

    def for_each(self, xs: Iterable[T], cb: Callable[[T], bool | None]) -> bool:
        """Calls `cb` for each element. Records and recovers from `DiagError`s.

        Returns `True` if no errors are encountered.
        """
        no_error = True
        for x in xs:
            try:
                if cb(x):
                    return True
            except DiagError as e:
                self.emit(e)
                no_error = False
        return no_error
