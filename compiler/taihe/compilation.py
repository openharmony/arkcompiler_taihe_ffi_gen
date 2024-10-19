import os
import sys

if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup
from pathlib import Path

from antlr4 import FileStream

from taihe.code_generation import CodeGenerator
from taihe.parse.ast_generation import generate_ast
from taihe.semantic_analysis import Package, semantic_check, symbol_substitute


def compile(
    src_dirs: list[Path | str],
    dst_dir: Path | str,
    gen_author: bool = False,
    gen_user: bool = False,
) -> None:
    # Find all .taihe files in the containing directories
    src_paths = []
    for src_dir in src_dirs:
        for src_path in os.listdir(src_dir):
            if os.path.splitext(src_path)[1].lower() == ".taihe":
                src_path = os.path.abspath(os.path.join(src_dir, src_path))
                src_paths.append(src_path)

    # Parse into ASTs
    packages: list[Package] = []
    for src_path in src_paths:
        pktupl = tuple(os.path.splitext(os.path.basename(src_path))[0].split("."))
        try:
            spec = generate_ast(FileStream(src_path))
        except SyntaxError:
            raise SyntaxError(src_path) from None
        packages.append(Package(src_path, pktupl, spec))

    # Semantic analysis
    errors = []
    symbol_tables = symbol_substitute(errors, packages)
    semantic_check(errors, packages, symbol_tables)
    if errors:
        raise ExceptionGroup("Semantic Errors", errors)

    # Code generation
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
    for package in packages:
        code_generator = CodeGenerator(
            symbol_tables, package.tupl, author=gen_author, user=gen_user
        )
        code_generator.visit(package.spec)
        for dst_path, file in code_generator.files.items():
            file.output_to(os.path.join(dst_dir, dst_path))
