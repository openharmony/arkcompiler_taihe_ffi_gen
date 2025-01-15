#pragma once

#include <array>
#include <cstdlib>
#include <memory>
#include <vector>
#include <cstddef>

#include <taihe/common.hpp>

template <typename T>
struct ArrayABI {
    T* m_data;
    std::size_t m_size;
};

namespace taihe::core {
template <typename T>
struct array_view;

template <typename T>
struct array;

template <typename T>
struct array_view {
    using value_type = T;
    using size_type = std::size_t;
    using reference = value_type&;
    using const_reference = value_type const&;
    using pointer = value_type*;
    using const_pointer = value_type const*;
    using iterator = value_type*;
    using const_iterator = value_type const*;
    using reverse_iterator = std::reverse_iterator<iterator>;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    explicit array_view(ArrayABI<T> handle) noexcept
        : m_handle(handle) {}

    array_view(pointer data, size_type size) noexcept
        : m_handle{data, size} {}

    array_view(array<T> const& other)
        : array_view(other.data(), other.size()) {}

    array_view(array_view<T> const& other)
        : array_view(other.data(), other.size()) {}

    array_view &operator=(array_view other) {
        std::swap(m_handle, other.m_handle);
        return *this;
    }

    template <typename C>
    array_view(std::initializer_list<C> value) noexcept
        : array_view(value.begin(), static_cast<size_type>(value.size())) {}

    template <typename C, size_type N>
    array_view(C (&value)[N]) noexcept
        : array_view(value, N) {}

    template <typename C>
    array_view(std::vector<C>& value) noexcept
        : array_view(get_data(value), static_cast<size_type>(value.size())) {}

    template <typename C>
    array_view(std::vector<C> const& value) noexcept
        : array_view(get_data(value), static_cast<size_type>(value.size())) {}

    template <typename C, size_t N>
    array_view(std::array<C, N>& value) noexcept
        : array_view(value.data(), static_cast<size_type>(value.size())) {}

    template <typename C, size_t N>
    array_view(std::array<C, N> const& value) noexcept
        : array_view(value.data(), static_cast<size_type>(value.size())) {}

    template <typename C>
    array_view(array_view<C> const& other) noexcept
        : array_view(other.data(), other.size()) {}

    template <typename C>
    array_view(array<C> const& other) noexcept
        : array_view(other.data(), other.size()) {}

    reference operator[](size_type const pos) noexcept {
        TH_ASSERT(pos < size(), "Pos should be less than array's size");
        return m_handle.m_data[pos];
    }

    const_reference operator[](size_type const pos) const noexcept {
        TH_ASSERT(pos < size(), "Pos should be less than array's size");
        return m_handle.m_data[pos];
    }

    reference at(size_type const pos) {
        if (size() <= pos) {
            throw std::out_of_range("Invalid array subscript");
        }
        return m_handle.m_data[pos];
    }

    const_reference at(size_type const pos) const {
        if (size() <= pos) {
            throw std::out_of_range("Invalid array subscript");
        }
        return m_handle.m_data[pos];
    }

    reference front() noexcept {
        TH_ASSERT(m_handle.m_size > 0, "Array's size should be greater than 0");
        return *m_handle.m_data;
    }

    const_reference front() const noexcept {
        TH_ASSERT(m_handle.m_size > 0, "Array's size should be greater than 0");
        return *m_handle.m_data;
    }

    reference back() noexcept {
        TH_ASSERT(m_handle.m_size > 0, "Array's size should be greater than 0");
        return m_handle.m_data[m_handle.m_size - 1];
    }

    const_reference back() const noexcept {
        TH_ASSERT(m_handle.m_size > 0, "Array's size should be greater than 0");
        return m_handle.m_data[m_handle.m_size - 1];
    }

    pointer data() noexcept {
        return m_handle.m_data;
    }

    const_pointer data() const noexcept {
        return m_handle.m_data;
    }

