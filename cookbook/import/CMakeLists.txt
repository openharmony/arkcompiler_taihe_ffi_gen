set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/user.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/notification.taihe"
)

set(GEN_ETS_FILES
    "user.ets"
    "notification.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(import "${IDL_FILES}" "${GEN_ETS_FILES}" "" "${USER_ETS_FILES}" "${AUTHOR_CPP_FILES}" "cookbook")