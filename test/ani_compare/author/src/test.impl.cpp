#include <vector>

#include "taihe/array.hpp"
#include "taihe/runtime.hpp"
#include "taihe/string.hpp"

#include "taihe.platform.ani.proj.hpp"
#include "test.impl.hpp"
#include "test.proj.hpp"

namespace {
// To be implemented.

class CallbackManagerImpl {
  std::vector<::taihe::callback<taihe::string()>> callbacks_;

public:
  CallbackManagerImpl() {}

  bool addCallback(::taihe::callback_view<taihe::string()> new_cb) {
    for (auto const &old_cb : callbacks_) {
      if (old_cb == new_cb) {
        std::cerr << "Callback already exists." << std::endl;
        return false;
      }
    }
    callbacks_.emplace_back(new_cb);
    return true;
  }

  bool removeCallback(::taihe::callback_view<taihe::string()> cb) {
    for (auto it = callbacks_.begin(); it != callbacks_.end(); ++it) {
      if (*it == cb) {
        callbacks_.erase(it);
        return true;
      }
    }
    std::cerr << "Callback not found." << std::endl;
    return false;
  }

  taihe::array<taihe::string> invokeCallbacks() {
    std::vector<taihe::string> results;
    for (auto const &cb : callbacks_) {
      results.push_back(cb());
    }
    return taihe::array<taihe::string>(taihe::copy_data, results.data(),
                                       results.size());
  }
};

::test::CallbackManager getCallbackManager() {
  return taihe::make_holder<CallbackManagerImpl, ::test::CallbackManager>();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_getCallbackManager(getCallbackManager);
// NOLINTEND
