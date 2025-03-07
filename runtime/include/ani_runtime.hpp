#include "taihe/string.abi.h"
#include <ani.h>

#include <type_traits>

#include <taihe/common.hpp>
#include <core/string.hpp>

namespace taihe::core {
template<typename T, typename = void>
struct ani_convert;

////////////
// scalar //
////////////

template<typename T>
struct ani_convert<T, std::enable_if_t<std::is_arithmetic_v<T>>> {
    static T into_ani(ani_env env, T v) {
        return v;
    }

    static T from_ani(ani_env env, T v) {
        return v;
    }
};

////////////
// string //
////////////

template<>
struct ani_convert<taihe::core::string> {
    static ani_string into_ani(ani_env env, taihe::core::string&& name) {
        ani_string result;
        env->String_NewUTF8(name.c_str(), name.size(), &result);
        return result;
    }

    static taihe::core::string from_ani(ani_env env, ani_string value) {
        ani_size size;
        env->String_GetUTF8Size(value, &ani_size);
        TString tstr;
        char* buf = tstr_initialize(&tstr, size + 1);
        env->String_GetUTF8(value, buf, size + 1, &size);
        buf[size] = '\0';
        return taihe::core::string(tstr);
    }
};

template<>
struct ani_convert<taihe::core::string_view> {
    static ani_string into_ani(ani_env env, taihe::core::string_view name) {
        ani_string result;
        env->String_NewUTF8(name.c_str(), name.size(), &result);
        return result;
    }

    static taihe::core::string from_ani(ani_env env, ani_string value) {
        ani_size size;
        env->String_GetUTF8Size(value, &ani_size);
        TString tstr;
        char* buf = tstr_initialize(&tstr, size + 1);
        env->String_GetUTF8(value, buf, size + 1, &size);
        buf[size] = '\0';
        return taihe::core::string(tstr);
    }
};
}
