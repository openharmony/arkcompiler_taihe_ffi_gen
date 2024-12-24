"""Orchestrates the compilation process."""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from taihe.codegen.generator import ABICodeGenerator
from taihe.codegen.kn_bridge_generator import KNBridgeGenerator

# from taihe.codegen.proj_cpp_generator import CppProjGenerator
from taihe.parse.convert import AstConverter
from taihe.semantics.analysis import analyze_semantics
from taihe.semantics.declarations import PackageGroup
from taihe.semantics.format import pretty_print
from taihe.utils.analyses import AnalysisManager
from taihe.utils.diagnostics import DiagnosticsManager, Level
from taihe.utils.outputs import OutputManager
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

    analysis_manager: AnalysisManager

    target_manager: OutputManager

    def __init__(self, invocation: CompilerInvocation):
        self.invocation = invocation
        self.source_manager = SourceManager()
        self.diagnostics_manager = DiagnosticsManager()
        self.package_group = PackageGroup()
        self.analysis_manager = AnalysisManager()
        self.target_manager = OutputManager()

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

    def show(self):
        pretty_print(self.package_group, sys.stdout)

    def generate(self):
        if self.diagnostics_manager.current_max_level >= Level.ERROR:
            return
        if not self.invocation.out_dir:
            return
        generator = ABICodeGenerator(self.target_manager, self.analysis_manager)
        generator.generate(self.package_group)
        self.target_manager.output_to(self.invocation.out_dir)

        # cpp_generator = CppProjGenerator(self.target_manager, self.analysis_manager)
        # cpp_generator.generate(self.package_group)
        # self.target_manager.output_to(self.invocation.out_dir)

        kn_bridge_generator = KNBridgeGenerator(
            self.target_manager, self.analysis_manager
        )
        kn_bridge_generator.generate(self.package_group)
        self.target_manager.output_to(self.invocation.out_dir)

    def run(self):
        self.scan()
        self.parse()
        self.validate()
        self.show()
        self.generate()
