from taihe.parse import ast, Visitor


class CodeGenerator(Visitor):
    def __init__(self, package_name: tuple[str, ...]):
        self.package_name = package_name

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
        fields = []
        for field in node.fields:
            fields.append(self.visit(field))

        basename = ".".join(self.package_name)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"
        namespace = "::".join(self.package_name)

        abi_h_code = ""
        abi_h_code += f"#pragma once\n"
        abi_h_code += f'#include "taihe/common.h"\n'
        for h_field, hpp_field, cpp_field in fields:
            abi_h_code += h_field

        abi_hpp_code = ""
        abi_hpp_code += f"#pragma once\n"
        abi_hpp_code += f'#include "{abi_h_name}"\n'
        abi_hpp_code += f"namespace {namespace} {{\n"
        for h_field, hpp_field, cpp_field in fields:
            abi_hpp_code += hpp_field
        abi_hpp_code += f"}}\n"

        impl_h_code = ""
        impl_h_code += f'#include "{abi_h_name}"\n'
        for h_field, hpp_field, cpp_field in fields:
            impl_h_code += cpp_field

        return [
            (True, True, abi_h_name, abi_h_code),
            (False, True, abi_hpp_name, abi_hpp_code),
            (True, False, impl_h_name, impl_h_code),
        ]

    def visit_Function(self, node: ast.Function):
        namespace = "::".join(self.package_name)
        func_name = node.name.text
        abi_name = "__".join(self.package_name) + "__" + func_name
        cpp_params = ", ".join(self.visit(parameter) for parameter in node.parameters)
        cpp_args = ", ".join(parameter.name.text for parameter in node.parameters)
        abi_params = cpp_params
        abi_args = cpp_args
        if len(node.return_types) > 1:
            raise NotImplementedError
        return_type = self.visit(node.return_types[0]) if node.return_types else "void"

        abi_h_field = f"TH_EXPORT {return_type} {abi_name}({abi_params});\n"

        abi_hpp_field = ""
        abi_hpp_field += f"inline {return_type} {func_name}({cpp_params}) {{\n"
        abi_hpp_field += f"    return {abi_name}({abi_args});\n"
        abi_hpp_field += f"}}\n"

        impl_h_field = ""
        impl_h_field += f"#define TH_EXPORT_API_{func_name}(real_name) \\\n"
        impl_h_field += f"    {return_type} {abi_name}({abi_params}) {{ \\\n"
        impl_h_field += f"        return real_name({cpp_args}); \\\n"
        impl_h_field += f"    }}\n"

        return abi_h_field, abi_hpp_field, impl_h_field
