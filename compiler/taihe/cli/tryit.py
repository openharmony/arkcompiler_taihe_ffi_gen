import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tarfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from taihe.utils.outputs import DebugLevel

if TYPE_CHECKING:
    from taihe.driver.backend import BackendConfig


# A lower value means more verbosity
TRACE_CONCISE = logging.DEBUG - 1
TRACE_VERBOSE = TRACE_CONCISE - 1


@dataclass
class UserInfo:
    """User information for authentication."""

    username: str
    password: str


class BuildUtils:
    """Utility class for common operations."""

    def __init__(self, verbosity: int):
        self.logger = self._setup_logger(verbosity)

    def _setup_logger(self, verbosity: int) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger("build_system")
        logger.setLevel(verbosity)

        # Clear any existing handlers to avoid duplicate logging
        if logger.handlers:
            logger.handlers.clear()

        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def run_command(
        self,
        command: Sequence[Union[Path, str]],
        capture_output: bool = True,
        env: Optional[dict[str, str]] = None,
    ) -> None:
        """Run a command with environment variables."""
        # Convert all command elements to strings
        command_str = [str(c) for c in command]

        # Format command for logging
        if env:
            env_str = " ".join(f"{key}={val}" for key, val in env.items()) + " "
        else:
            env_str = ""
        log_cmd = (
            f"+ {env_str}{' '.join(command_str)}"
            if env_str
            else f"+ {' '.join(command_str)}"
        )
        self.logger.debug(log_cmd)

        try:
            subprocess.run(
                command_str,
                check=True,
                text=True,
                env=env,
                capture_output=capture_output,
            )
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
        shutil.move(str(src), str(dst))
        self.logger.debug("Moved directory from %s to %s", src, dst)

    def copy_directory(self, src: Path, dst: Path) -> None:
        if not src.exists():
            raise FileNotFoundError(f"Source directory does not exist: {src}")
        shutil.copytree(src, dst, dirs_exist_ok=True)
        self.logger.debug("Copied directory from %s to %s", src, dst)

    def download_file(
        self,
        target_file: Path,
        url: str,
        user_info: Optional[UserInfo] = None,
    ) -> None:
        """Download a file from a URL."""
        if target_file.exists():
            self.logger.info("Already found %s, skipping download", target_file)
            return

        temp_file = target_file.with_suffix(".tmp")

        command = ["curl", "-L", "--progress-bar", url, "-o", str(temp_file)]

        if user_info:
            command.extend(["-u", f"{user_info.username}:{user_info.password}"])

        self.run_command(command, capture_output=False)

        if temp_file.exists():
            temp_file.rename(target_file)
            self.logger.info("Downloaded %s to %s", url, target_file)
        else:
            self.logger.error("Failed to download %s", url)
            raise FileNotFoundError(f"Failed to download {url}")

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


class BuildConfig:
    """Configuration for the build process."""

    def __init__(self, for_distribution: bool = False):
        self.cxx = os.getenv("CXX", "clang++")
        self.cc = os.getenv("CC", "clang")
        self.panda_userinfo = UserInfo(
            username=os.getenv("PANDA_USERNAME", "koala-pub"),
            password=os.getenv("PANDA_PASSWORD", "y3t!n0therP"),
        )
        self.panda_url = "https://nexus.bz-openlab.ru:10443/repository/koala-npm/%40panda/sdk/-/sdk-1.5.0.tgz"

        current_file = Path(__file__).resolve()
        if for_distribution:
            # Inside the distributed repository: dist/lib/taihe/compiler/taihe/cli/compiler.py
            self.taihe_base_dir = current_file.parents[5]
            self.runtime_include_dir = self.taihe_base_dir / "include"
            self.runtime_src_dir = self.taihe_base_dir / "src" / "taihe" / "runtime"
            self.panda_extract_dir = self.taihe_base_dir / "var" / "taihe" / "panda_vm"
        else:
            # Inside the git repository: repo/compiler/taihe/cli/run_test.py
            self.taihe_base_dir = current_file.parents[3]
            self.runtime_include_dir = self.taihe_base_dir / "runtime" / "include"
            self.runtime_src_dir = self.taihe_base_dir / "runtime" / "src"
            self.panda_extract_dir = self.taihe_base_dir / ".panda_vm"
        self.taihe_version_file = self.taihe_base_dir / "version.txt"
        self.panda_version_file = self.panda_extract_dir / "version.txt"
        self.panda_base_dir = self.panda_extract_dir / "package"
        self.panda_home_dir = self.panda_base_dir / "linux_host_tools"
        self.panda_include_dir = (
            self.panda_base_dir / "ohos_arm64/include/plugins/ets/runtime/ani"
        )


