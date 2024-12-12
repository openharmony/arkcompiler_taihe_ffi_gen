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
    # pyre-fixme[11]: Annotation `SpecField` is not defined as a type.
    symbol_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]],
    # pyre-fixme[11]: Annotation `Type` is not defined as a type.
    node: ast.Type,
    mutable: (
        bool | None
    ) = None,  # None: not param, False: immutable param, True: mutable param
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
                (
                    (
                        "taihe::core::string_view"
                        if mutable is not None
                        else "taihe::core::string"
                    ),
                    "core/string.hpp",
                ),
            )
        raise NotImplementedError

    if isinstance(node, ast.UserType):
        pkname = tuple(token.text for token in node.pkname)
        text = node.name.text
        cpp_type = get_cpp_name(pkname, text)
        abi_type = get_abi_name(pkname, text)
        _, _, abi_header, cpp_header = get_file_names(pkname, text)
        target = symbol_tables[pkname][text][0]
        if isinstance(target, ast.Struct):
            abi_type = get_mutable_name(abi_type, mutable, "abi")
            cpp_type = get_mutable_name(cpp_type, mutable, "cpp")
            return (abi_type, abi_header), (cpp_type, cpp_header)
        if isinstance(target, ast.Enum):
            return (abi_type, abi_header), (cpp_type, cpp_header)
        raise NotImplementedError

    raise NotImplementedError


