#include <gtest/gtest.h>
#include <core/string.hpp>

using namespace taihe::core;

// Test default constructor
TEST(TaiheStringTest, DefaultConstructor) {
    string str;
    EXPECT_TRUE(str.empty());
    EXPECT_EQ(str.size(), 0);
    EXPECT_STREQ(str.c_str(), "");
}

// Test c style constructor
TEST(TaiheStringTest, CStrConstructor) {
    const char* testStr = "Hello";
    string str(testStr);
    EXPECT_FALSE(str.empty());
    EXPECT_EQ(str.size(), 5);
    EXPECT_STREQ(str.c_str(), "Hello");
}

// Test std::string_view constructor
TEST(TaiheStringTest, StringViewConstructor) {
    std::string_view sv = "World";
    string str(sv);
    EXPECT_FALSE(str.empty());
    EXPECT_EQ(str.size(), 5);
    EXPECT_STREQ(str.c_str(), "World");
}

// Test copy constructor
TEST(TaiheStringTest, CopyConstructor) {
    string str1("Copy");
    string str2(str1);
    EXPECT_EQ(str1.size(), str2.size());
    EXPECT_STREQ(str1.c_str(), str2.c_str());
}

// Test move constructor
TEST(TaiheStringTest, MoveConstructor) {
    string str1("Move");
    string str2(std::move(str1));
    EXPECT_STREQ(str2.c_str(), "Move");
    EXPECT_TRUE(str1.empty());
}

// Test operator=
TEST(TaiheStringTest, CopyAssignment) {
    string str1("Assignment");
    string str2;
    str2 = str1;
    EXPECT_EQ(str1.size(), str2.size());
    EXPECT_STREQ(str1.c_str(), str2.c_str());
}

// Test move operator=
TEST(TaiheStringTest, MoveAssignment) {
    string str1("Move Assignment");
    string str2;
    str2 = std::move(str1);
    EXPECT_STREQ(str2.c_str(), "Move Assignment");
    EXPECT_TRUE(str1.empty());
}

// Test `empty()` and `size()`
TEST(TaiheStringTest, EmptyAndSize) {
    string str1;
    EXPECT_TRUE(str1.empty());
    EXPECT_EQ(str1.size(), 0);

    string str2("NotEmpty");
    EXPECT_FALSE(str2.empty());
    EXPECT_EQ(str2.size(), 8);
}

// Test `front()` and `back()`
TEST(TaiheStringTest, FrontAndBack) {
    string str("Test");
    EXPECT_EQ(str.front(), 'T');
    EXPECT_EQ(str.back(), 't');
}

// Test out of range
TEST(TaiheStringTest, OutOfRange) {
    string str("Test");
    EXPECT_THROW(str[10], std::out_of_range);
}

// Test operator[]
TEST(TaiheStringTest, IndexOperator) {
    taihe::core::string s("index");
    EXPECT_EQ(s[0], 'i');
    EXPECT_EQ(s[4], 'x');
    EXPECT_THROW(s[5], std::out_of_range);
}

// Test substr function
TEST(TaiheStringTest, Substring) {
    taihe::core::string s("substring");
    taihe::core::string sub = s.substr(3, 6);
    EXPECT_EQ(sub.size(), 6);
    EXPECT_EQ(sub, "string");
}

// Test concat function
TEST(TaiheStringTest, ConcatTest) {
    taihe::core::string s1("con");
    taihe::core::string s2("cat");
    taihe::core::string s3 = concat(s1, s2);
    EXPECT_EQ(s3.size(), 6);
    EXPECT_EQ(s3, "concat");
}

// Test comparison operators
TEST(TaiheStringTest, ComparisonTest) {
    taihe::core::string s1("abc");
    taihe::core::string s2("abc");
    taihe::core::string s3("def");

    EXPECT_TRUE(s1 == s2);
    EXPECT_FALSE(s1 == s3);
    EXPECT_TRUE(s1 < s3);
    EXPECT_TRUE(s3 > s1);
}

// Test C++ to C and C to C++
TEST(TaiheStringTest, CrossLanguageTest) {
    taihe::core::string s1("abc");
    TString* s2 = taihe::core::into_abi<taihe::core::string>(s1);
    ASSERT_STREQ(tstr_buf(s2), "abc");
    ASSERT_EQ(tstr_len(s2), 3);
    taihe::core::string s3 = taihe::core::from_abi<taihe::core::string>(s2);
    EXPECT_EQ(s3, "abc");
    EXPECT_EQ(s3.size(), 3);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}