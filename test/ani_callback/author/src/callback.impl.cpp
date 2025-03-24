#include "core/callback.hpp"

#include <iostream>

#include "callbackTest.impl.hpp"
#include "core/string.hpp"
using namespace taihe::core;
void test_cb_v(callback_view<void()> f) { f(); }
void test_cb_i(callback_view<void(int32_t)> f) { f(1); }
void test_cb_s(callback_view<void(string_view, bool)> f) { f("hello", true); }
string test_cb_rs(callback_view<string(string_view)> f) {
  taihe::core::string out = f("hello");
  std::cout << out << " which is callback output in author implement"
            << std::endl;
  return "hello";
}
void test_cb_struct(
    callback_view<::callbackTest::Data(::callbackTest::Data const&)> f) {
  ::callbackTest::Data result = f(::callbackTest::Data{"a", "b", 1});
  std::cout << result.a << " " << result.b << " " << result.c << std::endl;
  return;
}

TH_EXPORT_CPP_API_test_cb_v(test_cb_v) TH_EXPORT_CPP_API_test_cb_i(test_cb_i)
    TH_EXPORT_CPP_API_test_cb_s(test_cb_s)
        TH_EXPORT_CPP_API_test_cb_rs(test_cb_rs)
            TH_EXPORT_CPP_API_test_cb_struct(test_cb_struct)