def get_dup_and_drop(
    symbol_tables: dict[tuple[str, ...], dict[str, list[ast.SpecField]]],
    node: ast.Type,
) -> tuple[str, str]:
    if isinstance(node, ast.PrimitiveType):
        if node.name.text in (
            "bool",
            "f32",
            "f64",
            "i8",
            "i16",
            "i32",
            "i64",
            "u8",
            "u16",
            "u32",
            "u64",
        ):
            return "", ""
        if node.name.text == "String":
            return "tstr_dup", "tstr_drop"
        raise NotImplementedError

    if isinstance(node, ast.UserType):
        pkname = tuple(token.text for token in node.pkname)
        name = node.name.text
        target = symbol_tables[pkname][name][0]
        if isinstance(target, ast.Struct | ast.Interface):
            return (
                get_abi_name(pkname, name, suffix="__dup"),
                get_abi_name(pkname, name, suffix="__drop"),
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
        pass

    def visit_Spec(self, node: ast.Spec) -> None:
        write_basic_info_in_files(self)

        for field in node.fields:
            self.visit(field)

    def visit_Function(self, node: ast.Function) -> None:
        func_name = node.name.text

        (
            args_str,
            args_from_abi_str,
            args_into_abi_str,
            abi_params_str,
            cpp_params_str,
            abi_param_headers,
            cpp_param_headers,
        ) = get_function_params(self, node)
        (
            abi_return_type,
            cpp_return_type,
            return_from_abi,
            return_into_abi,
            abi_return_headers,
            cpp_return_headers,
        ) = get_function_returns(self, node)
        abi_headers = abi_param_headers + abi_return_headers
        cpp_headers = cpp_param_headers + cpp_return_headers
        write_function_in_files(
            self,
            func_name,
            abi_headers,
            cpp_headers,
            abi_return_type,
            abi_params_str,
            cpp_return_type,
            cpp_params_str,
            return_from_abi,
            return_into_abi,
            args_into_abi_str,
            args_from_abi_str,
            args_str,
        )

    def visit_Struct(self, node: ast.Struct) -> None:
        struct_name = node.name.text
        (
            abi_attr_headers,
            cpp_attr_headers,
            attr_dupl_methods,
            attr_drop_methods,
            abi_attr_types,
            cpp_attr_types,
            attr_names,
        ) = get_struct_field(self, node)
        write_struct_in_files(
            self,
            struct_name,
            abi_attr_headers,
            cpp_attr_headers,
            attr_dupl_methods,
            attr_drop_methods,
            abi_attr_types,
            cpp_attr_types,
            attr_names,
        )

    def visit_Enum(self, node: ast.Enum) -> None:
        enum_name = node.name.text
        abi_f_names, field_names, vals = get_enum_field(self, node)
        write_enum_in_files(self, enum_name, abi_f_names, field_names, vals)


def get_file_names(
    pkname: tuple[str, ...], type_name: str | None
) -> tuple[str, str, str, str]:
    basename = ".".join(pkname)
    abi_h_name = basename + ".abi.h"
    abi_hpp_name = basename + ".abi.hpp"
    if type_name is not None:
        type_basename = basename + "." + type_name
        type_h_name = type_basename + ".abi.h"
        type_hpp_name = type_basename + ".abi.hpp"
        return abi_h_name, abi_hpp_name, type_h_name, type_hpp_name
    else:
        impl_h_name = basename + ".impl.h"
        impl_hpp_name = basename + ".impl.hpp"
        return abi_h_name, abi_hpp_name, impl_h_name, impl_hpp_name


def get_cpp_name(
    pkname: tuple[str, ...],
    type_name: str | None,
    prefix: str = "::",
    suffix: str = "",
) -> str:
    if type_name is not None:
        cpp_name = prefix + "::".join(pkname) + "::" + type_name + suffix
    else:
        cpp_name = "::".join(pkname)
    return cpp_name


def get_abi_name(
    pkname: tuple[str, ...],
    type_name: str,
    prefix: str = "__",
    suffix: str = "",
) -> str:
    abi_name = prefix + "__".join(pkname) + "__" + type_name + suffix
    return abi_name


def get_mutable_name(name: str, mutable: bool | None, type: str) -> str:
    if mutable is True and type == "cpp":
        name += " &"
    if mutable is False and type == "cpp":
        name += " const&"
    if mutable is True and type == "abi":
        name += " *"
    if mutable is False and type == "abi":
        name += " const*"
    return name


def write_class_declaration(
    file: File,
    type: str,
    type_name: str,
    attr_types: list[str],
    attr_vals: list[int] | list[str],
):
    file.include("taihe/common.h")
    file.write(f"typedef {type} {type_name} {{\n")
    if type == "enum":
        for attr_type, attr_val in zip(attr_types, attr_vals, strict=True):
            file.write(f"    {attr_type} = {attr_val},\n")
    else:
        for attr_type, attr_val in zip(attr_types, attr_vals, strict=True):
            file.write(f"    {attr_type} {attr_val};\n")
    file.write(f"}} {type_name};\n")


def write_class_define(
    file: File,
    h_file_name: str,
    namespace: str,
    type: str,
    type_name: str,
    attr_types: list[str],
    attr_vals: list[int] | list[str],
):
    file.include("taihe/common.hpp")
    file.include(h_file_name)
    file.write(f"namespace {namespace} {{\n")
    if type == "enum":
        file.write(f"{type} class {type_name} {{\n")
        for attr_type, attr_val in zip(attr_types, attr_vals, strict=True):
            file.write(f"    {attr_type} = {attr_val},\n")
    else:
        file.write(f"struct {type_name} {{\n")
        for attr_type, attr_val in zip(attr_types, attr_vals, strict=True):
            file.write(f"    {attr_type} {attr_val};\n")
    file.write(f"}};\n")
    file.write(f"}}\n")


def write_api_define(
    file: File,
    type: str,
    func_name: str,
    return_type: str,
    params_str: str,
    use_func_name: str,
    abi_return_type: str,
    abi_func_name: str,
    abi_params_str: str,
    return_into_abi: str,
    args_str: str,
):
    content = f"""#define TH_EXPORT_{type}_API_{func_name}(_func) \\
    TH_STATIC_ASSERT(TH_IS_SAME(TH_TYPEOF(_func), {return_type} ({params_str})), \\
        \"'\" #_func \"' is incompatible with '{return_type} {use_func_name}({params_str})'\"); \\
    {abi_return_type} {abi_func_name}({abi_params_str}) {{ \\
        return {return_into_abi}(_func({args_str})); \\
    }}
"""
    file.write(content)


def write_inline_function_struct(
    file: File,
    mutable: str,
    parm_type: str,
    return_type: str,
    function_name: str,
) -> None:
    parm_mutable = mutable[:-1] + "&" if mutable[-1] == "*" else mutable[:-1] + "*"
    content = f"""template<>
inline {return_type} {mutable}taihe::core::{function_name}(std::add_rvalue_reference_t<{parm_type} {parm_mutable}> _val) {{
    return reinterpret_cast<{return_type} {mutable}>({parm_mutable[-1]}_val);
}}
"""
    file.write(content)


def write_inline_function_struct_detail(
    file: File,
    parm_type: str,
    return_type: str,
    function_name: str,
    abi_attr_types: list[str],
    cpp_attr_types: list[str],
    attr_names: list[str],
) -> None:
    file.write(f"template<>\n")
    file.write(
        f"inline {return_type} taihe::core::{function_name}(std::add_rvalue_reference_t<{parm_type}> _val) {{\n"
    )
    file.write(f"    return {{\n")
    if function_name == "from_abi":
        for abi_attr_type, cpp_attr_type, attr_name in zip(
            abi_attr_types, cpp_attr_types, attr_names, strict=True
        ):
            file.write(
                f"        taihe::core::{function_name}<{cpp_attr_type}, {abi_attr_type}>(static_cast<std::add_rvalue_reference_t<{abi_attr_type}>>(_val.{attr_name})),\n"
            )
    else:
        for abi_attr_type, cpp_attr_type, attr_name in zip(
            abi_attr_types, cpp_attr_types, attr_names, strict=True
        ):
            file.write(
                f"        taihe::core::{function_name}<{cpp_attr_type}, {abi_attr_type}>(static_cast<std::add_rvalue_reference_t<{cpp_attr_type}>>(_val.{attr_name})),\n"
            )
    file.write(f"    }};\n")
    file.write(f"}}\n")


def write_inline_function_func(
    file: File,
    parm_type: str,
    return_type: str,
    function_name: str,
    cpp_return_parts: list[str],
    abi_return_parts: list[str],
) -> None:
    file.write(f"template<>\n")
    file.write(
        f"inline {return_type} taihe::core::{function_name}(std::add_rvalue_reference_t<{parm_type}> _val) {{\n"
    )
    file.write(f"    return {{\n")
    if function_name == "from_abi":
        for i, (cpp_return_part, abi_return_part) in enumerate(
            zip(cpp_return_parts, abi_return_parts, strict=True)
        ):
            file.write(
                f"        taihe::core::{function_name}<{cpp_return_part}, {abi_return_part}>(static_cast<std::add_rvalue_reference_t<{abi_return_part}>>(_val._{i})), \n"
            )
    else:
        for i, (cpp_return_part, abi_return_part) in enumerate(
            zip(cpp_return_parts, abi_return_parts, strict=True)
        ):
            file.write(
                f"        taihe::core::{function_name}<{cpp_return_part}, {abi_return_part}>(static_cast<std::add_rvalue_reference_t<{cpp_return_part}>>(std::get<{i}>(_val))), \n"
            )
    file.write(f"    }};\n")
    file.write(f"}}\n")


def write_inline_function_enum(
    file: File, parm_type: str, return_type: str, function_name: str
) -> None:
    content = f"""template<>
inline {return_type} taihe::core::{function_name}(std::add_rvalue_reference_t<{parm_type}> _val) {{
    return static_cast<{return_type}>(_val);
}}
"""
    file.write(content)


def get_enum_field(self, node: ast.Enum) -> tuple[list[str], list[str], list[int]]:
    enum_name = node.name.text
    abi_f_names = []
    field_names = []
    vals = []
    for field in node.fields:
        assert isinstance(field.expr, ast.IntLiteralExpr)
        field_name = field.name.text
        abi_field_name = get_abi_name(self.pkname, enum_name, suffix="__" + field_name)
        val = int(field.expr.val.text)
        abi_f_names.append(abi_field_name)
        field_names.append(field_name)
        vals.append(val)
    return abi_f_names, field_names, vals


def write_enum_in_files(
    self,
    enum_name: str,
    abi_f_names: list[str],
    field_names: list[str],
    vals: list[int],
):
    abi_h_name, abi_hpp_name, enum_h_name, enum_hpp_name = get_file_names(
        self.pkname, enum_name
    )
    namespace = get_cpp_name(self.pkname, None)
    abi_enum_name = get_abi_name(self.pkname, enum_name)
    cpp_enum_type = get_cpp_name(self.pkname, enum_name)
    abi_enum_type = get_abi_name(self.pkname, enum_name)

    if self.author or self.user:
        enum_h = self.files.setdefault(enum_h_name, File(is_header=True))
        write_class_declaration(enum_h, "enum", abi_enum_name, abi_f_names, vals)

        abi_h = self.files[abi_h_name]
        abi_h.include(enum_h_name)

        enum_hpp = self.files.setdefault(enum_hpp_name, File(is_header=True))
        write_class_define(
            enum_hpp, enum_h_name, namespace, "enum", enum_name, field_names, vals
        )
        write_inline_function_enum(enum_hpp, cpp_enum_type, abi_enum_type, "into_abi")
        write_inline_function_enum(enum_hpp, abi_enum_type, cpp_enum_type, "from_abi")

    if self.user:
        abi_hpp = self.files[abi_hpp_name]
        abi_hpp.include(enum_hpp_name)


def get_struct_field(
    self, node: ast.Struct
) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str], list[str]]:
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
        attr_dupl_method, attr_drop_method = get_dup_and_drop(
            self.symbol_tables, field.type
        )
        attr_dupl_methods.append(attr_dupl_method)
        attr_drop_methods.append(attr_drop_method)
        attr_names.append(attr_name)
        cpp_attr_headers.append(cpp_attr_header)
        abi_attr_headers.append(abi_attr_header)
        cpp_attr_types.append(cpp_attr_type)
        abi_attr_types.append(abi_attr_type)
    return (
        abi_attr_headers,
        cpp_attr_headers,
        attr_dupl_methods,
        attr_drop_methods,
        abi_attr_types,
        cpp_attr_types,
        attr_names,
    )


