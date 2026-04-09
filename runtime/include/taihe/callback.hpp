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

#ifndef TAIHE_CALLBACK_HPP
#define TAIHE_CALLBACK_HPP

#include <taihe/callback.abi.h>
#include <taihe/common.hpp>
#include <taihe/invoke.hpp>
#include <taihe/object.hpp>

#include <utility>

namespace taihe {
template<typename Signature>
struct callback_view;

template<typename Signature>
struct callback;

template<typename Return, typename... Params>
struct callback_view<taihe::expected<Return, taihe::error>(Params...)> {
private:
    template<typename T = Return>
    union cb_out_impl {
        as_abi_t<T> data;
        struct TError error;
    };

    template<>
    union cb_out_impl<void> {
        struct TError error;
    };

    using cb_out = cb_out_impl<Return>;

public:
    static constexpr bool is_holder = false;

    using vtable_type = int32_t(cb_out *_taihe_out, TCallback, as_abi_t<Params>...);
    using view_type = callback_view<taihe::expected<Return, taihe::error>(Params...)>;
    using holder_type = callback<taihe::expected<Return, taihe::error>(Params...)>;

    struct abi_type {
        vtable_type *vtbl_ptr;
        DataBlockHead *data_ptr;
    } m_handle;

    explicit callback_view(abi_type handle) : m_handle(handle)
    {
    }

    operator data_view() const &
    {
        return data_view(this->m_handle.data_ptr);
    }

    operator data_holder() const &
    {
        return data_holder(tobj_dup(this->m_handle.data_ptr));
    }

public:
    bool is_error() const &
    {
        return m_handle.vtbl_ptr == nullptr;
    }

    taihe::expected<Return, taihe::error> operator()(Params... params) const &
    {
        return taihe::checked::call_abi_func<cb_out, Return, callback_view, Params...>(
            m_handle.vtbl_ptr, *this, ::std::forward<Params>(params)...);
    }

public:
    template<typename Impl>
    static int32_t vtbl_impl(cb_out *_taihe_out, TCallback tobj, as_abi_t<Params>... params)
    {
        return taihe::checked::call_cpp_method<cb_out, Return, Params...>(
            _taihe_out, &Impl::operator(), *cast_data_ptr<Impl>(tobj.data_ptr), params...);
    };

