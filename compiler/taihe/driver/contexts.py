"""Orchestrates the compilation process.

- BackendRegistry: initializes all known backends
- CompilerInvocation: constructs the invocation from cmdline
    - Parses the general command line arguments
    - Enables user specified backends
    - Parses backend-specific arguments
    - Sets backend options
- CompilerInstance: runs the compilation
    - CompilerInstance: scans and parses sources files
    - Backends: post-process the IR
    - Backends: validate the IR
    - Backends: generate the output
"""

from dataclasses import dataclass, field
from pathlib import Path

from taihe.driver.backend import Backend, BackendConfig
from taihe.parse.convert import (
    AstConverter,
    IgnoredFileReason,
    IgnoredFileWarn,
    normalize_pkg_name,
)
from taihe.semantics.analysis import analyze_semantics
from taihe.semantics.declarations import PackageGroup
from taihe.utils.analyses import AnalysisManager
from taihe.utils.diagnostics import ConsoleDiagnosticsManager, DiagnosticsManager
from taihe.utils.exceptions import AdhocNote
from taihe.utils.outputs import OutputConfig
from taihe.utils.sources import SourceFile, SourceLocation, SourceManager


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

    src_files: list[Path] = field(default_factory=lambda: [])
    src_dirs: list[Path] = field(default_factory=lambda: [])
    output_config: OutputConfig = field(default_factory=OutputConfig)
    backends: list[BackendConfig] = field(default_factory=lambda: [])

    # TODO: refactor this to a more structured way
    sts_keep_name: bool = False
    arkts_module_prefix: str | None = None
    arkts_path_prefix: str | None = None


class CompilerInstance:
    """Helper class for storing key objects.

    CompilerInstance holds key intermediate objects across the compilation
    process, such as the source manager and the diagnostics manager.

    It also provides utility methods for driving the compilation process.
    """

    invocation: CompilerInvocation
    backends: list[Backend]

    diagnostics_manager: DiagnosticsManager

    source_manager: SourceManager
    package_group: PackageGroup

    analysis_manager: AnalysisManager

    def __init__(self, invocation: CompilerInvocation):
        self.invocation = invocation
        self.diagnostics_manager = ConsoleDiagnosticsManager()
        self.analysis_manager = AnalysisManager(invocation, self.diagnostics_manager)
        self.source_manager = SourceManager()
        self.package_group = PackageGroup()
        self.output_manager = invocation.output_config.construct(self)
        self.backends = [conf.construct(self) for conf in invocation.backends]

    ##########################
    # The compilation phases #
    ##########################

    def scan(self):
        """Adds all `.taihe` files inside a directory. Subdirectories are ignored."""
        files: list[Path] = []

        for src_dir in self.invocation.src_dirs:
            for src_file in src_dir.iterdir():
                files.append(src_file)

        for src_file in self.invocation.src_files:
            files.append(src_file)

        for file in files:
            loc = SourceLocation.with_path(file)
            # subdirectories are ignored
            if not file.is_file():
                w = IgnoredFileWarn(IgnoredFileReason.IS_DIRECTORY, loc=loc)
                self.diagnostics_manager.emit(w)

            # unexpected file extension
            elif file.suffix != ".taihe":
                target = file.with_suffix(".taihe").name
                w = IgnoredFileWarn(
                    IgnoredFileReason.EXTENSION_MISMATCH,
                    loc=loc,
                    note=AdhocNote(f"consider renaming to `{target}`", loc=loc),
                )
                self.diagnostics_manager.emit(w)

            else:
                source = SourceFile(file)
                orig_name = source.pkg_name
                norm_name = normalize_pkg_name(orig_name)

                # invalid package name
                if norm_name != orig_name:
                    loc = SourceLocation(source)
                    self.diagnostics_manager.emit(
                        IgnoredFileWarn(
                            IgnoredFileReason.INVALID_PKG_NAME,
                            note=AdhocNote(
                                f"consider using `{norm_name}` instead of `{orig_name}`",
                                loc=loc,
                            ),
                            loc=loc,
                        )
                    )

                # Okay...
                else:
                    self.source_manager.add_source(source)

    def parse(self):
        for src in self.source_manager.sources:
            conv = AstConverter(src, self.diagnostics_manager)
            pkg = conv.convert()
            with self.diagnostics_manager.capture_error():
                self.package_group.add(pkg)

        for b in self.backends:
            b.post_process()

    def validate(self):
        analyze_semantics(self.package_group, self.diagnostics_manager)

        for b in self.backends:
            b.validate()

    def generate(self):
        if self.diagnostics_manager.has_error:
            return

        for b in self.backends:
            b.generate()

        self.output_manager.post_generate()

    def run(self):
        self.scan()
        self.parse()
        self.validate()
        self.generate()
        return not self.diagnostics_manager.has_error