def write_struct_in_files(
    self,
    struct_name: str,
    abi_headers: list[str],
    cpp_headers: list[str],
    attr_dupl_methods: list[str],
    attr_drop_methods: list[str],
    abi_attr_types: list[str],
    cpp_attr_types: list[str],
    attr_names: list[str],
):
    abi_h_name, abi_hpp_name, struct_h_name, struct_hpp_name = get_file_names(
        self.pkname, struct_name
    )
    namespace = get_cpp_name(self.pkname, None)
    abi_struct_name = get_abi_name(self.pkname, struct_name)
    cpp_struct_type = get_cpp_name(self.pkname, struct_name)
    abi_struct_type = get_abi_name(self.pkname, struct_name)
    abi_struct_dupl_method = get_abi_name(self.pkname, struct_name, suffix="__dup")
    abi_struct_drop_method = get_abi_name(self.pkname, struct_name, suffix="__drop")

    if self.author or self.user:
        struct_h = self.files.setdefault(struct_h_name, File(is_header=True))
        struct_h.include(*abi_headers)
        write_class_declaration(
            struct_h, "struct", abi_struct_name, abi_attr_types, attr_names
        )

        struct_h.write(
            f"inline {abi_struct_type} {abi_struct_dupl_method}({abi_struct_type} _val) {{\n"
        )
        struct_h.write(f"    {abi_struct_type} _dup = {{\n")
        for attr_dupl_method, attr_name in zip(
            attr_dupl_methods, attr_names, strict=True
        ):
            struct_h.write(f"        {attr_dupl_method}(_val.{attr_name}),\n")
        struct_h.write(f"    }};\n")
        struct_h.write(f"    return _dup;\n")
        struct_h.write(f"}}\n")
        struct_h.write(
            f"inline void {abi_struct_drop_method}({abi_struct_type} _val) {{\n"
        )
        for attr_drop_method, attr_name in zip(
            attr_drop_methods, attr_names, strict=True
        ):
            if len(attr_drop_method):  # -Wunused-value
                struct_h.write(f"    {attr_drop_method}(_val.{attr_name});\n")
        struct_h.write(f"}}\n")

        abi_h = self.files[abi_h_name]
        abi_h.include(struct_h_name)

        struct_hpp = self.files.setdefault(struct_hpp_name, File(is_header=True))
        struct_hpp.include(*cpp_headers)
        write_class_define(
            struct_hpp,
            struct_h_name,
            namespace,
            "struct",
            struct_name,
            cpp_attr_types,
            attr_names,
        )
        write_inline_function_struct_detail(
            struct_hpp,
            cpp_struct_type,
            abi_struct_type,
            "into_abi",
            abi_attr_types,
            cpp_attr_types,
            attr_names,
        )
        write_inline_function_struct_detail(
            struct_hpp,
            abi_struct_type,
            cpp_struct_type,
            "from_abi",
            abi_attr_types,
            cpp_attr_types,
            attr_names,
        )
        write_inline_function_struct(
            struct_hpp, "*", cpp_struct_type, abi_struct_type, "into_abi"
        )
        write_inline_function_struct(
            struct_hpp, "&", abi_struct_type, cpp_struct_type, "from_abi"
        )
        write_inline_function_struct(
            struct_hpp, "const *", cpp_struct_type, abi_struct_type, "into_abi"
        )
        write_inline_function_struct(
            struct_hpp, "const &", abi_struct_type, cpp_struct_type, "from_abi"
        )

    if self.user:
        abi_hpp = self.files[abi_hpp_name]
        abi_hpp.include(struct_hpp_name)


