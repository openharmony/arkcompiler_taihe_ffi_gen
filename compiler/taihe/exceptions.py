from taihe.parse import ast


def pos(name: ast.token):
    return f"line {name.line}, col {name.column}"


class SemanticError(Exception):
    pass


class PackageNameConflictError(SemanticError):
    def __init__(self, src_path: str, rec_path: str):
        self.src_path = src_path
        self.rec_path = rec_path

    def __str__(self):
        return f"file {self.src_path!r} and file {self.rec_path!r} have the same package name"


class PackageAliasConflictError(SemanticError):
    def __init__(
        self,
        src_path: str,
        rec_pkname: ast.PackageNameUni,
        new_pkname: ast.PackageNameUni,
    ):
        self.src_path = src_path
        self.rec_pkname = rec_pkname
        self.new_pkname = new_pkname

    def __str__(self):
        pkname = ".".join(token.text for token in self.rec_pkname.parts)
        return f"package alias {pkname!r} is used multiple times in {self.src_path!r}: {pos(self.new_pkname.parts[0])} and {pos(self.rec_pkname.parts[0])}"


class SymbolConflictError(SemanticError):
    def __init__(self, src_path: str, rec_name: ast.token, new_name: ast.token):
        self.src_path = src_path
        self.rec_name = rec_name
        self.new_name = new_name

    def __str__(self):
        return f"symbol {self.rec_name.text!r} is declared multiple times in {self.src_path!r}: {pos(self.new_name)} and {pos(self.rec_name)}"


class SymbolConflictWithNamespaceError(SemanticError):
    def __init__(self, src_path: str, pktupl: tuple[str, ...], name: ast.token):
        self.src_path = src_path
        self.package_name = pktupl
        self.name = name

    def __str__(self):
        namespace = ".".join(self.package_name) + "." + self.name.text
        return f"{namespace!r} in {self.src_path!r}: {pos(self.name)} has been used as a namespace already"


class PackageNotExistError(SemanticError):
    def __init__(self, src_path: str, pkname: ast.PackageNameUni):
        self.src_path = src_path
        self.name = pkname

    def __str__(self):
        pkname = ".".join(token.text for token in self.name.parts)
        return f"package {pkname!r} not exist, found in {self.src_path!r}: {pos(self.name.parts[0])}"


class SymbolNotExistError(SemanticError):
    def __init__(self, src_path: str, name: ast.token):
        self.src_path = src_path
        self.name = name

    def __str__(self):
        return f"symbol {self.name.text!r} not exist, found in {self.src_path!r}: line {pos(self.name)}"


class NotATypeError(SemanticError):
    def __init__(self, src_path: str, name: ast.token):
        self.src_path = src_path
        self.name = name

    def __str__(self):
        return f"symbol {self.name.text!r} in {self.src_path!r}: {pos(self.name)} is not a type"
