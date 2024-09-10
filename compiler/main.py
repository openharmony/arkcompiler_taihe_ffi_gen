import argparse
import os

from antlr4 import FileStream

from compiler.ast_generation import generate_ast
from compiler.code_generation import CodeGenerator
from semantic_analysis import Package, semantic_analysis


def main():
    parser = argparse.ArgumentParser()
    # use -D{DLL_NAME}_DLLEXPORT / -D{DLL_NAME}_DLLIMPORT to export/import .dll when compiling
    parser.add_argument("dll_name", required=True, help="use -D{DLL_NAME}_DLLEXPORT / -D{DLL_NAME}_DLLIMPORT to export/import .dll when compiling")
    parser.add_argument("-I", dest="src_dirs", nargs="*", required=True, help="directories of .taihe source files")
    parser.add_argument("-O", dest="dst_dir", required=True, help="directory for generated .h and .cpp files")
    args = parser.parse_args()
    src_dirs, dst_dir, dll_name = args.src_dirs, args.dst_dir, args.dll_name
    # Find all .taihe files in the containing directories
    src_paths = []
    for src_dir in src_dirs:
        for src_path in os.listdir(src_dir):
            if os.path.splitext(src_path)[1].lower() == ".taihe":
                src_path = os.path.abspath(os.path.join(src_dir, src_path))
                src_paths.append(src_path)
    # Parse into ASTs
    packages = []
    for src_path in src_paths:
        package_name = tuple(os.path.splitext(os.path.basename(src_path))[0].split("."))
        spec = generate_ast(FileStream(src_path))
        packages.append(Package(src_path, package_name, spec))
    # Semantic analysis
    semantic_analysis(packages)
    # Code generation
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
    for package in packages:
        code_generator = CodeGenerator(package.name, dll_name)
        for name, code in code_generator.visit(package.spec):
            with open(os.path.join(dst_dir, name), "w") as file:
                file.write(code)


if __name__ == "__main__":
    main()