def get_function_params(
    self, node: ast.Function
) -> tuple[str, str, str, str, str, list[str], list[str]]:
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
        ) = get_type_infos(self.symbol_tables, param.param_type)
        args.append(param_name)
        cpp_param_headers.append(cpp_param_header)
        abi_param_headers.append(abi_param_header)
        args_from_abi.append(
            f"taihe::core::from_abi<{cpp_param_type}, {abi_param_type}>(static_cast<std::add_rvalue_reference_t<{abi_param_type}>>({param_name}))"
        )
        args_into_abi.append(
            f"taihe::core::into_abi<{cpp_param_type}, {abi_param_type}>(static_cast<std::add_rvalue_reference_t<{cpp_param_type}>>({param_name}))"
        )
        cpp_params.append(f"{cpp_param_type} {param_name}")
        abi_params.append(f"{abi_param_type} {param_name}")
    args_str = ", ".join(args)
    args_from_abi_str = ", ".join(args_from_abi)
    args_into_abi_str = ", ".join(args_into_abi)
    cpp_params_str = ", ".join(cpp_params)
    abi_params_str = ", ".join(abi_params)
    return (
        args_str,
        args_from_abi_str,
        args_into_abi_str,
        abi_params_str,
        cpp_params_str,
        abi_param_headers,
        cpp_param_headers,
    )


