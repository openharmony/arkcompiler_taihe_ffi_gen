from antlr4 import FileStream
from TaiheLexer import TaiheLexer
from TaiheParser import TaiheParser
from TaiheAST import TaiheAST
from ast import generate_ast
from exceptions import *
import argparse
import os
def find_on_tree(tree, path):
    if len(path) == 0:
        return tree
    return find_on_tree(tree[path[0]], path[1:])
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-I', dest = 'src_dirs', nargs = '*')
    parser.add_argument('-O', dest = 'dst_dir')
    args = parser.parse_args()
    src_dirs, dst_dir = args.src_dirs, args.dst_dir
    src_paths = []
    # Find all .taihe files in the containing directories
    for src_dir in src_dirs:
        for src_path in os.listdir(src_dir):
            if os.path.splitext(src_path)[1].lower() == '.taihe':
                src_path = os.path.abspath(os.path.join(src_dir, src_path))
                src_paths.append(src_path)
    # Parse the codes into ASTs, map filenames to package names and namespaces, and check for namespace conflicts
    namespace_tree_root = {}
    packages: dict[tuple[str], tuple[str, TaiheAST.Specification]] = {}
    for src_path in src_paths:
        package_name = tuple(os.path.splitext(os.path.basename(src_path))[0].split('.'))
        spec = generate_ast(FileStream(src_path))
        fst_path, _ = packages.setdefault(package_name, (src_path, spec))
        if src_path != fst_path:
            raise PackageNameConflictError(src_path, fst_path)
        namespace_tree_current = namespace_tree_root
        for part in package_name:
            namespace_tree_current = namespace_tree_current.setdefault(part, {})
    # Check symbol collision, not considering `use` statements, generate symbol tables
    symbol_tables: dict[tuple[str], dict[str, TaiheAST.SpecificationFieldUni]] = {}
    for package_name, (src_path, spec) in packages.items():
        namespace_tree_current = find_on_tree(namespace_tree_root, package_name)
        print(package_name, namespace_tree_root, namespace_tree_current)
        symbol_table = symbol_tables[package_name]
        for field in spec.fields:
            symbol = field.name.text
            if symbol in namespace_tree_current:
                raise NamespaceConflictError(src_path, package_name, field)
            first = symbol_table.setdefault(symbol, field)
            if first is not field:
                raise SymbolCollisionError(src_path, field, first)
if __name__ == '__main__':
    main()
