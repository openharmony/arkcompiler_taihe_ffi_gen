#pragma once

#include <array>
#include <memory>
#include <type_traits>
#include <utility>
#include <vector>
#include <stdexcept>
#include <cstdlib>
#include <cstddef>

#include <taihe/common.hpp>
#include <taihe/array.abi.h>

namespace taihe::core {
template<typename cpp_owner_t>
struct array_view;

template<typename cpp_owner_t>
struct array;

template<typename cpp_owner_t>
struct array_view {
    using value_type = cpp_owner_t;
    using size_type = std::size_t;
    using reference = value_type&;
    using const_reference = value_type const&;
    using pointer = value_type*;
    using const_pointer = value_type const*;
    using iterator = value_type*;
    using const_iterator = value_type const*;
    using reverse_iterator = std::reverse_iterator<iterator>;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    array_view(pointer data, size_type size) noexcept : m_data(data), m_size(size) {} // main constructor

    template<typename C>
    array_view(std::initializer_list<C> value) noexcept
        : array_view(value.begin(), static_cast<size_type>(value.size())) {}

    template<typename C, size_type N>
    array_view(C (&value)[N]) noexcept
        : array_view(value, N) {}

    template<typename C>
    array_view(std::vector<C>& value) noexcept
        : array_view(value.data(), static_cast<size_type>(value.size())) {}

    template<typename C>
    array_view(std::vector<C> const& value) noexcept
        : array_view(value.data(), static_cast<size_type>(value.size())) {}

    template<typename C, size_t N>
    array_view(std::array<C, N>& value) noexcept
        : array_view(value.data(), static_cast<size_type>(value.size())) {}

    template<typename C, size_t N>
    array_view(std::array<C, N> const& value) noexcept
        : array_view(value.data(), static_cast<size_type>(value.size())) {}

    template<typename C>
    array_view(array_view<C> const& other) noexcept
        : array_view(other.data(), other.size()) {}

    template<typename C>
    array_view(array<C> const& other) noexcept
        : array_view(other.data(), other.size()) {}

    reference operator[](size_type const pos) const noexcept {
        TH_ASSERT(pos < size(), "Pos should be less than array's size");
        return m_data[pos];
    }

    reference at(size_type const pos) const {
        if (size() <= pos) {
            throw std::out_of_range("Invalid array subscript");
        }
        return m_data[pos];
    }

    reference front() const noexcept {
        TH_ASSERT(m_size > 0, "Array's size should be greater than 0");
        return *m_data;
    }

    reference back() const noexcept {
        TH_ASSERT(m_size > 0, "Array's size should be greater than 0");
        return m_data[m_size - 1];
    }

    pointer data() const noexcept {
        return m_data;
    }

    bool empty() const noexcept {
        return m_size == 0;
    }

    size_type size() const noexcept {
        return m_size;
    }

    iterator begin() const noexcept {
        return m_data;
    }

    iterator end() const noexcept {
        return m_data + m_size;
    }

    reverse_iterator rbegin() const noexcept {
        return m_data + m_size;
    }

    reverse_iterator rend() const noexcept {
        return m_data;
    }

    const_iterator cbegin() const noexcept {
        return m_data;
    }

    const_iterator cend() const noexcept {
        return m_data + m_size;
    }

    const_reverse_iterator crbegin() const noexcept {
        return m_data + m_size;
    }

    const_reverse_iterator crend() const noexcept {
        return m_data;
    }

    friend bool operator==(array_view left, array_view right) noexcept {
        return std::equal(left.begin(), left.end(), right.begin(), right.end());
    }

    friend bool operator!=(array_view left, array_view right) noexcept { return !(left == right); }

    friend bool operator<(array_view left, array_view right) noexcept {
        return std::lexicographical_compare(left.begin(), left.end(), right.begin(), right.end());
    }

    friend bool operator>(array_view left, array_view right) noexcept { return right < left; }

    friend bool operator<=(array_view left, array_view right) noexcept { return !(right < left); }

    friend bool operator>=(array_view left, array_view right) noexcept { return !(left < right); }

protected:
    std::size_t m_size;
    cpp_owner_t* m_data;
};

struct copy_data_t {};
struct move_data_t {};

template<typename cpp_owner_t>
struct array : public array_view<cpp_owner_t> {
    using typename array_view<cpp_owner_t>::pointer;
    using typename array_view<cpp_owner_t>::size_type;

    array(pointer data, size_type size) noexcept : array_view<cpp_owner_t>(data, size) {} // main constructor

    template<typename value_type>
    array(std::initializer_list<value_type> value) noexcept
        : array((cpp_owner_t*)malloc(value.size() * sizeof(cpp_owner_t)), static_cast<size_type>(value.size())) {
        std::uninitialized_copy_n(value.begin(), value.size(), this->m_data);
    }


    template<typename C>
    array(C *data, size_type size, copy_data_t) noexcept
        : array((cpp_owner_t*)malloc(size * sizeof(cpp_owner_t)), size) {
        std::uninitialized_copy_n(data, size, this->m_data);
    }

    template<typename C>
    array(C *data, size_type size, move_data_t) noexcept
        : array((cpp_owner_t*)malloc(size * sizeof(cpp_owner_t)), size) {
        std::uninitialized_move_n(data, size, this->m_data);
    }

    template<typename... Args>
    static array make(size_type size, Args&&... args) {
        pointer data = (cpp_owner_t*)malloc(size * sizeof(cpp_owner_t));
        std::uninitialized_fill_n(data, size, cpp_owner_t(std::forward<Args>(args)...));
        return array(data, size);
    }

    array(array_view<cpp_owner_t> const& other)
        : array(other.data(), other.size(), copy_data_t{}) {}

    array(array<cpp_owner_t> const& other)
        : array(other.data(), other.size(), copy_data_t{}) {}

    array(array<cpp_owner_t>&& other)
        : array(std::exchange(other.m_data, nullptr), std::exchange(other.m_size, 0)) {}

    array &operator=(array other) {
        std::swap(this->m_size, other.m_size);
        std::swap(this->m_data, other.m_data);
        return *this;
    }

    ~array() {
        if (this->m_data) {
            std::destroy_n(this->m_data, this->m_size);
            free(this->m_data);
            this->m_size = 0;
            this->m_data = nullptr;
        }
    }
};

template<typename cpp_owner_t>
inline std::size_t hash_impl(adl_helper_t, array_view<cpp_owner_t> val) {
    std::size_t seed = 0;
    for (std::size_t i = 0; i < val.size(); i++) {
        seed ^= hash(val[i]) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    }
    return seed;
}

template<typename cpp_owner_t>
inline bool same_impl(adl_helper_t, array_view<cpp_owner_t> lhs, array_view<cpp_owner_t> rhs) {
    if (lhs.size() != rhs.size()) {
        return false;
    }
    for (std::size_t i = 0; i < lhs.size() && i < rhs.size(); i++) {
        if (!same(lhs[i], rhs[i])) {
            return false;
        }
    }
    return true;
}

template<typename cpp_owner_t>
struct as_abi<array_view<cpp_owner_t>> {
    using type = TArray;
};

template<typename cpp_owner_t>
struct as_abi<array<cpp_owner_t>> {
    using type = TArray;
};

template<typename cpp_owner_t>
struct as_param<array<cpp_owner_t>> {
    using type = array_view<cpp_owner_t>;
};
}
