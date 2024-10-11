import os

import pytest
from exceptiongroup import ExceptionGroup

from taihe.compilation import compile as taihec
from taihe.exceptions import (
    EnumValueCollisionError,
    PackageAliasConflictError,
    PackageNotExistError,
    PackageNotImportedError,
    QualifierError,
    RecursiveInclusionError,
    SymbolConflictError,
    SymbolConflictWithNamespaceError,
    TypeAliasConflictError,
    TypeNotExistError,
    TypeNotImportedError,
)


def run_test():
    idl_dir = "test_cases/idl"
    dst_dir = "test_cases/test/include"
    try:
        taihec([idl_dir], dst_dir)
    except ExceptionGroup as e:
        for exception in e.exceptions:
            os.system("cd `dirname $0`")
            os.system("rm -rf test_cases")
            raise exception from e


def write_file(test_case: str) -> None:
    idl_dir = "test_cases/idl"
    os.system("cd `dirname $0`")
    os.system("rm -rf test_cases")
    os.system("mkdir test_cases")
    os.system("mkdir test_cases/idl")

    file = [i.strip() for i in test_case.split("---")]
    for i in range(0, len(file), 2):
        with open(f"{idl_dir}/{file[i]}", "w") as f:
            f.writelines(file[i + 1])


def test_pkg_alias_conflict() -> None:
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
    write_file(test_case)
    with pytest.raises(PackageAliasConflictError):
        run_test()


def test_pkg_not_exist() -> None:
    test_case = """package.taihe
        ---
        use a;
        """
    write_file(test_case)
    with pytest.raises(PackageNotExistError):
        run_test()


def test_pkg_not_imported() -> None:
    test_case = """package.taihe
        ---
        struct BadStruct {
            a: unimported.package.Type;
        }
        """
    write_file(test_case)
    with pytest.raises(PackageNotImportedError):
        run_test()


def test_sym_conflict_1() -> None:
    test_case = """package.taihe
        ---
        function bad_func(a: i32, a: i32): ();
        """
    write_file(test_case)
    with pytest.raises(SymbolConflictError):
        run_test()


def test_sym_conflict_2() -> None:
    test_case = """package.taihe
        ---
        enum BadEnum {
            A;
            A;
        }
        """
    write_file(test_case)
    with pytest.raises(SymbolConflictError):
        run_test()


def test_sym_conflict_3() -> None:
    test_case = """package.taihe
        ---
        struct BadStruct {
            a: i32;
            a: i32;
        }
        """
    write_file(test_case)
    with pytest.raises(SymbolConflictError):
        run_test()


def test_sym_conflict_namespace() -> None:
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
    write_file(test_case)
    with pytest.raises(SymbolConflictWithNamespaceError):
        run_test()


def test_qualifier_1() -> None:
    test_case = """package.taihe
        ---
        function bad_func(a: mut i32): ();
        """
    write_file(test_case)
    with pytest.raises(QualifierError):
        run_test()


def test_qualifier_2() -> None:
    test_case = """package.taihe
        ---
        enum Enum {
            A;
        }
        struct Struct {
            a: Enum;
        }
        function bad_func(a: mut Struct, b: mut Enum): ();
        """
    write_file(test_case)
    with pytest.raises(QualifierError):
        run_test()


def test_enum_value_collision_1() -> None:
    test_case = """package.taihe
        ---
        enum BadEnum {
            A=if !(if 1+1==2 then 2<1&&3<2 else 1!=1) then -1 else -2;
            B=-1;
        }
        """
    write_file(test_case)
    with pytest.raises(EnumValueCollisionError):
        run_test()


def test_enum_value_collision2() -> None:
    test_case = """package.taihe
        ---
        enum BadEnum {
            A = 0b01 << 0b01;
            B = if (7 << 1 + 1) + (3 * 3 - 2 & 11) == 31 && 1 + 1 == 2 then 1 else 10;
            C;
        }
        """
    write_file(test_case)
    with pytest.raises(EnumValueCollisionError):
        run_test()


def test_type_alias_conflict() -> None:
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
    write_file(test_case)
    with pytest.raises(TypeAliasConflictError):
        run_test()


def test_type_not_exist_1() -> None:
    test_case = """package.taihe
        ---
        from package.example1 use A;
        ---
        package.example1.taihe
        ---
        """
    write_file(test_case)
    with pytest.raises(TypeNotExistError):
        run_test()


def test_type_not_exist_2() -> None:
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
    write_file(test_case)
    with pytest.raises(TypeNotExistError):
        run_test()


def test_type_not_imported() -> None:
    test_case = """package.taihe
        ---
        struct BadStruct {
            a: UnimportedType;
        }
        """
    write_file(test_case)
    with pytest.raises(TypeNotImportedError):
        run_test()


def test_recursive_inclusion() -> None:
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
    write_file(test_case)
    with pytest.raises(RecursiveInclusionError):
        run_test()
