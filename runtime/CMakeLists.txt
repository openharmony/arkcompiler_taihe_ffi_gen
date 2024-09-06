cmake_minimum_required(VERSION 3.9) # For GTest

project(TaiheRuntime C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Handy for development.
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_library(taihe-rt
  src/string.c
)

target_include_directories(taihe-rt PUBLIC include)
