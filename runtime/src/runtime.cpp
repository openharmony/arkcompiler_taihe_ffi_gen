#include <core/runtime.hpp>

namespace taihe::core {
__thread ani_env *cur_env;

void set_env(ani_env *env) {
    cur_env = env;
}

ani_env *get_env() {
    return cur_env;
}

void ani_throw_error(ani_env *env, taihe::core::string msg) {
    ani_boolean result_obj = ANI_FALSE;
    ani_class errCls;
    const char* className = "Lescompat/Error;";
    if (ANI_OK != env->FindClass(className, &errCls)) {
        std::cerr << "Not found '"  << className << std::endl;
        return;
    }

    ani_method errCtor;
    if (ANI_OK != env->Class_FindMethod(errCls, "<ctor>", "Lstd/core/String;Lescompat/ErrorOptions;:V", &errCtor)) {
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

void throw_error(taihe::core::string msg){
    ani_env *env = get_env();
    ani_throw_error(env, msg);
}
}
