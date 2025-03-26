#pragma once

#include <ani.h>

#include <core/string.hpp>

namespace taihe::core {
void set_env(ani_env *env);
ani_env *get_env();
void set_error(taihe::core::string_view msg);
}  // namespace taihe::core
