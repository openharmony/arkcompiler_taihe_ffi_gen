from typing import Any

from typing_extensions import override

from taihe.codegen.generator import COutputBuffer
from taihe.codegen.mangle import DeclKind, encode
from taihe.semantics.declarations import (
    FuncBaseDecl,
    # FuncDecl,
    Package,
    PackageGroup,
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


class KNBridgePackageInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.api.hpp"


class KNBridgeFuncBaseDeclInfo(AbstractAnalysis[FuncBaseDecl]):
    def __init__(self, am: AnalysisManager, f: FuncBaseDecl) -> None:
        segments = f.segments
        self.name = encode(segments, DeclKind.FUNCTION)
        self.konan_proj_name = (
            "_konan_function_0"  # Assuming that information is obtained from IR here
        )
        self.konan_param_name = "KObjHeader*, KObjHeader*, KObjHeader**"  # Assuming that information is obtained from IR here
        self.konan_retval_name = (
            "KObjHeader*"  # Assuming that information is obtained from IR here
        )
        info = KNBridgeNormalTypeRefDeclInfo.get(am, f.retvals[0].ty)
        self.return_ty = info.name
        params = []
        convert_params = []
        for param in f.params:
            abi_param_type_info = KNBridgeParamTypeRefDeclInfo.get(am, param.ty)
            params.append(f"{abi_param_type_info.name} {param.name}")
            if abi_param_type_info.convert_func:
                convert_params.append(
                    f"{abi_param_type_info.convert_func}({param.name}, {param.name}_holder.slot())"
                )
            else:
                convert_params.append(f"{param.name}")
        convert_params.append("result_holder.slot()")
        self.params_str = ", ".join(params)
        self.convert_params_str = ", ".join(convert_params)


class KNBridgeNormalTypeRefDeclInfo(AbstractAnalysis[TypeAlike], TypeVisitor):
    def __init__(self, am: AnalysisManager, t: TypeAlike) -> None:
        self.am = am
        self.header = None
        self.name = None
        self.copy_func = None
        self.drop_func = None
        self.convert_func = None
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
            self.convert_func = "CreateStringFromCString"
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

        kn_bridge_pkg_name = "prefix"  # need to read from pkg_prefix

        kn_bridge_pkg_target.write(
            f"#ifndef KONAN_{kn_bridge_pkg_name.upper()}_H\n"
            f"#define KONAN_{kn_bridge_pkg_name.upper()}_H\n"
            f"#ifdef __cplusplus\n"
            f'extern "C" {{\n'
            f"#endif\n"
            f"#ifdef __cplusplus\n"
            f"typedef bool            {kn_bridge_pkg_name}_KBoolean;\n"
            f"#endif\n"
            f"typedef unsigned short     {kn_bridge_pkg_name}_KChar;\n"
            f"typedef signed char        {kn_bridge_pkg_name}_KByte;\n"
            f"typedef short              {kn_bridge_pkg_name}_KShort;\n"
            f"typedef int                {kn_bridge_pkg_name}_KInt;\n"
            f"typedef long long          {kn_bridge_pkg_name}_KLong;\n"
            f"typedef unsigned char      {kn_bridge_pkg_name}_KUByte;\n"
            f"typedef unsigned short     {kn_bridge_pkg_name}_KUShort;\n"
            f"typedef unsigned int       {kn_bridge_pkg_name}_KUInt;\n"
            f"typedef unsigned long long {kn_bridge_pkg_name}_KULong;\n"
            f"typedef float              {kn_bridge_pkg_name}_KFloat;\n"
            f"typedef double             {kn_bridge_pkg_name}_KDouble;\n"
            f"typedef float __attribute__ ((__vector_size__ (16))) {kn_bridge_pkg_name}_KVector128;\n"  # need to know compiler
            f"typedef void*              {kn_bridge_pkg_name}_KNativePtr;\n"
            f"struct {kn_bridge_pkg_name}_KType;\n"
            f"typedef struct {kn_bridge_pkg_name}_KType {kn_bridge_pkg_name}_KType;\n"
            f"\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_Byte;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_Short;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_Int;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_Long;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_Float;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_Double;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_Char;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_Boolean;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_Unit;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_UByte;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_UShort;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_UInt;\n"
            f"typedef struct {{\n"
            f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
            f"}} {kn_bridge_pkg_name}_kref_kotlin_ULong;\n"
            f"typedef struct {{\n"
            f"  /* Service functions. */\n"
            f"  void (*DisposeStablePointer)({kn_bridge_pkg_name}_KNativePtr ptr);\n"
            f"  void (*DisposeString)(const char* string);\n"
            f"  {kn_bridge_pkg_name}_KBoolean (*IsInstance)({kn_bridge_pkg_name}_KNativePtr ref, const {kn_bridge_pkg_name}_KType* type);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_Byte (*createNullableByte)({kn_bridge_pkg_name}_KByte);\n"
            f"  {kn_bridge_pkg_name}_KByte (*getNonNullValueOfByte)({kn_bridge_pkg_name}_kref_kotlin_Byte);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_Short (*createNullableShort)({kn_bridge_pkg_name}_KShort);\n"
            f"  {kn_bridge_pkg_name}_KShort (*getNonNullValueOfShort)({kn_bridge_pkg_name}_kref_kotlin_Short);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_Int (*createNullableInt)({kn_bridge_pkg_name}_KInt);\n"
            f"  {kn_bridge_pkg_name}_KInt (*getNonNullValueOfInt)({kn_bridge_pkg_name}_kref_kotlin_Int);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_Long (*createNullableLong)({kn_bridge_pkg_name}_KLong);\n"
            f"  {kn_bridge_pkg_name}_KLong (*getNonNullValueOfLong)({kn_bridge_pkg_name}_kref_kotlin_Long);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_Float (*createNullableFloat)({kn_bridge_pkg_name}_KFloat);\n"
            f"  {kn_bridge_pkg_name}_KFloat (*getNonNullValueOfFloat)({kn_bridge_pkg_name}_kref_kotlin_Float);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_Double (*createNullableDouble)({kn_bridge_pkg_name}_KDouble);\n"
            f"  {kn_bridge_pkg_name}_KDouble (*getNonNullValueOfDouble)({kn_bridge_pkg_name}_kref_kotlin_Double);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_Char (*createNullableChar)({kn_bridge_pkg_name}_KChar);\n"
            f"  {kn_bridge_pkg_name}_KChar (*getNonNullValueOfChar)({kn_bridge_pkg_name}_kref_kotlin_Char);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_Boolean (*createNullableBoolean)({kn_bridge_pkg_name}_KBoolean);\n"
            f"  {kn_bridge_pkg_name}_KBoolean (*getNonNullValueOfBoolean)({kn_bridge_pkg_name}_kref_kotlin_Boolean);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_Unit (*createNullableUnit)(void);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_UByte (*createNullableUByte)({kn_bridge_pkg_name}_KUByte);\n"
            f"  {kn_bridge_pkg_name}_KUByte (*getNonNullValueOfUByte)({kn_bridge_pkg_name}_kref_kotlin_UByte);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_UShort (*createNullableUShort)({kn_bridge_pkg_name}_KUShort);\n"
            f"  {kn_bridge_pkg_name}_KUShort (*getNonNullValueOfUShort)({kn_bridge_pkg_name}_kref_kotlin_UShort);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_UInt (*createNullableUInt)({kn_bridge_pkg_name}_KUInt);\n"
            f"  {kn_bridge_pkg_name}_KUInt (*getNonNullValueOfUInt)({kn_bridge_pkg_name}_kref_kotlin_UInt);\n"
            f"  {kn_bridge_pkg_name}_kref_kotlin_ULong (*createNullableULong)({kn_bridge_pkg_name}_KULong);\n"
            f"  {kn_bridge_pkg_name}_KULong (*getNonNullValueOfULong)({kn_bridge_pkg_name}_kref_kotlin_ULong);\n"
            f"\n"
            f"  /* User functions. */\n"
            f"  struct {{\n"
            f"    struct {{\n"
        )
        for func in pkg.functions:
            kn_bridge_func_info = KNBridgeFuncBaseDeclInfo.get(self.am, func)
            kn_bridge_pkg_target.write(
                f"      {kn_bridge_func_info.return_ty} (*{kn_bridge_func_info.name})({kn_bridge_func_info.params_str});\n"
            )
        kn_bridge_pkg_target.write(
            f"    }} root;\n"
            f"  }} kotlin;\n"
            f"}} {kn_bridge_pkg_name}_ExportedSymbols;\n"
            f"extern {kn_bridge_pkg_name}_ExportedSymbols* {kn_bridge_pkg_name}_symbols(void);\n"
            f"#ifdef __cplusplus\n"
            f'}}  /* extern "C" */\n'
            f"#endif\n"
            f"#endif  /* KONAN_{kn_bridge_pkg_name.upper()}_H */\n"
        )
        for func in pkg.functions:
            kn_bridge_func_info = KNBridgeFuncBaseDeclInfo.get(self.am, func)
            kn_bridge_pkg_target.write(
                f'extern "C" {kn_bridge_func_info.konan_retval_name} {kn_bridge_func_info.konan_proj_name}({kn_bridge_func_info.konan_param_name});\n'
                f"static {kn_bridge_func_info.return_ty} {kn_bridge_func_info.konan_proj_name}_impl({kn_bridge_func_info.params_str}) {{\n"
                f"  Kotlin_initRuntimeIfNeeded();\n"
                f"  ScopedRunnableState stateGuard;\n"
                f"  FrameOverlay* frame = getCurrentFrame();   try {{\n"
                f"  auto result =   {kn_bridge_func_info.konan_proj_name}({kn_bridge_func_info.convert_params_str});\n"
                f"  return result;\n"
                f"  }} catch (...) {{      SetCurrentFrame(reinterpret_cast<KObjHeader**>(frame));\n"
                f"      HandleCurrentExceptionWhenLeavingKotlinCode();\n"
                f"  }} \n"
                f"}}\n"
            )
        kn_bridge_pkg_target.write(
            f"static static_ExportedSymbols __konan_symbols = {{\n"
            f"  .kotlin = {{\n"
            f"    .root = {{\n"
        )
        for func in pkg.functions:
            kn_bridge_func_info = KNBridgeFuncBaseDeclInfo.get(self.am, func)
            kn_bridge_pkg_target.write(
                f"      /* {kn_bridge_func_info.name} = */ {kn_bridge_func_info.konan_proj_name}_impl,\n"
            )
        kn_bridge_pkg_target.write(f"    }},\n" f"  }},\n" f"}};\n")
