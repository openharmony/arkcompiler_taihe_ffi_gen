import argparse
from taihe.compilation import compile


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
    args = parser.parse_args()
    compile(args.src_dirs, args.dst_dir)


if __name__ == "__main__":
    main()
