from collections.abc import Iterable

from typing_extensions import override

from taihe.parse import Visitor, ast
from taihe.parse.ast_generation import generate_ast
from taihe.semantics.declarations import (
    Decl,
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    FuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    ImportDecl,
    Package,
    PackageImportDecl,
    PackageRefDecl,
    StructDecl,
    TypeRefDecl,
)
from taihe.semantics.types import (
    BuiltinType,
    TypeQualifier,
)
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.sources import SourceBase, SourceLocation


def pkg2str(pkg_name: list[ast.token] | None) -> str:
    if pkg_name:
        return ".".join(t.text for t in pkg_name)
    else:
        return ""


def eval_bool_expr(node: ast.BoolExpr) -> bool:
    if isinstance(node, ast.IntComparisonExpr):
        return {
            ">": int.__gt__,
            "<": int.__lt__,
            ">=": int.__ge__,
            "<=": int.__le__,
            "==": int.__eq__,
            "!=": int.__ne__,
        }[node.op.text](
            eval_int_expr(node.left),
            eval_int_expr(node.right),
        )

    if isinstance(node, ast.BoolUnaryExpr):
        assert node.op.text == "!"
        return not eval_bool_expr(node.expr)

    if isinstance(node, ast.BoolBinaryExpr):
        return {
            "&&": bool.__and__,
            "||": bool.__or__,
        }[node.op.text](
            eval_bool_expr(node.left),
            eval_bool_expr(node.right),
        )

    if isinstance(node, ast.BoolParenthesisExpr):
        return eval_bool_expr(node.expr)

    if isinstance(node, ast.BoolConditionalExpr):
        return (
            eval_bool_expr(node.then_expr)
            if eval_bool_expr(node.cond)
            else eval_bool_expr(node.else_expr)
        )


def eval_int_expr(node: ast.IntExpr) -> int:
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
        return eval_int_expr(node.expr)

    if isinstance(node, ast.IntConditionalExpr):
        return (
            eval_int_expr(node.then_expr)
            if eval_bool_expr(node.cond)
            else eval_int_expr(node.else_expr)
        )

    if isinstance(node, ast.IntUnaryExpr):
        return {
            "-": int.__neg__,
            "+": int.__pos__,
            "~": int.__invert__,
        }[node.op.text](
            eval_int_expr(node.expr),
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
            eval_int_expr(node.left),
            eval_int_expr(node.right),
        )