def get_function_returns(
    self, node: ast.Function
) -> tuple[str, str, str, str, list[str], list[str]]:
    func_name = node.name.text
    cpp_return_headers = []
    abi_return_headers = []
    if len(node.returns) == 0:
        cpp_return_type = "void"
        abi_return_type = "void"
        return_from_abi = ""
        return_into_abi = ""
    elif len(node.returns) == 1:
        (
            (abi_return_type, abi_return_header),
            (cpp_return_type, cpp_return_header),
        ) = get_type_infos(self.symbol_tables, node.returns[0].return_type)
        return_from_abi = f"taihe::core::from_abi<{cpp_return_type}, {abi_return_type}>"
        return_into_abi = f"taihe::core::into_abi<{cpp_return_type}, {abi_return_type}>"
        cpp_return_headers.append(cpp_return_header)
        abi_return_headers.append(abi_return_header)
    else:
        cpp_return_parts = []
        abi_return_parts = []
        for ret in node.returns:
            (
                (abi_return_part, abi_return_header),
                (cpp_return_part, cpp_return_header),
            ) = get_type_infos(self.symbol_tables, ret.return_type)
            cpp_return_headers.append(cpp_return_header)
            abi_return_headers.append(abi_return_header)
            cpp_return_parts.append(cpp_return_part)
            abi_return_parts.append(abi_return_part)
        cpp_return_parts_str = ", ".join(cpp_return_parts)
        abi_return_struct_name = get_abi_name(
            self.pkname, func_name, suffix="__return_t"
        )
        abi_return_type = f"struct {abi_return_struct_name}"
        cpp_return_type = f"std::tuple<{cpp_return_parts_str}>"
        return_from_abi = f"taihe::core::from_abi<{cpp_return_type}, {abi_return_type}>"
        return_into_abi = f"taihe::core::into_abi<{cpp_return_type}, {abi_return_type}>"
        write_function_returns_in_files(
            self,
            func_name,
            abi_return_parts,
            cpp_return_parts,
            abi_return_type,
            cpp_return_type,
        )

    return (
        abi_return_type,
        cpp_return_type,
        return_from_abi,
        return_into_abi,
        abi_return_headers,
        cpp_return_headers,
    )


