from taihe.parse import ast


class SemanticError(Exception):
    pass


class PackageNameConflictError(SemanticError):
    def __init__(self, src_path: str, fst_path: str):
        self.src_path = src_path
        self.fst_path = fst_path

    def __str__(self):
        return (
            f"file {self.src_path!r} and {self.fst_path!r} have the same package name"
        )


class PackageAliasConflictError(SemanticError):
    def __init__(self, src_path: str, first: ast.PackageUni, alias: ast.PackageUni):
        self.src_path = src_path
        self.first = first
        self.alias = alias

    def __str__(self):
        return f"package alias {'.'.join(token.text for token in self.first.parts)!r} is used multiple times in {self.src_path!r}: line {self.alias.parts[0].line}, col {self.alias.parts[0].column} and line {self.first.parts[0].line}, col {self.first.parts[0].column}"


class SymbolCollisionError(SemanticError):
    def __init__(self, src_path: str, token: ast.token, first: ast.token):
        self.src_path = src_path
        self.token = token
        self.first = first

    def __str__(self):
        return f"symbol {self.token.text!r} is declared multiple times in {self.src_path!r}: line {self.first.line}, col {self.first.column} and line {self.token.line}, col {self.token.column}"


class SymbolCollisionWithNamespaceError(SemanticError):
    def __init__(self, src_path: str, package_name: tuple[str, ...], token: ast.token):
        self.src_path = src_path
        self.package_name = package_name
        self.token = token

    def __str__(self):
        return f"{'.'.join((*self.package_name, self.token.text))!r} in {self.src_path!r}: line {self.token.line}, col {self.token.column} has been used as a namespace"


class PackageNotExistError(SemanticError):
    def __init__(self, src_path: str, name: ast.PackageUni):
        self.src_path = src_path
        self.name = name

    def __str__(self):
        return f"package {'.'.join(token.text for token in self.name.parts)!r} not exist, found in {self.src_path!r}: line {self.name.parts[0].line}, col {self.name.parts[0].column}"


class SymbolNotExistError(SemanticError):
    def __init__(self, src_path: str, name: ast.token):
        self.src_path = src_path
        self.name = name

    def __str__(self):
        return f"symbol {self.name.text!r} not exist, found in {self.src_path!r}: line {self.name.line}, col {self.name.column}"


class NotATypeError(SemanticError):
    def __init__(self, src_path: str, name: ast.token):
        self.src_path = src_path
        self.name = name

    def __str__(self):
        return f"symbol {self.name.text!r} in {self.src_path!r}: line {self.name.line}, col {self.name.column} is not a type"
