#pragma once

#include <memory>
#include <utility>
#include <stdexcept>
#include <cstdlib>
#include <cstddef>

#include <taihe/common.hpp>
#include <taihe/optional.abi.h>

namespace taihe::core {
template<typename cpp_owner_t>
struct optional_view;

template<typename cpp_owner_t>
struct optional;

template<typename cpp_owner_t>
struct optional_view {
    optional_view(cpp_owner_t const* handle) noexcept : m_handle(handle) {} // main constructor
    
    cpp_owner_t const* operator->() const {
        return m_handle;
    }

    cpp_owner_t const& operator*() const {
        return *m_handle;
    }

    explicit operator bool() const {
        return m_handle;
    }

protected:
    cpp_owner_t const* m_handle;
};

template<typename cpp_owner_t>
struct optional : public optional_view<cpp_owner_t> {
    optional(cpp_owner_t const* handle) noexcept : optional_view<cpp_owner_t>(handle) {} // main constructor

    optional() noexcept : optional_view<cpp_owner_t>(nullptr) {}

    template<typename... Args>
    static optional make(Args&&... args) {
        return optional(new cpp_owner_t(std::forward<Args>(args)...));
    }

    optional(optional_view<cpp_owner_t> const& other)
        : optional(new cpp_owner_t(*other)) {}

    optional(optional<cpp_owner_t> const& other)
        : optional(new cpp_owner_t(*other)) {}

    optional(optional<cpp_owner_t>&& other)
        : optional(std::exchange(other.m_handle, nullptr)) {}

    optional &operator=(optional other) {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    ~optional() {
        if (this->m_handle) {
            delete this->m_handle;
        }
    }
};

template<typename cpp_owner_t>
inline std::size_t hash_impl(adl_helper_t, optional_view<cpp_owner_t> val) {
    return val ? hash(*val) + 0x9e3779b9 : 0;
}

template<typename cpp_owner_t>
inline bool same_impl(adl_helper_t, optional_view<cpp_owner_t> lhs, optional_view<cpp_owner_t> rhs) {
    return !lhs && !rhs || same(*lhs, *rhs);
}

template<typename cpp_owner_t>
struct as_abi<optional_view<cpp_owner_t>> {
    using type = struct TOptional;
};

template<typename cpp_owner_t>
struct as_abi<optional<cpp_owner_t>> {
    using type = struct TOptional;
};

template<typename cpp_owner_t>
struct as_param<optional<cpp_owner_t>> {
    using type = optional_view<cpp_owner_t>;
};
}
