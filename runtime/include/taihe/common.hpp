/*
 * Copyright (c) 2025-2026 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef TAIHE_COMMON_HPP
#define TAIHE_COMMON_HPP

#include <taihe/common.h>

#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>

#ifdef __EXCEPTIONS
#define TH_THROW(error_type, message) throw error_type(message)
#else
#define TH_THROW(error_type, message)                                    \
    do {                                                                 \
        fprintf(stderr,                                                  \
                "%s: %s, \nfunction: %s, "                               \
                "file: %s, line %d.\n",                                  \
                #error_type, message, __FUNCTION__, __FILE__, __LINE__); \
        abort();                                                         \
    } while (0)
#endif

namespace taihe {
template<typename cpp_t, typename = void>
struct as_abi;

template<typename cpp_t>
using as_abi_t = typename as_abi<cpp_t>::type;

template<typename cpp_owner_t, typename = void>
struct as_param;

template<typename cpp_owner_t>
using as_param_t = typename as_param<cpp_owner_t>::type;

template<typename cpp_t>
struct as_abi<cpp_t, std::enable_if_t<std::is_arithmetic_v<cpp_t>>> {
    using type = cpp_t;
};

template<typename cpp_owner_t>
struct as_param<cpp_owner_t, std::enable_if_t<std::is_arithmetic_v<cpp_owner_t>>> {
    using type = cpp_owner_t;
};

///////////////
// enum tags //
///////////////

template<auto tag>
struct static_tag_t {};

template<auto tag>
constexpr static_tag_t<tag> static_tag;
}  // namespace taihe

//////////////////////////////
// Compile-Time String Type //
//////////////////////////////

namespace taihe {
struct ct_null_string_t {
    static constexpr char const *c_str()
    {
        return nullptr;
    }
};

template<char... Chars>
struct ct_string_t {
    static constexpr char value[] = {Chars..., '\0'};

    static constexpr char const *c_str()
    {
        return value;
    }
};
}  // namespace taihe

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wgnu-string-literal-operator-template"

template<typename CharT, CharT... Chars>
constexpr taihe::ct_string_t<Chars...> operator""_taihe_ct_string()
{
    return {};
}

#pragma GCC diagnostic pop

constexpr taihe::ct_null_string_t nullptr_taihe_ct_string;

#define TH_AS_CT_STRING_T(c_str) decltype(c_str##_taihe_ct_string)
#define TH_AS_C_STR(ct_string_t) ct_string_t::c_str()

#endif  // TAIHE_COMMON_HPP
