# from io import StringIO
# from os import makedirs, path
# from pathlib import Path
from typing import Any

from typing_extensions import override

from taihe.codegen.generator import COutputBuffer

# from taihe.codegen.generator import ABIFuncBaseDeclInfo, COutputBuffer
from taihe.codegen.mangle import DeclKind, encode
from taihe.semantics.declarations import (
    # EnumDecl,
    # EnumItemDecl,
    FuncBaseDecl,
    FuncDecl,
    # IfaceDecl,
    Package,
    PackageGroup,
    # StructDecl,
)
from taihe.semantics.types import (
    BOOL,
    F32,
    F64,
    I8,
    I16,
    I32,
    I64,
    STRING,
    U8,
    U16,
    U32,
    U64,
    ScalarType,
    SpecialType,
    TypeAlike,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager

# from taihe.utils.outputs import OutputBase, OutputManager


class KNBridgePackageInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.api.hpp"


class KNBridgeFuncBaseDeclInfo(AbstractAnalysis[FuncBaseDecl]):
    def __init__(self, am: AnalysisManager, f: FuncBaseDecl) -> None:
        segments = f.segments
        self.name = encode(segments, DeclKind.FUNCTION)
        info = KNBridgeNormalTypeRefDeclInfo.get(am, f.retvals[0].ty)
        self.return_ty = info.name
        params = []
        for param in f.params:
            abi_param_type_info = KNBridgeParamTypeRefDeclInfo.get(am, param.ty)
            params.append(f"{abi_param_type_info.name} {param.name}")
        self.params_str = ", ".join(params)


class KNBridgeNormalTypeRefDeclInfo(AbstractAnalysis[TypeAlike], TypeVisitor):
    def __init__(self, am: AnalysisManager, t: TypeAlike) -> None:
        self.am = am
        self.header = None
        self.name = None
        self.copy_func = None
        self.drop_func = None
        self.handle_type(t)

    def visit_scalar_type(self, t: ScalarType):
        self.name = {
            BOOL: "bool",
            F32: "float",
            F64: "double",
            I8: "int8_t",
            I16: "int16_t",
            I32: "int32_t",
            I64: "int64_t",
            U8: "uint8_t",
            U16: "uint16_t",
            U32: "uint32_t",
            U64: "uint64_t",
        }.get(t)
        if self.name is None:
            raise ValueError

    def visit_special_type(self, t: SpecialType) -> Any:
        if t == STRING:
            self.name = "char*"
        else:
            raise ValueError


class KNBridgeParamTypeRefDeclInfo(KNBridgeNormalTypeRefDeclInfo):
    @override
    def visit_special_type(self, t: SpecialType) -> Any:
        if t == STRING:
            self.name = "const char*"
        else:
            raise ValueError


class KNBridgeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: Package):
        kn_bridge_pkg_info = KNBridgePackageInfo.get(self.am, pkg)
        kn_bridge_pkg_target = COutputBuffer.create(
            self.tm, f"include/{kn_bridge_pkg_info.header}", True
        )

        for func in pkg.functions:
            self.gen_func(func, kn_bridge_pkg_target)

    def gen_func(
        self,
        func: FuncDecl,
        kn_bridge_pkg_target: COutputBuffer,
    ):
        kn_bridge_func_info = KNBridgeFuncBaseDeclInfo.get(self.am, func)

        kn_bridge_pkg_target.write(
            f"typedef struct {{\n"
            f"  /* User functions. */\n"
            f"  struct {{\n"
            f"    struct {{\n"
            f"      {kn_bridge_func_info.return_ty} (*{kn_bridge_func_info.name})({kn_bridge_func_info.params_str});\n"
            f"    }} root;\n"
            f"  }} kotlin;\n"
            f"}} static_ExportedSymbols;\n"
            f"\n"
            f'extern "C" void* _konan_function_0();\n'
            f"static void* _konan_function_0_impl() {{\n"
            f"  Kotlin_initRuntimeIfNeeded();\n"
            f"  ScopedRunnableState stateGuard;\n"
            f"  FrameOverlay* frame = getCurrentFrame();   try {{\n"
            f"  auto result =   _konan_function_0();\n"
            f"  return result;\n"
            f"  }} catch (...) {{      SetCurrentFrame(reinterpret_cast<KObjHeader**>(frame));\n"
            f"      HandleCurrentExceptionWhenLeavingKotlinCode();\n"
            f"  }} \n"
            f"}}\n"
            f"static static_ExportedSymbols __konan_symbols = {{\n"
            f"  .kotlin = {{\n"
            f"    .root = {{\n"
            f"      /* {kn_bridge_func_info.name} = */ _konan_function_0_impl,\n"
            f"    }},\n"
            f"  }},\n"
            f"}};\n"
        )
