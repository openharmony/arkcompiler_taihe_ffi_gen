set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/new_ns.my_ns.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/new_ns.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/ns_test.baz.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/ns_test.foo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/ns_test.foo.bar.taihe"
)

set(GEN_ETS_FILES
    "new_ns.ets"
    "ns_test.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(namespace "${IDL_FILES}" "${GEN_ETS_FILES}" "" "${USER_ETS_FILES}" "${AUTHOR_CPP_FILES}" "cookbook")
