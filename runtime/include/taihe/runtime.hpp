#pragma once

#include <taihe/string.hpp>

#include <ani.h>

namespace taihe {
void set_env(ani_env *env);
ani_env *get_env();
void set_business_error(int32_t err_code, taihe::string_view msg);
void set_error(taihe::string_view msg);
void reset_error();
bool has_error();
}  // namespace taihe