def write_function_returns_in_files(
    self,
    func_name: str,
    abi_return_parts: list[str],
    cpp_return_parts: list[str],
    abi_return_type: str,
    cpp_return_type: str,
):
    abi_h_name, abi_hpp_name, _, impl_hpp_name = get_file_names(self.pkname, None)
    abi_return_struct_name = get_abi_name(self.pkname, func_name, suffix="__return_t")
    if self.author or self.user:
        abi_h = self.files[abi_h_name]
        abi_h.write(f"struct {abi_return_struct_name} {{\n")
        for i, abi_return_part in enumerate(abi_return_parts):
            abi_h.write(f"    {abi_return_part} _{i};\n")
        abi_h.write(f"}};\n")

    if self.user:
        abi_hpp = self.files[abi_hpp_name]
        write_inline_function_func(
            abi_hpp,
            abi_return_type,
            cpp_return_type,
            "from_abi",
            cpp_return_parts,
            abi_return_parts,
        )

    if self.author:
        impl_hpp = self.files[impl_hpp_name]
        write_inline_function_func(
            impl_hpp,
            cpp_return_type,
            abi_return_type,
            "into_abi",
            cpp_return_parts,
            abi_return_parts,
        )


def write_function_in_files(
    self,
    func_name: str,
    abi_headers: list[str],
    cpp_headers: list[str],
    abi_return_type: str,
    abi_params_str: str,
    cpp_return_type: str,
    cpp_params_str: str,
    return_from_abi: str,
    return_into_abi: str,
    args_into_abi_str: str,
    args_from_abi_str: str,
    args_str: str,
):
    namespace = get_cpp_name(self.pkname, None)
    abi_h_name, abi_hpp_name, impl_h_name, impl_hpp_name = get_file_names(
        self.pkname, None
    )
    abi_func_name = get_abi_name(self.pkname, func_name)
    cpp_func_name = get_cpp_name(self.pkname, func_name)

    if self.author or self.user:
        abi_h = self.files[abi_h_name]
        abi_h.include(*abi_headers)
        abi_h.write(f"TH_EXPORT {abi_return_type} {abi_func_name}({abi_params_str});\n")

    if self.user:
        abi_hpp = self.files[abi_hpp_name]
        abi_hpp.include(*cpp_headers)
        content = f"""namespace {namespace} {{
inline {cpp_return_type} {func_name}({cpp_params_str}) {{
return {return_from_abi}({abi_func_name}({args_into_abi_str}));
}}
}}
"""
        abi_hpp.write(content)

    if self.author:
        impl_h = self.files[impl_h_name]
        impl_h.include(*abi_headers)
        write_api_define(
            impl_h,
            "C",
            func_name,
            abi_return_type,
            abi_params_str,
            abi_func_name,
            abi_return_type,
            abi_func_name,
            abi_params_str,
            "",
            args_str,
        )

        impl_hpp = self.files[impl_hpp_name]
        impl_hpp.include(*cpp_headers)
        write_api_define(
            impl_hpp,
            "CPP",
            func_name,
            cpp_return_type,
            cpp_params_str,
            cpp_func_name,
            abi_return_type,
            abi_func_name,
            abi_params_str,
            return_into_abi,
            args_from_abi_str,
        )


def write_basic_info_in_files(self):
    abi_h_name, abi_hpp_name, impl_h_name, impl_hpp_name = get_file_names(
        self.pkname, None
    )

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
