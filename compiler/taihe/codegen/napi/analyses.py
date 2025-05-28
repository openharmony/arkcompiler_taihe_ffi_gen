from abc import ABCMeta, abstractmethod

from typing_extensions import override

from taihe.codegen.abi.mangle import DeclKind, encode
from taihe.codegen.abi.writer import CSourceWriter
from taihe.codegen.cpp.analyses import (
    TypeCppInfo,
)
from taihe.semantics.declarations import (
    PackageDecl,
    StructDecl,
    StructFieldDecl,
)
from taihe.semantics.types import (
    ScalarKind,
    ScalarType,
    StringType,
    StructType,
    Type,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager


class PackageNAPIInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        super().__init__(am, p)
        self.am = am
        self.source = f"{p.name}.napi.cpp"
        self.ts_decl = f"{p.name}.d.ts"
        self.cpp_ns = "::".join(p.segments)


class StructNAPIInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        super().__init__(am, d)
        segments = [*d.parent_pkg.segments, d.name]
        self.from_napi_func_name = encode(segments, DeclKind.FROM_NAPI)
        self.into_napi_func_name = encode(segments, DeclKind.INTO_NAPI)
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.napi.decl.h"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.napi.impl.h"
        self.dts_type_name = d.name
        if d.get_last_attr("class"):
            self.dts_impl_name = f"{d.name}"
        else:
            self.dts_impl_name = f"{d.name}_inner"

        self.sts_fields: list[StructFieldDecl] = []
        self.sts_final_fields: list[list[StructFieldDecl]] = []
        for field in d.fields:
            self.sts_fields.append(field)
            self.sts_final_fields.append([field])

    def is_class(self):
        return self.dts_type_name == self.dts_impl_name


class AbstractTypeNAPIInfo(metaclass=ABCMeta):
    dts_type_name: str

    def __init__(self, am: AnalysisManager, t: Type):
        self.cpp_info = TypeCppInfo.get(am, t)

    @abstractmethod
    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        pass

    @abstractmethod
    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        pass


class ScalarTypeNAPIInfo(AbstractTypeNAPIInfo, AbstractAnalysis[ScalarType]):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        dts_type = {
            ScalarKind.BOOL: "boolean",
            # ScalarKind.F32: "number",
            ScalarKind.F64: "number",
            ScalarKind.I32: "number",
            ScalarKind.I64: "number",
            ScalarKind.U32: "number",
        }.get(self.type.kind)
        if dts_type is None:
            raise ValueError(f"Unsupported ScalarKind: {self.type.kind}")
        self.dts_type_name = dts_type

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        as_napi_c = {
            ScalarKind.BOOL: "bool",
            # ScalarKind.F32: "double",
            ScalarKind.F64: "double",
            ScalarKind.I32: "int32_t",
            ScalarKind.I64: "int64_t",
            ScalarKind.U32: "uint32_t",
        }.get(self.type.kind)
        from_js_to_c_func = {
            ScalarKind.BOOL: "napi_get_value_bool",
            # ScalarKind.F32: "napi_get_value_double",
            ScalarKind.F64: "napi_get_value_double",
            ScalarKind.I32: "napi_get_value_int32",
            ScalarKind.I64: "napi_get_value_int64",
            ScalarKind.U32: "napi_get_value_uint32",
        }.get(self.type.kind)
        target.writelns(
            f"{as_napi_c} {cpp_result}_tmp;",
            f"{from_js_to_c_func}(env, {napi_value}, &{cpp_result}_tmp);",
            f"{self.cpp_info.as_owner} {cpp_result} = {cpp_result}_tmp;",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        from_c_to_js_func = {
            ScalarKind.BOOL: "napi_get_boolean",
            # ScalarKind.F32: "napi_create_double",
            ScalarKind.F64: "napi_create_double",
            ScalarKind.I32: "napi_create_int32",
            ScalarKind.I64: "napi_create_int64",
            ScalarKind.U32: "napi_create_uint32",
        }.get(self.type.kind)
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"{from_c_to_js_func}(env, {cpp_value}, &{napi_result});",
        )


class StringTypeNAPIInfo(AbstractTypeNAPIInfo, AbstractAnalysis[StringType]):
    def __init__(self, am: AnalysisManager, t: StringType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.cpp_info = TypeCppInfo.get(am, t)
        self.dts_type_name = "string"

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        target.writelns(
            f"size_t {cpp_result}_len = 0;",
            f"napi_get_value_string_utf8(env, {napi_value}, nullptr, 0, &{cpp_result}_len);",
            f"TString {cpp_result}_abi;",
            f"char* {cpp_result}_buf = tstr_initialize(&{cpp_result}_abi, {cpp_result}_len + 1);",
            f"napi_get_value_string_utf8(env, {napi_value}, {cpp_result}_buf, {cpp_result}_len + 1, &{cpp_result}_len);",
            f"{cpp_result}_buf[{cpp_result}_len] = '\\0';",
            f"{cpp_result}_abi.length = {cpp_result}_len;",
            f"taihe::string {cpp_result}({cpp_result}_abi);",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"napi_create_string_utf8(env, {cpp_value}.c_str(), {cpp_value}.size(), &{napi_result});",
        )


class StructTypeNAPIInfo(AbstractTypeNAPIInfo, AbstractAnalysis[StructType]):
    def __init__(self, am: AnalysisManager, t: StructType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        struct_napi_info = StructNAPIInfo.get(self.am, t.ty_decl)
        self.dts_type_name = struct_napi_info.dts_type_name

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        struct_napi_info = StructNAPIInfo.get(self.am, self.type.ty_decl)
        target.add_include(struct_napi_info.impl_header)
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result} = {struct_napi_info.from_napi_func_name}(env, {napi_value});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        struct_napi_info = StructNAPIInfo.get(self.am, self.type.ty_decl)
        target.add_include(struct_napi_info.impl_header)
        target.writelns(
            f"napi_value {napi_result} = {struct_napi_info.into_napi_func_name}(env, {cpp_value});",
        )


class TypeNAPIInfo(TypeVisitor[AbstractTypeNAPIInfo]):
    def __init__(self, am: AnalysisManager):
        self.am = am

    @staticmethod
    def get(am: AnalysisManager, t: Type):
        return TypeNAPIInfo(am).handle_type(t)

    @override
    def visit_scalar_type(self, t: ScalarType) -> AbstractTypeNAPIInfo:
        return ScalarTypeNAPIInfo.get(self.am, t)

    @override
    def visit_string_type(self, t: StringType) -> AbstractTypeNAPIInfo:
        return StringTypeNAPIInfo.get(self.am, t)

    @override
    def visit_struct_type(self, t: StructType) -> AbstractTypeNAPIInfo:
        return StructTypeNAPIInfo.get(self.am, t)
