import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import time
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from taihe.driver.backend import BackendRegistry
from taihe.driver.contexts import CompilerInstance, CompilerInvocation
from taihe.utils.logging import setup_logger
from taihe.utils.outputs import CMakeOutputConfig, OutputConfig
from taihe.utils.resources import (
    PandaVm,
    ResourceContext,
    RuntimeHeader,
    RuntimeSource,
    StandardLibrary,
    fetch_url,
)

# A lower value means more verbosity
TRACE_CONCISE = logging.DEBUG - 1
TRACE_VERBOSE = TRACE_CONCISE - 1


class BuildUtils:
    """Utility class for common operations."""

    def __init__(self):
        self.logger = logging.getLogger("build_system")

    def run_command(
        self,
        command: Sequence[Path | str],
        capture_output: bool = False,
        env: Mapping[str, Path | str] | None = None,
    ) -> float:
        """Run a command with environment variables."""
        command_str = " ".join(map(str, command))

        env_str = ""
        for key, val in (env or {}).items():
            env_str += f"{key}={val} "

        self.logger.debug("+ %s%s", env_str, command_str)

        try:
            start_time = time.time()
            subprocess.run(
                command,
                check=True,
                text=True,
                env=env,
                capture_output=capture_output,
            )
            end_time = time.time()
            elapsed_time = end_time - start_time
            return elapsed_time
        except subprocess.CalledProcessError as e:
            self.logger.error("Command failed with exit code %s", e.returncode)
            if e.stdout:
                self.logger.error("Standard output: %s", e.stdout)
            if e.stderr:
                self.logger.error("Standard error: %s", e.stderr)
            raise

    def create_directory(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        self.logger.debug("Created directory: %s", directory)

    def clean_directory(self, directory: Path) -> None:
        if not directory.exists():
            return
        shutil.rmtree(directory)
        self.logger.debug("Cleaned directory: %s", directory)

    def move_directory(self, src: Path, dst: Path) -> None:
        if not src.exists():
            raise FileNotFoundError(f"Source directory does not exist: {src}")
        shutil.move(src, dst)
        self.logger.debug("Moved directory from %s to %s", src, dst)

    def copy_directory(self, src: Path, dst: Path) -> None:
        if not src.exists():
            raise FileNotFoundError(f"Source directory does not exist: {src}")
        shutil.copytree(src, dst, dirs_exist_ok=True)
        self.logger.debug("Copied directory from %s to %s", src, dst)

    def extract_file(
        self,
        target_file: Path,
        extract_dir: Path,
    ) -> None:
        """Extract a tar.gz file."""
        if not target_file.exists():
            raise FileNotFoundError(f"File to extract does not exist: {target_file}")

        self.create_directory(extract_dir)

        with tarfile.open(target_file, "r:gz") as tar:
            # Check for any unsafe paths before extraction
            for member in tar.getmembers():
                member_path = Path(member.name)
                if member_path.is_absolute() or ".." in member_path.parts:
                    raise ValueError(f"Unsafe path in archive: {member.name}")
            # Extract safely
            tar.extractall(path=extract_dir)

        self.logger.info("Extracted %s to %s", target_file, extract_dir)

    def taihec(
        self,
        dst_dir: Path,
        src_files: list[Path],
        backend_names: list[str],
        buildsys_name: str | None = None,
        extra: dict[str, str | None] | None = None,
    ) -> None:
        registry = BackendRegistry()
        registry.register_all()
        backends = registry.collect_required_backends(backend_names)
        resolved_backends = [b() for b in backends]

        if buildsys_name == "cmake":
            output_config = CMakeOutputConfig(
                dst_dir=dst_dir,
                runtime_include_dir=RuntimeHeader.resolve_path(),
                runtime_src_dir=RuntimeSource.resolve_path(),
            )
        else:
            output_config = OutputConfig(
                dst_dir=dst_dir,
            )

        invocation = CompilerInvocation(
            src_files=src_files,
            output_config=output_config,
            backends=resolved_backends,
            extra=extra or {},
        )
        instance = CompilerInstance(invocation)
        if not instance.run():
            raise RuntimeError("Taihe compiler (taihec) failed to run")


class CppToolchain:
    """Utility class for C++ toolchain operations."""

    def __init__(self, util: BuildUtils):
        self.util = util
        self.logger = util.logger
        self.cxx = os.getenv("CXX", "clang++")
        self.cc = os.getenv("CC", "clang")

    def compile(
        self,
        output_dir: Path,
        input_files: Iterable[Path],
        include_dirs: Sequence[Path] = (),
        compile_flags: Sequence[str] = (),
    ) -> list[Path]:
        """Compile source files."""
        output_files: list[Path] = []

        for input_file in input_files:
            name = input_file.name
            output_file = output_dir / f"{name}.o"

            if name.endswith(".c"):
                compiler = self.cc
                std = "gnu11"
            else:
                compiler = self.cxx
                std = "gnu++17"

            command = [
                compiler,
                "-c",
                "-fvisibility=hidden",
                "-fPIC",
                # "-Wall",
                # "-Wextra",
                f"-std={std}",
                "-o",
                output_file,
                input_file,
                *compile_flags,
            ]

            for include_dir in include_dirs:
                if include_dir.exists():  # Only include directories that exist
                    command.append(f"-I{include_dir}")

            self.util.run_command(command)

            output_files.append(output_file)

        return output_files

    def link(
        self,
        output_file: Path,
        input_files: Sequence[Path],
        shared: bool = False,
        link_options: Sequence[str] = (),
    ) -> None:
        """Link object files."""
        if len(input_files) == 0:
            self.logger.warning("No input files to link")
            return

        command = [
            self.cxx,
            "-fPIC",
            "-o",
            output_file,
            *input_files,
            *link_options,
        ]

        if shared:
            command.append("-shared")

        self.util.run_command(command)

    def run(
        self,
        target: Path,
        ld_lib_path: Path,
        args: Sequence[str] = (),
    ) -> float:
        """Run the compiled target."""
        command = [
            target,
            *args,
        ]

        return self.util.run_command(
            command,
            env={"LD_LIBRARY_PATH": ld_lib_path},
        )


class ArkToolchain:
    """Utility class for ABC toolchain operations."""

    def __init__(self, util: BuildUtils):
        self.util = util
        self.logger = util.logger
        self.vm = PandaVm.resolve()

    def create_arktsconfig(
        self,
        arktsconfig_file: Path,
        app_paths: dict[str, Path] | None = None,
    ) -> None:
        """Create ArkTS configuration file."""
        vm = PandaVm.resolve()
        paths = vm.stdlib_sources | vm.sdk_sources | (app_paths or {})

        config_content = {
            "compilerOptions": {
                "baseUrl": str(vm.host_tools_dir),
                "paths": {key: [str(value)] for key, value in paths.items()},
            }
        }

        with open(arktsconfig_file, "w") as json_file:
            json.dump(config_content, json_file, indent=2)

        self.logger.debug("Created configuration file at: %s", arktsconfig_file)

    def compile(
        self,
        output_dir: Path,
        input_files: Iterable[Path],
        arktsconfig_file: Path,
    ) -> list[Path]:
        """Compile ETS files to ABC format."""
        output_files: list[Path] = []

        for input_file in input_files:
            name = input_file.name
            output_file = output_dir / f"{name}.abc"
            output_dump = output_dir / f"{name}.abc.dump"

            gen_abc_command = [
                self.vm.tool("es2panda"),
                input_file,
                "--output",
                output_file,
                "--extension",
                "ets",
                "--arktsconfig",
                arktsconfig_file,
            ]

            self.util.run_command(gen_abc_command)

            output_files.append(output_file)

            ark_disasm_path = self.vm.tool("ark_disasm")
            if not ark_disasm_path.exists():
                self.logger.warning(
                    "ark_disasm not found at %s, skipping disassembly", ark_disasm_path
                )
                continue

            gen_abc_dump_command = [
                ark_disasm_path,
                output_file,
                output_dump,
            ]

            self.util.run_command(gen_abc_dump_command)

        return output_files

    def link(
        self,
        target: Path,
        input_files: Sequence[Path],
    ) -> None:
        """Link ABC files."""
        if len(input_files) == 0:
            self.logger.warning("No input files to link")
            return

        command = [
            self.vm.tool("ark_link"),
            "--output",
            target,
            "--",
            *input_files,
        ]

        self.util.run_command(command)

    def run(
        self,
        abc_target: Path,
        ld_lib_path: Path,
        entry: str,
    ) -> float:
        """Run the compiled ABC file with the Ark runtime."""
        ark_path = self.vm.tool("ark")

        command = [
            ark_path,
            f"--boot-panda-files={self.vm.sdk_lib}",
            f"--boot-panda-files={self.vm.stdlib_lib}",
            f"--load-runtimes=ets",
            abc_target,
            entry,
        ]

        return self.util.run_command(
            command,
            env={"LD_LIBRARY_PATH": ld_lib_path},
        )


class BuildSystem(ABC):
    """Main build system class."""

    lib_files: list[Path]

    runtime_includes: list[Path]
    generated_includes: list[Path]
    author_includes: list[Path]

    runtime_sources: list[Path]

    author_backend_names: list[str]
    user_backend_names: list[str]

    def __init__(
        self,
        target_dir: str,
        verbosity: int = logging.INFO,
    ):
        self.util = BuildUtils()
        self.logger = self.util.logger

        self.should_run_pretty_print = verbosity <= logging.DEBUG

        self.cpp_toolchain = CppToolchain(self.util)

        # Build paths
        self.target_path = Path(target_dir).resolve()

        self.idl_dir = self.target_path / "idl"
        self.build_dir = self.target_path / "build"

        self.generated_dir = self.target_path / "generated"
        self.generated_include_dir = self.generated_dir / "include"
        self.generated_src_dir = self.generated_dir / "src"

        self.author_dir = self.target_path / "author"
        self.author_include_dir = self.author_dir / "include"
        self.author_src_dir = self.author_dir / "src"

        self.build_runtime_src_dir = self.build_dir / "runtime" / "src"
        self.build_generated_src_dir = self.build_dir / "generated" / "src"
        self.build_author_src_dir = self.build_dir / "author" / "src"

        self.lib_name = self.target_path.absolute().name
        self.so_target = self.build_dir / f"lib{self.lib_name}.so"

        self.author_backend_names = ["cpp-author"]

    def create(self) -> None:
        """Create a simple example project."""
        self._create_idl_files()
        self._create_author_files()
        self._create_user_files()

    def generate(self, buildsys_name: str | None, extra: dict[str, str | None]) -> None:
        """Generate code from IDL files."""
        if not self.idl_dir.is_dir():
            raise FileNotFoundError(f"IDL directory not found: '{self.idl_dir}'")

        self.util.clean_directory(self.generated_dir)

        self.logger.info("Generating author and ani codes...")

        # Generate taihe stdlib codes
        self.util.taihec(
            dst_dir=self.generated_dir,
            src_files=self.lib_files,
            backend_names=["abi-source", "cpp-common"],
        )
        # Generate author codes
        backend_names: list[str] = []
        backend_names.extend(self.author_backend_names)
        backend_names.extend(self.user_backend_names)
        if self.should_run_pretty_print:
            backend_names.append("pretty-print")
        self.util.taihec(
            dst_dir=self.generated_dir,
            src_files=list(self.idl_dir.glob("*.taihe")),
            backend_names=backend_names,
            buildsys_name=buildsys_name,
            extra=extra,
        )

    def build(self, opt_level: str) -> None:
        """Run the complete build process."""
        self.logger.info("Starting ANI compilation...")

        # Clean and prepare the build directory
        self.util.clean_directory(self.build_dir)
        self.util.create_directory(self.build_dir)

        # Compile the shared library
        self._compile_shared_library(opt_level=opt_level)
        self._compile_user_executable(opt_level=opt_level)
        self._run_user_executable()

        self.logger.info("Build and execution completed successfully")

    def _create_idl_files(self) -> None:
        """Create a simple example IDL file."""
        self.util.create_directory(self.idl_dir)
        with open(self.idl_dir / "hello.taihe", "w") as f:
            f.write(f"function sayHello(): void;\n")

    def _create_author_files(self) -> None:
        """Create a simple example author source file."""
        self.util.create_directory(self.author_src_dir)
        with open(self.author_dir / "compile_flags.txt", "w") as f:
            for author_include_dir in self.author_includes:
                f.write(f"-I{author_include_dir}\n")
        with open(self.author_src_dir / "hello.impl.cpp", "w") as f:
            f.write(
                f'#include "hello.proj.hpp"\n'
                f'#include "hello.impl.hpp"\n'
                f"\n"
                f"#include <iostream>\n"
                f"\n"
                f"void sayHello() {{\n"
                f'    std::cout << "Hello, World!" << std::endl;\n'
                f"    return;\n"
                f"}}\n"
                f"\n"
                f"TH_EXPORT_CPP_API_sayHello(sayHello);\n"
            )

    @abstractmethod
    def _create_user_files(self) -> None:
        """Create user files based on the user type."""
        pass

    def _compile_shared_library(self, opt_level: str):
        """Compile the shared library."""
        self.logger.info("Compiling shared library...")

        self.util.create_directory(self.build_runtime_src_dir)
        runtime_objects = self.cpp_toolchain.compile(
            self.build_runtime_src_dir,
            self.runtime_sources,
            self.runtime_includes,
            compile_flags=[f"-O{opt_level}"],
        )

        self.util.create_directory(self.build_generated_src_dir)
        generated_objects = self.cpp_toolchain.compile(
            self.build_generated_src_dir,
            self.generated_src_dir.glob("*.[cC]*"),
            self.generated_includes,
            compile_flags=[f"-O{opt_level}"],
        )

        self.util.create_directory(self.build_author_src_dir)
        author_objects = self.cpp_toolchain.compile(
            self.build_author_src_dir,
            self.author_src_dir.glob("*.[cC]*"),
            self.author_includes,
            compile_flags=[f"-O{opt_level}"],
        )

        # Link all objects
        if all_objects := runtime_objects + generated_objects + author_objects:
            self.cpp_toolchain.link(
                self.so_target,
                all_objects,
                shared=True,
                link_options=["-Wl,--no-undefined"],
            )
            self.logger.info("Shared library compiled: %s", self.so_target)
        else:
            self.logger.warning(
                "No object files to link, skipping shared library compilation"
            )

    @abstractmethod
    def _compile_user_executable(self, opt_level: str) -> None:
        """Compile and link the user executable."""
        pass

    @abstractmethod
    def _run_user_executable(self) -> None:
        """Run the user executable."""
        pass


class CppBuildSystem(BuildSystem):
    """Main build system class."""

    def __init__(
        self,
        target_dir: str,
        verbosity: int = logging.INFO,
    ):
        super().__init__(target_dir, verbosity)

        self.user_dir = self.target_path / "user"
        self.user_include_dir = self.user_dir / "include"
        self.user_src_dir = self.user_dir / "src"

        self.build_user_src_dir = self.build_dir / "user" / "src"

        self.runtime_includes = [RuntimeHeader.resolve_path()]
        self.generated_includes = [*self.runtime_includes, self.generated_include_dir]
        self.author_includes = [*self.generated_includes, self.author_include_dir]
        self.user_includes = [*self.generated_includes, self.user_include_dir]

        runtime_src_dir = RuntimeSource.resolve_path()
        self.runtime_sources = [
            runtime_src_dir / "string.cpp",
            runtime_src_dir / "object.cpp",
        ]

        self.exe_target = self.build_dir / "main"

        self.lib_files = []

        self.user_backend_names = ["cpp-user"]

    def _create_user_files(self) -> None:
        """Create a simple example user source file."""
        self.util.create_directory(self.user_src_dir)
        with open(self.user_dir / "compile_flags.txt", "w") as f:
            for user_include_dir in self.user_includes:
                f.write(f"-I{user_include_dir}\n")
        with open(self.user_src_dir / "main.cpp", "w") as f:
            f.write(
                f'#include "hello.user.hpp"\n'
                f"\n"
                f"int main() {{\n"
                f"    hello::sayHello();\n"
                f"    return 0;\n"
                f"}}\n"
            )

    def _compile_user_executable(self, opt_level: str) -> None:
        """Compile and link the executable."""
        self.logger.info("Compiling and linking executable...")

        self.util.create_directory(self.build_user_src_dir)
        user_objects = self.cpp_toolchain.compile(
            self.build_user_src_dir,
            self.user_src_dir.glob("*.[cC]*"),
            self.user_includes,
            compile_flags=[f"-O{opt_level}"],
        )

        # Link the executable
        if user_objects:
            self.cpp_toolchain.link(
                self.exe_target,
                [self.so_target, *user_objects],
            )
            self.logger.info("Executable compiled: %s", self.exe_target)
        else:
            self.logger.warning(
                "No object files to link, skipping executable compilation"
            )

    def _run_user_executable(self) -> None:
        """Run the compiled executable."""
        self.logger.info("Running executable...")

        elapsed_time = self.cpp_toolchain.run(
            self.exe_target,
            self.so_target.parent,
        )

        self.logger.info("Done, time = %f s", elapsed_time)


class StsBuildSystem(BuildSystem):
    """Main build system class."""

    def __init__(
        self,
        target_dir: str,
        verbosity: int = logging.INFO,
    ):
        super().__init__(target_dir, verbosity)

        self.ark_toolchain = ArkToolchain(self.util)

        self.user_dir = self.target_path / "user"

        self.build_generated_dir = self.build_dir / "generated"
        self.build_user_dir = self.build_dir / "user"

        self.runtime_includes = [
            RuntimeHeader.resolve_path(),
            self.ark_toolchain.vm.ani_header_dir,
        ]
        self.generated_includes = [*self.runtime_includes, self.generated_include_dir]
        self.author_includes = [*self.generated_includes, self.author_include_dir]

        runtime_src_dir = RuntimeSource.resolve_path()
        self.runtime_sources = [
            runtime_src_dir / "string.cpp",
            runtime_src_dir / "object.cpp",
            runtime_src_dir / "runtime.cpp",
        ]

        self.abc_target = self.build_dir / "main.abc"
        self.arktsconfig_file = self.build_dir / "arktsconfig.json"

        self.lib_files = [StandardLibrary.resolve_path() / "taihe.platform.ani.taihe"]

        self.user_backend_names = ["ani-bridge"]

    def _create_user_files(self) -> None:
        """Create a simple example user ETS file."""
        self.util.create_directory(self.user_dir)
        with open(self.user_dir / "main.ets", "w") as f:
            f.write(
                f'import * as hello from "hello";\n'
                f"\n"
                f'loadLibrary("{self.lib_name}");\n'
                f"\n"
                f"function main() {{\n"
                f"    hello.sayHello();\n"
                f"}}\n"
            )

    def _compile_user_executable(self, opt_level: str) -> None:
        """Compile and link ABC files."""
        self.logger.info("Compiling and linking ABC files...")

        paths: dict[str, Path] = {}
        for path in self.generated_dir.glob("*.ets"):
            paths[path.stem] = path
        for path in self.user_dir.glob("*.ets"):
            paths[path.stem] = path

        self.ark_toolchain.create_arktsconfig(self.arktsconfig_file, paths)

        self.util.create_directory(self.build_generated_dir)
        generated_abc = self.ark_toolchain.compile(
            self.build_generated_dir,
            self.generated_dir.glob("*.ets"),
            self.arktsconfig_file,
        )

        self.util.create_directory(self.build_user_dir)
        user_abc = self.ark_toolchain.compile(
            self.build_user_dir,
            self.user_dir.glob("*.ets"),
            self.arktsconfig_file,
        )

        # Link all ABC files
        if all_abc_files := generated_abc + user_abc:
            self.ark_toolchain.link(
                self.abc_target,
                all_abc_files,
            )
            self.logger.info("ABC files linked: %s", self.abc_target)
        else:
            self.logger.warning("No ABC files to link, skipping ABC compilation")

    def _run_user_executable(self) -> None:
        """Run the compiled ABC file with the Ark runtime."""
        self.logger.info("Running ABC file with Ark runtime...")

        elapsed_time = self.ark_toolchain.run(
            self.abc_target,
            self.so_target.parent,
            entry="main.ETSGLOBAL::main",
        )

        self.logger.info("Done, time = %f s", elapsed_time)


BUILD_MODES = {
    "cpp": CppBuildSystem,
    "sts": StsBuildSystem,
}


class RepositoryUpgrader:
    """Upgrade the code from a specified URL."""

    def __init__(self, repo_url: str):
        self.util = BuildUtils()
        self.logger = self.util.logger

        self.repo_url = repo_url

    def fetch_and_upgrade(self):
        filename = self.repo_url.split("/")[-1]
        version = self.repo_url.split("/")[-2]

        base_dir = ResourceContext.instance().base_dir
        extract_dir = base_dir / "../tmp"
        target_file = extract_dir / filename
        self.util.create_directory(extract_dir)
        fetch_url(self.repo_url, target_file)
        self.util.extract_file(target_file, extract_dir)

        temp_base_dir = extract_dir / "taihe"
        self.util.clean_directory(base_dir)
        self.util.move_directory(temp_base_dir, base_dir)
        self.util.clean_directory(extract_dir)

        self.logger.info("Successfully upgraded code to version %s", version)


class TaiheTryitParser(argparse.ArgumentParser):
    """Parser for the Taihe Tryit CLI."""

    def register_common_configs(self) -> None:
        self.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="Increase verbosity (can be used multiple times)",
        )

    def register_project_configs(self) -> None:
        self.add_argument(
            "target_directory",
            type=str,
            nargs="?",
            default=".",
            help="The target directory containing source files for the project",
        )
        self.add_argument(
            "-u",
            "--user",
            choices=BUILD_MODES.keys(),
            required=True,
            help="User type for the build system (ani/cpp)",
        )

    def register_build_configs(self) -> None:
        self.add_argument(
            "-O",
            "--optimization",
            type=str,
            nargs="?",
            default="0",
            const="0",
            help="Optimization level for compilation (0-3)",
        )

    def register_generate_configs(self) -> None:
        self.add_argument(
            "--build",
            "-B",
            dest="buildsys",
            choices=["cmake"],
            help="build system to use for generated sources",
        )
        self.add_argument(
            "--codegen",
            "-C",
            dest="config",
            nargs="*",
            action="extend",
            default=[],
            help="additional code generation configuration",
        )

    def register_update_configs(self) -> None:
        self.add_argument(
            "URL",
            type=str,
            help="The URL to fetch the code from",
        )


