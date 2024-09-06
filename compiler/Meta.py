from TaiheParser import TaiheParser
namespace = 'TaiheAST'
def get_attr_type(attr_type_name):
    if attr_type_name.endswith('Lst'):
        return f"List['{namespace}.{attr_type_name[:-3]}']"
    if attr_type_name.endswith('Opt'):
        return f"Optional['{namespace}.{attr_type_name[:-3]}']"
    return f"Type['{namespace}.{attr_type_name}']"
def get_attr_pairs(ctx):
    for attr_full_name, attr_ctx in ctx.__dict__.items():
        if attr_full_name[0].isupper() or attr_full_name.startswith('token'):
            attr_type_name, attr_name = attr_full_name.split('_', 1)
            attr_type = get_attr_type(attr_type_name)
            yield attr_type, attr_name
file = open('TaiheAST.py', 'w')
file.write(f'from typing import Type, List, Optional, NamedTuple, Union\n')
file.write(f'from antlr4 import Token, ParserRuleContext\n')
file.write(f'class {namespace}:\n')
file.write(f'    token = Token\n')
for rule_name in TaiheParser.ruleNames:
    ast_class_name = rule_name[0].upper() + rule_name[1:]
    ctx = getattr(TaiheParser, ast_class_name + 'Context')(None)
    if rule_name.endswith('Uni'):
        file.write(f'    {ast_class_name} = Union[\n')
        for attr_type, attr_name in get_attr_pairs(ctx):
            file.write(f'        {attr_type},\n')
        file.write(f'    ]\n')
    else:
        file.write(f'    class {ast_class_name}(NamedTuple):\n')
        file.write(f'        ctx: ParserRuleContext\n')
        for attr_type, attr_name in get_attr_pairs(ctx):
            file.write(f'        {attr_name}: {attr_type}\n')
