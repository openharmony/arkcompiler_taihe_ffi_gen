from antlr4 import *
from TaiheLexer import TaiheLexer
from TaiheParser import TaiheParser
from TaiheVisitor import TaiheVisitor
from Taihe import Taihe
class ASTGenerator(TaiheVisitor):
    def visitChildren(self, ctx):
        ctxName = ctx.__class__.__name__
        ruleName = ctxName[:-7]
        if ruleName.endswith('Opt'):
            return self.visit(ctx.getChild(0))
        kwargs = {'metainfo': ctx}
        for ctxAttrFullName, ctxAttrVal in ctx.__dict__.items():
            if ctxAttrFullName[0].isupper():
                ctxAttrType, ctxAttrName = ctxAttrFullName.split('_')
                def visit(val):
                    if ctxAttrType == 'Str':
                        return Taihe.Str(metainfo = val, data = val.text)
                    if ctxAttrType == 'Bool':
                        return Taihe.Bool(metainfo = val, data = val is not None)
                    return self.visit(val)
                kwargs[ctxAttrName] = [visit(val) for val in ctxAttrVal] if isinstance(ctxAttrVal, list) else visit(ctxAttrVal)
        return getattr(Taihe, ruleName)(**kwargs)
def ASTGenerate(inputStream) -> Taihe.Specification:
    lexer = TaiheLexer(inputStream)
    tokenStream = CommonTokenStream(lexer)
    parser = TaiheParser(tokenStream)
    tree = parser.specification()
    generator = ASTGenerator()
    return generator.visit(tree)
def main():
    ast = ASTGenerate(StdinStream())
    nameTable = [(field.name.data, field) for field in ast.fields]
    print(nameTable)
if __name__ == '__main__':
    main()
