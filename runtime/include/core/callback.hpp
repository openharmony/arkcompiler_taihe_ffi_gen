#pragma once

#include <taihe/common.hpp>

#include <taihe/callback.abi.h>

namespace taihe::core {
template<typename Return, typename ...CBArgs>
struct callback_view;

template<typename Return, typename ...CBArgs>
struct callback;

template<typename Return, typename ...CBArgs>
struct callback_view {
    TCallbackData* m_data;
    Return (*m_func)(TCallbackData* data, CBArgs... args);

    callback_view(TCallbackData* data, Return (*func)(TCallbackData* data, CBArgs... args))
        : m_data(data), m_func(func) {}

    Return operator()(CBArgs... args) {
        return m_func(m_data, args...);
    }
};

template<typename Return, typename ...CBArgs>
struct callback : callback_view<Return, CBArgs...> {
    callback(TCallbackData* data, Return (*func)(TCallbackData* data, CBArgs... args))
        : callback_view<Return, CBArgs...>(data, func) {}

    callback(callback<Return, CBArgs...> && other)
        : callback{other.m_data, other.m_func} {
        other.m_data = nullptr;
    }

    callback(callback<Return, CBArgs...> const& other)
        : callback{tcb_dup(other.m_data), other.m_func} {}

    callback(callback_view<Return, CBArgs...> const& other)
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

template<typename Impl>
struct callback_data_impl : TCallbackData, Impl {
    template<typename... Args>
    callback_data_impl(void (*free)(struct TCallbackData *), Args&&... args)
        : Impl(std::forward<Args>(args)...) {
        tcb_init(this, free);
    }
};

template<typename Impl, typename Return, typename... CBArgs>
Return callback_method_impl(TCallbackData* data, CBArgs... args) {
    return (*static_cast<callback_data_impl<Impl>*>(data))(args...);
}

template<typename Impl>
void callback_free_impl(TCallbackData* data) {
    delete static_cast<callback_data_impl<Impl>*>(data);
}

template<typename Impl, typename Return, typename... CBArgs, typename ...Args>
inline auto make_callback(Args&&... args) {
    return callback<Return, CBArgs...>{
        new callback_data_impl<Impl>(&callback_free_impl<Impl>, std::forward<Args>(args)...),
        &callback_method_impl<Impl, Return, CBArgs...>,
    };
}

template<typename Return, typename... CBArgs, typename Impl>
inline auto into_callback(Impl&& impl) {
    return callback<Return, CBArgs...>{
        new callback_data_impl<Impl>(&callback_free_impl<Impl>, std::forward<Impl>(impl)),
        &callback_method_impl<Impl, Return, CBArgs...>,
    };
}

template<typename Return, typename ...CBArgs>
struct cpp_type_traits<callback_view<Return, CBArgs...>> {
    using abi_t = TCallback;
};

template<typename Return, typename ...CBArgs>
struct cpp_type_traits<callback<Return, CBArgs...>> {
    using abi_t = TCallback;
};
}
