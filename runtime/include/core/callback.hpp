#pragma once

#include <type_traits>

#include <taihe/common.hpp>
#include <taihe/callback.abi.h>

namespace taihe::core {
template<typename Impl>
struct callback_data_impl : TCallbackData, Impl {
    template<typename... Args>
    callback_data_impl(Args&&... args)
        : Impl(std::forward<Args>(args)...) {
        tcb_init(this, &free_impl);
    }

    static void free_impl(TCallbackData* data) {
        delete static_cast<callback_data_impl<Impl>*>(data);
    }
};
}

namespace taihe::core {
template<typename Signature>
struct callback_view;

template<typename Signature>
struct callback;

template<typename Return, typename... Params>
struct callback_view<Return(Params...)> {
    typedef as_abi_t<Return> (*func_t)(TCallbackData* data, as_abi_t<Params>... params);

    TCallbackData* m_data;
    func_t m_func;

    explicit callback_view(TCallbackData* data, func_t func) : m_data(data), m_func(func) {}

    template<typename Impl, typename ...Args>
    static callback<Return(Params...)> from(Args&&... args) {
        return callback<Return(Params...)>{
            new callback_data_impl<Impl>(std::forward<Args>(args)...),
            &func_impl<Impl>,
        };
    }

    template<typename Impl>
    static callback<Return(Params...)> from(Impl&& impl) {
        return callback<Return(Params...)>{
            new callback_data_impl<Impl>(std::forward<Impl>(impl)),
            &func_impl<Impl>,
        };
    }

    template<typename Impl>
    static as_abi_t<Return> func_impl(TCallbackData* data, as_abi_t<Params>... params) {
        return into_abi<Return>((*static_cast<callback_data_impl<Impl>*>(data))(from_abi<Params>(params)...));
    }

    Return operator()(Params... params) const {
        return from_abi<Return>(m_func(m_data, into_abi<Params>(params)...));
    }

    friend bool same_impl(adl_helper_t, callback_view lhs, callback_view rhs) {
        return lhs.m_data == lhs.m_data;
    }

    friend std::size_t hash_impl(adl_helper_t, callback_view val) {
        return (std::size_t)val.m_data;
    }
};

template<typename Return, typename... Params>
struct callback<Return(Params...)> : callback_view<Return(Params...)> {
    using typename callback_view<Return(Params...)>::func_t;

    explicit callback(TCallbackData* data, func_t func) : callback_view<Return(Params...)>(data, func) {}

    callback(callback<Return(Params...)> && other)
        : callback{other.m_data, other.m_func} {
        other.m_data = nullptr;
    }

    callback(callback<Return(Params...)> const& other)
        : callback{tcb_dup(other.m_data), other.m_func} {}

    callback(callback_view<Return(Params...)> const& other)
        : callback{tcb_dup(other.m_data), other.m_func} {}

    ~callback() {
        tcb_drop(this->m_data);
    }

    callback& operator=(callback other) {
        std::swap(this->m_data, other.m_data);
        std::swap(this->m_func, other.m_func);
        return *this;
    }
};

template<typename Return, typename... Params>
struct cpp_type_traits<callback_view<Return(Params...)>> {
    using abi_t = TCallback;
};

template<typename Return, typename... Params>
struct cpp_type_traits<callback<Return(Params...)>> {
    using abi_t = TCallback;
};
}
