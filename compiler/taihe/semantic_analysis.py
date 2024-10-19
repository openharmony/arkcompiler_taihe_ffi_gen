from dataclasses import dataclass

from taihe.exceptions import (
    EnumValueCollisionError,
    PackageAliasConflictError,
    PackageNameConflictError,
    PackageNotExistError,
    PackageNotImportedError,
    QualifierError,
    RecursiveInclusionError,
    SymbolConflictError,
    SymbolConflictWithNamespaceError,
    TypeAliasConflictError,
    TypeNotExistError,
    TypeNotImportedError,
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
        errors: list,
        # pyre-fixme[11]: Annotation `SpecField` is not defined as a type.
        type_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]],
        src_path: str,
        pktupl: tuple[str, ...],
    ) -> None:
        self.errors = errors
        self.type_tables = type_tables
        self.src_path = src_path
        self.using_package_metas: dict[tuple[str, ...], list[list[ast.token]]] = {}
        self.using_package_table: dict[tuple[str, ...], set[tuple[str, ...]]] = {}
        self.using_type_metas: dict[str, list[ast.token]] = {}
        self.using_type_table: dict[str, set[tuple[tuple[str, ...], str]]] = {}
        self.pktupl = pktupl

    def visit_Spec(self, node: ast.Spec) -> None:
        while node.uses:
            self.visit(node.uses.pop(0))
        for decl in node.fields:
            if isinstance(
                decl, ast.Struct | ast.Enum | ast.Runtimeclass | ast.Interface
            ):
                meta = decl.name
                name = meta.text
                self.using_type_table.setdefault(name, set()).add((self.pktupl, name))
                self.using_type_metas.setdefault(name, []).append(meta)
        for decl in node.fields:
            self.visit(decl)

    def visit_UsePackage(self, node: ast.UsePackage) -> None:
        old_pkmeta = node.old_pkname
        new_pkmeta = node.new_pkname or node.old_pkname
        old_pktupl = tuple(id.text for id in old_pkmeta)
        new_pktupl = tuple(id.text for id in new_pkmeta)
        self.using_package_metas.setdefault(new_pktupl, []).append(new_pkmeta)
        self.using_package_table.setdefault(new_pktupl, set()).add(old_pktupl)
        if old_pktupl not in self.type_tables:
            self.errors.append(PackageNotExistError(self.src_path, old_pkmeta))

    def visit_UseSymbol(self, node: ast.UseSymbol) -> None:
        pkmeta = node.pkname
        pktupl = tuple(id.text for id in pkmeta)
        type_table = self.type_tables.get(pktupl)
        if type_table is None:
            self.errors.append(PackageNotExistError(self.src_path, pkmeta))
        for alias_pair in node.alias_pairs:
            old_meta = alias_pair.old_name
            new_meta = alias_pair.new_name or alias_pair.old_name
            old_name = old_meta.text
            new_name = new_meta.text
            self.using_type_metas.setdefault(new_name, []).append(new_meta)
            self.using_type_table.setdefault(new_name, set()).add((pktupl, old_name))
            if type_table is not None and old_name not in type_table:
                self.errors.append(TypeNotExistError(self.src_path, old_meta))

    # substitution
    def visit_UserType(self, node: ast.UserType) -> None:
        real_pktupl: tuple[str, ...] = ()
        real_name: str = ""
        pkmeta = node.pkname
        meta = node.name
        if pkmeta:
            # use package
            pktupl = tuple(id.text for id in pkmeta)
            name = meta.text
            packages = self.using_package_table.get(pktupl)
            if packages is None:
                self.errors.append(PackageNotImportedError(self.src_path, pkmeta))
            elif len(packages) == 1:
                real_pktupl = next(iter(packages))
                real_name = name
                type_table = self.type_tables.get(real_pktupl)
                if type_table is not None and real_name not in type_table:
                    self.errors.append(TypeNotExistError(self.src_path, meta))
        else:
            # use symbol
            name = meta.text
            symbols = self.using_type_table.get(name)
            if symbols is None:
                self.errors.append(TypeNotImportedError(self.src_path, meta))
            elif len(symbols) == 1:
                real_pktupl, real_name = next(iter(symbols))
        node.pkname = [ast.token(id) for id in real_pktupl]
        node.name = ast.token(real_name)


