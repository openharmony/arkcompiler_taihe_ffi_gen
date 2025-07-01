file(GLOB IDL_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/idl/*.taihe")

set(GEN_ETS_FILES
    "@ohos.base.ets"
    "overload_test.ets"
    "overload.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_overload "${IDL_FILES}" "-Csts:keep-name" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}" "test")
