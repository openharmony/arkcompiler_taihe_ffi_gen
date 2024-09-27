#pragma once

#include <array>
#include <vector>
#include <cstddef>

#include <taihe/common.h>

namespace taihe::core {
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

    array_view() noexcept = default;

    array_view(pointer data, size_type size) noexcept
        : m_data(data)
        , m_size(size) {}

    array_view(pointer first, pointer last) noexcept
        : m_data(first)
        , m_size(static_cast<size_type>(last - first)) {}

    array_view(std::initializer_list<value_type> value) noexcept :           
        array_view(const_cast<pointer>(value.begin()), static_cast<size_type>(value.size())) {}

    template <typename C, size_type N>
    array_view(C (&value)[N]) noexcept
        : array_view(value, N) {}

    template <typename C>
    array_view(std::vector<C>& value) noexcept
        : array_view(data(value), static_cast<size_type>(value.size())) {}

    template <typename C>
    array_view(std::vector<C> const& value) noexcept
        : array_view(data(value), static_cast<size_type>(value.size())) {}

    template <typename C, size_t N>
    array_view(std::array<C, N>& value) noexcept
        : array_view(value.data(), static_cast<size_type>(value.size())) {}

    template <typename C, size_t N>
    array_view(std::array<C, N> const& value) noexcept
        : array_view(value.data(), static_cast<size_type>(value.size())) {}

    template <typename OtherType>
    array_view(array_view<OtherType> const& other,
        std::enable_if_t<std::is_convertible_v<OtherType(*)[], T(*)[]>, int> = 0) noexcept
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

    pointer data() const noexcept {
        return m_data;
    }

    iterator begin() noexcept {
        return m_data;
    }

    const_iterator begin() const noexcept {
        return m_data;
    }

    const_iterator cbegin() const noexcept {
        return m_data;
    }

    iterator end() noexcept {
        return m_data + m_size;
    }

    const_iterator end() const noexcept {
        return m_data + m_size;
    }

    const_iterator cend() const noexcept {
        return m_data + m_size;
    }

    reverse_iterator rbegin() noexcept {
        return reverse_iterator(end());
    }

    const_reverse_iterator rbegin() const noexcept {
        return const_reverse_iterator(end());
    }

    const_reverse_iterator crbegin() const noexcept {
        return rbegin();
    }

    reverse_iterator rend() noexcept {
        return reverse_iterator(begin());
    }

    const_reverse_iterator rend() const noexcept {
        return const_reverse_iterator(begin());
    }

    const_reverse_iterator crend() const noexcept {
        return rend();
    }

    bool empty() const noexcept {
        return m_size == 0;
    }

    size_type size() const noexcept {
        return m_size;
    }

protected:
    pointer m_data{ nullptr };
    size_type m_size{ 0 };

private:
    template <typename C>
    auto data(std::vector<C> const& value) noexcept {
        static_assert(!std::is_same_v<C, bool>, "Cannot use std::vector<bool> as an array_view. Consider std::array or std::unique_ptr<bool[]>.");
        return value.data();
    }

    template <typename C>
    auto data(std::vector<C>& value) noexcept {
        static_assert(!std::is_same_v<C, bool>, "Cannot use std::vector<bool> as an array_view. Consider std::array or std::unique_ptr<bool[]>.");
        return value.data();
    }
};
/* C++ 20 
 * template <typename C, size_t N> array_view(C(&value)[N]) -> array_view<C>;
 * template <typename C> array_view(std::vector<C>& value) -> array_view<C>;
 * template <typename C> array_view(std::vector<C> const& value) -> array_view<C const>;
 * template <typename C, size_t N> array_view(std::array<C, N>& value) -> array_view<C>;
 * template <typename C, size_t N> array_view(std::array<C, N> const& value) -> array_view<C const>;
 */
}
