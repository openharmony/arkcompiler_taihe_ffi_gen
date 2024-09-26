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


class SymbolConflictWithNamespaceError(SemanticError):
    def __init__(self, src_path: str, pktupl: tuple[str, ...], name: ast.token):
        self.src_path = src_path
        self.package_name = pktupl
        self.name = name

    def __str__(self):
        namespace = ".".join(self.package_name) + "." + self.name.text
        return f"{self.src_path!r}: {pos(self.name)}: {namespace!r} has been used as a namespace already"


class PackageAliasConflictError(SemanticError):
    def __init__(self, src_path: str, rec_pkname: list[ast.token], new_pkname: list[ast.token]):
        self.src_path = src_path
        self.rec_pkname = rec_pkname
        self.new_pkname = new_pkname

    def __str__(self):
        pkname = ".".join(token.text for token in self.rec_pkname)
        return f"{self.src_path!r}: {pos(self.new_pkname[0])} and {pos(self.rec_pkname[0])}: package alias {pkname!r} is used multiple times"


class SymbolConflictError(SemanticError):
    def __init__(self, src_path: str, rec_name: ast.token, new_name: ast.token):
        self.src_path = src_path
        self.rec_name = rec_name
        self.new_name = new_name

    def __str__(self):
        return f"{self.src_path!r}: {pos(self.new_name)} and {pos(self.rec_name)}: symbol {self.rec_name.text!r} is declared multiple times"


class PackageAliasNotExistError(SemanticError):
    def __init__(self, src_path: str, pkname: list[ast.token]):
        self.src_path = src_path
        self.pkname = pkname

    def __str__(self):
        pkname = ".".join(token.text for token in self.pkname)
        return f"{self.src_path!r}: {pos(self.pkname[0])}, package alias {pkname!r} does not exist"


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


class QualifierError(SemanticError):
    def __init__(self, src_path: str, type: ast.token, qualifier: ast.token):
        self.src_path = src_path
        self.type = type
        self.qualifier = qualifier

    def __str__(self):
        return f"{self.src_path!r}: {pos(self.qualifier)}: {self.qualifier.text!r} cannot be used to {self.type.text!r}"


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


class EnumValueCollisionError(SemanticError):
    def __init__(self, src_path: str, enum_name: ast.token, rec_name: ast.token, new_name: ast.token, val: int):
        self.src_path = src_path
        self.enum_name = enum_name
        self.rec_name = rec_name
        self.new_name = new_name
        self.val = val

    def __str__(self):
        return f"{self.src_path!r}: {pos(self.enum_name)}: {self.rec_name.text!r} and {self.new_name.text!r} in enum class {self.enum_name.text!r} have the same value {self.val}"
