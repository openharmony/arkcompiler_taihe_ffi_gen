from typing import TextIO

from typing_extensions import override

from taihe.utils.outputs import DEFAULT_INDENT, FileWriter, OutputConfig


class CSourceWriter(FileWriter):
    """Represents a C or C++ source file."""

    @override
    def __init__(self, oc: OutputConfig, path: str, indent_unit: str = DEFAULT_INDENT):
        super().__init__(
            oc,
            path=path,
            default_indent=indent_unit,
            comment_prefix="// ",
        )
        self.headers: dict[str, None] = {}

    @override
    def write_prologue(self, f: TextIO):
        for header in self.headers:
            f.write(f'#include "{header}"\n')

    def add_include(self, *headers: str):
        for header in headers:
            self.headers.setdefault(header, None)


class CHeaderWriter(CSourceWriter):
    """Represents a C or C++ header file."""

    @override
    def write_prologue(self, f: TextIO):
        f.write(f"#pragma once\n")
        super().write_prologue(f)
