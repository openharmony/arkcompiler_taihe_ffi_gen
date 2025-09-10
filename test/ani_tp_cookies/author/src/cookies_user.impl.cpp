#include "cookies_user.impl.hpp"
#include <iostream>
#include "cookies_user.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
class CallbackAImpl {
public:
  CallbackAImpl() {}

  void operator()(bool arg) {
    std::cout << "CallbackA" << std::endl;
  }
};

void RunNativeBusiness(::cookies::weak::AntUserCookiesProvider cookieprovider) {
  ::cookies::AntUserCookie cookie1{"example1.com", "2099-01-01T23:59:59Z", "/",
                                   true, "sessionid=abc123"};
  ::cookies::AntUserCookie cookie2{"example2.com", "2099-01-01T23:59:59Z", "/",
                                   true, "sessionid=cba321"};
  ::taihe::array cookies{cookie1, cookie2};
  ::taihe::callback<void(bool)> cb =
      ::taihe::make_holder<CallbackAImpl, ::taihe::callback<void(bool)>>();
  cookieprovider->setCookiesAsync(cookies, cb);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_RunNativeBusiness(RunNativeBusiness);
// NOLINTEND
