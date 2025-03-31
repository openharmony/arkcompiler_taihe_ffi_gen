#pragma once

#include <taihe/string.hpp>

#include <ani.h>

namespace taihe {
void set_env(ani_env *env);
ani_env *get_env();
void set_error(taihe::string_view msg);
}  // namespace taihe
