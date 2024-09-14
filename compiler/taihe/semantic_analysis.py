from dataclasses import dataclass

from taihe.exceptions import *
from taihe.parse import ast, Visitor


@dataclass
class Package:
    tupl: tuple[str, ...]
    path: str
    spec: ast.Specification


class SemanticAnalyzer(Visitor):
    def __init__(
        self,
        symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecificationFieldUni]],
        old_pkname: tuple[str, ...],
        package_path: str,
    ) -> None:
        self.symbol_tables = symbol_tables
        self.using_packages: dict[
            tuple[str, ...], tuple[ast.PackageNameUni, tuple[str, ...]]
        ] = {}
        self.using_symbols = {
            symbol: (field.name, old_pkname, symbol)
            for symbol, field in symbol_tables[old_pkname].items()
        }
        self.package_path = package_path

    def visit_UsePackage(self, node: ast.UsePackage):
        old_pktupl = tuple(token.text for token in node.old_pkname.parts)
        symbol_table = self.symbol_tables.get(old_pktupl)
        if symbol_table is None:
            raise PackageNotExistError(self.package_path, node.old_pkname)
        new_pkname = node.new_pkname or node.old_pkname
        new_pktupl = tuple(token.text for token in new_pkname.parts)
        rec_pkname, _ = self.using_packages.setdefault(
            new_pktupl, (new_pkname, old_pktupl)
        )
        if rec_pkname != new_pkname:
            raise PackageAliasConflictError(self.package_path, rec_pkname, new_pkname)

    def visit_UseSymbol(self, node: ast.UseSymbol):
        pktupl = tuple(token.text for token in node.pkname.parts)
        symbol_table = self.symbol_tables.get(pktupl)
        if symbol_table is None:
            raise PackageNotExistError(self.package_path, node.pkname)
        for alias_pair in node.alias_pairs:
            old_text = alias_pair.old_name.text
            field = symbol_table.get(old_text)
            if field is None:
                raise SymbolNotExistError(self.package_path, alias_pair.old_name)
            if isinstance(field, ast.Const | ast.Function):
                raise NotATypeError(self.package_path, alias_pair.old_name)
            new_name = alias_pair.new_name or alias_pair.old_name
            new_text = new_name.text
            rec_name, _, _ = self.using_symbols.setdefault(
                new_text, (new_name, pktupl, old_text)
            )
            if rec_name != new_name:
                raise SymbolConflictError(self.package_path, rec_name, new_name)

    def visit_Specification(self, node: ast.Specification):
        while node.uses:
            self.visit(node.uses.pop())


def semantic_analysis(packages: list[Package]):
    # Generate packages dict, Check for package name conflicts
    packages_dict = {}
    for package in packages:
        other = packages_dict.setdefault(package.tupl, package)
        if other.path != package.path:
            raise PackageNameConflictError(package.path, other.path)
    # Generate namespace tree
    namespaces = {}
    namespace_tree = {}
    for package in packages:
        namespace = namespace_tree
        for part in package.tupl:
            namespace = namespace.setdefault(part, {})
        namespaces[package.tupl] = namespace
    # Check for symbol collisions, not considering `use` statements, generate symbol tables
    symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecificationFieldUni]] = {}
    for package in packages:
        symbol_table = symbol_tables.setdefault(package.tupl, {})
        for field in package.spec.fields:
            name_text = field.name.text
            if name_text in namespaces[package.tupl]:
                raise SymbolConflictWithNamespaceError(
                    package.path, package.tupl, field.name
                )
            first = symbol_table.setdefault(name_text, field)
            if first is not field:
                raise SymbolConflictError(package.path, field.name, first.name)
    # Check for package alias and using symbols
    for package in packages:
        analyzer = SemanticAnalyzer(symbol_tables, package.tupl, package.path)
        analyzer.visit(package.spec)
