set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/hms.core.map.map_inner.taihe"
)

set(GEN_ETS_FILES
    "@hms.core.map.map_inner.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
    "${CMAKE_CURRENT_LIST_DIR}/user/@hms.core.map.map.ets"
    "${CMAKE_CURRENT_LIST_DIR}/user/@ohos.multimedia.image.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(union_embed "${IDL_FILES}" "-Csts:keep-name" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")
