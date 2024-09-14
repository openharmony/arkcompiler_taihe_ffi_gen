#include <gtest/gtest.h>
#include <string.h>
extern "C" {
#include <taihe/string.abi.h>
}

// Test case for tstr_new
TEST(TStringTest, CreateNewString) {
    const char* test_str = "Hello";
    struct TString* tstr = (struct TString*)tstr_new(test_str, strlen(test_str));

    ASSERT_NE(tstr, nullptr);  // Ensure the string is created
    EXPECT_EQ(tstr_len(tstr), strlen(test_str));  // Check length
    EXPECT_STREQ(tstr_buf(tstr), test_str);  // Check content

    tstr_drop(tstr);  // Clean up
}

// Test case for tstr_new with invalid input (non-null terminated string)
TEST(TStringTest, CreateNewStringInvalidInput) {
    const char invalid_str[] = {'H', 'e', 'l', 'l', 'o', 'X'};
    struct TString* tstr = (struct TString*)tstr_new(invalid_str, 5);  // Invalid, since the input is not null-terminated

    EXPECT_EQ(tstr, nullptr);  // Should return nullptr
}

// Test case for tstr_dup (copying a string)
TEST(TStringTest, DuplicateString) {
    const char* test_str = "Hello";
    struct TString* tstr = (struct TString*)tstr_new(test_str, strlen(test_str));

    ASSERT_NE(tstr, nullptr);  // Ensure the original string is created
    const struct TString* dup_str = tstr_dup(tstr);

    ASSERT_NE(dup_str, nullptr);  // Ensure the duplicated string is created
    EXPECT_EQ(tstr_len(dup_str), strlen(test_str));  // Check length of duplicated string
    EXPECT_STREQ(tstr_buf(dup_str), test_str);  // Check content of duplicated string

    tstr_drop(tstr);  // Clean up
    tstr_drop((struct TString*)dup_str);  // Clean up duplicated string
}

// Test case for tstr_drop (reference counting and destruction)
TEST(TStringTest, DropString) {
    const char* test_str = "Hello";
    struct TString* tstr = (struct TString*)tstr_new(test_str, strlen(test_str));

    ASSERT_NE(tstr, nullptr);  // Ensure the string is created
    tstr_drop(tstr);  // Should properly free the memory
}

// Test cae for tstr_concat (concat two string)
TEST(TStringTest, TestTstrConcat) {
    const char* test_left_tstr = "Hello";
    struct TString* left_tstr = (struct TString*)tstr_new(test_left_tstr, strlen(test_left_tstr));
    const char* test_right_str = "World";
    struct TString* right_tstr = (struct TString*)tstr_new(test_right_str, strlen(test_right_str));

    struct TString* tstr = tstr_concat(left_tstr, right_tstr);
    ASSERT_NE(tstr, nullptr);
    ASSERT_EQ(tstr_len(tstr), 10);
    ASSERT_STREQ(tstr_buf(tstr), "HelloWorld");
    tstr_drop(left_tstr);
    tstr_drop(right_tstr);
    tstr_drop(tstr);
}

// Test case for tstr_substr (substr a string)
TEST(TStringTest, TestTstrSubstr) {
    const char* test_tstr = "Lalaland";
    struct TString* tstr = (struct TString*)tstr_new(test_tstr, strlen(test_tstr));
    struct TString* sub_tstr = tstr_substr(tstr, 2, 2);
    ASSERT_NE(tstr, nullptr);
    ASSERT_EQ(tstr_len(sub_tstr), 2);
    ASSERT_STREQ(tstr_buf(sub_tstr), "la");
    tstr_drop(tstr);
    tstr_drop(sub_tstr);
}

// Test case for reference counting (tref_inc and tref_dec)
TEST(TRefCountTest, ReferenceCounting) {
    TRefCount ref_count;
    tref_set(&ref_count, 1);  // Set initial count to 1

    EXPECT_EQ(tref_inc(&ref_count), 1);  // Increment and check previous value (should be 1)
    EXPECT_EQ(tref_dec(&ref_count), 0);  // Decrement and check if it should be freed (should return 0 for no free)
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