    bool empty() const noexcept {
        return m_handle.m_size == 0;
    }

    size_type size() const noexcept {
        return m_handle.m_size;
    }

    iterator begin() const noexcept {
        return m_handle.m_data;
    }

    const_iterator cbegin() const noexcept {
        return m_handle.m_data;
    }

    iterator end() const noexcept {
        return m_handle.m_data + m_handle.m_size;
    }

    const_iterator cend() const noexcept {
        return m_handle.m_data + m_handle.m_size;
    }

    reverse_iterator rbegin() const noexcept {
        return m_handle.m_data + m_handle.m_size;
    }

    const_reverse_iterator crbegin() const noexcept {
        return m_handle.m_data + m_handle.m_size;
    }

    reverse_iterator rend() const noexcept {
        return m_handle.m_data;
    }

    const_reverse_iterator crend() const noexcept {
        return m_handle.m_data;
    }

private:
    ArrayABI<T> m_handle;

    template <typename C>
    static auto get_data(std::vector<C> const& value) noexcept {
        static_assert(!std::is_same_v<C, bool>, "Cannot use std::vector<bool> as an array_view. Consider std::array or std::unique_ptr<bool[]>.");
        return value.data();
    }

    template <typename C>
    static auto get_data(std::vector<C>& value) noexcept {
        static_assert(!std::is_same_v<C, bool>, "Cannot use std::vector<bool> as an array_view. Consider std::array or std::unique_ptr<bool[]>.");
        return value.data();
    }
};

struct copy_data_t {};
struct move_data_t {};

template <typename T>
struct array {
    using value_type = T;
    using size_type = std::size_t;
    using reference = value_type&;
    using const_reference = value_type const&;
    using pointer = value_type*;
    using const_pointer = value_type const*;
    using iterator = value_type*;
    using const_iterator = value_type const*;
    using reverse_iterator = std::reverse_iterator<iterator>;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    explicit array(ArrayABI<T> handle) noexcept
        : m_handle(handle) {}

    template<typename Arg>
    array(size_t size, Arg&& arg) {
        m_handle.m_size = size;
        m_handle.m_data = malloc(size * sizeof(T));
        std::uninitialized_fill_n(m_handle.m_data, size, std::forward<Arg>(arg));
    }

    array(pointer data, size_type size, copy_data_t) noexcept {
        m_handle.m_size = size;
        m_handle.m_data = malloc(size * sizeof(T));
        std::uninitialized_copy_n(data, size, m_handle.m_data);
    }

    array(pointer data, size_type size, move_data_t) noexcept {
        m_handle.m_size = size;
        m_handle.m_data = malloc(size * sizeof(T));
        std::uninitialized_move_n(data, size, m_handle.m_data);
    }

    array(array<T> const& other)
        : array(other.data(), other.size(), copy_data_t{}) {}

    array(array<T>&& other)
        : m_handle(other.m_handle) {
        other.m_handle.m_size = 0;
        other.m_handle.m_data = nullptr;
    }

    array &operator=(array other) {
        std::swap(m_handle, other.m_handle);
        return *this;
    }

    ~array() {
        if (m_handle.m_data) {
            std::destroy_n(data(), size());
            free(m_handle.m_data);
            m_handle.m_data = nullptr;
        }
    }

    template <typename C>
    array(std::initializer_list<C> value) noexcept
        : array(value.begin(), static_cast<size_type>(value.size()), copy_data_t{}) {}

    template <typename C, size_type N>
    array(C (&&value)[N]) noexcept
        : array(value, N, move_data_t{}) {}

    template <typename C, size_type N>
    array(C (&value)[N]) noexcept
        : array(value, N, copy_data_t{}) {}

    template <typename C>
    array(std::vector<C> const& value) noexcept
        : array(value.data(), static_cast<size_type>(value.size()), copy_data_t{}) {}

