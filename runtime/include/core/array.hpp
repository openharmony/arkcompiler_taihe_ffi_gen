#pragma once

#include <array>
#include <memory>
#include <utility>
#include <vector>
#include <stdexcept>
#include <cstdlib>
#include <cstddef>

#include <taihe/common.hpp>

template<typename abi_field_t>
struct TArray {
    std::size_t m_size;
    abi_field_t* m_data;
};

template<typename abi_field_t>
TArray<abi_field_t> tarr_dup(TArray<abi_field_t> a) {
    TArray<abi_field_t> b;
    b.m_size = a.m_size;
    b.m_data = (abi_field_t*)malloc(a.m_size * sizeof(abi_field_t));
    std::uninitialized_copy_n(a.m_data, a.m_size, b.m_data);
    return b;
}

template<typename abi_field_t>
void tarr_drop(TArray<abi_field_t> a) {
    std::destroy_n(a.m_data, a.m_size);
    free(a.m_data);
}

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

    array_view(array<cpp_owner_t> const& other)
        : m_data(other.m_data), m_size(other.m_size) {}

    array_view(array_view<cpp_owner_t> const& other)
        : m_data(other.m_data), m_size(other.m_size) {}

    array_view &operator=(array_view other) {
        std::swap(m_data, other.m_data);
        std::swap(m_size, other.m_size);
        return *this;
    }

    array_view(pointer data, size_type size) noexcept
        : m_data(data), m_size(size) {}

    template<typename C>
    array_view(std::initializer_list<C> value) noexcept
        : array_view(value.begin(), static_cast<size_type>(value.size())) {}

    template<typename C, size_type N>
    array_view(C (&value)[N]) noexcept
        : array_view(value, N) {}

    template<typename C>
    array_view(std::vector<C>& value) noexcept
        : array_view(get_data(value), static_cast<size_type>(value.size())) {}

    template<typename C>
    array_view(std::vector<C> const& value) noexcept
        : array_view(get_data(value), static_cast<size_type>(value.size())) {}

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

    reference operator[](size_type const pos) noexcept {
        TH_ASSERT(pos < size(), "Pos should be less than array's size");
        return m_data[pos];
    }

    const_reference operator[](size_type const pos) const noexcept {
        TH_ASSERT(pos < size(), "Pos should be less than array's size");
        return m_data[pos];
    }

    reference at(size_type const pos) {
        if (size() <= pos) {
            throw std::out_of_range("Invalid array subscript");
        }
        return m_data[pos];
    }

    const_reference at(size_type const pos) const {
        if (size() <= pos) {
            throw std::out_of_range("Invalid array subscript");
        }
        return m_data[pos];
    }

    reference front() noexcept {
        TH_ASSERT(m_size > 0, "Array's size should be greater than 0");
        return *m_data;
    }

    const_reference front() const noexcept {
        TH_ASSERT(m_size > 0, "Array's size should be greater than 0");
        return *m_data;
    }

    reference back() noexcept {
        TH_ASSERT(m_size > 0, "Array's size should be greater than 0");
        return m_data[m_size - 1];
    }

    const_reference back() const noexcept {
        TH_ASSERT(m_size > 0, "Array's size should be greater than 0");
        return m_data[m_size - 1];
    }

    pointer data() noexcept {
        return m_data;
    }

    const_pointer data() const noexcept {
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

    const_iterator cbegin() const noexcept {
        return m_data;
    }

    iterator end() const noexcept {
        return m_data + m_size;
    }

    const_iterator cend() const noexcept {
        return m_data + m_size;
    }

    reverse_iterator rbegin() const noexcept {
        return m_data + m_size;
    }

    const_reverse_iterator crbegin() const noexcept {
        return m_data + m_size;
    }

    reverse_iterator rend() const noexcept {
        return m_data;
    }

    const_reverse_iterator crend() const noexcept {
        return m_data;
    }

private:
    std::size_t m_size;
    cpp_owner_t* m_data;

    template<typename C>
    static auto get_data(std::vector<C> const& value) noexcept {
        static_assert(!std::is_same_v<C, bool>, "Cannot use std::vector<bool> as an array_view. Consider std::array or std::unique_ptr<bool[]>.");
        return value.data();
    }

    template<typename C>
    static auto get_data(std::vector<C>& value) noexcept {
        static_assert(!std::is_same_v<C, bool>, "Cannot use std::vector<bool> as an array_view. Consider std::array or std::unique_ptr<bool[]>.");
        return value.data();
    }

    friend struct array<cpp_owner_t>;
};

struct copy_data_t {};
struct move_data_t {};

template<typename cpp_owner_t>
struct array {
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

    array(size_t size, cpp_owner_t const& arg)
        : m_size(size), m_data((cpp_owner_t*)malloc(size * sizeof(cpp_owner_t))) {
        std::uninitialized_fill_n(m_data, size, arg);
    }

    array(pointer data, size_type size, copy_data_t) noexcept
        : m_size(size), m_data((cpp_owner_t*)malloc(size * sizeof(cpp_owner_t))) {
        std::uninitialized_copy_n(data, size, m_data);
    }

