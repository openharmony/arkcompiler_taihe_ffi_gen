from dataclasses import dataclass

from exceptions import *
from TaiheAST import TaiheAST
from TaiheVisitor import TaiheVisitor


@dataclass
class Package:
    path: str
    name: tuple[str]
    spec: TaiheAST.Specification


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
    local_symbol_tables = {}
    for package in packages:
        local_symbol_table = local_symbol_tables.setdefault(package.name, {})
        for field in package.spec.fields:
            symbol = field.name.text
            if symbol in namespaces[package.name]:
                raise SymbolCollisionWithNamespaceError(package.path, package.name, field)
            first = local_symbol_table.setdefault(symbol, field)
            if first is not field:
                raise SymbolCollisionError(package.path, field, first)
    # Check for package alias and using symbols
    # ...
