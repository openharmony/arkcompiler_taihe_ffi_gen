from TaiheAST import TaiheAST
from exceptions import *
from dataclasses import dataclass


@dataclass
class PackageInput:
    path: str
    name: tuple[str]
    spec: TaiheAST.Specification


@dataclass
class PackageOutput:
    name: tuple[str]
    spec: TaiheAST.Specification


def semantic_analysis(packages: list[PackageInput]) -> list[PackageOutput]:
    # Generate packages dict, Check for package name conflicts
    packages_dict = {}
    for package in packages:
        other_path, other_spec = packages_dict.setdefault(
            package.name, (package.path, package.spec)
        )
        if other_path != package.path:
            raise PackageNameConflictError(package.path, other_path)
    # Generate namespace tree
    namespaces = {}
    namespace_tree = {}
    for package in packages:
        namespace = namespace_tree
        for part in package.name:
            namespace = namespace.setdefault(part, {})
    # Check for symbol collisions, not considering `use` statements, generate symbol tables
    local_symbol_tables = {}
    for package in packages:
        local_symbol_table = local_symbol_tables.setdefault(package.name, {})
        for field in package.spec.fields:
            symbol = field.name.text
            if symbol in namespace:
                raise SymbolCollisionWithNamespaceError(
                    package.path, package.name, field
                )
            first = local_symbol_table.setdefault(symbol, field)
            if first is not field:
                raise SymbolCollisionError(package.path, field, first)
    # Check for package alias and using symbols
    # ...
    return packages
