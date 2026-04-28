# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from taihe.codegen.abi.analyses import (
    IfaceAbiInfo,
)
from taihe.codegen.ani.analyses import (
    ArkTsModule,
    ArkTsModuleOrNamespace,
    EnumAniInfo,
    EnumConstAniInfo,
    EnumFieldAniInfo,
    EnumObjectAniInfo,
    GlobFuncAniInfo,
    IfaceAniInfo,
    IfaceMethodAniInfo,
    IfaceThunkAniInfo,
    IfaceThunkKey,
    NamedCallableAniInfo,
    PackageAniInfo,
    PackageGroupAniInfo,
    ParamAniInfo,
    ScalarTypeAniInfo,
    StructAniInfo,
    StructFieldAniInfo,
    StructObjectAniInfo,
    StructTupleAniInfo,
    TypeAniInfo,
    UnionAniInfo,
)
from taihe.codegen.ani.attributes import (
    OptionalAttr,
    ReadOnlyAttr,
)
from taihe.codegen.ani.writer import (
    StsWriter,
    render_ets_value,
)
from taihe.semantics.declarations import (
    EnumDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
    StructDecl,
    UnionDecl,
)
from taihe.semantics.types import NonVoidType
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputManager


@dataclass(frozen=True)
class FuncKind(ABC):
    func_prefix: ClassVar[str]
    get_prefix: ClassVar[str]
    set_prefix: ClassVar[str]
    overload_prefix: ClassVar[str]

    @abstractmethod
    def call_from_local(self, name: str) -> str: ...

    @abstractmethod
    def reverse_base_params(self) -> list[str]: ...

    @abstractmethod
    def call_from_reverse(self, name: str) -> str: ...


@dataclass(frozen=True)
class CtorKind:
    func_prefix = "constructor "
    overload_prefix = "overload constructor "

    class_name: str

    def call_from_local(self, name: str) -> str:
        return f"this.{name}" if name else "this"

    def reverse_base_params(self) -> list[str]:
        return []

    def call_from_reverse(self, name: str) -> str:
        return f"new {self.class_name}.{name}" if name else f"new {self.class_name}"


@dataclass(frozen=True)
class InterfaceKind(FuncKind):
    func_prefix = ""
    get_prefix = "get "
    set_prefix = "set "
    overload_prefix = "overload "

    type_name: str

    def call_from_local(self, name: str) -> str:
        return f"this.{name}"

    def reverse_base_params(self) -> list[str]:
        return [f"self: {self.type_name}"]

    def call_from_reverse(self, name: str) -> str:
        return f"self.{name}"


@dataclass(frozen=True)
class StaticKind(FuncKind):
    func_prefix = "static "
    get_prefix = "static get "
    set_prefix = "static set "
    overload_prefix = "static overload "

    class_name: str

    def call_from_local(self, name: str) -> str:
        return f"{self.class_name}.{name}"

    def reverse_base_params(self) -> list[str]:
        return []

    def call_from_reverse(self, name: str) -> str:
        return f"{self.class_name}.{name}"


@dataclass(frozen=True)
class GlobalKind(FuncKind):
    func_prefix = "function "
    get_prefix = "get "
    set_prefix = "set "
    overload_prefix = "overload "

    def call_from_local(self, name: str) -> str:
        return name

    def reverse_base_params(self) -> list[str]:
        return []

    def call_from_reverse(self, name: str) -> str:
        return name


OverloadInfo = list[str]


class OverloadRegister:
    def __init__(self):
        self.infos: dict[str, OverloadInfo] = {}

    def register(self, orig_name: str, name: str):
        info = self.infos.setdefault(name, [])
        info.append(orig_name)


OnOffInfo = dict[tuple[str, ...], dict[str, tuple[str, list[str], str]]]


class OnOffRegister:
    def __init__(self):
        self.infos: dict[str, OnOffInfo] = {}

    def register(
        self,
        pair: tuple[str, str],
        params_ty_sts_sig: list[str],
        orig_name: str,
        params_ty_sts_name: list[str],
        return_ty_sts_name: str,
    ):
        name, type = pair
        info = self.infos.setdefault(name, {})
        cases = info.setdefault(tuple(params_ty_sts_sig), {})
        cases.setdefault(type, (orig_name, params_ty_sts_name, return_ty_sts_name))


class StsCodeGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am

    def generate(self, pg: PackageGroup):
        pg_ani_info = PackageGroupAniInfo.get(self.am, pg)
        for _, mod in pg_ani_info.mods.items():
            module_generator = StsModuleGenerator(self.om, self.am, mod)
            module_generator.gen_module_file()


class StsModuleGenerator:
    def __init__(
        self,
        om: OutputManager,
        am: AnalysisManager,
        mod: ArkTsModule,
    ):
        self.am = am
        self.target = StsWriter(om, mod)
        self.mod = mod

    def gen_module_file(self):
        with self.target:
            for descendant_ns in self.mod.descendants:
                for head in descendant_ns.injected_globs:
                    self.target.write_block(head)
            namespace_generator = StsNamespaceGenerator(
                self.target,
                self.am,
                self.mod,
            )
            namespace_generator.gen_namespace()
            self.gen_utils()

    def gen_utils(self):
        self.target.add_import_decl(self.mod.BE_type, "@ohos.base", "BusinessError")
        self.target.writelns(
            f"type {self.mod.AC_type}<T, E = void> = (error: {self.mod.BE_type}<E> | null, data: T | undefined) => void;",
        )

        self.target.writelns(
            f"function {self.mod.arrbuf_to_bigint}(arr: ArrayBuffer): BigInt {{",
            f"    let res: BigInt = 0n;",
            f"    for (let i: int = 0; i < arr.getByteLength(); i++) {{",
            f"        res |= BigInt(arr.at(i).toLong() & 0xff) << BigInt(i * 8);",
            f"    }}",
            f"    let m: int = arr.getByteLength();",
            f"    if (arr.at(m - 1) < 0) {{",
            f"        res |= -1n << BigInt(m * 8 - 1);",
            f"    }}",
            f"    return res;",
            f"}}",
        )
        self.target.writelns(
            f"function {self.mod.bigint_to_arrbuf}(val: BigInt, blk: int): ArrayBuffer {{",
            f"    let n_7 = BigInt(blk * 8 - 1);",
            f"    let n_8 = BigInt(blk * 8);",
            f"    let ocp: BigInt = val;",
            f"    let n: int = 0;",
            f"    while (true) {{",
            f"        n += blk;",
            f"        let t_7 = ocp >> n_7;",
            f"        let t_8 = ocp >> n_8;",
            f"        if (t_7 == t_8) {{",
            f"            break;",
            f"        }}",
            f"        ocp = t_8;",
            f"    }}",
            f"    let buf = new ArrayBuffer(n);",
            f"    for (let i: int = 0; i < n; i++) {{",
            f"        buf.set(i, (val & 255n).getLong().toByte())",
            f"        val >>= 8n;",
            f"    }}",
            f"    return buf;",
            f"}}",
        )

        self.target.writelns(
            f"native function {self.mod.callback_invoke}(",
            f"    invokePtr: long, vtblPtr: long, dataPtr: long,",
            f"    arg_0?: Object, arg_1?: Object, arg_2?: Object, arg_3?: Object,",
            f"    arg_4?: Object, arg_5?: Object, arg_6?: Object, arg_7?: Object,",
            f"    arg_8?: Object, arg_9?: Object, arg_a?: Object, arg_b?: Object,",
            f"    arg_c?: Object, arg_d?: Object, arg_e?: Object, arg_f?: Object,",
            f"): Object | null | undefined;",
        )
        self.target.writelns(
            f"class {self.mod.callback_inner} {{",
            f"    invokePtr: long;",
            f"    vtblPtr: long;",
            f"    dataPtr: long;",
            f"    constructor(invokePtr: long, vtblPtr: long, dataPtr: long) {{",
            f"        this.invokePtr = invokePtr;",
            f"        this.vtblPtr = vtblPtr;",
            f"        this.dataPtr = dataPtr;",
            f"        {self.mod.obj_registry}.register(this, dataPtr);",
            f"    }}",
            f"    invoke(",
            f"        arg_0?: Object, arg_1?: Object, arg_2?: Object, arg_3?: Object,",
            f"        arg_4?: Object, arg_5?: Object, arg_6?: Object, arg_7?: Object,",
            f"        arg_8?: Object, arg_9?: Object, arg_a?: Object, arg_b?: Object,",
            f"        arg_c?: Object, arg_d?: Object, arg_e?: Object, arg_f?: Object,",
            f"    ): Object | null | undefined {{",
            f"        return {self.mod.callback_invoke}(",
            f"            this.invokePtr, this.vtblPtr, this.dataPtr,",
            f"            arg_0, arg_1, arg_2, arg_3,",
            f"            arg_4, arg_5, arg_6, arg_7,",
            f"            arg_8, arg_9, arg_a, arg_b,",
            f"            arg_c, arg_d, arg_e, arg_f,",
            f"        );",
            f"    }}",
            f"}}",
        )
        self.target.writelns(
            f"function {self.mod.callback_factory}(invokePtr: long, vtblPtr: long, dataPtr: long) {{",
            f"    let callback = new {self.mod.callback_inner}(invokePtr, vtblPtr, dataPtr);",
            f"    return callback.invoke;",
            f"}}",
        )
        self.target.writelns(
            f"native function {self.mod.obj_drop}(dataPtr: long): void;",
            f"native function {self.mod.obj_dup}(dataPtr: long): long;",
            f"const {self.mod.obj_registry} = new FinalizationRegistry<long>({self.mod.obj_drop});",
        )

        self.target.writelns(
            f"native function {self.mod.async_handler_on_fulfilled}(onFulfilledPtr: long, contextPtr: long, data: Any): void;",
            f"native function {self.mod.async_handler_on_rejected}(onRejectedPtr: long, contextPtr: long, error: Any): void;",
            f"native function {self.mod.async_handler_drop}(freePtr: long, contextPtr: long): void;",
            f"const {self.mod.async_handler_registry} = new FinalizationRegistry<[long, long]>((value: [long, long]) => {self.mod.async_handler_drop}(value[0], value[1]));",
        )
        self.target.writelns(
            f"class {self.mod.async_handler}<T> {{",
            f"    onFulfilledPtr: long;",
            f"    onRejectedPtr: long;",
            f"    contextPtr: long;",
            f"    constructor(onFulfilledPtr: long, onRejectedPtr: long, freePtr: long, contextPtr: long) {{",
            f"        this.onFulfilledPtr = onFulfilledPtr;",
            f"        this.onRejectedPtr = onRejectedPtr;",
            f"        this.contextPtr = contextPtr;",
            f"        {self.mod.async_handler_registry}.register(this, [freePtr, contextPtr]);",
            f"    }}",
            f"    onFulfilled(data: T): void {{",
            f"        {self.mod.async_handler_on_fulfilled}(this.onFulfilledPtr, this.contextPtr, data);",
            f"    }}",
            f"    onRejected(error: Error): void {{",
            f"        {self.mod.async_handler_on_rejected}(this.onRejectedPtr, this.contextPtr, error);",
            f"    }}",
            f"}}",
        )
        self.target.writelns(
            f"function {self.mod.completer_factory}<T>(onFulfilledPtr: long, onRejectedPtr: long, freePtr: long, contextPtr: long) {{",
            f"    let handler = new {self.mod.async_handler}<T>(onFulfilledPtr, onRejectedPtr, freePtr, contextPtr);",
            f"    return (error: {self.mod.BE_type} | null, data: T | undefined) => {{",
            f"        if (error) {{",
            f"            handler.onRejected(error);",
            f"        }} else {{",
            f"            handler.onFulfilled(data as T);",
            f"        }}",
            f"    }};",
            f"}}",
        )
        self.target.writelns(
            f"function {self.mod.future_completory}<T>(onFulfilledPtr: long, onRejectedPtr: long, freePtr: long, contextPtr: long, promise: Promise<T>) {{",
            f"    let handler = new {self.mod.async_handler}<T>(onFulfilledPtr, onRejectedPtr, freePtr, contextPtr);",
            f"    promise.then(",
            f"        handler.onFulfilled,",
            f"        handler.onRejected,",
            f"    );",
            f"}}",
        )


