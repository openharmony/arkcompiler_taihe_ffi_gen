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

#ifndef TAIHE_INVOKE_HPP
#define TAIHE_INVOKE_HPP

#include <taihe/common.hpp>
#include <taihe/expected.hpp>
#include <taihe/object.hpp>

namespace taihe {
template<typename cpp_t, std::enable_if_t<!std::is_reference_v<cpp_t>, int> = 0>
inline as_abi_t<cpp_t> into_abi(cpp_t &&cpp_val)
{
    as_abi_t<cpp_t> abi_val;
    new (&abi_val) cpp_t(std::move(cpp_val));
    return abi_val;
}

template<typename cpp_t, std::enable_if_t<!std::is_reference_v<cpp_t>, int> = 0>
inline as_abi_t<cpp_t> into_abi(cpp_t &cpp_val)
{
    as_abi_t<cpp_t> abi_val;
    new (&abi_val) cpp_t(std::move(cpp_val));
    return abi_val;
}

template<typename cpp_t, std::enable_if_t<!std::is_reference_v<cpp_t>, int> = 0>
inline cpp_t &&from_abi(as_abi_t<cpp_t> &abi_val)
{
    return reinterpret_cast<cpp_t &&>(abi_val);
}

template<typename cpp_t, std::enable_if_t<!std::is_reference_v<cpp_t>, int> = 0>
inline cpp_t &&from_abi(as_abi_t<cpp_t> &&abi_val)
{
    return reinterpret_cast<cpp_t &&>(abi_val);
}

template<typename cpp_t, std::enable_if_t<std::is_reference_v<cpp_t>, int> = 0>
inline as_abi_t<cpp_t> into_abi(cpp_t cpp_val)
{
    return reinterpret_cast<as_abi_t<cpp_t>>(&cpp_val);
}

template<typename cpp_t, std::enable_if_t<std::is_reference_v<cpp_t>, int> = 0>
inline cpp_t from_abi(as_abi_t<cpp_t> abi_val)
{
    return reinterpret_cast<cpp_t>(*abi_val);
}
}  // namespace taihe

