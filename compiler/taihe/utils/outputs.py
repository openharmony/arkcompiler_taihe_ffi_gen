"""Manage output files."""

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from types import TracebackType
from typing import Optional, TextIO

from typing_extensions import Self

DEFAULT_INDENT = "    "  # Four spaces


@dataclass
class OutputConfig:
    """Manages the creation and saving of output files."""

    dst_dir: Optional[Path] = None


class BaseWriter:
    def __init__(self, out: TextIO, default_indent: str = DEFAULT_INDENT):
        """Initialize a code writer with a writable output stream.

        Args:
            out: A writable stream object
            indent_unit: The string used for each level of indentation
            default_indent: The default indentation string
        """
        if not hasattr(out, "write"):
            raise ValueError("output_stream must be writable")

        self._out = out
        self._default_indent = default_indent
        self._current_indent = ""

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
        for line in lines:
            self.writeln(line)

    def write_block(self, text_block: str):
        """Writes a potentially multi-line text block.

        Args:
            text_block: The block of text to write
        """
        self.writelns(*text_block.splitlines())

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
    ):
        super().__init__(out=StringIO(), default_indent=default_indent)
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
