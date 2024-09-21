from io import StringIO

from taihe.parse import Visitor, ast


class File:
    def __init__(self, is_header: bool):
        self.is_header = is_header
        self.headers: set[str] = set()
        self.code = StringIO()

    def output_to(self, dst_path: str):
        # fmt: off
        with open(dst_path, "w") as dst:
            if self.is_header:
                dst.write(f"#pragma once\n")
            for header in self.headers:
                dst.write(f'#include "{header}"\n')
            dst.write(self.code.getvalue())

    def write(self, code: str):
        self.code.write(code)

    def include(self, *headers: str | None):
        for header in headers:
            if header is not None:
                self.headers.add(header)


class CodeGenerator(Visitor):
    # fmt: off
    def __init__(self, pktupl: tuple[str, ...], author: bool, user: bool):
        self.pktupl = pktupl
        self.author = author
        self.user = user
        self.files: dict[str, File] = {}

    def generic_visit(self, node):
        raise NotImplementedError

    def visit_BasicType(self, node: ast.BasicType, cpp: bool, param: bool):
        if node.name.text == "bool":
            return "bool", None
        if node.name.text == "f32":
            return "float", None
        if node.name.text == "f64":
            return "double", None
        if node.name.text == "i8":
            return "int8_t", None
        if node.name.text == "i16":
            return "int16_t", None
        if node.name.text == "i32":
            return "int32_t", None
        if node.name.text == "i64":
            return "int64_t", None
        if node.name.text == "u8":
            return "uint8_t", None
        if node.name.text == "u16":
            return "uint16_t", None
        if node.name.text == "u32":
            return "uint32_t", None
        if node.name.text == "u64":
            return "uint64_t", None
        if node.name.text == "String":
            if cpp:
                return "taihe::core::param::string" if param else "taihe::core::string", "core/string.hpp"
            else:
                return "struct TString*", "taihe/string.abi.h"
        raise NotImplementedError

    def visit_UserType(self, node: ast.UserType, cpp: bool, param: bool):
        assert node.pkname
        pktupl = tuple(token.text for token in node.pkname.parts)
        type_name = node.name.text
        type_basename = ".".join(pktupl) + "." + type_name
        if cpp:
            return "::".join(pktupl) + "::" + type_name, type_basename + ".abi.hpp"
        else:
            return "__".join(pktupl) + "__" + type_name, type_basename + ".abi.h"

    def visit_TypeWithSpecifier(self, node: ast.TypeWithSpecifier, cpp: bool, param: bool):
        type, header = self.visit(node.type, cpp, param)
        if node.const:
            type += " const"
        if node.ref:
            type += "&" if cpp else "*"
        return type, header

    def visit_Specification(self, node: ast.Specification):
        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"
        impl_hpp_name = basename + ".impl.hpp"

        if self.author or self.user:
            abi_h = self.files.setdefault(abi_h_name, File(is_header=True))
            abi_h.include("taihe/common.h")

        if self.user:
            abi_hpp = self.files.setdefault(abi_hpp_name, File(is_header=True))
            abi_hpp.include("core/common.hpp")
            abi_hpp.include(abi_h_name)

        if self.author:
            impl_h = self.files.setdefault(impl_h_name, File(is_header=True))
            impl_h.include("taihe/common.h")
            impl_h.include(abi_h_name)

            impl_hpp = self.files.setdefault(impl_hpp_name, File(is_header=True))
            impl_hpp.include("core/common.hpp")
            impl_hpp.include(abi_h_name)

        for field in node.fields:
            self.visit(field)

    def visit_Function(self, node: ast.Function):
        func_name = node.name.text
        func_abi_name = "__".join(self.pktupl) + "__" + func_name

        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"
        impl_hpp_name = basename + ".impl.hpp"

        namespace = "::".join(self.pktupl)

        args_from_abi = []
        args_into_abi = []
        cpp_params = []
        abi_params = []
        cpp_param_headers = []
        abi_param_headers = []
        for param in node.parameters:
            cpp_param_type, cpp_param_header = self.visit(param.type_with_specifier, cpp=True, param=True)
            abi_param_type, abi_param_header = self.visit(param.type_with_specifier, cpp=False, param=True)
            param_name = param.name.text
            cpp_param_headers.append(cpp_param_header)
            abi_param_headers.append(abi_param_header)
            args_from_abi.append(f"taihe::core::from_abi<{cpp_param_type}, {abi_param_type}>({param_name})")
            args_into_abi.append(f"taihe::core::into_abi<{cpp_param_type}, {abi_param_type}>({param_name})")
            cpp_params.append(f"{cpp_param_type} {param_name}")
            abi_params.append(f"{abi_param_type} {param_name}")
        args_from_abi_str = ", ".join(args_from_abi)
        args_into_abi_str = ", ".join(args_into_abi)
        cpp_params_str = ", ".join(cpp_params)
        abi_params_str = ", ".join(abi_params)

        cpp_return_headers = []
        abi_return_headers = []
        if len(node.return_types) == 0:
            cpp_return_type = "void"
            abi_return_type = "void"
            return_from_abi = ""
            return_into_abi = ""
        elif len(node.return_types) == 1:
            cpp_return_type, cpp_return_header = self.visit(node.return_types[0], cpp=True, param=False)
            abi_return_type, abi_return_header = self.visit(node.return_types[0], cpp=False, param=False)
            return_from_abi = f"taihe::core::from_abi<{cpp_return_type}, {abi_return_type}>"
            return_into_abi = f"taihe::core::into_abi<{cpp_return_type}, {abi_return_type}>"
            cpp_return_headers.append(cpp_return_header)
            abi_return_headers.append(abi_return_header)
        else:
            cpp_return_iters = []
            abi_return_iters = []
            for return_type in node.return_types:
                cpp_return_iter, cpp_return_header = self.visit(return_type, cpp=True, param=False)
                abi_return_iter, abi_return_header = self.visit(return_type, cpp=False, param=False)
                cpp_return_headers.append(cpp_return_header)
                abi_return_headers.append(abi_return_header)
                cpp_return_iters.append(cpp_return_iter)
                abi_return_iters.append(abi_return_iter)
            cpp_return_iters_str = ", ".join(cpp_return_iters)
            cpp_return_type = f"std::tuple<{cpp_return_iters_str}>"
            abi_return_type = f"{func_abi_name}__return_t"

            if self.author or self.user:
                abi_h = self.files[abi_h_name]
                abi_h.write(f"typedef struct {abi_return_type} {{\n")
                for i, abi_return_iter in enumerate(abi_return_iters):
                    abi_h.write(f"    {abi_return_iter} _{i};\n")
                abi_h.write(f"}} {abi_return_type};\n")

            if self.user:
                abi_hpp = self.files[abi_hpp_name]
                abi_hpp.include("tuple")
                abi_hpp.write(f"template<>\n")
                abi_hpp.write(f"inline {cpp_return_type} taihe::core::from_abi({abi_return_type} _val) {{\n")
                abi_hpp.write(f"    return {{\n")
                for i, (cpp_return_iter, abi_return_iter) in enumerate(zip(cpp_return_iters, abi_return_iters)):
                    abi_hpp.write(f"        taihe::core::from_abi<{cpp_return_iter}, {abi_return_iter}>(_val._{i}), \n")
                abi_hpp.write(f"    }};\n")
                abi_hpp.write(f"}}\n")
    
            if self.author:
                impl_hpp = self.files[impl_hpp_name]
                abi_hpp.include("tuple")
                impl_hpp.write(f"template<>\n")
                impl_hpp.write(f"inline {abi_return_type} taihe::core::into_abi({cpp_return_type} _val) {{\n")
                impl_hpp.write(f"    return {{\n")
                for i, (cpp_return_iter, abi_return_iter) in enumerate(zip(cpp_return_iters, abi_return_iters)):
                    impl_hpp.write(f"        taihe::core::into_abi<{cpp_return_iter}, {abi_return_iter}>(std::get<{i}>(_val)), \n")
                impl_hpp.write(f"    }};\n")
                impl_hpp.write(f"}}\n")
    
            return_from_abi = f"taihe::core::from_abi<{cpp_return_type}, {abi_return_type}>"
            return_into_abi = f"taihe::core::into_abi<{cpp_return_type}, {abi_return_type}>"

        if self.author or self.user:
            abi_h = self.files[abi_h_name]
            abi_h.include(*abi_param_headers, *abi_return_headers)
            abi_h.write(f"TH_EXPORT {abi_return_type} {func_abi_name}({abi_params_str});\n")

        if self.user:
            abi_hpp = self.files[abi_hpp_name]
            abi_hpp.include(*cpp_param_headers, *cpp_return_headers)
            abi_hpp.write(f"namespace {namespace} {{\n")
            abi_hpp.write(f"inline {cpp_return_type} {func_name}({cpp_params_str}) {{\n")
            abi_hpp.write(f"    return {return_from_abi}({func_abi_name}({args_into_abi_str}));\n")
            abi_hpp.write(f"}}\n")
            abi_hpp.write(f"}}\n")

        if self.author:
            impl_h = self.files[impl_h_name]
            impl_h.include(*abi_param_headers, *abi_return_headers)
            impl_h.write(f"#define TH_EXPORT_C_API_{func_name}(_func) \\\n")
            impl_h.write(f"    {abi_return_type} {func_abi_name}({abi_params_str}) __attribute__((alias(#_func)));\n")

            impl_hpp = self.files[impl_hpp_name]
            impl_hpp.include(*cpp_param_headers, *cpp_return_headers)
            impl_hpp.write(f"#define TH_EXPORT_CPP_API_{func_name}(_func) \\\n")
            impl_hpp.write(f"    {abi_return_type} {func_abi_name}({abi_params_str}) {{ \\\n")
            impl_hpp.write(f"        return {return_into_abi}(_func({args_from_abi_str})); \\\n")
            impl_hpp.write(f"    }}\n")

    def visit_Struct(self, node: ast.Struct):
        struct_name = node.name.text

        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        struct_basename = basename + "." + struct_name
        struct_abi_h_name = struct_basename + ".abi.h"
        struct_abi_hpp_name = struct_basename + ".abi.hpp"

        namespace = "::".join(self.pktupl)

        struct_abi_name = "__".join(self.pktupl) + "__" + struct_name
        struct_cpp_name = "::".join(self.pktupl) + "::" + struct_name

        if self.author or self.user:
            struct_abi_h = self.files.setdefault(struct_abi_h_name, File(is_header=True))
            struct_abi_h.include("taihe/common.h")
            struct_abi_h.write(f"typedef struct {struct_abi_name} {{\n")
            for field in node.fields:
                type, header = self.visit(field.type, cpp=False, param=False)
                name = field.name.text
                struct_abi_h.write(f"    {type} {name};\n")
                struct_abi_h.include(header)
            struct_abi_h.write(f"}} {struct_abi_name};\n")

            abi_h = self.files[abi_h_name]
            abi_h.include(struct_abi_h_name)

            struct_abi_hpp = self.files.setdefault(struct_abi_hpp_name, File(is_header=True))
            struct_abi_hpp.include("core/common.hpp")
            struct_abi_hpp.include(struct_abi_h_name)
            struct_abi_hpp.write(f"namespace {namespace} {{\n")
            struct_abi_hpp.write(f"struct {struct_name} {{\n")
            for field in node.fields:
                type, header = self.visit(field.type, cpp=True, param=False)
                name = field.name.text
                struct_abi_hpp.write(f"    {type} {name};\n")
                struct_abi_hpp.include(header)
            struct_abi_hpp.write(f"}};\n")
            struct_abi_hpp.write(f"}}\n")
            struct_abi_hpp.write(f"template<>\n")
            struct_abi_hpp.write(f"inline {struct_abi_name} taihe::core::into_abi({struct_cpp_name} _val) {{\n")
            struct_abi_hpp.write(f"    return reinterpret_cast<{struct_abi_name} &>(_val);\n")
            struct_abi_hpp.write(f"}}\n")
            struct_abi_hpp.write(f"template<>\n")
            struct_abi_hpp.write(f"inline {struct_cpp_name} taihe::core::from_abi({struct_abi_name} _val) {{\n")
            struct_abi_hpp.write(f"    return reinterpret_cast<{struct_cpp_name} &>(_val);\n")
            struct_abi_hpp.write(f"}}\n")
            struct_abi_hpp.write(f"template<>\n")
            struct_abi_hpp.write(f"inline {struct_abi_name} *taihe::core::into_abi({struct_cpp_name} &_val) {{\n")
            struct_abi_hpp.write(f"    return reinterpret_cast<{struct_abi_name} *>(&_val);\n")
            struct_abi_hpp.write(f"}}\n")
            struct_abi_hpp.write(f"template<>\n")
            struct_abi_hpp.write(f"inline {struct_cpp_name} &taihe::core::from_abi({struct_abi_name} *_val) {{\n")
            struct_abi_hpp.write(f"    return reinterpret_cast<{struct_cpp_name} &>(*_val);\n")
            struct_abi_hpp.write(f"}}\n")
            struct_abi_hpp.write(f"template<>\n")
            struct_abi_hpp.write(f"inline {struct_abi_name} const *taihe::core::into_abi({struct_cpp_name} const &_val) {{\n")
            struct_abi_hpp.write(f"    return reinterpret_cast<{struct_abi_name} const *>(&_val);\n")
            struct_abi_hpp.write(f"}}\n")
            struct_abi_hpp.write(f"template<>\n")
            struct_abi_hpp.write(f"inline {struct_cpp_name} const &taihe::core::from_abi({struct_abi_name} const *_val) {{\n")
            struct_abi_hpp.write(f"    return reinterpret_cast<{struct_cpp_name} const &>(*_val);\n")
            struct_abi_hpp.write(f"}}\n")

        if self.user:
            abi_hpp = self.files[abi_hpp_name]
            abi_hpp.include(struct_abi_hpp_name)
