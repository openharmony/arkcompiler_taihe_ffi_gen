"""Manage output files."""

from abc import ABC, abstractmethod
from io import StringIO
from os import makedirs, path
from pathlib import Path
from typing import Generic, ParamSpec, TypeVar

from typing_extensions import override

P = ParamSpec("P")
T = TypeVar("T", bound="OutputBase")


class OutputBase(ABC, Generic[P]):
    """Abstract base class for all types of generated output.

    Created, managed and saved to file via an `OutputManager`.
    """

    def __init__(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        """Initialize the output instance."""

    @classmethod
    def create(
        cls: type[T],  # pyre-ignore
        tm: "OutputManager",
        filename: str,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        """Create or retrieve an output instance via the manager."""
        return tm.get_or_create(cls, filename, *args, **kwargs)

    @abstractmethod
    def save_as(self, file_path: Path):
        """Save the output to the specified file path."""


class COutputBuffer(OutputBase[bool]):
    """Represents a C or C++ target file."""

    def __init__(self, is_header: bool):
        self.is_header = is_header
        self.headers: dict[str, None] = {}
        self.code = StringIO()

    @override
    def save_as(self, file_path: Path):
        if not path.exists(file_path.parent):
            makedirs(file_path.parent, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as dst:
            if self.is_header:
                dst.write(f"#pragma once\n")
            for header in self.headers:
                dst.write(f'#include "{header}"\n')
            dst.write(self.code.getvalue())

    def write(self, code: str):
        self.code.write(code)

    def include(self, *headers: str, back=False):
        for header in headers:
            self.headers.setdefault(header, None)


class OutputManager:
    """Manages the creation and saving of output files."""

    def __init__(self):
        """Initialize with an empty cache."""
        self.targets: dict[str, OutputBase] = {}

    def output_to(self, dst_dir: Path):
        """Save all managed outputs to a target directory."""
        for filename, target in self.targets.items():
            target.save_as(dst_dir / filename)

    def get_or_create(
        self,
        cls: type[T],
        filename: str,
        *args,
        **kwargs,
    ) -> T:
        """Get or create an output instance by filename."""
        if target := self.targets.get(filename):
            assert isinstance(target, cls)
            return target

        target = cls(*args, **kwargs)
        self.targets[filename] = target
        return target
