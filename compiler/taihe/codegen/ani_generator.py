from abc import ABCMeta

from typing_extensions import override

from taihe.codegen.cpp_generator import (
    EnumCppInfo,
    GlobFuncCppInfo,
    IfaceCppInfo,
    PackageCppInfo,
    StructCppInfo,
    TypeCppInfo,
)
from taihe.codegen.mangle import DeclKind, encode
from taihe.semantics.declarations import (
    EnumDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
    StructDecl,
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
    U16,
    ArrayType,
    BoxType,
    CallbackType,
    EnumType,
    IfaceType,
    MapType,
    ScalarType,
    SetType,
    SpecialType,
    StructType,
    Type,
    VectorType,
)
from taihe.semantics.visitor import TypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager
from taihe.utils.outputs import COutputBuffer, OutputBuffer, OutputManager


class PackageANIInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        self.src = f"{p.name}.ani.cpp"
        self.sts = f"{p.name}.ets"
        self.lib_name = (
            ani_lib_item.value if (ani_lib_item := p.attrs.get("ani_lib")) else p.name
        )
        self.cls_name = f"L{self.lib_name}/ETSGLOBAL;"


class GlobFuncANIInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        p = f.node_parent
        assert p
        segments = [*p.segments, f.name]
        self.mangled_name = encode(segments, DeclKind.ANI_FUNC)
        self.sts_name = f.name


class IfaceMethodANIInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, f: IfaceMethodDecl) -> None:
        d = f.node_parent
        assert d
        p = d.node_parent
        assert p
        segments = [*p.segments, d.name, f.name]
        self.mangled_name = encode(segments, DeclKind.ANI_FUNC)
        self.sts_name = f.name


class StructANIInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        p = d.node_parent
        assert p
        self.header = f"{p.name}.{d.name}.ani.hpp"
        self.sts_name = d.name
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.cls_name = f"L{pkg_ani_info.lib_name}/{self.sts_name};"


class EnumANIInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        p = d.node_parent
        assert p
        self.header = f"{p.name}.{d.name}.ani.hpp"
        self.sts_name = d.name
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.cls_name = f"L{pkg_ani_info.lib_name}/{self.sts_name};"


class IfaceANIInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        p = d.node_parent
        assert p
        self.header = f"{p.name}.{d.name}.ani.hpp"
        self.sts_name = d.name
        pkg_ani_info = PackageANIInfo.get(am, p)
        self.cls_name = f"L{pkg_ani_info.lib_name}/{self.sts_name};"


class AbstractTypeANIInfo(metaclass=ABCMeta):
    ani_type: str
    sts_type: str
    headers: list[str]

    def __init__(self, am: AnalysisManager, t: Type):
        self.cpp_info = TypeCppInfo.get(am, t)

    def return_from_ani(self, env, val):
        return f"taihe::core::ani_convert<{self.cpp_info.as_owner}>::from_ani({env}, {val})"

    def return_into_ani(self, env, val):
        return f"taihe::core::ani_convert<{self.cpp_info.as_owner}>::into_ani({env}, {val})"

    def pass_from_ani(self, env, val):
        return f"taihe::core::ani_convert<{self.cpp_info.as_param}>::from_ani({env}, {val})"

    def pass_into_ani(self, env, val):
        return f"taihe::core::ani_convert<{self.cpp_info.as_param}>::into_ani({env}, {val})"