def _map_output_debug_level(verbosity: int) -> DebugLevel:
    if verbosity <= TRACE_VERBOSE:
        return DebugLevel.VERBOSE
    if verbosity <= TRACE_CONCISE:
        return DebugLevel.CONCISE
    return DebugLevel.NONE


class BuildSystem(BuildUtils):
    """Main build system class."""

    def __init__(
        self,
        target_dir: str,
        config: BuildConfig,
        verbosity: int,
        sts_keep_name: bool = False,
        opt_level: str = "0",
    ):
        super().__init__(verbosity)
        self.config = config
        self.sts_keep_name = sts_keep_name
        self.should_run_pretty_print = verbosity <= logging.DEBUG
        self.codegen_debug_level = _map_output_debug_level(verbosity)

        # Build paths
        self.target_path = Path(target_dir).resolve()
        self.idl_dir = self.target_path / "idl"
        self.system_dir = self.target_path / "system"
        self.user_dir = self.target_path / "user"
        self.build_dir = self.target_path / "build"

        self.author_dir = self.target_path / "author"
        self.author_include_dir = self.author_dir / "include"
        self.author_src_dir = self.author_dir / "src"

        self.generated_dir = self.target_path / "author_generated"
        self.generated_include_dir = self.generated_dir / "include"
        self.generated_src_dir = self.generated_dir / "src"

        # Build sub-directories
        self.build_generated_src_dir = self.build_dir / "author_generated" / "src"
        self.build_author_src_dir = self.build_dir / "author" / "src"
        self.build_runtime_src_dir = self.build_dir / "runtime" / "src"
        self.build_generated_dir = self.build_dir / "author_generated"
        self.build_system_dir = self.build_dir / "system"
        self.build_user_dir = self.build_dir / "user"

        # Output files
        self.so_target = self.build_dir / f"lib{self.target_path.name}.so"
        self.abc_target = self.build_dir / "main.abc"
        self.arktsconfig_target = self.build_dir / "arktsconfig.json"

        # Build options
        self.opt_level = opt_level.strip()  # Ensure no whitespace
        self.lib_name = self.target_path.absolute().name

    def create(self) -> None:
        self.create_directory(self.idl_dir)
        self.create_directory(self.author_dir)
        self.create_directory(self.author_src_dir)
        self.create_directory(self.user_dir)

        include_dirs: list[Path] = []
        include_dirs.append(self.config.panda_include_dir)
        include_dirs.append(self.config.runtime_include_dir)
        include_dirs.append(self.generated_include_dir)
        include_dirs.append(self.author_include_dir)

        with open(self.idl_dir / "hello.taihe", "w") as f:
            f.write("function sayHello(): void;\n")

        with open(self.author_src_dir / "hello.impl.cpp", "w") as f:
            f.write(
                '#include "hello.proj.hpp"\n'
                '#include "hello.impl.hpp"\n'
                "\n"
                "#include <iostream>\n"
                "\n"
                "void sayHello() {\n"
                '    std::cout << "Hello, World!" << std::endl;\n'
                "    return;\n"
                "}\n"
                "\n"
                "TH_EXPORT_CPP_API_sayHello(sayHello);\n"
            )

        with open(self.user_dir / "main.ets", "w") as f:
            f.write(
                'import * as hello from "@generated/hello";\n'
                f'loadLibrary("{self.lib_name}");\n'
                "\n"
                "function main() {\n"
                "    hello.sayHello();\n"
                "}\n"
            )

        with open(self.target_path / "compile_flags.txt", "w") as f:
            for include_dir in include_dirs:
                f.write(f"-I{include_dir}\n")

    def generate_and_build(self) -> None:
        self.generate()
        self.build()

    def generate(self) -> None:
        """Generate code from IDL files."""
        if not self.idl_dir.is_dir():
            raise FileNotFoundError(f"IDL directory not found: '{self.idl_dir}'")

        self.clean_directory(self.generated_dir)

        # Import here to avoid module dependency issues
        from taihe.driver.backend import BackendRegistry
        from taihe.driver.contexts import CompilerInstance, CompilerInvocation

        self.logger.info("Generating author and ani codes...")

        registry = BackendRegistry()
        registry.register_all()
        backend_names = ["ani-bridge", "cpp-author"]
        if self.should_run_pretty_print:
            backend_names.append("pretty-print")
        backends = registry.collect_required_backends(backend_names)

        resolved_backends: list[BackendConfig] = []
        for b in backends:
            if b.NAME == "ani-bridge":
                resolved_backends.append(b(keep_name=self.sts_keep_name))  # type: ignore
            else:
                resolved_backends.append(b())

        instance = CompilerInstance(
            CompilerInvocation(
                src_dirs=[self.idl_dir],
                out_dir=self.generated_dir,
                out_debug_level=self.codegen_debug_level,
                backends=resolved_backends,
            )
        )

        if not instance.run():
            raise RuntimeError(f"Code generation failed")

    def build(self) -> None:
        """Run the complete build process."""
        self.logger.info("Starting ANI compilation...")

        self.setup_build_directories()

        # Set up paths for Panda VM
        self.download_panda_vm()

        if not self.config.panda_home_dir.exists():
            raise FileNotFoundError(
                f"Panda home directory not found: {self.config.panda_home_dir}"
            )

        # Path to include directory for ANI
        panda_include_dir = self.config.panda_include_dir

        if not panda_include_dir.exists():
            self.logger.warning(
                "ANI include directory not found: %s", panda_include_dir
            )
            # Create a fallback include directory
            self.create_directory(panda_include_dir)

        # Compile the shared library
        self.compile_shared_library()

        # Compile and link ABC files
        self.compile_and_link_abc()

        # Run with Ark runtime
        self.run_ark()

        self.logger.info("Build and execution completed successfully")

    def compile_shared_library(self):
        """Compile the shared library."""
        self.logger.info("Compiling shared library...")

        # Compile each component
        runtime_objects = self.compile(
            self.build_runtime_src_dir,
            self.config.runtime_src_dir,
            self.config.panda_include_dir,
            self.config.runtime_include_dir,
        )
        generated_objects = self.compile(
            self.build_generated_src_dir,
            self.generated_src_dir,
            self.config.panda_include_dir,
            self.config.runtime_include_dir,
            self.generated_include_dir,
        )
        author_objects = self.compile(
            self.build_author_src_dir,
            self.author_src_dir,
            self.config.panda_include_dir,
            self.config.runtime_include_dir,
            self.generated_include_dir,
            self.author_include_dir,
        )

        # Link all objects
        if all_objects := runtime_objects + generated_objects + author_objects:
            self.link(
                self.so_target,
                *all_objects,
                shared=True,
                link_options=["-Wl,--no-undefined"],
            )
            self.logger.info("Shared library compiled: %s", self.so_target)
        else:
            self.logger.warning(
                "No object files to link, skipping shared library compilation"
            )

    def compile_and_link_abc(self):
        """Compile and link ABC files."""
        self.logger.info("Compiling and linking ABC files...")

        self.create_arktsconfig()

        # Compile ETS files in each directory
        generated_abc = self.compile_abc(
            self.build_generated_dir,
            self.generated_dir,
            self.arktsconfig_target,
            panda_home=self.config.panda_home_dir,
        )
        user_abc = self.compile_abc(
            self.build_user_dir,
            self.user_dir,
            self.arktsconfig_target,
            panda_home=self.config.panda_home_dir,
        )
        system_abc = self.compile_abc(
            self.build_system_dir,
            self.system_dir,
            self.arktsconfig_target,
            panda_home=self.config.panda_home_dir,
        )

        # Link all ABC files
        if all_abc_files := generated_abc + user_abc + system_abc:
            self.link_abc(
                self.abc_target,
                *all_abc_files,
                panda_home=self.config.panda_home_dir,
            )
            self.logger.info("ABC files linked: %s", self.abc_target)
        else:
            self.logger.warning("No ABC files to link, skipping ABC compilation")

    def run_ark(self) -> None:
        self.run_abc(
            self.abc_target,
            self.so_target.parent,
            entry="main.ETSGLOBAL::main",
            panda_home=self.config.panda_home_dir,
        )

    def setup_build_directories(self) -> None:
        """Set up necessary build directories."""
        # Clean and create directories
        self.clean_directory(self.build_dir)

        self.create_directory(self.build_dir)
        self.create_directory(self.build_runtime_src_dir)
        self.create_directory(self.build_generated_src_dir)
        self.create_directory(self.build_author_src_dir)
        self.create_directory(self.build_generated_dir)
        self.create_directory(self.build_system_dir)
        self.create_directory(self.build_user_dir)

    def download_panda_vm(self):
        """Download and extract Panda VM."""
        self.create_directory(self.config.panda_extract_dir)

        url = self.config.panda_url
        filename = url.split("/")[-1]
        target_file = self.config.panda_extract_dir / filename
        version = Path(filename).stem  # Use the filename without extension as version

        if not self.check_local_version(version):
            self.clean_directory(self.config.panda_base_dir)
            self.logger.info("Downloading panda VM version: %s", version)
            self.download_file(target_file, url, self.config.panda_userinfo)
            self.extract_file(target_file, self.config.panda_extract_dir)
            self.write_local_version(version)
            self.logger.info("Completed download and extraction.")

    def check_local_version(self, version: str) -> bool:
        """Check if the local version matches the desired version."""
        if not self.config.panda_version_file.exists():
            return False
        try:
            with open(self.config.panda_version_file) as vf:
                local_version = vf.read().strip()
                return local_version == version
        except OSError as e:
            self.logger.warning("Failed to read version file: %s", e)
            return False

    def write_local_version(self, version: str) -> None:
        """Write the local version to the version file."""
        try:
            with open(self.config.panda_version_file, "w") as vf:
                vf.write(version)
        except OSError as e:
            self.logger.warning("Failed to write version file: %s", e)

    def create_arktsconfig(self) -> None:
        """Create ArkTS configuration file."""
        config_content = {
            "compilerOptions": {
                "baseUrl": str(self.config.panda_home_dir),
                "paths": {
                    "std": [str(self.config.panda_home_dir / "../ets/stdlib/std")],
                    "escompat": [
                        str(self.config.panda_home_dir / "../ets/stdlib/escompat")
                    ],
                    "@ohos.base": [str(self.generated_dir / "@ohos.base.ets")],
                    "@generated": [str(self.generated_dir)],
                    "@system": [str(self.system_dir)],
                },
            }
        }

        with open(self.arktsconfig_target, "w") as json_file:
            json.dump(config_content, json_file, indent=2)

        self.logger.debug("Created configuration file at: %s", self.arktsconfig_target)

    def compile(
        self,
        output_dir: Path,
        input_dir: Path,
        *include_dirs: Path,
    ) -> list[Path]:
        """Compile source files."""
        output_files: list[Path] = []

        if not input_dir.exists():
            self.logger.warning("Input directory does not exist: %s", input_dir)
            return output_files

        for input_file in input_dir.glob("*.[cC]*"):  # Find .c, .cpp, .cc, .C files
            name = input_file.name
            output_file = output_dir / f"{name}.o"

            if name.endswith(".c"):
                compiler = self.config.cc
                std = "gnu11"
            else:
                compiler = self.config.cxx
                std = "gnu++17"

            command = [
                compiler,
                "-c",
                "-fvisibility=hidden",
                "-fPIC",
                f"-O{self.opt_level}",
                f"-std={std}",
                "-o",
                output_file,
                input_file,
            ]

            for include_dir in include_dirs:
                if include_dir.exists():  # Only include directories that exist
                    command.extend(["-I", include_dir])

            self.run_command(command)
            output_files.append(output_file)

        return output_files

    def link(
        self,
        output_file: Path,
        *input_files: Path,
        shared: bool = False,
        link_options: Optional[list[str]] = None,
    ) -> None:
        """Link object files."""
        if not input_files:
            self.logger.warning("No input files to link")
            return

        link_options = link_options or []

        command = [self.config.cxx, "-fPIC", "-o", output_file]
        command.extend(str(input_file) for input_file in input_files)
        command.extend(link_options)

        if shared:
            command.append("-shared")

        self.run_command(command)

    def compile_abc(
        self,
        output_dir: Path,
        input_dir: Path,
        config_file_path: Path,
        panda_home: Path,
    ) -> list[Path]:
        """Compile ETS files to ABC format."""
        output_files: list[Path] = []

        if not input_dir.exists() or not input_dir.is_dir():
            self.logger.warning(
                "Input directory does not exist or is not a directory: %s", input_dir
            )
            return output_files

        for input_file in input_dir.glob("*.ets"):
            name = input_file.name
            output_file = output_dir / f"{name}.abc"
            output_dump = output_dir / f"{name}.abc.dump"

            es2panda_path = panda_home / "bin/es2panda"
            if not es2panda_path.exists():
                raise FileNotFoundError(f"es2panda not found at {es2panda_path}")

            self.run_command(
                [
                    es2panda_path,
                    input_file,
                    "--output",
                    output_file,
                    "--extension",
                    "ets",
                    "--arktsconfig",
                    config_file_path,
                ]
            )

            ark_disasm_path = panda_home / "bin/ark_disasm"
            if not ark_disasm_path.exists():
                self.logger.warning(
                    "ark_disasm not found at %s, skipping disassembly", ark_disasm_path
                )
                continue

            self.run_command(
                [
                    ark_disasm_path,
                    output_file,
                    output_dump,
                ]
            )

            output_files.append(output_file)

        return output_files

    def link_abc(
        self,
        target: Path,
        *input_files: Path,
        panda_home: Path,
    ) -> None:
        """Link ABC files."""
        if not input_files:
            self.logger.warning("No input files to link")
            return

        ark_link_path = panda_home / "bin/ark_link"
        if not ark_link_path.exists():
            raise FileNotFoundError(f"ark_link not found at {ark_link_path}")

        command = [ark_link_path, "--output", target, "--"]
        command.extend(input_files)

        self.run_command(command)

    def run_abc(
        self,
        abc_target: Path,
        ld_lib_path: Path,
        entry: str,
        panda_home: Path,
    ):
        """Run the compiled ABC file with the Ark runtime."""
        if not abc_target.exists():
            self.logger.error("ABC file not found: %s", abc_target)
            raise FileNotFoundError(f"ABC file not found: {abc_target}")

        ark_path = panda_home / "bin/ark"
        if not ark_path.exists():
            raise FileNotFoundError(f"ark executable not found at {ark_path}")

        etsstdlib_path = panda_home / "../ets/etsstdlib.abc"
        if not etsstdlib_path.exists():
            self.logger.warning("etsstdlib.abc not found at %s", etsstdlib_path)

        self.logger.info("Running with Ark runtime: %s", abc_target)
        self.run_command(
            [
                ark_path,
                f"--boot-panda-files={etsstdlib_path}",
                f"--load-runtimes=ets",
                abc_target,
                entry,
            ],
            env={"LD_LIBRARY_PATH": str(ld_lib_path)},
            capture_output=False,
        )


