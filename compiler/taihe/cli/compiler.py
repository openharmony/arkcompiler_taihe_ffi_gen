import argparse
import sys
from pathlib import Path

from taihe.driver.backend import BackendConfig, BackendRegistry
from taihe.driver.contexts import CompilerInstance, CompilerInvocation
from taihe.utils.outputs import CMakeOutputConfig, OutputConfig


def main(for_distribution: bool = False):
    registry = BackendRegistry()
    registry.register_all()

    parser = argparse.ArgumentParser(
        prog="taihec",
        description="generates source code from taihe files",
    )
    parser.add_argument(
        "src_files",
        type=Path,
        nargs="*",
        default=[],
        help="input .taihe files, if not provided, will read from stdin",
    )
    parser.add_argument(
        "-I",
        type=Path,
        dest="src_dirs",
        nargs="*",
        default=[],
        help="directories of .taihe source files",
    )  # deprecated
    parser.add_argument(
        "--output",
        "-O",
        type=Path,
        dest="dst_dir",
        required=True,
        help="directory for generated files",
    )
    parser.add_argument(
        "--generate",
        "-G",
        dest="backends",
        nargs="*",
        default=[],
        choices=registry.get_backend_names(),
        help="backends to generate sources, default: abi-header, abi-source, c-author",
    )
    parser.add_argument(
        "--codegen",
        "-C",
        dest="config",
        action="append",
        default=[],
        help="additional code generation configuration",
    )
    parser.add_argument(
        "--build",
        "-B",
        dest="build_system",
        choices=["cmake"],
        help="build system to use for generated sources",
    )
    args = parser.parse_args()

    resolved_backends: list[BackendConfig] = []
    for b in registry.collect_required_backends(args.backends):
        resolved_backends.append(b())

    current_file = Path(__file__).resolve()
    if for_distribution:
        taihe_root_dir = current_file.parents[5]
        runtime_include_dir = taihe_root_dir / "include"
        runtime_src_dir = taihe_root_dir / "src" / "taihe" / "runtime"
    else:
        taihe_root_dir = current_file.parents[3]
        runtime_include_dir = taihe_root_dir / "runtime" / "include"
        runtime_src_dir = taihe_root_dir / "runtime" / "src"

    if args.build_system == "cmake":
        output_config = CMakeOutputConfig(
            dst_dir=Path(args.dst_dir),
            runtime_include_dir=runtime_include_dir,
            runtime_src_dir=runtime_src_dir,
        )
    else:
        output_config = OutputConfig(
            dst_dir=Path(args.dst_dir),
        )

    invocation = CompilerInvocation(
        src_files=args.src_files,
        src_dirs=args.src_dirs,
        output_config=output_config,
        backends=resolved_backends,
    )

    for config in args.config:
        k, *v = config.split("=", 1)
        if k == "sts:keep-name":
            invocation.sts_keep_name = True
        elif k == "arkts:module-prefix":
            invocation.arkts_module_prefix = v[0] if v else None
        elif k == "arkts:path-prefix":
            invocation.arkts_path_prefix = v[0] if v else None
        else:
            raise ValueError(f"unknown codegen config {k!r}")

    instance = CompilerInstance(invocation)
    if not instance.run():
        return -1
    return 0


if __name__ == "__main__":
    sys.exit(main())
