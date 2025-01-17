#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <utility>
#include <string>
#include <string_view>
#include <iostream>
#include <charconv>

#include <taihe/common.hpp>
#include <taihe/string.abi.h>

namespace taihe::core {
struct string_view_container;

using string_view = string_view_container const&;

struct string {
public:
    // Using
    using value_type = char;
    using size_type = std::size_t;
    using const_reference = value_type const&;
    using const_pointer = value_type const*;
    using const_iterator = const_pointer;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    string(const char* value TH_NONNULL)
        : m_handle(tstr_new(value, std::strlen(value))) {}

    string(const char* value TH_NONNULL, size_type size)
        : m_handle(tstr_new(value, size)) {}

    string(std::initializer_list<char> value)
        : string(value.begin(), static_cast<uint32_t>(value.size())) {}

    string(std::string_view value)
        : string(value.data(), value.size()) {}

    string(std::string const &value)
        : string(value.data(), value.size()) {}

    operator string_view() const {
        return reinterpret_cast<string_view>(*m_handle);
    }

    operator std::string_view() const noexcept {
        return { tstr_buf(m_handle), tstr_len(m_handle) };
    }

    // copy assignment
    string(string const& other)
        : m_handle(tstr_dup(other.m_handle)) {}

    // move assignment
    string(string&& other) noexcept
        : m_handle(other.m_handle) {
        other.m_handle = nullptr;
    }

    // destructor
    ~string() {
        tstr_drop(m_handle);
    }

    // assignment
    string& operator=(string other) {
        // copy-and-swap idiom
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

private:
    explicit string(TString const* other_handle)
        : m_handle(other_handle) {}

public:
    const_reference operator[](size_type pos) const {
        if (pos >= size()) {
            throw std::out_of_range("Index out of range");
        }
        return tstr_buf(m_handle)[pos];
    }

    // others
    bool empty() const noexcept {
        return tstr_len(m_handle) == 0;
    }

    size_type size() const noexcept {
        return tstr_len(m_handle);
    }

    const_reference front() const {
        if (empty()) {
            throw std::out_of_range("Empty string");
        }
        return tstr_buf(m_handle)[0];
    }

    const_reference back() const {
        if (empty()) {
            throw std::out_of_range("Empty string");
        }
        return tstr_buf(m_handle)[size() - 1];
    }

    const_pointer c_str() const noexcept {
        return tstr_buf(m_handle);
    }

    const_pointer data() const noexcept {
        return c_str();
    }

    const_iterator begin() const noexcept {
        return tstr_buf(m_handle);
    }

    const_iterator cbegin() const noexcept {
        return begin();
    }

    const_iterator end() const noexcept {
        return tstr_buf(m_handle) + tstr_len(m_handle);
    }

    const_iterator cend() const noexcept {
        return end();
    }

    const_reverse_iterator rbegin() const noexcept {
        return const_reverse_iterator(end());
    }

    const_reverse_iterator crbegin() const noexcept {
        return rbegin();
    }

    const_reverse_iterator rend() const noexcept {
        return const_reverse_iterator(begin());
    }

    const_reverse_iterator crend() const noexcept {
        return rend();
    }

private:
    friend class string_view_container;
    friend string concat(string_view left, string_view right);
    friend string substr(string_view sv, std::size_t pos, std::size_t len);

    TString const* m_handle;
};

struct string_view_container {
    // Using
    using value_type = char;
    using size_type = std::size_t;
    using const_reference = value_type const&;
    using const_pointer = value_type const*;
    using const_iterator = const_pointer;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    string_view_container(const char* value TH_NONNULL)
        : m_header(tstr_new_ref(value, strlen(value))) {}

    string_view_container(const char* value TH_NONNULL, size_type size)
        : m_header(tstr_new_ref(value, size)) {}

    string_view_container(std::initializer_list<char> value)
        : string_view_container(value.begin(), static_cast<uint32_t>(value.size())) {}

    string_view_container(std::string_view value)
        : string_view_container(value.data(), value.size()) {}

    string_view_container(std::string const &value)
        : string_view_container(value.data(), value.size()) {}

    operator std::string_view() const noexcept {
        return { tstr_buf(&m_header), tstr_len(&m_header) };
    }

