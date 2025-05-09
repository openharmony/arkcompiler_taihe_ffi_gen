set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/class_extends.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/extends_inject.taihe"
)

set(GEN_ETS_FILES
    "@ohos.base.ets"
    "class_extends.ets"
    "extends_inject.ets"
)

set(SYS_ETS_FILES 
    "Person.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(inheritance "${IDL_FILES}" "${GEN_ETS_FILES}" "${SYS_ETS_FILES}" "${USER_ETS_FILES}" "${AUTHOR_CPP_FILES}" "cookbook")
