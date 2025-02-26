#pragma once

#include <type_traits>

#include <taihe/common.hpp>

namespace taihe::core {
template<typename Signature>
struct callback_view;

template<typename Signature>
struct callback;

template<typename Return, typename... Params>
struct callback_view<Return(Params...)> {
    struct callback_data_t {
        TRefCount m_count;
        void (*m_free)(struct callback_data_t*);
        as_abi_t<Return> (*m_func)(callback_data_t* data_ptr, as_abi_t<Params>... params);
    };

    template<typename Impl>
    struct callback_data_impl : callback_data_t, Impl {
        template<typename... Args>
        callback_data_impl(Args&&... args)
            : Impl(std::forward<Args>(args)...) {
            this->m_free = [](callback_data_t* data_ptr) {
                delete static_cast<callback_data_impl<Impl>*>(data_ptr);
            };
            this->m_func = [](callback_data_t* data_ptr, as_abi_t<Params>... params) -> as_abi_t<Return> {
                return into_abi<Return>((*static_cast<callback_data_impl<Impl>*>(data_ptr))(from_abi<Params>(params)...));
            };
            tref_set(&this->m_count, 1);
        }
    };

    callback_data_t* data_ptr;

    explicit callback_view(callback_data_t* data_ptr) : data_ptr(data_ptr) {}

    template<typename Impl, typename ...Args>
    static callback<Return(Params...)> from(Args&&... args) {
        return callback<Return(Params...)>{
            new callback_data_impl<Impl>(std::forward<Args>(args)...),
        };
    }

    template<typename Impl>
    static callback<Return(Params...)> from(Impl&& impl) {
        return callback<Return(Params...)>{
            new callback_data_impl<Impl>(std::forward<Impl>(impl)),
        };
    }

    Return operator()(Params... params) const {
        return from_abi<Return>(data_ptr->m_func(data_ptr, into_abi<Params>(params)...));
    }

    friend bool same_impl(adl_helper_t, callback_view lhs, callback_view rhs) {
        return lhs.data_ptr == lhs.data_ptr;
    }

    friend std::size_t hash_impl(adl_helper_t, callback_view val) {
        return (std::size_t)val.data_ptr;
    }
};

template<typename Return, typename... Params>
struct callback<Return(Params...)> : callback_view<Return(Params...)> {
    using typename callback_view<Return(Params...)>::callback_data_t;
    using callback_view<Return(Params...)>::data_ptr;

    explicit callback(callback_data_t* data_ptr) : callback_view<Return(Params...)>(data_ptr) {}

    callback(callback<Return(Params...)> && other) : callback{other.data_ptr} {
        other.data_ptr = nullptr;
    }

    callback(callback<Return(Params...)> const& other) : callback{other.data_ptr} {
        if (data_ptr) {
            tref_inc(&data_ptr->m_count);
        }
    }

    callback(callback_view<Return(Params...)> const& other) : callback{other.data_ptr} {
        if (data_ptr) {
            tref_inc(&data_ptr->m_count);
        }
    }

    ~callback() {
        if (data_ptr && tref_dec(&data_ptr->m_count)) {
            data_ptr->m_free(data_ptr);
        }
    }

    callback& operator=(callback other) {
        std::swap(data_ptr, other.data_ptr);
        return *this;
    }
};

template<typename Return, typename... Params>
struct as_abi<callback_view<Return(Params...)>> {
    using type = void*;
};

template<typename Return, typename... Params>
struct as_abi<callback<Return(Params...)>> {
    using type = void*;
};

template<typename Return, typename... Params>
struct as_param<callback<Return(Params...)>> {
    using type = callback_view<Return(Params...)>;
};
}
