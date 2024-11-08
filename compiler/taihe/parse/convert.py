from collections.abc import Iterable
from typing import Optional, Union

from typing_extensions import override

from taihe.parse import Visitor, ast
from taihe.semantics.declarations import (
    Decl,
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    EnumItemDecl,
    FuncDecl,
    ImportDecl,
    Package,
    PackageImportDecl,
    PackageRefDecl,
    ParamDecl,
    StructDecl,
    StructFieldDecl,
    TypeRefDecl,
)
from taihe.semantics.types import (
    BuiltinType,
    QualifiedType,
    TypeQualifier,
)
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import (
    DeclRedefDiagError,
    EnumValueCollisionError,
    TypeNotExistError,
)
from taihe.utils.sources import SourceBase, SourceBuffer, SourceFile, SourceLocation


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


def check_DeclRefDiagError(
    diag: DiagnosticsManager,
    items: Union[list[ParamDecl], list[EnumItemDecl], list[StructFieldDecl]],
):
    symbol = {}
    for f in items:
        if prev := symbol.get(f.name, None):
            diag.emit(DeclRedefDiagError(prev, f))
        else:
            symbol[f.name] = f


def check_EnumValueCollisionError(diag: DiagnosticsManager, items: list[EnumItemDecl]):
    symbol = {}
    for f in items:
        if prev := symbol.get(f.value, None):
            diag.emit(EnumValueCollisionError(prev, f, f.value))
        else:
            symbol[f.value] = f


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
        # print(f"{r=} {node=}")
        return r

    def loc(self, t: ast.token | list[ast.token]):
        # Remember, token.column is 0-based.
        if isinstance(t, ast.token):
            col = 0 if t.column is None else t.column + 1
            return SourceLocation(self.source, t.line or 0, col, span=len(t.text))

        first_begin = 0 if t[0].column is None else t[0].column + 1
        last_begin = 0 if t[-1].column is None else t[-1].column + 1
        span = max(last_begin + len(t[-1].text) - first_begin, 0)
        return SourceLocation(self.source, t[0].line or 0, first_begin, span=span)

    @override
    def visit_PrimitiveType(self, node: ast.PrimitiveType) -> TypeRefDecl:
        name = str(node.name)
        loc = self.loc(node.name)
        ty = BuiltinType.lookup(name)
        if ty is None:
            self.diag.emit(TypeNotExistError(name, loc=loc))
        return TypeRefDecl(name, ty, loc=loc)

    @override
    def visit_UserType(self, node: ast.UserType) -> TypeRefDecl:
        full_name = [*node.pkname, node.name]
        name = pkg2str(full_name)
        loc = self.loc(full_name)
        return TypeRefDecl(name, loc=loc)

    @override
    def visit_Struct(self, node: ast.Struct) -> Optional[StructDecl]:
        d = StructDecl(str(node.name), loc=self.loc(node.name))
        no_error = self.diag.for_each(
            node.fields,
            lambda f: d.add_field(
                str(f.name), self.visit(f.type), loc=self.loc(f.name)
            ),
        )
        check_DeclRefDiagError(self.diag, d.fields)
        if no_error:
            return d

    @override
    def visit_Enum(self, node: ast.Enum) -> Optional[EnumDecl]:
        decl = EnumDecl(str(node.name), loc=self.loc(node.name))
        next_value = 0
        for node_item in node.fields:
            if node_item.expr:
                v = eval_int_expr(node_item.expr)
                next_value = v + 1
            else:
                v = next_value
                next_value += 1
            decl.add_item(str(node_item.name), v, loc=self.loc(node_item.name))
        check_DeclRefDiagError(self.diag, decl.items)
        check_EnumValueCollisionError(self.diag, decl.items)
        return decl

    @override
    def visit_QualifiedType(self, node: ast.QualifiedType) -> QualifiedType:
        qual = TypeQualifier.NONE
        if node.mut:
            qual |= TypeQualifier.MUT

        ty = self.visit(node.type)
        assert isinstance(ty, TypeRefDecl)
        return QualifiedType(ty, qual)

    @override
    def visit_Function(self, node: ast.Function) -> Optional[FuncDecl]:
        f = FuncDecl(str(node.name), loc=self.loc(node.name))
        no_error = self.diag.for_each(
            node.parameters,
            lambda p: f.add_param(
                str(p.name), self.visit(p.param_type), loc=self.loc(p.name)
            ),
        )
        check_DeclRefDiagError(self.diag, f.params)
        if no_error:
            return f

    @override
    def visit_UsePackage(self, node: ast.UsePackage) -> Iterable[PackageImportDecl]:
        pkg = PackageRefDecl(pkg2str(node.old_pkname), self.loc(node.old_pkname))
        if node.new_pkname:
            yield PackageImportDecl(
                pkg=pkg,
                name=pkg2str(node.new_pkname),
                loc=self.loc(node.new_pkname),
            )
        else:
            yield PackageImportDecl(
                pkg=pkg,
            )

    @override
    def visit_UseSymbol(self, node: ast.UseSymbol) -> Iterable[DeclarationImportDecl]:
        pkg = PackageRefDecl(pkg2str(node.pkname), self.loc(node.pkname))
        for p in node.alias_pairs:
            decl = DeclarationRefDecl(str(p.old_name), self.loc(p.old_name))
            if p.new_name:
                yield DeclarationImportDecl(
                    pkg=pkg,
                    decl=decl,
                    name=str(p.new_name),
                    loc=self.loc(p.new_name),
                )
            else:
                yield DeclarationImportDecl(
                    pkg=pkg,
                    decl=decl,
                )

    @override
    def visit_Spec(self, node: ast.Spec) -> Package:
        pkg = Package(self.source.pkg_name)
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
        from antlr4 import FileStream, InputStream

        from taihe.parse.ast_generation import generate_ast

        if isinstance(self.source, SourceBuffer):
            stream = InputStream(self.source.buf)
        elif isinstance(self.source, SourceFile):
            stream = FileStream(self.source.source_identifier)
        else:
            raise NotImplementedError

        ast = generate_ast(stream)
        return self.visit_Spec(ast)
