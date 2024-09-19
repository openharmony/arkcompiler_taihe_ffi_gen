from io import StringIO

from taihe.parse import Visitor, ast


class File:
    def __init__(self, is_header: bool = True):
        self.is_header = is_header
        self.headers: set[str] = set()
        self.code = StringIO()

    def output_to(self, dst_path: str):
        with open(dst_path, "w") as dst:
            if self.is_header:
                dst.write("#pragma once\n")
            for header in self.headers:
                dst.write(f'#include "{header}"\n')
            dst.write(self.code.getvalue())

    def update(self, code: str):
        self.code.write(code)

    def include(self, *header: str):
        self.headers.update(header)


class CodeGenerator(Visitor):
    def __init__(self, pktupl: tuple[str, ...], author: bool, user: bool):
        self.pktupl = pktupl
        self.author = author
        self.user = user
        self.files: dict[str, File] = {}

    def generic_visit(self, node):
        raise NotImplementedError

    def visit_BasicType(self, node: ast.BasicType, cpp: bool, param: bool):
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

    def visit_UserType(self, node: ast.UserType, cpp: bool, param: bool):
        assert isinstance(node.pkname, ast.PackageName)
        pktupl = tuple(token.text for token in node.pkname.parts)
        if not cpp:
            return "__".join(pktupl) + "__" + node.name.text
        else:
            return "::".join(pktupl) + "::" + node.name.text

    def visit_TypeWithSpecifier(
        self, node: ast.TypeWithSpecifier, cpp: bool, param: bool
    ):
        text = self.visit(node.type, cpp, param)
        if node.const:
            text += " const"
        if node.ref:
            text += "&" if cpp else "*"
        return text

    def visit_Parameter(self, node: ast.Parameter, cpp: bool):
        return (
            self.visit(node.type_with_specifier, cpp, param=True) + " " + node.name.text
        )

    def visit_Specification(self, node: ast.Specification):
        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"
        impl_hpp_name = basename + ".impl.hpp"

        if self.author or self.user:
            abi_h = self.files.setdefault(abi_h_name, File())
            abi_h.update('#include "taihe/common.h"\n')

        if self.user:
            abi_hpp = self.files.setdefault(abi_hpp_name, File())
            abi_hpp.include(abi_h_name)

        if self.author:
            impl_h = self.files.setdefault(impl_h_name, File())
            impl_h.include(abi_h_name)

            impl_hpp = self.files.setdefault(impl_hpp_name, File())
            impl_hpp.include(abi_h_name)

        for field in node.fields:
            self.visit(field)

    def visit_Function(self, node: ast.Function):
        func_name = node.name.text

        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"
        impl_hpp_name = basename + ".impl.hpp"

        namespace = "::".join(self.pktupl)

        func_abi_name = "__".join(self.pktupl) + "__" + func_name
        cpp_args_from_abi = ", ".join(
            ("*" if param.type_with_specifier.ref else "") + param.name.text
            for param in node.parameters
        )
        abi_args_from_cpp = ", ".join(
            ("&" if param.type_with_specifier.ref else "") + param.name.text
            for param in node.parameters
        )
        abi_args = ", ".join(param.name.text for param in node.parameters)
        cpp_params = ", ".join(
            [self.visit(param, cpp=True) for param in node.parameters]
        )
        abi_params = ", ".join(
            [self.visit(param, cpp=False) for param in node.parameters]
        )

        return_count = len(node.return_types)
        if return_count == 0:
            cpp_return_type = "void"
            abi_return_type = "void"
        elif return_count == 1:
            cpp_return_type = self.visit(node.return_types[0], cpp=True, param=False)
            abi_return_type = self.visit(node.return_types[0], cpp=False, param=False)
        else:
            raise NotImplementedError
        if return_count == 1 and node.return_types[0].ref:
            cpp_rv_from_abi = "*"
            abi_rv_from_cpp = "&"
        else:
            cpp_rv_from_abi = ""
            abi_rv_from_cpp = ""

        types = [
            param.type_with_specifier.type
            for param in node.parameters
            if isinstance(param.type_with_specifier.type, ast.UserType)
        ] + [
            return_type.type
            for return_type in node.return_types
            if isinstance(return_type.type, ast.UserType)
        ]

        if self.author or self.user:
            abi_h = self.files[abi_h_name]
            for type in types:
                assert isinstance(type.pkname, ast.PackageName)
                pktupl = tuple(token.text for token in type.pkname.parts)
                text = type.name.text
                user_type_abi_h_name = ".".join(pktupl) + "." + text + ".abi.h"
                abi_h.include(user_type_abi_h_name)
            abi_h.update(
                f"TH_EXPORT {abi_return_type} {func_abi_name}({abi_params});\n"
            )

        if self.user:
            abi_hpp = self.files[abi_hpp_name]
            for type in types:
                assert isinstance(type.pkname, ast.PackageName)
                pktupl = tuple(token.text for token in type.pkname.parts)
                text = type.name.text
                user_type_abi_hpp_name = ".".join(pktupl) + "." + text + ".abi.hpp"
                abi_hpp.include(user_type_abi_hpp_name)
            abi_hpp.update(f"namespace {namespace} {{\n")
            abi_hpp.update(f"inline {cpp_return_type} {func_name}({cpp_params}) {{\n")
            abi_hpp.update(
                f"    return {cpp_rv_from_abi}{func_abi_name}({abi_args_from_cpp});\n"
            )
            abi_hpp.update("}\n")
            abi_hpp.update("}\n")

        if self.author:
            impl_h = self.files[impl_h_name]
            impl_h.update(f"#define TH_EXPORT_C_API_{func_name}(_f) \\\n")
            impl_h.update(f"    {abi_return_type} {func_abi_name}({abi_params}) {{\\\n")
            impl_h.update(f"        return _f({abi_args}); \\\n")
            impl_h.update("    }\n")

            impl_hpp = self.files[impl_hpp_name]
            for type in types:
                assert isinstance(type.pkname, ast.PackageName)
                pktupl = tuple(token.text for token in type.pkname.parts)
                text = type.name.text
                user_type_abi_hpp_name = ".".join(pktupl) + "." + text + ".abi.hpp"
                impl_hpp.include(user_type_abi_hpp_name)
            impl_hpp.update(f"#define TH_EXPORT_CPP_API_{func_name}(_f) \\\n")
            impl_hpp.update(
                f"    {abi_return_type} {func_abi_name}({abi_params}) {{\\\n"
            )
            impl_hpp.update(
                f"        return {abi_rv_from_cpp}_f({cpp_args_from_abi}); \\\n"
            )
            impl_hpp.update("    }\n")

    def visit_Struct(self, node: ast.Struct):
        struct_name = node.name.text

        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        struct_abi_h_name = basename + "." + struct_name + ".abi.h"
        struct_abi_hpp_name = basename + "." + struct_name + ".abi.hpp"

        namespace = "::".join(self.pktupl)

        struct_abi_name = "__".join(self.pktupl) + "__" + struct_name

        types = [
            field.type for field in node.fields if isinstance(field.type, ast.UserType)
        ]

        if self.author or self.user:
            struct_abi_h = self.files.setdefault(struct_abi_h_name, File())
            struct_abi_h.include("taihe/common.h")
            for type in types:
                assert isinstance(type.pkname, ast.PackageName)
                pktupl = tuple(token.text for token in type.pkname.parts)
                text = type.name.text
                user_type_abi_h_name = ".".join(pktupl) + "." + text + ".abi.h"
                struct_abi_h.include(user_type_abi_h_name)
            struct_abi_h.update(f"typedef struct {struct_abi_name} {{\n")
            for field in node.fields:
                type = self.visit(field.type, cpp=False, param=False)
                name = field.name.text
                struct_abi_h.update(f"    {type} {name};\n")
            struct_abi_h.update(f"}} {struct_abi_name};\n")

            abi_h = self.files[abi_h_name]
            abi_h.include(struct_abi_h_name)

            struct_abi_hpp = self.files.setdefault(struct_abi_hpp_name, File())
            struct_abi_hpp.include(struct_abi_h_name)
            struct_abi_hpp.update(f"namespace {namespace} {{\n")
            struct_abi_hpp.update(f"using {struct_name} = {struct_abi_name};\n")
            struct_abi_hpp.update("}\n")

        if self.user:
            abi_hpp = self.files[abi_hpp_name]
            abi_hpp.include(struct_abi_hpp_name)
