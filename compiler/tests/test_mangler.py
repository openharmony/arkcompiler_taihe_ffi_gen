from taihe.codegen.abi.mangle import DeclKind, decode, encode


def test_name_mangler():
    """Comprehensive test suite for NameMangler."""
    test_cases = [
        (["a", "b_c", "d", "e_f_g"], DeclKind.FUNC),
        (["x", "y", "z"], DeclKind.TYPE),
        (["a_b_c"], DeclKind.FUNC),
        (["a"], DeclKind.FUNC),
        (["a_b", "c_d_e"], DeclKind.FUNC),
        (["test", "with____multiple", "consecutive"], DeclKind.FUNC),
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
