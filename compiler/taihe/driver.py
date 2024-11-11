"""Orchestrates the compilation process."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from taihe.parse.convert import AstConverter
from taihe.semantics.analysis import analyze_semantics
from taihe.semantics.declarations import PackageGroup
from taihe.semantics.format import pretty_print
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.sources import SourceManager


@dataclass
class CompilerInvocation:
    """Describes the options and intents for a compiler invocation.

    CompilerInvocation stores the high-level intent in a structured way, such
    as the input paths, the target for code generation. Generally speaking, it
    can be considered as the parsed and verified version of a compiler's
    command line flags.

    CompilerInvocation does not manage the internal state. Use
    `CompilerInstance` instead.
    """

    src_dirs: list[Path] = field(default_factory=lambda: [])

    # TODO: implement "CompilerBackend" and store the backend-specific options there?
    out_dir: Optional[Path] = None
    gen_author: bool = False
    gen_user: bool = False


class CompilerInstance:
    """Helper class for storing key objects.

    CompilerInstance holds key intermediate objects across the compilation
    process, such as the source manager and the diagnostics manager.

    It also provides utility methods for driving the compilation process.
    """

    invocation: CompilerInvocation
    diagnostics_manager: DiagnosticsManager

    source_manager: SourceManager
    package_group: PackageGroup

    def __init__(self, invocation: CompilerInvocation):
        self.invocation = invocation
        self.source_manager = SourceManager()
        self.diagnostics_manager = DiagnosticsManager()
        self.package_group = PackageGroup()

    ##########################
    # The compilation phases #
    ##########################

    def scan(self):
        for src_dir in self.invocation.src_dirs:
            self.source_manager.add_directory(Path(src_dir), self.diagnostics_manager)

    def parse(self):
        for src in self.source_manager.sources:
            conv = AstConverter(src, self.diagnostics_manager)
            pkg = conv.convert()
            self.package_group.add(pkg)

    def validate(self):
        analyze_semantics(self.package_group, self.diagnostics_manager)

    def generate(self):
        s = pretty_print(self.package_group)
        print(s)

    def run(self):
        self.scan()
        self.parse()
        self.validate()
        self.generate()
