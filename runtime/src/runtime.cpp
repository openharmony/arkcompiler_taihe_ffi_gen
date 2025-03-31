#include <taihe/runtime.hpp>

namespace taihe {
__thread ani_env *cur_env;

void set_env(ani_env *env) {
  cur_env = env;
}

ani_env *get_env() {
  return cur_env;
}

void ani_set_error(ani_env *env, taihe::string_view msg) {
  ani_class errCls;
  char const *className = "Lescompat/Error;";
  if (ANI_OK != env->FindClass(className, &errCls)) {
    std::cerr << "Not found '" << className << std::endl;
    return;
  }

  ani_method errCtor;
  if (ANI_OK != env->Class_FindMethod(
                    errCls, "<ctor>",
                    "Lstd/core/String;Lescompat/ErrorOptions;:V", &errCtor)) {
    std::cerr << "get errCtor Failed'" << className << "'" << std::endl;
    return;
  }

  ani_string result_string{};
  env->String_NewUTF8(msg.c_str(), msg.size(), &result_string);

  ani_object errObj;
  if (ANI_OK != env->Object_New(errCls, errCtor, &errObj, result_string)) {
    std::cerr << "Create Object Failed'" << className << "'" << std::endl;
    return;
  }
  env->ThrowError(static_cast<ani_error>(errObj));
}

void set_error(taihe::string_view msg) {
  ani_env *env = get_env();
  ani_set_error(env, msg);
}
}  // namespace taihe
