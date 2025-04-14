#include "external_obj.impl.hpp"

#include "ani.h"
#include "stdexcept"
#include "taihe/array.hpp"
#include "taihe/runtime.hpp"

#include <iostream>
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
bool is_string(uintptr_t s) {
  ani_env* env = get_env();
  ani_boolean res;
  ani_class cls;
  env->FindClass("Lstd/core/String;", &cls);
  env->Object_InstanceOf((ani_object)s, cls, &res);
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

void processPerson(uintptr_t person) {
  ani_env* env = get_env();
  ani_object ani_obj = reinterpret_cast<ani_object>(person);
  ani_string name;
  ani_int age;
  env->Object_GetPropertyByName_Ref(ani_obj, "name",
                                    reinterpret_cast<ani_ref*>(&name));
  env->Object_GetPropertyByName_Int(ani_obj, "age", &age);
  ani_size len;
  env->String_GetUTF8Size(name, &len);
  char* name_utf8 = new char[len + 1];
  env->String_GetUTF8(name, name_utf8, len + 1, &len);
  std::cout << "name: " << name_utf8 << ", age: " << age << std::endl;
  delete[] name_utf8;
}
}  // namespace

TH_EXPORT_CPP_API_is_string(is_string);
TH_EXPORT_CPP_API_get_objects(get_objects);
TH_EXPORT_CPP_API_processPerson(processPerson);
