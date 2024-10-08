from dataclasses import dataclass

from taihe.parse import ast


class SemanticError(Exception):
    pass


@dataclass
class PackageNameConflictError(SemanticError):
    pktupl: tuple[str, ...]
    pks: list


@dataclass
class SymbolConflictWithNamespaceError(SemanticError):
    src_path: str
    pktupl: tuple[str, ...]
    name: ast.token


@dataclass
class SymbolConflictError(SemanticError):
    src_path: str
    name: str
    metas: list[ast.token]


@dataclass
class EnumValueCollisionError(SemanticError):
    src_path: str
    val: int
    metas: list[ast.token]


@dataclass
class PackageAliasConflictError(SemanticError):
    src_path: str
    symbol: tuple[str, ...]
    pkmetas: list[list[ast.token]]


@dataclass
class PackageNotExistError(SemanticError):
    src_path: str
    pkmeta: list[ast.token]


@dataclass
class PackageNotImportedError(SemanticError):
    src_path: str
    pkmeta: list[ast.token]


@dataclass
class TypeAliasConflictError(SemanticError):
    src_path: str
    name: str
    metas: list[ast.token]


@dataclass
class TypeNotExistError(SemanticError):
    src_path: str
    meta: ast.token


@dataclass
class TypeNotImportedError(SemanticError):
    src_path: str
    meta: ast.token


@dataclass
class QualifierError(SemanticError):
    src_path: str
    type: ast.Type
    qualifier: ast.token


@dataclass
class RecursiveInclusionError(SemanticError):
    start: tuple[tuple[str, ...], str]
    cycle: list[tuple[str, tuple[tuple[str, ...], str]]]
