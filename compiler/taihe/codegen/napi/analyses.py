from abc import ABCMeta, abstractmethod

from typing_extensions import override

from taihe.codegen.abi.analyses import IfaceABIInfo, StructABIInfo
from taihe.codegen.abi.mangle import DeclKind, encode
from taihe.codegen.abi.writer import CSourceWriter
from taihe.codegen.cpp.analyses import (
    EnumCppInfo,
    TypeCppInfo,
)
from taihe.semantics.declarations import (
    EnumDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    StructDecl,
    StructFieldDecl,
)
from taihe.semantics.types import (
    ArrayType,
    CallbackType,
    EnumType,
    IfaceType,
    OptionalType,
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
        self.constructor_func_name = encode(segments, DeclKind.CONSTRUCTOR)
        self.create_func_name = encode(segments, DeclKind.CREATE)
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.napi.decl.h"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.napi.impl.h"
        self.dts_type_name = d.name
        struct_abi_info = StructABIInfo.get(am, d)
        self.ctor_ref_name = f"ctor_ref_{struct_abi_info.mangled_name}"
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


class StructFieldNAPIInfo(AbstractAnalysis[StructFieldDecl]):
    def __init__(self, am: AnalysisManager, d: StructFieldDecl) -> None:
        super().__init__(am, d)
        segments = [*d.parent_pkg.segments, d.name]
        self.getter_name = encode(segments, DeclKind.GETTER)
        self.setter_name = encode(segments, DeclKind.SETTER)


class IfaceNAPIInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        super().__init__(am, d)
        segments = [*d.parent_pkg.segments, d.name]
        self.from_napi_func_name = encode(segments, DeclKind.FROM_NAPI)
        self.into_napi_func_name = encode(segments, DeclKind.INTO_NAPI)
        self.constructor_func_name = encode(segments, DeclKind.CONSTRUCTOR)
        self.create_func_name = encode(segments, DeclKind.CREATE)
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.napi.decl.h"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.napi.impl.h"
        self.meth_decl_header = f"{d.parent_pkg.name}.{d.name}.meth.napi.decl.h"
        self.meth_impl_header = f"{d.parent_pkg.name}.{d.name}.meth.napi.impl.h"
        self.dts_type_name = d.name
        iface_abi_info = IfaceABIInfo.get(am, d)
        self.ctor_ref_name = f"ctor_ref_{iface_abi_info.mangled_name}"
        if d.get_last_attr("class"):
            self.dts_impl_name = f"{d.name}"
        else:
            self.dts_impl_name = f"{d.name}_inner"

        iface_abi_info = IfaceABIInfo.get(am, d)
        iface_register_infos: dict[str, tuple[IfaceMethodDecl, IfaceDecl]] = {}
        for ancestor in iface_abi_info.ancestor_dict:
            for method in ancestor.methods:
                segments = [
                    *d.parent_pkg.segments,
                    d.name,
                    method.name,
                ]
                mangled_name = encode(segments, DeclKind.NAPI_FUNC)
                iface_register_infos[mangled_name] = (method, ancestor)
        self.iface_register_infos = iface_register_infos

    def is_class(self):
        return self.dts_type_name == self.dts_impl_name


class EnumNAPIInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        super().__init__(am, d)
        self.dts_type_name = d.name


class AbstractTypeNAPIInfo(metaclass=ABCMeta):
    dts_type_name: str
    return_dts_type_name: str
    is_optional: bool = False

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
            ScalarKind.U8: "number",
        }.get(self.type.kind)
        if dts_type is None:
            raise ValueError(f"Unsupported ScalarKind: {self.type.kind}")
        self.dts_type_name = dts_type
        self.return_dts_type_name = self.dts_type_name

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
            ScalarKind.U8: "uint32_t",
        }.get(self.type.kind)
        from_js_to_c_func = {
            ScalarKind.BOOL: "napi_get_value_bool",
            # ScalarKind.F32: "napi_get_value_double",
            ScalarKind.F64: "napi_get_value_double",
            ScalarKind.I32: "napi_get_value_int32",
            ScalarKind.I64: "napi_get_value_int64",
            ScalarKind.U32: "napi_get_value_uint32",
            ScalarKind.U8: "napi_get_value_uint32",
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
            ScalarKind.U8: "napi_create_uint32",
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
        self.return_dts_type_name = self.dts_type_name

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
        self.return_dts_type_name = self.dts_type_name

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


class IfaceTypeNAPIInfo(AbstractTypeNAPIInfo, AbstractAnalysis[IfaceType]):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        iface_napi_info = IfaceNAPIInfo.get(self.am, t.ty_decl)
        self.dts_type_name = iface_napi_info.dts_type_name
        self.return_dts_type_name = self.dts_type_name
        self.iface_register_infos = iface_napi_info.iface_register_infos

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        iface_napi_info = IfaceNAPIInfo.get(self.am, self.type.ty_decl)
        target.add_include(iface_napi_info.impl_header)
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result} = {iface_napi_info.from_napi_func_name}(env, {napi_value});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        iface_napi_info = IfaceNAPIInfo.get(self.am, self.type.ty_decl)
        target.add_include(iface_napi_info.impl_header)
        target.writelns(
            f"napi_value {napi_result} = {iface_napi_info.into_napi_func_name}(env, {cpp_value});",
        )


