include(../../cmake/TaiheWorkflows.cmake)
setup_taihe_cmake_test_env()
cmake_minimum_required(VERSION 3.18)
project(ani_string)

set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/string_io.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/string_op.taihe"
)

set(GEN_ETS_FILES
    "string_io.ets"
    "string_op.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_string "${IDL_FILES}" "-Csts:keep-name" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")
