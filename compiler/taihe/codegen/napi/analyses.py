from abc import ABCMeta, abstractmethod

from typing_extensions import override

from taihe.codegen.abi.writer import CSourceWriter
from taihe.codegen.cpp.analyses import (
    TypeCppInfo,
)
from taihe.semantics.declarations import (
    PackageDecl,
)
from taihe.semantics.types import (
    ScalarKind,
    ScalarType,
    StringType,
    Type,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager


class PackageNapiInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        super().__init__(am, p)
        self.am = am
        self.source = f"{p.name}.napi.cpp"
        self.ts_decl = f"{p.name}.d.ts"
        self.cpp_ns = "::".join(p.segments)


class AbstractTypeNapiInfo(metaclass=ABCMeta):
    dts_type: str

    def __init__(self, am: AnalysisManager, t: Type):
        self.cpp_info = TypeCppInfo.get(am, t)

    @abstractmethod
    def from_napi(
        self,
        pkg_napi_target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        pass

    @abstractmethod
    def into_napi(
        self,
        pkg_napi_target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        pass


class ScalarTypeNapiInfo(AbstractAnalysis[ScalarType], AbstractTypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.cpp_info = TypeCppInfo.get(am, t)
        dts_type = {
            ScalarKind.BOOL: "bool",
            ScalarKind.F32: "number",
            ScalarKind.I32: "number",
            ScalarKind.I64: "number",
            ScalarKind.U32: "number",
        }.get(self.type.kind)
        if dts_type is None:
            raise ValueError(f"Unsupported ScalarKind: {self.type.kind}")
        self.dts_type = dts_type

    def from_napi(
        self,
        pkg_napi_target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        as_napi_c = {
            ScalarKind.BOOL: "bool",
            ScalarKind.F32: "double",
            # ScalarKind.F64: "double",
            ScalarKind.I32: "int32_t",
            ScalarKind.I64: "int64_t",
            ScalarKind.U32: "uint32_t",
        }.get(self.type.kind)
        from_js_to_c_func = {
            ScalarKind.BOOL: "napi_get_value_bool",
            ScalarKind.F32: "napi_get_value_double",
            # ScalarKind.F64: "napi_get_value_double",
            ScalarKind.I32: "napi_get_value_int32",
            ScalarKind.I64: "napi_get_value_int64",
            ScalarKind.U32: "napi_get_value_uint32",
        }.get(self.type.kind)
        pkg_napi_target.writelns(
            f"{as_napi_c} {cpp_result}_tmp;",
            f"{from_js_to_c_func}(env, {napi_value}, &{cpp_result}_tmp);",
            f"{self.cpp_info.as_owner} {cpp_result} = {cpp_result}_tmp;",
        )

    def into_napi(
        self,
        pkg_napi_target: CSourceWriter,
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
        pkg_napi_target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"{from_c_to_js_func}(env, {cpp_value}, &{napi_result});",
        )


class StringTypeNapiInfo(AbstractAnalysis[StringType], AbstractTypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: StringType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.dts_type = "string"

    def from_napi(
        self,
        pkg_napi_target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        pkg_napi_target.writelns(
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
        pkg_napi_target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        pkg_napi_target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"napi_create_string_utf8(env, {cpp_value}.c_str(), {cpp_value}.size(), &{napi_result});",
        )


class TypeNapiInfo(TypeVisitor[AbstractTypeNapiInfo]):
    def __init__(self, am: AnalysisManager):
        self.am = am

    @staticmethod
    def get(am: AnalysisManager, t: Type):
        return TypeNapiInfo(am).handle_type(t)

    @override
    def visit_scalar_type(self, t: ScalarType) -> AbstractTypeNapiInfo:
        return ScalarTypeNapiInfo.get(self.am, t)

    @override
    def visit_string_type(self, t: StringType) -> AbstractTypeNapiInfo:
        return StringTypeNapiInfo.get(self.am, t)