def main():
    parser = TaiheTryitParser(
        prog="taihe-tryit",
        description="Build and run project from a target directory",
    )
    parser.register_common_configs()

    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_create = subparsers.add_parser(
        "create",
        help="Create a simple example",
    )
    parser_create.register_common_configs()
    parser_create.register_project_configs()

    parser_generate = subparsers.add_parser(
        "generate",
        help="Generate code from the target directory",
    )
    parser_generate.register_common_configs()
    parser_generate.register_project_configs()
    parser_generate.register_generate_configs()

    parser_build = subparsers.add_parser(
        "build",
        help="Build the project from the target directory",
    )
    parser_build.register_common_configs()
    parser_build.register_project_configs()
    parser_build.register_build_configs()

    parser_test = subparsers.add_parser(
        "test",
        help="Generate and build the project from the target directory",
    )
    parser_test.register_common_configs()
    parser_test.register_project_configs()
    parser_test.register_build_configs()
    parser_test.register_generate_configs()

    parser_upgrade = subparsers.add_parser(
        "upgrade",
        help="Upgrade using the specified URL",
    )
    parser_upgrade.register_common_configs()
    parser_upgrade.register_update_configs()

    ResourceContext.register_cli_options(parser)
    args = parser.parse_args()
    ResourceContext.initialize(args)

    match args.verbose:
        case 0:
            verbosity = logging.INFO
        case 1:
            verbosity = logging.DEBUG
        case 2:
            verbosity = TRACE_CONCISE
        case _:
            verbosity = TRACE_VERBOSE
    setup_logger(verbosity)

    user = BUILD_MODES[args.user]

    try:
        if args.command == "upgrade":
            upgrader = RepositoryUpgrader(args.URL)
            upgrader.fetch_and_upgrade()
        else:
            build_system = user(args.target_directory, verbosity)
            if args.command == "create":
                build_system.create()
            if args.command in ("generate", "test"):
                extra: dict[str, str | None] = {}
                for config in args.config:
                    k, *v = config.split("=", 1)
                    if v:
                        extra[k] = v[0]
                    else:
                        extra[k] = None
                build_system.generate(
                    buildsys_name=args.buildsys,
                    extra=extra,
                )
            if args.command in ("build", "test"):
                build_system.build(
                    opt_level=args.optimization,
                )
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting build process.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
