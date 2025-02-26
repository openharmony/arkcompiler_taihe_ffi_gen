#pragma once

#include <memory>
#include <utility>
#include <stdexcept>
#include <cstdlib>
#include <cstddef>

#include <taihe/common.hpp>
#include <taihe/box.abi.h>

namespace taihe::core {
template<typename cpp_owner_t>
struct box_view;

template<typename cpp_owner_t>
struct box;

template<typename cpp_owner_t>
struct box_view {
    box_view(cpp_owner_t const* handle) noexcept : m_handle(handle) {} // main constructor
    
    cpp_owner_t const* operator->() const {
        return m_handle;
    }

    cpp_owner_t const& operator*() const {
        return *m_handle;
    }

    operator bool() const {
        return m_handle;
    }

protected:
    cpp_owner_t const* m_handle;
};

template<typename cpp_owner_t>
struct box : public box_view<cpp_owner_t> {
    box(cpp_owner_t const* handle) noexcept : box_view<cpp_owner_t>(handle) {} // main constructor

    template<typename... Args>
    static box make(Args&&... args) {
        return box(new cpp_owner_t(std::forward<Args>(args)...));
    }

    box(box_view<cpp_owner_t> const& other)
        : box(new cpp_owner_t(*other)) {}

    box(box<cpp_owner_t> const& other)
        : box(new cpp_owner_t(*other)) {}

    box(box<cpp_owner_t>&& other)
        : box(std::exchange(other.m_handle, nullptr)) {}

    box &operator=(box other) {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    ~box() {
        if (this->m_handle) {
            delete this->m_handle;
        }
    }
};

template<typename cpp_owner_t>
inline std::size_t hash_impl(adl_helper_t, box_view<cpp_owner_t> val) {
    return val ? hash(*val) + 0x9e3779b9 : 0;
}

template<typename cpp_owner_t>
inline bool same_impl(adl_helper_t, box_view<cpp_owner_t> lhs, box_view<cpp_owner_t> rhs) {
    return !lhs && !rhs || same(*lhs, *rhs);
}

template<typename cpp_owner_t>
struct as_abi<box_view<cpp_owner_t>> {
    using type = struct TBox;
};

template<typename cpp_owner_t>
struct as_abi<box<cpp_owner_t>> {
    using type = struct TBox;
};

template<typename cpp_owner_t>
struct as_param<box<cpp_owner_t>> {
    using type = box_view<cpp_owner_t>;
};
}