    array(pointer data, size_type size, move_data_t) noexcept
        : m_size(size), m_data((cpp_owner_t*)malloc(size * sizeof(cpp_owner_t))) {
        std::uninitialized_move_n(data, size, m_data);
    }

    array(array_view<cpp_owner_t> const& other)
        : array(other.data(), other.size(), copy_data_t{}) {}

    array(array<cpp_owner_t> const& other)
        : array(other.data(), other.size(), copy_data_t{}) {}

    array(array<cpp_owner_t>&& other)
        : m_size(std::exchange(other.m_size, 0)), m_data(std::exchange(other.m_data, nullptr)) {}

    array &operator=(array other) {
        std::swap(m_size, other.m_size);
        std::swap(m_data, other.m_data);
        return *this;
    }

    ~array() {
        if (m_data) {
            std::destroy_n(data(), size());
            free(m_data);
            m_size = 0;
            m_data = nullptr;
        }
    }

    template<typename C>
    array(std::initializer_list<C> value) noexcept
        : array(value.begin(), static_cast<size_type>(value.size()), copy_data_t{}) {}

    template<typename C, size_type N>
    array(C (&&value)[N]) noexcept
        : array(value, N, move_data_t{}) {}

    template<typename C, size_type N>
    array(C (&value)[N]) noexcept
        : array(value, N, copy_data_t{}) {}

    template<typename C>
    array(std::vector<C> const& value) noexcept
        : array(value.data(), static_cast<size_type>(value.size()), copy_data_t{}) {}

    template<typename C>
    array(std::vector<C>&& value) noexcept
        : array(value.data(), static_cast<size_type>(value.size()), move_data_t{}) {}

    template<typename C, size_t N>
    array(std::array<C, N> const& value) noexcept
        : array(value.data(), static_cast<size_type>(value.size()), copy_data_t{}) {}

    template<typename C, size_t N>
    array(std::array<C, N>&& value) noexcept
        : array(value.data(), static_cast<size_type>(value.size()), move_data_t{}) {}

    reference operator[](size_type const pos) noexcept {
        TH_ASSERT(pos < size(), "Pos should be less than array's size");
        return m_data[pos];
    }

    const_reference operator[](size_type const pos) const noexcept {
        TH_ASSERT(pos < size(), "Pos should be less than array's size");
        return m_data[pos];
    }

    reference at(size_type const pos) {
        if (size() <= pos) {
            throw std::out_of_range("Invalid array subscript");
        }
        return m_data[pos];
    }

    const_reference at(size_type const pos) const {
        if (size() <= pos) {
            throw std::out_of_range("Invalid array subscript");
        }
        return m_data[pos];
    }

    reference front() noexcept {
        TH_ASSERT(m_size > 0, "Array's size should be greater than 0");
        return *m_data;
    }

    const_reference front() const noexcept {
        TH_ASSERT(m_size > 0, "Array's size should be greater than 0");
        return *m_data;
    }

    reference back() noexcept {
        TH_ASSERT(m_size > 0, "Array's size should be greater than 0");
        return m_data[m_size - 1];
    }

    const_reference back() const noexcept {
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

    const_iterator cbegin() const noexcept {
        return m_data;
    }

    iterator end() const noexcept {
        return m_data + m_size;
    }

    const_iterator cend() const noexcept {
        return m_data + m_size;
    }

    reverse_iterator rbegin() const noexcept {
        return m_data + m_size;
    }

    const_reverse_iterator crbegin() const noexcept {
        return m_data + m_size;
    }

    reverse_iterator rend() const noexcept {
        return m_data;
    }

    const_reverse_iterator crend() const noexcept {
        return m_data;
    }

private:
    std::size_t m_size;
    cpp_owner_t* m_data;

    friend struct array_view<cpp_owner_t>;
};

template<typename cpp_owner_t>
bool operator==(array_view<cpp_owner_t> const& left, array_view<cpp_owner_t> const& right) noexcept {
    return std::equal(left.begin(), left.end(), right.begin(), right.end());
}

template<typename cpp_owner_t>
bool operator!=(array_view<cpp_owner_t> const& left, array_view<cpp_owner_t> const& right) noexcept { return !(left == right); }

template<typename cpp_owner_t>
bool operator<(array_view<cpp_owner_t> const& left, array_view<cpp_owner_t> const& right) noexcept {
    return std::lexicographical_compare(left.begin(), left.end(), right.begin(), right.end());
}

template<typename cpp_owner_t>
bool operator>(array_view<cpp_owner_t> const& left, array_view<cpp_owner_t> const& right) noexcept { return right < left; }

template<typename cpp_owner_t>
bool operator<=(array_view<cpp_owner_t> const& left, array_view<cpp_owner_t> const& right) noexcept { return !(right < left); }

template<typename cpp_owner_t>
bool operator>=(array_view<cpp_owner_t> const& left, array_view<cpp_owner_t> const& right) noexcept { return !(left < right); }
}