class EnumTypeANIInfo(AbstractAnalysis[EnumType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        AbstractTypeANIInfo.__init__(self, am, t)
        enum_ani_info = EnumANIInfo.get(am, t.ty_decl)
        self.sts_type = enum_ani_info.sts_name
        self.ani_type = "ani_object"
        self.headers = [enum_ani_info.header]


class StructTypeANIInfo(AbstractAnalysis[StructType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: StructType):
        AbstractTypeANIInfo.__init__(self, am, t)
        struct_ani_info = StructANIInfo.get(am, t.ty_decl)
        self.sts_type = struct_ani_info.sts_name
        self.ani_type = "ani_object"
        self.headers = [struct_ani_info.header]


class IfaceTypeANIInfo(AbstractAnalysis[IfaceType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        AbstractTypeANIInfo.__init__(self, am, t)
        iface_ani_info = IfaceANIInfo.get(am, t.ty_decl)
        self.sts_type = iface_ani_info.sts_name
        self.ani_type = "ani_object"
        self.headers = [iface_ani_info.header]


class ScalarTypeANIInfo(AbstractAnalysis[ScalarType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        AbstractTypeANIInfo.__init__(self, am, t)
        res = {
            BOOL: "boolean",
            F32: "float",
            F64: "double",
            I8: "byte",
            I16: "short",
            I32: "int",
            I64: "long",
            U16: "char",
        }.get(t)
        if res is None:
            raise ValueError
        self.sts_type = res
        self.ani_type = f"ani_{res}"
        self.headers = ["ani_runtime.hpp"]


class SpecialTypeANIInfo(AbstractAnalysis[SpecialType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: SpecialType):
        AbstractTypeANIInfo.__init__(self, am, t)
        if t != STRING:
            raise ValueError
        self.sts_type = "string"
        self.ani_type = "ani_string"
        self.headers = ["ani_runtime.hpp"]


class ArrayTypeANIInfo(AbstractAnalysis[ArrayType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)


class BoxTypeANIInfo(AbstractAnalysis[BoxType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: BoxType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)


class VectorTypeANIInfo(AbstractAnalysis[VectorType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: VectorType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)
        val_ty_ani_info = TypeANIInfo.get(am, t.val_ty)
        self.sts_type = f"Array<{val_ty_ani_info.sts_type}>"
        self.ani_type = "ani_object"
        self.headers = [
            "ani_runtime.hpp",
            *val_ty_ani_info.headers,
        ]


class MapTypeANIInfo(AbstractAnalysis[MapType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)
        key_ty_ani_info = TypeANIInfo.get(am, t.key_ty)
        val_ty_ani_info = TypeANIInfo.get(am, t.val_ty)
        self.sts_type = f"Map<{key_ty_ani_info.sts_type}, {val_ty_ani_info.sts_type}>"
        self.ani_type = "ani_object"
        self.headers = [
            "ani_runtime.hpp",
            *key_ty_ani_info.headers,
            *val_ty_ani_info.headers,
        ]


class SetTypeANIInfo(AbstractAnalysis[SetType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: SetType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)
        key_ty_ani_info = TypeANIInfo.get(am, t.key_ty)
        self.sts_type = f"Set<{key_ty_ani_info.sts_type}>"
        self.ani_type = "ani_object"
        self.headers = [
            "ani_runtime.hpp",
            *key_ty_ani_info.headers,
        ]


class CallbackTypeANIInfo(AbstractAnalysis[CallbackType], AbstractTypeANIInfo):
    def __init__(self, am: AnalysisManager, t: CallbackType) -> None:
        AbstractTypeANIInfo.__init__(self, am, t)


class TypeANIInfo(TypeVisitor[AbstractTypeANIInfo]):
    def __init__(self, am: AnalysisManager):
        self.am = am

    @staticmethod
    def get(am: AnalysisManager, t: Type | None) -> AbstractTypeANIInfo:
        assert t is not None
        return TypeANIInfo(am).handle_type(t)

    @override
    def visit_enum_type(self, t: EnumType) -> AbstractTypeANIInfo:
        return EnumTypeANIInfo.get(self.am, t)

    @override
    def visit_struct_type(self, t: StructType) -> AbstractTypeANIInfo:
        return StructTypeANIInfo.get(self.am, t)

    @override
    def visit_iface_type(self, t: IfaceType) -> AbstractTypeANIInfo:
        return IfaceTypeANIInfo.get(self.am, t)

    @override
    def visit_scalar_type(self, t: ScalarType) -> AbstractTypeANIInfo:
        return ScalarTypeANIInfo.get(self.am, t)

    @override
    def visit_special_type(self, t: SpecialType) -> AbstractTypeANIInfo:
        return SpecialTypeANIInfo.get(self.am, t)

    @override
    def visit_array_type(self, t: ArrayType) -> AbstractTypeANIInfo:
        return ArrayTypeANIInfo.get(self.am, t)

    @override
    def visit_box_type(self, t: BoxType) -> AbstractTypeANIInfo:
        return BoxTypeANIInfo.get(self.am, t)

    @override
    def visit_vector_type(self, t: VectorType) -> AbstractTypeANIInfo:
        return VectorTypeANIInfo.get(self.am, t)

    @override
    def visit_map_type(self, t: MapType) -> AbstractTypeANIInfo:
        return MapTypeANIInfo.get(self.am, t)

    @override
    def visit_set_type(self, t: SetType) -> AbstractTypeANIInfo:
        return SetTypeANIInfo.get(self.am, t)

    @override
    def visit_callback_type(self, t: CallbackType) -> AbstractTypeANIInfo:
        return CallbackTypeANIInfo.get(self.am, t)


class STSCodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_ani_info = PackageANIInfo.get(self.am, pkg)
        pkg_sts_target = OutputBuffer.create(self.tm, f"{pkg_ani_info.sts}")
        pkg_sts_target.write(f'loadLibrary("{pkg_ani_info.lib_name}");\n')
        for struct in pkg.structs:
            self.gen_struct(struct, pkg_sts_target)
        for enum in pkg.enums:
            self.gen_enum(enum, pkg_sts_target)
        for iface in pkg.interfaces:
            self.gen_iface(iface, pkg_sts_target)
        for func in pkg.functions:
            self.gen_func(func, pkg_sts_target)

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_ani_target: OutputBuffer,
    ):
        func_ani_info = GlobFuncANIInfo.get(self.am, func)
        params_sts = []
        for param in func.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            params_sts.append(f"{param.name}: {type_ani_info.sts_type}")
        params_sts_str = ", ".join(params_sts)
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            sts_return_ty_name = type_ani_info.sts_type
        else:
            sts_return_ty_name = "void"
        pkg_ani_target.write(
            f"native function {func_ani_info.sts_name}({params_sts_str}): {sts_return_ty_name};\n"
        )

    def gen_struct(
        self,
        struct: StructDecl,
        pkg_ani_target: OutputBuffer,
    ):
        struct_ani_info = StructANIInfo.get(self.am, struct)
        pkg_ani_target.write(
            f"export class {struct_ani_info.sts_name} {{\n" f"    constructor(\n"
        )
        for field in struct.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            pkg_ani_target.write(f"        {field.name}: {type_ani_info.sts_type},\n")
        pkg_ani_target.write("    ) {\n")
        for field in struct.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            pkg_ani_target.write(f"        this.{field.name} = {field.name};\n")
        pkg_ani_target.write("    }\n")
        for field in struct.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            pkg_ani_target.write(
                f"    public {field.name}: {type_ani_info.sts_type};\n"
            )
        pkg_ani_target.write("}\n")

    def gen_enum(
        self,
        enum: EnumDecl,
        pkg_ani_target: OutputBuffer,
    ):
        pass

    def gen_iface(
        self,
        iface: IfaceDecl,
        pkg_ani_target: OutputBuffer,
    ):
        pass


class ANICodeGenerator:
    def __init__(self, tm: OutputManager, am: AnalysisManager):
        self.tm = tm
        self.am = am

    def generate(self, pg: PackageGroup):
        for pkg in pg.packages:
            self.gen_package_file(pkg)

    def gen_package_file(self, pkg: PackageDecl):
        pkg_ani_info = PackageANIInfo.get(self.am, pkg)
        pkg_ani_target = COutputBuffer.create(self.tm, f"{pkg_ani_info.src}", False)
        pkg_cpp_info = PackageCppInfo.get(self.am, pkg)
        pkg_ani_target.include("ani.h")
        pkg_ani_target.include(pkg_cpp_info.header)
        for struct in pkg.structs:
            self.gen_struct_file(struct)
        for enum in pkg.enums:
            self.gen_enum_file(enum)
        for iface in pkg.interfaces:
            self.gen_iface_file(iface)
        for iface in pkg.interfaces:
            self.gen_iface_methods(iface, pkg_ani_target)
        for func in pkg.functions:
            self.gen_func(func, pkg_ani_target)
        pkg_ani_target.write(
            "ANI_EXPORT ani_status ANI_Constructor(ani_vm *vm, uint32_t *result) {\n"
            "    ani_env *env;\n"
            "    if (ANI_OK != vm->GetEnv(ANI_VERSION_1, &env)) {\n"
            "        return ANI_ERROR;\n"
            "    }\n"
        )
        pkg_ani_target.write(
            f"    {{\n"
            f'    static const char *className = "{pkg_ani_info.cls_name}";\n'
            f"    ani_class cls;\n"
            f"    if (ANI_OK != env->FindClass(className, &cls)) {{\n"
            f"        return ANI_ERROR;\n"
            f"    }}\n"
            f"    ani_native_function methods[] = {{\n"
        )
        for func in pkg.functions:
            func_ani_info = GlobFuncANIInfo.get(self.am, func)
            pkg_ani_target.write(
                f'        {{"{func_ani_info.sts_name}", nullptr, reinterpret_cast<void*>({func_ani_info.mangled_name})}},\n'
            )
        pkg_ani_target.write(
            "    };\n"
            "    if (ANI_OK != env->Class_BindNativeMethods(cls, methods, sizeof(methods) / sizeof(ani_native_function))) {\n"
            "        return ANI_ERROR;\n"
            "    }\n"
            "    }\n"
        )
        pkg_ani_target.write(
            "    *result = ANI_VERSION_1;\n" "    return ANI_OK;\n" "}\n"
        )

    def gen_func(
        self,
        func: GlobFuncDecl,
        pkg_ani_target: COutputBuffer,
    ):
        func_ani_info = GlobFuncANIInfo.get(self.am, func)
        func_cpp_info = GlobFuncCppInfo.get(self.am, func)
        params_ani = [
            "[[maybe_unused]] ani_env *env",
            "[[maybe_unused]] ani_object object",
        ]
        args_cpp = []
        for param in func.params:
            type_ani_info = TypeANIInfo.get(self.am, param.ty_ref.resolved_ty)
            pkg_ani_target.include(*type_ani_info.headers)
            params_ani.append(f"{type_ani_info.ani_type} {param.name}")
            args_cpp.append(type_ani_info.pass_from_ani("env", param.name))
        params_ani_str = ", ".join(params_ani)
        args_cpp_str = ", ".join(args_cpp)
        cpp_result = f"{func_cpp_info.full_name}({args_cpp_str})"
        if return_ty_ref := func.return_ty_ref:
            type_ani_info = TypeANIInfo.get(self.am, return_ty_ref.resolved_ty)
            pkg_ani_target.include(*type_ani_info.headers)
            ani_return_ty_name = type_ani_info.ani_type
            ani_result = type_ani_info.return_into_ani("env", cpp_result)
        else:
            ani_return_ty_name = "void"
            ani_result = cpp_result
        pkg_ani_target.write(
            f"static {ani_return_ty_name} {func_ani_info.mangled_name}({params_ani_str}) {{\n"
            f"    return {ani_result};\n"
            f"}}\n"
        )

    def gen_struct_file(
        self,
        struct: StructDecl,
    ):
        struct_cpp_info = StructCppInfo.get(self.am, struct)
        struct_ani_info = StructANIInfo.get(self.am, struct)
        struct_ani_target = COutputBuffer.create(
            self.tm, f"include/{struct_ani_info.header}", True
        )
        struct_ani_target.include(struct_cpp_info.defn_header)
        for field in struct.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            struct_ani_target.include(*type_ani_info.headers)
        # owner
        struct_ani_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"struct ani_convert<{struct_cpp_info.as_owner}> {{\n"
        )
        # return into abi
        struct_ani_target.write(
            f"    static ani_object into_ani(ani_env* env, {struct_cpp_info.full_name}&& value) {{\n"
        )
        fields_ani = []
        for field in struct.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            field_ani = type_ani_info.return_into_ani(
                "env", f"std::move(value.{field.name})"
            )
            struct_ani_target.write(
                f"        {type_ani_info.ani_type} {field.name}_value = {field_ani};\n"
            )
            fields_ani.append(f"{field.name}_value")
        fields_ani_str = ", ".join(fields_ani)
        struct_ani_target.write(
            f"        ani_object obj;\n"
            f'        static const char *className = "{struct_ani_info.cls_name}";\n'
            f"        ani_class cls;\n"
            f"        env->FindClass(className, &cls);\n"
            f"        ani_method ctor;\n"
            f'        env->Class_FindMethod(cls, "<ctor>", nullptr, &ctor);\n'
            f"        env->Object_New(cls, ctor, &obj, {fields_ani_str});\n"
            f"        return obj;\n"
            f"    }}\n"
        )
        # return from abi
        struct_ani_target.write(
            f"    static {struct_cpp_info.full_name} from_ani(ani_env* env, ani_object obj) {{\n"
            f'        static const char *className = "{struct_ani_info.cls_name}";\n'
            f"        ani_class cls;\n"
            f"        env->FindClass(className, &cls);\n"
        )
        fields_cpp = []
        for field in struct.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            struct_ani_target.write(
                f"        {type_ani_info.ani_type} {field.name}_value;\n"
                f'        taihe::core::ani_helper<{type_ani_info.ani_type}>::Object_GetPropertyByName(env, obj, "{field.name}", reinterpret_cast<taihe::core::ani_helper<{type_ani_info.ani_type}>::ani_base*>(&{field.name}_value));\n'
            )
            fields_cpp.append(
                type_ani_info.return_from_ani("env", f"{field.name}_value")
            )
        fields_cpp_str = ", ".join(fields_cpp)
        struct_ani_target.write(
            f"        return {struct_cpp_info.full_name}{{{fields_cpp_str}}};\n"
            f"    }}\n"
        )
        struct_ani_target.write("};\n")
        struct_ani_target.write("}\n")
        # param
        struct_ani_target.write(
            f"namespace taihe::core {{\n"
            f"template<>\n"
            f"struct ani_convert<{struct_cpp_info.as_param}> {{\n"
        )
        # pass into abi
        struct_ani_target.write(
            f"    static ani_object into_ani(ani_env* env, {struct_cpp_info.full_name} const& value) {{\n"
        )
        fields_ani = []
        for field in struct.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            field_ani = type_ani_info.pass_into_ani("env", f"value.{field.name}")
            struct_ani_target.write(
                f"        {type_ani_info.ani_type} {field.name}_value = {field_ani};\n"
            )
            fields_ani.append(f"{field.name}_value")
        fields_ani_str = ", ".join(fields_ani)
        struct_ani_target.write(
            f"        ani_object obj;\n"
            f'        static const char *className = "{struct_ani_info.cls_name}";\n'
            f"        ani_class cls;\n"
            f"        env->FindClass(className, &cls);\n"
            f"        ani_method ctor;\n"
            f'        env->Class_FindMethod(cls, "<ctor>", nullptr, &ctor);\n'
            f"        env->Object_New(cls, ctor, &obj, {fields_ani_str});\n"
            f"        return obj;\n"
            f"    }}\n"
        )
        # pass from abi
        struct_ani_target.write(
            f"    static {struct_cpp_info.full_name} from_ani(ani_env* env, ani_object obj) {{\n"
            f'        static const char *className = "{struct_ani_info.cls_name}";\n'
            f"        ani_class cls;\n"
            f"        env->FindClass(className, &cls);\n"
        )
        fields_cpp = []
        for field in struct.fields:
            type_ani_info = TypeANIInfo.get(self.am, field.ty_ref.resolved_ty)
            struct_ani_target.write(
                f"        {type_ani_info.ani_type} {field.name}_value;\n"
                f'        taihe::core::ani_helper<{type_ani_info.ani_type}>::Object_GetPropertyByName(env, obj, "{field.name}", reinterpret_cast<taihe::core::ani_helper<{type_ani_info.ani_type}>::ani_base*>(&{field.name}_value));\n'
            )
            fields_cpp.append(type_ani_info.pass_from_ani("env", f"{field.name}_value"))
        fields_cpp_str = ", ".join(fields_cpp)
        struct_ani_target.write(
            f"        return {struct_cpp_info.full_name}{{{fields_cpp_str}}};\n"
            f"    }}\n"
        )
        struct_ani_target.write("};\n")
        struct_ani_target.write("}\n")

    def gen_enum_file(
        self,
        enum: EnumDecl,
    ):
        enum_ani_info = EnumANIInfo.get(self.am, enum)
        enum_cpp_info = EnumCppInfo.get(self.am, enum)
        enum_ani_target = COutputBuffer.create(
            self.tm, f"include/{enum_ani_info.header}", True
        )
        enum_ani_target.include(enum_cpp_info.defn_header)
        for item in enum.items:
            if item.ty_ref is None:
                continue
            type_ani_info = TypeANIInfo.get(self.am, item.ty_ref.resolved_ty)
            enum_ani_target.include(*type_ani_info.headers)

    def gen_iface_file(
        self,
        iface: IfaceDecl,
    ):
        iface_ani_info = IfaceANIInfo.get(self.am, iface)
        iface_cpp_info = IfaceCppInfo.get(self.am, iface)
        iface_ani_target = COutputBuffer.create(
            self.tm, f"include/{iface_ani_info.header}", True
        )
        iface_ani_target.include(iface_cpp_info.defn_header)

    def gen_iface_methods(
        self,
        iface: IfaceDecl,
        pkg_ani_target: COutputBuffer,
    ):
        pass
