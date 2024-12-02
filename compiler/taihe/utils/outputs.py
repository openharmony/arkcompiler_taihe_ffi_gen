"""Manage output files."""

from abc import ABC, abstractmethod
from os import PathLike


class OutputBase(ABC):
    """Base class reprensenting all kinds of generated code."""

    filename: str

    def __init__(self, filename):
        self.filename = filename

    @abstractmethod
    def output_to(self, dst_dir: PathLike): ...

    @abstractmethod
    def show(self): ...


class OutputManager:
    """Manage all target files."""

    def __init__(self):
        self.targets: list[OutputBase] = []

    def output_to(self, dst_dir: PathLike):
        for target in self.targets:
            target.output_to(dst_dir)

    def show(self):
        for target in self.targets:
            target.show()

    def add(self, target: OutputBase):
        self.targets.append(target)
