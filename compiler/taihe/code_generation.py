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


def get_type_infos(
    symbol_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]],
    node: ast.Type,
    mutable: bool | None = None,  # None: not param, False: immutable param, True: mutable param
) -> tuple[
    tuple[str, str | None],  # abi typename and header
    tuple[str, str | None],  # cpp typename and header
]:
    if isinstance(node, ast.PrimitiveType):
        text = node.name.text
        type = {
            "bool": "bool",
            "f32": "float",
            "f64": "double",
            "i8": "int8_t",
            "i16": "int16_t",
            "i32": "int32_t",
            "i64": "int64_t",
            "u8": "uint8_t",
            "u16": "uint16_t",
            "u32": "uint32_t",
            "u64": "uint64_t",
        }.get(text)
        if type is not None:
            return (type, None), (type, None)
        if node.name.text == "String":
            return (
                ("struct TString*", "taihe/string.abi.h"),
                ("taihe::core::string_view" if mutable is not None else "taihe::core::string", "core/string.hpp"),
            )
        raise NotImplementedError

    if isinstance(node, ast.UserType):
        pkname = tuple(token.text for token in node.pkname)
        text = node.name.text
        basename = ".".join(pkname) + "." + text
        cpp_type = "::" + "::".join(pkname) + "::" + text
        cpp_header = basename + ".abi.hpp"
        abi_type = "__" + "__".join(pkname) + "__" + text
        abi_header = basename + ".abi.h"
        target = symbol_tables[pkname][text][0]
        if isinstance(target, ast.Struct):
            if mutable is True:
                cpp_type += " &"
                abi_type += " *"
            if mutable is False:
                cpp_type += " const&"
                abi_type += " const*"
            return (abi_type, abi_header), (cpp_type, cpp_header)
        if isinstance(target, ast.Enum):
            return (abi_type, abi_header), (cpp_type, cpp_header)
        raise NotImplementedError

    raise NotImplementedError


def get_qualified_type_infos(
    symbol_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]],
    node: ast.QualifiedType,
) -> tuple[
    tuple[str, str | None],
    tuple[str, str | None],
]:
    return get_type_infos(symbol_tables, node.type, node.mut is not None)


def get_dup_and_drop(
    symbol_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]],
    node: ast.Type,
) -> tuple[str, str]:
    if isinstance(node, ast.PrimitiveType):
        if node.name.text in ("bool", "f32", "f64", "i8", "i16", "i32", "i64", "u8", "u16", "u32", "u64"):
            return "", ""
        if node.name.text == "String":
            return "tstr_dup", "tstr_drop"
        raise NotImplementedError

    if isinstance(node, ast.UserType):
        pkname = tuple(token.text for token in node.pkname)
        name = node.name.text
        target = symbol_tables[pkname][name][0]
        if isinstance(target, ast.Struct | ast.Interface | ast.Runtimeclass):
            return (
                "__" + "__".join(pkname) + "__" + name + "__dup",
                "__" + "__".join(pkname) + "__" + name + "__drop",
            )
        if isinstance(target, ast.Enum):
            return "", ""
        raise NotImplementedError

    raise NotImplementedError


