set(IDL_FILES
    "${CMAKE_CURRENT_LIST_DIR}/idl/abilityInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/applicationInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/bundleInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/elementName.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/extensionAbilityInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/hapModuleInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/metadata.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/ohos.bundle.bundleManager.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/overlayModuleInfo.taihe"
    "${CMAKE_CURRENT_LIST_DIR}/idl/skill.taihe"
)

set(GEN_ETS_FILES
    "@ohos.base.ets"
    "abilityInfo.ets"
    "applicationInfo.ets"
    "bundleInfo.ets"
    "elementName.ets"
    "extensionAbilityInfo.ets"
    "hapModuleInfo.ets"
    "metadata.ets"
    "ohos.ets"
    "overlayModuleInfo.ets"
    "skill.ets"
)

set(USER_ETS_FILES
    "${CMAKE_CURRENT_LIST_DIR}/user/main.ets"
)

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

set(AUTHOR_INCLUDE
    "${CMAKE_CURRENT_LIST_DIR}/author/include"
)

add_ani_demo(ani_bundlemanager "${IDL_FILES}" "" "${GEN_ETS_FILES}" "${USER_ETS_FILES}" "${AUTHOR_INCLUDE}" "${AUTHOR_CPP_FILES}")
