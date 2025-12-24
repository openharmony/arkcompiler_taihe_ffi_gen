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

from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass, field
from typing import TextIO

from typing_extensions import override

from taihe.utils.outputs import FileKind, FileWriter, OutputManager

C_DEFAULT_INDENT = "    "
C_COMMENT_PREFIX = "// "

DEFAULT_CLANG_DIAGNOSTIC_SETTINGS = {
    "everything": "ignored",
    # "extra": "warning",
    # "all": "warning",
}


class IncludeGuard(ABC):
    @abstractmethod
    def gen_prologue(self) -> Generator[str, None, None]:
        """Generate the prologue lines for the header guard."""

    @abstractmethod
    def gen_epilogue(self) -> Generator[str, None, None]:
        """Generate the epilogue lines for the header guard."""


@dataclass(frozen=True)
class PragmaBasedIncludeGuard(IncludeGuard):
    def gen_prologue(self):
        yield "#pragma once"
        yield ""

    def gen_epilogue(self):
        yield from ()


@dataclass(frozen=True)
class MacroBasedIncludeGuard(IncludeGuard):
    identifier: str

    @staticmethod
    def from_path(path: str) -> "MacroBasedIncludeGuard":
        last_end = 0
        for pattern in ("include/", "inc/"):
            begin = path.rfind(pattern)
            end = 0 if begin == -1 else begin + len(pattern)
            last_end = max(last_end, end)
        path = path[last_end:]
        identifier = "".join([c if c.isalnum() else "_" for c in path]).upper()
        return MacroBasedIncludeGuard(identifier)

    def gen_prologue(self):
        yield f"#ifndef {self.identifier}"
        yield f"#define {self.identifier}"
        yield ""

    def gen_epilogue(self):
        yield ""
        yield f"#endif  // {self.identifier}"


@dataclass
class CMacroManager:
    """A mixin class that manages C/C++ preprocessor macros."""

    include_guard: IncludeGuard | None = field(kw_only=True, default=None)
    diag_settings: dict[str, str] = field(kw_only=True, default_factory=lambda: {})
    headers: dict[str, None] = field(kw_only=True, default_factory=lambda: {})

    def add_include(self, *headers: str):
        for header in headers:
            self.headers.setdefault(header, None)

    def gen_prologue(self):
        if self.include_guard is not None:
            yield from self.include_guard.gen_prologue()

        if self.diag_settings:
            yield "#pragma clang diagnostic push"
            for diag, level in self.diag_settings.items():
                yield f'#pragma clang diagnostic {level} "-W{diag}"'
            yield ""

        if self.headers:
            for header in self.headers:
                yield f'#include "{header}"'
            yield ""

    def gen_epilogue(self):
        if self.diag_settings:
            yield ""
            yield "#pragma clang diagnostic pop"

        if self.include_guard is not None:
            yield from self.include_guard.gen_epilogue()


class CSourceWriter(FileWriter, CMacroManager):
    """Represents a C or C++ source file."""

    def __init__(
        self,
        om: OutputManager,
        relative_path: str,
        file_kind: FileKind,
        *,
        include_guard: IncludeGuard | None = None,
    ):
        super().__init__(
            om,
            relative_path=relative_path,
            file_kind=file_kind,
            default_indent=C_DEFAULT_INDENT,
            comment_prefix=C_COMMENT_PREFIX,
        )
        CMacroManager.__init__(
            self,
            diag_settings={}
            if file_kind == FileKind.C_TEMPLATE
            else DEFAULT_CLANG_DIAGNOSTIC_SETTINGS,
            include_guard=include_guard,
        )

    @override
    def write_prologue(self, f: TextIO):
        for line in self.gen_prologue():
            f.write(f"{line}\n")

    @override
    def write_epilogue(self, f: TextIO):
        for line in self.gen_epilogue():
            f.write(f"{line}\n")


class CHeaderWriter(CSourceWriter):
    """Represents a C or C++ header file."""

    def __init__(
        self,
        om: OutputManager,
        relative_path: str,
        file_kind: FileKind,
    ):
        super().__init__(
            om,
            relative_path=relative_path,
            file_kind=file_kind,
            include_guard=PragmaBasedIncludeGuard(),
        )
