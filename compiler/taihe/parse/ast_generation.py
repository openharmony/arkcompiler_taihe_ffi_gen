from typing import Any

from antlr4 import CommonTokenStream, FileStream, InputStream, Token
from antlr4.error.ErrorListener import ErrorListener

from taihe.parse.antlr.TaiheAST import TaiheAST
from taihe.parse.antlr.TaiheLexer import TaiheLexer
from taihe.parse.antlr.TaiheParser import TaiheParser
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import IDLSyntaxError
from taihe.utils.sources import SourceBase, SourceBuffer, SourceFile, SourceLocation


class TaiheErrorListener(ErrorListener):
    def __init__(self, source: SourceBase, diag: DiagnosticsManager) -> None:
        super().__init__()
        self.diag = diag
        self.source = source
        self.has_error = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.diag.emit(
            IDLSyntaxError(
                offendingSymbol.text,
                loc=SourceLocation(
                    self.source, line, column + 1, len(offendingSymbol.text)
                ),
            )
        )
        self.has_error = True


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


def generate_ast(source: SourceBase, diag: DiagnosticsManager) -> TaiheAST.Spec:
    error_listener = TaiheErrorListener(source, diag)

    if isinstance(source, SourceBuffer):
        input_stream = InputStream(source.buf)
    elif isinstance(source, SourceFile):
        input_stream = FileStream(source.source_identifier)
    else:
        raise NotImplementedError

    lexer = TaiheLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    token_stream = CommonTokenStream(lexer)

    parser = TaiheParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    tree = parser.spec()

    if error_listener.has_error:
        return TaiheAST.Spec([], [])
    return visit(tree)
