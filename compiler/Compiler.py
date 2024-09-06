from antlr4 import *
from TaiheLexer import TaiheLexer
from TaiheParser import TaiheParser
from TaiheAST import TaiheAST
def visit(tree):
        if isinstance(tree, list):
            return [visit(node) for node in tree]
        if tree is None:
            return None
        if isinstance(tree, Token):
            return tree
        ctxName = tree.__class__.__name__[:-7]
        if ctxName.endswith('Opt'):
            return visit(tree.getChild(0))
        kwargs = {'metainfo': tree}
        for ctxAttrFullName, ctxAttrVal in tree.__dict__.items():
            if ctxAttrFullName[0].isupper() or ctxAttrFullName.startswith('token'):
                ctxAttrType, ctxAttrName = ctxAttrFullName.split('_')
                kwargs[ctxAttrName] = visit(ctxAttrVal)
        return getattr(TaiheAST, ctxName)(**kwargs)
def generateAST(inputStream) -> TaiheAST.Specification:
    lexer = TaiheLexer(inputStream)
    tokenStream = CommonTokenStream(lexer)
    parser = TaiheParser(tokenStream)
    tree = parser.specification()
    return visit(tree)
def main():
    ast = generateAST(StdinStream())
    nameTable = [(field.name.text, field) for field in ast.fields]
    print(nameTable)
if __name__ == '__main__':
    main()
