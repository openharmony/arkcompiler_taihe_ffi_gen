/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
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

#ifndef TAIHE_INVOKE_HPP
#define TAIHE_INVOKE_HPP

#include <taihe/common.hpp>
#include <taihe/expected.hpp>

namespace taihe {
namespace checked {
template<typename OutT, typename cpp_return_t, typename... cpp_param_t, typename abi_func_t,
         std::enable_if_t<std::is_same_v<void, cpp_return_t>, int> = 0>
inline ::taihe::expected<cpp_return_t, ::taihe::error> call_abi_func(abi_func_t &&abi_func, cpp_param_t... params)
{
    OutT _taihe_out;
    int32_t res_flag = abi_func(&_taihe_out, into_abi<cpp_param_t>(params)...);
    if (res_flag == 0) {
        return {};
    } else {
        return ::taihe::unexpected<::taihe::error>(::taihe::from_abi<::taihe::error>(_taihe_out.error));
    }
}

template<typename OutT, typename cpp_return_t, typename... cpp_param_t, typename abi_func_t,
         std::enable_if_t<!std::is_same_v<void, cpp_return_t>, int> = 0>
inline ::taihe::expected<cpp_return_t, ::taihe::error> call_abi_func(abi_func_t &&abi_func, cpp_param_t... params)
{
    OutT _taihe_out;
    int32_t res_flag = abi_func(&_taihe_out, into_abi<cpp_param_t>(params)...);
    if (res_flag == 0) {
        return from_abi<cpp_return_t>(_taihe_out.data);
    } else {
        return ::taihe::unexpected<::taihe::error>(::taihe::from_abi<::taihe::error>(_taihe_out.error));
    }
}

template<typename OutT, typename cpp_return_t, typename... cpp_param_t, typename cpp_func_t,
         std::enable_if_t<std::is_same_v<void, cpp_return_t>, int> = 0>
inline int32_t call_cpp_func(OutT *_taihe_out, cpp_func_t &&cpp_func, as_abi_t<cpp_param_t>... params)
{
    using result_type = decltype(cpp_func(from_abi<cpp_param_t>(params)...));
    if constexpr (is_expected_v<result_type>) {
        auto result = cpp_func(from_abi<cpp_param_t>(params)...);
        if (result.has_value()) {
            return 0;
        } else {
            _taihe_out->error = ::taihe::into_abi<::taihe::error>(result.error());
            return 1;
        }
    } else {
        cpp_func(from_abi<cpp_param_t>(params)...);
        return 0;
    }
}

template<typename OutT, typename cpp_return_t, typename... cpp_param_t, typename cpp_func_t,
         std::enable_if_t<!std::is_same_v<void, cpp_return_t>, int> = 0>
inline int32_t call_cpp_func(OutT *_taihe_out, cpp_func_t &&cpp_func, as_abi_t<cpp_param_t>... params)
{
    using result_type = decltype(cpp_func(from_abi<cpp_param_t>(params)...));
    if constexpr (is_expected_v<result_type>) {
        auto result = cpp_func(from_abi<cpp_param_t>(params)...);
        if (result.has_value()) {
            _taihe_out->data = ::taihe::into_abi<cpp_return_t>(result.value());
            return 0;
        } else {
            _taihe_out->error = ::taihe::into_abi<::taihe::error>(result.error());
            return 1;
        }
    } else {
        auto result = cpp_func(from_abi<cpp_param_t>(params)...);
        _taihe_out->data = ::taihe::into_abi<cpp_return_t>(result);
        return 0;
    }
}

template<typename OutT, typename cpp_return_t, typename... cpp_param_t, typename cpp_obj_t, typename cpp_method_t,
         std::enable_if_t<std::is_same_v<void, cpp_return_t>, int> = 0>
inline int32_t call_cpp_method(OutT *_taihe_out, cpp_method_t &&cpp_method, cpp_obj_t &&cpp_obj,
                               as_abi_t<cpp_param_t>... params)
{
    using result_type = decltype((std::forward<cpp_obj_t>(cpp_obj).*cpp_method)(from_abi<cpp_param_t>(params)...));
    if constexpr (is_expected_v<result_type>) {
        auto result = (std::forward<cpp_obj_t>(cpp_obj).*cpp_method)(from_abi<cpp_param_t>(params)...);
        if (result.has_value()) {
            return 0;
        } else {
            _taihe_out->error = ::taihe::into_abi<::taihe::error>(result.error());
            return 1;
        }
    } else {
        (std::forward<cpp_obj_t>(cpp_obj).*cpp_method)(from_abi<cpp_param_t>(params)...);
        return 0;
    }
}

template<typename OutT, typename cpp_return_t, typename... cpp_param_t, typename cpp_obj_t, typename cpp_method_t,
         std::enable_if_t<!std::is_same_v<void, cpp_return_t>, int> = 0>
inline int32_t call_cpp_method(OutT *_taihe_out, cpp_method_t &&cpp_method, cpp_obj_t &&cpp_obj,
                               as_abi_t<cpp_param_t>... params)
{
    using result_type = decltype((std::forward<cpp_obj_t>(cpp_obj).*cpp_method)(from_abi<cpp_param_t>(params)...));
    if constexpr (is_expected_v<result_type>) {
        auto result = (std::forward<cpp_obj_t>(cpp_obj).*cpp_method)(from_abi<cpp_param_t>(params)...);
        if (result.has_value()) {
            _taihe_out->data = ::taihe::into_abi<cpp_return_t>(result.value());
            return 0;
        } else {
            _taihe_out->error = ::taihe::into_abi<::taihe::error>(result.error());
            return 1;
        }
    } else {
        auto result = (std::forward<cpp_obj_t>(cpp_obj).*cpp_method)(from_abi<cpp_param_t>(params)...);
        _taihe_out->data = ::taihe::into_abi<cpp_return_t>(result);
        return 0;
    }
}
}  // namespace checked

template<typename cpp_return_t, typename... cpp_param_t, typename abi_func_t,
         std::enable_if_t<std::is_same_v<void, cpp_return_t>, int> = 0>
inline cpp_return_t call_abi_func(abi_func_t &&abi_func, cpp_param_t... params)
{
    return abi_func(into_abi<cpp_param_t>(params)...);
}

template<typename cpp_return_t, typename... cpp_param_t, typename abi_func_t,
         std::enable_if_t<!std::is_same_v<void, cpp_return_t>, int> = 0>
inline cpp_return_t call_abi_func(abi_func_t &&abi_func, cpp_param_t... params)
{
    return from_abi<cpp_return_t>(abi_func(into_abi<cpp_param_t>(params)...));
}

template<typename cpp_return_t, typename... cpp_param_t, typename cpp_func_t,
         std::enable_if_t<std::is_same_v<void, cpp_return_t>, int> = 0>
inline as_abi_t<cpp_return_t> call_cpp_func(cpp_func_t &&cpp_func, as_abi_t<cpp_param_t>... params)
{
    return cpp_func(from_abi<cpp_param_t>(params)...);
}

template<typename cpp_return_t, typename... cpp_param_t, typename cpp_func_t,
         std::enable_if_t<!std::is_same_v<void, cpp_return_t>, int> = 0>
inline as_abi_t<cpp_return_t> call_cpp_func(cpp_func_t &&cpp_func, as_abi_t<cpp_param_t>... params)
{
    return into_abi<cpp_return_t>(cpp_func(from_abi<cpp_param_t>(params)...));
}

template<typename cpp_return_t, typename... cpp_param_t, typename cpp_obj_t, typename cpp_method_t,
         std::enable_if_t<std::is_same_v<void, cpp_return_t>, int> = 0>
inline as_abi_t<cpp_return_t> call_cpp_method(cpp_method_t &&cpp_method, cpp_obj_t &&cpp_obj,
                                              as_abi_t<cpp_param_t>... params)
{
    (std::forward<cpp_obj_t>(cpp_obj).*cpp_method)(from_abi<cpp_param_t>(params)...);
}

template<typename cpp_return_t, typename... cpp_param_t, typename cpp_obj_t, typename cpp_method_t,
         std::enable_if_t<!std::is_same_v<void, cpp_return_t>, int> = 0>
inline as_abi_t<cpp_return_t> call_cpp_method(cpp_method_t &&cpp_method, cpp_obj_t &&cpp_obj,
                                              as_abi_t<cpp_param_t>... params)
{
    return into_abi<cpp_return_t>((std::forward<cpp_obj_t>(cpp_obj).*cpp_method)(from_abi<cpp_param_t>(params)...));
}
}  // namespace taihe

#endif  // TAIHE_INVOKE_HPP