    template<typename Impl>
    static constexpr struct IdMapItem idmap_impl[0] = {};
};

template<typename Return, typename... Params>
struct callback<taihe::expected<Return, taihe::error>(Params...)>
    : callback_view<taihe::expected<Return, taihe::error>(Params...)> {
    static constexpr bool is_holder = true;

    using typename callback_view<taihe::expected<Return, taihe::error>(Params...)>::abi_type;

    explicit callback(abi_type handle) : callback_view<taihe::expected<Return, taihe::error>(Params...)>(handle)
    {
    }

    ~callback()
    {
        tobj_drop(this->m_handle.data_ptr);
    }

    callback &operator=(callback other)
    {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    callback(callback<taihe::expected<Return, taihe::error>(Params...)> &&other)
        : callback({
              other.m_handle.vtbl_ptr,
              std::exchange(other.m_handle.data_ptr, nullptr),
          })
    {
    }

    callback(callback<taihe::expected<Return, taihe::error>(Params...)> const &other)
        : callback({
              other.m_handle.vtbl_ptr,
              tobj_dup(other.m_handle.data_ptr),
          })
    {
    }

    callback(callback_view<taihe::expected<Return, taihe::error>(Params...)> const &other)
        : callback({
              other.m_handle.vtbl_ptr,
              tobj_dup(other.m_handle.data_ptr),
          })
    {
    }

    operator data_view() const &
    {
        return data_view(this->m_handle.data_ptr);
    }

    operator data_holder() const &
    {
        return data_holder(tobj_dup(this->m_handle.data_ptr));
    }

    operator data_holder() &&
    {
        return data_holder(std::exchange(this->m_handle.data_ptr, nullptr));
    }
};

template<typename Return, typename... Params>
struct callback_view<Return(Params...)> {
    static constexpr bool is_holder = false;

    using vtable_type = as_abi_t<Return>(TCallback, as_abi_t<Params>...);
    using view_type = callback_view<Return(Params...)>;
    using holder_type = callback<Return(Params...)>;

    struct abi_type {
        vtable_type *vtbl_ptr;
        DataBlockHead *data_ptr;
    } m_handle;

    explicit callback_view(abi_type handle) : m_handle(handle)
    {
    }

    operator data_view() const &
    {
        return data_view(this->m_handle.data_ptr);
    }

    operator data_holder() const &
    {
        return data_holder(tobj_dup(this->m_handle.data_ptr));
    }

public:
    bool is_error() const &
    {
        return m_handle.vtbl_ptr == nullptr;
    }

    Return operator()(Params... params) const &
    {
        return call_abi_func<Return, callback_view, Params...>(m_handle.vtbl_ptr, *this,
                                                               ::std::forward<Params>(params)...);
    }

public:
    template<typename Impl>
    static as_abi_t<Return> vtbl_impl(TCallback tobj, as_abi_t<Params>... params)
    {
        return call_cpp_method<Return, Params...>(&Impl::operator(), *cast_data_ptr<Impl>(tobj.data_ptr), params...);
    };

    template<typename Impl>
    static constexpr struct IdMapItem idmap_impl[0] = {};
};

template<typename Return, typename... Params>
struct callback<Return(Params...)> : callback_view<Return(Params...)> {
    static constexpr bool is_holder = true;

    using typename callback_view<Return(Params...)>::abi_type;

    explicit callback(abi_type handle) : callback_view<Return(Params...)>(handle)
    {
    }

    ~callback()
    {
        tobj_drop(this->m_handle.data_ptr);
    }

    callback &operator=(callback other)
    {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    callback(callback<Return(Params...)> &&other)
        : callback({
              other.m_handle.vtbl_ptr,
              std::exchange(other.m_handle.data_ptr, nullptr),
          })
    {
    }

    callback(callback<Return(Params...)> const &other)
        : callback({
              other.m_handle.vtbl_ptr,
              tobj_dup(other.m_handle.data_ptr),
          })
    {
    }

    callback(callback_view<Return(Params...)> const &other)
        : callback({
              other.m_handle.vtbl_ptr,
              tobj_dup(other.m_handle.data_ptr),
          })
    {
    }

    operator data_view() const &
    {
        return data_view(this->m_handle.data_ptr);
    }

    operator data_holder() const &
    {
        return data_holder(tobj_dup(this->m_handle.data_ptr));
    }

    operator data_holder() &&
    {
        return data_holder(std::exchange(this->m_handle.data_ptr, nullptr));
    }
};

template<typename Return, typename... Params>
struct as_abi<taihe::callback_view<Return(Params...)>> {
    using type = TCallback;
};

template<typename Return, typename... Params>
struct as_abi<taihe::callback<Return(Params...)>> {
    using type = TCallback;
};

template<typename Return, typename... Params>
struct as_param<taihe::callback<Return(Params...)>> {
    using type = taihe::callback_view<Return(Params...)>;
};

template<typename Return, typename... Params>
inline bool operator==(taihe::callback_view<Return(Params...)> lhs, taihe::callback_view<Return(Params...)> rhs)
{
    return data_view(lhs) == data_view(rhs);
}

template<typename Return, typename... Params>
struct as_abi<taihe::callback_view<taihe::expected<Return, taihe::error>(Params...)>> {
    using type = TCallback;
};

template<typename Return, typename... Params>
struct as_abi<taihe::callback<taihe::expected<Return, taihe::error>(Params...)>> {
    using type = TCallback;
};

template<typename Return, typename... Params>
struct as_param<taihe::callback<taihe::expected<Return, taihe::error>(Params...)>> {
    using type = taihe::callback_view<taihe::expected<Return, taihe::error>(Params...)>;
};

template<typename Return, typename... Params>
inline bool operator==(taihe::callback_view<taihe::expected<Return, taihe::error>(Params...)> lhs,
                       taihe::callback_view<taihe::expected<Return, taihe::error>(Params...)> rhs)
{
    return data_view(lhs) == data_view(rhs);
}
}  // namespace taihe

template<typename Return, typename... Params>
struct std::hash<taihe::callback<Return(Params...)>> {
    std::size_t operator()(taihe::callback_view<Return(Params...)> val) const noexcept
    {
        return std::hash<taihe::data_holder>()(val);
    }
};

template<typename Return, typename... Params>
struct std::hash<taihe::callback<taihe::expected<Return, taihe::error>(Params...)>> {
    std::size_t operator()(
        taihe::callback_view<taihe::expected<Return, taihe::error>(Params...)> val) const noexcept
    {
        return std::hash<taihe::data_holder>()(val);
    }
};
#endif  // TAIHE_CALLBACK_HPP
