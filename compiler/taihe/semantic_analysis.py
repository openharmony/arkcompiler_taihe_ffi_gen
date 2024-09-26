from dataclasses import dataclass

from taihe.exceptions import (
    CircularReferenceError,
    EnumValueCollisionError,
    NotATypeError,
    PackageAliasConflictError,
    PackageNameConflictError,
    PackageNotExistError,
    QualifierError,
    SymbolConflictError,
    SymbolConflictWithNamespaceError,
    SymbolNotExistError,
)
from taihe.parse import Visitor, ast


@dataclass
class Package:
    path: str
    tupl: tuple[str, ...]
    spec: ast.Spec


class SymbolReplacer(Visitor):
    def __init__(
        self,
        symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecField]],
        src_path: str,
        pktupl: tuple[str, ...],
    ) -> None:
        self.symbol_tables = symbol_tables
        self.src_path = src_path
        self.using_packages: dict[tuple[str, ...], tuple[ast.PackageName, tuple[str, ...]]] = {}
        self.using_symbols = {symbol: (field.name, pktupl, symbol) for symbol, field in symbol_tables[pktupl].items()}

    def visit_Spec(self, node: ast.Spec):
        while node.uses:
            self.visit(node.uses.pop())
        for field in node.fields:
            self.visit(field)

    def visit_UsePackage(self, node: ast.UsePackage):
        old_pktupl = tuple(token.text for token in node.old_pkname.parts)
        symbol_table = self.symbol_tables.get(old_pktupl)
        if symbol_table is None:
            raise PackageNotExistError(self.src_path, node.old_pkname)
        # new_pkname = node.new_pkname or node.old_pkname
        if node.new_pkname:
            new_pkname = ast.PackageName(node.new_pkname.parts)
        else:
            new_pkname = ast.PackageName(node.old_pkname.parts)
        new_pktupl = tuple(token.text for token in new_pkname.parts)
        rec_pkname, _ = self.using_packages.setdefault(new_pktupl, (new_pkname, old_pktupl))
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
            rec_name, _, _ = self.using_symbols.setdefault(new_text, (new_name, pktupl, old_text))
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
            text = node.name.text
            target = self.symbol_tables[pktupl].get(node.name.text)
            if target is None:
                raise SymbolNotExistError(self.src_path, node.name)
        if isinstance(target, ast.Function):
            raise NotATypeError(self.src_path, node.name)
        node.pkname = ast.PackageName([ast.token(text) for text in pktupl])
        node.name.text = text


class SemanticAnalyzer(Visitor):
    def __init__(
        self,
        symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecField]],
        src_path: str,
    ) -> None:
        self.symbol_tables = symbol_tables
        self.src_path = src_path

    def generic_visit(self, node):
        raise NotImplementedError

    # Spec
    def visit_Spec(self, node: ast.Spec):
        for field in node.fields:
            self.visit(field)

    # SpecField
    def visit_Function(self, node: ast.Function):
        parameters = {}
        for parameter in node.parameters:
            new_name = parameter.name
            rec_name = parameters.setdefault(new_name.text, new_name)
            if rec_name is not new_name:
                raise SymbolConflictError(self.src_path, rec_name, new_name)
            parameter.param_type.mut = convert_qualifier(
                self,
                parameter.param_type.type,
                parameter.param_type.mut,
            )

    def visit_Struct(self, node: ast.Struct):
        fields = {}
        for field in node.fields:
            new_name = field.name
            rec_name = fields.setdefault(new_name.text, new_name)
            if rec_name is not new_name:
                raise SymbolConflictError(self.src_path, rec_name, new_name)

    def visit_Enum(self, node: ast.Enum):
        fields = {}
        vals = {}
        val = 0
        for field in node.fields:
            new_name = field.name
            rec_name = fields.setdefault(new_name.text, new_name)
            if rec_name is not new_name:
                raise SymbolConflictError(self.src_path, rec_name, new_name)
            if field.expr is not None:
                val = get_int_val(field.expr)
            field.expr = ast.IntLiteralExpr(ast.token(str(val)))
            rec_name = vals.setdefault(val, field.name)
            if rec_name is not new_name:
                raise EnumValueCollisionError(self.src_path, node.name, rec_name, new_name, val)
            val += 1


def convert_qualifier(self: SemanticAnalyzer, node: ast.Type, mut: ast.token | None) -> ast.token | None:
    if isinstance(node, ast.BasicType):
        if node.name.text in ("bool", "f32", "f64", "i8", "i16", "i32", "i64", "u8", "u16", "u32", "u64"):
            if mut is not None:
                raise QualifierError(self.src_path, node.name, mut)
            return None
        if node.name.text == "String":
            if mut is not None:
                raise QualifierError(self.src_path, node.name, mut)
            return None
        raise NotImplementedError

    if isinstance(node, ast.UserType):
        assert node.pkname
        pktupl = tuple(token.text for token in node.pkname.parts)
        type_name = node.name.text
        spec = self.symbol_tables[pktupl][type_name]
        if isinstance(spec, ast.Enum):
            if mut is not None:
                raise QualifierError(self.src_path, node.name, mut)
            return None
        if isinstance(spec, ast.Struct):
            return ast.token("mut") if mut is not None else ast.token("ref")
        if isinstance(spec, ast.Runtimeclass | ast.Interface):
            return None if mut is not None else ast.token("const")
        raise NotImplementedError
    
    raise NotImplementedError


