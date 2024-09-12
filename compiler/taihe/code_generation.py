from taihe.parse import ast, Visitor


class CodeGenerator(Visitor):
    def __init__(self, package_name: tuple[str]):
        self.package_name = package_name

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
        impl_hpp_name = basename + "_impl.hpp"
        impl_cpp_name = basename + "_impl.cpp"
        h_name = basename + ".h"
        hpp_name = basename + ".hpp"
        cpp_name = basename + ".cpp"
        namespace = "::".join(self.package_name)
        impl_namespace = "_impl::" + namespace

        impl_hpp_code = ""
        impl_hpp_code += f"#pragma once\n"
        impl_hpp_code += f"#include <cstdint>\n"
        impl_hpp_code += f"namespace {impl_namespace} {{\n"
        for h_field, hpp_field, cpp_field, impl_h_field, impl_cpp_field in fields:
            impl_hpp_code += impl_h_field
        impl_hpp_code += f"}}\n"

        impl_cpp_code = ""
        impl_cpp_code += f'#include "{impl_hpp_name}"\n'
        impl_cpp_code += f"namespace {impl_namespace} {{\n"
        for h_field, hpp_field, cpp_field, impl_h_field, impl_cpp_field in fields:
            impl_cpp_code += impl_cpp_field
        impl_cpp_code += f"}}\n"

        h_code = ""
        h_code += f"#pragma once\n"
        h_code += f'#include "taihe/common.h"\n'
        h_code += f'#ifdef __cplusplus\n'
        h_code += f'#define TH_EXTERN_C extern "C" TH_EXPORT\n'
        h_code += f'#else\n'
        h_code += f'#define TH_EXTERN_C TH_EXPORT\n'
        h_code += f'#endif\n'
        for h_field, hpp_field, cpp_field, impl_h_field, impl_cpp_field in fields:
            h_code += h_field

        hpp_code = ""
        hpp_code += f"#pragma once\n"
        hpp_code += f'#include "{h_name}"\n'
        hpp_code += f"namespace {namespace} {{\n"
        for h_field, hpp_field, cpp_field, impl_h_field, impl_cpp_field in fields:
            hpp_code += hpp_field
        hpp_code += f"}}\n"

        cpp_code = ""
        cpp_code += f'#include "{h_name}"\n'
        cpp_code += f'#include "{impl_hpp_name}"\n'
        for h_field, hpp_field, cpp_field, impl_h_field, impl_cpp_field in fields:
            cpp_code += cpp_field

        return [
            (True, h_name, h_code),
            (True, hpp_name, hpp_code),
            (False, cpp_name, cpp_code),
            (False, impl_hpp_name, impl_hpp_code),
            (False, impl_cpp_name, impl_cpp_code),
        ]

    def visit_Function(self, node: ast.Function):
        namespace = "::".join(self.package_name)
        impl_namespace = "_impl::" + namespace
        func_name = node.name.text
        abi_name = "__".join(self.package_name) + "__" + func_name
        impl_name = impl_namespace + "::" + func_name
        parameters = ", ".join(self.visit(parameter) for parameter in node.parameters)
        arguments = ", ".join(parameter.name.text for parameter in node.parameters)
        if len(node.return_types) > 1:
            raise NotImplementedError
        return_type = self.visit(node.return_types[0]) if node.return_types else "void"

        h_field = f"TH_EXTERN_C {return_type} {abi_name}({parameters});\n"

        hpp_field = ""
        hpp_field += f"inline {return_type} {func_name}({parameters}) {{\n"
        hpp_field += f"    return {abi_name}({arguments});\n"
        hpp_field += f"}}\n"

        cpp_field = ""
        cpp_field += f"{return_type} {abi_name}({parameters}) {{\n"
        cpp_field += f"    return {impl_name}({arguments});\n"
        cpp_field += f"}}\n"

        impl_h_field = f"{return_type} {func_name}({parameters});\n"

        impl_cpp_field = ""
        impl_cpp_field += f"{return_type} {func_name}({parameters}) {{\n"
        impl_cpp_field += f"    // todo\n"
        impl_cpp_field += f"}}\n"

        return h_field, hpp_field, cpp_field, impl_h_field, impl_cpp_field
