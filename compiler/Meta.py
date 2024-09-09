from TaiheParser import TaiheParser


def get_attr_type(attr_type_name):
    if attr_type_name.endswith('Lst'):
        return f"List['TaiheAST.{attr_type_name[:-3]}']"
    if attr_type_name.endswith('Opt'):
        return f"Optional['TaiheAST.{attr_type_name[:-3]}']"
    return f"Type['TaiheAST.{attr_type_name}']"


def get_attr_pairs(ctx):
    for attr_full_name, attr_ctx in ctx.__dict__.items():
        if attr_full_name[0].isupper() or attr_full_name.startswith('token'):
            attr_type_name, attr_name = attr_full_name.split('_', 1)
            attr_type = get_attr_type(attr_type_name)
            yield attr_type, attr_name


def gen_ast_code():
    ast = []
    ast.append(f'from dataclasses import dataclass\n')
    ast.append(f'from typing import Type, List, Optional, Union\n')
    ast.append(f'from antlr4 import Token\n')
    ast.append(f'class TaiheAST:\n')
    ast.append(f'    token = Token\n')
    for rule_name in TaiheParser.ruleNames:
        ast_class_name = rule_name[0].upper() + rule_name[1:]
        ctx = getattr(TaiheParser, ast_class_name + 'Context')(None)
        if rule_name.endswith('Uni'):
            ast.append(f'    {ast_class_name} = Union[\n')
            for attr_type, attr_name in get_attr_pairs(ctx):
                ast.append(f'        {attr_type},\n')
            ast.append(f'    ]\n')
        else:
            ast.append(f'    @dataclass\n')
            ast.append(f'    class {ast_class_name}:\n')
            for attr_type, attr_name in get_attr_pairs(ctx):
                ast.append(f'        {attr_name}: {attr_type}\n')
    with open(f'TaiheAST.py', 'w') as file:
        file.writelines(ast)


def gen_visitor_code():
    visitor = []
    visitor.append(f'from TaiheAST import TaiheAST\n')
    visitor.append(f'class TaiheVisitor:\n')
    visitor.append(f'    def visit(self, node):\n')
    visitor.append(f"        return getattr(self, 'visit_' + node.__class__.__name__)(node)\n")
    visitor.append(f'    def visit_token(self, node):\n')
    visitor.append(f"        raise NotImplementedError\n")
    for rule_name in TaiheParser.ruleNames:
        ast_class_name = rule_name[0].upper() + rule_name[1:]
        if rule_name.endswith('Uni'):
            continue
        visitor.append(f'    def visit_{ast_class_name}(self, node: TaiheAST.{ast_class_name}):\n')
        visitor.append(f'        raise NotImplementedError\n')
    with open(f'TaiheVisitor.py', 'w') as file:
        file.writelines(visitor)


if __name__ == '__main__':
    gen_ast_code()
    gen_visitor_code()
