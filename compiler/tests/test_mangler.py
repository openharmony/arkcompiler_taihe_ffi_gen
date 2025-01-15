from taihe.codegen.mangle import DeclKind, decode, encode


def test_name_mangler():
    """Comprehensive test suite for NameMangler."""
    test_cases = [
        (["a", "b_c", "d", "e_f_g"], DeclKind.FUNCTION),
        (["pkg", "sub_pkg", "name"], DeclKind.ENUM_TAG),
        (["x", "y", "z"], DeclKind.STRUCT),
        (["a_b_c"], DeclKind.FUNCTION),
        (["a"], DeclKind.FUNCTION),
        (["a_b", "c_d_e"], DeclKind.FUNCTION),
        (["test", "with____multiple", "consecutive"], DeclKind.FUNCTION),
    ]

    for segments, kind in test_cases:
        try:
            mangled = encode(segments, kind)
            decoded = decode(mangled)
            assert decoded == (
                segments,
                kind,
            ), f"Failed roundtrip: {segments} -> {mangled} -> {decoded}"
            print(f"Success: {segments} -> {mangled} -> {decoded}")
        except Exception as e:
            print(f"Error testing {segments}: {e!s}")