class CodeGenerator(Visitor):
    def __init__(
        self,
        symbol_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]],
        pkname: tuple[str, ...],
        author: bool,
        user: bool,
    ) -> None:
        self.symbol_tables = symbol_tables
        self.pkname = pkname
        self.author = author
        self.user = user
        self.files: dict[str, File] = {}

    def generic_visit(self, node) -> None:
        raise NotImplementedError

    def visit_Spec(self, node: ast.Spec) -> None:
        basename = ".".join(self.pkname)
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

    def visit_Function(self, node: ast.Function) -> None:
        func_name = node.name.text

        basename = ".".join(self.pkname)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        impl_h_name = basename + ".impl.h"
        impl_hpp_name = basename + ".impl.hpp"

        namespace = "::".join(self.pkname)

        abi_func_name = "__" + "__".join(self.pkname) + "__" + func_name
        cpp_func_name = "::" + "::".join(self.pkname) + "::" + func_name

        args = []
        cpp_param_headers = []
        abi_param_headers = []
        args_from_abi = []
        args_into_abi = []
        cpp_params = []
        abi_params = []
        for param in node.parameters:
            param_name = param.name.text
            (
                (abi_param_type, abi_param_header),
                (cpp_param_type, cpp_param_header),
            ) = get_qualified_type_infos(self.symbol_tables, param.param_type)
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
            (
                (abi_return_type, abi_return_header),
                (cpp_return_type, cpp_return_header),
            ) = get_type_infos(self.symbol_tables, node.return_types[0])
            return_from_abi = f"taihe::core::from_abi<{cpp_return_type}, {abi_return_type}>"
            return_into_abi = f"taihe::core::into_abi<{cpp_return_type}, {abi_return_type}>"
            cpp_return_headers.append(cpp_return_header)
            abi_return_headers.append(abi_return_header)
        else:
            cpp_return_parts = []
            abi_return_parts = []
            for return_type in node.return_types:
                (
                    (abi_return_part, abi_return_header),
                    (cpp_return_part, cpp_return_header),
                ) = get_type_infos(self.symbol_tables, return_type)
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

    def visit_Struct(self, node: ast.Struct) -> None:
        struct_name = node.name.text

        basename = ".".join(self.pkname)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        struct_basename = basename + "." + struct_name
        struct_h_name = struct_basename + ".abi.h"
        struct_hpp_name = struct_basename + ".abi.hpp"

        namespace = "::".join(self.pkname)

        abi_struct_name = "__" + "__".join(self.pkname) + "__" + struct_name
        cpp_struct_type = "::" + "::".join(self.pkname) + "::" + struct_name
        abi_struct_type = "__" + "__".join(self.pkname) + "__" + struct_name
        abi_struct_dupl_method = f"{abi_struct_name}__dup"
        abi_struct_drop_method = f"{abi_struct_name}__drop"

        attr_names = []
        attr_dupl_methods = []
        attr_drop_methods = []
        cpp_attr_types = []
        abi_attr_types = []
        cpp_attr_headers = []
        abi_attr_headers = []
        for field in node.fields:
            attr_name = field.name.text
            (
                (abi_attr_type, abi_attr_header),
                (cpp_attr_type, cpp_attr_header),
            ) = get_type_infos(self.symbol_tables, field.type)
            attr_dupl_method, attr_drop_method = get_dup_and_drop(self.symbol_tables, field.type)
            attr_dupl_methods.append(attr_dupl_method)
            attr_drop_methods.append(attr_drop_method)
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
            struct_h.write(f"inline {abi_struct_type} {abi_struct_dupl_method}({abi_struct_type} _val) {{\n")
            struct_h.write(f"    {abi_struct_type} _dup = {{\n")
            for attr_dupl_method, attr_name in zip(attr_dupl_methods, attr_names, strict=True):
                struct_h.write(f"        {attr_dupl_method}(_val.{attr_name}),\n")
            struct_h.write(f"    }};\n")
            struct_h.write(f"    return _dup;\n")
            struct_h.write(f"}}\n")
            struct_h.write(f"inline void {abi_struct_drop_method}({abi_struct_type} _val) {{\n")
            for attr_drop_method, attr_name in zip(attr_drop_methods, attr_names, strict=True):
                if len(attr_drop_method):  # -Wunused-value
                    struct_h.write(f"    {attr_drop_method}(_val.{attr_name});\n")
            struct_h.write(f"}}\n")

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

    def visit_Enum(self, node: ast.Enum) -> None:
        enum_name = node.name.text

        basename = ".".join(self.pkname)
        abi_h_name = basename + ".abi.h"
        abi_hpp_name = basename + ".abi.hpp"
        enum_basename = basename + "." + enum_name
        enum_h_name = enum_basename + ".abi.h"
        enum_hpp_name = enum_basename + ".abi.hpp"

        namespace = "::".join(self.pkname)

        abi_enum_name = "__" + "__".join(self.pkname) + "__" + enum_name
        cpp_enum_type = "::" + "::".join(self.pkname) + "::" + enum_name
        abi_enum_type = "__" + "__".join(self.pkname) + "__" + enum_name

        abi_f_names = []
        field_names = []
        vals = []
        for field in node.fields:
            assert isinstance(field.expr, ast.IntLiteralExpr)
            field_name = field.name.text
            abi_field_name = "__" + "__".join(self.pkname) + "__" + enum_name + "__" + field_name
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
