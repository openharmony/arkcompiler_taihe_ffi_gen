from TaiheAST import TaiheAST
from TaiheVisitor import TaiheVisitor


class CodeGenerator(TaiheVisitor):
    def __init__(self, package_name: tuple[str]):
        self.package_name = package_name

    def visit_BasicType(self, node: TaiheAST.BasicType):
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

    def visit_TypeWithSpecifier(self, node: TaiheAST.TypeWithSpecifier):
        text = self.visit(node.type)
        if node.const:
            text += " const"
        text += " "
        if node.ref:
            text += "&"
        return text

    def visit_Parameter(self, node: TaiheAST.Parameter):
        return self.visit(node.type_with_specifier) + node.name.text

    def visit_Specification(self, node: TaiheAST.Specification):
        fields = []
        for field in node.fields:
            fields.append(self.visit(field))

        basename = ".".join(self.package_name)
        impl_basename = basename + "_impl"
        h_name = basename + ".h"
        cpp_name = basename + ".cpp"
        impl_h_name = impl_basename + ".h"
        impl_cpp_name = impl_basename + ".cpp"
        namespace = "::".join(self.package_name)
        impl_namespace = "_impl::" + namespace

        h_code = ""
        h_code += f"#pragma once\n"
        h_code += f'#include "taihe/common.h"\n'
        h_code += f'#define TH_EXTERN_C extern "C" TH_EXPORT\n'
        for h_first, h_second, cpp_field, impl_h_field, impl_cpp_field in fields:
            h_code += h_first
        h_code += f"namespace {namespace} {{\n"
        for h_first, h_second, cpp_field, impl_h_field, impl_cpp_field in fields:
            h_code += h_second
        h_code += f"}}\n"
        h_code += f"#undef TH_EXTERN_C\n"

        cpp_code = ""
        cpp_code += f'#include "{h_name}"\n'
        cpp_code += f'#include "{impl_h_name}"\n'
        for h_first, h_second, cpp_field, impl_h_field, impl_cpp_field in fields:
            cpp_code += cpp_field

        impl_h_code = ""
        impl_h_code += f"#pragma once\n"
        impl_h_code += f"#include <cstdint>\n"
        impl_h_code += f"namespace {impl_namespace} {{\n"
        for h_first, h_second, cpp_field, impl_h_field, impl_cpp_field in fields:
            impl_h_code += impl_h_field
        impl_h_code += f"}}\n"

        impl_cpp_code = ""
        impl_cpp_code += f'#include "{impl_h_name}"\n'
        impl_cpp_code += f"namespace {impl_namespace} {{\n"
        for h_first, h_second, cpp_field, impl_h_field, impl_cpp_field in fields:
            impl_cpp_code += impl_cpp_field
        impl_cpp_code += f"}}\n"

        return [
            (True, h_name, h_code),
            (False, cpp_name, cpp_code),
            (False, impl_h_name, impl_h_code),
            (False, impl_cpp_name, impl_cpp_code),
        ]

    def visit_Function(self, node: TaiheAST.Function):
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

        h_first = f"TH_EXTERN_C {return_type} {abi_name}({parameters});\n"
        h_second = ""
        h_second += f"inline {return_type} {func_name}({parameters}) {{\n"
        h_second += f"    return {abi_name}({arguments});\n"
        h_second += f"}}\n"

        cpp_field = ""
        cpp_field += f"{return_type} {abi_name}({parameters}) {{\n"
        cpp_field += f"    return {impl_name}({arguments});\n"
        cpp_field += f"}}\n"

        impl_h_field = f"{return_type} {func_name}({parameters});\n"

        impl_cpp_field = ""
        impl_cpp_field += f"{return_type} {func_name}({parameters}) {{\n"
        impl_cpp_field += f"    // todo\n"
        impl_cpp_field += f"}}\n"

        return h_first, h_second, cpp_field, impl_h_field, impl_cpp_field
