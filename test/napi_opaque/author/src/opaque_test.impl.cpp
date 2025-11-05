/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
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
// This file is a test file.
// NOLINTBEGIN

#include "opaque_test.impl.hpp"
#include <taihe/napi_runtime.hpp>

namespace {
bool is_string(uintptr_t s)
{
    napi_env env = ::taihe::get_env();
    napi_valuetype value_ty;
    napi_typeof(env, (napi_value)s, &value_ty);
    if (value_ty == napi_string) {
        return true;
    } else {
        return false;
    }
}

uintptr_t get_object()
{
    napi_env env = ::taihe::get_env();
    napi_value napi_arr_0 = nullptr;
    ::taihe::string cpp_arr_0 = "OnlyObject";
    napi_create_string_utf8(env, cpp_arr_0.c_str(), cpp_arr_0.size(), &napi_arr_0);
    return (uintptr_t)napi_arr_0;
}

::taihe::array<uintptr_t> get_objects()
{
    napi_env env = ::taihe::get_env();
    napi_value napi_arr_0 = nullptr;
    ::taihe::string cpp_arr_0 = "FirstOne";
    napi_create_string_utf8(env, cpp_arr_0.c_str(), cpp_arr_0.size(), &napi_arr_0);
    napi_value napi_arr_1 = nullptr;
    napi_get_undefined(env, &napi_arr_1);
    return ::taihe::array<uintptr_t>({(uintptr_t)napi_arr_0, (uintptr_t)napi_arr_1});
}

bool is_opaque(::opaque_test::Union const &s)
{
    if (s.get_tag() == ::opaque_test::Union::tag_t::oValue) {
        return true;
    }
    return false;
}
}  // namespace

TH_EXPORT_CPP_API_is_string(is_string);
TH_EXPORT_CPP_API_get_object(get_object);
TH_EXPORT_CPP_API_get_objects(get_objects);
TH_EXPORT_CPP_API_is_opaque(is_opaque);
// NOLINTEND
