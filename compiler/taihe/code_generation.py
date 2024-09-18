from os import path
from typing import Any

from taihe.parse import Visitor, ast


class CodeGenerator(Visitor):
    def __init__(
        self, package_name: tuple[str, ...], dst_dir: str, author: bool, user: bool
    ):
        self.package_name = package_name
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
        basename = ".".join(self.package_name)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"

        namespace = "::".join(self.package_name)

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

        if self.user:
            with open(path.join(self.dst_dir, abi_hpp_name), "a") as abi_hpp:
                abi_hpp.write(f"}}\n")

    def visit_Function(self, node: ast.Function):
        basename = ".".join(self.package_name)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"

        func_name = node.name.text
        abi_name = "__".join(self.package_name) + "__" + func_name
        cpp_params = ", ".join(self.visit(parameter) for parameter in node.parameters)
        cpp_args = ", ".join(parameter.name.text for parameter in node.parameters)
        abi_params = cpp_params
        abi_args = cpp_args
        if len(node.return_types) > 1:
            raise NotImplementedError
        return_type = self.visit(node.return_types[0]) if node.return_types else "void"

        if self.author or self.user:
            with open(path.join(self.dst_dir, abi_h_name), "a") as abi_h:
                abi_h.write(f"TH_EXPORT {return_type} {abi_name}({abi_params});\n")

        if self.user:
            with open(path.join(self.dst_dir, abi_hpp_name), "a") as abi_hpp:
                abi_hpp.write(f"inline {return_type} {func_name}({cpp_params}) {{\n")
                abi_hpp.write(f"    return {abi_name}({abi_args});\n")
                abi_hpp.write("}\n")

        if self.author:
            with open(path.join(self.dst_dir, impl_h_name), "a") as impl_h:
                impl_h.write(f"#define TH_EXPORT_API_{func_name}(real_name) \\\n")
                impl_h.write(f"    {return_type} {abi_name}({abi_params}) {{\\\n")
                impl_h.write(f"        return real_name({cpp_args}); \\\n")
                impl_h.write("    }\n")
