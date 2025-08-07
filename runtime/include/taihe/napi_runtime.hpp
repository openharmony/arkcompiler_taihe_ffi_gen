#pragma once

#if __has_include(<node/node_api.h>)
#include <node/node_api.h>
#elif __has_include(<napi/native_api.h>)
#include <napi/native_api.h>
#else
#error "Please ensure the napi is correctly installed."
#endif

#include <taihe/string.hpp>

namespace taihe {
void set_env(napi_env env);
napi_env get_env();

void set_error(::taihe::string_view msg, ::taihe::string_view errcode = "");
void set_type_error(::taihe::string_view msg,
                    ::taihe::string_view errcode = "");
void set_range_error(::taihe::string_view msg,
                     ::taihe::string_view errcode = "");
bool has_error();

class EnvGuard {
public:
  explicit EnvGuard(napi_env env = nullptr);
  ~EnvGuard();

  EnvGuard(EnvGuard const &) = delete;
  EnvGuard &operator=(EnvGuard const &) = delete;

  napi_env env() const {
    return env_;
  }

private:
  napi_env env_;
};

}  // namespace taihe