class StsNamespaceGenerator:
    def __init__(
        self,
        target: StsWriter,
        am: AnalysisManager,
        ns: ArkTsModuleOrNamespace,
    ):
        self.am = am
        self.target = target
        self.ns = ns

    def gen_namespace(self):
        for code in self.ns.injected_codes:
            self.target.write_block(code)
        for pkg in self.ns.packages:
            package_generator = StsPackageGenerator(self.am, self.target, pkg)
            package_generator.gen_package()
        for child_ns_name, child_ns in self.ns.children.items():
            sts_decl = f"namespace {child_ns_name}"
            if child_ns.is_default:
                sts_decl = f"export default {sts_decl}"
            else:
                sts_decl = f"export {sts_decl}"
            with self.target.indented(
                f"{sts_decl} {{",
                f"}}",
            ):
                child_ns_generator = StsNamespaceGenerator(
                    self.target,
                    self.am,
                    child_ns,
                )
                child_ns_generator.gen_namespace()


class StsPackageGenerator:
    def __init__(self, am: AnalysisManager, target: StsWriter, pkg: PackageDecl):
        self.am = am
        self.target = target
        self.pkg = pkg

        self.ctors_map: dict[str, list[GlobFuncDecl]] = {}
        self.statics_map: dict[str, list[GlobFuncDecl]] = {}
        self.glob_funcs: list[GlobFuncDecl] = []
        for func in self.pkg.functions:
            func_ani_info = GlobFuncAniInfo.get(self.am, func)
            if class_name := func_ani_info.static_scope:
                self.statics_map.setdefault(class_name, []).append(func)
            elif class_name := func_ani_info.ctor_scope:
                self.ctors_map.setdefault(class_name, []).append(func)
            else:
                self.glob_funcs.append(func)

    def gen_package(self):
        self.gen_func_natives()

        for enum in self.pkg.enums:
            enum_generator = StsEnumGenerator(self.am, self.target, enum)
            enum_generator.gen_enum()
        for union in self.pkg.unions:
            union_generator = StsUnionGenerator(self.am, self.target, union)
            union_generator.gen_union()
        for struct in self.pkg.structs:
            struct_generator = StsStructGenerator(
                self.am,
                self.target,
                struct,
                self.statics_map,
                self.ctors_map,
            )
            struct_generator.gen_struct()
        for iface in self.pkg.interfaces:
            iface_generator = StsIfaceGenerator(
                self.am,
                self.target,
                iface,
                self.statics_map,
                self.ctors_map,
            )
            iface_generator.gen_iface()
        self.gen_func_impls()

        self.gen_func_reverses()

    def gen_func_natives(self):
        for func in self.pkg.functions:
            func_nat_info = GlobFuncAniInfo.get(self.am, func)
            native_func_generator = StsNativeFuncGenerator(
                self.am,
                self.target,
                func,
                func_nat_info,
            )
            native_func_generator.gen_native_func()

    def gen_func_impls(self):
        func_overload_register = OverloadRegister()
        func_on_off_register = OnOffRegister()
        func_kind = GlobalKind()
        for func in self.glob_funcs:
            func_ani_info = GlobFuncAniInfo.get(self.am, func)
            any_func_generator = StsAnyFuncGenerator(
                self.am,
                self.target,
                func,
                func_ani_info,
                func_kind,
                "export default " if func_ani_info.is_default else "export ",
                func_overload_register,
                func_on_off_register,
            )
            any_func_generator.gen_any_func()
        for name, info in func_overload_register.infos.items():
            overload_func_generator = StsOverloadFuncGenerator(
                self.am,
                self.target,
                name,
                info,
                func_kind,
                "export ",
            )
            overload_func_generator.gen_overload_func()
        for name, info in func_on_off_register.infos.items():
            on_off_func_generator = StsOnOffFuncGenerator(
                self.am,
                self.target,
                name,
                info,
                func_kind,
                "export ",
            )
            on_off_func_generator.gen_full_on_off_func()

    def gen_func_reverses(self):
        func_kind = GlobalKind()
        for func in self.glob_funcs:
            func_rev_info = GlobFuncAniInfo.get(self.am, func)
            reverse_func_generator = StsReverseFuncGenerator(
                self.am,
                self.target,
                func,
                func_rev_info,
                func_kind,
            )
            reverse_func_generator.gen_reverse_func()


class StsEnumGenerator:
    def __init__(self, am: AnalysisManager, target: StsWriter, enum: EnumDecl):
        self.am = am
        self.target = target
        self.enum = enum

    def gen_enum(self):
        enum_ani_info = EnumAniInfo.get(self.am, self.enum)

        if isinstance(enum_ani_info, EnumConstAniInfo):
            self.gen_enum_const(enum_ani_info)
        if isinstance(enum_ani_info, EnumObjectAniInfo):
            self.gen_enum_decl(enum_ani_info)

    def gen_enum_const(self, enum_ani_info: EnumConstAniInfo):
        enum_ty_ani_info = TypeAniInfo.get(self.am, self.enum.ty)

        sts_decl = f"type {enum_ani_info.sts_type}"
        if enum_ani_info.is_default:
            sts_decl = f"export default {sts_decl}"
        else:
            sts_decl = f"export {sts_decl}"

        self.target.writelns(
            f"{sts_decl} = {enum_ty_ani_info.sts_type_in(self.target)};",
        )

        for item in self.enum.items:
            item_ani_info = EnumFieldAniInfo.get(self.am, item)
            self.target.writelns(
                f"export const {item_ani_info.sts_name}: {enum_ani_info.sts_type} = {render_ets_value(item.typed_value)};",
            )

    def gen_enum_decl(self, enum_ani_info: EnumObjectAniInfo):
        enum_ty_ani_info = TypeAniInfo.get(self.am, self.enum.ty)

        sts_decl = f"enum {enum_ani_info.sts_type}"
        # TODO: remove this condition when string type annotation is supported
        if isinstance(enum_ty_ani_info, ScalarTypeAniInfo):
            sts_decl = f"{sts_decl}: {enum_ty_ani_info.sts_type_in(self.target)}"
        if enum_ani_info.is_default:
            sts_decl = f"export default {sts_decl}"
        else:
            sts_decl = f"export {sts_decl}"

        with self.target.indented(
            f"{sts_decl} {{",
            f"}}",
        ):
            for item in self.enum.items:
                item_ani_info = EnumFieldAniInfo.get(self.am, item)
                self.target.writelns(
                    f"{item_ani_info.sts_name} = {render_ets_value(item.typed_value)},",
                )


