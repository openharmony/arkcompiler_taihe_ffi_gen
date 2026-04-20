# -*- coding: utf-8 -*-
#
# Copyright (c) 2025-2026 Huawei Device Co., Ltd.
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

from collections.abc import Collection

from taihe.codegen.abi.analyses import IfaceAbiInfo
from taihe.codegen.napi.analyses import (
    EnumNapiInfo,
    GlobFuncNapiInfo,
    IfaceMethodNapiInfo,
    IfaceNapiInfo,
    Namespace,
    PackageGroupNapiInfo,
    StructNapiInfo,
    TypeNapiInfo,
    UnionNapiInfo,
)
from taihe.codegen.napi.attributes import (
    LibAttr,
    ReadOnlyAttr,
)
from taihe.codegen.napi.writer import (
    DtsWriter,
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


def check_lib(ns: Namespace) -> bool:
    for pkg in ns.packages:
        if LibAttr.get(pkg):
            return True
    return any(check_lib(child_ns) for child_ns_name, child_ns in ns.children.items())


class TsCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
        for module, ns in pg_napi_info.module_dict.items():
            self.gen_module_file(module, ns)

    def gen_module_file(self, module: str, ns: Namespace):
        if check_lib(ns):
            with DtsWriter(
                self.oc,
                f"proxy/{module}.ts",
            ) as target:
                native_lib_name = "_taihe_native_lib"
                self.gen_namespace(ns, target, native_lib_name)

    def gen_namespace(self, ns: Namespace, target: DtsWriter, native_lib_name: str):
        for head in ns.ts_injected_heads:
            target.write_block(head)
        for code in ns.ts_injected_codes:
            target.write_block(code)
        for pkg in ns.packages:
            if attr := LibAttr.get(pkg):
                lib_name = attr.lib_name
                # TODO: hack to decide require/import
                target.writelns(
                    f"const _taihe_native_lib = requireNapi('./{lib_name}', RequireBaseDir.SCRIPT_DIR);",
                )
                self.gen_package(pkg, target, native_lib_name)

        for child_ns_name, child_ns in ns.children.items():
            dts_decl = f"namespace {child_ns_name}"
            dts_decl = f"export {dts_decl}"
            with target.indented(
                f"{dts_decl} {{",
                f"}}",
            ):
                native_lib_name = f"{native_lib_name}.{child_ns_name}"
                self.gen_namespace(child_ns, target, native_lib_name)

    def gen_package(self, pkg: PackageDecl, target: DtsWriter, native_lib_name: str):
        self.gen_utils(target)
        for func in pkg.functions:
            func_napi_info = GlobFuncNapiInfo.get(self.am, func)
            if (
                func_napi_info.ctor_class_name is None
                and func_napi_info.static_class_name is None
            ):
                self.gen_func(func, target, native_lib_name)
        for struct in pkg.structs:
            self.gen_struct_interface(struct, target)
            self.gen_struct_class(struct, target, native_lib_name)
        for iface in pkg.interfaces:
            self.gen_iface_interface(iface, target)
            self.gen_iface_class(iface, target, native_lib_name)
        for enum in pkg.enums:
            self.gen_enum(enum, target)
        for union in pkg.unions:
            self.gen_union(union, target)

    def gen_utils(self, target: DtsWriter):
        target.writelns(
            f"type AsyncCallback<T> = (error: Error | null, result: T | undefined) => void;",
        )

    def gen_func(self, func: GlobFuncDecl, target: DtsWriter, native_lib_name: str):
        func_napi_info = GlobFuncNapiInfo.get(self.am, func)
        target.writelns(
            f"export const {func_napi_info.norm_name} = {native_lib_name}.{func_napi_info.norm_name};",
        )

    def gen_struct_interface(
        self,
        struct: StructDecl,
        target: DtsWriter,
    ):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        if struct_napi_info.is_class():
            # no interface
            return

        struct_decl = f"interface {struct_napi_info.dts_type_name}"
        if struct_napi_info.dts_iface_parents:
            parents = []
            for parent in struct_napi_info.dts_iface_parents:
                parent_ty = parent.ty
                parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(target))
            extends_str = ", ".join(parents) if parents else ""
            struct_decl = f"{struct_decl} extends {extends_str}"
        struct_decl = f"export {struct_decl}"

        with target.indented(
            f"{struct_decl} {{",
            f"}}",
        ):
            for injected in struct_napi_info.interfacets_ts_injected_codes:
                target.write_block(injected)

            for field in struct_napi_info.dts_fields:
                readonly = "readonly " if ReadOnlyAttr.get(field) is not None else ""
                ty_napi_info = TypeNapiInfo.get(self.am, field.ty)
                target.writelns(
                    f"{readonly}{field.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)};"
                )

    def gen_struct_class(
        self,
        struct: StructDecl,
        target: DtsWriter,
        native_lib_name: str,
    ):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        if not struct_napi_info.is_class():
            return

        struct_decl = f"class {struct_napi_info.dts_type_name}"
        if struct_napi_info.dts_iface_parents:
            parents = []
            for parent in struct_napi_info.dts_iface_parents:
                parent_ty = parent.ty
                parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(target))
            extends_str = ", ".join(parents) if parents else ""
            struct_decl = f"{struct_decl} implements {extends_str}"
        struct_decl = f"export {struct_decl}"

        with target.indented(
            f"{struct_decl} {{",
            f"}}",
        ):
            nativa_class_name = f"native{struct_napi_info.dts_type_name}"
            target.writelns(
                f"private {nativa_class_name};",
            )

            for injected in struct_napi_info.class_ts_injected_codes:
                target.write_block(injected)

            for parts in struct_napi_info.dts_final_fields:
                final = parts[-1]
                ty_napi_info = TypeNapiInfo.get(self.am, final.ty)
                with target.indented(
                    f"get {final.name}(): {ty_napi_info.dts_return_type_in(target)} {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return this.{nativa_class_name}.{final.name};",
                    )
                if not ReadOnlyAttr.get(final):
                    with target.indented(
                        f"set {final.name}({final.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)}) {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"this.{nativa_class_name}.{final.name} = {final.name};",
                        )

            if ctor := struct_napi_info.ctor:
                params = []
                args = []
                for param in ctor.params:
                    type_napi_info = TypeNapiInfo.get(self.am, param.ty)
                    params.append(
                        f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                    )
                    args.append(param.name)
                params_str = ", ".join(params)
                args_str = ", ".join(args)
                with target.indented(
                    f"constructor({params_str}) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"this.{nativa_class_name} = new {native_lib_name}.{struct_napi_info.dts_type_name}({args_str});",
                    )

            # static methods
            for mng_name, static_func in struct_napi_info.static_funcs:
                static_func_napi_info = GlobFuncNapiInfo.get(self.am, static_func)
                params = []
                args = []
                for param in static_func.params:
                    value_ty = param.ty
                    param_dts_info = TypeNapiInfo.get(self.am, value_ty)
                    params.append(
                        f"{param.name}{'?' if param_dts_info.is_optional else ''}: {param_dts_info.dts_type_in(target)}"
                    )
                    args.append(param.name)
                params_str = ", ".join(params)
                args_str = ", ".join(args)
                if isinstance(static_func.return_ty, NonVoidType):
                    return_ty_dts_info = TypeNapiInfo.get(
                        self.am, static_func.return_ty
                    )
                    return_ty = return_ty_dts_info.dts_return_type_in(target)
                else:
                    return_ty = "void"
                with target.indented(
                    f"static {static_func_napi_info.norm_name}({params_str}): {return_ty} {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return {native_lib_name}.{struct_napi_info.dts_type_name}.{static_func_napi_info.norm_name}({args_str});",
                    )

    def gen_iface_interface(
        self,
        iface: IfaceDecl,
        target: DtsWriter,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        if iface_napi_info.is_class():
            return

        parents = []
        for parent in iface.extends:
            parent_ty = parent.ty
            parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
            parents.append(parent_napi_info.dts_type_in(target))
        extends_str = " extends " + ", ".join(parents) if parents else ""
        with target.indented(
            f"export interface {iface_napi_info.dts_type_name}{extends_str} {{",
            f"}}",
        ):
            for injected in iface_napi_info.interface_ts_injected_codes:
                target.write_block(injected)
            self.gen_iface_interface_methods_decl(iface.methods, target)

    def gen_iface_class(
        self,
        iface: IfaceDecl,
        target: DtsWriter,
        native_lib_name: str,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        if not iface_napi_info.is_class():
            return

        iface_abi_info = IfaceAbiInfo.get(self.am, iface)

        iface_decl = f"class {iface_napi_info.dts_type_name}"
        if iface_napi_info.dts_iface_parents:
            parents = []
            for parent in iface_napi_info.dts_iface_parents:
                parent_ty = parent.ty
                parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(target))
            extends_str = ", ".join(parents) if parents else ""
            iface_decl = f"{iface_decl} implements {extends_str}"
        iface_decl = f"export {iface_decl}"

        nativa_class_name = f"native{iface_napi_info.dts_type_name}"
        with target.indented(
            f"{iface_decl} {{",
            f"}}",
        ):
            for injected in iface_napi_info.class_ts_injected_codes:
                target.write_block(injected)

            target.writelns(
                f"private {nativa_class_name};",
            )
            if ctor := iface_napi_info.ctor:
                params = []
                args = []
                for param in ctor.params:
                    type_napi_info = TypeNapiInfo.get(self.am, param.ty)
                    params.append(
                        f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                    )
                    args.append(param.name)
                params_str = ", ".join(params)
                args_str = ", ".join(args)
                with target.indented(
                    f"constructor({params_str}) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"this.{nativa_class_name} = new {native_lib_name}.{iface_napi_info.dts_type_name}({args_str});",
                    )

                # static methods
                for mng_name, static_func in iface_napi_info.static_funcs:
                    static_func_napi_info = GlobFuncNapiInfo.get(self.am, static_func)
                    params = []
                    args = []
                    for param in static_func.params:
                        value_ty = param.ty
                        param_dts_info = TypeNapiInfo.get(self.am, value_ty)
                        params.append(
                            f"{param.name}{'?' if param_dts_info.is_optional else ''}: {param_dts_info.dts_type_in(target)}"
                        )
                        args.append(param.name)
                    params_str = ", ".join(params)
                    args_str = ", ".join(args)
                    if isinstance(static_func.return_ty, NonVoidType):
                        return_ty_dts_info = TypeNapiInfo.get(
                            self.am, static_func.return_ty
                        )
                        return_ty = return_ty_dts_info.dts_return_type_in(target)
                    else:
                        return_ty = "void"

                    with target.indented(
                        f"static {static_func_napi_info.norm_name}({params_str}): {return_ty} {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"return {native_lib_name}.{iface_napi_info.dts_type_name}.{static_func_napi_info.norm_name}({args_str});",
                        )
            for ancestor in iface_abi_info.ancestor_infos:
                self.gen_iface_class_methods_impl(
                    ancestor.methods, target, nativa_class_name
                )

    def gen_iface_interface_methods_decl(
        self,
        methods: Collection[IfaceMethodDecl],
        target: DtsWriter,
    ):
        for method in methods:
            iface_method_napi_info = IfaceMethodNapiInfo.get(self.am, method)
            params = []
            for param in method.params:
                type_napi_info = TypeNapiInfo.get(self.am, param.ty)
                params.append(
                    f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                )
            params_str = ", ".join(params)
            if isinstance(method.return_ty, NonVoidType):
                type_napi_info = TypeNapiInfo.get(self.am, method.return_ty)
                return_ty = type_napi_info.dts_return_type_in(target)
                property_return_ty_name = ": " + return_ty
            else:
                property_return_ty_name = ""
                return_ty = "void"
            if name := iface_method_napi_info.get_name:
                target.writelns(
                    f"get {name}({params_str}){property_return_ty_name};",
                )
            elif name := iface_method_napi_info.set_name:
                target.writelns(
                    f"set {name}({params_str}){property_return_ty_name};",
                )
            else:
                if iface_method_napi_info.async_name is not None:
                    cbname = "callback"
                    callback_ty_ts_name = f"AsyncCallback<{return_ty}>"
                    callback_ts = f"{cbname}: {callback_ty_ts_name}"
                    params_with_callback_ts_str = ", ".join([*params, callback_ts])
                    target.writelns(
                        f"{iface_method_napi_info.async_name}({params_with_callback_ts_str}): void;",
                    )
                elif iface_method_napi_info.promise_name is not None:
                    promise_ty = f"Promise<{return_ty}>"
                    target.writelns(
                        f"{iface_method_napi_info.promise_name}({params_str}): {promise_ty};",
                    )
                else:
                    target.writelns(
                        f"{iface_method_napi_info.norm_name}({params_str}): {return_ty};",
                    )

    def gen_iface_class_methods_impl(
        self,
        methods: Collection[IfaceMethodDecl],
        target: DtsWriter,
        nativa_class_name: str,
    ):
        for method in methods:
            iface_method_napi_info = IfaceMethodNapiInfo.get(self.am, method)
            params = []
            args = []
            for param in method.params:
                type_napi_info = TypeNapiInfo.get(self.am, param.ty)
                params.append(
                    f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                )
                args.append(param.name)
            params_str = ", ".join(params)
            args_str = ", ".join(args)
            if isinstance(method.return_ty, NonVoidType):
                type_napi_info = TypeNapiInfo.get(self.am, method.return_ty)
                return_ty = type_napi_info.dts_return_type_in(target)
                property_return_ty_name = ": " + return_ty
            else:
                property_return_ty_name = ""
                return_ty = "void"
            if iface_method_napi_info.get_name is not None:
                with target.indented(
                    f"get {iface_method_napi_info.get_name}({params_str}){property_return_ty_name} {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return this.{nativa_class_name}.{iface_method_napi_info.get_name};",
                    )
            elif iface_method_napi_info.set_name is not None:
                with target.indented(
                    f"set {iface_method_napi_info.set_name}({params_str}){property_return_ty_name} {{",
                    f"}}",
                ):
                    target.writelns(
                        f"this.{nativa_class_name}.{iface_method_napi_info.set_name} = {args_str};",
                    )
            else:
                if iface_method_napi_info.async_name is not None:
                    cbname = "callback"
                    callback_ty_ts_name = f"AsyncCallback<{return_ty}>"
                    callback_ts = f"{cbname}: {callback_ty_ts_name}"
                    params_with_callback_ts_str = ", ".join([*params, callback_ts])
                    with target.indented(
                        f"{iface_method_napi_info.async_name}({params_with_callback_ts_str}): void {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"return this.{nativa_class_name}.{iface_method_napi_info.norm_name}({args_str});",
                        )
                elif iface_method_napi_info.promise_name is not None:
                    promise_ty = f"Promise<{return_ty}>"
                    with target.indented(
                        f"{iface_method_napi_info.promise_name}({params_str}): {promise_ty} {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"return this.{nativa_class_name}.{iface_method_napi_info.norm_name}({args_str});",
                        )
                else:
                    with target.indented(
                        f"{iface_method_napi_info.norm_name}({params_str}): {return_ty} {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"return this.{nativa_class_name}.{iface_method_napi_info.norm_name}({args_str});",
                        )

    def gen_enum(
        self,
        enum: EnumDecl,
        target: DtsWriter,
    ):
        enum_napi_info = EnumNapiInfo.get(self.am, enum)
        if enum_napi_info.is_literal:
            for item in enum.items:
                target.writelns(
                    f"export const {item.name} = {render_ets_value(item.typed_value)};",
                )
        else:
            with target.indented(
                f"export enum {enum_napi_info.dts_type_name} {{",
                f"}}",
            ):
                for item in enum.items:
                    target.writelns(
                        f"{item.name} = {render_ets_value(item.typed_value)},",
                    )

    def gen_union(
        self,
        union: UnionDecl,
        target: DtsWriter,
    ):
        union_napi_info = UnionNapiInfo.get(self.am, union)
        dts_types = []
        for field in union.fields:
            ty_napi_info = TypeNapiInfo.get(self.am, field.ty)
            dts_types.append(ty_napi_info.dts_type_in(target))
        dts_types_str = " | ".join(dts_types)
        target.writelns(
            f"export type {union_napi_info.dts_type_name} = {dts_types_str};",
        )
