from dataclasses import dataclass

from taihe.exceptions import (
    EnumValueCollisionError,
    NotATypeError,
    PackageAliasConflictError,
    PackageAliasNotExistError,
    PackageNameConflictError,
    QualifierError,
    RecursiveInclusionError,
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
        self.using_packages: dict[tuple[str, ...], tuple[list[ast.token], tuple[str, ...]]] = {}
        self.using_symbols = {symbol: (field.name, pktupl, symbol) for symbol, field in symbol_tables[pktupl].items()}

    def visit_Spec(self, node: ast.Spec) -> None:
        while node.uses:
            self.visit(node.uses.pop())
        for field in node.fields:
            self.visit(field)

    def visit_UsePackage(self, node: ast.UsePackage) -> None:
        old_pktupl = tuple(token.text for token in node.old_pkname)
        symbol_table = self.symbol_tables.get(old_pktupl)
        if symbol_table is None:
            raise PackageAliasNotExistError(self.src_path, node.old_pkname)
        new_pkname = node.new_pkname or node.old_pkname
        new_pktupl = tuple(token.text for token in new_pkname)
        rec_pkname, _ = self.using_packages.setdefault(new_pktupl, (new_pkname, old_pktupl))
        if rec_pkname is not new_pkname:
            raise PackageAliasConflictError(self.src_path, rec_pkname, new_pkname)

    def visit_UseSymbol(self, node: ast.UseSymbol) -> None:
        pktupl = tuple(token.text for token in node.pkname)
        symbol_table = self.symbol_tables.get(pktupl)
        if symbol_table is None:
            raise PackageAliasNotExistError(self.src_path, node.pkname)
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

    # substitution
    def visit_UserType(self, node: ast.UserType) -> None:
        if not node.pkname:
            text = node.name.text
            symbol = self.using_symbols.get(text)
            if symbol is None:
                raise SymbolNotExistError(self.src_path, node.name)
            _, pktupl, text = symbol
            symbol_table = self.symbol_tables[pktupl]
            target = symbol_table[text]
        else:
            pktupl = tuple(token.text for token in node.pkname)
            package = self.using_packages.get(pktupl)
            if package is None:
                raise PackageAliasNotExistError(self.src_path, node.pkname)
            _, pktupl = package
            text = node.name.text
            symbol_table = self.symbol_tables[pktupl]
            target = symbol_table.get(text)
            if target is None:
                raise SymbolNotExistError(self.src_path, node.name)
        if isinstance(target, ast.Function):
            raise NotATypeError(self.src_path, node.name)
        node.pkname = [ast.token(text) for text in pktupl]
        node.name.text = text


def symbol_substitute(
    packages: list[Package],
) -> dict[tuple[str, ...], dict[str, ast.SpecField]]:
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

    # Check for package alias and using symbols and perform symbol substitution
    for package in packages:
        SymbolReplacer(symbol_tables, package.path, package.tupl).visit(package.spec)

    # return the symbol tables
    return symbol_tables


class SemanticAnalyzer(Visitor):
    def __init__(
        self,
        symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecField]],
        src_path: str,
    ) -> None:
        self.symbol_tables = symbol_tables
        self.src_path = src_path

    def generic_visit(self, node) -> None:
        raise NotImplementedError

    # Spec
    def visit_Spec(self, node: ast.Spec) -> None:
        for field in node.fields:
            self.visit(field)

    # SpecField
    def visit_Function(self, node: ast.Function) -> None:
        parameters = {}
        for parameter in node.parameters:
            new_name = parameter.name
            rec_name = parameters.setdefault(new_name.text, new_name)
            if rec_name is not new_name:
                raise SymbolConflictError(self.src_path, rec_name, new_name)
            mut = parameter.param_type.mut
            type = parameter.param_type.type
            if mut is not None and not can_be_mutable(self.symbol_tables, type):
                raise QualifierError(self.src_path, node.name, mut)

    def visit_Struct(self, node: ast.Struct) -> None:
        fields = {}
        for field in node.fields:
            new_name = field.name
            rec_name = fields.setdefault(new_name.text, new_name)
            if rec_name is not new_name:
                raise SymbolConflictError(self.src_path, rec_name, new_name)

    def visit_Enum(self, node: ast.Enum) -> None:
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


def can_be_mutable(
    symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecField]],
    node: ast.Type,
) -> bool:
    if isinstance(node, ast.PrimitiveType):
        if node.name.text in ("bool", "f32", "f64", "i8", "i16", "i32", "i64", "u8", "u16", "u32", "u64", "String"):
            return False
        raise NotImplementedError

    if isinstance(node, ast.UserType):
        pktupl = tuple(token.text for token in node.pkname)
        text = node.name.text
        target = symbol_tables[pktupl][text]
        if isinstance(target, ast.Enum):
            return False
        if isinstance(target, ast.Struct):
            return True
        if isinstance(target, ast.Runtimeclass | ast.Interface):
            return True
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


def check_cycle(struct_table) -> None:
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
            raise RecursiveInclusionError(*result)


def semantic_check(
    packages: list[Package],
    symbol_tables: dict[tuple[str, ...], dict[str, ast.SpecField]],
) -> None:
    # Semantic checking within each file
    for package in packages:
        SemanticAnalyzer(symbol_tables, package.path).visit(package.spec)

    # Check for circular reference in structs
    struct_table = {}
    for package in packages:
        for node in package.spec.fields:
            if not isinstance(node, ast.Struct):
                continue
            struct_name = node.name.text
            children = struct_table.setdefault((package.tupl, struct_name), [])
            for child in node.fields:
                child_name = child.name.text
                child_type = child.type
                if not isinstance(child_type, ast.UserType):
                    continue
                child_pktupl = tuple(token.text for token in child_type.pkname)
                child_text = child_type.name.text
                child_target = symbol_tables[child_pktupl][child_text]
                if isinstance(child_target, ast.Struct):
                    children.append((child_name, (child_pktupl, child_text)))
    check_cycle(struct_table)
