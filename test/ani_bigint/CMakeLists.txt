set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/bigint_test.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/bigint_new.taihe"
)

set(GEN_ETS_FILES
    "bigint_test.ets"
    "bigint_new.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_bigint "${IDL_FILES}" "${GEN_ETS_FILES}" "" "${USER_ETS_FILES}" "${AUTHOR_CPP_FILES}" "test")
