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
struct string_view;
struct string;

struct string_view {
    using value_type = char;
    using size_type = std::size_t;
    using const_reference = value_type const&;
    using const_pointer = value_type const*;
    using const_iterator = const_pointer;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    explicit string_view(struct TString m_data) : m_data(m_data) {}

    string_view(const char* value TH_NONNULL)
        : string_view(tstr_new_ref(value, strlen(value))) {}

    string_view(const char* value TH_NONNULL, size_type size)
        : string_view(tstr_new_ref(value, size)) {}

    string_view(std::initializer_list<char> value)
        : string_view(value.begin(), static_cast<uint32_t>(value.size())) {}

    string_view(std::string_view value)
        : string_view(value.data(), value.size()) {}

    string_view(std::string const &value)
        : string_view(value.data(), value.size()) {}

    operator std::string_view() const noexcept {
        return { tstr_buf(m_data), tstr_len(m_data) };
    }

    // methods
    const_reference operator[](size_type pos) const {
        if (pos >= size()) {
            throw std::out_of_range("Index out of range");
        }
        return tstr_buf(m_data)[pos];
    }

    bool empty() const noexcept {
        return tstr_len(m_data) == 0;
    }

    size_type size() const noexcept {
        return tstr_len(m_data);
    }

    const_reference front() const {
        if (empty()) {
            throw std::out_of_range("Empty string");
        }
        return tstr_buf(m_data)[0];
    }

    const_reference back() const {
        if (empty()) {
            throw std::out_of_range("Empty string");
        }
        return tstr_buf(m_data)[size() - 1];
    }

    const_pointer c_str() const noexcept {
        return tstr_buf(m_data);
    }

    const_pointer data() const noexcept {
        return tstr_buf(m_data);
    }

    const_iterator begin() const noexcept {
        return tstr_buf(m_data);
    }

    const_iterator cbegin() const noexcept {
        return begin();
    }

    const_iterator end() const noexcept {
        return tstr_buf(m_data) + tstr_len(m_data);
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

protected:
    friend struct string;

    struct TString m_data;

    friend string concat(string_view left, string_view right);
    friend string substr(string_view sv, std::size_t pos, std::size_t len);
};

struct string : public string_view {
    explicit string(struct TString m_data) : string_view(m_data) {}

    string(const char* value TH_NONNULL)
        : string(tstr_new(value, std::strlen(value))) {}

    string(const char* value TH_NONNULL, size_type size)
        : string(tstr_new(value, size)) {}

    string(std::initializer_list<char> value)
        : string(value.begin(), static_cast<uint32_t>(value.size())) {}

    string(std::string_view value)
        : string(value.data(), value.size()) {}

    string(std::string const &value)
        : string(value.data(), value.size()) {}

    // constructors
    string(string_view const& other)
        : string(tstr_dup(other.m_data)) {}

    string(string const& other)
        : string(tstr_dup(other.m_data)) {}

    string(string&& other) noexcept
        : string(other.m_data) {
        other.m_data.ptr = NULL;
    }

    // assignment
    string& operator=(string other) {
        std::swap(this->m_data, other.m_data);
        return *this;
    }

    // destructor
    ~string() {
        if (m_data.ptr != NULL) {
            tstr_drop(m_data);
        }
    }
};

inline string substr(string_view sv, std::size_t pos, std::size_t len) {
    return string(tstr_substr(sv.m_data, pos, len));
}

inline string concat(string_view left, string_view right) {
    return string(tstr_concat(left.m_data, right.m_data));
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
    // *result.ptr = '\0'; // std::to_chars does not write '\0' at the end of the buffer automatcally
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
    // *result.ptr = '\0'; // std::to_chars does not write '\0' at the end of the buffer automatcally
    return string{ buffer, static_cast<std::size_t>(result.ptr - buffer) };
}

template<typename T, std::enable_if_t<std::is_same_v<T, bool>, int> = 0>
string to_string(T value) {
    if (value) {
        return string{ "true", 4 };
    } else {
        return string{ "false", 5 };
    }
}

inline std::size_t hash_impl(adl_helper_t, string_view val) {
    return std::hash<std::string_view>{}(val);
}

inline bool same_impl(adl_helper_t, string_view lhs, string_view rhs) {
    return lhs == rhs;
}
}
