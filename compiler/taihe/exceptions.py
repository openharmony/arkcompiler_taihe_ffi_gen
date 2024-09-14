from taihe.parse import ast


class SemanticError(Exception):
    pass


class PackageNameConflictError(SemanticError):
    def __init__(self, src_path: str, rec_path: str):
        self.src_path = src_path
        self.rec_path = rec_path

    def __str__(self):
        return (
            f"file {self.src_path!r} and {self.rec_path!r} have the same package name"
        )


class PackageAliasConflictError(SemanticError):
    def __init__(self, src_path: str, rec_pkname: ast.PackageNameUni, new_pkname: ast.PackageNameUni):
        self.src_path = src_path
        self.rec_pkname = rec_pkname
        self.new_pkname = new_pkname

    def __str__(self):
        return f"package alias {'.'.join(token.text for token in self.rec_pkname.parts)!r} is used multiple times in {self.src_path!r}: line {self.new_pkname.parts[0].line}, col {self.new_pkname.parts[0].column} and line {self.rec_pkname.parts[0].line}, col {self.rec_pkname.parts[0].column}"


class SymbolConflictError(SemanticError):
    def __init__(self, src_path: str, rec_name: ast.token, new_name: ast.token):
        self.src_path = src_path
        self.token = rec_name
        self.other = new_name

    def __str__(self):
        return f"symbol {self.token.text!r} is declared multiple times in {self.src_path!r}: line {self.other.line}, col {self.other.column} and line {self.token.line}, col {self.token.column}"


class SymbolConflictWithNamespaceError(SemanticError):
    def __init__(self, src_path: str, pktupl: tuple[str, ...], name: ast.token):
        self.src_path = src_path
        self.package_name = pktupl
        self.name = name

    def __str__(self):
        return f"{'.'.join((*self.package_name, self.name.text))!r} in {self.src_path!r}: line {self.name.line}, col {self.name.column} has been used as a namespace"


class PackageNotExistError(SemanticError):
    def __init__(self, src_path: str, pkname: ast.PackageNameUni):
        self.src_path = src_path
        self.name = pkname

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
