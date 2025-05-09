import argparse
import json
import logging
import os
import shutil
import subprocess
import tarfile
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union


@dataclass
class UserInfo:
    """User information for authentication."""

    username: str
    password: str


class Utils:
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
        capture_output=True,
        env: Optional[dict[str, str]] = None,
    ) -> subprocess.CompletedProcess:
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
            return subprocess.run(
                command_str,
                check=True,
                text=True,
                env=env,
                capture_output=capture_output,
            )
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed with exit code {e.returncode}")
            if e.stdout:
                self.logger.error(f"Standard output: {e.stdout}")
            if e.stderr:
                self.logger.error(f"Standard error: {e.stderr}")
            raise

    def create_directory(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Created directory: {directory}")

    def clean_directory(self, directory: Path) -> None:
        if not directory.exists():
            return
        shutil.rmtree(directory)
        self.logger.debug(f"Cleaned directory: {directory}")

    def download_file(
        self, target_file: Path, url: str, user_info: Optional[UserInfo] = None
    ) -> None:
        """Download a file from a URL."""
        if target_file.exists():
            self.logger.info(f"Already found {target_file}, skipping download")
            return

        temp_file = target_file.with_suffix(".tmp")

        command = ["curl", "-L", "--progress-bar", url, "-o", str(temp_file)]

        if user_info:
            command.extend(["-u", f"{user_info.username}:{user_info.password}"])

        self.run_command(command, capture_output=False)

        if temp_file.exists():
            temp_file.rename(target_file)
            self.logger.info(f"Downloaded {url} to {target_file}")
        else:
            self.logger.error(f"Failed to download {url}")
            raise FileNotFoundError(f"Failed to download {url}")

    def extract_file(
        self,
        target_file: Path,
        extract_dir: Path,
        version_file: Optional[Path] = None,
        version: Optional[str] = None,
    ) -> None:
        """Extract a tar.gz file."""
        if not target_file.exists():
            raise FileNotFoundError(
                f"File to extract does not exist: {target_file}"
            )

        package_dir = extract_dir / "package"
        if package_dir.exists():
            shutil.rmtree(package_dir)

        os.makedirs(extract_dir, exist_ok=True)

        with tarfile.open(target_file, "r:gz") as tar:
            # Check for any unsafe paths before extraction
            for member in tar.getmembers():
                member_path = Path(member.name)
                if member_path.is_absolute() or ".." in member_path.parts:
                    raise ValueError(f"Unsafe path in archive: {member.name}")
            # Extract safely
            tar.extractall(path=extract_dir)

        if version_file and version:
            with open(version_file, "w") as vf:
                vf.write(version)

        self.logger.info(f"Extracted {target_file} to {extract_dir}")


class BuildConfig:
    """Configuration for the build process."""

    def __init__(self, for_distribution=False):
        self.cxx = os.getenv("CXX", "clang++")
        self.cc = os.getenv("CC", "clang")
        self.panda_userinfo = UserInfo(
            username=os.getenv("PANDA_USERNAME", "koala-pub"),
            password=os.getenv("PANDA_PASSWORD", "y3t!n0therP"),
        )
        self.panda_url = "https://nexus.bz-openlab.ru:10443/repository/koala-npm/%40panda/sdk/-/sdk-1.5.0-dev.31052.tgz"

        current_file = Path(__file__).resolve()
        if for_distribution:
            self.base_dir = current_file.parents[5]
            # Inside the distributed repository: dist/lib/taihe/ compiler/taihe/cli/compiler.py
            self.runtime_include_dir = self.base_dir / "include"
            self.runtime_src_dir = self.base_dir / "src" / "taihe" / "runtime"
            self.panda_home = self.base_dir / "var" / "taihe" / "panda_vm"
        else:
            # Inside the git repository: repo/ compiler/taihe/cli/run_test.py
            self.base_dir = current_file.parents[3]
            self.runtime_include_dir = self.base_dir / "runtime" / "include"
            self.runtime_src_dir = self.base_dir / "runtime" / "src"
            self.panda_home = self.base_dir / ".panda_vm"
        self.panda_include_home = (
            self.panda_home / "package/ohos_arm64/include/plugins/ets/runtime/ani"
        )


class BuildSystem(Utils):
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

        # Build options
        self.opt_level = opt_level.strip()  # Ensure no whitespace
        self.lib_name = self.target_path.absolute().name

    def create(self) -> None:
        self.create_directory(self.idl_dir)
        self.create_directory(self.author_dir)
        self.create_directory(self.author_src_dir)
        self.create_directory(self.user_dir)

        include_dirs = []
        include_dirs.append(self.config.panda_include_home)
        include_dirs.append(self.config.runtime_include_dir)
        include_dirs.append(self.generated_include_dir)
        include_dirs.append(self.author_include_dir)

        with open(os.path.join(self.idl_dir, "hello.taihe"), "w") as f:
            f.write("function sayHello(): void;\n")

        with open(os.path.join(self.author_src_dir, "hello.impl.cpp"), "w") as f:
            f.write(
                '#include "hello.proj.hpp"\n'
                '#include "hello.impl.hpp"\n'
                "#include <iostream>\n"
                "\n"
                "void sayHello() {\n"
                '    std::cout << "Hello, World!" << std::endl;\n'
                "    return;\n"
                "}\n"
                "\n"
                "TH_EXPORT_CPP_API_sayHello(sayHello);\n"
            )

        with open(os.path.join(self.user_dir, "main.ets"), "w") as f:
            f.write(
                'import * as hello from "@generated/hello";\n'
                f'loadLibrary("{self.lib_name}");\n'
                "\n"
                "function main() {\n"
                "    hello.sayHello();\n"
                "}\n"
            )

        with open(os.path.join(self.target_path, "compile_flags.txt"), "w") as f:
            for include_dir in include_dirs:
                f.write(f"-I{include_dir}\n")

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
        backends = registry.collect_required_backends(["ani-bridge", "cpp-author"])

        resolved_backends = []
        for b in backends:
            if b.NAME == "ani-bridge":
                resolved_backends.append(b(keep_name=self.sts_keep_name))  # type: ignore
            else:
                resolved_backends.append(b())  # pyre-ignore

        instance = CompilerInstance(
            CompilerInvocation(
                src_dirs=[self.idl_dir],
                out_dir=self.generated_dir,
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
        extract_dir = self.config.panda_home.resolve()
        self.create_directory(extract_dir)

        # Download and extract Panda VM
        package_dir = self.download_panda_vm(extract_dir)
        panda_home = package_dir / "linux_host_tools"

        if not panda_home.exists():
            raise FileNotFoundError(f"Panda home directory not found: {panda_home}")

        # Path to include directory for ANI
        panda_include_dir = self.config.panda_include_home

        if not panda_include_dir.exists():
            self.logger.warning(
                f"ANI include directory not found: {panda_include_dir}"
            )
            # Create a fallback include directory
            self.create_directory(panda_include_dir)

        # Compile the shared library
        self.compile_shared_library(panda_include_dir)

        # Create config file for ABC compilation
        config_file_path = self.build_dir / "arktsconfig.json"
        self.create_arktsconfig(panda_home, config_file_path)

        # Compile and link ABC files
        abc_target = self.compile_and_link_abc(panda_home, config_file_path)

        # Run with Ark runtime
        self.run_ark(panda_home, abc_target)

        self.logger.info("Build and execution completed successfully")

    def generate_and_build(self) -> None:
        self.generate()
        self.build()

    def compile(
        self, output_dir: Path, input_dir: Path, *include_dirs: Path
    ) -> list[Path]:
        """Compile source files."""
        output_files = []

        if not input_dir.exists():
            self.logger.warning(f"Input directory does not exist: {input_dir}")
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

    def check_local_version(self, version_file: Path, version: str) -> bool:
        """Check if the local version matches the desired version."""
        if version_file.exists():
            try:
                with open(version_file) as vf:
                    local_version = vf.read().strip()
                    return local_version == version
            except OSError as e:
                self.logger.warning(f"Failed to read version file: {e}")
        return False

    def download_panda_vm(self, extract_dir: Path) -> Path:
        """Download and extract Panda VM."""
        url = self.config.panda_url
        filename = url.split("/")[-1]
        target_file = extract_dir / filename
        version_file = extract_dir / "version.txt"
        version = Path(filename).stem  # Use the filename without extension as version

        if not self.check_local_version(version_file, version):
            self.logger.info(f"Downloading panda VM {version=}")
            self.download_file(target_file, url, self.config.panda_userinfo)
            self.extract_file(target_file, extract_dir, version_file, version)
            self.logger.info("Completed download and extraction.")

        return extract_dir / "package"

    def create_arktsconfig(self, panda_home: Path, config_file_path: Path) -> None:
        """Create ArkTS configuration file."""
        config_content = {
            "compilerOptions": {
                "baseUrl": str(panda_home),
                "paths": {
                    "std": [str(panda_home / "../ets/stdlib/std")],
                    "escompat": [str(panda_home / "../ets/stdlib/escompat")],
                    "@ohos.base": [str(self.generated_dir / "@ohos.base.ets")],
                    "@generated": [str(self.generated_dir)],
                    "@system": [str(self.system_dir)],
                },
            }
        }

        with open(config_file_path, "w") as json_file:
            json.dump(config_content, json_file, indent=2)

        self.logger.debug(f"Created configuration file at: {config_file_path}")

    def compile_abc(
        self,
        output_dir: Path,
        input_dir: Path,
        panda_home: Path,
        config_file_path: Path,
    ) -> list[Path]:
        """Compile ETS files to ABC format."""
        output_files = []

        if not input_dir.exists() or not input_dir.is_dir():
            self.logger.warning(
                f"Input directory does not exist or is not a directory: {input_dir}"
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
                    f"ark_disasm not found at {ark_disasm_path}, skipping disassembly"
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

    def link_abc(self, target: Path, *input_files, panda_home: Path) -> None:
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

    def compile_shared_library(self, panda_include_dir: Path) -> Path:
        """Compile the shared library."""
        self.logger.info("Compiling shared library...")

        so_target = self.build_dir / f"lib{self.lib_name}.so"

        # Compile each component
        runtime_objects = self.compile(
            self.build_runtime_src_dir,
            self.config.runtime_src_dir,
            panda_include_dir,
            self.config.runtime_include_dir,
        )
        generated_objects = self.compile(
            self.build_generated_src_dir,
            self.generated_src_dir,
            panda_include_dir,
            self.config.runtime_include_dir,
            self.generated_include_dir,
        )
        author_objects = self.compile(
            self.build_author_src_dir,
            self.author_src_dir,
            panda_include_dir,
            self.config.runtime_include_dir,
            self.generated_include_dir,
            self.author_include_dir,
        )

        # Link all objects
        if all_objects := runtime_objects + generated_objects + author_objects:
            self.link(
                so_target,
                *all_objects,
                shared=True,
                link_options=["-Wl,--no-undefined"],
            )
            self.logger.info(f"Shared library compiled: {so_target}")
        else:
            self.logger.warning(
                "No object files to link, skipping shared library compilation"
            )

        return so_target

    def compile_and_link_abc(self, panda_home: Path, config_file_path: Path) -> Path:
        """Compile and link ABC files."""
        self.logger.info("Compiling and linking ABC files...")

        abc_target = self.build_dir / "main.abc"

        # Compile ETS files in each directory
        generated_abc = self.compile_abc(
            self.build_generated_dir,
            self.generated_dir,
            panda_home,
            config_file_path,
        )
        user_abc = self.compile_abc(
            self.build_user_dir,
            self.user_dir,
            panda_home,
            config_file_path,
        )
        system_abc = self.compile_abc(
            self.build_system_dir,
            self.system_dir,
            panda_home,
            config_file_path,
        )

        # Link all ABC files
        if all_abc_files := generated_abc + user_abc + system_abc:
            self.link_abc(
                abc_target,
                *all_abc_files,
                panda_home=panda_home,
            )
            self.logger.info(f"ABC files linked: {abc_target}")
        else:
            self.logger.warning("No ABC files to link, skipping ABC compilation")

        return abc_target

    def run_ark(self, panda_home: Path, abc_target: Path) -> None:
        """Run the compiled ABC file with the Ark runtime."""
        if not abc_target.exists():
            self.logger.error(f"ABC file not found: {abc_target}")
            raise FileNotFoundError(f"ABC file not found: {abc_target}")

        ark_path = panda_home / "bin/ark"
        if not ark_path.exists():
            raise FileNotFoundError(f"ark executable not found at {ark_path}")

        etsstdlib_path = panda_home / "../ets/etsstdlib.abc"
        if not etsstdlib_path.exists():
            self.logger.warning(f"etsstdlib.abc not found at {etsstdlib_path}")

        self.logger.info(f"Running with Ark runtime: {abc_target}")
        self.run_command(
            [
                ark_path,
                f"--boot-panda-files={etsstdlib_path}",
                f"--load-runtimes=ets",
                abc_target,
                "main.ETSGLOBAL::main",
            ],
            env={"LD_LIBRARY_PATH": str(self.build_dir)},
            capture_output=False,
        )


class UpgradeCode(Utils):
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

    def upgrade_code(self, repo_url: str):
        filename = repo_url.split("/")[-1]
        version = repo_url.split("/")[-2]
        extract_dir = self.config.base_dir.parent
        target_file = extract_dir / filename
        version_file = self.config.base_dir / "version.txt"
        with open(version_file) as vf:
            version_str = vf.read()
            local_version = version_str.splitlines()[0].split(":")[-1].strip()
        if local_version == version:
            self.logger.info(f"Already at version {version}")
            return

        self.download_file(target_file, repo_url)
        temp_dir = extract_dir / "temp_upgrade"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)
        self.extract_file(target_file, temp_dir)

        extracted_subdir = temp_dir / "taihe"
        current_subdir = self.config.base_dir
        shutil.rmtree(current_subdir)
        shutil.copytree(extracted_subdir, current_subdir)

        shutil.rmtree(temp_dir)
        if target_file.exists():
            target_file.unlink()

        self.logger.info(f"Successfully upgraded code to version {version}")


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
            help="The URL to update from",
        )

    parser = argparse.ArgumentParser(
        prog="taihe-tryit",
        description="Build and run project from a target directory",
    )
    subparsers = parser.add_subparsers(dest="command")

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

    parser_run = subparsers.add_parser(
        "run",
        help="Generate and build the project from the target directory",
    )
    add_argument_verbosity(parser_run)
    add_argument_target_directory(parser_run)
    add_argument_optimization(parser_run)
    add_argument_sts_keep_name(parser_run)

    parser_upgrade = subparsers.add_parser(
        "upgrade",
        help="Update using the specified URL",
    )
    add_argument_verbosity(parser_upgrade)
    add_argument_url(parser_upgrade)

    args = parser.parse_args()

    match args.verbose:
        case 0:
            verbosity = logging.INFO
        case 1:
            verbosity = logging.DEBUG
        case _:
            verbosity = logging.DEBUG

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
            case "run":
                BuildSystem(
                    args.target_directory,
                    config=config,
                    verbosity=verbosity,
                    opt_level=args.optimization,
                    sts_keep_name=args.sts_keep_name,
                ).generate_and_build()
            case "upgrade":
                UpgradeCode(
                    args.URL,
                    config=config,
                    verbosity=verbosity,
                ).upgrade_code(args.URL)
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