def get_int_val(node: ast.IntExpr) -> int:
    if isinstance(node, ast.IntLiteralExpr):
        text = node.val.text
        if text.startswith("0b"):
            return int(text, 2)
        if text.startswith("0o"):
            return int(text, 8)
        if text.startswith("0x"):
            return int(text, 16)
        return int(text)

    if isinstance(node, ast.IntParenthesisExpr):
        return get_int_val(node.expr)

    if isinstance(node, ast.IntConditionalExpr):
        return get_int_val(node.then_expr) if get_bool_val(node.cond) else get_int_val(node.else_expr)

    if isinstance(node, ast.IntUnaryExpr):
        return {
            "-": int.__neg__,
            "+": int.__pos__,
            "~": int.__invert__,
        }[node.op.text](
            get_int_val(node.expr),
        )

    if isinstance(node, ast.IntBinaryExpr):
        return {
            "+": int.__add__,
            "-": int.__sub__,
            "*": int.__mul__,
            "/": int.__floordiv__,
            "%": int.__mod__,
            "<<": int.__lshift__,
            ">>": int.__rshift__,
            "&": int.__and__,
            "|": int.__or__,
            "^": int.__xor__,
        }[node.op.text](
            get_int_val(node.left),
            get_int_val(node.right),
        )
    
    raise NotImplementedError


def get_bool_val(node: ast.BoolExpr) -> bool:
    if isinstance(node, ast.IntComparisonExpr):
        return {
            ">": int.__gt__,
            "<": int.__lt__,
            ">=": int.__ge__,
            "<=": int.__le__,
            "==": int.__eq__,
            "!=": int.__ne__,
        }[node.op.text](
            get_int_val(node.left),
            get_int_val(node.right),
        )

    if isinstance(node, ast.BoolUnaryExpr):
        assert node.op.text == "!"
        return not get_bool_val(node.expr)

    if isinstance(node, ast.BoolBinaryExpr):
        return {
            "&&": bool.__and__,
            "||": bool.__or__,
        }[node.op.text](
            get_bool_val(node.left),
            get_bool_val(node.right),
        )

    if isinstance(node, ast.BoolParenthesisExpr):
        return get_bool_val(node.expr)

    if isinstance(node, ast.BoolConditionalExpr):
        return get_bool_val(node.then_expr) if get_bool_val(node.cond) else get_bool_val(node.else_expr)
    
    raise NotImplementedError


def check_cycle(struct_table):
    visited = set()
    visiting_dict = {}
    visiting_list = []

    def visit(struct) -> tuple | None:
        if struct in visited:
            return None
        idx = len(visiting_list)
        rec = visiting_dict.setdefault(struct, idx)
        if rec != idx:
            return struct, visiting_list[rec:]
        for name, child in struct_table[struct]:
            visiting_list.append((name, child))
            result = visit(child)
            if result is not None:
                return result
            visiting_list.pop()
        visiting_dict.pop(struct)

    for struct in struct_table:
        result = visit(struct)
        if result is not None:
            raise CircularReferenceError(*result)


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
    symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecField]] = {}
    for package in packages:
        symbol_table = symbol_tables.setdefault(package.tupl, {})
        for field in package.spec.fields:
            name_text = field.name.text
            if name_text in namespaces[package.tupl]:
                raise SymbolConflictWithNamespaceError(package.path, package.tupl, field.name)
            first = symbol_table.setdefault(name_text, field)
            if first is not field:
                raise SymbolConflictError(package.path, field.name, first.name)

    # Check for package alias and using symbols
    for package in packages:
        symbol_replacer = SymbolReplacer(symbol_tables, package.path, package.tupl)
        symbol_replacer.visit(package.spec)

    # Semantic analysis (type errors, symbol conflicts)
    for package in packages:
        semantic_analyzer = SemanticAnalyzer(symbol_tables, package.path)
        semantic_analyzer.visit(package.spec)

    # Check for circular reference in structs
    struct_table = {}
    for package in packages:
        for decl in package.spec.fields:
            if not isinstance(decl, ast.Struct):
                continue
            struct_name = decl.name.text
            child = struct_table.setdefault((package.tupl, struct_name), [])
            for attr in decl.fields:
                name = attr.name.text
                type = attr.type
                if not isinstance(type, ast.UserType):
                    continue
                assert type.pkname
                pktupl = tuple(token.text for token in type.pkname.parts)
                type_name = type.name.text
                if isinstance(symbol_tables[pktupl][type_name], ast.Struct):
                    child.append((name, (pktupl, type_name)))
    check_cycle(struct_table)
