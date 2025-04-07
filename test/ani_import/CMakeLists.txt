set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/mate.bar.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/mate.foo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/mate.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/nova.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/pura.baz.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/pura.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/test.inner.taihe"
)

set(GEN_ETS_FILES
    "mate.ets"
    "nova.ets"
    "pura.ets"
    "@ohos.test.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_import "${IDL_FILES}" "${GEN_ETS_FILES}" "" "${USER_ETS_FILES}" "${AUTHOR_CPP_FILES}" "test")
