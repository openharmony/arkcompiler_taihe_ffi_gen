from taihe.codegen.abi.analyses import (
    GlobFuncAbiInfo,
    GlobFuncCImplInfo,
    PackageAbiInfo,
    PackageCImplInfo,
    TypeAbiInfo,
)
from taihe.codegen.abi.writer import CHeaderWriter, CSourceWriter
from taihe.semantics.declarations import (
    GlobFuncDecl,
    PackageDecl,
    PackageGroup,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import FileKind, OutputManager


class CImplHeadersGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_c_impl_info = PackageCImplInfo.get(self.am, pkg)
        pkg_abi_info = PackageAbiInfo.get(self.am, pkg)
        with CHeaderWriter(
            self.om,
            f"include/{pkg_c_impl_info.header}",
            FileKind.C_HEADER,
        ) as target:
            target.add_include("taihe/common.h", pkg_abi_info.header)
            for func in pkg.functions:
                for param in func.params:
                    type_abi_info = TypeAbiInfo.get(self.am, param.ty_ref.resolved_ty)
                    target.add_include(*type_abi_info.impl_headers)
                if return_ty_ref := func.return_ty_ref:
                    type_abi_info = TypeAbiInfo.get(self.am, return_ty_ref.resolved_ty)
                    target.add_include(*type_abi_info.impl_headers)
                self.gen_func(func, target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        target: CHeaderWriter,
    ):
        func_abi_info = GlobFuncAbiInfo.get(self.am, func)
        func_c_impl_info = GlobFuncCImplInfo.get(self.am, func)
        func_impl = "C_FUNC_IMPL"
        params = []
        args = []
        for param in func.params:
            type_abi_info = TypeAbiInfo.get(self.am, param.ty_ref.resolved_ty)
            params.append(f"{type_abi_info.as_param} {param.name}")
            args.append(param.name)
        params_str = ", ".join(params)
        args_str = ", ".join(args)
        if return_ty_ref := func.return_ty_ref:
            type_abi_info = TypeAbiInfo.get(self.am, return_ty_ref.resolved_ty)
            return_ty_name = type_abi_info.as_owner
        else:
            return_ty_name = "void"
        target.writelns(
            f"#define {func_c_impl_info.macro}({func_impl}) \\",
            f"    {return_ty_name} {func_abi_info.mangled_name}({params_str}) {{ \\",
            f"        return {func_impl}({args_str}); \\",
            f"    }}",
        )


class CImplSourcesGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_c_impl_info = PackageCImplInfo.get(self.am, pkg)
        with CSourceWriter(
            self.om,
            f"temp/{pkg_c_impl_info.source}",
            FileKind.TEMPLATE,
        ) as target:
            target.add_include(pkg_c_impl_info.header)
            for func in pkg.functions:
                self.gen_func(func, target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        target: CSourceWriter,
    ):
        func_c_impl_info = GlobFuncCImplInfo.get(self.am, func)
        func_c_impl_name = f"{func.name}_impl"
        params = []
        for param in func.params:
            type_abi_info = TypeAbiInfo.get(self.am, param.ty_ref.resolved_ty)
            params.append(f"{type_abi_info.as_param} {param.name}")
        params_str = ", ".join(params)
        if return_ty_ref := func.return_ty_ref:
            type_abi_info = TypeAbiInfo.get(self.am, return_ty_ref.resolved_ty)
            return_ty_name = type_abi_info.as_owner
        else:
            return_ty_name = "void"
        with target.indented(
            f"{return_ty_name} {func_c_impl_name}({params_str}) {{",
            f"}}",
        ):
            target.writelns(
                f"// TODO",
            )
        target.writelns(
            f"{func_c_impl_info.macro}({func_c_impl_name});",
        )
