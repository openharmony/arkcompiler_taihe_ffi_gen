set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/hello_ani.taihe"
)

set(GEN_ETS_FILES
    "@ohos.base.ets"
    "hello_ani.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(hello_ani "${IDL_FILES}" "-Csts:keep-name" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}" "cookbook")
