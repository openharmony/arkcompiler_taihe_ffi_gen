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

from typing import TextIO

from typing_extensions import override

from taihe.utils.outputs import FileKind, FileWriter, OutputManager


class CSourceWriter(FileWriter):
    """Represents a C or C++ source file."""

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
            default_indent="    ",
            comment_prefix="// ",
        )
        self.headers: dict[str, None] = {}

    @override
    def write_prologue(self, f: TextIO):
        if self.desc.kind != FileKind.TEMPLATE:
            f.write("#pragma clang diagnostic push\n")
            f.write('#pragma clang diagnostic ignored "-Weverything"\n')
            f.write('#pragma clang diagnostic warning "-Wextra"\n')
            f.write('#pragma clang diagnostic warning "-Wall"\n')
            f.write('#pragma clang diagnostic ignored "-Wmissing-braces"\n')
            f.write("\n")
        for header in self.headers:
            f.write(f'#include "{header}"\n')
        if self.headers:
            f.write("\n")

    @override
    def write_epilogue(self, f: TextIO):
        if self.desc.kind != FileKind.TEMPLATE:
            f.write("\n")
            f.write("#pragma clang diagnostic pop\n")

    def add_include(self, *headers: str):
        for header in headers:
            self.headers.setdefault(header, None)


class CHeaderWriter(CSourceWriter):
    """Represents a C or C++ header file."""

    def __init__(
        self,
        om: OutputManager,
        relative_path: str,
        file_kind: FileKind,
    ):
        super().__init__(om, relative_path, file_kind)

    @property
    def guard_macro(self) -> str:
        path = self.desc.relative_path.split("/")
        try:
            index = path.index("include") + 1
        except ValueError:
            index = 0
        return "_".join(path[index:]).replace(".", "_").replace("/", "_").upper()

    @override
    def write_prologue(self, f: TextIO):
        f.write(f"#ifndef {self.guard_macro}\n")
        f.write(f"#define {self.guard_macro}\n")
        f.write("\n")
        super().write_prologue(f)

    @override
    def write_epilogue(self, f: TextIO):
        super().write_epilogue(f)
        f.write("\n")
        f.write(f"#endif  // {self.guard_macro}\n")
