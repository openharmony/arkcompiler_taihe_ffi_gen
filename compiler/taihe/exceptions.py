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
    def __init__(self, src_path: str, rec_pkname: ast.PackageNameUni, new_pkname: ast.PackageNameUni):
        self.src_path = src_path
        self.rec_pkname = rec_pkname
        self.new_pkname = new_pkname

    def __str__(self):
        pkname = ".".join(token.text for token in self.rec_pkname.parts)
        return f"{self.src_path!r}: {pos(self.new_pkname.parts[0])} and {pos(self.rec_pkname.parts[0])}: package alias {pkname!r} is used multiple times"


class SymbolConflictError(SemanticError):
    def __init__(self, src_path: str, rec_name: ast.token, new_name: ast.token):
        self.src_path = src_path
        self.rec_name = rec_name
        self.new_name = new_name

    def __str__(self):
        return f"{self.src_path!r}: {pos(self.new_name)} and {pos(self.rec_name)}: symbol {self.rec_name.text!r} is declared multiple times"


class SymbolConflictWithNamespaceError(SemanticError):
    def __init__(self, src_path: str, pktupl: tuple[str, ...], name: ast.token):
        self.src_path = src_path
        self.package_name = pktupl
        self.name = name

    def __str__(self):
        namespace = ".".join(self.package_name) + "." + self.name.text
        return f"{self.src_path!r}: {pos(self.name)}: {namespace!r} has been used as a namespace already"


class PackageNotExistError(SemanticError):
    def __init__(self, src_path: str, pkname: ast.PackageNameUni):
        self.src_path = src_path
        self.name = pkname

    def __str__(self):
        pkname = ".".join(token.text for token in self.name.parts)
        return f"{self.src_path!r}: {pos(self.name.parts[0])}, package {pkname!r} does not exist"


class SymbolNotExistError(SemanticError):
    def __init__(self, src_path: str, name: ast.token):
        self.src_path = src_path
        self.name = name

    def __str__(self):
        return f"{self.src_path!r}: {pos(self.name)}: symbol {self.name.text!r} does not exist"


class NotATypeError(SemanticError):
    def __init__(self, src_path: str, name: ast.token):
        self.src_path = src_path
        self.name = name

    def __str__(self):
        return f"{self.src_path!r}: {pos(self.name)}: symbol {self.name.text!r} is not a type"


class ReferenceTypeError(SemanticError):
    def __init__(self, src_path: str, name: ast.token):
        self.src_path = src_path
        self.name = name

    def __str__(self):
        return f"{self.src_path!r}: {pos(self.name)}: only value types can be used in the current context"


class CircularReferenceError(SemanticError):
    def __init__(self, start: tuple[tuple[str, ...], str], cycle: list[tuple[str, tuple[tuple[str, ...], str]]]):
        self.start = start
        self.cycle = cycle

    def __str__(self):
        pkname, text = self.start
        cycle_str = ".".join(pkname) + "." + text
        for name, (pkname, text) in self.cycle:
            cycle_str += " -> " + name + ": " + ".".join(pkname) + "." + text
        return f"circular reference has been found: {cycle_str}"
