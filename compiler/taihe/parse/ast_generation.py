from typing import Any

from antlr4 import CommonTokenStream, StdinStream, Token
from antlr4.error.ErrorListener import ErrorListener

from taihe.parse.antlr.TaiheAST import TaiheAST
from taihe.parse.antlr.TaiheLexer import TaiheLexer
from taihe.parse.antlr.TaiheParser import TaiheParser


class TaiheErrorListener(ErrorListener):
    def __init__(self) -> None:
        super().__init__()

    def syntaxError(self, *args, **kwargs):
        raise SyntaxError

    def reportAmbiguity(self, *args, **kwargs):
        raise SyntaxError

    def reportAttemptingFullContext(self, *args, **kwargs):
        raise SyntaxError

    def reportContextSensitivity(self, *args, **kwargs):
        raise SyntaxError


def get_meta(ctx) -> tuple[int, int]:
    if isinstance(ctx, Token):
        return ctx.line, ctx.column
    return 0, 0


def visit(ctx) -> Any:
    if isinstance(ctx, list):
        return [visit(node) for node in ctx]
    if ctx is None:
        return None
    line, column = get_meta(ctx)
    if isinstance(ctx, Token):
        return TaiheAST.token(text=ctx.text, line=line, column=column)
    kwargs = {"line": line, "column": column}
    for attr_full_name, attr_ctx in ctx.__dict__.items():
        if attr_full_name[0].isupper() or attr_full_name.startswith("token"):
            attr_type_name, attr_name = attr_full_name.split("_", 1)
            kwargs[attr_name] = visit(attr_ctx)
    ast_class_name = ctx.__class__.__name__[:-7]
    return getattr(TaiheAST, ast_class_name)(**kwargs)


def generate_ast(input_stream) -> TaiheAST.Spec:
    lexer = TaiheLexer(input_stream)
    lexer.addErrorListener(TaiheErrorListener())
    token_stream = CommonTokenStream(lexer)
    parser = TaiheParser(token_stream)
    parser.addErrorListener(TaiheErrorListener())
    tree = parser.spec()
    return visit(tree)


if __name__ == "__main__":
    print(generate_ast(StdinStream()))
