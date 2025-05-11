"""Manage output files."""

import inspect
import os
import os.path
import sys
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum, auto
from io import StringIO
from pathlib import Path
from types import FrameType, TracebackType
from typing import Optional, TextIO

from typing_extensions import Self

DEFAULT_INDENT = "    "  # Four spaces


class DebugLevel(Enum):
    """Controls the code-generator debug info.

    When enabled, the generated code would contain comments, representing the
    location of Python code which generates.
    """

    NONE = auto()
    """Don't print any debug info."""
    CONCISE = auto()
    """Prints function and line number."""
    VERBOSE = auto()
    """Besides CONSICE, also prints code snippet. Could be slow."""


@dataclass
class OutputConfig:
    """Manages the creation and saving of output files."""

    dst_dir: Optional[Path] = None
    debug_level: DebugLevel = DebugLevel.NONE


class BaseWriter:
    def __init__(
        self,
        out: TextIO,
        *,
        comment_prefix: str,
        default_indent: str,
        debug_level: DebugLevel = DebugLevel.NONE,
    ):
        """Initialize a code writer with a writable output stream.

        Args:
            out: A writable stream object
            comment_prefix: The prefix for line-comment, for instance, "// " for C++
            default_indent: The default indentation string for each level of indentation
            debug_level: see `DebugLevel` for details
        """
        if not hasattr(out, "write"):
            raise ValueError("output_stream must be writable")

        self._out = out
        self._default_indent = default_indent
        self._current_indent = ""
        self._debug_level = debug_level
        self._comment_prefix = comment_prefix

    def writeln(self, line: str = ""):
        """Writes a single-line string.

        Args:
            line: The line to write (must not contain newlines)
        """
        assert "\n" not in line, "use write_block to write multi-line text block"

        if not line:
            # Don't use indent for empty lines
            self._out.write("\n")
            return

        self._out.write(self._current_indent)
        self._out.write(line)
        self._out.write("\n")

    def writelns(self, *lines: str):
        """Writes multiple one-line strings.

        Args:
            *lines: One or more lines to write
        """
        self._write_debug(skip=2)
        for line in lines:
            self.writeln(line)

    def write_block(self, text_block: str):
        """Writes a potentially multi-line text block.

        Args:
            text_block: The block of text to write
        """
        self.writelns(*text_block.splitlines())

    def write_comment(self, comment: str):
        """Writes a comment block, prefixing each line with the comment prefix.

        Indents the comment block according to the current indentation level.
        Handles multi-line comments by splitting the input string.

        Args:
            comment: The comment text to write. Can be multi-line.
        """
        for line in comment.splitlines():
            self._out.write(self._current_indent)
            self._out.write(self._comment_prefix)
            self._out.write(line)
            self._out.write("\n")

    def _write_debug(self, *, skip: int):
        if self._debug_level == DebugLevel.NONE:
            return
        self.write_comment(
            _format_frame(
                sys._getframe(skip),  # type: ignore
                show_source=self._debug_level == DebugLevel.VERBOSE,
            )
        )

    @contextmanager
    def indented(
        self, prologue: str = "", epilogue: str = "", indent: str | None = None
    ) -> Generator[Self, None, None]:
        """Context manager that indents code within its scope.

        Args:
            prologue: Optional text to write before indentation
            epilogue: Optional text to write after indentation
            indent: Optional string to use for indentation (overrides default)

        Returns:
            A context manager that yields this BaseWriter
        """
        self._write_debug(skip=3)
        if prologue:
            self.writeln(prologue)
        previous_indent = self._current_indent
        self._current_indent += self._default_indent if indent is None else indent
        try:
            yield self
        finally:
            self._current_indent = previous_indent
            if epilogue:
                self.writeln(epilogue)


class FileWriter(BaseWriter):
    def __init__(
        self,
        oc: OutputConfig,
        path: str,
        *,
        default_indent: str = DEFAULT_INDENT,
        comment_prefix: str,
    ):
        super().__init__(
            out=StringIO(),
            default_indent=default_indent,
            comment_prefix=comment_prefix,
            debug_level=oc.debug_level,
        )
        assert oc.dst_dir
        self._path = oc.dst_dir / path

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        del exc_val, exc_tb

        # Discard on exception
        if not exc_type:
            self.save_as(self._path)

        # Propagate the exception if exists
        return False

    def write_prologue(self, f: TextIO):
        del f

    def save_as(self, file_path: Path):
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, "w", encoding="utf-8") as dst:
            assert isinstance(self._out, StringIO)
            self.write_prologue(dst)
            dst.write(self._out.getvalue())


def _format_frame(f: FrameType, show_source: bool = False) -> str:
    # For /a/b/c/d/e.py, only keep FILENAME_KEEP directories, resulting "c/d/e.py"
    FILENAME_KEEP = 3

    file_name = f.f_code.co_filename
    parts = file_name.split(os.sep)
    if len(parts) > FILENAME_KEEP:
        file_name = os.path.join(*parts[-FILENAME_KEEP:])

    base_format = f"CODEGEN-DEBUG: {f.f_code.co_name} in {file_name}:{f.f_lineno}"

    if show_source:
        try:
            lines, start_lineno = inspect.getsourcelines(f.f_code)
            # Adjust for the actual line number within the retrieved block
            line_index = f.f_lineno - start_lineno
            if 0 <= line_index < len(lines):
                source_line = lines[line_index].strip()
                return f"{base_format} -> {source_line}"
        except (TypeError, OSError):
            # Handle cases where source code is not available (e.g., compiled code)
            pass

    return base_format
