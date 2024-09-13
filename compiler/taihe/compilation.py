import os

from antlr4 import FileStream

from taihe.parse.ast_generation import generate_ast
from taihe.code_generation import CodeGenerator
from taihe.semantic_analysis import Package, semantic_analysis


def compile(src_dirs, dst_dir, gen_author=True, gen_user=True):
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
        code_generator = CodeGenerator(package.name)
        for for_author, for_user, name, code in code_generator.visit(package.spec):
            if gen_author and for_author or gen_user and for_user:
                with open(os.path.join(dst_dir, name), "w") as file:
                    file.write(code)
