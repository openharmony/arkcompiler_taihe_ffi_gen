find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})

# string abi test
add_executable(string_abi_test string_abi_test.cpp)

target_link_libraries(string_abi_test
    ${GTEST_LIBRARIES}
    pthread  # if used Linux
    taihe-rt
)

add_test(NAME string_abi_test COMMAND string_abi_test)

# string test
add_executable(string_test string_test.cpp)

target_link_libraries(string_test
    ${GTEST_LIBRARIES}
    pthread  # if used Linux
    taihe-rt
)

add_test(NAME string_test COMMAND string_test)