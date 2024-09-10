find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})

add_executable(string_test string_test.cpp)

target_link_libraries(run_tests
    ${GTEST_LIBRARIES}
    pthread  # if used Linux
)

add_test(NAME string_test COMMAND string_test)