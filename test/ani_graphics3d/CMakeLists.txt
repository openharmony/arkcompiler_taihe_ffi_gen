set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/scene.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/sceneNodeParameters.taihe"

)

set(GEN_ETS_FILES
    "scene.ets"
    "sceneNodeParameters.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

set(AUTHOR_INCLUDE
    "${CMAKE_CURRENT_LIST_DIR}/author/include"
)

add_ani_demo(ani_graphics3d "${IDL_FILES}" "" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "${AUTHOR_INCLUDE}" "${AUTHOR_CPP_FILES}")
