cmake_minimum_required(VERSION 3.18)
project(TaiheGeneratedLib)

# 设置 C 编译器为 clang
set(CMAKE_C_COMPILER "clang")
# 设置 C++ 编译器为 clang++
set(CMAKE_CXX_COMPILER "clang++")

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

# include generated .cmake
include(${CMAKE_CURRENT_LIST_DIR}/generated/TaiheGenerated.cmake)

# include header files
include_directories(
    ${TAIHE_GEN_INCLUDE}
    ${TAIHE_RUNTIME_INCLUDE}
    ${EXTERNAL_INCLUDE}
)

# set source files
set(TAIHE_GEN_SRC
    ${TAIHE_RUNTIME_SRC}
    ${TAIHE_GEN_SRC}
)

add_library(taihe_generated STATIC ${TAIHE_GEN_SRC})
