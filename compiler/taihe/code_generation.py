from os import path
from typing import Any

from taihe.parse import Visitor, ast


class CodeGenerator(Visitor):
    def __init__(self, pktupl: tuple[str, ...], dst_dir: str, author: bool, user: bool):
        self.pktupl = pktupl
        self.dst_dir = dst_dir
        self.author = author
        self.user = user

    def generic_visit(self, node):
        raise NotImplementedError

    def visit_BasicType(self, node: ast.BasicType):
        if node.name.text == "i8":
            return "int8_t"
        if node.name.text == "i16":
            return "int16_t"
        if node.name.text == "i32":
            return "int32_t"
        if node.name.text == "i64":
            return "int64_t"
        if node.name.text == "u8":
            return "uint8_t"
        if node.name.text == "u16":
            return "uint16_t"
        if node.name.text == "u32":
            return "uint32_t"
        if node.name.text == "u64":
            return "uint64_t"
        if node.name.text == "f32":
            return "float"
        if node.name.text == "f64":
            return "double"
        if node.name.text == "bool":
            return "bool"
        raise NotImplementedError

    def visit_TypeWithSpecifier(self, node: ast.TypeWithSpecifier):
        text = self.visit(node.type)
        if node.const:
            text += " const"
        text += " "
        if node.ref:
            text += "&"
        return text

    def visit_Parameter(self, node: ast.Parameter):
        return self.visit(node.type_with_specifier) + node.name.text

    def visit_Specification(self, node: ast.Specification):
        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"

        namespace = "::".join(self.pktupl)

        if self.author or self.user:
            with open(path.join(self.dst_dir, abi_h_name), "w") as abi_h:
                abi_h.write("#pragma once\n")
                abi_h.write('#include "taihe/common.h"\n')

        if self.user:
            with open(path.join(self.dst_dir, abi_hpp_name), "w") as abi_hpp:
                abi_hpp.write("#pragma once\n")
                abi_hpp.write(f'#include "{abi_h_name}"\n')
                abi_hpp.write(f"namespace {namespace} {{\n")

        if self.author:
            with open(path.join(self.dst_dir, impl_h_name), "w") as impl_h:
                impl_h.write(f'#include "{abi_h_name}"\n')

        for field in node.fields:
            if isinstance(field, ast.Function):
                self.visit(field)
            if isinstance(field, ast.Struct):
                self.visit(field)
                struct_name = field.name.text
                struct_abi_name = "__".join(self.pktupl) + "__" + struct_name
                struct_abi_h_name = basename + "." + struct_name + ".abi.h"
                if self.author or self.user:
                    with open(path.join(self.dst_dir, abi_h_name), "a") as abi_h:
                        abi_h.write(f'#include "{struct_abi_h_name}"\n')
                if self.user:
                    with open(path.join(self.dst_dir, abi_hpp_name), "a") as abi_h:
                        abi_h.write(f"using {struct_name} = {struct_abi_name};\n")

        if self.user:
            with open(path.join(self.dst_dir, abi_hpp_name), "a") as abi_hpp:
                abi_hpp.write(f"}}\n")

    def visit_Function(self, node: ast.Function):
        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"

        func_name = node.name.text
        func_abi_name = "__".join(self.pktupl) + "__" + func_name
        cpp_params = ", ".join(self.visit(parameter) for parameter in node.parameters)
        cpp_args = ", ".join(parameter.name.text for parameter in node.parameters)
        abi_params = cpp_params
        abi_args = cpp_args
        if len(node.return_types) > 1:
            raise NotImplementedError
        return_type = self.visit(node.return_types[0]) if node.return_types else "void"

        if self.author or self.user:
            with open(path.join(self.dst_dir, abi_h_name), "a") as abi_h:
                abi_h.write(f"TH_EXPORT {return_type} {func_abi_name}({abi_params});\n")

        if self.user:
            with open(path.join(self.dst_dir, abi_hpp_name), "a") as abi_hpp:
                abi_hpp.write(f"inline {return_type} {func_name}({cpp_params}) {{\n")
                abi_hpp.write(f"    return {func_abi_name}({abi_args});\n")
                abi_hpp.write("}\n")

        if self.author:
            with open(path.join(self.dst_dir, impl_h_name), "a") as impl_h:
                impl_h.write(f"#define TH_EXPORT_API_{func_name}(real_name) \\\n")
                impl_h.write(f"    {return_type} {func_abi_name}({abi_params}) {{\\\n")
                impl_h.write(f"        return real_name({cpp_args}); \\\n")
                impl_h.write("    }\n")

    def visit_UserType(self, node: ast.UserType):
        assert isinstance(node.pkname, ast.PackageName)
        pktupl = tuple(token.text for token in node.pkname.parts)
        return "__".join(pktupl) + "__" + node.name.text

    def visit_Struct(self, node: ast.Struct):
        basename = ".".join(self.pktupl)

        struct_name = node.name.text
        struct_abi_name = "__".join(self.pktupl) + "__" + struct_name
        struct_abi_h_name = basename + "." + struct_name + ".abi.h"

        if self.author or self.user:
            with open(path.join(self.dst_dir, struct_abi_h_name), "w") as abi_h:
                abi_h.write("#pragma once\n")
                abi_h.write('#include "taihe/common.h"\n')
                user_types: set[tuple[tuple[str, ...], str]] = set()
                for field in node.fields:
                    type = field.type
                    if isinstance(type, ast.UserType):
                        assert isinstance(type.pkname, ast.PackageName)
                        pktupl = tuple(token.text for token in type.pkname.parts)
                        text = type.name.text
                        user_types.add((pktupl, text))
                for pktupl, text in user_types:
                    user_type_abi_h_name = ".".join(pktupl) + "." + text + ".abi.h"
                    abi_h.write(f'#include "{user_type_abi_h_name}"\n')
                abi_h.write(f"struct {struct_abi_name} {{\n")
                for field in node.fields:
                    type = self.visit(field.type)
                    name = field.name.text
                    abi_h.write(f"    {type} {name};\n")
                abi_h.write("};\n")
