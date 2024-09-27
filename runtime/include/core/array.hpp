#pragma once

#include <array>
#include <vector>
#include <cstddef>

#include <taihe/common.h>

namespace taihe::core {

struct take_ownership_from_abi_t {};

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

template <typename T>
struct th_array : array_view<T>
{
    using typename array_view<T>::value_type;
    using typename array_view<T>::size_type;
    using typename array_view<T>::reference;
    using typename array_view<T>::const_reference;
    using typename array_view<T>::pointer;
    using typename array_view<T>::const_pointer;
    using typename array_view<T>::iterator;
    using typename array_view<T>::const_iterator;
    using typename array_view<T>::reverse_iterator;
    using typename array_view<T>::const_reverse_iterator;

    th_array(th_array const&) = delete;
    th_array& operator=(th_array const&) = delete;

    th_array() noexcept = default;

    explicit th_array(size_type const count)
        : th_array(count, value_type()) {}

    th_array(void* ptr, uint32_t const count, take_ownership_from_abi_t) noexcept
        : array_view<T>(static_cast<value_type*>(ptr), static_cast<value_type*>(ptr) + count) {
    }

    th_array(size_type const count, value_type const& value) {
        alloc(count);
        std::uninitialized_fill_n(this->m_data, count, value);
    }

    template <typename InIt, typename = std::void_t<typename std::iterator_traits<InIt>::difference_type>>
    th_array(InIt first, InIt last) {
        alloc(static_cast<size_type>(std::distance(first, last)));
        std::uninitialized_copy(first, last, this->begin());
    }

    template <typename U>
    explicit th_array(std::vector<U> const& value) 
        : th_array(value.begin(), value.end()) {}

    template <typename U, size_t N>
    explicit th_array(std::array<U, N> const& value)
        : th_array(value.begin(), value.end()) {}

    template <typename U, size_t N>
    explicit th_array(U const(&value)[N])
        : th_array(value, value + N) {}

    th_array(std::initializer_list<value_type> value)
        : th_array(value.begin(), value.end()) {}

    template <typename U, typename = std::enable_if_t<std::is_convertible_v<U, T>>>
    th_array(std::initializer_list<U> value)
        : th_array(value.begin(), value.end()) {}

    th_array(th_array&& other) noexcept
        : array_view<T>(other.m_data, other.m_size) {
        other.m_data = nullptr;
        other.m_size = 0;
    }

    th_array& operator=(th_array&& other) noexcept {
        clear();
        this->m_data = other.m_data;
        this->m_size = other.m_size;
        other.m_data = nullptr;
        other.m_size = 0;
        return*this;
    }

    ~th_array() noexcept {
        clear();
    }

    void clear() noexcept {
        if (this->m_data == nullptr) { return; }

        std::destroy(this->begin(), this->end());

        free(this->m_data);
        this->m_data = nullptr;
        this->m_size = 0;
    }

    friend void swap(th_array& left, th_array& right) noexcept {
        std::swap(left.m_data, right.m_data);
        std::swap(left.m_size, right.m_size);
    }

private:
    void alloc(size_type const size) {
        TH_ASSERT(this->empty(), "this array should be empty");

        if (0 != size) {
            size_t bytes_required = sizeof(value_type) * size;
            this->m_data = static_cast<value_type*>(malloc(bytes_required));

            if (this->m_data == nullptr) {
                throw std::bad_alloc();
            }

            this->m_size = size;
        }
    }
};

namespace impl {
    template <typename T, typename U>
    inline constexpr bool array_comparable = std::is_same_v<std::remove_cv_t<T>, std::remove_cv_t<U>>;
}

template <typename T, typename U, 
    std::enable_if_t<impl::array_comparable<T, U>, int> = 0>
bool operator==(array_view<T> const& left, array_view<U> const& right) noexcept {
    return std::equal(left.begin(), left.end(), right.begin(), right.end());
}

template <typename T, typename U,
    std::enable_if_t<impl::array_comparable<T, U>, int> = 0>
bool operator<(array_view<T> const& left, array_view<U> const& right) noexcept {
    return std::lexicographical_compare(left.begin(), left.end(), right.begin(), right.end());
}

template <typename T, typename U, std::enable_if_t<impl::array_comparable<T, U>, int> = 0>
bool operator!=(array_view<T> const& left, array_view<U> const& right) noexcept { return !(left == right); }
template <typename T, typename U,std::enable_if_t<impl::array_comparable<T, U>, int> = 0>
bool operator>(array_view<T> const& left, array_view<U> const& right) noexcept { return right < left; }
template <typename T, typename U,std::enable_if_t<impl::array_comparable<T, U>, int> = 0>
bool operator<=(array_view<T> const& left, array_view<U> const& right) noexcept { return !(right < left); }
template <typename T, typename U, std::enable_if_t<impl::array_comparable<T, U>, int> = 0>
bool operator>=(array_view<T> const& left, array_view<U> const& right) noexcept { return !(left < right); }

/////////////////////////////
//////////abi func///////////
/////////////////////////////
///////to be continued///////
/////////////////////////////
}
