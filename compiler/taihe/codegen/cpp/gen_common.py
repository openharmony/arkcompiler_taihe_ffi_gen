from json import dumps

from taihe.codegen.abi.analyses import (
    EnumAbiInfo,
    IfaceAbiInfo,
    IfaceMethodAbiInfo,
    StructAbiInfo,
    TypeAbiInfo,
    UnionAbiInfo,
)
from taihe.codegen.abi.writer import CHeaderWriter
from taihe.codegen.cpp.analyses import (
    EnumCppInfo,
    IfaceCppInfo,
    IfaceMethodCppInfo,
    PackageCppInfo,
    StructCppInfo,
    TypeCppInfo,
    UnionCppInfo,
)
from taihe.semantics.declarations import (
    EnumDecl,
    IfaceDecl,
    PackageDecl,
    PackageGroup,
    StructDecl,
    UnionDecl,
)
from taihe.semantics.types import (
    ScalarType,
    StringType,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import FileKind, OutputManager


class CppHeadersGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_files(pkg)

    def gen_package_files(self, pkg: PackageDecl):
        pkg_cpp_info = PackageCppInfo.get(self.am, pkg)
        with CHeaderWriter(
            self.om,
            f"include/{pkg_cpp_info.header}",
            FileKind.CPP_HEADER,
        ) as target:
            for enum in pkg.enums:
                enum_abi_info = EnumAbiInfo.get(self.am, enum)
                enum_cpp_info = EnumCppInfo.get(self.am, enum)
                self.gen_enum_decl_file(enum, enum_abi_info, enum_cpp_info)
                self.gen_enum_defn_file(enum, enum_abi_info, enum_cpp_info)
                target.add_include(enum_cpp_info.defn_header)
            for struct in pkg.structs:
                struct_abi_info = StructAbiInfo.get(self.am, struct)
                struct_cpp_info = StructCppInfo.get(self.am, struct)
                self.gen_struct_decl_file(struct, struct_abi_info, struct_cpp_info)
                self.gen_struct_defn_file(struct, struct_abi_info, struct_cpp_info)
                self.gen_struct_impl_file(struct, struct_abi_info, struct_cpp_info)
                target.add_include(struct_cpp_info.impl_header)
            for union in pkg.unions:
                union_abi_info = UnionAbiInfo.get(self.am, union)
                union_cpp_info = UnionCppInfo.get(self.am, union)
                self.gen_union_decl_file(union, union_abi_info, union_cpp_info)
                self.gen_union_defn_file(union, union_abi_info, union_cpp_info)
                self.gen_union_impl_file(union, union_abi_info, union_cpp_info)
                target.add_include(union_cpp_info.impl_header)
            for iface in pkg.interfaces:
                iface_abi_info = IfaceAbiInfo.get(self.am, iface)
                iface_cpp_info = IfaceCppInfo.get(self.am, iface)
                self.gen_iface_decl_file(iface, iface_abi_info, iface_cpp_info)
                self.gen_iface_defn_file(iface, iface_abi_info, iface_cpp_info)
                self.gen_iface_impl_file(iface, iface_abi_info, iface_cpp_info)
                target.add_include(iface_cpp_info.impl_header)

    def gen_enum_decl_file(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumAbiInfo,
        enum_cpp_info: EnumCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{enum_cpp_info.decl_header}",
            FileKind.C_HEADER,
        ) as target:
            target.add_include("taihe/common.hpp")
            with target.indented(
                f"namespace {enum_cpp_info.namespace} {{",
                f"}}",
                indent="",
            ):
                target.writelns(
                    f"struct {enum_cpp_info.name};",
                )
            with target.indented(
                f"namespace taihe {{",
                f"}}",
                indent="",
            ):
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_abi<{enum_cpp_info.full_name}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {enum_abi_info.abi_type};",
                    )
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_param<{enum_cpp_info.full_name}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {enum_cpp_info.full_name};",
                    )

    def gen_enum_defn_file(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumAbiInfo,
        enum_cpp_info: EnumCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{enum_cpp_info.defn_header}",
            FileKind.C_HEADER,
        ) as target:
            target.add_include(enum_cpp_info.decl_header)
            self.gen_enum_defn(
                enum,
                enum_abi_info,
                enum_cpp_info,
                target,
            )
            self.gen_enum_same(
                enum,
                enum_abi_info,
                enum_cpp_info,
                target,
            )
            self.gen_enum_hash(
                enum,
                enum_abi_info,
                enum_cpp_info,
                target,
            )

    def gen_enum_defn(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumAbiInfo,
        enum_cpp_info: EnumCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"namespace {enum_cpp_info.namespace} {{",
            f"}}",
            indent="",
        ):
            ty_cpp_info = TypeCppInfo.get(self.am, enum.ty_ref.resolved_ty)
            target.add_include(*ty_cpp_info.impl_headers)
            with target.indented(
                f"struct {enum_cpp_info.name} {{",
                f"}};",
            ):
                target.writelns(
                    f"public:",
                )
                self.gen_enum_key_type(
                    enum,
                    enum_abi_info,
                    enum_cpp_info,
                    target,
                )
                self.gen_enum_basic_methods(
                    enum,
                    enum_abi_info,
                    enum_cpp_info,
                    target,
                )
                self.gen_enum_key_utils(
                    enum,
                    enum_abi_info,
                    enum_cpp_info,
                    target,
                )
                self.gen_enum_value_utils(
                    enum,
                    enum_abi_info,
                    enum_cpp_info,
                    target,
                )
                target.writelns(
                    f"private:",
                )
                self.gen_enum_properties(
                    enum,
                    enum_abi_info,
                    enum_cpp_info,
                    target,
                )

    def gen_enum_key_type(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumAbiInfo,
        enum_cpp_info: EnumCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"enum class key_t: {enum_abi_info.abi_type} {{",
            f"}};",
        ):
            for item in enum.items:
                target.writelns(
                    f"{item.name},",
                )

    def gen_enum_properties(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumAbiInfo,
        enum_cpp_info: EnumCppInfo,
        target: CHeaderWriter,
    ):
        target.writelns(
            f"key_t key;",
        )

    def gen_enum_basic_methods(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumAbiInfo,
        enum_cpp_info: EnumCppInfo,
        target: CHeaderWriter,
    ):
        # copy constructor
        target.writelns(
            f"{enum_cpp_info.name}({enum_cpp_info.name} const& other) : key(other.key) {{}}",
        )
        # copy assignment
        with target.indented(
            f"{enum_cpp_info.name}& operator=({enum_cpp_info.name} other) {{",
            f"}}",
        ):
            target.writelns(
                f"key = other.key;",
                f"return *this;",
            )

    def gen_enum_key_utils(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumAbiInfo,
        enum_cpp_info: EnumCppInfo,
        target: CHeaderWriter,
    ):
        # constructor
        target.writelns(
            f"{enum_cpp_info.name}(key_t key) : key(key) {{}}",
        )
        # key getter
        with target.indented(
            f"key_t get_key() const {{",
            f"}}",
        ):
            target.writelns(
                f"return key;",
            )
        # validity checker
        with target.indented(
            f"bool is_valid() const {{",
            f"}}",
        ):
            target.writelns(
                f"return static_cast<{enum_abi_info.abi_type}>(key) >= 0 && static_cast<{enum_abi_info.abi_type}>(key) < {len(enum.items)};",
            )

    def gen_enum_value_utils(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumAbiInfo,
        enum_cpp_info: EnumCppInfo,
        target: CHeaderWriter,
    ):
        ty_cpp_info = TypeCppInfo.get(self.am, enum.ty_ref.resolved_ty)
        match enum.ty_ref.resolved_ty:
            case StringType():
                as_owner = "char const*"
                as_param = ty_cpp_info.as_param
            case ScalarType():
                as_owner = ty_cpp_info.as_owner
                as_param = ty_cpp_info.as_param
            case _:
                raise ValueError("invalid enum type")
        # table
        with target.indented(
            f"static constexpr {as_owner} table[] = {{",
            f"}};",
        ):
            for item in enum.items:
                target.writelns(
                    f"{dumps(item.value)},",
                )
        # value getter
        with target.indented(
            f"{as_owner} get_value() const {{",
            f"}}",
        ):
            target.writelns(
                f"return table[static_cast<{enum_abi_info.abi_type}>(key)];",
            )
        # value converter
        with target.indented(
            f"operator {as_owner}() const {{",
            f"}}",
        ):
            target.writelns(
                f"return table[static_cast<{enum_abi_info.abi_type}>(key)];",
            )
        # creator from value
        with target.indented(
            f"static {enum_cpp_info.as_owner} from_value({as_param} value) {{",
            f"}}",
        ):
            for i, item in enumerate(enum.items):
                with target.indented(
                    f"if (value == {dumps(item.value)}) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return {enum_cpp_info.as_owner}(static_cast<key_t>({i}));",
                    )
            target.writelns(
                f"return {enum_cpp_info.as_owner}(static_cast<key_t>(-1));",
            )

    def gen_enum_same(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumAbiInfo,
        enum_cpp_info: EnumCppInfo,
        target: CHeaderWriter,
    ):
        # others
        with target.indented(
            f"namespace {enum_cpp_info.namespace} {{",
            f"}}",
            indent="",
        ):
            with target.indented(
                f"inline bool operator==({enum_cpp_info.as_param} lhs, {enum_cpp_info.as_param} rhs) {{",
                f"}}",
            ):
                target.writelns(
                    f"return lhs.get_key() == rhs.get_key();",
                )

    def gen_enum_hash(
        self,
        enum: EnumDecl,
        enum_abi_info: EnumAbiInfo,
        enum_cpp_info: EnumCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"template<> struct ::std::hash<{enum_cpp_info.full_name}> {{",
            f"}};",
        ):
            with target.indented(
                f"size_t operator()({enum_cpp_info.as_param} val) const {{",
                f"}}",
            ):
                target.writelns(
                    f"return ::std::hash<{enum_abi_info.abi_type}>()(static_cast<{enum_abi_info.abi_type}>(val.get_key()));",
                )

    def gen_union_decl_file(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{union_cpp_info.decl_header}",
            FileKind.C_HEADER,
        ) as target:
            target.add_include("taihe/common.hpp")
            target.add_include(union_abi_info.decl_header)
            with target.indented(
                f"namespace {union_cpp_info.namespace} {{",
                f"}}",
                indent="",
            ):
                target.writelns(
                    f"struct {union_cpp_info.name};",
                )
            with target.indented(
                f"namespace taihe {{",
                f"}}",
                indent="",
            ):
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_abi<{union_cpp_info.as_owner}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {union_abi_info.as_owner};",
                    )
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_abi<{union_cpp_info.as_param}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {union_abi_info.as_param};",
                    )
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_param<{union_cpp_info.as_owner}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {union_cpp_info.as_param};",
                    )

    def gen_union_defn_file(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{union_cpp_info.defn_header}",
            FileKind.CPP_HEADER,
        ) as target:
            target.add_include(union_cpp_info.decl_header)
            target.add_include(union_abi_info.defn_header)
            for field in union.fields:
                if field.ty_ref is None:
                    continue
                type_cpp_info = TypeCppInfo.get(self.am, field.ty_ref.resolved_ty)
                target.add_include(*type_cpp_info.defn_headers)
            self.gen_union_defn(
                union,
                union_abi_info,
                union_cpp_info,
                target,
            )
            self.gen_union_same(
                union,
                union_abi_info,
                union_cpp_info,
                target,
            )
            self.gen_union_hash(
                union,
                union_abi_info,
                union_cpp_info,
                target,
            )

    def gen_union_defn(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"namespace {union_cpp_info.namespace} {{",
            f"}}",
            indent="",
        ):
            with target.indented(
                f"struct {union_cpp_info.name} {{",
                f"}};",
            ):
                target.writelns(
                    f"public:",
                )
                self.gen_union_tag_type(
                    union,
                    union_abi_info,
                    union_cpp_info,
                    target,
                )
                self.gen_union_storage_type(
                    union,
                    union_abi_info,
                    union_cpp_info,
                    target,
                )
                self.gen_union_basic_methods(
                    union,
                    union_abi_info,
                    union_cpp_info,
                    target,
                )
                self.gen_union_utils(
                    union,
                    union_abi_info,
                    union_cpp_info,
                    target,
                )
                self.gen_union_named_utils(
                    union,
                    union_abi_info,
                    union_cpp_info,
                    target,
                )
                target.writelns(
                    f"private:",
                )
                self.gen_union_properties(
                    union,
                    union_abi_info,
                    union_cpp_info,
                    target,
                )

    def gen_union_tag_type(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"enum class tag_t : {union_abi_info.tag_type} {{",
            f"}};",
        ):
            for field in union.fields:
                target.writelns(
                    f"{field.name},",
                )

    def gen_union_storage_type(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"union storage_t {{",
            f"}};",
        ):
            target.writelns(
                f"storage_t() {{}}",
                f"~storage_t() {{}}",
            )
            for field in union.fields:
                if field.ty_ref is None:
                    continue
                type_cpp_info = TypeCppInfo.get(self.am, field.ty_ref.resolved_ty)
                target.writelns(
                    f"{type_cpp_info.as_owner} {field.name};",
                )

    def gen_union_properties(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
        target: CHeaderWriter,
    ):
        target.writelns(
            f"tag_t m_tag;",
            f"storage_t m_data;",
        )

    def gen_union_basic_methods(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
        target: CHeaderWriter,
    ):
        # copy constructor
        with target.indented(
            f"{union_cpp_info.name}({union_cpp_info.name} const& other) : m_tag(other.m_tag) {{",
            f"}}",
        ):
            with target.indented(
                f"switch (m_tag) {{",
                f"}}",
                indent="",
            ):
                for field in union.fields:
                    if field.ty_ref is None:
                        continue
                    with target.indented(
                        f"case tag_t::{field.name}: {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"new (&m_data.{field.name}) decltype(m_data.{field.name})(other.m_data.{field.name});",
                            f"break;",
                        )
                with target.indented(
                    f"default: {{",
                    f"}}",
                ):
                    target.writelns(
                        f"break;",
                    )
        # move constructor
        with target.indented(
            f"{union_cpp_info.name}({union_cpp_info.name}&& other) : m_tag(other.m_tag) {{",
            f"}}",
        ):
            with target.indented(
                f"switch (m_tag) {{",
                f"}}",
                indent="",
            ):
                for field in union.fields:
                    if field.ty_ref is None:
                        continue
                    with target.indented(
                        f"case tag_t::{field.name}: {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"new (&m_data.{field.name}) decltype(m_data.{field.name})(::std::move(other.m_data.{field.name}));",
                            f"break;",
                        )
                with target.indented(
                    f"default: {{",
                    f"}}",
                ):
                    target.writelns(
                        f"break;",
                    )
        # copy assignment
        with target.indented(
            f"{union_cpp_info.name}& operator=({union_cpp_info.name} const& other) {{",
            f"}}",
        ):
            with target.indented(
                f"if (this != &other) {{",
                f"}}",
            ):
                target.writelns(
                    f"::std::destroy_at(this);",
                    f"new (this) {union_cpp_info.name}(other);",
                )
            target.writelns(
                f"return *this;",
            )
        # move assignment
        with target.indented(
            f"{union_cpp_info.name}& operator=({union_cpp_info.name}&& other) {{",
            f"}}",
        ):
            with target.indented(
                f"if (this != &other) {{",
                f"}}",
            ):
                target.writelns(
                    f"::std::destroy_at(this);",
                    f"new (this) {union_cpp_info.name}(::std::move(other));",
                )
            target.writelns(
                f"return *this;",
            )
        # destructor
        with target.indented(
            f"~{union_cpp_info.name}() {{",
            f"}}",
        ):
            with target.indented(
                f"switch (m_tag) {{",
                f"}}",
                indent="",
            ):
                for field in union.fields:
                    if field.ty_ref is None:
                        continue
                    with target.indented(
                        f"case tag_t::{field.name}: {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"::std::destroy_at(&m_data.{field.name});",
                            f"break;",
                        )
                with target.indented(
                    f"default: {{",
                    f"}}",
                ):
                    target.writelns(
                        f"break;",
                    )

    def gen_union_utils(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
        target: CHeaderWriter,
    ):
        # in place constructor
        for field in union.fields:
            if field.ty_ref is None:
                target.writelns(
                    f"{union_cpp_info.name}(::taihe::static_tag_t<tag_t::{field.name}>) : m_tag(tag_t::{field.name}) {{}}",
                )
            else:
                target.writelns(
                    f"template<typename... Args>",
                )
                with target.indented(
                    f"{union_cpp_info.name}(::taihe::static_tag_t<tag_t::{field.name}>, Args&&... args) : m_tag(tag_t::{field.name}) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"new (&m_data.{field.name}) decltype(m_data.{field.name})(::std::forward<Args>(args)...);",
                    )
        # creator
        target.writelns(
            f"template<tag_t tag, typename... Args>",
        )
        with target.indented(
            f"static {union_cpp_info.name} make(Args&&... args) {{",
            f"}}",
        ):
            target.writelns(
                f"return {union_cpp_info.name}(::taihe::static_tag<tag>, ::std::forward<Args>(args)...);",
            )
        # emplacement
        target.writelns(
            f"template<tag_t tag, typename... Args>",
        )
        with target.indented(
            f"{union_cpp_info.name} const& emplace(Args&&... args) {{",
            f"}}",
        ):
            target.writelns(
                f"::std::destroy_at(this);",
                f"new (this) {union_cpp_info.name}(::taihe::static_tag<tag>, ::std::forward<Args>(args)...);",
                f"return *this;",
            )
        # non-const reference getter
        target.writelns(
            f"template<tag_t tag>",
        )
        with target.indented(
            f"auto& get_ref() {{",
            f"}}",
        ):
            for field in union.fields:
                if field.ty_ref is None:
                    continue
                with target.indented(
                    f"if constexpr (tag == tag_t::{field.name}) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return m_data.{field.name};",
                    )
        # non-const pointer getter
        target.writelns(
            f"template<tag_t tag>",
        )
        with target.indented(
            f"auto* get_ptr() {{",
            f"}}",
        ):
            target.writelns(
                f"return m_tag == tag ? &get_ref<tag>() : nullptr;",
            )
        # const reference getter
        target.writelns(
            f"template<tag_t tag>",
        )
        with target.indented(
            f"auto const& get_ref() const {{",
            f"}}",
        ):
            for field in union.fields:
                if field.ty_ref is None:
                    continue
                with target.indented(
                    f"if constexpr (tag == tag_t::{field.name}) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return m_data.{field.name};",
                    )
        # const pointer getter
        target.writelns(
            f"template<tag_t tag>",
        )
        with target.indented(
            f"auto const* get_ptr() const {{",
            f"}}",
        ):
            target.writelns(
                f"return m_tag == tag ? &get_ref<tag>() : nullptr;",
            )
        # tag checker
        target.writelns(
            f"template<tag_t tag>",
        )
        with target.indented(
            f"bool holds() const {{",
            f"}}",
        ):
            target.writelns(
                f"return m_tag == tag;",
            )
        # tag getter
        with target.indented(
            f"tag_t get_tag() const {{",
            f"}}",
        ):
            target.writelns(
                f"return m_tag;",
            )
        # non-const visitor
        target.writelns(
            f"template<typename Visitor>",
        )
        with target.indented(
            f"auto accept_template(Visitor&& visitor) {{",
            f"}}",
        ):
            with target.indented(
                f"switch (m_tag) {{",
                f"}}",
                indent="",
            ):
                for field in union.fields:
                    with target.indented(
                        f"case tag_t::{field.name}: {{",
                        f"}}",
                    ):
                        result = f"::taihe::static_tag<tag_t::{field.name}>"
                        if field.ty_ref:
                            result += f", m_data.{field.name}"
                        target.writelns(
                            f"return visitor({result});",
                        )
        # const visitor
        target.writelns(
            f"template<typename Visitor>",
        )
        with target.indented(
            f"auto accept_template(Visitor&& visitor) const {{",
            f"}}",
        ):
            with target.indented(
                f"switch (m_tag) {{",
                f"}}",
                indent="",
            ):
                for field in union.fields:
                    with target.indented(
                        f"case tag_t::{field.name}: {{",
                        f"}}",
                    ):
                        result = f"::taihe::static_tag<tag_t::{field.name}>"
                        if field.ty_ref:
                            result += f", m_data.{field.name}"
                        target.writelns(
                            f"return visitor({result});",
                        )

    def gen_union_named_utils(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
        target: CHeaderWriter,
    ):
        for field in union.fields:
            # creator
            target.writelns(
                f"template<typename... Args>",
            )
            with target.indented(
                f"static {union_cpp_info.name} make_{field.name}(Args&&... args) {{",
                f"}}",
            ):
                target.writelns(
                    f"return make<tag_t::{field.name}>(::std::forward<Args>(args)...);",
                )
            # emplacement
            target.writelns(
                f"template<typename... Args>",
            )
            with target.indented(
                f"{union_cpp_info.name} const& emplace_{field.name}(Args&&... args) {{",
                f"}}",
            ):
                target.writelns(
                    f"return emplace<tag_t::{field.name}>(::std::forward<Args>(args)...);",
                )
            # tag checker
            with target.indented(
                f"bool holds_{field.name}() const {{",
                f"}}",
            ):
                target.writelns(
                    f"return holds<tag_t::{field.name}>();",
                )
            if field.ty_ref is None:
                continue
            # non-const pointer getter
            with target.indented(
                f"auto* get_{field.name}_ptr() {{",
                f"}}",
            ):
                target.writelns(
                    f"return get_ptr<tag_t::{field.name}>();",
                )
            # const pointer getter
            with target.indented(
                f"auto const* get_{field.name}_ptr() const {{",
                f"}}",
            ):
                target.writelns(
                    f"return get_ptr<tag_t::{field.name}>();",
                )
            # non-const reference getter
            with target.indented(
                f"auto& get_{field.name}_ref() {{",
                f"}}",
            ):
                target.writelns(
                    f"return get_ref<tag_t::{field.name}>();",
                )
            # const reference getter
            with target.indented(
                f"auto const& get_{field.name}_ref() const {{",
                f"}}",
            ):
                target.writelns(
                    f"return get_ref<tag_t::{field.name}>();",
                )
        # non-const visitor
        target.writelns(
            f"template<typename Visitor>",
        )
        with target.indented(
            f"auto accept(Visitor&& visitor) {{",
            f"}}",
        ):
            with target.indented(
                f"switch (m_tag) {{",
                f"}}",
                indent="",
            ):
                for field in union.fields:
                    with target.indented(
                        f"case tag_t::{field.name}: {{",
                        f"}}",
                    ):
                        result = "" if field.ty_ref is None else f"m_data.{field.name}"
                        target.writelns(
                            f"return visitor.{field.name}({result});",
                        )
        # const visitor
        target.writelns(
            f"template<typename Visitor>",
        )
        with target.indented(
            f"auto accept(Visitor&& visitor) const {{",
            f"}}",
        ):
            with target.indented(
                f"switch (m_tag) {{",
                f"}}",
                indent="",
            ):
                for field in union.fields:
                    with target.indented(
                        f"case tag_t::{field.name}: {{",
                        f"}}",
                    ):
                        result = "" if field.ty_ref is None else f"m_data.{field.name}"
                        target.writelns(
                            f"return visitor.{field.name}({result});",
                        )

    def gen_union_same(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"namespace {union_cpp_info.namespace} {{",
            f"}}",
            indent="",
        ):
            with target.indented(
                f"inline bool operator==({union_cpp_info.as_param} lhs, {union_cpp_info.as_param} rhs) {{",
                f"}}",
            ):
                result = "false"
                for field in union.fields:
                    cond = f"lhs.holds_{field.name}() && rhs.holds_{field.name}()"
                    if field.ty_ref:
                        cond = f"{cond} && lhs.get_{field.name}_ref() == rhs.get_{field.name}_ref()"
                    result = f"{result} || ({cond})"
                target.writelns(
                    f"return {result};",
                )

    def gen_union_hash(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"template<> struct ::std::hash<{union_cpp_info.full_name}> {{",
            f"}};",
        ):
            with target.indented(
                f"size_t operator()({union_cpp_info.as_param} val) const {{",
                f"}}",
            ):
                with target.indented(
                    f"switch (val.get_tag()) {{",
                    f"}}",
                    indent="",
                ):
                    for field in union.fields:
                        with target.indented(
                            f"case {union_cpp_info.full_name}::tag_t::{field.name}: {{",
                            f"}}",
                        ):
                            val = "0x9e3779b9 + (seed << 6) + (seed >> 2)"
                            if field.ty_ref:
                                val = f"{val} + ::std::hash<{TypeCppInfo.get(self.am, field.ty_ref.resolved_ty).as_owner}>()(val.get_{field.name}_ref())"
                            val = f"seed ^ ({val})"
                            target.writelns(
                                f"::std::size_t seed = ::std::hash<{union_abi_info.tag_type}>()(static_cast<{union_abi_info.tag_type}>({union_cpp_info.full_name}::tag_t::{field.name}));",
                                f"return {val};",
                            )

    def gen_union_impl_file(
        self,
        union: UnionDecl,
        union_abi_info: UnionAbiInfo,
        union_cpp_info: UnionCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{union_cpp_info.impl_header}",
            FileKind.C_HEADER,
        ) as target:
            target.add_include(union_cpp_info.defn_header)
            target.add_include(union_abi_info.impl_header)
            for field in union.fields:
                if field.ty_ref is None:
                    continue
                type_cpp_info = TypeCppInfo.get(self.am, field.ty_ref.resolved_ty)
                target.add_include(*type_cpp_info.impl_headers)

    def gen_struct_decl_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructAbiInfo,
        struct_cpp_info: StructCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{struct_cpp_info.decl_header}",
            FileKind.C_HEADER,
        ) as target:
            target.add_include("taihe/common.hpp")
            target.add_include(struct_abi_info.decl_header)
            with target.indented(
                f"namespace {struct_cpp_info.namespace} {{",
                f"}}",
                indent="",
            ):
                target.writelns(
                    f"struct {struct_cpp_info.name};",
                )
            with target.indented(
                f"namespace taihe {{",
                f"}}",
                indent="",
            ):
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_abi<{struct_cpp_info.as_owner}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {struct_abi_info.as_owner};",
                    )
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_abi<{struct_cpp_info.as_param}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {struct_abi_info.as_param};",
                    )
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_param<{struct_cpp_info.as_owner}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {struct_cpp_info.as_param};",
                    )

    def gen_struct_defn_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructAbiInfo,
        struct_cpp_info: StructCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{struct_cpp_info.defn_header}",
            FileKind.CPP_HEADER,
        ) as target:
            target.add_include(struct_cpp_info.decl_header)
            target.add_include(struct_abi_info.defn_header)
            for field in struct.fields:
                type_cpp_info = TypeCppInfo.get(self.am, field.ty_ref.resolved_ty)
                target.add_include(*type_cpp_info.defn_headers)
            self.gen_struct_defn(
                struct,
                struct_abi_info,
                struct_cpp_info,
                target,
            )
            self.gen_struct_same(
                struct,
                struct_abi_info,
                struct_cpp_info,
                target,
            )
            self.gen_struct_hash(
                struct,
                struct_abi_info,
                struct_cpp_info,
                target,
            )

    def gen_struct_defn(
        self,
        struct: StructDecl,
        struct_abi_info: StructAbiInfo,
        struct_cpp_info: StructCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"namespace {struct_cpp_info.namespace} {{",
            f"}}",
            indent="",
        ):
            with target.indented(
                f"struct {struct_cpp_info.name} {{",
                f"}};",
            ):
                for field in struct.fields:
                    type_cpp_info = TypeCppInfo.get(self.am, field.ty_ref.resolved_ty)
                    target.writelns(
                        f"{type_cpp_info.as_owner} {field.name};",
                    )

    def gen_struct_same(
        self,
        struct: StructDecl,
        struct_abi_info: StructAbiInfo,
        struct_cpp_info: StructCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"namespace {struct_cpp_info.namespace} {{",
            f"}}",
            indent="",
        ):
            with target.indented(
                f"inline bool operator==({struct_cpp_info.as_param} lhs, {struct_cpp_info.as_param} rhs) {{",
                f"}}",
            ):
                result = "true"
                for field in struct.fields:
                    result = f"{result} && lhs.{field.name} == rhs.{field.name}"
                target.writelns(
                    f"return {result};",
                )

    def gen_struct_hash(
        self,
        struct: StructDecl,
        struct_abi_info: StructAbiInfo,
        struct_cpp_info: StructCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"template<> struct ::std::hash<{struct_cpp_info.full_name}> {{",
            f"}};",
        ):
            with target.indented(
                f"size_t operator()({struct_cpp_info.as_param} val) const {{",
                f"}}",
            ):
                target.writelns(
                    f"::std::size_t seed = 0;",
                )
                for field in struct.fields:
                    target.writelns(
                        f"seed ^= ::std::hash<{TypeCppInfo.get(self.am, field.ty_ref.resolved_ty).as_owner}>()(val.{field.name}) + 0x9e3779b9 + (seed << 6) + (seed >> 2);",
                    )
                target.writelns(
                    f"return seed;",
                )

    def gen_struct_impl_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructAbiInfo,
        struct_cpp_info: StructCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{struct_cpp_info.impl_header}",
            FileKind.C_HEADER,
        ) as target:
            target.add_include(struct_cpp_info.defn_header)
            target.add_include(struct_abi_info.impl_header)
            for field in struct.fields:
                type_cpp_info = TypeCppInfo.get(self.am, field.ty_ref.resolved_ty)
                target.add_include(*type_cpp_info.impl_headers)

    def gen_iface_decl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{iface_cpp_info.decl_header}",
            FileKind.C_HEADER,
        ) as target:
            target.add_include("taihe/object.hpp")
            target.add_include(iface_abi_info.decl_header)
            with target.indented(
                f"namespace {iface_cpp_info.weakspace} {{",
                f"}}",
                indent="",
            ):
                target.writelns(
                    f"struct {iface_cpp_info.weak_name};",
                )
            with target.indented(
                f"namespace {iface_cpp_info.namespace} {{",
                f"}}",
                indent="",
            ):
                target.writelns(
                    f"struct {iface_cpp_info.norm_name};",
                )
            with target.indented(
                f"namespace taihe {{",
                f"}}",
                indent="",
            ):
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_abi<{iface_cpp_info.as_owner}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {iface_abi_info.as_owner};",
                    )
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_abi<{iface_cpp_info.as_param}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {iface_abi_info.as_param};",
                    )
                target.writelns(
                    f"template<>",
                )
                with target.indented(
                    f"struct as_param<{iface_cpp_info.as_owner}> {{",
                    f"}};",
                ):
                    target.writelns(
                        f"using type = {iface_cpp_info.as_param};",
                    )

    def gen_iface_defn_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{iface_cpp_info.defn_header}",
            FileKind.CPP_HEADER,
        ) as target:
            target.add_include(iface_cpp_info.decl_header)
            target.add_include(iface_abi_info.defn_header)
            for ancestor, info in iface_abi_info.ancestor_dict.items():
                if ancestor is iface:
                    continue
                ancestor_cpp_info = IfaceCppInfo.get(self.am, ancestor)
                target.add_include(ancestor_cpp_info.defn_header)
            self.gen_iface_view_defn(
                iface,
                iface_abi_info,
                iface_cpp_info,
                target,
            )
            self.gen_iface_holder_defn(
                iface,
                iface_abi_info,
                iface_cpp_info,
                target,
            )
            self.gen_iface_same(
                iface,
                iface_abi_info,
                iface_cpp_info,
                target,
            )
            self.gen_iface_hash(
                iface,
                iface_abi_info,
                iface_cpp_info,
                target,
            )

    def gen_iface_view_defn(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"namespace {iface_cpp_info.weakspace} {{",
            f"}}",
            indent="",
        ):
            with target.indented(
                f"struct {iface_cpp_info.weak_name} {{",
                f"}};",
            ):
                target.writelns(
                    f"static constexpr bool is_holder = false;",
                )
                target.writelns(
                    f"{iface_abi_info.as_owner} m_handle;",
                )
                target.writelns(
                    f"explicit {iface_cpp_info.weak_name}({iface_abi_info.as_param} handle) : m_handle(handle) {{}}",
                )
                self.gen_iface_view_dynamic_cast(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )
                self.gen_iface_view_static_cast(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )
                self.gen_iface_user_methods_decl(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )
                self.gen_iface_impl_methods_decl(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )
                self.gen_iface_ftbl_decl(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )
                self.gen_iface_vtbl_impl(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )
                self.gen_iface_idmap_impl(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )
                self.gen_iface_infos(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )
                self.gen_iface_utils(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )

    def gen_iface_view_dynamic_cast(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"operator ::taihe::data_view() const& {{",
            f"}}",
        ):
            target.writelns(
                f"return ::taihe::data_view(this->m_handle.data_ptr);",
            )
        with target.indented(
            f"operator ::taihe::data_holder() const& {{",
            f"}}",
        ):
            target.writelns(
                f"return ::taihe::data_holder(tobj_dup(this->m_handle.data_ptr));",
            )
        with target.indented(
            f"explicit {iface_cpp_info.weak_name}(::taihe::data_view other) : {iface_cpp_info.weak_name}({{",
            f"}}) {{}}",
        ):
            target.writelns(
                f"{iface_abi_info.dynamic_cast}(other.data_ptr->rtti_ptr),",
                f"other.data_ptr,",
            )

    def gen_iface_view_static_cast(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if ancestor is iface:
                continue
            ancestor_cpp_info = IfaceCppInfo.get(self.am, ancestor)
            with target.indented(
                f"operator {ancestor_cpp_info.full_weak_name}() const& {{",
                f"}}",
            ):
                with target.indented(
                    f"return {ancestor_cpp_info.full_weak_name}({{",
                    f"}});",
                ):
                    target.writelns(
                        f"{info.static_cast}(this->m_handle.vtbl_ptr),",
                        f"this->m_handle.data_ptr,",
                    )
            with target.indented(
                f"operator {ancestor_cpp_info.full_norm_name}() const& {{",
                f"}}",
            ):
                with target.indented(
                    f"return {ancestor_cpp_info.full_norm_name}({{",
                    f"}});",
                ):
                    target.writelns(
                        f"{info.static_cast}(this->m_handle.vtbl_ptr),",
                        f"tobj_dup(this->m_handle.data_ptr),",
                    )

    def gen_iface_user_methods_decl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        target.writelns(
            f"struct virtual_type;",
        )

    def gen_iface_impl_methods_decl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        target.writelns(
            f"template<typename Impl>",
            f"struct methods_impl;",
        )

    def gen_iface_ftbl_decl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        target.writelns(
            f"template<typename Impl>",
            f"static const {iface_abi_info.ftable} ftbl_impl;",
        )

    def gen_iface_vtbl_impl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        target.writelns(
            f"template<typename Impl>",
        )
        with target.indented(
            f"static constexpr {iface_abi_info.vtable} vtbl_impl = {{",
            f"}};",
        ):
            for ancestor_info in iface_abi_info.ancestor_list:
                ancestor_cpp_info = IfaceCppInfo.get(self.am, ancestor_info.iface)
                target.writelns(
                    f".{ancestor_info.ftbl_ptr} = &{ancestor_cpp_info.full_weak_name}::template ftbl_impl<Impl>,",
                )

    def gen_iface_idmap_impl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        target.writelns(
            f"template<typename Impl>",
        )
        with target.indented(
            f"static constexpr struct IdMapItem idmap_impl[{len(iface_abi_info.ancestor_dict)}] = {{",
            f"}};",
        ):
            for ancestor, info in iface_abi_info.ancestor_dict.items():
                ancestor_abi_info = IfaceAbiInfo.get(self.am, ancestor)
                target.writelns(
                    f"{{&{ancestor_abi_info.iid}, &vtbl_impl<Impl>.{info.ftbl_ptr}}},",
                )

    def gen_iface_infos(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        target.writelns(
            f"using vtable_type = {iface_abi_info.vtable};",
            f"using view_type = {iface_cpp_info.full_weak_name};",
            f"using holder_type = {iface_cpp_info.full_norm_name};",
            f"using abi_type = {iface_abi_info.mangled_name};",
        )

    def gen_iface_utils(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"bool is_error() const& {{",
            f"}}",
        ):
            target.writelns(
                f"return m_handle.vtbl_ptr == nullptr;",
            )
        with target.indented(
            f"virtual_type const& operator*() const& {{",
            f"}}",
        ):
            target.writelns(
                f"return *reinterpret_cast<virtual_type const*>(&m_handle);",
            )
        with target.indented(
            f"virtual_type const* operator->() const& {{",
            f"}}",
        ):
            target.writelns(
                f"return reinterpret_cast<virtual_type const*>(&m_handle);",
            )

    def gen_iface_holder_defn(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"namespace {iface_cpp_info.namespace} {{",
            f"}}",
            indent="",
        ):
            with target.indented(
                f"struct {iface_cpp_info.norm_name} : public {iface_cpp_info.full_weak_name} {{",
                f"}};",
            ):
                target.writelns(
                    f"static constexpr bool is_holder = true;",
                )
                target.writelns(
                    f"explicit {iface_cpp_info.norm_name}({iface_abi_info.as_owner} handle) : {iface_cpp_info.full_weak_name}(handle) {{}}",
                )
                with target.indented(
                    f"{iface_cpp_info.norm_name}& operator=({iface_cpp_info.full_norm_name} other) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"::std::swap(this->m_handle, other.m_handle);",
                        f"return *this;",
                    )
                with target.indented(
                    f"~{iface_cpp_info.norm_name}() {{",
                    f"}}",
                ):
                    target.writelns(
                        f"tobj_drop(this->m_handle.data_ptr);",
                    )
                self.gen_iface_holder_dynamic_cast(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )
                self.gen_iface_holder_static_cast(
                    iface,
                    iface_abi_info,
                    iface_cpp_info,
                    target,
                )

    def gen_iface_holder_dynamic_cast(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"operator ::taihe::data_view() const& {{",
            f"}}",
        ):
            target.writelns(
                f"return ::taihe::data_view(this->m_handle.data_ptr);",
            )
        with target.indented(
            f"operator ::taihe::data_holder() const& {{",
            f"}}",
        ):
            target.writelns(
                f"return ::taihe::data_holder(tobj_dup(this->m_handle.data_ptr));",
            )
        with target.indented(
            f"operator ::taihe::data_holder() && {{",
            f"}}",
        ):
            target.writelns(
                f"return ::taihe::data_holder(std::exchange(this->m_handle.data_ptr, nullptr));",
            )
        with target.indented(
            f"explicit {iface_cpp_info.norm_name}(::taihe::data_holder other) : {iface_cpp_info.norm_name}({{",
            f"}}) {{}}",
        ):
            target.writelns(
                f"{iface_abi_info.dynamic_cast}(other.data_ptr->rtti_ptr),",
                f"std::exchange(other.data_ptr, nullptr),",
            )

    def gen_iface_holder_static_cast(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"{iface_cpp_info.norm_name}({iface_cpp_info.full_weak_name} const& other) : {iface_cpp_info.norm_name}({{",
            f"}}) {{}}",
        ):
            target.writelns(
                f"other.m_handle.vtbl_ptr,",
                f"tobj_dup(other.m_handle.data_ptr),",
            )
        with target.indented(
            f"{iface_cpp_info.norm_name}({iface_cpp_info.full_norm_name} const& other) : {iface_cpp_info.norm_name}({{",
            f"}}) {{}}",
        ):
            target.writelns(
                f"other.m_handle.vtbl_ptr,",
                f"tobj_dup(other.m_handle.data_ptr),",
            )
        with target.indented(
            f"{iface_cpp_info.norm_name}({iface_cpp_info.full_norm_name}&& other) : {iface_cpp_info.norm_name}({{",
            f"}}) {{}}",
        ):
            target.writelns(
                f"other.m_handle.vtbl_ptr,",
                f"std::exchange(other.m_handle.data_ptr, nullptr),",
            )
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if ancestor is iface:
                continue
            ancestor_cpp_info = IfaceCppInfo.get(self.am, ancestor)
            with target.indented(
                f"operator {ancestor_cpp_info.full_weak_name}() const& {{",
                f"}}",
            ):
                with target.indented(
                    f"return {ancestor_cpp_info.full_weak_name}({{",
                    f"}});",
                ):
                    target.writelns(
                        f"{info.static_cast}(this->m_handle.vtbl_ptr),",
                        f"this->m_handle.data_ptr,",
                    )
            with target.indented(
                f"operator {ancestor_cpp_info.full_norm_name}() const& {{",
                f"}}",
            ):
                with target.indented(
                    f"return {ancestor_cpp_info.full_norm_name}({{",
                    f"}});",
                ):
                    target.writelns(
                        f"{info.static_cast}(this->m_handle.vtbl_ptr),",
                        f"tobj_dup(this->m_handle.data_ptr),",
                    )
            with target.indented(
                f"operator {ancestor_cpp_info.full_norm_name}() && {{",
                f"}}",
            ):
                with target.indented(
                    f"return {ancestor_cpp_info.full_norm_name}({{",
                    f"}});",
                ):
                    target.writelns(
                        f"{info.static_cast}(this->m_handle.vtbl_ptr),",
                        f"std::exchange(this->m_handle.data_ptr, nullptr),",
                    )

    def gen_iface_same(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"namespace {iface_cpp_info.weakspace} {{",
            f"}}",
            indent="",
        ):
            with target.indented(
                f"inline bool operator==({iface_cpp_info.as_param} lhs, {iface_cpp_info.as_param} rhs) {{",
                f"}}",
            ):
                target.writelns(
                    f"return ::taihe::data_view(lhs) == ::taihe::data_view(rhs);",
                )

    def gen_iface_hash(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"template<> struct ::std::hash<{iface_cpp_info.full_norm_name}> {{",
            f"}};",
        ):
            with target.indented(
                f"size_t operator()({iface_cpp_info.as_param} val) const {{",
                f"}}",
            ):
                target.writelns(
                    f"return ::std::hash<::taihe::data_holder>()(val);",
                )

    def gen_iface_impl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
    ):
        with CHeaderWriter(
            self.om,
            f"include/{iface_cpp_info.impl_header}",
            FileKind.CPP_HEADER,
        ) as target:
            target.add_include(iface_cpp_info.defn_header)
            target.add_include(iface_abi_info.impl_header)
            for method in iface.methods:
                for param in method.params:
                    type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
                    target.add_include(*type_cpp_info.defn_headers)
                if return_ty_ref := method.return_ty_ref:
                    type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
                    target.add_include(*type_cpp_info.defn_headers)
            self.gen_iface_user_methods_impl(
                iface,
                iface_abi_info,
                iface_cpp_info,
                target,
            )
            self.gen_iface_impl_methods_impl(
                iface,
                iface_abi_info,
                iface_cpp_info,
                target,
            )
            self.gen_iface_ftbl_impl(
                iface,
                iface_abi_info,
                iface_cpp_info,
                target,
            )
            for ancestor, info in iface_abi_info.ancestor_dict.items():
                if ancestor is iface:
                    continue
                ancestor_cpp_info = IfaceCppInfo.get(self.am, ancestor)
                target.add_include(ancestor_cpp_info.impl_header)
            for method in iface.methods:
                for param in method.params:
                    type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
                    target.add_include(*type_cpp_info.impl_headers)
                if return_ty_ref := method.return_ty_ref:
                    type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
                    target.add_include(*type_cpp_info.impl_headers)

    def gen_iface_user_methods_impl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        with target.indented(
            f"struct {iface_cpp_info.full_weak_name}::virtual_type {{",
            f"}};",
        ):
            for method in iface.methods:
                method_abi_info = IfaceMethodAbiInfo.get(self.am, method)
                method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
                params_cpp = []
                thiz = f"*reinterpret_cast<{iface_abi_info.mangled_name} const*>(this)"
                args_into_abi = [thiz]
                for param in method.params:
                    type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
                    params_cpp.append(f"{type_cpp_info.as_param} {param.name}")
                    args_into_abi.append(type_cpp_info.pass_into_abi(param.name))
                params_cpp_str = ", ".join(params_cpp)
                args_into_abi_str = ", ".join(args_into_abi)
                abi_result = f"{method_abi_info.mangled_name}({args_into_abi_str})"
                if return_ty_ref := method.return_ty_ref:
                    type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
                    cpp_return_ty_name = type_cpp_info.as_owner
                    cpp_result = type_cpp_info.return_from_abi(abi_result)
                else:
                    cpp_return_ty_name = "void"
                    cpp_result = abi_result
                with target.indented(
                    f"{cpp_return_ty_name} {method_cpp_info.call_name}({params_cpp_str}) const& {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return {cpp_result};",
                    )

    def gen_iface_impl_methods_impl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        target.writelns(
            f"template<typename Impl>",
        )
        with target.indented(
            f"struct {iface_cpp_info.full_weak_name}::methods_impl {{",
            f"}};",
        ):
            for method in iface.methods:
                method_cpp_info = IfaceMethodCppInfo.get(self.am, method)
                params_abi = [f"{iface_abi_info.as_param} tobj"]
                args_from_abi = []
                for param in method.params:
                    type_abi_info = TypeAbiInfo.get(self.am, param.ty_ref.resolved_ty)
                    type_cpp_info = TypeCppInfo.get(self.am, param.ty_ref.resolved_ty)
                    params_abi.append(f"{type_abi_info.as_param} {param.name}")
                    args_from_abi.append(type_cpp_info.pass_from_abi(param.name))
                params_abi_str = ", ".join(params_abi)
                args_from_abi_str = ", ".join(args_from_abi)
                cpp_result = f"::taihe::cast_data_ptr<Impl>(tobj.data_ptr)->{method_cpp_info.impl_name}({args_from_abi_str})"
                if return_ty_ref := method.return_ty_ref:
                    type_abi_info = TypeAbiInfo.get(self.am, return_ty_ref.resolved_ty)
                    type_cpp_info = TypeCppInfo.get(self.am, return_ty_ref.resolved_ty)
                    abi_return_ty_name = type_abi_info.as_owner
                    abi_result = type_cpp_info.return_into_abi(cpp_result)
                else:
                    abi_return_ty_name = "void"
                    abi_result = cpp_result
                with target.indented(
                    f"static {abi_return_ty_name} {method.name}({params_abi_str}) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return {abi_result};",
                    )

    def gen_iface_ftbl_impl(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceAbiInfo,
        iface_cpp_info: IfaceCppInfo,
        target: CHeaderWriter,
    ):
        target.writelns(
            f"template<typename Impl>",
        )
        with target.indented(
            f"constexpr {iface_abi_info.ftable} {iface_cpp_info.weakspace}::{iface_cpp_info.weak_name}::ftbl_impl = {{",
            f"}};",
        ):
            for method in iface.methods:
                target.writelns(
                    f".{method.name} = &methods_impl<Impl>::{method.name},",
                )
