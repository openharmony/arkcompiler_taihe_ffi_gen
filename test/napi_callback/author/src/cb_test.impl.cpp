#include "cb_test.impl.hpp"
#include <iostream>
#include "cb_test.proj.hpp"

namespace {
void test_cb_v(::taihe::callback_view<void()> f) {
  std::cout << "CPP impl test_cb_v " << std::endl;
  f();
}

void test_cb_i(::taihe::callback_view<void(int32_t)> f) {
  std::cout << "CPP impl test_cb_i " << std::endl;
  f(1);
}

void test_cb_s(::taihe::callback_view<void(::taihe::string_view, bool)> f) {
  std::cout << "CPP impl test_cb_s " << std::endl;
  f("hello", true);
}

::taihe::string test_cb_rs(
    ::taihe::callback_view<::taihe::string(::taihe::string_view)> f) {
  ::taihe::string out = f("hello");
  std::cout << "CPP impl test_cb_rs: " << out << std::endl;
  return out;
}

void test_cb_struct(
    ::taihe::callback_view<::cb_test::Data(::cb_test::Data const &)> f) {
  ::cb_test::Data result = f(::cb_test::Data{"a", "b", 1});
  std::cout << "CPP impl test_cb_struct " << result.a << " " << result.b << " "
            << result.c << std::endl;
  return;
}

class CallbackAImpl {
public:
  CallbackAImpl() {}

  ::taihe::string operator()(::taihe::string_view a) {
    std::cout << a << std::endl;
    return "CallbackReverse";
  }
};

::taihe::callback<::taihe::string(::taihe::string_view a)> test_x(
    ::taihe::callback_view<void()> f) {
  f();
  return ::taihe::make_holder<CallbackAImpl, ::taihe::callback<::taihe::string(
                                                 ::taihe::string_view a)>>();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_test_cb_v(test_cb_v);
TH_EXPORT_CPP_API_test_cb_i(test_cb_i);
TH_EXPORT_CPP_API_test_cb_s(test_cb_s);
TH_EXPORT_CPP_API_test_cb_rs(test_cb_rs);
TH_EXPORT_CPP_API_test_cb_struct(test_cb_struct);
TH_EXPORT_CPP_API_test_x(test_x);
// NOLINTEND
