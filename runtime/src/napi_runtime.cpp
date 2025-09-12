#include <taihe/napi_runtime.hpp>

namespace taihe {

namespace {
napi_env global_env = nullptr;
thread_local napi_env thread_env = nullptr;
}  // namespace

void set_env(napi_env env) {
  global_env = env;
}

napi_env get_env() {
  return thread_env ? thread_env : global_env;
}

EnvGuard::EnvGuard(napi_env env) : env_(env) {
  if (!env_) {
    env_ = global_env;
  }
  thread_env = env_;
}

EnvGuard::~EnvGuard() {
  thread_env = nullptr;
}

void set_error(taihe::string_view msg, ::taihe::string_view errcode) {
  EnvGuard guard;
  napi_env env = guard.env();

  char const *code = !errcode.empty() ? errcode.c_str() : nullptr;
  napi_throw_error(env, code, msg.c_str());
}

void set_type_error(taihe::string_view msg, ::taihe::string_view errcode) {
  EnvGuard guard;
  napi_env env = guard.env();

  char const *code = !errcode.empty() ? errcode.c_str() : nullptr;
  napi_throw_type_error(env, code, msg.c_str());
}

void set_range_error(taihe::string_view msg, ::taihe::string_view errcode) {
  EnvGuard guard;
  napi_env env = guard.env();

  char const *code = !errcode.empty() ? errcode.c_str() : nullptr;
  napi_throw_range_error(env, code, msg.c_str());
}

bool has_error() {
  EnvGuard guard;
  napi_env env = guard.env();
  napi_value exception;
  napi_get_and_clear_last_exception(env, &exception);
  if (exception == nullptr) return false;

  bool is_error = false;
  napi_is_error(env, exception, &is_error);
  return is_error;
}
}  // namespace taihe