class OptionalTypeNAPIInfo(AbstractTypeNAPIInfo, AbstractAnalysis[OptionalType]):
    def __init__(self, am: AnalysisManager, t: OptionalType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        item_ty_napi_info = TypeNAPIInfo.get(self.am, self.type.item_ty)
        self.dts_type_name = item_ty_napi_info.dts_type_name
        self.return_dts_type_name = f"{self.dts_type_name} | undefined"
        self.is_optional = True

    @override
    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        napi_ty = f"{cpp_result}_v_ty"
        napi_status = f"{cpp_result}_v_ty_status"
        cpp_pointer = f"{cpp_result}_ptr"
        cpp_spec = f"{cpp_result}_spec"
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        target.writelns(
            f"{item_ty_cpp_info.as_owner}* {cpp_pointer} = nullptr;",
            f"napi_valuetype {napi_ty};",
            f"napi_status {napi_status} = napi_typeof(env, {napi_value}, &{napi_ty});",
        )
        with target.indented(
            f"if ({napi_status} == napi_ok && {napi_ty} != napi_undefined) {{",
            f"}}",
        ):
            item_ty_napi_info = TypeNAPIInfo.get(self.am, self.type.item_ty)
            item_ty_napi_info.from_napi(target, napi_value, cpp_spec)
            target.writelns(
                f"{cpp_pointer} = new {item_ty_cpp_info.as_owner}(std::move({cpp_spec}));",
            )
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result}({cpp_pointer});",
        )

    @override
    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        napi_spec = f"{napi_result}_spec"
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
        )
        with target.indented(
            f"if (!{cpp_value}) {{",
            f"}}",
        ):
            target.writelns(f"napi_get_undefined(env, &{napi_result});")
        with target.indented(
            f"else {{",
            f"}}",
        ):
            item_ty_napi_info = TypeNAPIInfo.get(self.am, self.type.item_ty)
            item_ty_napi_info.into_napi(target, f"(*{cpp_value})", napi_spec)
            target.writelns(
                f"{napi_result} = {napi_spec};",
            )


