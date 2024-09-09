from antlr4 import *
from TaiheLexer import TaiheLexer
from TaiheParser import TaiheParser
from TaiheAST import TaiheAST


def visit(ctx):
        if isinstance(ctx, list):
            return [visit(node) for node in ctx]
        if ctx is None:
            return None
        if isinstance(ctx, Token):
            return ctx
        ast_class_name = ctx.__class__.__name__[:-7]
        if ast_class_name.endswith('Uni'):
            return visit(ctx.getChild(0))
        kwargs = {}
        for attr_full_name, attr_ctx in ctx.__dict__.items():
            if attr_full_name[0].isupper() or attr_full_name.startswith('token'):
                attr_type_name, attr_name = attr_full_name.split('_', 1)
                kwargs[attr_name] = visit(attr_ctx)
        return getattr(TaiheAST, ast_class_name)(**kwargs)


def ast_generation(input_stream) -> TaiheAST.Specification:
    lexer = TaiheLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = TaiheParser(token_stream)
    tree = parser.specification()
    return visit(tree)


if __name__ == '__main__':
    print(ast_generation(StdinStream()))
