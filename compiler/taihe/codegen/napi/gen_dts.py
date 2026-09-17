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


from taihe.codegen.abi.analyses import IfaceAbiInfo
from taihe.codegen.napi.analyses import (
    EnumNapiInfo,
    GlobFuncNapiInfo,
    IfaceMethodNapiInfo,
    IfaceNapiInfo,
    Namespace,
    PackageGroupNapiInfo,
    PackageNapiInfo,
    StructNapiInfo,
    TypeNapiInfo,
    UnionNapiInfo,
)
from taihe.codegen.napi.attributes import ReadOnlyAttr
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


class DtsCodeGenerator:
    def __init__(self, oc: OutputManager, am: AnalysisManager):
        self.oc = oc
        self.am = am

    def generate(self, pg: PackageGroup):
        pg_napi_info = PackageGroupNapiInfo.get(self.am, pg)
        for _, ns in pg_napi_info.module_dict.items():
            DtsModuleGenerator(self.oc, self.am, ns).gen_module_file()


class DtsModuleGenerator:
    def __init__(
        self,
        oc: OutputManager,
        am: AnalysisManager,
        ns: Namespace,
    ):
        self.am = am
        self.ns = ns
        self.target = DtsWriter(oc, f"{self.ns.name}.d.ts")

    def gen_module_file(self):
        with self.target:
            for head in self.ns.dts_injected_heads:
                self.target.write_block(head)
            DtsNamespaceGenerator(self.target, self.am, self.ns).gen_namespace()


