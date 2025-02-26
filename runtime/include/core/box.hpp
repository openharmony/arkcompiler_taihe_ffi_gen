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

    friend std::size_t hash_impl(adl_helper_t, box_view val) {
        return val ? hash(*val) + 0x9e3779b9 : 0;
    }

    friend bool same_impl(adl_helper_t, box_view lhs, box_view rhs) {
        return !lhs && !rhs || same(*lhs, *rhs);
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
struct cpp_type_traits<box_view<cpp_owner_t>> {
    using abi_t = struct TBox;
};

template<typename cpp_owner_t>
struct cpp_type_traits<box<cpp_owner_t>> {
    using abi_t = struct TBox;
};
}
