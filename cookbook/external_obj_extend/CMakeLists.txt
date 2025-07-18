set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/external_obj_extend.taihe"
)

set(GEN_ETS_FILES
    "@ohos.base.ets"
    "external_obj_extend.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
    "${CMAKE_CURRENT_LIST_DIR}/user/other.subsystem.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(external_obj_extend "${IDL_FILES}" "-Csts:keep-name" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")