class DtsNamespaceGenerator:
    def __init__(
        self,
        target: DtsWriter,
        am: AnalysisManager,
        ns: Namespace,
    ):
        self.am = am
        self.ns = ns
        self.target = target

    def gen_namespace(self):
        for code in self.ns.dts_injected_codes:
            self.target.write_block(code)
        for pkg in self.ns.packages:
            self.gen_package(pkg)
        for _, child_ns in self.ns.children.items():
            dts_decl = f"namespace {child_ns.name}"
            dts_decl = f"export {dts_decl}"
            with self.target.indented(
                f"{dts_decl} {{",
                f"}}",
            ):
                DtsNamespaceGenerator(self.target, self.am, child_ns).gen_namespace()

    def gen_package(self, pkg: PackageDecl):
        self.gen_utils()
        pkg_napi_info = PackageNapiInfo.get(self.am, pkg)
        for func in pkg_napi_info.global_funcs:
            self.gen_func(func)
        for struct in pkg.structs:
            self.gen_struct_interface(struct)
            self.gen_struct_class(struct)
        for iface in pkg.interfaces:
            self.gen_iface_interface(iface)
            self.gen_iface_class(iface)
        for enum in pkg.enums:
            self.gen_enum(enum)
        for union in pkg.unions:
            self.gen_union(union)

    def gen_utils(self):
        self.target.writelns(
            f"type AsyncCallback<T> = (error: Error | null, result: T | undefined) => void;",
        )

    def gen_func(self, func: GlobFuncDecl):
        func_napi_info = GlobFuncNapiInfo.get(self.am, func)
        params = []
        for param in func.params:
            param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
            params.append(
                f"{param.name}{'?' if param_ty_napi_info.is_optional else ''}: {param_ty_napi_info.dts_type_in(self.target)}"
            )
        params_str = ", ".join(params)
        if isinstance(func.return_ty, NonVoidType):
            return_ty_napi_info = TypeNapiInfo.get(self.am, func.return_ty)
            return_ty = return_ty_napi_info.dts_return_type_in(self.target)
        else:
            return_ty = "void"
        if func_napi_info.async_name is not None:
            cbname = "callback"
            callback_ty_ts_name = f"AsyncCallback<{return_ty}>"
            callback_ts = f"{cbname}: {callback_ty_ts_name}"
            params_with_callback_ts_str = ", ".join([*params, callback_ts])
            self.target.writelns(
                f"export function {func_napi_info.async_name}({params_with_callback_ts_str}): void;",
            )
        elif func_napi_info.promise_name is not None:
            promise_ty = f"Promise<{return_ty}>"
            self.target.writelns(
                f"export function {func_napi_info.promise_name}({params_str}): {promise_ty};",
            )
        else:
            self.target.writelns(
                f"export function {func_napi_info.norm_name}({params_str}): {return_ty};",
            )

    def gen_struct_interface(self, struct: StructDecl):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        if struct_napi_info.is_class():
            return

        struct_decl = f"interface {struct_napi_info.dts_type_name}"
        if struct_napi_info.dts_iface_parents:
            parents = []
            for parent in struct_napi_info.dts_iface_parents:
                parent_ty = parent.ty
                parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(self.target))
            extends_str = ", ".join(parents)
            struct_decl = f"{struct_decl} extends {extends_str}"
        struct_decl = f"export {struct_decl}"

        with self.target.indented(
            f"{struct_decl} {{",
            f"}}",
        ):
            for injected in struct_napi_info.interfacets_dts_injected_codes:
                self.target.write_block(injected)

            for field in struct_napi_info.dts_local_fields:
                readonly = "readonly " if ReadOnlyAttr.get(field) is not None else ""
                ty_napi_info = TypeNapiInfo.get(self.am, field.ty)
                self.target.writelns(
                    f"{readonly}{field.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(self.target)};"
                )

    def gen_struct_class(self, struct: StructDecl):
        struct_napi_info = StructNapiInfo.get(self.am, struct)
        if not struct_napi_info.is_class():
            return

        struct_decl = f"class {struct_napi_info.dts_type_name}"
        if parent := struct_napi_info.dts_class_parent:
            parent_ty = parent.ty
            parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
            extends_str = parent_napi_info.dts_type_in(self.target)
            struct_decl = f"{struct_decl} extends {extends_str}"
        if struct_napi_info.dts_iface_parents:
            parents = []
            for parent in struct_napi_info.dts_iface_parents:
                parent_ty = parent.ty
                parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(self.target))
            extends_str = ", ".join(parents)
            struct_decl = f"{struct_decl} implements {extends_str}"
        struct_decl = f"export {struct_decl}"

        with self.target.indented(
            f"{struct_decl} {{",
            f"}}",
        ):
            for injected in struct_napi_info.class_dts_injected_codes:
                self.target.write_block(injected)

            for parts in struct_napi_info.dts_final_fields:
                final = parts[-1]
                readonly = "readonly " if ReadOnlyAttr.get(final) is not None else ""
                ty_napi_info = TypeNapiInfo.get(self.am, final.ty)
                self.target.writelns(
                    f"{readonly}{final.name}{'?' if ty_napi_info.is_optional else ''}: {ty_napi_info.dts_type_in(self.target)};"
                )

            if ctor := struct_napi_info.ctor:
                self.gen_ctor_decl(ctor)

            for static_func in struct_napi_info.static_funcs:
                self.gen_static_method_decl(static_func)

    def gen_iface_interface(self, iface: IfaceDecl):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        if iface_napi_info.is_class():
            return

        iface_decl = f"interface {iface_napi_info.dts_type_name}"
        if iface_napi_info.dts_iface_parents:
            parents = []
            for parent in iface_napi_info.dts_iface_parents:
                parent_ty = parent.ty
                parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(self.target))
            extends_str = ", ".join(parents)
            iface_decl = f"{iface_decl} extends {extends_str}"
        iface_decl = f"export {iface_decl}"

        with self.target.indented(
            f"{iface_decl} {{",
            f"}}",
        ):
            for injected in iface_napi_info.interface_dts_injected_codes:
                self.target.write_block(injected)

            for method in iface.methods:
                self.gen_iface_method_decl(method)

    def gen_iface_class(self, iface: IfaceDecl):
        iface_napi_info = IfaceNapiInfo.get(self.am, iface)
        if not iface_napi_info.is_class():
            return

        iface_decl = f"class {iface_napi_info.dts_type_name}"
        if parent := iface_napi_info.dts_class_parent:
            parent_ty = parent.ty
            parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
            extends_str = parent_napi_info.dts_type_in(self.target)
            iface_decl = f"{iface_decl} extends {extends_str}"
        if iface_napi_info.dts_iface_parents:
            parents = []
            for parent in iface_napi_info.dts_iface_parents:
                parent_ty = parent.ty
                parent_napi_info = TypeNapiInfo.get(self.am, parent_ty)
                parents.append(parent_napi_info.dts_type_in(self.target))
            extends_str = ", ".join(parents)
            iface_decl = f"{iface_decl} implements {extends_str}"
        iface_decl = f"export {iface_decl}"

        with self.target.indented(
            f"{iface_decl} {{",
            f"}}",
        ):
            for injected in iface_napi_info.class_dts_injected_codes:
                self.target.write_block(injected)

            if ctor := iface_napi_info.ctor:
                self.gen_ctor_decl(ctor)

            for static_func in iface_napi_info.static_funcs:
                self.gen_static_method_decl(static_func)

            iface_abi_info = IfaceAbiInfo.get(self.am, iface)
            for ancestor in iface_abi_info.ancestor_infos:
                for method in ancestor.methods:
                    self.gen_iface_method_decl(method)

    def gen_ctor_decl(self, ctor: GlobFuncDecl):
        params = []
        for param in ctor.params:
            type_napi_info = TypeNapiInfo.get(self.am, param.ty)
            params.append(
                f"{param.name}{'?' if type_napi_info.is_optional else ''}: {type_napi_info.dts_type_in(self.target)}"
            )
        params_str = ", ".join(params)
        self.target.writelns(f"constructor({params_str});")

    def gen_static_method_decl(self, static_func: GlobFuncDecl):
        static_func_napi_info = GlobFuncNapiInfo.get(self.am, static_func)
        params = []
        for param in static_func.params:
            param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
            params.append(
                f"{param.name}{'?' if param_ty_napi_info.is_optional else ''}: {param_ty_napi_info.dts_type_in(self.target)}"
            )
        params_str = ", ".join(params)
        if isinstance(static_func.return_ty, NonVoidType):
            return_ty_napi_info = TypeNapiInfo.get(self.am, static_func.return_ty)
            return_ty = return_ty_napi_info.dts_return_type_in(self.target)
        else:
            return_ty = "void"
        if static_func_napi_info.async_name is not None:
            cbname = "callback"
            callback_ty_ts_name = f"AsyncCallback<{return_ty}>"
            callback_ts = f"{cbname}: {callback_ty_ts_name}"
            params_with_callback_ts_str = ", ".join([*params, callback_ts])
            self.target.writelns(
                f"static {static_func_napi_info.async_name}({params_with_callback_ts_str}): void;",
            )
        elif static_func_napi_info.promise_name is not None:
            promise_ty = f"Promise<{return_ty}>"
            self.target.writelns(
                f"static {static_func_napi_info.promise_name}({params_str}): {promise_ty};",
            )
        else:
            self.target.writelns(
                f"static {static_func_napi_info.norm_name}({params_str}): {return_ty};",
            )

    def gen_iface_method_decl(self, method: IfaceMethodDecl):
        iface_method_napi_info = IfaceMethodNapiInfo.get(self.am, method)
        params = []
        for param in method.params:
            param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
            params.append(
                f"{param.name}{'?' if param_ty_napi_info.is_optional else ''}: {param_ty_napi_info.dts_type_in(self.target)}"
            )
        params_str = ", ".join(params)
        if isinstance(method.return_ty, NonVoidType):
            return_ty_napi_info = TypeNapiInfo.get(self.am, method.return_ty)
            return_ty = return_ty_napi_info.dts_return_type_in(self.target)
        else:
            return_ty = "void"
        if iface_method_napi_info.get_name is not None:
            self.target.writelns(
                f"get {iface_method_napi_info.get_name}(): {return_ty};",
            )
        elif iface_method_napi_info.set_name is not None:
            self.target.writelns(
                f"set {iface_method_napi_info.set_name}({params_str});",
            )
        elif iface_method_napi_info.async_name is not None:
            cbname = "callback"
            callback_ty_ts_name = f"AsyncCallback<{return_ty}>"
            callback_ts = f"{cbname}: {callback_ty_ts_name}"
            params_with_callback_ts_str = ", ".join([*params, callback_ts])
            self.target.writelns(
                f"{iface_method_napi_info.async_name}({params_with_callback_ts_str}): void;",
            )
        elif iface_method_napi_info.promise_name is not None:
            promise_ty = f"Promise<{return_ty}>"
            self.target.writelns(
                f"{iface_method_napi_info.promise_name}({params_str}): {promise_ty};",
            )
        else:
            self.target.writelns(
                f"{iface_method_napi_info.norm_name}({params_str}): {return_ty};",
            )

    def gen_enum(self, enum: EnumDecl):
        enum_napi_info = EnumNapiInfo.get(self.am, enum)
        if enum_napi_info.is_literal:
            for item in enum.items:
                self.target.writelns(
                    f"export const {item.name} = {render_ets_value(item.typed_value)};",
                )
        else:
            with self.target.indented(
                f"export enum {enum_napi_info.dts_type_name} {{",
                f"}}",
            ):
                for item in enum.items:
                    self.target.writelns(
                        f"{item.name} = {render_ets_value(item.typed_value)},",
                    )

    def gen_union(self, union: UnionDecl):
        union_napi_info = UnionNapiInfo.get(self.am, union)
        dts_types = []
        for field in union.fields:
            ty_napi_info = TypeNapiInfo.get(self.am, field.ty)
            dts_types.append(ty_napi_info.dts_type_in(self.target))
        dts_types_str = " | ".join(dts_types)
        self.target.writelns(
            f"export type {union_napi_info.dts_type_name} = {dts_types_str};",
        )
