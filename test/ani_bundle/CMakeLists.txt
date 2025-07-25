set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/abilityInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/applicationInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/bundleInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/customizeData.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/elementName.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/hapModuleInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/moduleInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/ohos_app_ability_want.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/ohos_bundle.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/shortcutInfo.taihe"
)

set(GEN_ETS_FILES
    "abilityInfo.ets"
    "applicationInfo.ets"
    "bundleInfo.ets"
    "customizeData.ets"
    "elementName.ets"
    "hapModuleInfo.ets"
    "moduleInfo.ets"
    "ohos_app_ability_want.ets"
    "ohos_bundle.ets"
    "shortcutInfo.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

add_ani_demo(ani_bundle "${IDL_FILES}" "" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "" "${AUTHOR_CPP_FILES}")
