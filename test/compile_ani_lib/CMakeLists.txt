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
project(compile_ani_lib)

file(GLOB IDL_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/idl/*.taihe")

file(GLOB AUTHOR_CPP_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_LIST_DIR}/author/src/*.cpp")

set(MAIN_ABC "${CMAKE_CURRENT_BINARY_DIR}/main.abc")

# TODO: need to remove, now runtime is coupled with ani
# panda sdk 环境配置
setup_panda_sdk()
# ani 头文件
setup_ani_header()

#########################################################
############# TEST add_taihe_ani_library ################
#########################################################
add_taihe_ani_library(compile_ani_lib_taihegen
    "${IDL_FILES}"
)

add_library(compile_ani_lib SHARED ${AUTHOR_CPP_FILES})
target_compile_options(compile_ani_lib PRIVATE "-Wno-attributes")
set_target_properties(compile_ani_lib PROPERTIES LINKER_LANGUAGE CXX)
target_link_libraries(compile_ani_lib PUBLIC compile_ani_lib_taihegen)
target_link_options(compile_ani_lib PRIVATE "-Wl,--no-undefined")