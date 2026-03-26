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

from collections.abc import Collection
from json import dumps

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
from taihe.codegen.napi.attributes import ReadOnlyAttr
from taihe.codegen.napi.writer import DtsWriter
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


class DtsCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
        for module, ns in pg_napi_info.module_dict.items():
            self.gen_module_file(module, ns)

    def gen_module_file(self, module: str, ns: Namespace):
        with DtsWriter(
            self.oc,
            f"{module}.d.ts",
        ) as target:
            self.gen_namespace(ns, target)

    def gen_namespace(self, ns: Namespace, target: DtsWriter):
        for head in ns.dts_injected_heads:
            target.write_block(head)
        for code in ns.dts_injected_codes:
            target.write_block(code)
        for pkg in ns.packages:
            self.gen_package(pkg, target)
        for child_ns_name, child_ns in ns.children.items():
            dts_decl = f"namespace {child_ns_name}"
            dts_decl = f"export {dts_decl}"
            with target.indented(
                f"{dts_decl} {{",
                f"}}",
            ):
                self.gen_namespace(child_ns, target)

    def gen_package(self, pkg: PackageDecl, pkg_dts_target: DtsWriter):
        self.gen_utils(pkg_dts_target)
        for func in pkg.functions:
            func_napi_info = GlobFuncNapiInfo.get(self.am, func)
            if (
                func_napi_info.ctor_class_name is None
                and func_napi_info.static_class_name is None
            ):
                self.gen_func(func, pkg_dts_target)
        for struct in pkg.structs:
            self.gen_struct_interface(struct, pkg_dts_target)
            self.gen_struct_class(struct, pkg_dts_target)
        for iface in pkg.interfaces:
            self.gen_iface_interface(iface, pkg_dts_target)
        for enum in pkg.enums:
            self.gen_enum(enum, pkg_dts_target)
        for union in pkg.unions:
            self.gen_union(union, pkg_dts_target)

    def gen_utils(self, target: DtsWriter):
        target.writelns(
            f"type AsyncCallback<T> = (error: Error | null, result: T | undefined) => void;",
        )

    def gen_func(self, func: GlobFuncDecl, pkg_dts_target: DtsWriter):
        func_napi_info = GlobFuncNapiInfo.get(self.am, func)
        args = []
        for param in func.params:
            value_ty = param.ty
            param_dts_info = TypeNapiInfo.get(self.am, value_ty)
            args.append(
                f"{param.name}{'?' if param_dts_info.is_optional else ''}: {param_dts_info.dts_type_in(pkg_dts_target)}"
            )
        args_str = ", ".join(args)
        if isinstance(func.return_ty, NonVoidType):
            return_ty_dts_info = TypeNapiInfo.get(self.am, func.return_ty)
            return_ty = return_ty_dts_info.dts_return_type_in(pkg_dts_target)
        else:
            return_ty = "void"
        if func_napi_info.async_name is not None:
            cbname = "callback"
            callback_ty_ts_name = f"AsyncCallback<{return_ty}>"
            callback_ts = f"{cbname}: {callback_ty_ts_name}"
            params_with_callback_ts_str = ", ".join([*args, callback_ts])
            pkg_dts_target.writelns(
                f"export function {func_napi_info.async_name}({params_with_callback_ts_str}): void;",
            )
        elif func_napi_info.promise_name is not None:
            promise_ty = f"Promise<{return_ty}>"
            pkg_dts_target.writelns(
                f"export function {func_napi_info.promise_name}({args_str}): {promise_ty};",
            )
        else:
            pkg_dts_target.writelns(
                f"export function {func_napi_info.norm_name}({args_str}): {return_ty};",
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
            for injected in struct_napi_info.interfacets_dts_injected_codes:
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
            for injected in struct_napi_info.class_dts_injected_codes:
                target.write_block(injected)

            for parts in struct_napi_info.dts_final_fields:
                final = parts[-1]
                readonly = "readonly " if ReadOnlyAttr.get(final) is not None else ""
                ty_napi_info = TypeNapiInfo.get(self.am, final.ty)
                target.writelns(
                    f"{readonly}{final.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(target)};"
                )

            if ctor := struct_napi_info.ctor:
                params = []
                for param in ctor.params:
                    type_napi_info = TypeNapiInfo.get(self.am, param.ty)
                    params.append(
                        f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                    )
                params_str = ", ".join(params)
                target.writelns(f"constructor({params_str});")

            # static methods
            for mng_name, static_func in struct_napi_info.static_funcs:
                static_func_napi_info = GlobFuncNapiInfo.get(self.am, static_func)
                params = []
                for param in static_func.params:
                    value_ty = param.ty
                    param_dts_info = TypeNapiInfo.get(self.am, value_ty)
                    params.append(
                        f"{param.name}{'?' if param_dts_info.is_optional else ''}: {param_dts_info.dts_type_in(target)}"
                    )
                params_str = ", ".join(params)
                if isinstance(static_func.return_ty, NonVoidType):
                    return_ty_dts_info = TypeNapiInfo.get(
                        self.am, static_func.return_ty
                    )
                    return_ty = return_ty_dts_info.dts_return_type_in(target)
                else:
                    return_ty = "void"
                if static_func_napi_info.async_name is not None:
                    cbname = "callback"
                    callback_ty_ts_name = f"AsyncCallback<{return_ty}>"
                    callback_ts = f"{cbname}: {callback_ty_ts_name}"
                    params_with_callback_ts_str = ", ".join([*params, callback_ts])
                    target.writelns(
                        f"static {static_func_napi_info.async_name}({params_with_callback_ts_str}): void;",
                    )
                elif static_func_napi_info.promise_name is not None:
                    promise_ty = f"Promise<{return_ty}>"
                    target.writelns(
                        f"static {static_func_napi_info.promise_name}({params_str}): {promise_ty};",
                    )
                else:
                    target.writelns(
                        f"static {static_func_napi_info.norm_name}({params_str}): {return_ty};",
                    )

    def gen_iface_interface(
        self,
        iface: IfaceDecl,
        target: DtsWriter,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        if iface_napi_info.is_class():
            self.gen_iface_class(iface, target)
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
            for injected in iface_napi_info.interface_dts_injected_codes:
                target.write_block(injected)
            self.gen_iface_methods_decl(iface.methods, target)

    def gen_iface_class(
        self,
        iface: IfaceDecl,
        target: DtsWriter,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
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

        with target.indented(
            f"{iface_decl} {{",
            f"}}",
        ):
            for injected in iface_napi_info.class_dts_injected_codes:
                target.write_block(injected)

            if ctor := iface_napi_info.ctor:
                params = []
                for param in ctor.params:
                    type_napi_info = TypeNapiInfo.get(self.am, param.ty)
                    params.append(
                        f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                    )
                params_str = ", ".join(params)
                target.writelns(f"constructor({params_str});")

                # static methods
                for mng_name, static_func in iface_napi_info.static_funcs:
                    params = []
                    for param in static_func.params:
                        value_ty = param.ty
                        param_dts_info = TypeNapiInfo.get(self.am, value_ty)
                        params.append(
                            f"{param.name}{'?' if param_dts_info.is_optional else ''}: {param_dts_info.dts_type_in(target)}"
                        )
                    params_str = ", ".join(params)
                    if isinstance(static_func.return_ty, NonVoidType):
                        return_ty_dts_info = TypeNapiInfo.get(
                            self.am, static_func.return_ty
                        )
                        return_ty = return_ty_dts_info.dts_return_type_in(target)
                    else:
                        return_ty = "void"
                    static_func_napi_info = GlobFuncNapiInfo.get(self.am, static_func)
                    if static_func_napi_info.async_name is not None:
                        cbname = "callback"
                        callback_ty_ts_name = f"AsyncCallback<{return_ty}>"
                        callback_ts = f"{cbname}: {callback_ty_ts_name}"
                        params_with_callback_ts_str = ", ".join([*params, callback_ts])
                        target.writelns(
                            f"static {static_func_napi_info.async_name}({params_with_callback_ts_str}): void;",
                        )
                    elif static_func_napi_info.promise_name is not None:
                        promise_ty = f"Promise<{return_ty}>"
                        target.writelns(
                            f"static {static_func_napi_info.promise_name}({params_str}): {promise_ty};",
                        )
                    else:
                        target.writelns(
                            f"static {static_func_napi_info.norm_name}({params_str}): {return_ty};",
                        )
            for ancestor in iface_abi_info.ancestor_infos:
                self.gen_iface_methods_decl(ancestor.methods, target)

    def gen_iface_methods_decl(
        self,
        methods: Collection[IfaceMethodDecl],
        target: DtsWriter,
    ):
        for method in methods:
            iface_method_napi_info = IfaceMethodNapiInfo.get(self.am, method)
            dts_params = []
            for param in method.params:
                type_napi_info = TypeNapiInfo.get(self.am, param.ty)
                dts_params.append(
                    f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(target)}"
                )
            dts_params_str = ", ".join(dts_params)
            if isinstance(method.return_ty, NonVoidType):
                type_napi_info = TypeNapiInfo.get(self.am, method.return_ty)
                return_ty = type_napi_info.dts_return_type_in(target)
                property_return_ty_name = ": " + return_ty
            else:
                property_return_ty_name = ""
                return_ty = "void"
            if iface_method_napi_info.get_name is not None:
                target.writelns(
                    f"get {iface_method_napi_info.get_name}({dts_params_str}){property_return_ty_name};",
                )
            elif iface_method_napi_info.set_name is not None:
                target.writelns(
                    f"set {iface_method_napi_info.set_name}({dts_params_str}){property_return_ty_name};",
                )
            elif iface_method_napi_info.async_name is not None:
                cbname = "callback"
                callback_ty_ts_name = f"AsyncCallback<{return_ty}>"
                callback_ts = f"{cbname}: {callback_ty_ts_name}"
                params_with_callback_ts_str = ", ".join([*dts_params, callback_ts])
                target.writelns(
                    f"{iface_method_napi_info.async_name}({params_with_callback_ts_str}): void;",
                )
            elif iface_method_napi_info.promise_name is not None:
                promise_ty = f"Promise<{return_ty}>"
                target.writelns(
                    f"{iface_method_napi_info.promise_name}({dts_params_str}): {promise_ty};",
                )
            else:
                target.writelns(
                    f"{iface_method_napi_info.norm_name}({dts_params_str}): {return_ty};",
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
                    f"export const {item.name} = {dumps(item.value)};",
                )
        else:
            with target.indented(
                f"export enum {enum_napi_info.dts_type_name} {{",
                f"}}",
            ):
                for item in enum.items:
                    if item.value is None:
                        target.writelns(
                            f"{item.name},",
                        )
                    else:
                        target.writelns(
                            f"{item.name} = {dumps(item.value)},",
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
