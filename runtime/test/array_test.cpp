#include <gtest/gtest.h>
#include <core/array.hpp>

using namespace taihe::core;

TEST(ArrayViewTest, DefaultConstructor) {
    array_view<int> av;
    EXPECT_TRUE(av.empty());
    EXPECT_EQ(av.size(), 0);
}

TEST(ArrayViewTest, PointerConstructor) {
    int arr[] = {1, 2, 3, 4, 5};
    array_view<int> av(arr, 5);
    EXPECT_EQ(av.size(), 5);
    EXPECT_FALSE(av.empty());
    EXPECT_EQ(av[0], 1);
    EXPECT_EQ(av[4], 5);
}

TEST(ArrayViewTest, RangeConstructor) {
    int arr[] = {1, 2, 3, 4, 5};
    array_view<int> av(arr, arr + 5);
    EXPECT_EQ(av.size(), 5);
    EXPECT_EQ(av.front(), 1);
    EXPECT_EQ(av.back(), 5);
}

TEST(ArrayViewTest, AtFunction) {
    int arr[] = {1, 2, 3, 4, 5};
    array_view<int> av(arr, 5);
    EXPECT_EQ(av.at(1), 2);
    EXPECT_THROW(av.at(5), std::out_of_range); // out of range access
}

TEST(ArrayViewTest, ComparisonOperators) {
    int arr1[] = {1, 2, 3};
    int arr2[] = {1, 2, 3};
    int arr3[] = {4, 5, 6};

    array_view<int> av1(arr1, 3);
    array_view<int> av2(arr2, 3);
    array_view<int> av3(arr3, 3);

    EXPECT_TRUE(av1 == av2);
    EXPECT_FALSE(av1 == av3);
    EXPECT_TRUE(av1 < av3);
    EXPECT_TRUE(av3 > av1);
}

TEST(th_arrayTest, DefaultConstructor) {
    array<int> ta;
    EXPECT_TRUE(ta.empty());
    EXPECT_EQ(ta.size(), 0);
}

TEST(th_arrayTest, SizeConstructor) {
    array<int> ta(5);
    EXPECT_EQ(ta.size(), 5);
    EXPECT_FALSE(ta.empty());
    for (size_t i = 0; i < ta.size(); ++i) {
        EXPECT_EQ(ta[i], 0); // default-initialized to 0
    }
}

TEST(th_arrayTest, InitializerListConstructor) {
    array<int> ta = {1, 2, 3, 4, 5};
    EXPECT_EQ(ta.size(), 5);
    EXPECT_EQ(ta[2], 3);
}

TEST(th_arrayTest, MoveConstructor) {
    array<int> ta1 = {1, 2, 3};
    array<int> ta2 = std::move(ta1);
    
    EXPECT_EQ(ta2.size(), 3);
    EXPECT_TRUE(ta1.empty()); // ta1 should be empty after move
}

TEST(th_arrayTest, MoveAssignment) {
    array<int> ta1 = {1, 2, 3};
    array<int> ta2;
    ta2 = std::move(ta1);
    
    EXPECT_EQ(ta2.size(), 3);
    EXPECT_TRUE(ta1.empty()); // ta1 should be empty after move
}

TEST(th_arrayTest, ClearFunction) {
    array<int> ta(5);
    EXPECT_EQ(ta.size(), 5);
    ta.clear();
    EXPECT_TRUE(ta.empty());
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}