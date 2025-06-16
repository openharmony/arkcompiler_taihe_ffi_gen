import argparse
import sys
from pathlib import Path

from taihe.driver.backend import BackendConfig, BackendRegistry
from taihe.driver.contexts import CompilerInstance, CompilerInvocation


def main():
    parser = argparse.ArgumentParser(
        prog="taihec",
        description="generates source code from taihe files",
    )
    parser.add_argument(
        "-I",
        dest="src_dirs",
        nargs="*",
        required=True,
        help="directories of .taihe source files",
    )
    parser.add_argument(
        "-O",
        dest="dst_dir",
        required=True,
        help="directory for generated .h and .cpp files",
    )
    parser.add_argument(
        "--author",
        "-a",
        action="store_true",
        help="generate sources for API authors",
    )
    parser.add_argument(
        "--user",
        "-u",
        action="store_true",
        help="generate sources for API users",
    )
    parser.add_argument(
        "--ani",
        action="store_true",
        help="generate sources for ANI binding",
    )
    parser.add_argument(
        "--c-impl",
        action="store_true",
        help="generate skeleton for C implementation",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="debug mode",
    )
    parser.add_argument(
        "--sts-keep-name",
        action="store_true",
        help="keep original function and interface method names",
    )
    parser.add_argument(
        "--arkts-module-prefix",
        type=str,
        default=None,
        help="prefix for the generated ArkTS module name",
    )
    parser.add_argument(
        "--arkts-path-prefix",
        type=str,
        default=None,
        help="path to the generated ArkTS module",
    )
    args = parser.parse_args()

    registry = BackendRegistry()
    registry.register_all()

    enabled_backend_names: list[str] = []
    if args.author:
        enabled_backend_names.append("cpp-author")
    if args.ani:
        enabled_backend_names.append("ani-bridge")
    if args.debug:
        enabled_backend_names.append("pretty-print")

    resolved_backends: list[BackendConfig] = []
    for b in registry.collect_required_backends(enabled_backend_names):
        resolved_backends.append(b())

    invocation = CompilerInvocation(
        src_dirs=[Path(d) for d in args.src_dirs],
        out_dir=Path(args.dst_dir),
        backends=resolved_backends,
        sts_keep_name=args.sts_keep_name,
        arkts_module_prefix=args.arkts_module_prefix,
        arkts_path_prefix=args.arkts_path_prefix,
    )
    instance = CompilerInstance(invocation)
    if not instance.run():
        return -1
    return 0


if __name__ == "__main__":
    sys.exit(main())