class CallbackTypeNAPIInfo(AbstractTypeNAPIInfo, AbstractAnalysis[CallbackType]):
    def __init__(self, am: AnalysisManager, t: CallbackType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        params_ty_sts = []
        for index, param_ty in enumerate(self.type.params_ty):
            param_ty_napi_info = TypeNAPIInfo.get(self.am, param_ty)
            params_ty_sts.append(
                f"arg_{index}{'?' if param_ty_napi_info.is_optional else ''}: {param_ty_napi_info.dts_type_name}"
            )
        params_ty_sts_str = ", ".join(params_ty_sts)
        if return_ty := self.type.return_ty:
            return_ty_napi_info = TypeNAPIInfo.get(self.am, return_ty)
            return_ty_sts = return_ty_napi_info.dts_type_name
        else:
            return_ty_sts = "void"
        self.dts_type_name = f"(({params_ty_sts_str}) => {return_ty_sts})"
        self.return_dts_type_name = self.dts_type_name

    @override
    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        cpp_impl_class = f"{cpp_result}_cpp_impl_t"
        with target.indented(
            f"struct {cpp_impl_class} {{",
            f"}};",
        ):
            target.writelns(f"napi_env env;", f"napi_ref ref;")
            with target.indented(
                f"{cpp_impl_class}(napi_env env, napi_value callback): env(env), ref(nullptr) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_create_reference(env, callback, 1, &ref);",
                )
            with target.indented(
                f"~{cpp_impl_class}() {{",
                f"}}",
            ):
                with target.indented(
                    f"if (ref) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"napi_delete_reference(env, ref);",
                    )
            inner_cpp_params = []
            inner_napi_args = []
            inner_cpp_args = []
            for index, param_ty in enumerate(self.type.params_ty):
                inner_cpp_arg = f"cpp_arg_{index}"
                inner_napi_arg = f"napi_arg_{index}"
                param_ty_cpp_info = TypeCppInfo.get(self.am, param_ty)
                inner_cpp_params.append(f"{param_ty_cpp_info.as_param} {inner_cpp_arg}")
                inner_napi_args.append(inner_napi_arg)
                inner_cpp_args.append(inner_cpp_arg)
            cpp_params_str = ", ".join(inner_cpp_params)
            if return_ty := self.type.return_ty:
                return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                return_ty_as_owner = return_ty_cpp_info.as_owner
            else:
                return_ty_as_owner = "void"
            with target.indented(
                f"{return_ty_as_owner} operator()({cpp_params_str}) {{",
                f"}}",
            ):
                target.writelns()
                for inner_napi_arg, inner_cpp_arg, param_ty in zip(
                    inner_napi_args, inner_cpp_args, self.type.params_ty, strict=True
                ):
                    param_ty_napi_info = TypeNAPIInfo.get(self.am, param_ty)
                    param_ty_napi_info.into_napi(target, inner_cpp_arg, inner_napi_arg)
                inner_napi_args_str = ", ".join(inner_napi_args)
                if return_ty := self.type.return_ty:
                    inner_napi_res = "napi_result"
                    inner_cpp_res = "cpp_result"
                    target.writelns(
                        f"napi_value napi_argv[] = {{{inner_napi_args_str}}};",
                        f"napi_value {inner_napi_res} = nullptr;",
                        f"napi_value cb_ref = nullptr, global = nullptr;",
                        f"napi_get_reference_value(env, ref, &cb_ref);",
                        f"napi_get_global(env, &global);",
                        f"napi_call_function(env, global, cb_ref, {len(self.type.params_ty)}, napi_argv, &{inner_napi_res});",
                    )
                    return_ty_napi_info = TypeNAPIInfo.get(self.am, return_ty)
                    return_ty_napi_info.from_napi(target, inner_napi_res, inner_cpp_res)
                    target.writelns(
                        f"return {inner_cpp_res};",
                    )
                else:
                    inner_napi_res = "napi_result"
                    target.writelns(
                        f"napi_value napi_argv[] = {{{inner_napi_args_str}}};",
                        f"napi_value {inner_napi_res} = nullptr;",
                        f"napi_value cb_ref = nullptr, global = nullptr;",
                        f"napi_get_reference_value(env, ref, &cb_ref);",
                        f"napi_get_global(env, &global);",
                        f"napi_call_function(env, global, cb_ref, 1, napi_argv, &{inner_napi_res});",
                        f"return;",
                    )
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result} = ::taihe::make_holder<{cpp_impl_class}, {self.cpp_info.as_owner}>(env, {napi_value});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        # TODO: Callback into napi
        target.writelns(
            f"napi_value {napi_result} = {{}};",
        )