    operator string() const noexcept {
        return string(tstr_dup(&m_header));
    }

public:
    const_reference operator[](size_type pos) const {
        if (pos >= size()) {
            throw std::out_of_range("Index out of range");
        }
        return tstr_buf(&m_header)[pos];
    }

    // others
    bool empty() const noexcept {
        return tstr_len(&m_header) == 0;
    }

    size_type size() const noexcept {
        return tstr_len(&m_header);
    }

    const_reference front() const {
        if (empty()) {
            throw std::out_of_range("Empty string");
        }
        return tstr_buf(&m_header)[0];
    }

    const_reference back() const {
        if (empty()) {
            throw std::out_of_range("Empty string");
        }
        return tstr_buf(&m_header)[size() - 1];
    }

    const_pointer c_str() const noexcept {
        return tstr_buf(&m_header);
    }

    const_pointer data() const noexcept {
        return c_str();
    }

    const_iterator begin() const noexcept {
        return tstr_buf(&m_header);
    }

    const_iterator cbegin() const noexcept {
        return begin();
    }

    const_iterator end() const noexcept {
        return tstr_buf(&m_header) + tstr_len(&m_header);
    }

    const_iterator cend() const noexcept {
        return end();
    }

    const_reverse_iterator rbegin() const noexcept {
        return const_reverse_iterator(end());
    }

    const_reverse_iterator crbegin() const noexcept {
        return rbegin();
    }

    const_reverse_iterator rend() const noexcept {
        return const_reverse_iterator(begin());
    }

    const_reverse_iterator crend() const noexcept {
        return rend();
    }

private:
    friend string concat(string_view left, string_view right);
    friend string substr(string_view sv, std::size_t pos, std::size_t len);

    struct TString m_header;
};

inline string substr(string_view sv, std::size_t pos, std::size_t len) {
    return string(tstr_substr(&sv.m_header, pos, len));
}

inline string concat(string_view left, string_view right) {
    return string(tstr_concat(&left.m_header, &right.m_header));
}

inline bool operator==(string_view lhs, string_view rhs) {
    return std::string_view(lhs) == std::string_view(rhs);
}

inline bool operator!=(string_view lhs, string_view rhs) {
    return std::string_view(lhs) != std::string_view(rhs);
}

inline bool operator<(string_view lhs, string_view rhs) {
    return std::string_view(lhs) < std::string_view(rhs);
}

inline bool operator>(string_view lhs, string_view rhs) {
    return std::string_view(lhs) > std::string_view(rhs);
}

inline bool operator<=(string_view lhs, string_view rhs) {
    return std::string_view(lhs) <= std::string_view(rhs);
}

inline bool operator>=(string_view lhs, string_view rhs) {
    return std::string_view(lhs) >= std::string_view(rhs);
}

inline std::ostream& operator<<(std::ostream& os, string_view sv) {
    return os << std::string_view(sv);
}

template<typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
inline string to_string(T value) {
    char buffer[32];
    std::to_chars_result result;
    result = std::to_chars(std::begin(buffer), std::end(buffer), value);
    if (result.ec != std::errc{}) {
        throw std::runtime_error("Conversion to char failed");
    }
    *result.ptr = '\0'; // std::to_chars does not write '\0' at the end of the buffer automatcally
    return string{ buffer, static_cast<std::size_t>(result.ptr - buffer) };
}

template<typename T, std::enable_if_t<std::is_floating_point_v<T>, int> = 0>
inline string to_string(T value) {
    char buffer[32];
    std::to_chars_result result;
    result = std::to_chars(std::begin(buffer), std::end(buffer), value, std::chars_format::general);
    if (result.ec != std::errc{}) {
        throw std::runtime_error("Conversion to char failed");
    }
    *result.ptr = '\0'; // std::to_chars does not write '\0' at the end of the buffer automatcally
    return string{ buffer, static_cast<std::size_t>(result.ptr - buffer) };
}

template<typename T, std::enable_if_t<std::is_same_v<T, bool>, int> = 0>
string to_string(T const value) {
    if (value) {
        return string{ "true" };
    } else {
        return string{ "false" };
    }
}
}
