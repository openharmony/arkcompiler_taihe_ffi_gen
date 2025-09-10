include(../../cmake/TaiheWorkflows.cmake)
setup_taihe_cmake_test_env()
cmake_minimum_required(VERSION 3.18)
project(reversed)

set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/impl.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/native_user.taihe"
)

set(GEN_ETS_FILES
    "impl.ets"
    "native_user.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/user_impl.ets"
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(reversed "${IDL_FILES}" "" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")