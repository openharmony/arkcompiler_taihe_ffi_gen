from collections.abc import Iterable

from typing_extensions import override

from taihe.parse import Visitor, ast
from taihe.parse.ast_generation import generate_ast
from taihe.semantics.declarations import (
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
    TypeAliasDecl,
    TypeRefDecl,
)
from taihe.semantics.types import (
    BuiltinType,
)
from taihe.utils.diagnostics import AbstractDiagnosticsManager
from taihe.utils.sources import SourceBase, SourceLocation


def pkg2str(pkg_name: ast.PkgName) -> str:
    if pkg_name:
        return ".".join(t.text for t in pkg_name.parts)
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
    diag: AbstractDiagnosticsManager

    def __init__(self, source: SourceBase, diag: AbstractDiagnosticsManager):
        self.source = source
        self.diag = diag

    def loc(self, t: ast.any):
        # Remember, token.column is 0-based.
        return SourceLocation(self.source, *t._beg, *t._end)

    @override
    def visit_PrimitiveType(self, node: ast.PrimitiveType) -> TypeRefDecl:
        name = str(node.name)
        loc = self.loc(node.name)
        ty = BuiltinType.lookup(name)
        assert ty
        return TypeRefDecl(name, loc, ty)

    @override
    def visit_UserType(self, node: ast.UserType) -> TypeRefDecl:
        if node.pkg_name:
            loc = self.loc(node)
            name = pkg2str(node.pkg_name) + "." + str(node.decl_name)
        else:
            loc = self.loc(node.decl_name)
            name = str(node.decl_name)
        return TypeRefDecl(name, loc)

    @override
    def visit_Struct(self, node: ast.Struct) -> StructDecl:
        d = StructDecl(str(node.name), loc=self.loc(node.name))
        for f in node.fields:
            with self.diag.capture_error():
                d.add_field(str(f.name), self.loc(f.name), self.visit(f.ty))
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
                f.add_param(str(p.name), self.loc(p.name), self.visit(p.ty))
        for r in node.retvals:
            with self.diag.capture_error():
                f.add_retval(self.visit(r.ty))
        return f

    @override
    def visit_Interface(self, node: ast.Interface) -> IfaceDecl:
        d = IfaceDecl(str(node.name), loc=self.loc(node.name))
        for f in node.fields:
            m = self.visit(f)
            with self.diag.capture_error():
                d.add_method(m)
        for i in node.extends:
            with self.diag.capture_error():
                d.add_parent(self.visit(i.ty))
        return d

    @override
    def visit_TypeAlias(self, node: ast.TypeAlias) -> TypeAliasDecl:
        return TypeAliasDecl(str(node.name), self.loc(node.name), self.visit(node.ty))

    @override
    def visit_Function(self, node: ast.Function) -> FuncDecl:
        f = FuncDecl(str(node.name), loc=self.loc(node.name))
        for p in node.parameters:
            with self.diag.capture_error():
                f.add_param(str(p.name), self.loc(p.name), self.visit(p.ty))
        for r in node.retvals:
            with self.diag.capture_error():
                f.add_retval(self.visit(r.ty))
        return f

    @override
    def visit_UsePackage(self, node: ast.UsePackage) -> Iterable[PackageImportDecl]:
        pkg = PackageRefDecl(pkg2str(node.pkg_name), self.loc(node.pkg_name))
        if node.pkg_alias:
            yield PackageImportDecl(
                pkg,
                name=str(node.pkg_alias),
                loc=self.loc(node.pkg_alias),
            )
        else:
            yield PackageImportDecl(
                pkg,
            )

    @override
    def visit_UseSymbol(self, node: ast.UseSymbol) -> Iterable[DeclarationImportDecl]:
        pkg = PackageRefDecl(pkg2str(node.pkg_name), self.loc(node.pkg_name))
        for p in node.decl_alias_pairs:
            decl = DeclarationRefDecl(str(p.decl_name), self.loc(p.decl_name), pkg)
            if p.decl_alias:
                yield DeclarationImportDecl(
                    decl,
                    name=str(p.decl_alias),
                    loc=self.loc(p.decl_alias),
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

            with self.diag.capture_error():
                pkg.add_declaration(d)

        return pkg

    def convert(self) -> Package:
        """Converts the whole source code buffer to a package."""
        ast = generate_ast(self.source, self.diag)

        return self.visit_Spec(ast)