class AstConverter(Visitor):
    """Converts a node on AST to the intermetiade representation.

    Note that declerations with errors are discarded.
    """

    source: SourceBase
    diag: DiagnosticsManager

    def __init__(self, source: SourceBase, diag: DiagnosticsManager):
        super().__init__()
        self.source = source
        self.diag = diag

    def visit(self, node):
        r = super().visit(node)
        return r

    def loc(self, t: ast.token | list[ast.token]):
        # Remember, token.column is 0-based.
        if isinstance(t, ast.token):
            col = 0 if t.column is None else t.column + 1
            return SourceLocation(self.source, t.line or 0, col, len(t.text))

        first_begin = 0 if t[0].column is None else t[0].column + 1
        last_begin = 0 if t[-1].column is None else t[-1].column + 1
        span = max(last_begin + len(t[-1].text) - first_begin, 0)
        return SourceLocation(self.source, t[0].line or 0, first_begin, span)

    @override
    def visit_PrimitiveType(self, node: ast.PrimitiveType) -> TypeRefDecl:
        name = str(node.name)
        loc = self.loc(node.name)
        ty = BuiltinType.lookup(name)
        assert ty
        return TypeRefDecl(name, loc, ty)

    @override
    def visit_UserType(self, node: ast.UserType) -> TypeRefDecl:
        full_name = [*node.pkname, node.name]
        name = pkg2str(full_name)
        loc = self.loc(full_name)
        return TypeRefDecl(name, loc)

    @override
    def visit_QualifiedType(self, node: ast.QualifiedType) -> TypeRefDecl:
        ty = self.visit(node.type)
        assert isinstance(ty, TypeRefDecl)
        if node.mut:
            ty.qual |= TypeQualifier.MUT
        return ty

    @override
    def visit_Struct(self, node: ast.Struct) -> StructDecl:
        d = StructDecl(str(node.name), loc=self.loc(node.name))
        for f in node.fields:
            with self.diag.capture_error():
                d.add_field(str(f.name), self.loc(f.name), self.visit(f.type))
        return d

    @override
    def visit_Enum(self, node: ast.Enum) -> EnumDecl:
        d = EnumDecl(str(node.name), loc=self.loc(node.name))
        next_value = 0
        for f in node.fields:
            with self.diag.capture_error():
                value = eval_int_expr(f.expr) if f.expr else next_value
                d.add_item(str(f.name), self.loc(f.name), value)
                next_value = value + 1
        return d

    @override
    def visit_InterfaceFunction(self, node: ast.InterfaceFunction) -> IfaceMethodDecl:
        f = IfaceMethodDecl(str(node.name), loc=self.loc(node.name))
        for p in node.parameters:
            with self.diag.capture_error():
                f.add_param(str(p.name), self.loc(p.name), self.visit(p.param_type))
        for r in node.return_types:
            with self.diag.capture_error():
                f.add_return_ty(self.visit(r))
        return f

    @override
    def visit_Interface(self, node: ast.Interface) -> IfaceDecl:
        d = IfaceDecl(str(node.name), loc=self.loc(node.name))
        for f in node.fields:
            m = self.visit(f)
            with self.diag.capture_error():
                d.add_function(m)
        for i in node.extends:
            with self.diag.capture_error():
                d.add_parent(self.visit(i))
        return d

    @override
    def visit_Function(self, node: ast.Function) -> FuncDecl:
        f = FuncDecl(str(node.name), loc=self.loc(node.name))
        for p in node.parameters:
            with self.diag.capture_error():
                f.add_param(str(p.name), self.loc(p.name), self.visit(p.param_type))
        for r in node.return_types:
            with self.diag.capture_error():
                f.add_return_ty(self.visit(r))
        return f

    @override
    def visit_UsePackage(self, node: ast.UsePackage) -> Iterable[PackageImportDecl]:
        pkg = PackageRefDecl(pkg2str(node.old_pkname), self.loc(node.old_pkname))
        if node.new_pkname:
            yield PackageImportDecl(
                pkg,
                name=pkg2str(node.new_pkname),
                loc=self.loc(node.new_pkname),
            )
        else:
            yield PackageImportDecl(
                pkg,
            )

    @override
    def visit_UseSymbol(self, node: ast.UseSymbol) -> Iterable[DeclarationImportDecl]:
        pkg = PackageRefDecl(pkg2str(node.pkname), self.loc(node.pkname))
        for p in node.alias_pairs:
            decl = DeclarationRefDecl(str(p.old_name), self.loc(p.old_name), pkg)
            if p.new_name:
                yield DeclarationImportDecl(
                    decl,
                    name=str(p.new_name),
                    loc=self.loc(p.new_name),
                )
            else:
                yield DeclarationImportDecl(
                    decl,
                )

    @override
    def visit_Spec(self, node: ast.Spec) -> Package:
        pkg = Package(self.source.pkg_name, SourceLocation(self.source))
        for u in node.uses:
            for i in self.visit(u):
                assert isinstance(i, ImportDecl)
                with self.diag.capture_error():
                    pkg.add_import(i)

        for n in node.fields:
            d = self.visit(n)
            if d is None:
                # TODO handle all node types.
                print(f"visit_Spec: Ignoring {n.__class__.__qualname__}")
                continue

            assert isinstance(d, Decl)
            with self.diag.capture_error():
                pkg.add_declaration(d)

        return pkg

    def convert(self) -> Package:
        """Converts the whole source code buffer to a package."""
        ast = generate_ast(self.source, self.diag)

        return self.visit_Spec(ast)
