from os import path

from taihe.parse import Visitor, ast


class CodeGenerator(Visitor):
    def __init__(self, pktupl: tuple[str, ...], dst_dir: str, author: bool, user: bool):
        self.pktupl = pktupl
        self.dst_dir = dst_dir
        self.author = author
        self.user = user

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
            text += "&"
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

        if self.author or self.user:
            with open(path.join(self.dst_dir, abi_h_name), "w") as abi_h:
                abi_h.write("#pragma once\n")
                abi_h.write('#include "taihe/common.h"\n')

        if self.user:
            with open(path.join(self.dst_dir, abi_hpp_name), "w") as abi_hpp:
                abi_hpp.write("#pragma once\n")
                abi_hpp.write(f'#include "{abi_h_name}"\n')

        if self.author:
            with open(path.join(self.dst_dir, impl_h_name), "w") as impl_h:
                impl_h.write(f'#include "{abi_h_name}"\n')

        for field in node.fields:
            self.visit(field)

    def visit_Function(self, node: ast.Function):
        func_name = node.name.text
        
        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"

        namespace = "::".join(self.pktupl)

        func_abi_name = "__".join(self.pktupl) + "__" + func_name
        args = ", ".join(param.name.text for param in node.parameters)
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

        types = [
            type
            for param in node.parameters
            if isinstance(type := param.type_with_specifier.type, ast.UserType)
        ] + [
            type
            for return_type in node.return_types
            if isinstance(type := return_type.type, ast.UserType)
        ]

        if self.author or self.user:
            with open(path.join(self.dst_dir, abi_h_name), "a") as abi_h:
                for type in types:
                    assert isinstance(type.pkname, ast.PackageName)
                    pktupl = tuple(token.text for token in type.pkname.parts)
                    text = type.name.text
                    user_type_abi_h_name = ".".join(pktupl) + "." + text + ".abi.h"
                    abi_h.write(f'#include "{user_type_abi_h_name}"\n')
                abi_h.write(
                    f"TH_EXPORT {abi_return_type} {func_abi_name}({abi_params});\n"
                )

        if self.user:
            with open(path.join(self.dst_dir, abi_hpp_name), "a") as abi_hpp:
                for type in types:
                    assert isinstance(type.pkname, ast.PackageName)
                    pktupl = tuple(token.text for token in type.pkname.parts)
                    text = type.name.text
                    user_type_abi_hpp_name = ".".join(pktupl) + "." + text + ".abi.hpp"
                    abi_hpp.write(f'#include "{user_type_abi_hpp_name}"\n')
                abi_hpp.write(f"namespace {namespace} {{\n")
                abi_hpp.write(
                    f"inline {cpp_return_type} {func_name}({cpp_params}) {{\n"
                )
                abi_hpp.write(f"    return {func_abi_name}({args});\n")
                abi_hpp.write("}\n")
                abi_hpp.write("}\n")

        if self.author:
            with open(path.join(self.dst_dir, impl_h_name), "a") as impl_h:
                impl_h.write("#ifdef __cplusplus\n")
                for type in types:
                    assert isinstance(type.pkname, ast.PackageName)
                    pktupl = tuple(token.text for token in type.pkname.parts)
                    text = type.name.text
                    user_type_abi_hpp_name = ".".join(pktupl) + "." + text + ".abi.hpp"
                    impl_h.write(f'#include "{user_type_abi_hpp_name}"\n')
                impl_h.write("#endif\n")
                impl_h.write(f"#define TH_EXPORT_API_{func_name}(_func) \\\n")
                impl_h.write(
                    f"    {abi_return_type} {func_abi_name}({abi_params}) {{\\\n"
                )
                impl_h.write(f"        return _func({args}); \\\n")
                impl_h.write("    }\n")

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
            type
            for field in node.fields
            if isinstance(type := field.type, ast.UserType)
        ]

        if self.author or self.user:
            with open(path.join(self.dst_dir, struct_abi_h_name), "w") as struct_abi_h:
                struct_abi_h.write("#pragma once\n")
                struct_abi_h.write('#include "taihe/common.h"\n')
                for type in types:
                    assert isinstance(type.pkname, ast.PackageName)
                    pktupl = tuple(token.text for token in type.pkname.parts)
                    text = type.name.text
                    user_type_abi_h_name = ".".join(pktupl) + "." + text + ".abi.h"
                    struct_abi_h.write(f'#include "{user_type_abi_h_name}"\n')
                struct_abi_h.write(f"struct {struct_abi_name} {{\n")
                for field in node.fields:
                    type = self.visit(field.type, cpp=False, param=False)
                    name = field.name.text
                    struct_abi_h.write(f"    {type} {name};\n")
                struct_abi_h.write("};\n")

            with open(path.join(self.dst_dir, abi_h_name), "a") as abi_h:
                abi_h.write(f'#include "{struct_abi_h_name}"\n')

        if self.author or self.user:
            with open(
                path.join(self.dst_dir, struct_abi_hpp_name), "w"
            ) as struct_abi_hpp:
                struct_abi_hpp.write(f'#include "{struct_abi_h_name}"\n')
                struct_abi_hpp.write(f"namespace {namespace} {{\n")
                struct_abi_hpp.write(f"using {struct_name} = {struct_abi_name};\n")
                struct_abi_hpp.write("}\n")

            with open(path.join(self.dst_dir, abi_hpp_name), "a") as abi_hpp:
                abi_hpp.write(f'#include "{struct_abi_hpp_name}"\n')