class EnumTypeNAPIInfo(AbstractTypeNAPIInfo, AbstractAnalysis[EnumType]):
    def __init__(self, am: AnalysisManager, t: EnumType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.dts_type_name = t.ty_decl.name
        self.return_dts_type_name = self.dts_type_name

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        enum_cpp_info = EnumCppInfo.get(self.am, self.type.ty_decl)
        if isinstance(self.type.ty_decl.ty_ref.resolved_ty, ScalarType | StringType):
            item_ty_napi_info = TypeNAPIInfo.get(
                self.am, self.type.ty_decl.ty_ref.resolved_ty
            )
            item_ty_napi_info.from_napi(target, napi_value, f"{cpp_result}_item")
        else:
            raise ValueError

        target.writelns(
            f"{enum_cpp_info.as_owner} {cpp_result} = {enum_cpp_info.as_owner}::from_value({cpp_result}_item);",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        if isinstance(self.type.ty_decl.ty_ref.resolved_ty, ScalarType | StringType):
            item_ty_napi_info = TypeNAPIInfo.get(
                self.am, self.type.ty_decl.ty_ref.resolved_ty
            )
            item_ty_cpp_info = TypeCppInfo.get(
                self.am, self.type.ty_decl.ty_ref.resolved_ty
            )
            item_ty_napi_info.into_napi(
                target,
                f"(({item_ty_cpp_info.as_owner})({cpp_value}.get_value()))",
                napi_result,
            )
        else:
            raise ValueError


class ArrayBufferTypeNAPIInfo(AbstractTypeNAPIInfo, AbstractAnalysis[ArrayType]):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.dts_type_name = "ArrayBuffer"
        self.return_dts_type_name = self.dts_type_name

        if not isinstance(t.item_ty, ScalarType) or t.item_ty.kind not in (
            ScalarKind.I8,
            ScalarKind.U8,
        ):
            raise ValueError(
                "@arraybuffer only supports Array<i8> or Array<i8>",
            )

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        napi_data = f"{cpp_result}_data"
        napi_length = f"{cpp_result}_length"
        target.writelns(
            f"void* {napi_data};",
            f"size_t {napi_length};",
            f"napi_get_arraybuffer_info(env, {napi_value}, &{napi_data}, &{napi_length});",
            f"{self.cpp_info.as_param} {cpp_result}(reinterpret_cast<{item_ty_cpp_info.as_owner}*>({napi_data}), {napi_length});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        target.add_include("string.h")
        napi_data = f"{napi_result}_data"
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"void* {napi_data} = nullptr;",
            f"napi_create_arraybuffer(env, {cpp_value}.size(), &{napi_data}, &{napi_result});",
            f"memcpy({napi_data}, {cpp_value}.data(), {cpp_value}.size());",
        )


class ArrayTypeNAPIInfo(AbstractTypeNAPIInfo, AbstractAnalysis[ArrayType]):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        item_ty_napi_info = TypeNAPIInfo.get(self.am, self.type.item_ty)
        sts_type = item_ty_napi_info.dts_type_name
        self.dts_type_name = f"Array<{sts_type}>"
        self.return_dts_type_name = self.dts_type_name

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        item_ty_napi_info = TypeNAPIInfo.get(self.am, self.type.item_ty)
        array_size = f"{cpp_result}_size"
        cpp_buffer = f"{cpp_result}_buffer"
        napi_item = f"{cpp_buffer}_napi_item"
        cpp_item = f"{cpp_buffer}_cpp_item"
        cpp_ctr = f"{cpp_buffer}_i"
        target.writelns(
            f"uint32_t {array_size};",
            f"napi_get_array_length(env, {napi_value}, &{array_size});",
            f"{item_ty_cpp_info.as_owner}* {cpp_buffer} = reinterpret_cast<{item_ty_cpp_info.as_owner}*>(malloc({array_size} * sizeof({item_ty_cpp_info.as_owner})));",
        )
        with target.indented(
            f"for (uint32_t {cpp_ctr} = 0; {cpp_ctr} < {array_size}; {cpp_ctr}++) {{",
            f"}}",
        ):
            target.writelns(
                f"napi_value {napi_item};",
                f"napi_get_element(env, {napi_value}, {cpp_ctr}, &{napi_item});",
            )
            item_ty_napi_info.from_napi(target, napi_item, cpp_item)
            target.writelns(
                f"new (&{cpp_buffer}[{cpp_ctr}]) {item_ty_napi_info.cpp_info.as_owner}(std::move({cpp_item}));",
            )
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result}({cpp_buffer}, {array_size});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        item_ty_napi_info = TypeNAPIInfo.get(self.am, self.type.item_ty)
        cpp_size = f"{napi_result}_size"
        napi_item = f"{napi_result}_item"
        cpp_ctr = f"{napi_result}_i"
        target.writelns(
            f"uint32_t {cpp_size} = {cpp_value}.size();",
            f"napi_value {napi_result} = nullptr;",
            f"napi_create_array_with_length(env, {cpp_size}, &{napi_result});",
        )
        with target.indented(
            f"for (uint32_t {cpp_ctr} = 0; {cpp_ctr} < {cpp_size}; {cpp_ctr}++) {{",
            f"}}",
        ):
            item_ty_napi_info.into_napi(target, f"{cpp_value}[{cpp_ctr}]", napi_item)
            target.writelns(
                f"napi_set_element(env, {napi_result}, {cpp_ctr}, {napi_item});",
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

    @override
    def visit_iface_type(self, t: IfaceType) -> AbstractTypeNAPIInfo:
        return IfaceTypeNAPIInfo.get(self.am, t)

    @override
    def visit_optional_type(self, t: OptionalType) -> AbstractTypeNAPIInfo:
        return OptionalTypeNAPIInfo.get(self.am, t)

    @override
    def visit_callback_type(self, t: CallbackType) -> AbstractTypeNAPIInfo:
        return CallbackTypeNAPIInfo.get(self.am, t)

    @override
    def visit_enum_type(self, t: EnumType) -> AbstractTypeNAPIInfo:
        return EnumTypeNAPIInfo.get(self.am, t)

    @override
    def visit_array_type(self, t: ArrayType) -> AbstractTypeNAPIInfo:
        if t.ty_ref.attrs.get("arraybuffer"):
            return ArrayBufferTypeNAPIInfo.get(self.am, t)
        return ArrayTypeNAPIInfo.get(self.am, t)