    template <typename C>
    array(std::vector<C>&& value) noexcept
        : array(value.data(), static_cast<size_type>(value.size()), move_data_t{}) {}

    template <typename C, size_t N>
    array(std::array<C, N> const& value) noexcept
        : array(value.data(), static_cast<size_type>(value.size()), copy_data_t{}) {}

    template <typename C, size_t N>
    array(std::array<C, N>&& value) noexcept
        : array(value.data(), static_cast<size_type>(value.size()), move_data_t{}) {}

    reference operator[](size_type const pos) noexcept {
        TH_ASSERT(pos < size(), "Pos should be less than array's size");
        return m_handle.m_data[pos];
    }

    const_reference operator[](size_type const pos) const noexcept {
        TH_ASSERT(pos < size(), "Pos should be less than array's size");
        return m_handle.m_data[pos];
    }

    reference at(size_type const pos) {
        if (size() <= pos) {
            throw std::out_of_range("Invalid array subscript");
        }
        return m_handle.m_data[pos];
    }

    const_reference at(size_type const pos) const {
        if (size() <= pos) {
            throw std::out_of_range("Invalid array subscript");
        }
        return m_handle.m_data[pos];
    }

    reference front() noexcept {
        TH_ASSERT(m_handle.m_size > 0, "Array's size should be greater than 0");
        return *m_handle.m_data;
    }

    const_reference front() const noexcept {
        TH_ASSERT(m_handle.m_size > 0, "Array's size should be greater than 0");
        return *m_handle.m_data;
    }

    reference back() noexcept {
        TH_ASSERT(m_handle.m_size > 0, "Array's size should be greater than 0");
        return m_handle.m_data[m_handle.m_size - 1];
    }

    const_reference back() const noexcept {
        TH_ASSERT(m_handle.m_size > 0, "Array's size should be greater than 0");
        return m_handle.m_data[m_handle.m_size - 1];
    }

    pointer data() noexcept {
        return m_handle.m_data;
    }

    const_pointer data() const noexcept {
        return m_handle.m_data;
    }

    bool empty() const noexcept {
        return m_handle.m_size == 0;
    }

    size_type size() const noexcept {
        return m_handle.m_size;
    }

    iterator begin() const noexcept {
        return m_handle.m_data;
    }

    const_iterator cbegin() const noexcept {
        return m_handle.m_data;
    }

    iterator end() const noexcept {
        return m_handle.m_data + m_handle.m_size;
    }

    const_iterator cend() const noexcept {
        return m_handle.m_data + m_handle.m_size;
    }

    reverse_iterator rbegin() const noexcept {
        return m_handle.m_data + m_handle.m_size;
    }

    const_reverse_iterator crbegin() const noexcept {
        return m_handle.m_data + m_handle.m_size;
    }

    reverse_iterator rend() const noexcept {
        return m_handle.m_data;
    }

    const_reverse_iterator crend() const noexcept {
        return m_handle.m_data;
    }

private:
    ArrayABI<T> m_handle;
};

template <typename T>
bool operator==(array_view<T> const& left, array_view<T> const& right) noexcept {
    return std::equal(left.begin(), left.end(), right.begin(), right.end());
}

template <typename T>
bool operator!=(array_view<T> const& left, array_view<T> const& right) noexcept { return !(left == right); }

template <typename T>
bool operator<(array_view<T> const& left, array_view<T> const& right) noexcept {
    return std::lexicographical_compare(left.begin(), left.end(), right.begin(), right.end());
}

template <typename T>
bool operator>(array_view<T> const& left, array_view<T> const& right) noexcept { return right < left; }

template <typename T>
bool operator<=(array_view<T> const& left, array_view<T> const& right) noexcept { return !(right < left); }

template <typename T>
bool operator>=(array_view<T> const& left, array_view<T> const& right) noexcept { return !(left < right); }

template<typename T>
using const_array = array<const T>;

template<typename T>
using const_array_view = array_view<const T>;
}
