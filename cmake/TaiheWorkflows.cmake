include(${CMAKE_CURRENT_LIST_DIR}/TaiheUtils.cmake)

function(add_taihe_ani_library target_name idl_files)
  set(options "")
  set(oneValueArgs "TAIHE_CONFIGS" "TAIHEC_PATH")
  set(multiValueArgs "")
  cmake_parse_arguments(ARGS "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
  if(NOT ARGS_TAIHE_CONFIGS)
    set(ARGS_TAIHE_CONFIGS "")
  endif()
  if(NOT ARGS_TAIHEC_PATH)
    set(TAIHEC_PATH "taihec")
  else()
    set(TAIHEC_PATH "${ARGS_TAIHEC_PATH}")
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
  if(NOT ARGS_TAIHEC_PATH)
    set(TAIHEC_PATH "taihec")
  else()
    set(TAIHEC_PATH "${ARGS_TAIHEC_PATH}")
  endif()

  add_taihe_library(${target_name} "${idl_files}"
    AUTHOR_BRIDGE "cpp-author"
    USER_BRIDGE "cpp-user"
    TAIHE_CONFIGS "${ARGS_TAIHE_CONFIGS}"
    TAIHEC_PATH ${TAIHEC_PATH}
  )
endfunction()

function(add_ani_demo demo_name idl_files taihe_configs gen_ets_names user_ets_files user_include_dir user_cpp_files)
  if (NOT DEFINED TAIHE_STDLIB_DIR)
    execute_and_set_variable(TAIHE_STDLIB_DIR "--print-stdlib-path")
  endif()

  set(MAIN_ABC "${CMAKE_CURRENT_BINARY_DIR}/main.abc")
  
  # panda sdk 环境配置
  setup_panda_sdk()
  # ani 头文件
  setup_ani_header()
  # 编译 taihe 运行时
  add_taihe_runtime()
  # 编译 taihe 标准库
  add_taihe_stdlib()
  # ani 代码生成相关配置
  set(taihe_configs "-Gpretty-print ${taihe_configs}")
  # 生成代码
  generate_code_from_idl(${demo_name} "${idl_files}" "${gen_ets_names}" "cpp-author" "ani-bridge" "${taihe_configs}" GEN_INCLUDE_DIR GEN_ABI_C_FILES GEN_ANI_CPP_FILES GEN_ETS_FILES)
  # 生成代码静态库编译
  compile_gen_lib("taihe_gen_${demo_name}" "${GEN_INCLUDE_DIR}" "${GEN_ABI_C_FILES}" "${GEN_ANI_CPP_FILES}")
  # 动态库编译
  compile_dylib(${demo_name} "${user_include_dir}" "${user_cpp_files}" "${GEN_INCLUDE_DIR}" "taihe_gen_${demo_name}")
  # 链接为 main.abc
  set(ALL_ETS_FILES ${user_ets_files} ${GEN_ETS_FILES})
  abc_link(${demo_name} ${MAIN_ABC} "${ALL_ETS_FILES}")
  # 运行
  run_abc(${demo_name} ${MAIN_ABC})
endfunction()