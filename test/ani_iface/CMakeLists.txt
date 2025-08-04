include(../../cmake/TaiheWorkflows.cmake)
setup_taihe_cmake_test_env()
cmake_minimum_required(VERSION 3.18)
project(ani_iface)

set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/iface_readonly_test.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/iface_test.taihe"
)

set(GEN_ETS_FILES
    "iface_readonly_test.ets"
    "iface_test.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_iface "${IDL_FILES}" "" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")
