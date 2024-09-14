from dataclasses import dataclass

from taihe.exceptions import *
from taihe.parse import ast, Visitor


@dataclass
class Package:
    name: tuple[str, ...]
    path: str
    spec: ast.Specification


class SemanticAnalyzer(Visitor):
    def __init__(
        self,
        symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecificationFieldUni]],
        package_old: tuple[str, ...],
        package_path: str,
    ) -> None:
        self.symbol_tables = symbol_tables
        self.using_packages: dict[
            tuple[str, ...], tuple[ast.PackageUni, tuple[str, ...]]
        ] = {}
        self.using_symbols = {
            symbol: (field.name, package_old, symbol)
            for symbol, field in symbol_tables[package_old].items()
        }
        self.package_path = package_path

    def visit_UsePackage(self, node: ast.UsePackage):
        old_text = tuple(token.text for token in node.package_old.parts)
        symbol_table = self.symbol_tables.get(old_text)
        if symbol_table is None:
            raise PackageNotExistError(self.package_path, node.package_old)
        new_meta = node.package_new or node.package_old
        new_text = tuple(token.text for token in new_meta.parts)
        first_meta, _ = self.using_packages.setdefault(new_text, (new_meta, old_text))
        if first_meta != new_meta:
            raise PackageAliasConflictError(self.package_path, first_meta, new_meta)

    def visit_UseSymbol(self, node: ast.UseSymbol):
        package_text = tuple(token.text for token in node.package_old.parts)
        symbol_table = self.symbol_tables.get(package_text)
        if symbol_table is None:
            raise PackageNotExistError(self.package_path, node.package_old)
        for alias_pair in node.alias_pairs:
            old_text = alias_pair.old.text
            field = symbol_table.get(old_text)
            if field is None:
                raise SymbolNotExistError(self.package_path, alias_pair.old)
            if not isinstance(field, ast.TypeDeclUni):
                raise NotATypeError(self.package_path, alias_pair.old)
            new_meta = alias_pair.new or alias_pair.old
            new_text = new_meta.text
            first_meta, _, _ = self.using_symbols.setdefault(
                new_text, (new_meta, package_text, old_text)
            )
            if first_meta != new_meta:
                raise SymbolCollisionError(self.package_path, first_meta, new_meta)

    def visit_Specification(self, node: ast.Specification):
        while node.uses:
            self.visit(node.uses.pop())


def semantic_analysis(packages: list[Package]):
    # Generate packages dict, Check for package name conflicts
    packages_dict = {}
    for package in packages:
        other = packages_dict.setdefault(package.name, package)
        if other.path != package.path:
            raise PackageNameConflictError(package.path, other.path)
    # Generate namespace tree
    namespaces = {}
    namespace_tree = {}
    for package in packages:
        namespace = namespace_tree
        for part in package.name:
            namespace = namespace.setdefault(part, {})
        namespaces[package.name] = namespace
    # Check for symbol collisions, not considering `use` statements, generate symbol tables
    symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecificationFieldUni]] = {}
    for package in packages:
        symbol_table = symbol_tables.setdefault(package.name, {})
        for field in package.spec.fields:
            name_text = field.name.text
            if name_text in namespaces[package.name]:
                raise SymbolCollisionWithNamespaceError(
                    package.path, package.name, field.name
                )
            first = symbol_table.setdefault(name_text, field)
            if first is not field:
                raise SymbolCollisionError(package.path, field.name, first.name)
    # Check for package alias and using symbols
    for package in packages:
        analyzer = SemanticAnalyzer(symbol_tables, package.name, package.path)
        analyzer.visit(package.spec)