def symbol_substitute(
    errors: list,
    packages: list[Package],
) -> dict[tuple[str, ...], dict[str, list[ast.SpecField]]]:
    # Generate packages dict, Check for package name conflicts
    packages_dict: dict[tuple[str, ...], list[Package]] = {}
    for package in packages:
        packages_dict.setdefault(package.tupl, []).append(package)
    for pktupl, pks in packages_dict.items():
        if len(pks) > 1:
            errors.append(PackageNameConflictError(pktupl, pks))

    # Generate namespace tree and check for relative errors
    namespaces = {}
    namespace_tree = {}
    for package in packages:
        namespace = namespace_tree
        for part in package.tupl:
            namespace = namespace.setdefault(part, {})
        namespaces.setdefault(package.tupl, namespace)
    for package in packages:
        for decl in package.spec.fields:
            if decl.name.text in namespaces[package.tupl]:
                errors.append(
                    SymbolConflictWithNamespaceError(
                        package.path, package.tupl, decl.name
                    )
                )

    # Check for declaration conflicts
    for package in packages:
        decls: dict[str, list[ast.token]] = {}
        for decl in package.spec.fields:
            meta = decl.name
            name = meta.text
            decls.setdefault(name, []).append(meta)
        for name, metas in decls.items():
            if len(metas) > 1:
                errors.append(SymbolConflictError(package.path, name, metas))

    # Generate type tables
    type_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]] = {}
    for package in packages:
        type_table = type_tables.setdefault(package.tupl, {})
        for decl in package.spec.fields:
            if isinstance(
                decl, ast.Struct | ast.Enum | ast.Runtimeclass | ast.Interface
            ):
                type_table.setdefault(decl.name.text, []).append(decl)

    # Check for using packages and symbols and perform symbol substitution
    for package in packages:
        replacer = SymbolReplacer(errors, type_tables, package.path, package.tupl)
        replacer.visit(package.spec)
        for key, vals in replacer.using_type_table.items():
            if len(vals) > 1:
                errors.append(
                    TypeAliasConflictError(
                        package.path, key, replacer.using_type_metas[key]
                    )
                )
        for key, vals in replacer.using_package_table.items():
            if len(vals) > 1:
                errors.append(
                    PackageAliasConflictError(
                        package.path, key, replacer.using_package_metas[key]
                    )
                )

    # return the symbol tables
    return type_tables


class SemanticAnalyzer(Visitor):
    def __init__(
        self,
        errors: list,
        type_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]],
        src_path: str,
    ) -> None:
        self.errors = errors
        self.type_tables = type_tables
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
            meta = parameter.name
            name = meta.text
            parameters.setdefault(name, []).append(meta)
        for name, metas in parameters.items():
            if len(metas) > 1:
                self.errors.append(SymbolConflictError(self.src_path, name, metas))
        for parameter in node.parameters:
            meta = parameter.name
            name = meta.text
            mut = parameter.param_type.mut
            type = parameter.param_type.type
            if mut is not None and not can_be_mutable(self.type_tables, type):
                # pyre-fixme[19]: Expected 2 positional arguments.
                self.errors.append(QualifierError(self.src_path, type, mut))

    def visit_Struct(self, node: ast.Struct) -> None:
        fields = {}
        for field in node.fields:
            meta = field.name
            name = meta.text
            fields.setdefault(name, []).append(meta)
        for name, metas in fields.items():
            if len(metas) > 1:
                self.errors.append(SymbolConflictError(self.src_path, name, metas))

    def visit_Enum(self, node: ast.Enum) -> None:
        fields = {}
        for field in node.fields:
            meta = field.name
            name = meta.text
            fields.setdefault(name, []).append(meta)
        for name, metas in fields.items():
            if len(metas) > 1:
                self.errors.append(SymbolConflictError(self.src_path, name, metas))
        vals = {}
        val = 0
        for field in node.fields:
            meta = field.name
            name = meta.text
            if field.expr is not None:
                val = get_int_val(field.expr)
            field.expr = ast.IntLiteralExpr(ast.token(str(val)))
            vals.setdefault(val, []).append(meta)
            val += 1
        for val, metas in vals.items():
            if len(metas) > 1:
                self.errors.append(EnumValueCollisionError(self.src_path, val, metas))


