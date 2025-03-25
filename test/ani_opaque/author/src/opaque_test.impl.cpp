#include "opaque_test.impl.hpp"

#include <cstdint>
#include <iostream>

#include "core/array.hpp"
#include "core/runtime.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {

bool is_string(uintptr_t a) {
  ani_boolean res;
  ani_class cls;
  ani_env* env = get_env();
  env->FindClass("Lstd/core/String;", &cls);
  env->Object_InstanceOf((ani_object)a, cls, &res);
  return res;
}
array<uintptr_t> get_objects() {
  ani_env* env = get_env();
  ani_string ani_arr_0;
  env->String_NewUTF8("AAA", 3, &ani_arr_0);
  ani_ref ani_arr_1;
  env->GetUndefined(&ani_arr_1);
  return array<uintptr_t>({(uintptr_t)ani_arr_0, (uintptr_t)ani_arr_1});
}

}  // namespace

TH_EXPORT_CPP_API_is_string(is_string);
TH_EXPORT_CPP_API_get_objects(get_objects);
