class SemanticError(Exception):
    pass


class PackageNameConflictError(SemanticError):
    def __init__(self, src_path, fst_path):
        self.src_path = src_path
        self.fst_path = fst_path
    def __str__(self):
        return f'file {self.src_path!r} and {self.fst_path!r} have the same package name'


class SymbolCollisionError(SemanticError):
    def __init__(self, src_path, field, first):
        self.src_path = src_path
        self.field = field
        self.first = first
    def __str__(self):
        return f'symbol {self.field.name.text!r} is declared multiple times in {self.src_path!r}: line {self.first.name.line}, col {self.first.name.column} and line {self.field.name.line}, col {self.field.name.column}'


class SymbolCollisionWithNamespaceError(SemanticError):
    def __init__(self, src_path, package_name, field):
        self.src_path = src_path
        self.package_name = package_name
        self.field = field
    def __str__(self):
        symbol = '.'.join((*self.package_name, self.field.name.text))
        return f'{symbol!r} in {self.src_path!r}: line {self.field.name.line}, col {self.field.name.column} has been used as a namespace'
