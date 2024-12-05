"""Manage output files."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T", bound="OutputBase")


class OutputBase(ABC, Generic[P]):
    """Base class reprensenting all kinds of generated code."""

    def __init__(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ): ...

    @classmethod
    def create(
        cls: type[T],
        tm: "OutputManager",
        filename: str,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        return tm.get_or_create(cls, filename, *args, **kwargs)

    @abstractmethod
    def save_as(self, file_path: Path): ...


class OutputManager:
    """Manage all target files."""

    def __init__(self):
        self.targets: dict[str, OutputBase] = {}

    def output_to(self, dst_dir: Path):
        for filename, target in self.targets.items():
            target.save_as(dst_dir / filename)

    def get_or_create(
        self,
        cls: type[T],
        filename: str,
        *args,
        **kwargs,
    ) -> T:
        if target := self.targets.get(filename):
            assert isinstance(target, cls)
            return target

        target = cls(*args, **kwargs)
        self.targets[filename] = target
        return target
