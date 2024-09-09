from antlr4 import FileStream

from ast_generation import ast_generation
from semantic_analysis import semantic_analysis, PackageInput, PackageOutput
from code_generation import CodeGenerator

import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-I', dest = 'src_dirs', nargs = '*')
    parser.add_argument('-O', dest = 'dst_dir')
    args = parser.parse_args()
    src_dirs, dst_dir = args.src_dirs, args.dst_dir
    # Find all .taihe files in the containing directories
    src_paths = []
    for src_dir in src_dirs:
        for src_path in os.listdir(src_dir):
            if os.path.splitext(src_path)[1].lower() == '.taihe':
                src_path = os.path.abspath(os.path.join(src_dir, src_path))
                src_paths.append(src_path)
    package_inputs = []
    for src_path in src_paths:
        package_name = tuple(os.path.splitext(os.path.basename(src_path))[0].split('.'))
        spec = ast_generation(FileStream(src_path))
        package_inputs.append(PackageInput(path=src_path, name=package_name, spec=spec))
    package_outputs = semantic_analysis(package_inputs)
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    for package_output in package_outputs:
        code_generator = CodeGenerator(package_output.name)
        for name, code in code_generator.visit(package_output.spec):
            with open(os.path.join(dst_dir, name), 'w') as file:
                file.write(code)

if __name__ == '__main__':
    main()
