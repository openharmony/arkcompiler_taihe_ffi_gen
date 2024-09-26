from io import StringIO

from taihe.parse import Visitor, ast


class File:
    def __init__(self, is_header: bool):
        self.is_header = is_header
        self.headers: set[str] = set()
        self.code = StringIO()

    def output_to(self, dst_path: str):
        with open(dst_path, "w") as dst:
            if self.is_header:
                dst.write(f"#pragma once\n")
            for header in self.headers:
                dst.write(f"#include <{header}>\n")
            dst.write(self.code.getvalue())

    def write(self, code: str):
        self.code.write(code)

    def include(self, *headers: str | None):
        for header in headers:
            if header is not None:
                self.headers.add(header)


class CodeGenerator(Visitor):
    def __init__(self, pktupl: tuple[str, ...], author: bool, user: bool):
        self.pktupl = pktupl
        self.author = author
        self.user = user
        self.files: dict[str, File] = {}

    def generic_visit(self, node):
        raise NotImplementedError

    def visit_BasicType(self, node: ast.BasicType, cpp: bool, param: bool = False):
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
                return "taihe::core::string_view" if param else "taihe::core::string", "core/string.hpp"
            else:
                return "struct TString*", "taihe/string.abi.h"
        raise NotImplementedError

    def visit_UserType(self, node: ast.UserType, cpp: bool, param: bool = False):
        assert node.pkname
        pktupl = tuple(token.text for token in node.pkname.parts)
        type_name = node.name.text
        type_basename = ".".join(pktupl) + "." + type_name
        if cpp:
            return "::" + "::".join(pktupl) + "::" + type_name, type_basename + ".abi.hpp"
        else:
            return "__" + "__".join(pktupl) + "__" + type_name, type_basename + ".abi.h"

    def visit_QualifiedType(self, node: ast.QualifiedType, cpp: bool, param: bool = False):
        type, header = self.visit(node.type, cpp, param)
        if node.mut is not None:
            if node.mut.text != "mut":
                type += " const"
            type += "&" if cpp else "*"
        return type, header

    def visit_Spec(self, node: ast.Spec):
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
            abi_hpp.include("taihe/common.hpp")
            abi_hpp.include(abi_h_name)

        if self.author:
            impl_h = self.files.setdefault(impl_h_name, File(is_header=True))
            impl_h.include("taihe/common.h")
            impl_h.include(abi_h_name)

            impl_hpp = self.files.setdefault(impl_hpp_name, File(is_header=True))
            impl_hpp.include("taihe/common.hpp")
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

        abi_func_name = "__" + "__".join(self.pktupl) + "__" + func_name
        cpp_func_name = "::" + "::".join(self.pktupl) + "::" + func_name

        args = []
        cpp_param_headers = []
        abi_param_headers = []
        args_from_abi = []
        args_into_abi = []
        cpp_params = []
        abi_params = []
        for param in node.parameters:
            cpp_param_type, cpp_param_header = self.visit(param.param_type, cpp=True, param=True)
            abi_param_type, abi_param_header = self.visit(param.param_type, cpp=False)
            param_name = param.name.text
            args.append(param_name)
            cpp_param_headers.append(cpp_param_header)
            abi_param_headers.append(abi_param_header)
            args_from_abi.append(f"taihe::core::from_abi<{cpp_param_type}, {abi_param_type}>(static_cast<std::add_rvalue_reference_t<{abi_param_type}>>({param_name}))")
            args_into_abi.append(f"taihe::core::into_abi<{cpp_param_type}, {abi_param_type}>(static_cast<std::add_rvalue_reference_t<{cpp_param_type}>>({param_name}))")
            cpp_params.append(f"{cpp_param_type} {param_name}")
            abi_params.append(f"{abi_param_type} {param_name}")
        args_str = ", ".join(args)
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
            cpp_return_type, cpp_return_header = self.visit(node.return_types[0], cpp=True)
            abi_return_type, abi_return_header = self.visit(node.return_types[0], cpp=False)
            return_from_abi = f"taihe::core::from_abi<{cpp_return_type}, {abi_return_type}>"
            return_into_abi = f"taihe::core::into_abi<{cpp_return_type}, {abi_return_type}>"
            cpp_return_headers.append(cpp_return_header)
            abi_return_headers.append(abi_return_header)
        else:
            cpp_return_parts = []
            abi_return_parts = []
            for return_type in node.return_types:
                cpp_return_part, cpp_return_header = self.visit(return_type, cpp=True)
                abi_return_part, abi_return_header = self.visit(return_type, cpp=False)
                cpp_return_headers.append(cpp_return_header)
                abi_return_headers.append(abi_return_header)
                cpp_return_parts.append(cpp_return_part)
                abi_return_parts.append(abi_return_part)
            cpp_return_parts_str = ", ".join(cpp_return_parts)
            abi_return_struct_name = f"{abi_func_name}__return_t"
            abi_return_type = f"struct {abi_func_name}__return_t"
            cpp_return_type = f"std::tuple<{cpp_return_parts_str}>"
            return_from_abi = f"taihe::core::from_abi<{cpp_return_type}, {abi_return_type}>"
            return_into_abi = f"taihe::core::into_abi<{cpp_return_type}, {abi_return_type}>"

            if self.author or self.user:
                abi_h = self.files[abi_h_name]
                abi_h.write(f"struct {abi_return_struct_name} {{\n")
                for i, abi_return_part in enumerate(abi_return_parts):
                    abi_h.write(f"    {abi_return_part} _{i};\n")
                abi_h.write(f"}};\n")

            if self.user:
                abi_hpp = self.files[abi_hpp_name]
                abi_hpp.write(f"template<>\n")
                abi_hpp.write(f"inline {cpp_return_type} taihe::core::from_abi(std::add_rvalue_reference_t<{abi_return_type}> _val) {{\n")
                abi_hpp.write(f"    return {{\n")
                for i, (cpp_return_part, abi_return_part) in enumerate(zip(cpp_return_parts, abi_return_parts, strict=True)):
                    abi_hpp.write(f"        taihe::core::from_abi<{cpp_return_part}, {abi_return_part}>(static_cast<std::add_rvalue_reference_t<{abi_return_part}>>(_val._{i})), \n")
                abi_hpp.write(f"    }};\n")
                abi_hpp.write(f"}}\n")

            if self.author:
                impl_hpp = self.files[impl_hpp_name]
                impl_hpp.write(f"template<>\n")
                impl_hpp.write(f"inline {abi_return_type} taihe::core::into_abi(std::add_rvalue_reference_t<{cpp_return_type}> _val) {{\n")
                impl_hpp.write(f"    return {{\n")
                for i, (cpp_return_part, abi_return_part) in enumerate(zip(cpp_return_parts, abi_return_parts, strict=True)):
                    impl_hpp.write(f"        taihe::core::into_abi<{cpp_return_part}, {abi_return_part}>(static_cast<std::add_rvalue_reference_t<{cpp_return_part}>>(std::get<{i}>(_val))), \n")
                impl_hpp.write(f"    }};\n")
                impl_hpp.write(f"}}\n")

        if self.author or self.user:
            abi_h = self.files[abi_h_name]
            abi_h.include(*abi_param_headers, *abi_return_headers)
            abi_h.write(f"TH_EXPORT {abi_return_type} {abi_func_name}({abi_params_str});\n")

        if self.user:
            abi_hpp = self.files[abi_hpp_name]
            abi_hpp.include(*cpp_param_headers, *cpp_return_headers)
            abi_hpp.write(f"namespace {namespace} {{\n")
            abi_hpp.write(f"inline {cpp_return_type} {func_name}({cpp_params_str}) {{\n")
            abi_hpp.write(f"    return {return_from_abi}({abi_func_name}({args_into_abi_str}));\n")
            abi_hpp.write(f"}}\n")
            abi_hpp.write(f"}}\n")

        if self.author:
            impl_h = self.files[impl_h_name]
            impl_h.include(*abi_param_headers, *abi_return_headers)
            impl_h.write(f"#define TH_EXPORT_C_API_{func_name}(_func) \\\n")
            impl_h.write(f"    TH_STATIC_ASSERT(TH_IS_SAME(TH_TYPEOF(_func), {abi_return_type} ({abi_params_str})), \\\n")
            impl_h.write(f"        \"'\" #_func \"' is incompatible with '{abi_return_type} {abi_func_name}({abi_params_str})'\"); \\\n")
            impl_h.write(f"    {abi_return_type} {abi_func_name}({abi_params_str}) {{ \\\n")
            impl_h.write(f"        return _func({args_str}); \\\n")
            impl_h.write(f"    }}\n")

        if self.author:
            impl_hpp = self.files[impl_hpp_name]
            impl_hpp.include(*cpp_param_headers, *cpp_return_headers)
            impl_hpp.write(f"#define TH_EXPORT_CPP_API_{func_name}(_func) \\\n")
            impl_hpp.write(f"    TH_STATIC_ASSERT(TH_IS_SAME(TH_TYPEOF(_func), {cpp_return_type} ({cpp_params_str})), \\\n")
            impl_hpp.write(f"        \"'\" #_func \"' is incompatible with '{cpp_return_type} {cpp_func_name}({cpp_params_str})'\"); \\\n")
            impl_hpp.write(f"    {abi_return_type} {abi_func_name}({abi_params_str}) {{ \\\n")
            impl_hpp.write(f"        return {return_into_abi}(_func({args_from_abi_str})); \\\n")
            impl_hpp.write(f"    }}\n")

    def visit_Struct(self, node: ast.Struct):
        struct_name = node.name.text

        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        struct_basename = basename + "." + struct_name
        struct_h_name = struct_basename + ".abi.h"
        struct_hpp_name = struct_basename + ".abi.hpp"

        namespace = "::".join(self.pktupl)

        abi_struct_name = "__" + "__".join(self.pktupl) + "__" + struct_name
        cpp_struct_type = "::" + "::".join(self.pktupl) + "::" + struct_name
        abi_struct_type = "__" + "__".join(self.pktupl) + "__" + struct_name

        attr_names = []
        cpp_attr_types = []
        abi_attr_types = []
        cpp_attr_headers = []
        abi_attr_headers = []
        for field in node.fields:
            abi_attr_type, abi_attr_header = self.visit(field.type, cpp=False)
            cpp_attr_type, cpp_attr_header = self.visit(field.type, cpp=True)
            attr_name = field.name.text
            attr_names.append(attr_name)
            cpp_attr_headers.append(cpp_attr_header)
            abi_attr_headers.append(abi_attr_header)
            cpp_attr_types.append(cpp_attr_type)
            abi_attr_types.append(abi_attr_type)

        if self.author or self.user:
            struct_h = self.files.setdefault(struct_h_name, File(is_header=True))
            struct_h.include("taihe/common.h")
            struct_h.include(*abi_attr_headers)
            struct_h.write(f"typedef struct {abi_struct_name} {{\n")
            for abi_attr_type, attr_name in zip(abi_attr_types, attr_names, strict=True):
                struct_h.write(f"    {abi_attr_type} {attr_name};\n")
            struct_h.write(f"}} {abi_struct_name};\n")

        if self.author or self.user:
            abi_h = self.files[abi_h_name]
            abi_h.include(struct_h_name)

        if self.author or self.user:
            struct_hpp = self.files.setdefault(struct_hpp_name, File(is_header=True))
            struct_hpp.include("taihe/common.hpp")
            struct_hpp.include(*cpp_attr_headers)
            struct_hpp.include(struct_h_name)
            struct_hpp.write(f"namespace {namespace} {{\n")
            struct_hpp.write(f"struct {struct_name} {{\n")
            for cpp_attr_type, attr_name in zip(cpp_attr_types, attr_names, strict=True):
                struct_hpp.write(f"    {cpp_attr_type} {attr_name};\n")
            struct_hpp.write(f"}};\n")
            struct_hpp.write(f"}}\n")

        if self.author or self.user:
            struct_hpp.write(f"template<>\n")
            struct_hpp.write(f"inline {abi_struct_type} taihe::core::into_abi(std::add_rvalue_reference_t<{cpp_struct_type}> _val) {{\n")
            struct_hpp.write(f"    return {{\n")
            for abi_attr_type, cpp_attr_type, attr_name in zip(abi_attr_types, cpp_attr_types, attr_names, strict=True):
                struct_hpp.write(f"        taihe::core::into_abi<{cpp_attr_type}, {abi_attr_type}>(static_cast<std::add_rvalue_reference_t<{cpp_attr_type}>>(_val.{attr_name})),\n")
            struct_hpp.write(f"    }};\n")
            struct_hpp.write(f"}}\n")
            struct_hpp.write(f"template<>\n")
            struct_hpp.write(f"inline {cpp_struct_type} taihe::core::from_abi(std::add_rvalue_reference_t<{abi_struct_type}> _val) {{\n")
            struct_hpp.write(f"    return {{\n")
            for abi_attr_type, cpp_attr_type, attr_name in zip(abi_attr_types, cpp_attr_types, attr_names, strict=True):
                struct_hpp.write(f"        taihe::core::from_abi<{cpp_attr_type}, {abi_attr_type}>(static_cast<std::add_rvalue_reference_t<{abi_attr_type}>>(_val.{attr_name})),\n")
            struct_hpp.write(f"    }};\n")
            struct_hpp.write(f"}}\n")
            struct_hpp.write(f"template<>\n")
            struct_hpp.write(f"inline {abi_struct_type} *taihe::core::into_abi(std::add_rvalue_reference_t<{cpp_struct_type} &> _val) {{\n")
            struct_hpp.write(f"    return reinterpret_cast<{abi_struct_type} *>(&_val);\n")
            struct_hpp.write(f"}}\n")
            struct_hpp.write(f"template<>\n")
            struct_hpp.write(f"inline {cpp_struct_type} &taihe::core::from_abi(std::add_rvalue_reference_t<{abi_struct_type} *> _val) {{\n")
            struct_hpp.write(f"    return reinterpret_cast<{cpp_struct_type} &>(*_val);\n")
            struct_hpp.write(f"}}\n")
            struct_hpp.write(f"template<>\n")
            struct_hpp.write(f"inline {abi_struct_type} const *taihe::core::into_abi(std::add_rvalue_reference_t<{cpp_struct_type} const &> _val) {{\n")
            struct_hpp.write(f"    return reinterpret_cast<{abi_struct_type} const *>(&_val);\n")
            struct_hpp.write(f"}}\n")
            struct_hpp.write(f"template<>\n")
            struct_hpp.write(f"inline {cpp_struct_type} const &taihe::core::from_abi(std::add_rvalue_reference_t<{abi_struct_type} const *> _val) {{\n")
            struct_hpp.write(f"    return reinterpret_cast<{cpp_struct_type} const &>(*_val);\n")
            struct_hpp.write(f"}}\n")

        if self.user:
            abi_hpp = self.files[abi_hpp_name]
            abi_hpp.include(struct_hpp_name)

    def visit_Enum(self, node: ast.Enum):
        enum_name = node.name.text

        basename = ".".join(self.pktupl)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        enum_basename = basename + "." + enum_name
        enum_h_name = enum_basename + ".abi.h"
        enum_hpp_name = enum_basename + ".abi.hpp"

        namespace = "::".join(self.pktupl)

        abi_enum_name = "__" + "__".join(self.pktupl) + "__" + enum_name
        cpp_enum_type = "::" + "::".join(self.pktupl) + "::" + enum_name
        abi_enum_type = "__" + "__".join(self.pktupl) + "__" + enum_name

        abi_f_names = []
        field_names = []
        vals = []
        for field in node.fields:
            assert isinstance(field.expr, ast.IntLiteralExpr)
            field_name = field.name.text
            abi_field_name = "__" + "__".join(self.pktupl) + "__" + enum_name + "__" + field_name
            val = int(field.expr.val.text)
            abi_f_names.append(abi_field_name)
            field_names.append(field_name)
            vals.append(val)

        if self.author or self.user:
            enum_h = self.files.setdefault(enum_h_name, File(is_header=True))
            enum_h.include("taihe/common.h")
            enum_h.write(f"typedef enum {abi_enum_name} {{\n")
            for abi_field_name, val in zip(abi_f_names, vals, strict=True):
                enum_h.write(f"    {abi_field_name} = {val},\n")
            enum_h.write(f"}} {abi_enum_name};\n")

        if self.author or self.user:
            abi_h = self.files[abi_h_name]
            abi_h.include(enum_h_name)

        if self.author or self.user:
            enum_hpp = self.files.setdefault(enum_hpp_name, File(is_header=True))
            enum_hpp.include("taihe/common.hpp")
            enum_hpp.include(enum_h_name)
            enum_hpp.write(f"namespace {namespace} {{\n")
            enum_hpp.write(f"enum class {enum_name} {{\n")
            for field_name, val in zip(field_names, vals, strict=True):
                enum_hpp.write(f"    {field_name} = {val},\n")
            enum_hpp.write(f"}};\n")
            enum_hpp.write(f"}}\n")
            enum_hpp.write(f"template<>\n")
            enum_hpp.write(f"inline {abi_enum_type} taihe::core::into_abi(std::add_rvalue_reference_t<{cpp_enum_type}> _val) {{\n")
            enum_hpp.write(f"    return static_cast<{abi_enum_type}>(_val);\n")
            enum_hpp.write(f"}}\n")
            enum_hpp.write(f"template<>\n")
            enum_hpp.write(f"inline {cpp_enum_type} taihe::core::from_abi(std::add_rvalue_reference_t<{abi_enum_type}> _val) {{\n")
            enum_hpp.write(f"    return static_cast<{cpp_enum_type}>(_val);\n")
            enum_hpp.write(f"}}\n")

        if self.user:
            abi_hpp = self.files[abi_hpp_name]
            abi_hpp.include(enum_hpp_name)