def can_be_mutable(
    type_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]],
    # pyre-fixme[11]: Annotation `Type` is not defined as a type.
    node: ast.Type,
) -> bool:
    if isinstance(node, ast.PrimitiveType):
        if node.name.text in (
            "bool",
            "f32",
            "f64",
            "i8",
            "i16",
            "i32",
            "i64",
            "u8",
            "u16",
            "u32",
            "u64",
            "String",
        ):
            return False
        raise NotImplementedError

    if isinstance(node, ast.UserType):
        pktupl = tuple(id.text for id in node.pkname)
        name = node.name.text
        targets = type_tables.get(pktupl, {}).get(name)
        if targets is None or len(targets) > 1:
            return True
        target = targets[0]
        if isinstance(target, ast.Enum):
            return False
        if isinstance(target, ast.Struct):
            return True
        if isinstance(target, ast.Runtimeclass | ast.Interface):
            return True
        raise NotImplementedError

    raise NotImplementedError


# pyre-fixme[11]: Annotation `IntExpr` is not defined as a type.
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
        return (
            get_int_val(node.then_expr)
            if get_bool_val(node.cond)
            else get_int_val(node.else_expr)
        )

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


# pyre-fixme[11]: Annotation `BoolExpr` is not defined as a type.
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
        return (
            get_bool_val(node.then_expr)
            if get_bool_val(node.cond)
            else get_bool_val(node.else_expr)
        )

    raise NotImplementedError


def check_cycle(errors: list, table) -> None:
    visited = set()
    visiting_dict = {}
    visiting_list = []

    def visit(parent):
        if parent in visited:
            return
        idx = len(visiting_list)
        rec = visiting_dict.setdefault(parent, idx)
        if idx != rec:
            errors.append(RecursiveInclusionError(parent, visiting_list[rec:]))
            return
        for name, child in table[parent]:
            visiting_list.append((name, child))
            visit(child)
            visiting_list.pop()
        visited.add(parent)

    for parent in table:
        visit(parent)


def semantic_check(
    errors: list,
    packages: list[Package],
    type_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]],
) -> None:
    # Semantic checking within each file
    for package in packages:
        analyzer = SemanticAnalyzer(errors, type_tables, package.path)
        analyzer.visit(package.spec)

    # Check for circular reference in structs
    struct_table = {}
    for pktupl, type_table in type_tables.items():
        for name, decls in type_table.items():
            if len(decls) > 1:
                continue
            decl = decls[0]
            if not isinstance(decl, ast.Struct):
                continue
            children = struct_table.setdefault((pktupl, name), [])
            for child in decl.fields:
                child_name = child.name.text
                child_type = child.type
                if not isinstance(child_type, ast.UserType):
                    continue
                child_type_pktupl = tuple(id.text for id in child_type.pkname)
                child_type_name = child_type.name.text
                child_type_decls = type_tables.get(child_type_pktupl, {}).get(
                    child_type_name
                )
                if child_type_decls is None or len(child_type_decls) > 1:
                    continue
                child_type_decl = child_type_decls[0]
                if not isinstance(child_type_decl, ast.Struct):
                    continue
                children.append((child_name, (child_type_pktupl, child_type_name)))
    check_cycle(errors, struct_table)
