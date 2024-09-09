cmake_minimum_required(VERSION 3.14)

project(TaiheRuntime C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_C_VISIBILITY_PRESET "hidden")
set(CMAKE_CXX_VISIBILITY_PRESET "hidden")

# Handy for development use.
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_library(taihe-rt SHARED
  src/string.c
)

target_include_directories(taihe-rt PUBLIC include)

# Add test directory
enable_testing()
add_subdirectory(test)