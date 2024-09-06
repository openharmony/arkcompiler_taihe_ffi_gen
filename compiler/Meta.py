from TaiheParser import TaiheParser
namespace = 'TaiheAST'
file = open('TaiheAST.py', 'w')
file.write(f"from typing import List, Union, NamedTuple, Optional\n")
file.write(f"from antlr4 import Token, ParserRuleContext\n")
file.write(f"class {namespace}:\n")
file.write(f"    token = Optional[Token]\n")
for ruleName in TaiheParser.ruleNames:
    ctxName = ruleName[0].upper() + ruleName[1:]
    ctxType = getattr(TaiheParser, ctxName + 'Context')
    ctx = ctxType(None)
    if ruleName.endswith('Opt'):
        file.write(f"    {ctxName} = Union[\n")
        for ctxAttrType in ctx.__dict__:
            if ctxAttrType[0].isupper() or ctxAttrType == 'token':
                if ctxAttrVal is None:
                    file.write(f"        '{namespace}.{ctxAttrType}',\n")
                else:
                    file.write(f"        List['{namespace}.{ctxAttrType}'],\n")
        file.write(f"    ]\n")
    else:
        file.write(f"    class {ctxName}(NamedTuple):\n")
        file.write(f"        metainfo: ParserRuleContext\n")
        for ctxAttrFullName, ctxAttrVal in ctx.__dict__.items():
            if ctxAttrFullName[0].isupper() or ctxAttrFullName.startswith('token'):
                ctxAttrType, ctxAttrName = ctxAttrFullName.split('_')
                if ctxAttrVal is None:
                    file.write(f"        {ctxAttrName}: '{namespace}.{ctxAttrType}'\n")
                else:
                    file.write(f"        {ctxAttrName}: List['{namespace}.{ctxAttrType}']\n")
