include(../../cmake/TaiheWorkflows.cmake)
setup_taihe_cmake_test_env()
cmake_minimum_required(VERSION 3.18)
project(ani_export_default)

set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/export_enum.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/export_iface.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/export_namespace.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/export_struct.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/export_union.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/export_toplevel_func.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/import_example.taihe"
)

set(GEN_ETS_FILES
    "export_enum.ets"
    "export_iface.ets"
    "export_ns.ets"
    "export_struct.ets"
    "export_union.ets"
    "export_toplevel_func.ets"
    "import_example.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_export_default "${IDL_FILES}" "" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")