class RepositoryUpgrader(BuildUtils):
    """Upgrade the code from a specified URL."""

    def __init__(
        self,
        repo_url: str,
        config: BuildConfig,
        verbosity: int = logging.INFO,
    ):
        super().__init__(verbosity)
        self.repo_url = repo_url
        self.config = config

    def fetch_and_upgrade(self):
        filename = self.repo_url.split("/")[-1]
        version = self.repo_url.split("/")[-2]
        with open(self.config.taihe_version_file) as vf:
            version_str = vf.read()
            local_version = version_str.splitlines()[0].split(":")[-1].strip()
        if local_version == version:
            self.logger.info("Already at version %s", version)
            return

        extract_dir = self.config.taihe_base_dir / "../tmp"
        target_file = extract_dir / filename
        self.create_directory(extract_dir)
        self.download_file(target_file, self.repo_url)
        self.extract_file(target_file, extract_dir)

        tmp_taihe_base_dir = extract_dir / "taihe"
        self.clean_directory(self.config.taihe_base_dir)
        self.move_directory(tmp_taihe_base_dir, self.config.taihe_base_dir)
        self.clean_directory(extract_dir)

        self.logger.info("Successfully upgraded code to version %s", version)


def main(config: Optional[BuildConfig] = None):
    """Main entry point for the script."""

    def add_argument_target_directory(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "target_directory",
            type=str,
            help="The target directory containing source files for the project",
        )

    def add_argument_optimization(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-O",
            "--optimization",
            type=str,
            nargs="?",
            default="0",
            const="0",
            help="Optimization level for compilation (0-3)",
        )

    def add_argument_sts_keep_name(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--sts-keep-name",
            action="store_true",
            help="Keep original function and interface method names",
        )

    def add_argument_verbosity(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="Increase verbosity (can be used multiple times)",
        )

    def add_argument_url(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "URL",
            type=str,
            help="The URL to fetch the code from",
        )

    parser = argparse.ArgumentParser(
        prog="taihe-tryit",
        description="Build and run project from a target directory",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_create = subparsers.add_parser(
        "create",
        help="Create a simple example",
    )
    add_argument_verbosity(parser_create)
    add_argument_target_directory(parser_create)

    parser_generate = subparsers.add_parser(
        "generate",
        help="Generate code from the target directory",
    )
    add_argument_verbosity(parser_generate)
    add_argument_target_directory(parser_generate)
    add_argument_sts_keep_name(parser_generate)

    parser_build = subparsers.add_parser(
        "build",
        help="Build the project from the target directory",
    )
    add_argument_verbosity(parser_build)
    add_argument_target_directory(parser_build)
    add_argument_optimization(parser_build)

    parser_test = subparsers.add_parser(
        "test",
        help="Generate and build the project from the target directory",
    )
    add_argument_verbosity(parser_test)
    add_argument_target_directory(parser_test)
    add_argument_optimization(parser_test)
    add_argument_sts_keep_name(parser_test)

    parser_upgrade = subparsers.add_parser(
        "upgrade",
        help="Upgrade using the specified URL",
    )
    add_argument_verbosity(parser_upgrade)
    add_argument_url(parser_upgrade)

    args = parser.parse_args()

    match args.verbose:
        case 0:
            verbosity = logging.INFO
        case 1:
            verbosity = logging.DEBUG
        case 2:
            verbosity = TRACE_CONCISE
        case _:
            verbosity = TRACE_VERBOSE

    if config is None:
        config = BuildConfig()

    try:
        match args.command:
            case "create":
                BuildSystem(
                    args.target_directory,
                    config=config,
                    verbosity=verbosity,
                ).create()
            case "generate":
                BuildSystem(
                    args.target_directory,
                    config=config,
                    verbosity=verbosity,
                    sts_keep_name=args.sts_keep_name,
                ).generate()
            case "build":
                BuildSystem(
                    args.target_directory,
                    config=config,
                    verbosity=verbosity,
                    opt_level=args.optimization,
                ).build()
            case "test":
                BuildSystem(
                    args.target_directory,
                    config=config,
                    verbosity=verbosity,
                    opt_level=args.optimization,
                    sts_keep_name=args.sts_keep_name,
                ).generate_and_build()
            case "upgrade":
                RepositoryUpgrader(
                    args.URL,
                    config=config,
                    verbosity=verbosity,
                ).fetch_and_upgrade()
            case _:
                parser.print_help()
                return
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting build process.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
