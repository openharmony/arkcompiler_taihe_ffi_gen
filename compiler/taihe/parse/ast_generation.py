from contextlib import suppress
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


def issubkind(real_kind, node_kind):
    ctx_kind = node_kind + "Context"
    ctx_type = getattr(TaiheParser, ctx_kind)
    sub_kind = real_kind + "Context"
    sub_type = getattr(TaiheParser, sub_kind)
    subclasses = ctx_type.__subclasses__()
    if subclasses:
        return sub_type in subclasses
    else:
        return real_kind == node_kind


def visit(node_kind: str, ctx) -> Any:
    if node_kind.endswith("Lst"):
        node = []
        for sub in ctx:
            with suppress(Exception):
                node.append(visit(node_kind[:-3], sub))
        return node
    if node_kind.endswith("Opt"):
        node = None
        if ctx is not None:
            with suppress(Exception):
                node = visit(node_kind[:-3], ctx)
        return node
    line, column = get_meta(ctx)
    if node_kind == "token":
        return TaiheAST.token(text=ctx.text, line=line, column=column)
    kwargs = {"line": line, "column": column}
    for attr_full_name, attr_ctx in ctx.__dict__.items():
        if attr_full_name[0].isupper() or attr_full_name.startswith("token"):
            attr_kind_name, attr_name = attr_full_name.split("_", 1)
            kwargs[attr_name] = visit(attr_kind_name, attr_ctx)
    real_kind = ctx.__class__.__name__[:-7]
    assert issubkind(real_kind, node_kind)
    return getattr(TaiheAST, real_kind)(**kwargs)


def generate_ast(source: SourceBase, diag: DiagnosticsManager) -> TaiheAST.Spec:
    if isinstance(source, SourceBuffer):
        input_stream = InputStream(source.buf)
    elif isinstance(source, SourceFile):
        input_stream = FileStream(source.source_identifier)
    else:
        raise NotImplementedError

    lexer = TaiheLexer(input_stream)
    token_stream = CommonTokenStream(lexer)

    error_listener = TaiheErrorListener(source, diag)

    parser = TaiheParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    tree = parser.spec()

    return visit("Spec", tree)