namespace taihe {
template<typename Return, typename... Params>
struct as_abi_func;

template<typename Return, typename... Params>
using as_abi_func_t = typename as_abi_func<Return, Params...>::type;

template<typename Return, typename... Params>
struct as_abi_func {
    using type = void (*)(as_abi_t<Params>..., as_abi_t<Return> *);
};

template<typename... Params>
struct as_abi_func<void, Params...> {
    using type = void (*)(as_abi_t<Params>...);
};

template<typename Return, typename Error, typename... Params>
struct as_abi_func<taihe::expected<Return, Error>, Params...> {
    using type = void (*)(as_abi_t<Params>..., as_abi_t<Error> **, as_abi_t<Return> *);
};

template<typename Error, typename... Params>
struct as_abi_func<taihe::expected<void, Error>, Params...> {
    using type = void (*)(as_abi_t<Params>..., as_abi_t<Error> **);
};

template<auto function, typename Return, typename... Params>
struct function_calling_convention {
    static void abi_func(as_abi_t<Params>... abi_params, as_abi_t<Return> *abi_ret)
    {
        *abi_ret = into_abi<Return>(function(from_abi<Params>(abi_params)...));
    }
};

template<auto function, typename... Params>
struct function_calling_convention<function, void, Params...> {
    static void abi_func(as_abi_t<Params>... abi_params)
    {
        function(from_abi<Params>(abi_params)...);
    }
};

template<auto function, typename Return, typename Error, typename... Params>
struct function_calling_convention<function, taihe::expected<Return, Error>, Params...> {
    static void abi_func(as_abi_t<Params>... abi_params, as_abi_t<Error> **abi_err, as_abi_t<Return> *abi_ret)
    {
        taihe::expected<Return, Error> res = function(from_abi<Params>(abi_params)...);
        if (!res.has_value()) {
            *abi_err = new as_abi_t<Error>;
            **abi_err = into_abi<Error>(res.error());
        } else {
            *abi_ret = into_abi<Return>(res.value());
        }
    }
};

template<auto function, typename Error, typename... Params>
struct function_calling_convention<function, taihe::expected<void, Error>, Params...> {
    static void abi_func(as_abi_t<Params>... abi_params, as_abi_t<Error> **abi_err)
    {
        using return_t = decltype(function(from_abi<Params>(abi_params)...));
        if constexpr (std::is_same_v<return_t, void>) {
            function(from_abi<Params>(abi_params)...);
            return;
        } else {
            taihe::expected<void, Error> res = function(from_abi<Params>(abi_params)...);
            if (!res.has_value()) {
                *abi_err = new as_abi_t<Error>;
                **abi_err = into_abi<Error>(res.error());
            }
        }
    }
};

template<typename Impl, auto method, typename Return, typename InterfaceView, typename... Params>
struct method_calling_convention {
    static void abi_func(as_abi_t<InterfaceView> abi_obj, as_abi_t<Params>... abi_params, as_abi_t<Return> *abi_ret)
    {
        *abi_ret = into_abi<Return>((cast_data_ptr<Impl>(abi_obj.data_ptr)->*method)(from_abi<Params>(abi_params)...));
    }
};

template<typename Impl, auto method, typename InterfaceView, typename... Params>
struct method_calling_convention<Impl, method, void, InterfaceView, Params...> {
    static void abi_func(as_abi_t<InterfaceView> abi_obj, as_abi_t<Params>... abi_params)
    {
        (cast_data_ptr<Impl>(abi_obj.data_ptr)->*method)(from_abi<Params>(abi_params)...);
    }
};

template<typename Impl, auto method, typename Return, typename Error, typename InterfaceView, typename... Params>
struct method_calling_convention<Impl, method, taihe::expected<Return, Error>, InterfaceView, Params...> {
    static void abi_func(as_abi_t<InterfaceView> abi_obj, as_abi_t<Params>... abi_params, as_abi_t<Error> **abi_err,
                         as_abi_t<Return> *abi_ret)
    {
        taihe::expected<Return, Error> res =
            (cast_data_ptr<Impl>(abi_obj.data_ptr)->*method)(from_abi<Params>(abi_params)...);
        if (!res.has_value()) {
            *abi_err = new as_abi_t<Error>;
            **abi_err = into_abi<Error>(res.error());
        } else {
            *abi_ret = into_abi<Return>(res.value());
        }
    }
};

template<typename Impl, auto method, typename Error, typename InterfaceView, typename... Params>
struct method_calling_convention<Impl, method, taihe::expected<void, Error>, InterfaceView, Params...> {
    static void abi_func(as_abi_t<InterfaceView> abi_obj, as_abi_t<Params>... abi_params, as_abi_t<Error> **abi_err)
    {
        using return_t = decltype((cast_data_ptr<Impl>(abi_obj.data_ptr)->*method)(from_abi<Params>(abi_params)...));
        if constexpr (std::is_same_v<return_t, void>) {
            (cast_data_ptr<Impl>(abi_obj.data_ptr)->*method)(from_abi<Params>(abi_params)...);
            return;
        } else {
            taihe::expected<void, Error> res =
                (cast_data_ptr<Impl>(abi_obj.data_ptr)->*method)(from_abi<Params>(abi_params)...);
            if (!res.has_value()) {
                *abi_err = new as_abi_t<Error>;
                **abi_err = into_abi<Error>(res.error());
            }
        }
    }
};

template<typename Return, typename... Params>
struct call_abi_func_t {
    Return operator()(as_abi_func_t<Return, Params...> abi_func, Params... params) const
    {
        as_abi_t<Return> abi_ret;
        abi_func(into_abi<Params>(params)..., &abi_ret);
        return from_abi<Return>(abi_ret);
    }
};

template<typename... Params>
struct call_abi_func_t<void, Params...> {
    void operator()(as_abi_func_t<void, Params...> abi_func, Params... params) const
    {
        abi_func(into_abi<Params>(params)...);
        return;
    }
};

template<typename Return, typename Error, typename... Params>
struct call_abi_func_t<taihe::expected<Return, Error>, Params...> {
    taihe::expected<Return, Error> operator()(as_abi_func_t<taihe::expected<Return, Error>, Params...> abi_func,
                                              Params... params) const
    {
        as_abi_t<Error> *abi_err = nullptr;
        as_abi_t<Return> abi_ret;
        abi_func(into_abi<Params>(params)..., &abi_err, &abi_ret);
        if (abi_err) {
            Error err = from_abi<Error>(*abi_err);
            delete abi_err;
            return taihe::unexpected<Error>(err);
        } else {
            return from_abi<Return>(abi_ret);
        }
    }
};

template<typename Error, typename... Params>
struct call_abi_func_t<taihe::expected<void, Error>, Params...> {
    taihe::expected<void, Error> operator()(as_abi_func_t<taihe::expected<void, Error>, Params...> abi_func,
                                            Params... params) const
    {
        as_abi_t<Error> *abi_err = nullptr;
        abi_func(into_abi<Params>(params)..., &abi_err);
        if (abi_err) {
            Error err = from_abi<Error>(*abi_err);
            delete abi_err;
            return taihe::unexpected<Error>(err);
        } else {
            return {};
        }
    }
};

template<typename Return, typename... Params>
constexpr call_abi_func_t<Return, Params...> call_abi_func;
}  // namespace taihe

#endif  // TAIHE_INVOKE_HPP
