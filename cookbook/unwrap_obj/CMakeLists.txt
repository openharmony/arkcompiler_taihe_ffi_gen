set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/wrap_interface.taihe"
)

set(GEN_ETS_FILES
    "@ohos.base.ets"
    "wrap_interface.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(unwrap_obj "${IDL_FILES}" "${GEN_ETS_FILES}" "" "${USER_ETS_FILES}" "${AUTHOR_CPP_FILES}" "cookbook")
