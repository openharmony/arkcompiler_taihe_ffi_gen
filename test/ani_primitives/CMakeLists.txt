set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/primitives_test.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/void_func.mytest.taihe"
)

set(GEN_ETS_FILES
    "@ohos.base.ets"
    "primitives_test.ets"
    "void_func.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_primitives "${IDL_FILES}" "-Csts:keep-name" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")
