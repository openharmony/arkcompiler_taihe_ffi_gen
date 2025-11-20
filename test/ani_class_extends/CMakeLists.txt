include(../../cmake/TaiheWorkflows.cmake)
setup_taihe_cmake_test_env()
cmake_minimum_required(VERSION 3.18)
project(ani_class_extends)

set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/foo.taihe"
)

set(GEN_ETS_FILES
    "foo.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

set(AUTHOR_INCLUDE_DIRS
    "${CMAKE_CURRENT_LIST_DIR}/author/include"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_class_extends "${IDL_FILES}" "-Csts:keep-name" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "${AUTHOR_INCLUDE_DIRS}" "${AUTHOR_CPP_FILES}")
