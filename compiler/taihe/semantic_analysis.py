from dataclasses import dataclass
from typing import Any

from numpy import isin

from taihe.exceptions import *
from taihe.parse import ast, Visitor


@dataclass
class Package:
    path: str
    tupl: tuple[str, ...]
    spec: ast.Specification


class SymbolReplacement(Visitor):
    def __init__(
        self,
        symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecificationFieldUni]],
        src_path: str,
        pktupl: tuple[str, ...],
    ) -> None:
        self.symbol_tables = symbol_tables
        self.src_path = src_path
        self.using_packages: dict[
            tuple[str, ...], tuple[ast.PackageNameUni, tuple[str, ...]]
        ] = {}
        self.using_symbols = {
            symbol: (field.name, pktupl, symbol)
            for symbol, field in symbol_tables[pktupl].items()
        }

    def visit_Specification(self, node: ast.Specification):
        while node.uses:
            self.visit(node.uses.pop())
        for field in node.fields:
            self.visit(field)

    def visit_UsePackage(self, node: ast.UsePackage):
        old_pktupl = tuple(token.text for token in node.old_pkname.parts)
        symbol_table = self.symbol_tables.get(old_pktupl)
        if symbol_table is None:
            raise PackageNotExistError(self.src_path, node.old_pkname)
        new_pkname = node.new_pkname or node.old_pkname
        new_pktupl = tuple(token.text for token in new_pkname.parts)
        rec_pkname, _ = self.using_packages.setdefault(
            new_pktupl, (new_pkname, old_pktupl)
        )
        if rec_pkname is not new_pkname:
            raise PackageAliasConflictError(self.src_path, rec_pkname, new_pkname)

    def visit_UseSymbol(self, node: ast.UseSymbol):
        pktupl = tuple(token.text for token in node.pkname.parts)
        symbol_table = self.symbol_tables.get(pktupl)
        if symbol_table is None:
            raise PackageNotExistError(self.src_path, node.pkname)
        for alias_pair in node.alias_pairs:
            old_text = alias_pair.old_name.text
            field = symbol_table.get(old_text)
            if field is None:
                raise SymbolNotExistError(self.src_path, alias_pair.old_name)
            new_name = alias_pair.new_name or alias_pair.old_name
            new_text = new_name.text
            rec_name, _, _ = self.using_symbols.setdefault(
                new_text, (new_name, pktupl, old_text)
            )
            if rec_name is not new_name:
                raise SymbolConflictError(self.src_path, rec_name, new_name)

    def visit_UserType(self, node: ast.UserType):
        if node.pkname is None:
            symbol = self.using_symbols.get(node.name.text)
            if symbol is None:
                raise SymbolNotExistError(self.src_path, node.name)
            _, pktupl, text = symbol
            target = self.symbol_tables[pktupl][text]
        else:
            pktupl = tuple(token.text for token in node.pkname.parts)
            package = self.using_packages.get(pktupl)
            if package is None:
                raise PackageNotExistError(self.src_path, node.pkname)
            _, pktupl = package
            target = self.symbol_tables[pktupl].get(node.name.text)
            if target is None:
                raise SymbolNotExistError(self.src_path, node.name)
        if isinstance(target, ast.Const | ast.Function):
            raise NotATypeError(self.src_path, node.name)
        node.pkname = ast.PackageName([ast.token(text) for text in pktupl])
        node.name.text = text


class SemanticAnalyzer(Visitor):
    def __init__(
        self,
        symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecificationFieldUni]],
        src_path: str,
    ) -> None:
        self.symbol_tables = symbol_tables
        self.src_path = src_path

    def generic_visit(self, node):
        raise NotImplementedError

    def visit_Specification(self, node: ast.Specification):
        for field in node.fields:
            self.visit(field)

    def visit_Function(self, node: ast.Function):
        parameters = {}
        for parameter in node.parameters:
            new_name = parameter.name
            rec_name = parameters.setdefault(new_name.text, new_name)
            if rec_name is not new_name:
                raise SymbolConflictError(self.src_path, rec_name, new_name)


def semantic_analysis(packages: list[Package]):
    # Generate packages dict, Check for package name conflicts
    packages_dict: dict[tuple[str, ...], Package] = {}
    for package in packages:
        other = packages_dict.setdefault(package.tupl, package)
        if other.path is not package.path:
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
        symbol_replacement = SymbolReplacement(
            symbol_tables, package.path, package.tupl
        )
        symbol_replacement.visit(package.spec)
    # Semantic analysis
    for package in packages:
        semantic_analyzer = SemanticAnalyzer(symbol_tables, package.path)
        semantic_analyzer.visit(package.spec)
