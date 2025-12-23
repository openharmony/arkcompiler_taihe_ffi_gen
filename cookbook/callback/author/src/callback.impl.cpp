#include "callback.impl.hpp"

#include "callback.Person.proj.1.hpp"
#include "stdexcept"
#include "taihe/callback.hpp"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
void cb_void_void(callback_view<void()> f) {
  f();
}

void cb_i_void(callback_view<void(int32_t)> f) {
  f(1);
}

string cb_str_str(callback_view<string(string_view)> f) {
  taihe::string out = f("hello");
  return "hello";
}

void cb_struct(
    callback_view<::callback::Person(::callback::Person const &)> f) {
  ::callback::Person result = f(::callback::Person{"Tom", 18});
  std::cout << result.name << " " << result.age << std::endl;
  return;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_cb_void_void(cb_void_void);
TH_EXPORT_CPP_API_cb_i_void(cb_i_void);
TH_EXPORT_CPP_API_cb_str_str(cb_str_str);
TH_EXPORT_CPP_API_cb_struct(cb_struct);
// NOLINTEND
