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
struct string;
struct string_view;

struct string {
public:
    // Using
    using value_type = char;
    using size_type = std::size_t;
    using const_reference = value_type const&;
    using const_pointer = value_type const*;
    using const_iterator = const_pointer;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    // Constructors
    string() noexcept : m_handle(nullptr) {}

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

    operator std::string_view() const noexcept {
        if (m_handle) {
            return { tstr_buf(m_handle), tstr_len(m_handle) };
        }
        return { "", 0 };
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
        if (m_handle) {
            tstr_drop(m_handle);
        }
        m_handle = nullptr;
    }

    // assignment
    string& operator=(string other) {
        // copy-and-swap idiom
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

private:
    explicit string(TString* other_handle)
        : m_handle(other_handle) {}

    template<typename cpp_t, typename abi_t>
    friend abi_t into_abi(cpp_t val);
    template<typename cpp_t, typename abi_t>
    friend cpp_t from_abi(abi_t val);

public:
    const_reference operator[](size_type pos) const {
        if (pos >= size()) {
            throw std::out_of_range("Index out of range");
        }
        return tstr_buf(m_handle)[pos];
    }

    // others
    bool empty() const noexcept {
        return m_handle == nullptr || tstr_len(m_handle) == 0;
    }

    size_type size() const noexcept {
        return m_handle ? tstr_len(m_handle) : 0;
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
        return m_handle ? tstr_buf(m_handle) : "";
    }

    const_pointer data() const noexcept {
        return c_str();
    }

    const_iterator begin() const noexcept {
        return m_handle ? tstr_buf(m_handle) : "";
    }

    const_iterator cbegin() const noexcept {
        return begin();
    }

    const_iterator end() const noexcept {
        return m_handle ? tstr_buf(m_handle) + tstr_len(m_handle) : "";
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
    friend class string_view;
    friend string concat(string_view left, string_view right);
    friend string substr(string_view sv, std::size_t pos, std::size_t len);

    TString* m_handle;
};

struct string_view {
    // Using
    using value_type = char;
    using size_type = std::size_t;
    using const_reference = value_type const&;
    using const_pointer = value_type const*;
    using const_iterator = const_pointer;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    // Constructors
    string_view() noexcept : m_handle(nullptr) {}

    string_view(const char* value TH_NONNULL)
        : m_handle(tstr_new_ref(value, strlen(value), &m_header)) {}

    string_view(const char* value TH_NONNULL, size_type size)
        : m_handle(tstr_new_ref(value, size, &m_header)) {}

    string_view(std::initializer_list<char> value)
        : string_view(value.begin(), static_cast<uint32_t>(value.size())) {}

    string_view(std::string_view value)
        : string_view(value.data(), value.size()) {}

    string_view(std::string const &value)
        : string_view(value.data(), value.size()) {}

    operator std::string_view() const noexcept {
        if (m_handle) {
            return { tstr_buf(m_handle), tstr_len(m_handle) };
        }
        return { "", 0 };
    }

    // copy/move constructor
    string_view(string_view const& other)
        : m_handle(other.m_handle) {}

    // convert from/to taihe::core::string
    string_view(string const& other)
        : m_handle(other.m_handle) {}

    operator string() const noexcept {
        return string(tstr_dup(m_handle));
    }

    // destructor
    ~string_view() {}

    // assignment
    string_view& operator=(string_view other) {
        // copy-and-swap idiom
        std::swap(this->m_handle, other.m_handle);
        std::swap(this->m_header, other.m_header);
        return *this;
    }

private:
    explicit string_view(TString* other_handle)
        : m_handle(other_handle) {}

    template<typename cpp_t, typename abi_t>
    friend abi_t into_abi(cpp_t val);
    template<typename cpp_t, typename abi_t>
    friend cpp_t from_abi(abi_t val);

public:
    const_reference operator[](size_type pos) const {
        if (pos >= size()) {
            throw std::out_of_range("Index out of range");
        }
        return tstr_buf(m_handle)[pos];
    }

    // others
    bool empty() const noexcept {
        return m_handle == nullptr || tstr_len(m_handle) == 0;
    }

    size_type size() const noexcept {
        return m_handle ? tstr_len(m_handle) : 0;
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
        return m_handle ? tstr_buf(m_handle) : "";
    }

    const_pointer data() const noexcept {
        return c_str();
    }

    const_iterator begin() const noexcept {
        return m_handle ? tstr_buf(m_handle) : "";
    }

    const_iterator cbegin() const noexcept {
        return begin();
    }

    const_iterator end() const noexcept {
        return m_handle ? tstr_buf(m_handle) + tstr_len(m_handle) : "";
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

    TString* m_handle;
    TString  m_header;
};


inline string substr(string_view sv, std::size_t pos, std::size_t len) {
    struct TString* result_handle = tstr_substr(sv.m_handle, pos, len);
    if (!result_handle) {
        return string();
    }
    string result;
    result.m_handle = result_handle;
    return result;
}

inline string concat(string_view left, string_view right) {
    struct TString* result_handle = tstr_concat(left.m_handle, right.m_handle);
    if (!result_handle) {
        return string();
    }
    string result;
    result.m_handle = result_handle;
    return result;
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

// returning from abi
template<> inline taihe::core::string from_abi(TString* _val) {
    TString* r_handle = _val;
    return taihe::core::string(r_handle);
}

// returning into abi
template<> inline TString* into_abi(taihe::core::string _val) {
    TString *r_handle = _val.m_handle;
    _val.m_handle = nullptr;
    return r_handle;
}

// passing argument from abi
template<> inline taihe::core::string_view from_abi(TString* _val) {
    TString* r_handle = _val;
    return taihe::core::string_view(_val);
}

// passing argument into abi
template<> inline TString* into_abi(taihe::core::string_view _val) {
    TString *r_handle = _val.m_handle;
    return r_handle;
}
}
