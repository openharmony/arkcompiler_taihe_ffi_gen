# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Manage output files."""

import os
from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass, field
from enum import Enum, auto
from io import StringIO
from pathlib import Path
from sys import _getframe, stderr, stdout  # type: ignore
from types import FrameType, TracebackType
from typing import Literal, TextIO

from typing_extensions import Self, override


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


IndentationLevel = tuple[str, ...]


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
            comment_prefix: The prefix for line-comment
            default_indent: The default indentation string for each level of indentation
            newline: The newline character(s) to use
            debug_level: see `DebugLevel` for details
        """
        self._out = out
        self._comment_prefix = comment_prefix
        self._default_indent = default_indent
        self._current_indent: IndentationLevel = ()
        self._indent_stack: list[IndentationLevel] = []
        self._debug_level = debug_level

    @property
    def comment_prefix(self) -> str:
        return self._comment_prefix

    @property
    def default_indent(self) -> str:
        return self._default_indent

    @property
    def current_indent(self) -> IndentationLevel:
        return self._current_indent

    @property
    def indent_stack(self) -> Sequence[IndentationLevel]:
        return self._indent_stack

    def newline(self, _show_debug: bool = True):
        """Writes a newline character."""
        if _show_debug:
            self._write_debug(_getframe(1))

        self._out.write("\n")

    def writeln(self, line: str = "", _show_debug: bool = True):
        """Writes a single-line string.

        Args:
            line: The line to write (must not contain newlines)
        """
        if _show_debug:
            self._write_debug(_getframe(1))

        assert "\n" not in line, "use write_block to write multi-line text block"
        # don't write indentation for empty lines
        if line:
            self._out.write("".join(self._current_indent))
            self._out.write(line)
        self._out.write("\n")

    def writelns(self, *lines: str, _show_debug: bool = True):
        """Writes multiple one-line strings.

        Args:
            *lines: One or more lines to write
        """
        if _show_debug:
            self._write_debug(_getframe(1))

        for line in lines:
            self.writeln(line, _show_debug=False)

    def write_block(self, text_block: str, *, _show_debug: bool = True):
        """Writes a potentially multi-line text block.

        Args:
            text_block: The block of text to write
        """
        if _show_debug:
            self._write_debug(_getframe(1))

        for line in text_block.splitlines():
            self.writeln(line, _show_debug=False)

    def write_comment(self, comment: str, *, _show_debug: bool = True):
        """Writes a comment block, prefixing each line with the comment prefix.

        Indents the comment block according to the current indentation level.
        Handles multi-line comments by splitting the input string.

        Args:
            comment: The comment text to write. Can be multi-line.
        """
        if _show_debug:
            self._write_debug(_getframe(1))

        for line in comment.splitlines():
            self.writeln(self._comment_prefix + line, _show_debug=False)

    @contextmanager
    def set_indent(
        self,
        indent: IndentationLevel,
        *,
        _show_debug: bool = True,
    ) -> Iterator[Self]:
        if _show_debug:
            self._write_debug(_getframe(2))

        self._indent_stack.append(self._current_indent)
        self._current_indent = indent
        try:
            yield self
        finally:
            self._current_indent = self._indent_stack.pop()

    @contextmanager
    def inc_indent(
        self,
        indent: str | None = None,
        *,
        _show_debug: bool = True,
    ) -> Iterator[Self]:
        if _show_debug:
            self._write_debug(_getframe(2))

        if indent is None:
            indent = self._default_indent
        new_indent = (*self._current_indent, indent)
        with self.set_indent(new_indent, _show_debug=False) as writer:
            yield writer

    @contextmanager
    def dec_indent(self, *, _show_debug: bool = True) -> Iterator[Self]:
        if _show_debug:
            self._write_debug(_getframe(2))

        assert self._current_indent, "cannot decrease indentation level below 0"
        new_indent = self._current_indent[:-1]
        with self.set_indent(new_indent, _show_debug=False) as writer:
            yield writer

    @contextmanager
    def indented(
        self,
        prologue: str | None,
        epilogue: str | None,
        *,
        indent: str | None = None,
        _show_debug: bool = True,
    ) -> Iterator[Self]:
        """Context manager that indents code within its scope.

        Args:
            prologue: Optional text to write before indentation
            epilogue: Optional text to write after indentation
            indent: Optional string to use for indentation (overrides default)

        Returns:
            A context manager that yields this BaseWriter
        """
        if _show_debug:
            self._write_debug(_getframe(2))

        if prologue is not None:
            self.writeln(prologue, _show_debug=False)
        with self.inc_indent(indent, _show_debug=False) as writer:
            yield writer
        if epilogue is not None:
            self.writeln(epilogue, _show_debug=False)

    def write_label(self, line: str, *, _show_debug: bool = True):
        """Writes a label line, which reduces indentation by one level.

        Args:
            line: The label text to write (must not contain newlines)
        """
        if _show_debug:
            self._write_debug(_getframe(1))

        with self.dec_indent(_show_debug=False) as writer:
            writer.writeln(line, _show_debug=False)

    def _write_debug(self, f: FrameType):
        if self._debug_level == DebugLevel.NONE:
            return

        taihe_dir = Path(__file__).parent.parent
        file_name = Path(f.f_code.co_filename).relative_to(taihe_dir).as_posix()
        self.write_comment(
            f"CODEGEN-DEBUG: {f.f_code.co_name} in {file_name}:{f.f_lineno}",
            _show_debug=False,
        )


@dataclass(frozen=True)
class VariableGroup:
    var_name: str

    def __str__(self):
        return self.var_name


@dataclass(frozen=True)
class GeneratedFileGroup:
    var_name: str

    def __str__(self):
        return self.var_name


@dataclass(frozen=True)
class RuntimeSourceGroup:
    var_name: str

    def __str__(self):
        return self.var_name


GEN_C_SRC_GROUP = GeneratedFileGroup("TAIHE_GEN_C_SRC")
GEN_CXX_SRC_GROUP = GeneratedFileGroup("TAIHE_GEN_CXX_SRC")
RUNTIME_C_SRC_GROUP = RuntimeSourceGroup("TAIHE_RUNTIME_C_SRC_INNER")
RUNTIME_CXX_SRC_GROUP = RuntimeSourceGroup("TAIHE_RUNTIME_CXX_SRC_INNER")


class FileWriter(BaseWriter):
    def __init__(
        self,
        om: "OutputManager",
        relative_path: str,
        *,
        group: GeneratedFileGroup | None,
        default_indent: str,
        comment_prefix: str,
    ):
        super().__init__(
            out=StringIO(),
            default_indent=default_indent,
            comment_prefix=comment_prefix,
            debug_level=om.debug_level,
        )
        self._om = om
        self._relative_path = relative_path
        self._group = group

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        del exc_val, exc_tb, exc_type
        with self._om.open(self._relative_path, self._group) as f:
            self.write_prologue(f)
            self.write_body(f)
            self.write_epilogue(f)
        return False

    def write_body(self, f: TextIO):
        assert isinstance(self._out, StringIO)
        f.write(self._out.getvalue())

    def write_prologue(self, f: TextIO):
        del f

    def write_epilogue(self, f: TextIO):
        del f


@dataclass
class OutputConfig(ABC):
    debug_level: DebugLevel = field(default=DebugLevel.NONE, kw_only=True)

    @abstractmethod
    def build(self) -> "OutputManager":
        """Builds an OutputManager based on this configuration."""


class OutputManager(ABC):
    """Abstract base class for output managers."""

    debug_level: DebugLevel

    def __init__(self, *, debug_level: DebugLevel):
        self.debug_level = debug_level

    def post_generate(self) -> None:
        """Hook called after all files have been generated."""
        return

    def record_variable(self, group: VariableGroup, value: str):
        """Records a variable for later use in code generation."""
        return

    def record_runtime_src(self, group: RuntimeSourceGroup, relative_path: str):
        """Records a runtime source file path."""
        return

    def record_generated_file(self, group: GeneratedFileGroup, relative_path: str):
        """Records a generated file path."""
        return

    def record_runtime_c_src(self, relative_path: str):
        self.record_runtime_src(RUNTIME_C_SRC_GROUP, relative_path)

    def record_runtime_cxx_src(self, relative_path: str):
        self.record_runtime_src(RUNTIME_CXX_SRC_GROUP, relative_path)

    @contextmanager
    def open(self, relative_path: str, group: GeneratedFileGroup | None = None):
        """Opens a file for writing."""
        if group is not None:
            self.record_generated_file(group, relative_path)

        with self._open_impl(relative_path) as f:
            yield f

    @abstractmethod
    def _open_impl(self, relative_path: str) -> AbstractContextManager[TextIO]:
        """Opens a file for writing."""


@dataclass
class NullOutputConfig(OutputConfig):
    def build(self) -> OutputManager:
        class NullOutputManager(OutputManager):
            def __init__(self, *, debug_level: DebugLevel):
                super().__init__(debug_level=debug_level)

            def _open_impl(self, relative_path: str):
                return Path(os.devnull).open("w", encoding="utf-8")

        return NullOutputManager(debug_level=self.debug_level)


@dataclass
class DebugOutputConfig(OutputConfig):
    target_desc: Literal["stderr", "stdout"]

    def build(self) -> OutputManager:
        class DebugOutputManager(OutputManager):
            def __init__(
                self,
                target_desc: Literal["stderr", "stdout"],
                *,
                debug_level: DebugLevel,
            ):
                super().__init__(debug_level=debug_level)
                match target_desc:
                    case "stderr":
                        self.target = stderr
                    case "stdout":
                        self.target = stdout

            @contextmanager
            def _open_impl(self, relative_path: str):
                self.target.write(f"=== Open file: {relative_path} ===\n")
                yield self.target
                self.target.write(f"=== Close file: {relative_path} ===\n")

        return DebugOutputManager(self.target_desc, debug_level=self.debug_level)


@dataclass
class BasicOutputConfig(OutputConfig):
    dst_dir: Path

    def build(self) -> OutputManager:
        return BasicOutputManager(
            self.dst_dir,
            debug_level=self.debug_level,
        )


class BasicOutputManager(OutputManager):
    """Manages the creation and saving of output files."""

    def __init__(
        self,
        dst_dir: Path,
        *,
        debug_level: DebugLevel,
    ):
        super().__init__(debug_level=debug_level)
        self.dst_dir = dst_dir

    def _open_impl(self, relative_path: str):
        file_path = self.dst_dir / relative_path
        file_path.parent.mkdir(exist_ok=True, parents=True)
        return file_path.open("w", encoding="utf-8")


#################################
# Cmake code generation related #
#################################


class CMakeWriter(FileWriter):
    """Represents a CMake file."""

    def __init__(
        self,
        om: OutputManager,
        relative_path: str,
    ):
        super().__init__(
            om,
            relative_path,
            default_indent="    ",
            comment_prefix="# ",
            group=None,
        )
        self.headers: dict[str, None] = {}


@dataclass
class CMakeOutputConfig(BasicOutputConfig):
    runtime_include_dir: Path = field(kw_only=True)
    runtime_src_dir: Path = field(kw_only=True)

    def build(self) -> OutputManager:
        return CMakeOutputManager(
            self.dst_dir,
            debug_level=self.debug_level,
            runtime_include_dir=self.runtime_include_dir,
            runtime_src_dir=self.runtime_src_dir,
        )


class CMakeOutputManager(BasicOutputManager):
    """Manages the generation of CMake files for Taihe runtime."""

    runtime_include_dir: Path
    runtime_src_dir: Path

    RUNTIME_SRC_DIR = "TAIHE_RUNTIME_SRC_DIR_INNER"
    RUNTIME_INCLUDE = "TAIHE_RUNTIME_INCLUDE"
    GEN_DIR = "TAIHE_GEN_DIR"
    GEN_INCLUDE = "TAIHE_GEN_INCLUDE"
    GEN_SRC = "TAIHE_GEN_SRC"
    RUNTIME_SRC = "TAIHE_RUNTIME_SRC"

    def __init__(
        self,
        dst_dir: Path,
        *,
        debug_level: DebugLevel,
        runtime_include_dir: Path,
        runtime_src_dir: Path,
    ):
        super().__init__(dst_dir, debug_level=debug_level)

        self.runtime_include_dir = runtime_include_dir
        self.runtime_src_dir = runtime_src_dir

        self.variables: dict[VariableGroup, list[str]] = {}
        self.runtime_src_files: dict[RuntimeSourceGroup, list[str]] = {}
        self.gen_src_files: dict[GeneratedFileGroup, list[str]] = {}

        self.target = CMakeWriter(self, "TaiheGenerated.cmake")

    @override
    def record_variable(self, group: VariableGroup, value: str):
        self.variables.setdefault(group, []).append(value)

    @override
    def record_runtime_src(self, group: RuntimeSourceGroup, relative_path: str):
        self.runtime_src_files.setdefault(group, []).append(relative_path)

    @override
    def record_generated_file(self, group: GeneratedFileGroup, relative_path: str):
        self.gen_src_files.setdefault(group, []).append(relative_path)

    @override
    def post_generate(self):
        with self.target:
            self.emit_prev_settings()
            self.emit_core_settings()
            self.emit_post_settings()

    def emit_prev_settings(self):
        with self.target.indented(
            f"if(NOT DEFINED {self.RUNTIME_INCLUDE})",
            f"endif()",
        ):
            with self.target.indented(
                f"set({self.RUNTIME_INCLUDE}",
                f")",
            ):
                self.target.writelns(
                    f'"{self.runtime_include_dir.as_posix()}"',
                )
        with self.target.indented(
            f"if(NOT DEFINED {self.RUNTIME_SRC_DIR})",
            f"endif()",
        ):
            with self.target.indented(
                f"set({self.RUNTIME_SRC_DIR}",
                f")",
            ):
                self.target.writelns(
                    f'"{self.runtime_src_dir.as_posix()}"',
                )
        with self.target.indented(
            f"if(NOT DEFINED {self.GEN_DIR})",
            f"endif()",
        ):
            with self.target.indented(
                f"set({self.GEN_DIR}",
                f")",
            ):
                self.target.writelns(
                    "${CMAKE_CURRENT_LIST_DIR}",
                )
        with self.target.indented(
            f"set({self.GEN_INCLUDE}",
            f")",
        ):
            self.target.writelns(
                f"${{{self.GEN_DIR}}}/include",
            )

    def emit_core_settings(self):
        for group, values in self.variables.items():
            with self.target.indented(
                f"set({group}",
                f")",
            ):
                for value in values:
                    self.target.writelns(value)
        for group, relative_paths in self.runtime_src_files.items():
            with self.target.indented(
                f"set({group}",
                f")",
            ):
                for relative_path in relative_paths:
                    self.target.writelns(f"${{{self.RUNTIME_SRC_DIR}}}/{relative_path}")
        for group, relative_paths in self.gen_src_files.items():
            with self.target.indented(
                f"set({group}",
                f")",
            ):
                for relative_path in relative_paths:
                    self.target.writelns(f"${{{self.GEN_DIR}}}/{relative_path}")

    def emit_post_settings(self):
        with self.target.indented(
            f"set({self.RUNTIME_SRC}",
            f")",
        ):
            self.target.writelns(
                f"${{{RUNTIME_C_SRC_GROUP}}}",
                f"${{{RUNTIME_CXX_SRC_GROUP}}}",
            )
        with self.target.indented(
            f"set({self.GEN_SRC}",
            f")",
        ):
            self.target.writelns(
                f"${{{GEN_C_SRC_GROUP}}}",
                f"${{{GEN_CXX_SRC_GROUP}}}",
            )
        with self.target.indented(
            f"set_source_files_properties(",
            f")",
        ):
            self.target.writelns(
                f"${{{GEN_CXX_SRC_GROUP}}}",
                f"${{{RUNTIME_CXX_SRC_GROUP}}}",
                # setting
                f"PROPERTIES",
                f"LANGUAGE CXX",
                f'COMPILE_FLAGS "-std=c++17"',
            )
