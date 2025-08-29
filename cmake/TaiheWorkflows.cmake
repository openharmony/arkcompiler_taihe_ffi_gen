include(${CMAKE_CURRENT_LIST_DIR}/TaiheUtils.cmake)

function(add_taihe_ani_library target_name idl_files)
  set(options "")
  set(oneValueArgs "TAIHE_CONFIGS" "TAIHEC_PATH")
  set(multiValueArgs "")
  cmake_parse_arguments(ARGS "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
  if(NOT ARGS_TAIHE_CONFIGS)
    set(ARGS_TAIHE_CONFIGS "")
  endif()
  if(ARGS_TAIHEC_PATH)
    set(TAIHEC_PATH "${ARGS_TAIHEC_PATH}")
  elseif(DEFINED IDE_TAIHEC_PATH)
    set(TAIHEC_PATH "${IDE_TAIHEC_PATH}")
  else()
    set(TAIHEC_PATH "taihec")
  endif()

  add_taihe_library(${target_name} "${idl_files}"
    AUTHOR_BRIDGE "cpp-author"
    USER_BRIDGE "ani-bridge"
    TAIHE_CONFIGS "${ARGS_TAIHE_CONFIGS}"
    TAIHEC_PATH ${TAIHEC_PATH}
  )
endfunction()

function(add_taihe_cpp_library target_name idl_files)
  set(options "")
  set(oneValueArgs "TAIHE_CONFIGS" "TAIHEC_PATH")
  set(multiValueArgs "")
  cmake_parse_arguments(ARGS "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
  if(NOT ARGS_TAIHE_CONFIGS)
    set(ARGS_TAIHE_CONFIGS "")
  endif()
  if(ARGS_TAIHEC_PATH)
    set(TAIHEC_PATH "${ARGS_TAIHEC_PATH}")
  elseif(DEFINED IDE_TAIHEC_PATH)
    set(TAIHEC_PATH "${IDE_TAIHEC_PATH}")
  else()
    set(TAIHEC_PATH "taihec")
  endif()

  add_taihe_library(${target_name} "${idl_files}"
    AUTHOR_BRIDGE "cpp-author"
    USER_BRIDGE "cpp-user"
    TAIHE_CONFIGS "${ARGS_TAIHE_CONFIGS}"
    TAIHEC_PATH ${TAIHEC_PATH}
  )
endfunction()
