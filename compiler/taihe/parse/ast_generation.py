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


def visit(ctx):
    if isinstance(ctx, list):
        return [visit(node) for node in ctx]
    if ctx is None:
        return None
    if isinstance(ctx, Token):
        return TaiheAST.token(text=ctx.text, line=ctx.line, column=ctx.column)
    ast_class_name = ctx.__class__.__name__[:-7]
    if ast_class_name.endswith("Uni"):
        return visit(ctx.getChild(0))
    kwargs = {}
    for attr_full_name, attr_ctx in ctx.__dict__.items():
        if attr_full_name[0].isupper() or attr_full_name.startswith("token"):
            attr_type_name, attr_name = attr_full_name.split("_", 1)
            kwargs[attr_name] = visit(attr_ctx)
    return getattr(TaiheAST, ast_class_name)(**kwargs)


def generate_ast(input_stream) -> TaiheAST.Specification:
    lexer = TaiheLexer(input_stream)
    lexer.addErrorListener(TaiheErrorListener())
    token_stream = CommonTokenStream(lexer)
    parser = TaiheParser(token_stream)
    parser.addErrorListener(TaiheErrorListener())
    tree = parser.specification()
    return visit(tree)


if __name__ == "__main__":
    print(generate_ast(StdinStream()))
