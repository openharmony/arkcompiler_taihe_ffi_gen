set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/ani_test.taihe"
)

set(GEN_ETS_FILES
    "ani_test.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_test "${IDL_FILES}" "${GEN_ETS_FILES}" "" "${USER_ETS_FILES}" "${AUTHOR_CPP_FILES}" "test")
