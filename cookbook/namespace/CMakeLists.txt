set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/module1.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/module1.foo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/module2.bar.taihe"
)

set(GEN_ETS_FILES
    "module1.ets"
    "module2.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(namespace "${IDL_FILES}" "-Csts:keep-name" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")
