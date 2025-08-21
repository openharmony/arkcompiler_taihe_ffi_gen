include(../../cmake/TaiheWorkflows.cmake)
setup_taihe_cmake_test_env()
cmake_minimum_required(VERSION 3.18)
project(ani_enum)

set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/enum_test.taihe"
)

set(GEN_ETS_FILES
    "enum_test.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_enum "${IDL_FILES}" "" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")
