from taihe.driver import SemanticTestCompilerInstance
from taihe.utils.diagnostics import DiagBase
from taihe.utils.exceptions import (
    DeclarationNotInScopeError,
    DeclNotExistError,
    DeclRedefDiagError,
    DuplicateExtendsWarn,
    EnumValueCollisionError,
    ExtendsTypeError,
    IDLSyntaxError,
    NotATypeError,
    PackageNotExistError,
    PackageNotInScopeError,
    PackageRedefDiagError,
    RecursiveExtensionError,
    RecursiveInclusionError,
    StructFieldTypeError,
    SymbolConflictWithNamespaceError,
)


def run_test(test_case: str, error_type: type[DiagBase]):
    test_contents = [i.strip(" \t\n") for i in test_case.split("---")]
    test_files = []
    for i in range(0, len(test_contents), 2):
        test_files.append((test_contents[i][:-6], test_contents[i + 1]))
    test_instance = SemanticTestCompilerInstance(test_files)
    test_instance.test()
    error_list = test_instance.diagnostics_manager.error_msg
    assert any(isinstance(err, error_type) for err in error_list)


def test_package_not_exist():
    test_case = """package.taihe
---
use a;
"""
    run_test(test_case, PackageNotExistError)


def test_package_not_in_scope_1():
    test_case = """package.taihe
---
struct BadStruct {
    a: unimported.package.Type;
}
"""
    run_test(test_case, PackageNotInScopeError)


def test_package_not_in_scope_2():
    test_case = """package.taihe
---
struct A {
    a: i32;
}
struct B{
    b: A.Type;
}
"""
    run_test(test_case, PackageNotInScopeError)


def test_package_not_in_scope_3():
    test_case = """package.taihe
---
from package.example use B;
struct A {
    a: B.Type;
}
---
package.example.taihe
---
struct B{
    b: i32;
}
"""
    run_test(test_case, PackageNotInScopeError)


def test_decl_redef_1():
    test_case = """package.taihe
---
function bad_func(a: i32, a: i32): ();
"""
    run_test(test_case, DeclRedefDiagError)


def test_decl_redef_2():
    test_case = """package.taihe
---
enum BadEnum {
    A;
    A;
}
"""
    run_test(test_case, DeclRedefDiagError)


def test_decl_redef_3():
    test_case = """package.taihe
---
struct BadStruct {
    a: i32;
    a: i32;
}
"""
    run_test(test_case, DeclRedefDiagError)


def test_decl_redef_4():
    test_case = """package.taihe
---
from package.example1 use A;
from package.example2 use A;
---
package.example1.taihe
---
struct A {
    a: i32;
}
---
package.example2.taihe
---
struct A {
    a: i32;
}
"""
    run_test(test_case, DeclRedefDiagError)


def test_decl_redef_5():
    test_case = """package.taihe
---
use package.example1 as example;
use package.example2 as example;
---
package.example1.taihe
---
---
package.example2.taihe
---
"""
    run_test(test_case, DeclRedefDiagError)


def test_package_redef():
    test_case = """package.taihe
---
---
package.taihe
---
"""
    run_test(test_case, PackageRedefDiagError)


def test_symbol_conflict_namespace():
    test_case = """package.taihe
---
use package.example1.a;
---
package.example1.taihe
---
struct a {
    A: String;
}
---
package.example1.a.taihe
---
"""
    run_test(test_case, SymbolConflictWithNamespaceError)


def test_enum_value_collision_1():
    test_case = """package.taihe
---
enum BadEnum {
    A=if !(if 1+1==2 then 2<1&&3<2 else 1!=1) then -1 else -2;
    B=-1;
}
"""
    run_test(test_case, EnumValueCollisionError)


def test_enum_value_collision2():
    test_case = """package.taihe
---
enum BadEnum {
    A = 0b01 << 0b01;
    B = if (7 << 1 + 1) + (3 * 3 - 2 & 11) == 31 && 1 + 1 == 2 then 1 else 10;
    C;
}
"""
    run_test(test_case, EnumValueCollisionError)


def test_decl_not_exist_1():
    test_case = """package.taihe
---
from package.example1 use A;
---
package.example1.taihe
---
"""
    run_test(test_case, DeclNotExistError)


def test_decl_not_exist_2():
    test_case = """package.taihe
---
use package.example1;
struct BadStruct {
    a: package.example1.B;
}
---
package.example1.taihe
---
struct A {
    a: i32;
}
"""
    run_test(test_case, DeclNotExistError)


def test_declaration_not_in_scope_1():
    test_case = """package.taihe
---
struct BadStruct {
    a: UnimportedType;
}
"""
    run_test(test_case, DeclarationNotInScopeError)


def test_declaration_not_in_scope_2():
    test_case = """package.taihe
---
use package.example1 as example
struct A {
    a: example;
}
---
package.example1.taihe
---
"""
    run_test(test_case, DeclarationNotInScopeError)


def test_recursive_inclusion():
    test_case = """package.taihe
---
struct A {
    a: B;
}
struct B {
    a: C;
}
struct C {
    a: A;
}
"""
    run_test(test_case, RecursiveInclusionError)


def test_struct_field_type():
    test_case = """package.taihe
---
interface TestIface {}
struct A {
    a: TestIface;
}
"""
    run_test(test_case, StructFieldTypeError)


def test_extends_type():
    test_case = """package.taihe
---
interface BadIface: i32 {}
"""
    run_test(test_case, ExtendsTypeError)


def test_duplicate_extends():
    test_case = """package.taihe
---
interface TestIface {}
interface BadIface: TestIface, TestIface {}
"""
    run_test(test_case, DuplicateExtendsWarn)


def test_recursive_extension():
    test_case = """package.taihe
---
interface RecursiveIfaceA: RecursiveIfaceB {}

interface RecursiveIfaceB: RecursiveIfaceC {}

interface RecursiveIfaceC: RecursiveIfaceA {}
"""
    run_test(test_case, RecursiveExtensionError)


def test_idl_syntax():
    test_case = """package.taihe
---
struct A {
    a;
}
"""
    run_test(test_case, IDLSyntaxError)


def test_not_a_type():
    test_case = """package.taihe
---
function good_func(a: i32): ();
struct A {
    a: good_func;
}
"""
    run_test(test_case, NotATypeError)
