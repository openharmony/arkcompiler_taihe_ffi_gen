# Copyright (c) 2025 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

include(../../cmake/TaiheWorkflows.cmake)
setup_taihe_cmake_test_env()
cmake_minimum_required(VERSION 3.18)
project(rgb)

file(GLOB IDL_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/idl/*.taihe")

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

file(GLOB USER_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/user/src/*.cpp")

set(USER_INCLUDE ${CMAKE_CURRENT_LIST_DIR}/user/include)

set(MAIN_ABC "${CMAKE_CURRENT_BINARY_DIR}/main.abc")

# TODO: need to remove, now runtime is coupled with ani
# panda sdk 环境配置
setup_panda_sdk()
# ani 头文件
setup_ani_header()

add_taihe_library(rgb_taihegen "${IDL_FILES}"
  USER_BRIDGE "cpp-user"
)

add_library(rgb SHARED ${AUTHOR_CPP_FILES})
target_compile_options(rgb PRIVATE "-Wno-attributes")
set_target_properties(rgb PROPERTIES LINKER_LANGUAGE CXX)
target_link_libraries(rgb PUBLIC rgb_taihegen)
target_link_options(rgb PRIVATE "-Wl,--no-undefined")

add_executable(rgb_program ${USER_CPP_FILES})
target_include_directories(rgb_program
    PRIVATE
        ${USER_INCLUDE}
)
target_link_libraries(rgb_program PRIVATE rgb)

add_custom_command(TARGET rgb_program POST_BUILD
    COMMAND rgb_program
    COMMENT "Running rgb_program"
)