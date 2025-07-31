set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/new_overload.taihe"
)

set(GEN_ETS_FILES
    "new_overload.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(new_overload "${IDL_FILES}" "-Csts:keep-name" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")
