from taihe.codegen.abi.analyses import (
    GlobFuncABIInfo,
    IfaceABIInfo,
    IfaceMethodABIInfo,
    PackageABIInfo,
    StructABIInfo,
    TypeABIInfo,
    UnionABIInfo,
)
from taihe.codegen.abi.writer import CHeaderWriter, CSourceWriter
from taihe.driver.backend import Backend
from taihe.driver.contexts import CompilerInstance
from taihe.semantics.declarations import (
    GlobFuncDecl,
    IfaceDecl,
    PackageDecl,
    StructDecl,
    UnionDecl,
)


class ABIHeadersGenerator(Backend):
    def __init__(self, ci: CompilerInstance):
        super().__init__(ci)
        self.oc = ci.output_config
        self.am = ci.analysis_manager
        self.pg = ci.package_group

    def generate(self):
        for pkg in self.pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_abi_info = PackageABIInfo.get(self.am, pkg)
        with CHeaderWriter(
            self.oc,
            f"include/{pkg_abi_info.header}",
        ) as pkg_abi_target:
            for struct in pkg.structs:
                struct_abi_info = StructABIInfo.get(self.am, struct)
                self.gen_struct_decl_file(struct, struct_abi_info)
                self.gen_struct_defn_file(struct, struct_abi_info)
                pkg_abi_target.add_include(struct_abi_info.impl_header)
            for union in pkg.unions:
                union_abi_info = UnionABIInfo.get(self.am, union)
                self.gen_union_decl_file(union, union_abi_info)
                self.gen_union_defn_file(union, union_abi_info)
                pkg_abi_target.add_include(union_abi_info.impl_header)
            for iface in pkg.interfaces:
                iface_abi_info = IfaceABIInfo.get(self.am, iface)
                self.gen_iface_decl_file(iface, iface_abi_info)
                self.gen_iface_defn_file(iface, iface_abi_info)
                self.gen_iface_impl_file(iface, iface_abi_info)
                pkg_abi_target.add_include(iface_abi_info.impl_header)
            pkg_abi_target.add_include("taihe/common.h")
            for func in pkg.functions:
                self.gen_func(func, pkg_abi_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_abi_target: CHeaderWriter,
    ):
        func_abi_info = GlobFuncABIInfo.get(self.am, func)
        params = []
        for param in func.params:
            type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_abi_target.add_include(*type_abi_info.impl_headers)
            params.append(f"{type_abi_info.as_param} {param.name}")
        params_str = ", ".join(params)
        if return_ty_ref := func.return_ty_ref:
            type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
            pkg_abi_target.add_include(*type_abi_info.impl_headers)
            return_ty_name = type_abi_info.as_owner
        else:
            return_ty_name = "void"
        pkg_abi_target.writelns(
            f"TH_EXPORT {return_ty_name} {func_abi_info.mangled_name}({params_str});",
        )

    def gen_struct_decl_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{struct_abi_info.decl_header}",
        ) as struct_abi_decl_target:
            struct_abi_decl_target.writelns(
                f"struct {struct_abi_info.mangled_name};",
            )

    def gen_struct_defn_file(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{struct_abi_info.impl_header}",
        ) as struct_abi_defn_target:
            struct_abi_defn_target.add_include("taihe/common.h")
            struct_abi_defn_target.add_include(struct_abi_info.decl_header)
            self.gen_struct_defn(struct, struct_abi_info, struct_abi_defn_target)

    def gen_struct_defn(
        self,
        struct: StructDecl,
        struct_abi_info: StructABIInfo,
        struct_abi_defn_target: CHeaderWriter,
    ):
        with struct_abi_defn_target.indented(
            f"struct {struct_abi_info.mangled_name} {{",
            f"}};",
        ):
            for field in struct.fields:
                type_abi_info = TypeABIInfo.get(self.am, field.ty_ref.resolved_ty)
                struct_abi_defn_target.add_include(*type_abi_info.impl_headers)
                struct_abi_defn_target.writelns(
                    f"{type_abi_info.as_owner} {field.name};",
                )

    def gen_union_decl_file(
        self,
        union: UnionDecl,
        union_abi_info: UnionABIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{union_abi_info.decl_header}",
        ) as union_abi_decl_target:
            union_abi_decl_target.writelns(
                f"struct {union_abi_info.mangled_name};",
            )

    def gen_union_defn_file(
        self,
        union: UnionDecl,
        union_abi_info: UnionABIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{union_abi_info.impl_header}",
        ) as union_abi_defn_target:
            union_abi_defn_target.add_include("taihe/common.h")
            union_abi_defn_target.add_include(union_abi_info.decl_header)
            self.gen_union_defn(union, union_abi_info, union_abi_defn_target)

    def gen_union_defn(
        self,
        union: UnionDecl,
        union_abi_info: UnionABIInfo,
        union_abi_defn_target: CHeaderWriter,
    ):
        with union_abi_defn_target.indented(
            f"union {union_abi_info.union_name} {{",
            f"}};",
        ):
            for field in union.fields:
                if field.ty_ref is None:
                    union_abi_defn_target.writelns(
                        f"// {field.name}",
                    )
                    continue
                type_abi_info = TypeABIInfo.get(self.am, field.ty_ref.resolved_ty)
                union_abi_defn_target.add_include(*type_abi_info.impl_headers)
                union_abi_defn_target.writelns(
                    f"{type_abi_info.as_owner} {field.name};",
                )
        with union_abi_defn_target.indented(
            f"struct {union_abi_info.mangled_name} {{",
            f"}};",
        ):
            union_abi_defn_target.writelns(
                f"{union_abi_info.tag_type} m_tag;",
                f"union {union_abi_info.union_name} m_data;",
            )

    def gen_iface_decl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{iface_abi_info.decl_header}",
        ) as iface_abi_decl_target:
            iface_abi_decl_target.writelns(
                f"struct {iface_abi_info.mangled_name};",
            )

    def gen_iface_defn_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{iface_abi_info.defn_header}",
        ) as iface_abi_defn_target:
            iface_abi_defn_target.add_include("taihe/object.abi.h")
            iface_abi_defn_target.add_include(iface_abi_info.decl_header)
            iface_abi_defn_target.writelns(
                f"TH_EXPORT void const* const {iface_abi_info.iid};",
            )
            self.gen_iface_ftable(iface, iface_abi_info, iface_abi_defn_target)
            self.gen_iface_vtable(iface, iface_abi_info, iface_abi_defn_target)
            self.gen_iface_defn(iface, iface_abi_info, iface_abi_defn_target)
            self.gen_iface_static_cast(iface, iface_abi_info, iface_abi_defn_target)
            self.gen_iface_dynamic_cast(iface, iface_abi_info, iface_abi_defn_target)

    def gen_iface_ftable(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: CHeaderWriter,
    ):
        with iface_abi_defn_target.indented(
            f"struct {iface_abi_info.ftable} {{",
            f"}};",
        ):
            for method in iface.methods:
                params = [f"{iface_abi_info.as_param} tobj"]
                for param in method.params:
                    type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
                    iface_abi_defn_target.add_include(*type_abi_info.decl_headers)
                    params.append(f"{type_abi_info.as_param} {param.name}")
                params_str = ", ".join(params)
                if return_ty_ref := method.return_ty_ref:
                    type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
                    iface_abi_defn_target.add_include(*type_abi_info.decl_headers)
                    return_ty_name = type_abi_info.as_owner
                else:
                    return_ty_name = "void"
                iface_abi_defn_target.writelns(
                    f"{return_ty_name} (*{method.name})({params_str});",
                )

    def gen_iface_vtable(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: CHeaderWriter,
    ):
        with iface_abi_defn_target.indented(
            f"struct {iface_abi_info.vtable} {{",
            f"}};",
        ):
            for ancestor_item_info in iface_abi_info.ancestor_list:
                ancestor_abi_info = IfaceABIInfo.get(self.am, ancestor_item_info.iface)
                iface_abi_defn_target.writelns(
                    f"struct {ancestor_abi_info.ftable} const* {ancestor_item_info.ftbl_ptr};",
                )

    def gen_iface_defn(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: CHeaderWriter,
    ):
        with iface_abi_defn_target.indented(
            f"struct {iface_abi_info.mangled_name} {{",
            f"}};",
        ):
            iface_abi_defn_target.writelns(
                f"struct {iface_abi_info.vtable} const* vtbl_ptr;",
                f"struct DataBlockHead* data_ptr;",
            )

    def gen_iface_static_cast(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: CHeaderWriter,
    ):
        for ancestor, info in iface_abi_info.ancestor_dict.items():
            if ancestor is iface:
                continue
            ancestor_abi_info = IfaceABIInfo.get(self.am, ancestor)
            iface_abi_defn_target.add_include(ancestor_abi_info.defn_header)
            with iface_abi_defn_target.indented(
                f"TH_INLINE struct {ancestor_abi_info.vtable} const* {info.static_cast}(struct {iface_abi_info.vtable} const* vtbl_ptr) {{",
                f"}}",
            ):
                iface_abi_defn_target.writelns(
                    f"return (struct {ancestor_abi_info.vtable} const*)((void* const*)vtbl_ptr + {info.offset});",
                )

    def gen_iface_dynamic_cast(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_defn_target: CHeaderWriter,
    ):
        with iface_abi_defn_target.indented(
            f"TH_INLINE struct {iface_abi_info.vtable} const* {iface_abi_info.dynamic_cast}(struct TypeInfo const* rtti_ptr) {{",
            f"}}",
        ):
            with iface_abi_defn_target.indented(
                f"for (size_t i = 0; i < rtti_ptr->len; i++) {{",
                f"}}",
            ):
                with iface_abi_defn_target.indented(
                    f"if (rtti_ptr->idmap[i].id == {iface_abi_info.iid}) {{",
                    f"}}",
                ):
                    iface_abi_defn_target.writelns(
                        f"return (struct {iface_abi_info.vtable}*)rtti_ptr->idmap[i].vtbl_ptr;",
                    )
            iface_abi_defn_target.writelns(
                f"return NULL;",
            )

    def gen_iface_impl_file(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
    ):
        with CHeaderWriter(
            self.oc,
            f"include/{iface_abi_info.impl_header}",
        ) as iface_abi_impl_target:
            iface_abi_impl_target.add_include(iface_abi_info.defn_header)
            self.gen_iface_methods(iface, iface_abi_info, iface_abi_impl_target)

    def gen_iface_methods(
        self,
        iface: IfaceDecl,
        iface_abi_info: IfaceABIInfo,
        iface_abi_impl_target: CHeaderWriter,
    ):
        for method in iface.methods:
            method_abi_info = IfaceMethodABIInfo.get(self.am, method)
            params = [f"{iface_abi_info.as_param} tobj"]
            args = ["tobj"]
            for param in method.params:
                type_abi_info = TypeABIInfo.get(self.am, param.ty_ref.resolved_ty)
                iface_abi_impl_target.add_include(*type_abi_info.impl_headers)
                params.append(f"{type_abi_info.as_param} {param.name}")
                args.append(param.name)
            params_str = ", ".join(params)
            args_str = ", ".join(args)
            if return_ty_ref := method.return_ty_ref:
                type_abi_info = TypeABIInfo.get(self.am, return_ty_ref.resolved_ty)
                iface_abi_impl_target.add_include(*type_abi_info.impl_headers)
                return_ty_name = type_abi_info.as_owner
            else:
                return_ty_name = "void"
            with iface_abi_impl_target.indented(
                f"TH_INLINE {return_ty_name} {method_abi_info.mangled_name}({params_str}) {{",
                f"}}",
            ):
                iface_abi_impl_target.writelns(
                    f"return tobj.vtbl_ptr->{iface_abi_info.ancestor_dict[iface].ftbl_ptr}->{method.name}({args_str});",
                )


class ABISourcesGenerator(Backend):
    def __init__(self, ci: CompilerInstance):
        super().__init__(ci)
        self.oc = ci.output_config
        self.am = ci.analysis_manager
        self.pg = ci.package_group

    def generate(self):
        for pkg in self.pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_abi_info = PackageABIInfo.get(self.am, pkg)
        with CSourceWriter(
            self.oc,
            f"src/{pkg_abi_info.src}",
        ) as pkg_abi_src_target:
            for iface in pkg.interfaces:
                self.gen_iface_file(iface, pkg_abi_src_target)

    def gen_iface_file(
        self,
        iface: IfaceDecl,
        pkg_abi_src_target: CSourceWriter,
    ):
        iface_abi_info = IfaceABIInfo.get(self.am, iface)
        pkg_abi_src_target.add_include(iface_abi_info.defn_header)
        pkg_abi_src_target.writelns(
            f"void const* const {iface_abi_info.iid} = &{iface_abi_info.iid};",
        )