class StsUnionGenerator:
    def __init__(self, am: AnalysisManager, target: StsWriter, union: UnionDecl):
        self.am = am
        self.target = target
        self.union = union

    def gen_union(self):
        union_ani_info = UnionAniInfo.get(self.am, self.union)

        sts_decl = f"type {union_ani_info.sts_type}"
        if union_ani_info.is_default:
            sts_decl = f"export default {sts_decl}"
        else:
            sts_decl = f"export {sts_decl}"

        sts_types = []
        for field in self.union.fields:
            field_ty_ani_info = TypeAniInfo.get(self.am, field.ty)
            sts_types.append(field_ty_ani_info.sts_type_in(self.target))
        sts_types_str = " | ".join(sts_types)

        self.target.writelns(
            f"{sts_decl} = {sts_types_str};",
        )


class StsStructGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        struct: StructDecl,
        funcs: dict[str, list[GlobFuncDecl]],
        ctors: dict[str, list[GlobFuncDecl]],
    ):
        self.am = am
        self.target = target
        self.struct = struct
        self.funcs = funcs
        self.ctors = ctors

    def gen_struct(self):
        struct_ani_info = StructAniInfo.get(self.am, self.struct)

        if isinstance(struct_ani_info, StructTupleAniInfo):
            self.gen_struct_tuple(struct_ani_info)
        if isinstance(struct_ani_info, StructObjectAniInfo):
            self.gen_struct_interface(struct_ani_info)
            self.gen_struct_class(struct_ani_info)
            self.gen_struct_factory(struct_ani_info)
            self.gen_struct_ctor_reverses(struct_ani_info)
            self.gen_struct_func_reverses(struct_ani_info)

    def gen_struct_tuple(self, struct_ani_info: StructTupleAniInfo):
        sts_decl = f"type {struct_ani_info.sts_type}"
        if struct_ani_info.is_default:
            sts_decl = f"export default {sts_decl}"
        else:
            sts_decl = f"export {sts_decl}"

        sts_types = []
        for field in self.struct.fields:
            field_ty_ani_info = TypeAniInfo.get(self.am, field.ty)
            sts_types.append(field_ty_ani_info.sts_type_in(self.target))
        sts_types_str = ", ".join(sts_types)

        self.target.writelns(
            f"{sts_decl} = [{sts_types_str}];",
        )

    def gen_struct_interface(self, struct_ani_info: StructObjectAniInfo):
        if struct_ani_info.is_class():
            # no interface
            return

        sts_decl = f"interface {struct_ani_info.sts_type}"
        if struct_ani_info.sts_iface_extends:
            extends = []
            for extend in struct_ani_info.sts_iface_extends:
                extend_ty = extend.ty
                extend_ani_info = TypeAniInfo.get(self.am, extend_ty)
                extends.append(extend_ani_info.sts_type_in(self.target))
            extends_str = ", ".join(extends) if extends else ""
            sts_decl = f"{sts_decl} extends {extends_str}"
        if struct_ani_info.is_default:
            sts_decl = f"export default {sts_decl}"
        else:
            sts_decl = f"export {sts_decl}"

        with self.target.indented(
            f"{sts_decl} {{",
            f"}}",
        ):
            # TODO: hack inject
            for injected in struct_ani_info.interface_injected_codes:
                self.target.write_block(injected)

            self.gen_struct_field_decls(struct_ani_info)

    def gen_struct_field_decls(self, struct_ani_info: StructObjectAniInfo):
        for field in struct_ani_info.sts_local_fields:
            readonly = "readonly " if ReadOnlyAttr.get(field) is not None else ""
            opt = "?" if OptionalAttr.get(field) else ""
            field_ani_info = StructFieldAniInfo.get(self.am, field)
            field_ty_ani_info = TypeAniInfo.get(self.am, field.ty)
            self.target.writelns(
                f"{readonly}{field_ani_info.sts_name}{opt}: {field_ty_ani_info.sts_type_in(self.target)};",
            )

    def gen_struct_class(self, struct_ani_info: StructObjectAniInfo):
        sts_decl = f"class {struct_ani_info.sts_impl}"
        if struct_ani_info.is_class():
            if struct_ani_info.sts_class_extends:
                inherits = []
                for inherit in struct_ani_info.sts_class_extends:
                    inherit_ty = inherit.ty
                    inherit_ani_info = TypeAniInfo.get(self.am, inherit_ty)
                    inherits.append(inherit_ani_info.sts_type_in(self.target))
                inherits_str = ", ".join(inherits) if inherits else ""
                sts_decl = f"{sts_decl} extends {inherits_str}"
            if struct_ani_info.sts_iface_extends:
                implements = []
                for implement in struct_ani_info.sts_iface_extends:
                    implement_ty = implement.ty
                    implement_ani_info = TypeAniInfo.get(self.am, implement_ty)
                    implements.append(implement_ani_info.sts_type_in(self.target))
                implements_str = ", ".join(implements) if implements else ""
                sts_decl = f"{sts_decl} implements {implements_str}"
            if struct_ani_info.is_default:
                sts_decl = f"export default {sts_decl}"
            else:
                sts_decl = f"export {sts_decl}"
        else:
            sts_decl = f"{sts_decl} implements {struct_ani_info.sts_type}"

        with self.target.indented(
            f"{sts_decl} {{",
            f"}}",
        ):
            # TODO: hack inject
            for injected in struct_ani_info.class_injected_codes:
                self.target.write_block(injected)

            self.gen_struct_field_impls(struct_ani_info)
            self.gen_struct_init_ctor(struct_ani_info)
            self.gen_struct_copy_ctor(struct_ani_info)
            self.gen_struct_ctor_impls(struct_ani_info)
            self.gen_struct_func_impls(struct_ani_info)

    def gen_struct_field_impls(self, struct_ani_info: StructObjectAniInfo):
        for final in [
            *struct_ani_info.sts_local_fields,
            *struct_ani_info.sts_iface_extend_fields,
        ]:
            readonly = "readonly " if ReadOnlyAttr.get(final) is not None else ""
            opt = "?" if OptionalAttr.get(final) else ""
            final_ani_info = StructFieldAniInfo.get(self.am, final)
            final_ty_ani_info = TypeAniInfo.get(self.am, final.ty)
            self.target.writelns(
                f"{readonly}{final_ani_info.sts_name}{opt}: {final_ty_ani_info.sts_type_in(self.target)};",
            )

    def gen_struct_init_ctor(self, struct_ani_info: StructObjectAniInfo):
        with self.target.indented(
            f"constructor(",
            f")",
        ):
            for parts in struct_ani_info.sorted_sts_all_fields:
                final = parts[-1]
                opt = "?" if OptionalAttr.get(final) else ""
                final_ani_info = StructFieldAniInfo.get(self.am, final)
                final_ty_ani_info = TypeAniInfo.get(self.am, final.ty)
                self.target.writelns(
                    f"{final_ani_info.sts_name}{opt}: {final_ty_ani_info.sts_type_in(self.target)},",
                )
        with self.target.indented(
            f"{{",
            f"}}",
        ):
            if struct_ani_info.sts_class_extends:
                finals = []
                for final in struct_ani_info.sts_class_extend_fields:
                    final_ani_info = StructFieldAniInfo.get(self.am, final)
                    finals.append(final_ani_info.sts_name)
                finals_str = ", ".join(finals)
                self.target.writelns(
                    f"super({finals_str});",
                )
            for final in [
                *struct_ani_info.sts_local_fields,
                *struct_ani_info.sts_iface_extend_fields,
            ]:
                final_ani_info = StructFieldAniInfo.get(self.am, final)
                self.target.writelns(
                    f"this.{final_ani_info.sts_name} = {final_ani_info.sts_name};",
                )

    def gen_struct_copy_ctor(self, struct_ani_info: StructObjectAniInfo):
        with self.target.indented(
            f"constructor(other: {struct_ani_info.sts_impl}) {{",
            f"}}",
        ):
            if struct_ani_info.sts_class_extends:
                finals = []
                for final in struct_ani_info.sts_class_extend_fields:
                    final_ani_info = StructFieldAniInfo.get(self.am, final)
                    finals.append(f"other.{final_ani_info.sts_name}")
                finals_str = ", ".join(finals)
                self.target.writelns(
                    f"super({finals_str});",
                )
            for final in [
                *struct_ani_info.sts_local_fields,
                *struct_ani_info.sts_iface_extend_fields,
            ]:
                final_ani_info = StructFieldAniInfo.get(self.am, final)
                self.target.writelns(
                    f"this.{final_ani_info.sts_name} = other.{final_ani_info.sts_name};",
                )

    def gen_struct_ctor_impls(self, struct_ani_info: StructObjectAniInfo):
        ctor_overload_register = OverloadRegister()
        ctor_on_off_register = OnOffRegister()
        ctor_kind = CtorKind(struct_ani_info.sts_impl)
        for ctor in self.ctors.get(struct_ani_info.sts_impl, []):
            ctor_nat_info = GlobFuncAniInfo.get(self.am, ctor)
            any_ctor_generator = StsAnyCtorGenerator(
                self.am,
                self.target,
                ctor,
                ctor_nat_info,
                ctor_kind,
                "",
                ctor_overload_register,
                ctor_on_off_register,
            )
            any_ctor_generator.gen_any_ctor()
        for name, info in ctor_overload_register.infos.items():
            overload_ctor_generator = StsOverloadCtorGenerator(
                self.am,
                self.target,
                name,
                info,
                ctor_kind,
                "",
            )
            overload_ctor_generator.gen_overload_ctor()
        for name, info in ctor_on_off_register.infos.items():
            on_off_ctor_generator = StsOnOffCtorGenerator(
                self.am,
                self.target,
                name,
                info,
                ctor_kind,
                "",
            )
            on_off_ctor_generator.gen_full_on_off_ctor()

    def gen_struct_func_impls(self, struct_ani_info: StructObjectAniInfo):
        func_overload_register = OverloadRegister()
        func_on_off_register = OnOffRegister()
        func_kind = StaticKind(struct_ani_info.sts_impl)
        for func in self.funcs.get(struct_ani_info.sts_impl, []):
            func_nat_info = GlobFuncAniInfo.get(self.am, func)
            any_func_generator = StsAnyFuncGenerator(
                self.am,
                self.target,
                func,
                func_nat_info,
                func_kind,
                "",
                func_overload_register,
                func_on_off_register,
            )
            any_func_generator.gen_any_func()
        for name, info in func_overload_register.infos.items():
            overload_func_generator = StsOverloadFuncGenerator(
                self.am,
                self.target,
                name,
                info,
                func_kind,
                "",
            )
            overload_func_generator.gen_overload_func()
        for name, info in func_on_off_register.infos.items():
            on_off_func_generator = StsOnOffFuncGenerator(
                self.am,
                self.target,
                name,
                info,
                func_kind,
                "",
            )
            on_off_func_generator.gen_full_on_off_func()

    def gen_struct_factory(self, struct_ani_info: StructObjectAniInfo):
        with self.target.indented(
            f"function {struct_ani_info.sts_factory}(",
            f"): {struct_ani_info.sts_impl}",
        ):
            for parts in struct_ani_info.sorted_sts_all_fields:
                final = parts[-1]
                opt = "?" if OptionalAttr.get(final) else ""
                final_ani_info = StructFieldAniInfo.get(self.am, final)
                final_ty_ani_info = TypeAniInfo.get(self.am, final.ty)
                self.target.writelns(
                    f"{final_ani_info.sts_name}{opt}: {final_ty_ani_info.sts_type_in(self.target)},",
                )
        with self.target.indented(
            f"{{",
            f"}}",
        ):
            finals = []
            for parts in struct_ani_info.sorted_sts_all_fields:
                final = parts[-1]
                final_ani_info = StructFieldAniInfo.get(self.am, final)
                finals.append(final_ani_info.sts_name)
            finals_str = ", ".join(finals)
            self.target.writelns(
                f"return new {struct_ani_info.sts_impl}({finals_str});",
            )

    def gen_struct_ctor_reverses(self, struct_ani_info: StructObjectAniInfo):
        ctor_kind = CtorKind(struct_ani_info.sts_impl)
        for ctor in self.ctors.get(struct_ani_info.sts_impl, []):
            ctor_rev_info = GlobFuncAniInfo.get(self.am, ctor)
            reverse_func_generator = StsReverseFuncGenerator(
                self.am,
                self.target,
                ctor,
                ctor_rev_info,
                ctor_kind,
            )
            reverse_func_generator.gen_reverse_func()

    def gen_struct_func_reverses(self, struct_ani_info: StructObjectAniInfo):
        func_kind = StaticKind(struct_ani_info.sts_impl)
        for func in self.funcs.get(struct_ani_info.sts_impl, []):
            func_rev_info = GlobFuncAniInfo.get(self.am, func)
            reverse_func_generator = StsReverseFuncGenerator(
                self.am,
                self.target,
                func,
                func_rev_info,
                func_kind,
            )
            reverse_func_generator.gen_reverse_func()


class StsIfaceGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        iface: IfaceDecl,
        funcs: dict[str, list[GlobFuncDecl]],
        ctors: dict[str, list[GlobFuncDecl]],
    ):
        self.am = am
        self.target = target
        self.iface = iface
        self.funcs = funcs
        self.ctors = ctors

    def gen_iface(self):
        iface_ani_info = IfaceAniInfo.get(self.am, self.iface)

        self.gen_iface_method_natives(iface_ani_info)
        self.gen_iface_interface(iface_ani_info)
        self.gen_iface_class(iface_ani_info)
        self.gen_iface_factory(iface_ani_info)
        self.gen_iface_method_reverses(iface_ani_info)
        self.gen_iface_ctor_reverses(iface_ani_info)
        self.gen_iface_func_reverses(iface_ani_info)

    def gen_iface_interface(self, iface_ani_info: IfaceAniInfo):
        if iface_ani_info.is_class():
            # no interface
            return

        sts_decl = f"interface {iface_ani_info.sts_type}"
        if iface_ani_info.sts_iface_extends:
            extends = []
            for extend in iface_ani_info.sts_iface_extends:
                extend_ty = extend.ty
                extend_ani_info = TypeAniInfo.get(self.am, extend_ty)
                extends.append(extend_ani_info.sts_type_in(self.target))
            extends_str = ", ".join(extends) if extends else ""
            sts_decl = f"{sts_decl} extends {extends_str}"
        if iface_ani_info.is_default:
            sts_decl = f"export default {sts_decl}"
        else:
            sts_decl = f"export {sts_decl}"

        with self.target.indented(
            f"{sts_decl} {{",
            f"}}",
        ):
            # TODO: hack inject
            for injected in iface_ani_info.interface_injected_codes:
                self.target.write_block(injected)

            self.gen_iface_method_decls(iface_ani_info)

    def gen_iface_method_decls(self, iface_ani_info: IfaceAniInfo):
        method_overload_register = OverloadRegister()
        method_on_off_register = OnOffRegister()
        method_kind = InterfaceKind(iface_ani_info.sts_type)
        for method in self.iface.methods:
            any_func_decl_generator = StsAnyFuncDeclGenerator(
                self.am,
                self.target,
                method,
                method_kind,
                "",
                method_overload_register,
                method_on_off_register,
            )
            any_func_decl_generator.gen_any_func_decl()
        for name, info in method_overload_register.infos.items():
            overload_func_generator = StsOverloadFuncGenerator(
                self.am,
                self.target,
                name,
                info,
                method_kind,
                "",
            )
            overload_func_generator.gen_overload_func()
        for name, info in method_on_off_register.infos.items():
            on_off_func_generator = StsOnOffFuncGenerator(
                self.am,
                self.target,
                name,
                info,
                method_kind,
                "",
            )
            on_off_func_generator.gen_half_on_off_func()

    def gen_iface_class(self, iface_ani_info: IfaceAniInfo):
        sts_decl = f"class {iface_ani_info.sts_impl}"
        if iface_ani_info.is_class():
            if iface_ani_info.sts_class_extends:
                inherits = []
                for inherit in iface_ani_info.sts_class_extends:
                    inherit_ty = inherit.ty
                    inherit_ani_info = TypeAniInfo.get(self.am, inherit_ty)
                    inherits.append(inherit_ani_info.sts_type_in(self.target))
                inherits_str = ", ".join(inherits) if inherits else ""
                sts_decl = f"{sts_decl} extends {inherits_str}"
            if iface_ani_info.sts_iface_extends:
                implements = []
                for implement in iface_ani_info.sts_iface_extends:
                    implement_ty = implement.ty
                    implement_ani_info = TypeAniInfo.get(self.am, implement_ty)
                    implements.append(implement_ani_info.sts_type_in(self.target))
                implements_str = ", ".join(implements) if implements else ""
                sts_decl = f"{sts_decl} implements {implements_str}"
            if iface_ani_info.is_default:
                sts_decl = f"export default {sts_decl}"
            else:
                sts_decl = f"export {sts_decl}"
        else:
            sts_decl = f"{sts_decl} implements {iface_ani_info.sts_type}"

        with self.target.indented(
            f"{sts_decl} {{",
            f"}}",
        ):
            # TODO: hack inject
            for injected in iface_ani_info.class_injected_codes:
                self.target.write_block(injected)

            self.gen_iface_init_ctor(iface_ani_info)
            self.gen_iface_copy_ctor(iface_ani_info)
            self.gen_iface_method_impls(iface_ani_info)
            self.gen_iface_ctor_impls(iface_ani_info)
            self.gen_iface_func_impls(iface_ani_info)

    def gen_iface_init_ctor(self, iface_ani_info: IfaceAniInfo):
        package_ani_info = PackageAniInfo.get(self.am, self.iface.parent_pkg)

        if not iface_ani_info.sts_class_extends:
            self.target.writelns(
                f"{iface_ani_info.vtbl_ptr}: long;",
                f"{iface_ani_info.data_ptr}: long;",
            )
            with self.target.indented(
                f"{iface_ani_info.register}(): void {{",
                f"}}",
            ):
                self.target.writelns(
                    f"{package_ani_info.ns.mod.obj_registry}.register(this, this.{iface_ani_info.data_ptr});",
                )
            with self.target.indented(
                f"constructor(vtblPtr: long, dataPtr: long) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"this.{iface_ani_info.vtbl_ptr} = vtblPtr;",
                    f"this.{iface_ani_info.data_ptr} = dataPtr;",
                    f"this.{iface_ani_info.register}();",
                )
        else:
            with self.target.indented(
                f"constructor(vtblPtr: long, dataPtr: long) {{",
                f"}}",
            ):
                self.target.writelns(
                    f"super(vtblPtr, dataPtr);",
                )

    def gen_iface_copy_ctor(self, iface_ani_info: IfaceAniInfo):
        package_ani_info = PackageAniInfo.get(self.am, self.iface.parent_pkg)

        with self.target.indented(
            f"constructor(other: {iface_ani_info.sts_impl}) {{",
            f"}}",
        ):
            self.target.writelns(
                f"this(other.{iface_ani_info.vtbl_ptr}, {package_ani_info.ns.mod.obj_dup}(other.{iface_ani_info.data_ptr}));",
            )

    def gen_iface_method_natives(self, iface_ani_info: IfaceAniInfo):
        iface_abi_info = IfaceAbiInfo.get(self.am, self.iface)
        for ancestor in iface_abi_info.ancestor_infos:
            for method in ancestor.methods:
                method_nat_info = IfaceThunkAniInfo.get(self.am, IfaceThunkKey(self.iface, method))  # fmt: skip
                native_func_generator = StsNativeFuncGenerator(
                    self.am,
                    self.target,
                    method,
                    method_nat_info,
                )
                native_func_generator.gen_native_func()

    def gen_iface_method_impls(self, iface_ani_info: IfaceAniInfo):
        method_overload_register = OverloadRegister()
        method_on_off_register = OnOffRegister()
        method_kind = InterfaceKind(iface_ani_info.sts_type)
        iface_abi_info = IfaceAbiInfo.get(self.am, self.iface)
        for ancestor in iface_abi_info.ancestor_infos:
            for method in ancestor.methods:
                method_nat_info = IfaceThunkAniInfo.get(self.am, IfaceThunkKey(self.iface, method))  # fmt: skip
                any_func_generator = StsAnyFuncGenerator(
                    self.am,
                    self.target,
                    method,
                    method_nat_info,
                    method_kind,
                    "",
                    method_overload_register,
                    method_on_off_register,
                )
                any_func_generator.gen_any_func()
        for name, info in method_overload_register.infos.items():
            overload_func_generator = StsOverloadFuncGenerator(
                self.am,
                self.target,
                name,
                info,
                method_kind,
                "",
            )
            overload_func_generator.gen_overload_func()
        for name, info in method_on_off_register.infos.items():
            on_off_func_generator = StsOnOffFuncGenerator(
                self.am,
                self.target,
                name,
                info,
                method_kind,
                "",
            )
            on_off_func_generator.gen_half_on_off_func()

    def gen_iface_ctor_impls(self, iface_ani_info: IfaceAniInfo):
        ctor_overload_register = OverloadRegister()
        ctor_on_off_register = OnOffRegister()
        ctor_kind = CtorKind(iface_ani_info.sts_impl)
        for ctor in self.ctors.get(iface_ani_info.sts_impl, []):
            ctor_nat_info = GlobFuncAniInfo.get(self.am, ctor)
            any_ctor_generator = StsAnyCtorGenerator(
                self.am,
                self.target,
                ctor,
                ctor_nat_info,
                ctor_kind,
                "",
                ctor_overload_register,
                ctor_on_off_register,
            )
            any_ctor_generator.gen_any_ctor()
        for name, info in ctor_overload_register.infos.items():
            overload_ctor_generator = StsOverloadCtorGenerator(
                self.am,
                self.target,
                name,
                info,
                ctor_kind,
                "",
            )
            overload_ctor_generator.gen_overload_ctor()
        for name, info in ctor_on_off_register.infos.items():
            on_off_ctor_generator = StsOnOffCtorGenerator(
                self.am,
                self.target,
                name,
                info,
                ctor_kind,
                "",
            )
            on_off_ctor_generator.gen_full_on_off_ctor()

    def gen_iface_func_impls(self, iface_ani_info: IfaceAniInfo):
        func_overload_register = OverloadRegister()
        func_on_off_register = OnOffRegister()
        func_kind = StaticKind(iface_ani_info.sts_impl)
        for func in self.funcs.get(iface_ani_info.sts_impl, []):
            func_nat_info = GlobFuncAniInfo.get(self.am, func)
            any_func_generator = StsAnyFuncGenerator(
                self.am,
                self.target,
                func,
                func_nat_info,
                func_kind,
                "",
                func_overload_register,
                func_on_off_register,
            )
            any_func_generator.gen_any_func()
        for name, info in func_overload_register.infos.items():
            overload_func_generator = StsOverloadFuncGenerator(
                self.am,
                self.target,
                name,
                info,
                func_kind,
                "",
            )
            overload_func_generator.gen_overload_func()
        for name, info in func_on_off_register.infos.items():
            on_off_func_generator = StsOnOffFuncGenerator(
                self.am,
                self.target,
                name,
                info,
                func_kind,
                "",
            )
            on_off_func_generator.gen_full_on_off_func()

    def gen_iface_factory(self, iface_ani_info: IfaceAniInfo):
        with self.target.indented(
            f"function {iface_ani_info.sts_factory}(vtblPtr: long, dataPtr: long): {iface_ani_info.sts_impl} {{",
            f"}}",
        ):
            self.target.writelns(
                f"return new {iface_ani_info.sts_impl}(vtblPtr, dataPtr);",
            )

    def gen_iface_method_reverses(self, iface_ani_info: IfaceAniInfo):
        method_kind = InterfaceKind(iface_ani_info.sts_type)
        for method in self.iface.methods:
            method_rev_info = IfaceMethodAniInfo.get(self.am, method)
            reverse_func_generator = StsReverseFuncGenerator(
                self.am,
                self.target,
                method,
                method_rev_info,
                method_kind,
            )
            reverse_func_generator.gen_reverse_func()

    def gen_iface_ctor_reverses(self, iface_ani_info: IfaceAniInfo):
        ctor_kind = CtorKind(iface_ani_info.sts_impl)
        for ctor in self.ctors.get(iface_ani_info.sts_impl, []):
            ctor_rev_info = GlobFuncAniInfo.get(self.am, ctor)
            reverse_func_generator = StsReverseFuncGenerator(
                self.am,
                self.target,
                ctor,
                ctor_rev_info,
                ctor_kind,
            )
            reverse_func_generator.gen_reverse_func()

    def gen_iface_func_reverses(self, iface_ani_info: IfaceAniInfo):
        func_kind = StaticKind(iface_ani_info.sts_impl)
        for func in self.funcs.get(iface_ani_info.sts_impl, []):
            func_rev_info = GlobFuncAniInfo.get(self.am, func)
            reverse_func_generator = StsReverseFuncGenerator(
                self.am,
                self.target,
                func,
                func_rev_info,
                func_kind,
            )
            reverse_func_generator.gen_reverse_func()


class StsNativeFuncGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        func: GlobFuncDecl | IfaceMethodDecl,
        func_nat_info: GlobFuncAniInfo | IfaceThunkAniInfo,
    ):
        self.am = am
        self.target = target
        self.func = func
        self.func_nat_info = func_nat_info

    def gen_native_func(self):
        params_sts = self.func_nat_info.sts_native_base_params.copy()
        for param in self.func.params:
            param_ani_info = ParamAniInfo.get(self.am, param)
            param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
            params_sts.append(
                f"{param_ani_info.sts_name}: {param_ty_ani_info.sts_type_in(self.target)}"
            )
        params_sts_str = ", ".join(params_sts)
        if isinstance(return_ty := self.func.return_ty, NonVoidType):
            return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
            return_ty_sts_name = return_ty_ani_info.sts_type_in(self.target)
        else:
            return_ty_sts_name = "void"

        self.target.writelns(
            f"native function {self.func_nat_info.sts_native}({params_sts_str}): {return_ty_sts_name};",
        )


class StsAnyFuncDeclGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        func: GlobFuncDecl | IfaceMethodDecl,
        func_kind: FuncKind,
        decl_prefix: str,
        overload_register: OverloadRegister,
        on_off_register: OnOffRegister,
    ):
        self.am = am
        self.target = target
        self.func = func
        self.func_kind = func_kind
        self.decl_prefix = decl_prefix
        self.overload_register = overload_register
        self.on_off_register = on_off_register

    def gen_any_func_decl(self):
        func_ani_info = NamedCallableAniInfo.get(self.am, self.func)
        params_ty_sts_sig = []
        params_ty_sts_name = []
        params_sts = []
        args_sts = []
        for param in func_ani_info.sts_params:
            opt = "?" if OptionalAttr.get(param) else ""
            param_ani_info = ParamAniInfo.get(self.am, param)
            param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
            params_ty_sts_sig.append(param_ty_ani_info.ets_type.sig)
            params_ty_sts_name.append(param_ty_ani_info.sts_type_in(self.target))
            params_sts.append(
                f"{param_ani_info.sts_name}{opt}: {param_ty_ani_info.sts_type_in(self.target)}"
            )
            args_sts.append(param_ani_info.sts_name)
        if isinstance(return_ty := self.func.return_ty, NonVoidType):
            return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
            return_ty_sts_name = return_ty_ani_info.sts_type_in(self.target)
        else:
            return_ty_sts_name = "void"

        if (norm_name := func_ani_info.norm_name) is not None:
            self.gen_normal_func_decl(
                norm_name,
                func_ani_info.gen_async_name,
                func_ani_info.gen_promise_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                func_ani_info.overload_name,
                func_ani_info.on_off_pair,
            )
        if (async_name := func_ani_info.async_name) is not None:
            self.gen_async_func_decl(
                async_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                func_ani_info.overload_name,
                func_ani_info.on_off_pair,
            )
        if (promise_name := func_ani_info.promise_name) is not None:
            self.gen_promise_func_decl(
                promise_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                func_ani_info.overload_name,
                func_ani_info.on_off_pair,
            )
        if (get_name := func_ani_info.get_name) is not None:
            self.gen_getter_decl(
                get_name,
                params_sts,
                return_ty_sts_name,
            )
        if (set_name := func_ani_info.set_name) is not None:
            self.gen_setter_decl(
                set_name,
                params_sts,
                return_ty_sts_name,
            )

    def gen_getter_decl(
        self,
        get_name: str,
        params_sts: list[str],
        return_ty_sts_name: str,
    ):
        params_sts_str = ", ".join(params_sts)

        self.target.writelns(
            f"{self.decl_prefix}{self.func_kind.get_prefix}{get_name}({params_sts_str}): {return_ty_sts_name};",
        )

    def gen_setter_decl(
        self,
        set_name: str,
        params_sts: list[str],
        return_ty_sts_name: str,
    ):
        params_sts_str = ", ".join(params_sts)

        self.target.writelns(
            f"{self.decl_prefix}{self.func_kind.set_prefix}{set_name}({params_sts_str});",
        )

    def gen_normal_func_decl(
        self,
        norm_name: str,
        async_name: str | None,
        promise_name: str | None,
        params_ty_sts_sig: list[str],
        params_sts: list[str],
        params_ty_sts_name: list[str],
        return_ty_sts_name: str,
        overload_name: str | None,
        on_off_pair: tuple[str, str] | None,
    ):
        params_sts_str = ", ".join(params_sts)

        self.target.writelns(
            f"{self.decl_prefix}{self.func_kind.func_prefix}{norm_name}({params_sts_str}): {return_ty_sts_name};",
        )

        if overload_name is not None:
            self.overload_register.register(norm_name, overload_name)
        if on_off_pair is not None:
            self.on_off_register.register(
                on_off_pair,
                params_ty_sts_sig,
                norm_name,
                params_ty_sts_name,
                return_ty_sts_name,
            )

        if promise_name is not None:
            self.gen_promise_func_decl(
                promise_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                None,
                None,
            )
        if async_name is not None:
            self.gen_async_func_decl(
                async_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                None,
                None,
            )

    def gen_promise_func_decl(
        self,
        promise_name: str,
        params_ty_sts_sig: list[str],
        params_sts: list[str],
        params_ty_sts_name: list[str],
        return_ty_sts_name: str,
        overload_name: str | None,
        on_off_pair: tuple[str, str] | None,
    ):
        params_sts_str = ", ".join(params_sts)
        promise_ty = f"Promise<{return_ty_sts_name}>"

        self.target.writelns(
            f"{self.decl_prefix}{self.func_kind.func_prefix}{promise_name}({params_sts_str}): {promise_ty};",
        )

        if overload_name is not None:
            self.overload_register.register(promise_name, overload_name)
        if on_off_pair is not None:
            self.on_off_register.register(
                on_off_pair,
                params_ty_sts_sig,
                promise_name,
                params_ty_sts_name,
                promise_ty,
            )

    def gen_async_func_decl(
        self,
        async_name: str,
        params_ty_sts_sig: list[str],
        params_sts: list[str],
        params_ty_sts_name: list[str],
        return_ty_sts_name: str,
        overload_name: str | None,
        on_off_pair: tuple[str, str] | None,
    ):
        pkg_ani_info = PackageAniInfo.get(self.am, self.func.parent_pkg)

        cbname = "callback"
        callback_ty_sts_sig = "C{std.core.Function2}"
        callback_ty_sts_name = f"{pkg_ani_info.ns.mod.AC_type}<{return_ty_sts_name}>"
        callback_sts = f"{cbname}: {callback_ty_sts_name}"
        params_with_callback_sts_str = ", ".join([*params_sts, callback_sts])

        self.target.writelns(
            f"{self.decl_prefix}{self.func_kind.func_prefix}{async_name}({params_with_callback_sts_str}): void;",
        )

        if overload_name is not None:
            self.overload_register.register(async_name, overload_name)
        if on_off_pair is not None:
            self.on_off_register.register(
                on_off_pair,
                [*params_ty_sts_sig, callback_ty_sts_sig],
                async_name,
                [*params_ty_sts_name, callback_ty_sts_name],
                "void",
            )


class StsAnyFuncGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        func: GlobFuncDecl | IfaceMethodDecl,
        func_nat_info: GlobFuncAniInfo | IfaceThunkAniInfo,
        func_kind: FuncKind,
        mode_prefix: str,
        overload_register: OverloadRegister,
        on_off_register: OnOffRegister,
    ):
        self.am = am
        self.target = target
        self.func = func
        self.func_nat_info = func_nat_info
        self.func_kind = func_kind
        self.mode_prefix = mode_prefix
        self.overload_register = overload_register
        self.on_off_register = on_off_register

    def gen_any_func(self):
        func_ani_info = NamedCallableAniInfo.get(self.am, self.func)
        params_ty_sts_sig = []
        params_ty_sts_name = []
        params_sts = []
        args_sts = []
        for param in func_ani_info.sts_params:
            opt = "?" if OptionalAttr.get(param) else ""
            param_ani_info = ParamAniInfo.get(self.am, param)
            param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
            params_ty_sts_sig.append(param_ty_ani_info.ets_type.sig)
            params_ty_sts_name.append(param_ty_ani_info.sts_type_in(self.target))
            params_sts.append(
                f"{param_ani_info.sts_name}{opt}: {param_ty_ani_info.sts_type_in(self.target)}"
            )
            args_sts.append(param_ani_info.sts_name)
        args_sts = [
            *self.func_nat_info.sts_native_base_args,
            *func_ani_info.as_native_args(args_sts),
        ]
        args_sts_str = ", ".join(args_sts)
        result_sts = f"{self.func_nat_info.sts_native}({args_sts_str})"
        if isinstance(return_ty := self.func.return_ty, NonVoidType):
            return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
            return_ty_sts_name = return_ty_ani_info.sts_type_in(self.target)
        else:
            return_ty_sts_name = "void"

        if (norm_name := func_ani_info.norm_name) is not None:
            self.gen_normal_func(
                norm_name,
                func_ani_info.gen_async_name,
                func_ani_info.gen_promise_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                result_sts,
                func_ani_info.overload_name,
                func_ani_info.on_off_pair,
            )
        if (promise_name := func_ani_info.promise_name) is not None:
            self.gen_promise_func(
                promise_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                result_sts,
                func_ani_info.overload_name,
                func_ani_info.on_off_pair,
            )
        if (async_name := func_ani_info.async_name) is not None:
            self.gen_async_func(
                async_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                result_sts,
                func_ani_info.overload_name,
                func_ani_info.on_off_pair,
            )
        if (get_name := func_ani_info.get_name) is not None:
            self.gen_getter(
                get_name,
                params_sts,
                return_ty_sts_name,
                result_sts,
            )
        if (set_name := func_ani_info.set_name) is not None:
            self.gen_setter(
                set_name,
                params_sts,
                return_ty_sts_name,
                result_sts,
            )

    def gen_getter(
        self,
        get_name: str,
        params_sts: list[str],
        return_ty_sts_name: str,
        result_sts: str,
    ):
        params_sts_str = ", ".join(params_sts)

        with self.target.indented(
            f"{self.mode_prefix}{self.func_kind.get_prefix}{get_name}({params_sts_str}): {return_ty_sts_name} {{",
            f"}}",
        ):
            self.target.writelns(
                f"return {result_sts};",
            )

    def gen_setter(
        self,
        set_name: str,
        params_sts: list[str],
        return_ty_sts_name: str,
        result_sts: str,
    ):
        params_sts_str = ", ".join(params_sts)

        with self.target.indented(
            f"{self.mode_prefix}{self.func_kind.set_prefix}{set_name}({params_sts_str}) {{",
            f"}}",
        ):
            self.target.writelns(
                f"return {result_sts};",
            )

    def gen_normal_func(
        self,
        norm_name: str,
        async_name: str | None,
        promise_name: str | None,
        params_ty_sts_sig: list[str],
        params_sts: list[str],
        params_ty_sts_name: list[str],
        return_ty_sts_name: str,
        result_sts: str,
        overload_name: str | None,
        on_off_pair: tuple[str, str] | None,
    ):
        params_sts_str = ", ".join(params_sts)

        with self.target.indented(
            f"{self.mode_prefix}{self.func_kind.func_prefix}{norm_name}({params_sts_str}): {return_ty_sts_name} {{",
            f"}}",
        ):
            self.target.writelns(
                f"return {result_sts};",
            )

        if overload_name is not None:
            self.overload_register.register(norm_name, overload_name)
        if on_off_pair is not None:
            self.on_off_register.register(
                on_off_pair,
                params_ty_sts_sig,
                norm_name,
                params_ty_sts_name,
                return_ty_sts_name,
            )

        if promise_name is not None:
            self.gen_promise_func(
                promise_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                result_sts,
                None,
                None,
            )
        if async_name is not None:
            self.gen_async_func(
                async_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                result_sts,
                None,
                None,
            )

    def gen_promise_func(
        self,
        promise_name: str,
        params_ty_sts_sig: list[str],
        params_sts: list[str],
        params_ty_sts_name: list[str],
        return_ty_sts_name: str,
        result_sts: str,
        overload_name: str | None,
        on_off_pair: tuple[str, str] | None,
    ):
        params_sts_str = ", ".join(params_sts)
        promise_ty_sts_name = f"Promise<{return_ty_sts_name}>"

        with self.target.indented(
            f"{self.mode_prefix}{self.func_kind.func_prefix}{promise_name}({params_sts_str}): {promise_ty_sts_name} {{",
            f"}}",
        ):
            with self.target.indented(
                f"return new {promise_ty_sts_name}((resolve, reject): void => {{",
                f"}});",
            ):
                with self.target.indented(
                    f"launch() {{",
                    f"}}",
                ):
                    with self.target.indented(
                        f"try {{",
                        f"}}",
                    ):
                        if return_ty_sts_name == "void":
                            self.target.writelns(
                                f"{result_sts};",
                                f"let res = undefined;",
                            )
                        else:
                            self.target.writelns(
                                f"let res = {result_sts};",
                            )
                        self.target.writelns(
                            f"resolve(res);",
                        )
                    with self.target.indented(
                        f"catch(err) {{",
                        f"}};",
                    ):
                        self.target.writelns(
                            f"reject(err as Error);",
                        )

        if overload_name is not None:
            self.overload_register.register(promise_name, overload_name)
        if on_off_pair is not None:
            self.on_off_register.register(
                on_off_pair,
                params_ty_sts_sig,
                promise_name,
                params_ty_sts_name,
                promise_ty_sts_name,
            )

    def gen_async_func(
        self,
        async_name: str,
        params_ty_sts_sig: list[str],
        params_sts: list[str],
        params_ty_sts_name: list[str],
        return_ty_sts_name: str,
        result_sts: str,
        overload_name: str | None,
        on_off_pair: tuple[str, str] | None,
    ):
        pkg_ani_info = PackageAniInfo.get(self.am, self.func.parent_pkg)

        cbname = "callback"
        callback_ty_sts_sig = "C{std.core.Function2}"
        callback_ty_sts_name = f"{pkg_ani_info.ns.mod.AC_type}<{return_ty_sts_name}>"
        callback_sts = f"{cbname}: {callback_ty_sts_name}"
        params_with_callback_sts_str = ", ".join([*params_sts, callback_sts])

        with self.target.indented(
            f"{self.mode_prefix}{self.func_kind.func_prefix}{async_name}({params_with_callback_sts_str}): void {{",
            f"}}",
        ):
            with self.target.indented(
                f"launch() {{",
                f"}}",
            ):
                with self.target.indented(
                    f"try {{",
                    f"}}",
                ):
                    if return_ty_sts_name == "void":
                        self.target.writelns(
                            f"{result_sts};",
                            f"let res = undefined;",
                        )
                    else:
                        self.target.writelns(
                            f"let res = {result_sts};",
                        )
                    self.target.writelns(
                        f"{cbname}(null, res);",
                    )
                with self.target.indented(
                    f"catch(err) {{",
                    f"}}",
                ):
                    self.target.writelns(
                        f"{cbname}(err as {pkg_ani_info.ns.mod.BE_type}, undefined);",
                    )

        if overload_name is not None:
            self.overload_register.register(async_name, overload_name)
        if on_off_pair is not None:
            self.on_off_register.register(
                on_off_pair,
                [*params_ty_sts_sig, callback_ty_sts_sig],
                async_name,
                [*params_ty_sts_name, callback_ty_sts_name],
                "void",
            )


class StsAnyCtorGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        ctor: GlobFuncDecl,
        ctor_nat_info: GlobFuncAniInfo | IfaceThunkAniInfo,
        ctor_kind: CtorKind,
        mode_prefix: str,
        overload_register: OverloadRegister,
        on_off_register: OnOffRegister,
    ):
        self.am = am
        self.target = target
        self.ctor = ctor
        self.ctor_nat_info = ctor_nat_info
        self.ctor_kind = ctor_kind
        self.mode_prefix = mode_prefix
        self.overload_register = overload_register
        self.on_off_register = on_off_register

    def gen_any_ctor(self):
        ctor_ani_info = NamedCallableAniInfo.get(self.am, self.ctor)
        params_ty_sts_sig = []
        params_ty_sts_name = []
        params_sts = []
        args_sts = []
        for param in ctor_ani_info.sts_params:
            opt = "?" if OptionalAttr.get(param) else ""
            param_ani_info = ParamAniInfo.get(self.am, param)
            param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
            params_ty_sts_sig.append(param_ty_ani_info.ets_type.sig)
            params_ty_sts_name.append(param_ty_ani_info.sts_type_in(self.target))
            params_sts.append(
                f"{param_ani_info.sts_name}{opt}: {param_ty_ani_info.sts_type_in(self.target)}"
            )
            args_sts.append(param_ani_info.sts_name)
        args_sts = [
            *self.ctor_nat_info.sts_native_base_args,
            *ctor_ani_info.as_native_args(args_sts),
        ]
        args_sts_str = ", ".join(args_sts)
        result_sts = f"{self.ctor_nat_info.sts_native}({args_sts_str})"
        if isinstance(return_ty := self.ctor.return_ty, NonVoidType):
            return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
            return_ty_sts_name = return_ty_ani_info.sts_type_in(self.target)
        else:
            return_ty_sts_name = "void"

        if (ctor_name := ctor_ani_info.norm_name) is not None:
            self.gen_ctor(
                ctor_name,
                params_ty_sts_sig,
                params_sts,
                params_ty_sts_name,
                return_ty_sts_name,
                result_sts,
                ctor_ani_info.overload_name,
                ctor_ani_info.on_off_pair,
            )

    def gen_ctor(
        self,
        ctor_name: str,
        params_ty_sts_sig: list[str],
        params_sts: list[str],
        params_ty_sts_name: list[str],
        return_ty_sts_name: str,
        result_sts: str,
        overload_name: str | None,
        on_off_pair: tuple[str, str] | None,
    ):
        params_sts_str = ", ".join(params_sts)

        with self.target.indented(
            f"{self.mode_prefix}{self.ctor_kind.func_prefix}{ctor_name}({params_sts_str}) {{",
            f"}}",
        ):
            self.target.writelns(
                f"this({result_sts});",
            )

        if overload_name is not None:
            self.overload_register.register(ctor_name, overload_name)
        if on_off_pair is not None:
            self.on_off_register.register(
                on_off_pair,
                params_ty_sts_sig,
                ctor_name,
                params_ty_sts_name,
                "void",
            )


class StsOverloadFuncGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        overload_name: str,
        overload_info: OverloadInfo,
        func_kind: FuncKind,
        mode_prefix: str,
    ):
        self.am = am
        self.target = target
        self.overload_name = overload_name
        self.overload_info = overload_info
        self.func_kind = func_kind
        self.mode_prefix = mode_prefix

    def gen_overload_func(self):
        with self.target.indented(
            f"{self.mode_prefix}{self.func_kind.overload_prefix}{self.overload_name} {{",
            f"}}",
        ):
            for orig in self.overload_info:
                self.target.writelns(
                    f"{orig},",
                )


class StsOnOffFuncGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        on_off_name: str,
        on_off_info: OnOffInfo,
        func_kind: FuncKind,
        mode_prefix: str,
    ):
        self.am = am
        self.target = target
        self.on_off_name = on_off_name
        self.on_off_info = on_off_info
        self.func_kind = func_kind
        self.mode_prefix = mode_prefix

    def gen_full_on_off_func(self):
        if not any(len(funcs) > 1 for funcs in self.on_off_info.values()):
            return self.gen_half_on_off_func()
        params_len = max(
            len(params_ty_sts_sig) for params_ty_sts_sig in self.on_off_info
        )
        args_sts = [f"p_{i}" for i in range(params_len)]
        params_sts = ["type: Object", *(f"{arg_sts}?: Object" for arg_sts in args_sts)]
        params_sts_str = ", ".join(params_sts)

        with self.target.indented(
            f"{self.mode_prefix}{self.func_kind.func_prefix}{self.on_off_name}({params_sts_str}): Any {{",
            f"}}",
        ):
            with self.target.indented(
                f"switch (type as string) {{",
                f"}}",
            ):
                for on_off_cases in self.on_off_info.values():
                    for on_off_type, (
                        orig_name,
                        params_ty_sts_name,
                        _,
                    ) in on_off_cases.items():
                        args_sts_str = ", ".join(
                            f"{arg_sts} as {param_ty_sts_name}"
                            for arg_sts, param_ty_sts_name in zip(
                                args_sts, params_ty_sts_name, strict=False
                            )
                        )
                        self.target.write_label(f'case "{on_off_type}":')
                        self.target.writelns(
                            f"return {self.func_kind.call_from_local(orig_name)}({args_sts_str});",
                        )
                self.target.writelns(
                    f"default: throw new Error(`Unknown tag: ${{type}}`);",
                )

    def gen_half_on_off_func(self):
        for params_ty_sts_sig, on_off_cases in self.on_off_info.items():
            params_ty_sts_sum: list[set[str]] = [
                set() for _ in range(len(params_ty_sts_sig))
            ]
            return_ty_sts_sum: set[str] = set()
            for _, params_ty_sts_name, return_ty_sts_name in on_off_cases.values():
                for param_ty_sts_sum, param_ty_sts_name in zip(
                    params_ty_sts_sum, params_ty_sts_name, strict=True
                ):
                    param_ty_sts_sum.add(param_ty_sts_name)
                return_ty_sts_sum.add(return_ty_sts_name)
            params_sts = ["type: string"]
            args_sts = []
            for index, param_ty_sts_sum in enumerate(params_ty_sts_sum):
                arg_sts = f"p_{index}"
                param_ty = " | ".join(param_ty_sts_sum)
                params_sts.append(f"{arg_sts}?: {param_ty}")
                args_sts.append(arg_sts)
            params_sts_str = ", ".join(params_sts)
            args_sts_str = ", ".join(args_sts)
            return_ty = " | ".join(return_ty_sts_sum)

            with self.target.indented(
                f"{self.mode_prefix}{self.func_kind.func_prefix}{self.on_off_name}({params_sts_str}): {return_ty} {{",
                f"}}",
            ):
                with self.target.indented(
                    f"switch (type) {{",
                    f"}}",
                ):
                    for on_off_type, (
                        orig_name,
                        params_ty_sts_name,
                        _,
                    ) in on_off_cases.items():
                        args_sts_str = ", ".join(
                            f"{arg_sts} as {param_ty_sts_name}"
                            for arg_sts, param_ty_sts_name in zip(
                                args_sts, params_ty_sts_name, strict=True
                            )
                        )
                        self.target.write_label(f'case "{on_off_type}":')
                        self.target.writelns(
                            f"return {self.func_kind.call_from_local(orig_name)}({args_sts_str});",
                        )
                    self.target.writelns(
                        f"default: throw new Error(`Unknown tag: ${{type}}`);",
                    )


class StsOverloadCtorGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        overload_name: str,
        overload_info: OverloadInfo,
        ctor_kind: CtorKind,
        mode_prefix: str,
    ):
        self.am = am
        self.target = target
        self.overload_name = overload_name
        self.overload_info = overload_info
        self.ctor_kind = ctor_kind
        self.mode_prefix = mode_prefix

    def gen_overload_ctor(self):
        with self.target.indented(
            f"{self.mode_prefix}{self.ctor_kind.overload_prefix}{self.overload_name} {{",
            f"}}",
        ):
            for orig in self.overload_info:
                self.target.writelns(
                    f"{orig},",
                )


class StsOnOffCtorGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        on_off_name: str,
        on_off_info: OnOffInfo,
        ctor_kind: CtorKind,
        mode_prefix: str,
    ):
        self.am = am
        self.target = target
        self.on_off_name = on_off_name
        self.on_off_info = on_off_info
        self.ctor_kind = ctor_kind
        self.mode_prefix = mode_prefix

    def gen_full_on_off_ctor(self):
        if not any(len(funcs) > 1 for funcs in self.on_off_info.values()):
            return self.gen_half_on_off_ctor()
        params_len = max(
            len(params_ty_sts_sig) for params_ty_sts_sig in self.on_off_info
        )
        args_sts = [f"p_{i}" for i in range(params_len)]
        params_sts = ["type: Object", *(f"{arg_sts}?: Object" for arg_sts in args_sts)]
        params_sts_str = ", ".join(params_sts)

        with self.target.indented(
            f"{self.mode_prefix}{self.ctor_kind.func_prefix}{self.on_off_name}({params_sts_str}) {{",
            f"}}",
        ):
            with self.target.indented(
                f"switch (type as object) {{",
                f"}}",
            ):
                for on_off_cases in self.on_off_info.values():
                    for on_off_type, (
                        orig_name,
                        params_ty_sts_name,
                        _,
                    ) in on_off_cases.items():
                        args_sts_str = ", ".join(
                            f"{arg_sts} as {param_ty_sts_name}"
                            for arg_sts, param_ty_sts_name in zip(
                                args_sts, params_ty_sts_name, strict=False
                            )
                        )
                        self.target.write_label(f'case "{on_off_type}":')
                        self.target.writelns(
                            f"{self.ctor_kind.call_from_local(orig_name)}({args_sts_str});",
                        )
                self.target.writelns(
                    f"default: throw new Error(`Unknown tag: ${{type}}`);",
                )

    def gen_half_on_off_ctor(self):
        for params_ty_sts_sig, on_off_cases in self.on_off_info.items():
            params_ty_sts_sum: list[set[str]] = [
                set() for _ in range(len(params_ty_sts_sig))
            ]
            return_ty_sts_sum: set[str] = set()
            for _, params_ty_sts_name, return_ty_sts_name in on_off_cases.values():
                for param_ty_sts_sum, param_ty_sts_name in zip(
                    params_ty_sts_sum, params_ty_sts_name, strict=True
                ):
                    param_ty_sts_sum.add(param_ty_sts_name)
                return_ty_sts_sum.add(return_ty_sts_name)
            params_sts = ["type: string"]
            args_sts = []
            for index, param_ty_sts_sum in enumerate(params_ty_sts_sum):
                arg_sts = f"p_{index}"
                param_ty = " | ".join(param_ty_sts_sum)
                params_sts.append(f"{arg_sts}?: {param_ty}")
                args_sts.append(arg_sts)
            params_sts_str = ", ".join(params_sts)
            args_sts_str = ", ".join(args_sts)
            return_ty = " | ".join(return_ty_sts_sum)

            with self.target.indented(
                f"{self.mode_prefix}{self.ctor_kind.func_prefix}{self.on_off_name}({params_sts_str}) {{",
                f"}}",
            ):
                with self.target.indented(
                    f"switch (type) {{",
                    f"}}",
                ):
                    for on_off_type, (
                        orig_name,
                        params_ty_sts_name,
                        _,
                    ) in on_off_cases.items():
                        args_sts_str = ", ".join(
                            f"{arg_sts} as {param_ty_sts_name}"
                            for arg_sts, param_ty_sts_name in zip(
                                args_sts, params_ty_sts_name, strict=True
                            )
                        )
                        self.target.write_label(f'case "{on_off_type}":')
                        self.target.writelns(
                            f"{self.ctor_kind.call_from_local(orig_name)}({args_sts_str});",
                        )
                    self.target.writelns(
                        f"default: throw new Error(`Unknown tag: ${{type}}`);",
                    )


class StsReverseFuncGenerator:
    def __init__(
        self,
        am: AnalysisManager,
        target: StsWriter,
        func: GlobFuncDecl | IfaceMethodDecl,
        func_rev_info: GlobFuncAniInfo | IfaceMethodAniInfo,
        func_kind: FuncKind | CtorKind,
    ):
        self.am = am
        self.target = target
        self.func = func
        self.func_rev_info = func_rev_info
        self.func_kind = func_kind

    def gen_reverse_func(self):
        func_ani_info = NamedCallableAniInfo.get(self.am, self.func)
        args_sts = []
        params_sts = self.func_kind.reverse_base_params()
        for param in self.func.params:
            param_ani_info = ParamAniInfo.get(self.am, param)
            param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
            args_sts.append(param_ani_info.sts_name)
            params_sts.append(
                f"{param_ani_info.sts_name}: {param_ty_ani_info.sts_type_in(self.target)}"
            )
        args_sts = func_ani_info.as_normal_args(args_sts)
        params_sts_str = ", ".join(params_sts)
        if isinstance(return_ty := self.func.return_ty, NonVoidType):
            return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
            return_ty_sts_name = return_ty_ani_info.sts_type_in(self.target)
            return_ty_sts_real = return_ty_ani_info.sts_type_in(self.target)
        else:
            return_ty_sts_name = "void"
            return_ty_sts_real = "undefined"

        with self.target.indented(
            f"function {self.func_rev_info.sts_reverse}({params_sts_str}): {return_ty_sts_name} {{",
            f"}}",
        ):
            if (norm_name := func_ani_info.norm_name) is not None:
                args_sts_str = ", ".join(args_sts)
                self.target.writelns(
                    f"return {self.func_kind.call_from_reverse(norm_name)}({args_sts_str});",
                )
            elif (get_name := func_ani_info.get_name) is not None:
                self.target.writelns(
                    f"return {self.func_kind.call_from_reverse(get_name)};",
                )
            elif (set_name := func_ani_info.set_name) is not None:
                self.target.writelns(
                    f"{self.func_kind.call_from_reverse(set_name)} = {args_sts[0]};",
                )
            elif (promise_name := func_ani_info.promise_name) is not None:
                args_sts_str = ", ".join(args_sts)
                self.target.writelns(
                    f"return {self.func_kind.call_from_reverse(promise_name)}({args_sts_str}).awaitSync();",
                )
            elif (async_name := func_ani_info.async_name) is not None:
                pkg_ani_info = PackageAniInfo.get(self.am, self.func.parent_pkg)
                with self.target.indented(
                    f"return new Promise<{return_ty_sts_name}>((resolve, reject) => {{",
                    f"}}).awaitSync();",
                ):
                    with self.target.indented(
                        f"let callback: {pkg_ani_info.ns.mod.AC_type}<{return_ty_sts_name}> = (err: {pkg_ani_info.ns.mod.BE_type} | null, res?: {return_ty_sts_real}): void => {{",
                        f"}}",
                    ):
                        with self.target.indented(
                            f"if (err !== null) {{",
                            f"}}",
                        ):
                            self.target.writelns(
                                f"reject(err);",
                            )
                        with self.target.indented(
                            f"else {{",
                            f"}}",
                        ):
                            self.target.writelns(
                                f"resolve(res as {return_ty_sts_real});",
                            )
                    args_with_cbname_sts_str = ", ".join([*args_sts, "callback"])
                    self.target.writelns(
                        f"{self.func_kind.call_from_reverse(async_name)}({args_with_cbname_sts_str});",
                    )
            else:
                self.target.writelns(
                    f"throw new Error(`No valid reverse function found`);",
                )
