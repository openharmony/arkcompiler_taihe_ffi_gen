#pragma once

#include <taihe/string.hpp>

#include <ani.h>

namespace taihe {
void set_vm(ani_vm *vm);
ani_vm *get_vm();
ani_env *get_env();

class env_guard {
  ani_env *env;
  bool is_attached;

public:
  env_guard();
  ~env_guard();

  env_guard(env_guard const &) = delete;
  env_guard &operator=(env_guard const &) = delete;
  env_guard(env_guard &&) = delete;
  env_guard &operator=(env_guard &&) = delete;

  ani_env *get_env() {
    return env;
  }
};

void set_error(taihe::string_view msg);
void set_business_error(int32_t err_code, taihe::string_view msg);
void reset_error();
bool has_error();
}  // namespace taihe
