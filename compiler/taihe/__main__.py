import argparse
import sys
from pathlib import Path

from taihe.driver import CompilerInstance, CompilerInvocation


def main():
    parser = argparse.ArgumentParser()
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
        help="generate files for interface author",
    )
    parser.add_argument(
        "--user",
        "-u",
        action="store_true",
        help="generate files for interface user",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="debug mode",
    )
    args = parser.parse_args()
    invocation = CompilerInvocation(
        src_dirs=[Path(d) for d in args.src_dirs],
        out_dir=Path(args.dst_dir),
        gen_author=args.author,
        gen_user=args.user,
        debug=args.debug,
    )
    instance = CompilerInstance(invocation)
    if not instance.run():
        return -1
    return 0


if __name__ == "__main__":
    sys.exit(main())
