from typing import Any, Optional

from taihe.codegen.abi_generator import COutputBuffer
from taihe.codegen.mangle import DeclKind, encode
from taihe.semantics.declarations import (
    BaseFuncDecl,
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
    Type,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import OutputManager


class KNBridgePackageInfo(AbstractAnalysis[Package]):
    def __init__(self, am: AnalysisManager, p: Package) -> None:
        self.header = f"{p.name}.api.hpp"


class KNBridgeFuncBaseDeclInfo(AbstractAnalysis[BaseFuncDecl]):
    def __init__(self, am: AnalysisManager, f: BaseFuncDecl) -> None:
        segments = f.segments
        self.name = encode(segments, DeclKind.FUNCTION)
        self.konan_proj_name = f.attrs["konan_name"].value
        assert isinstance(self.konan_proj_name, str)

        params = []
        konan_params_only_ty = []
        convert_params = []
        for param in f.params:
            param_type_info = KNBridgeTypeInfo.get(am, param.ty_ref.resolved_ty)
            params.append(f"{param_type_info.as_param} {param.name}")
            konan_params_only_ty.append(f"{param_type_info.as_konan_param}")
            if param_type_info.param_covert_func:
                convert_params.append(
                    f"{param_type_info.param_covert_func}({param.name}, {param.name}_holder.slot())"
                )
            else:
                convert_params.append(f"{param.name}")

        convert_params.append("result_holder.slot()")
        konan_params_only_ty.append(f"KObjHeader**")

        self.params_str = ", ".join(params)
        self.konan_params_only_ty = ", ".join(konan_params_only_ty)
        self.convert_params_str = ", ".join(convert_params)
        if f.return_ty_ref is None:
            self.return_ty_header = None
            self.return_ty_name = "void"
            self.return_ty_str = ""
        else:
            ty_info = KNBridgeTypeInfo.get(am, f.return_ty_ref.resolved_ty)
            self.return_ty_header = ty_info.header
            self.return_ty_name = ty_info.as_retval
            if ty_info.retval_covert_func:
                self.return_ty_str = f"{ty_info.retval_covert_func}(result)"
            else:
                self.return_ty_str = "result"

        if f.return_ty_ref is None:
            self.return_ty_konan_header = None
            self.return_ty_konan_name = "void"
            self.return_ty_konan_str = ""
        else:
            ty_info = KNBridgeTypeInfo.get(am, f.return_ty_ref.resolved_ty)
            self.return_ty_konan_header = ty_info.header
            self.return_ty_konan_name = ty_info.as_konan_retval


class KNBridgeTypeInfo(AbstractAnalysis[Optional[Type]], TypeVisitor[None]):
    def __init__(self, am: AnalysisManager, t: Optional[Type]) -> None:
        self.am = am
        self.header = None
        self.as_owner = None
        self.as_param = None
        self.as_retval = None
        self.as_konan_param = None
        self.as_konan_retval = None
        self.param_covert_func = None
        self.retval_covert_func = None
        self.handle_type(t)

    def visit_scalar_type(self, t: ScalarType):
        res = {
            BOOL: "TH_BOOL",
            F32: "TH_FLOAT",
            F64: "TH_DOUBLE",
            I8: "TH_INT8",
            I16: "TH_INT16",
            I32: "TH_INT32",
            I64: "TH_INT64",
            U8: "TH_UINT8",
            U16: "TH_UINT16",
            U32: "TH_UINT32",
            U64: "TH_UINT64",
        }.get(t)
        self.as_param = res
        self.as_owner = res
        self.as_retval = res
        self.as_konan_param = res
        self.as_konan_retval = res
        if res is None:
            raise ValueError

    def visit_special_type(self, t: SpecialType) -> Any:
        if t == STRING:
            self.as_owner = "const char*"
            self.as_param = "const char*"
            self.as_retval = "const char*"
            self.as_konan_param = "TH_STRING"
            self.as_konan_retval = "TH_STRING"
            self.param_covert_func = "CreateStringFromCString"
            self.retval_covert_func = "CreateCStringFromString"
        else:
            raise ValueError


class KNBridgeCodeGenerator:
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

        kn_bridge_pkg_name = pkg.attrs["pkg_name"].value
        assert isinstance(kn_bridge_pkg_name, str)

        kn_predefined_type_list = [
            "Byte",
            "Short",
            "Int",
            "Long",
            "Float",
            "Double",
            "Char",
            "Boolean",
            "Unit",
            "UByte",
            "UShort",
            "UInt",
            "ULong",
        ]

        kn_bridge_pkg_target.write(
            f"#define TH_BOOL {kn_bridge_pkg_name}_KBoolean\n"
            f"#define TH_FLOAT {kn_bridge_pkg_name}_KFloat\n"
            f"#define TH_DOUBLE {kn_bridge_pkg_name}_KDouble\n"
            f"#define TH_INT8 {kn_bridge_pkg_name}_KByte\n"
            f"#define TH_INT16 {kn_bridge_pkg_name}_KShort\n"
            f"#define TH_INT32 {kn_bridge_pkg_name}_KInt\n"
            f"#define TH_INT64 {kn_bridge_pkg_name}_KInt\n"
            f"#define TH_UINT8 {kn_bridge_pkg_name}_KUByte\n"
            f"#define TH_UINT16 {kn_bridge_pkg_name}_KUShort\n"
            f"#define TH_UINT32 {kn_bridge_pkg_name}_KUInt\n"
            f"#define TH_UINT64 {kn_bridge_pkg_name}_KUInt\n"
            f"#define TH_STRING KObjHeader*\n"
            f"\n"
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
        )
        for predefinedType in kn_predefined_type_list:
            kn_bridge_pkg_target.write(
                f"typedef struct {{\n"
                f"{kn_bridge_pkg_name}_KNativePtr pinned;\n"
                f"}} {kn_bridge_pkg_name}_kref_kotlin_{predefinedType};\n"
            )

        kn_bridge_pkg_target.write(
            f"typedef struct {{\n"
            f"  /* Service functions. */\n"
            f"  void (*DisposeStablePointer)({kn_bridge_pkg_name}_KNativePtr ptr);\n"
            f"  void (*DisposeString)(const char* string);\n"
            f"  {kn_bridge_pkg_name}_KBoolean (*IsInstance)({kn_bridge_pkg_name}_KNativePtr ref, const {kn_bridge_pkg_name}_KType* type);\n"
        )

        for predefinedType in kn_predefined_type_list:
            if predefinedType != "Unit":
                kn_bridge_pkg_target.write(
                    f"  {kn_bridge_pkg_name}_kref_kotlin_{predefinedType} (*createNullable{predefinedType})({kn_bridge_pkg_name}_K{predefinedType});\n"
                    f"  {kn_bridge_pkg_name}_K{predefinedType} (*getNonNullValueOf{predefinedType})({kn_bridge_pkg_name}_kref_kotlin_{predefinedType});\n"
                )
            else:
                kn_bridge_pkg_target.write(
                    f"  {kn_bridge_pkg_name}_kref_kotlin_Unit (*createNullableUnit)(void);\n"
                )

        kn_bridge_pkg_target.write(
            f"\n" f"  /* User functions. */\n" f"  struct {{\n" f"    struct {{\n"
        )

        for iface in pkg.interfaces:
            kn_bridge_pkg_target.write(f"      struct {{\n")
            for method in iface.methods:
                kn_bridge_iface_method_info = KNBridgeFuncBaseDeclInfo.get(
                    self.am, method
                )
                kn_bridge_pkg_target.write(
                    f"        {kn_bridge_iface_method_info.return_ty_konan_name} (*{kn_bridge_iface_method_info.name})({kn_bridge_pkg_name}_kref_{iface.name} thiz, {kn_bridge_iface_method_info.params_str});\n"
                )
            kn_bridge_pkg_target.write(f"      }} {iface.name};\n")

        for func in pkg.functions:
            kn_bridge_func_info = KNBridgeFuncBaseDeclInfo.get(self.am, func)
            kn_bridge_pkg_target.write(
                f"      {kn_bridge_func_info.return_ty_name} (*{kn_bridge_func_info.name})({kn_bridge_func_info.params_str});\n"
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
            f"struct KObjHeader;\n"
            f"typedef struct KObjHeader KObjHeader;\n"
            f"struct KTypeInfo;\n"
            f"typedef struct KTypeInfo KTypeInfo;\n"
            f"\n"
            f"struct FrameOverlay;\n"
            f"typedef struct FrameOverlay FrameOverlay;\n"
            f"\n"
            f"#define RUNTIME_NOTHROW __attribute__((nothrow))\n"
            f"\n"
            f"#if __has_attribute(retain)\n"
            f"#define RUNTIME_EXPORT __attribute__((used,retain))\n"
            f"#else\n"
            f"#define RUNTIME_EXPORT __attribute__((used))\n"
            f"#endif\n"
            f"\n"
            f"#define RUNTIME_NORETURN __attribute__((noreturn))\n"
            f"\n"
            f'extern "C" {{\n'
            f"void UpdateStackRef(KObjHeader**, const KObjHeader*) RUNTIME_NOTHROW;\n"
            f"KObjHeader* AllocInstance(const KTypeInfo*, KObjHeader**) RUNTIME_NOTHROW;\n"
            f"KObjHeader* DerefStablePointer(void*, KObjHeader**) RUNTIME_NOTHROW;\n"
            f"void* CreateStablePointer(KObjHeader*) RUNTIME_NOTHROW;\n"
            f"void DisposeStablePointer(void*) RUNTIME_NOTHROW;\n"
            f"{kn_bridge_pkg_name}_KBoolean IsInstanceInternal(const KObjHeader*, const KTypeInfo*) RUNTIME_NOTHROW;\n"
            f"void EnterFrame(KObjHeader** start, int parameters, int count) RUNTIME_NOTHROW;\n"
            f"void LeaveFrame(KObjHeader** start, int parameters, int count) RUNTIME_NOTHROW;\n"
            f"void SetCurrentFrame(KObjHeader** start) RUNTIME_NOTHROW;\n"
            f"FrameOverlay* getCurrentFrame() RUNTIME_NOTHROW;\n"
            f"void Kotlin_initRuntimeIfNeeded();\n"
            f"void Kotlin_mm_switchThreadStateRunnable() RUNTIME_NOTHROW;\n"
            f"void Kotlin_mm_switchThreadStateNative() RUNTIME_NOTHROW;\n"
            f"void HandleCurrentExceptionWhenLeavingKotlinCode();\n"
            f"\n"
            f"KObjHeader* CreateStringFromCString(const char*, KObjHeader**);\n"
            f"char* CreateCStringFromString(const KObjHeader*);\n"
            f"void DisposeCString(char* cstring);\n"
            f'}}  // extern "C"\n'
            f"\n"
            f"struct {kn_bridge_pkg_name}_FrameOverlay {{\n"
            f"  {kn_bridge_pkg_name}_FrameOverlay* previous;\n"
            f"  {kn_bridge_pkg_name}_KInt parameters;\n"
            f"  {kn_bridge_pkg_name}_KInt count;\n"
            f"}};\n"
            f"\n"
            f"class KObjHolder {{\n"
            f"public:\n"
            f"  KObjHolder() : obj_(nullptr) {{\n"
            f"    EnterFrame(frame(), 0, sizeof(*this)/sizeof(void*));\n"
            f"  }}\n"
            f"  explicit KObjHolder(const KObjHeader* obj) : obj_(nullptr) {{\n"
            f"    EnterFrame(frame(), 0, sizeof(*this)/sizeof(void*));\n"
            f"    UpdateStackRef(&obj_, obj);\n"
            f"  }}\n"
            f"  ~KObjHolder() {{\n"
            f"    LeaveFrame(frame(), 0, sizeof(*this)/sizeof(void*));\n"
            f"  }}\n"
            f"  KObjHeader* obj() {{ return obj_; }}\n"
            f"  KObjHeader** slot() {{ return &obj_; }}\n"
            f" private:\n"
            f"  {kn_bridge_pkg_name}_FrameOverlay frame_;\n"
            f"  KObjHeader* obj_;\n"
            f"\n"
            f"  KObjHeader** frame() {{ return reinterpret_cast<KObjHeader**>(&frame_); }}\n"
            f"}};\n"
            f"\n"
            f"class ScopedRunnableState {{\n"
            f"public:\n"
            f"  ScopedRunnableState() noexcept {{ Kotlin_mm_switchThreadStateRunnable(); }}\n"
            f"  ~ScopedRunnableState() {{ Kotlin_mm_switchThreadStateNative(); }}\n"
            f"  ScopedRunnableState(const ScopedRunnableState&) = delete;\n"
            f"  ScopedRunnableState(ScopedRunnableState&&) = delete;\n"
            f"  ScopedRunnableState& operator=(const ScopedRunnableState&) = delete;\n"
            f"  ScopedRunnableState& operator=(ScopedRunnableState&&) = delete;\n"
            f"}};\n"
            f"\n"
            f"static void DisposeStablePointerImpl({kn_bridge_pkg_name}_KNativePtr ptr) {{\n"
            f"  Kotlin_initRuntimeIfNeeded();\n"
            f"  ScopedRunnableState stateGuard;\n"
            f"  DisposeStablePointer(ptr);\n"
            f"}}\n"
            f"static void DisposeStringImpl(const char* ptr) {{\n"
            f"  DisposeCString((char*)ptr);\n"
            f"}}\n"
            f"static {kn_bridge_pkg_name}_KBoolean IsInstanceImpl({kn_bridge_pkg_name}_KNativePtr ref, const {kn_bridge_pkg_name}_KType* type) {{\n"
            f"  Kotlin_initRuntimeIfNeeded();\n"
            f"  ScopedRunnableState stateGuard;\n"
            f"  KObjHolder holder;\n"
            f"  return IsInstanceInternal(DerefStablePointer(ref, holder.slot()), (const KTypeInfo*)type);\n"
            f"}}\n"
        )
        for predefinedType in kn_predefined_type_list:
            if predefinedType != "Unit":
                kn_bridge_pkg_target.write(
                    f'extern "C" KObjHeader* Kotlin_box{predefinedType}({kn_bridge_pkg_name}_K{predefinedType} value, KObjHeader**);\n'
                    f"static {kn_bridge_pkg_name}_kref_kotlin_{predefinedType} createNullable{predefinedType}Impl({kn_bridge_pkg_name}_K{predefinedType} value) {{\n"
                    f"  Kotlin_initRuntimeIfNeeded();\n"
                    f"  ScopedRunnableState stateGuard;\n"
                    f"  KObjHolder result_holder;\n"
                    f"  KObjHeader* result = Kotlin_box{predefinedType}(value,  result_holder.slot());\n"
                    f"  return {kn_bridge_pkg_name}_kref_kotlin_{predefinedType} {{ .pinned = CreateStablePointer(result) }};\n"
                    f"}}\n"
                    f'extern "C" {kn_bridge_pkg_name}_K{predefinedType} Kotlin_unbox{predefinedType}(KObjHeader*);\n'
                    f"static {kn_bridge_pkg_name}_K{predefinedType} getNonNullValueOf{predefinedType}Impl({kn_bridge_pkg_name}_kref_kotlin_{predefinedType} value) {{\n"
                    f"  Kotlin_initRuntimeIfNeeded();\n"
                    f"  ScopedRunnableState stateGuard;\n"
                    f"  KObjHolder value_holder;\n"
                    f"  return Kotlin_unbox{predefinedType}(DerefStablePointer(value.pinned, value_holder.slot()));\n"
                    f"}}\n"
                )
            else:
                kn_bridge_pkg_target.write(
                    f'extern "C" KObjHeader* Kotlin_box{predefinedType}( KObjHeader**);\n'
                    f"static {kn_bridge_pkg_name}_kref_kotlin_{predefinedType} createNullable{predefinedType}Impl() {{\n"
                    f"  Kotlin_initRuntimeIfNeeded();\n"
                    f"  ScopedRunnableState stateGuard;\n"
                    f" KObjHolder result_holder;\n"
                    f"  KObjHeader* result = Kotlin_box{predefinedType}( result_holder.slot());\n"
                    f"  return {kn_bridge_pkg_name}_kref_kotlin_{predefinedType} {{ .pinned = CreateStablePointer(result) }};\n"
                    f"}}\n"
                )
        for func in pkg.functions:
            kn_bridge_func_info = KNBridgeFuncBaseDeclInfo.get(self.am, func)
            kn_bridge_pkg_target.write(
                f'extern "C" {kn_bridge_func_info.return_ty_konan_name} {kn_bridge_func_info.konan_proj_name}({kn_bridge_func_info.konan_params_only_ty});\n'
                f"static {kn_bridge_func_info.return_ty_name} {kn_bridge_func_info.konan_proj_name}_impl({kn_bridge_func_info.params_str}) {{\n"
                f"  Kotlin_initRuntimeIfNeeded();\n"
                f"  ScopedRunnableState stateGuard;\n"
                f"  FrameOverlay* frame = getCurrentFrame();\n"
            )
            for param in func.params:
                kn_bridge_pkg_target.write(f"  KObjHolder {param.name}_holder;\n")
            kn_bridge_pkg_target.write(f"  try {{\n")
            if func.return_ty_ref is None:
                kn_bridge_pkg_target.write(
                    f"{kn_bridge_func_info.konan_proj_name}({kn_bridge_func_info.convert_params_str});\n"
                )
            else:
                kn_bridge_pkg_target.write(
                    f"    KObjHolder result_holder;\n"
                    f"    auto result = {kn_bridge_func_info.konan_proj_name}({kn_bridge_func_info.convert_params_str});\n"
                    f"    return {kn_bridge_func_info.return_ty_str};\n"
                )
            kn_bridge_pkg_target.write(
                f"  }} catch (...) {{\n"
                f"    SetCurrentFrame(reinterpret_cast<KObjHeader**>(frame));\n"
                f"    HandleCurrentExceptionWhenLeavingKotlinCode();\n"
                f"  }} \n"
                f"}}\n"
            )
        kn_bridge_pkg_target.write(
            f"static {kn_bridge_pkg_name}_ExportedSymbols __konan_symbols = {{\n"
            f"  .DisposeStablePointer = DisposeStablePointerImpl,\n"
            f"  .DisposeString = DisposeStringImpl,\n"
            f"  .IsInstance = IsInstanceImpl,\n"
        )
        for predefinedType in kn_predefined_type_list:
            if predefinedType != "Unit":
                kn_bridge_pkg_target.write(
                    f"  .createNullable{predefinedType} = createNullable{predefinedType}Impl,\n"
                    f"  .getNonNullValueOf{predefinedType} = getNonNullValueOf{predefinedType}Impl,\n"
                )
            else:
                kn_bridge_pkg_target.write(
                    f"  .createNullableUnit = createNullableUnitImpl,\n"
                )

        kn_bridge_pkg_target.write(f"  .kotlin = {{\n" f"    .root = {{\n")
        for iface in pkg.interfaces:
            kn_bridge_pkg_target.write(f"      .{iface.name} {{\n")
            for method in iface.methods:
                kn_bridge_pkg_target.write(
                    f"        /* {method.name} = */ {method.attrs['konan_name'].value}_impl, \n"
                )
            kn_bridge_pkg_target.write(f"      }}, \n")
        for func in pkg.functions:
            kn_bridge_func_info = KNBridgeFuncBaseDeclInfo.get(self.am, func)
            kn_bridge_pkg_target.write(
                f"      /* {kn_bridge_func_info.name} = */ {kn_bridge_func_info.konan_proj_name}_impl,\n"
            )
        kn_bridge_pkg_target.write(f"    }},\n" f"  }},\n" f"}};\n")
        kn_bridge_pkg_target.write(
            f"#ifdef TH_BOOL\n"
            f"#undef TH_BOOL\n"
            f"#endif\n"
            f"#ifdef TH_FLOAT\n"
            f"#undef TH_FLOAT\n"
            f"#endif\n"
            f"#ifdef TH_DOUBLE\n"
            f"#undef TH_DOUBLE\n"
            f"#endif\n"
            f"#ifdef TH_INT8\n"
            f"#undef TH_INT8\n"
            f"#endif\n"
            f"#ifdef TH_INT16\n"
            f"#undef TH_INT16\n"
            f"#endif\n"
            f"#ifdef TH_INT32\n"
            f"#undef TH_INT32\n"
            f"#endif\n"
            f"#ifdef TH_INT64\n"
            f"#undef TH_INT64\n"
            f"#endif\n"
            f"#ifdef TH_UINT8\n"
            f"#undef TH_UINT8\n"
            f"#endif\n"
            f"#ifdef TH_UINT16\n"
            f"#undef TH_UINT16\n"
            f"#endif\n"
            f"#ifdef TH_UINT32\n"
            f"#undef TH_UINT32\n"
            f"#endif\n"
            f"#ifdef TH_UINT64\n"
            f"#undef TH_UINT64\n"
            f"#endif\n"
            f"#ifdef TH_STRING\n"
            f"#undef TH_STRING\n"
            f"#endif\n"
            f"\n"
        )
