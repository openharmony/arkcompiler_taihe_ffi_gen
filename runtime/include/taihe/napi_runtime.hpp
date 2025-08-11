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

#define NAPI_CALL(env, call)                                        \
  do {                                                              \
    napi_status status = (call);                                    \
    if (status != napi_ok) {                                        \
      const napi_extended_error_info *error_info;                   \
      napi_get_last_error_info(env, &error_info);                   \
      const char *message =                                         \
          error_info ? error_info->error_message : "Unknown error"; \
      char error_buf[256];                                          \
      snprintf(error_buf, sizeof(error_buf),                        \
               "N-API call failed at %s:%d\n"                       \
               "Call: " #call                                       \
               "\n"                                                 \
               "Status: %d\n"                                       \
               "Message: %s",                                       \
               __FILE__, __LINE__, status, message);                \
      napi_throw_error(env, nullptr, error_buf);                    \
    }                                                               \
  } while (0)
