/*
 * Copyright (c) 2025-2026 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef TAIHE_STRING_HPP
#define TAIHE_STRING_HPP

#include <taihe/string.abi.h>
#include <taihe/common.hpp>

#include <algorithm>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace taihe {
struct common_string_view;
struct common_string;
struct string_view;
struct string;
struct u16string_view;
struct u16string;

enum class string_encoding { utf8, utf16, unknown };

struct common_string_view {
    using value_type = char;
    using size_type = std::size_t;
    using const_reference = value_type const &;
    using const_pointer = value_type const *;
    using const_iterator = const_pointer;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    explicit common_string_view(struct TString handle) : m_handle(handle)
    {
    }

    common_string_view(char const *value TH_NONNULL) : common_string_view(tstr_new_ref(value, std::strlen(value)))
    {
    }

    common_string_view(char const *value TH_NONNULL, size_type size) : common_string_view(tstr_new_ref(value, size))
    {
    }

    common_string_view(char16_t const *value TH_NONNULL, size_type size)
        : common_string_view(tstr_new_ref_utf16(reinterpret_cast<uint16_t const *>(value), size))
    {
    }

    common_string_view(std::initializer_list<char> value) : common_string_view(value.begin(), value.size())
    {
    }

    common_string_view(std::initializer_list<char16_t> value) : common_string_view(value.begin(), value.size())
    {
    }

    common_string_view(std::string_view value) : common_string_view(value.data(), value.size())
    {
    }

    common_string_view(std::string const &value) : common_string_view(value.data(), value.size())
    {
    }

    common_string_view(std::u16string_view value) : common_string_view(value.data(), value.size())
    {
    }

    common_string_view(std::u16string const &value) : common_string_view(value.data(), value.size())
    {
    }

    // methods
    bool empty() const noexcept
    {
        return tstr_len(m_handle) == 0;
    }

    bool is_utf8() const noexcept
    {
        return tstr_encoding(m_handle) == TSTRING_UTF8;
    }

    bool is_utf16() const noexcept
    {
        return tstr_encoding(m_handle) == TSTRING_UTF16;
    }

    [[nodiscard]]
    string_encoding encoding() const noexcept
    {
        switch (tstr_encoding(m_handle) & TSTRING_ENCODING_MASK) {
            case TSTRING_UTF8:
                return string_encoding::utf8;

            case TSTRING_UTF16:
                return string_encoding::utf16;

            default:
                return string_encoding::unknown;
        }
    }

    friend struct common_string;
    friend struct string_view;
    friend struct u16string_view;

protected:
    struct TString m_handle;
};

struct common_string : public common_string_view {
    explicit common_string(struct TString handle) : common_string_view(handle)
    {
    }

    common_string(char const *value TH_NONNULL) : common_string(tstr_new(value, std::strlen(value)))
    {
    }

    common_string(char const *value TH_NONNULL, size_type size) : common_string(tstr_new(value, size))
    {
    }

    common_string(char16_t const *value TH_NONNULL, size_type size)
        : common_string(tstr_new_utf16(reinterpret_cast<uint16_t const *>(value), size))
    {
    }

    common_string(std::initializer_list<char> value) : common_string(value.begin(), value.size())
    {
    }

    common_string(std::initializer_list<char16_t> value) : common_string(value.begin(), value.size())
    {
    }

    common_string(std::string_view value) : common_string(value.data(), value.size())
    {
    }

    common_string(std::string const &value) : common_string(value.data(), value.size())
    {
    }

    common_string(std::u16string_view value) : common_string(value.data(), value.size())
    {
    }

    common_string(std::u16string const &value) : common_string(value.data(), value.size())
    {
    }

    // constructors
    common_string(common_string_view const &other) : common_string(tstr_dup(other.m_handle))
    {
    }

    common_string(common_string const &other) : common_string(tstr_dup(other.m_handle))
    {
    }

    common_string(common_string &&other) noexcept : common_string(other.m_handle)
    {
        other.m_handle.pstrinfo = nullptr;
    }

    // assignment
    common_string &operator=(common_string other)
    {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    // destructor
    ~common_string()
    {
        if (m_handle.pstrinfo != nullptr) {
            tstr_drop(m_handle);
        }
    }

    friend struct string;
    friend struct u16string;
};

struct string_view {
    using value_type = char;
    using size_type = std::size_t;
    using const_reference = value_type const &;
    using const_pointer = value_type const *;
    using const_iterator = const_pointer;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    explicit string_view(struct TString handle) : m_handle(handle)
    {
    }

    string_view(char const *value TH_NONNULL) : string_view(tstr_new_ref(value, std::strlen(value)))
    {
    }

    string_view(char const *value TH_NONNULL, size_type size) : string_view(tstr_new_ref(value, size))
    {
    }

    string_view(std::initializer_list<char> value) : string_view(value.begin(), value.size())
    {
    }

    string_view(std::string_view value) : string_view(value.data(), value.size())
    {
    }

    string_view(std::string const &value) : string_view(value.data(), value.size())
    {
    }

    // Explicit downcast
    explicit string_view(common_string_view value)
    {
        if (!value.is_utf8()) {
            TH_THROW(std::invalid_argument, "string_view requires UTF-8 common_string_view");
        }

        m_handle = value.m_handle;
    }

    // Implicit upcast
    operator common_string_view() const noexcept
    {
        return common_string_view(m_handle);
    }

    operator common_string() const noexcept
    {
        return common_string(tstr_dup(m_handle));
    }

    operator std::string_view() const noexcept
    {
        return {tstr_buf(m_handle), tstr_len(m_handle)};
    }

    // methods
    const_reference operator[](size_type pos) const
    {
        if (pos >= size()) {
            TH_THROW(std::out_of_range, "Index out of range");
        }
        return tstr_buf(m_handle)[pos];
    }

    bool empty() const noexcept
    {
        return tstr_len(m_handle) == 0;
    }

    size_type size() const noexcept
    {
        return tstr_len(m_handle);
    }

    const_reference front() const
    {
        if (empty()) {
            TH_THROW(std::out_of_range, "Empty string");
        }
        return tstr_buf(m_handle)[0];
    }

    const_reference back() const
    {
        if (empty()) {
            TH_THROW(std::out_of_range, "Empty string");
        }
        return tstr_buf(m_handle)[size() - 1];
    }

    const_pointer c_str() const noexcept
    {
        return tstr_buf(m_handle);
    }

    const_pointer data() const noexcept
    {
        return tstr_buf(m_handle);
    }

    const_iterator begin() const noexcept
    {
        return tstr_buf(m_handle);
    }

    const_iterator cbegin() const noexcept
    {
        return begin();
    }

    const_iterator end() const noexcept
    {
        return tstr_buf(m_handle) + tstr_len(m_handle);
    }

    const_iterator cend() const noexcept
    {
        return end();
    }

    const_reverse_iterator rbegin() const noexcept
    {
        return const_reverse_iterator(end());
    }

    const_reverse_iterator crbegin() const noexcept
    {
        return rbegin();
    }

    const_reverse_iterator rend() const noexcept
    {
        return const_reverse_iterator(begin());
    }

    const_reverse_iterator crend() const noexcept
    {
        return rend();
    }

    friend struct string;

    friend string concat(std::initializer_list<string_view> sv_list);
    friend string_view substr(string_view sv, std::size_t pos, std::size_t len);
    friend string operator+(string_view left, string_view right);
    string_view substr(std::size_t pos, std::size_t len) const;

protected:
    struct TString m_handle;
};

struct string : public string_view {
    explicit string(struct TString handle) : string_view(handle)
    {
    }

    string(char const *value TH_NONNULL) : string(tstr_new(value, std::strlen(value)))
    {
    }

    string(char const *value TH_NONNULL, size_type size) : string(tstr_new(value, size))
    {
    }

    string(std::initializer_list<char> value) : string(value.begin(), value.size())
    {
    }

    string(std::string_view value) : string(value.data(), value.size())
    {
    }

    string(std::string const &value) : string(value.data(), value.size())
    {
    }

    // constructors
    string(string_view const &other) : string(tstr_dup(other.m_handle))
    {
    }

    string(string const &other) : string(tstr_dup(other.m_handle))
    {
    }

    string(string &&other) noexcept : string(other.m_handle)
    {
        other.m_handle.pstrinfo = nullptr;
    }

    // Explicit downcast
    static TString move_as_utf8_handle(common_string &&other)
    {
        if (other.is_utf8()) {
            TString handle = other.m_handle;
            other.m_handle.pstrinfo = nullptr;
            return handle;
        } else if (other.is_utf16()) {
            TString handle = tstr_utf16_to_utf8(other.m_handle);
            return handle;
        }

        TH_THROW(std::invalid_argument, "unknown encoding in common_string");

#if defined(__GNUC__) || defined(__clang__)
        __builtin_unreachable();
#elif defined(_MSC_VER)
        __assume(false);
#endif
    }

    explicit string(common_string other) : string_view(move_as_utf8_handle(std::move(other)))
    {
    }

    // Implicit upcast
    operator common_string() const & noexcept
    {
        return common_string(tstr_dup(m_handle));
    }

    operator common_string() && noexcept
    {
        common_string str = common_string(m_handle);
        m_handle.pstrinfo = nullptr;
        m_handle.ptr = nullptr;
        return str;
    }

    // assignment
    string &operator=(string other)
    {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    // destructor
    ~string()
    {
        if (m_handle.pstrinfo != nullptr) {
            tstr_drop(m_handle);
        }
    }

    string &operator+=(string_view other);
};

struct u16string_view {
    using value_type = char16_t;
    using size_type = std::size_t;
    using const_reference = value_type const &;
    using const_pointer = value_type const *;
    using const_iterator = const_pointer;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    explicit u16string_view(struct TString handle) : m_handle(handle)
    {
    }

    u16string_view(char16_t const *value TH_NONNULL, size_type size)
        : u16string_view(tstr_new_utf16(reinterpret_cast<uint16_t const *>(value), size))
    {
    }

    u16string_view(std::initializer_list<char16_t> value) : u16string_view(value.begin(), value.size())
    {
    }

    u16string_view(std::u16string_view value) : u16string_view(value.data(), value.size())
    {
    }

    u16string_view(std::u16string const &value) : u16string_view(value.data(), value.size())
    {
    }

    // Explicit downcast
    explicit u16string_view(common_string_view value)
    {
        if (!value.is_utf16()) {
            TH_THROW(std::invalid_argument, "string_view requires UTF-16 common_string_view");
        }

        m_handle = value.m_handle;
    }

    // Implicit upcast
    operator common_string_view() const noexcept
    {
        return common_string_view(m_handle);
    }

    operator common_string() const noexcept
    {
        return common_string(tstr_dup(m_handle));
    }

    operator std::u16string_view() const noexcept
    {
        return {reinterpret_cast<char16_t const *>(tstr_buf(m_handle)), tstr_len(m_handle) / sizeof(uint16_t)};
    }

    // methods
    const_reference operator[](size_type pos) const
    {
        if (pos >= size()) {
            TH_THROW(std::out_of_range, "Index out of range");
        }
        return reinterpret_cast<char16_t const *>(tstr_buf(m_handle))[pos];
    }

    bool empty() const noexcept
    {
        return tstr_len(m_handle) == 0;
    }

    size_type size() const noexcept
    {
        return tstr_len(m_handle) / sizeof(uint16_t);
    }

    const_reference front() const
    {
        if (empty()) {
            TH_THROW(std::out_of_range, "Empty string");
        }
        return reinterpret_cast<char16_t const *>(tstr_buf(m_handle))[0];
    }

    const_reference back() const
    {
        if (empty()) {
            TH_THROW(std::out_of_range, "Empty string");
        }
        return reinterpret_cast<char16_t const *>(tstr_buf(m_handle))[size() - 1];
    }

    const_pointer c_str() const noexcept
    {
        return reinterpret_cast<char16_t const *>(tstr_buf(m_handle));
    }

    const_pointer data() const noexcept
    {
        return reinterpret_cast<char16_t const *>(tstr_buf(m_handle));
    }

    const_iterator begin() const noexcept
    {
        return reinterpret_cast<char16_t const *>(tstr_buf(m_handle));
    }

    const_iterator cbegin() const noexcept
    {
        return begin();
    }

    const_iterator end() const noexcept
    {
        return reinterpret_cast<char16_t const *>(tstr_buf(m_handle)) + tstr_len(m_handle);
    }

    const_iterator cend() const noexcept
    {
        return end();
    }

    const_reverse_iterator rbegin() const noexcept
    {
        return const_reverse_iterator(end());
    }

    const_reverse_iterator crbegin() const noexcept
    {
        return rbegin();
    }

    const_reverse_iterator rend() const noexcept
    {
        return const_reverse_iterator(begin());
    }

    const_reverse_iterator crend() const noexcept
    {
        return rend();
    }

    friend struct u16string;

    friend u16string concat(std::initializer_list<u16string_view> sv_list);
    friend u16string_view substr(u16string_view sv, std::size_t pos, std::size_t len);
    friend u16string operator+(u16string_view left, u16string_view right);
    u16string_view substr(std::size_t pos, std::size_t len) const;

protected:
    struct TString m_handle;
};

struct u16string : public u16string_view {
    explicit u16string(struct TString handle) : u16string_view(handle)
    {
    }

    u16string(char16_t const *value TH_NONNULL, size_type size)
        : u16string(tstr_new_utf16(reinterpret_cast<uint16_t const *>(value), size))
    {
    }

    u16string(std::initializer_list<char16_t> value) : u16string(value.begin(), value.size())
    {
    }

    u16string(std::u16string_view value) : u16string(value.data(), value.size())
    {
    }

    u16string(std::u16string const &value) : u16string(value.data(), value.size())
    {
    }

    // constructors
    u16string(u16string_view const &other) : u16string(tstr_dup(other.m_handle))
    {
    }

    u16string(u16string const &other) : u16string(tstr_dup(other.m_handle))
    {
    }

    u16string(u16string &&other) noexcept : u16string(other.m_handle)
    {
        other.m_handle.pstrinfo = nullptr;
    }

    // Explicit downcast
    static TString move_as_utf16_handle(common_string &&other)
    {
        if (other.is_utf16()) {
            TString handle = other.m_handle;
            other.m_handle.pstrinfo = nullptr;
            return handle;
        } else if (other.is_utf8()) {
            TString handle = tstr_utf8_to_utf16(other.m_handle);
            return handle;
        }

        TH_THROW(std::invalid_argument, "unknown encoding in common_string");

#if defined(__GNUC__) || defined(__clang__)
        __builtin_unreachable();
#elif defined(_MSC_VER)
        __assume(false);
#endif
    }

    explicit u16string(common_string other) : u16string_view(move_as_utf16_handle(std::move(other)))
    {
    }

    // Implicit upcast
    operator common_string() const & noexcept
    {
        return common_string(m_handle);
    }

    operator common_string() && noexcept
    {
        common_string str = common_string(m_handle);
        m_handle.pstrinfo = nullptr;
        m_handle.ptr = nullptr;
        return str;
    }

    // assignment
    u16string &operator=(u16string other)
    {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    // destructor
    ~u16string()
    {
        if (m_handle.pstrinfo != nullptr) {
            tstr_drop(m_handle);
        }
    }

    u16string &operator+=(u16string_view other);
};

inline string concat(std::initializer_list<string_view> sv_list)
{
    static_assert(alignof(string_view) == alignof(struct TString));
    return string(tstr_concat(sv_list.size(), reinterpret_cast<struct TString const *>(sv_list.begin())));
}

inline string operator+(string_view left, string_view right)
{
    return concat({left, right});
}

inline string &string::operator+=(string_view other)
{
    return *this = *this + other;
}

inline string_view substr(string_view sv, std::size_t pos, std::size_t len)
{
    return string_view(tstr_substr(sv.m_handle, pos, len));
}

inline string_view string_view::substr(std::size_t pos, std::size_t len) const
{
    return string_view(tstr_substr(this->m_handle, pos, len));
}

inline bool operator==(string_view lhs, string_view rhs)
{
    return std::string_view(lhs) == std::string_view(rhs);
}

inline bool operator!=(string_view lhs, string_view rhs)
{
    return std::string_view(lhs) != std::string_view(rhs);
}

inline bool operator<(string_view lhs, string_view rhs)
{
    return std::string_view(lhs) < std::string_view(rhs);
}

inline bool operator>(string_view lhs, string_view rhs)
{
    return std::string_view(lhs) > std::string_view(rhs);
}

inline bool operator<=(string_view lhs, string_view rhs)
{
    return std::string_view(lhs) <= std::string_view(rhs);
}

inline bool operator>=(string_view lhs, string_view rhs)
{
    return std::string_view(lhs) >= std::string_view(rhs);
}

inline std::ostream &operator<<(std::ostream &os, string_view sv)
{
    return os << std::string_view(sv);
}

inline u16string concat(std::initializer_list<u16string_view> sv_list)
{
    static_assert(alignof(string_view) == alignof(struct TString));
    return u16string(tstr_concat_utf16(sv_list.size(), reinterpret_cast<struct TString const *>(sv_list.begin())));
}

inline u16string operator+(u16string_view left, u16string_view right)
{
    return concat({left, right});
}

inline u16string &u16string::operator+=(u16string_view other)
{
    return *this = *this + other;
}

inline u16string_view substr(u16string_view sv, std::size_t pos, std::size_t len)
{
    return u16string_view(tstr_substr_utf16(sv.m_handle, pos, len));
}

inline u16string_view u16string_view::substr(std::size_t pos, std::size_t len) const
{
    return u16string_view(tstr_substr_utf16(this->m_handle, pos, len));
}

inline bool operator==(u16string_view lhs, u16string_view rhs)
{
    return std::u16string_view(lhs) == std::u16string_view(rhs);
}

inline bool operator!=(u16string_view lhs, u16string_view rhs)
{
    return std::u16string_view(lhs) != std::u16string_view(rhs);
}

inline bool operator<(u16string_view lhs, u16string_view rhs)
{
    return std::u16string_view(lhs) < std::u16string_view(rhs);
}

inline bool operator>(u16string_view lhs, u16string_view rhs)
{
    return std::u16string_view(lhs) > std::u16string_view(rhs);
}

inline bool operator<=(u16string_view lhs, u16string_view rhs)
{
    return std::u16string_view(lhs) <= std::u16string_view(rhs);
}

inline bool operator>=(u16string_view lhs, u16string_view rhs)
{
    return std::u16string_view(lhs) >= std::u16string_view(rhs);
}

template<typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
inline string to_string(T value)
{
    char buffer[32];
    std::to_chars_result result = std::to_chars(std::begin(buffer), std::end(buffer), value);
    if (result.ec != std::errc {}) {
        TH_THROW(std::runtime_error, "Conversion to char failed");
    }
    // buffer automatcally
    return string {buffer, static_cast<std::size_t>(result.ptr - buffer)};
}

template<typename T, std::enable_if_t<std::is_floating_point_v<T>, int> = 0>
inline string to_string(T value)
{
    char buffer[32];
    std::to_chars_result result =
        std::to_chars(std::begin(buffer), std::end(buffer), value, std::chars_format::general);
    if (result.ec != std::errc {}) {
        TH_THROW(std::runtime_error, "Conversion to char failed");
    }
    // buffer automatcally
    return string {buffer, static_cast<std::size_t>(result.ptr - buffer)};
}

template<typename T, std::enable_if_t<std::is_same_v<T, bool>, int> = 0>
string to_string(T value)
{
    if (value) {
        return string {"true", 4};
    } else {
        return string {"false", 5};
    }
}

template<>
struct as_abi<common_string_view> {
    using type = TString;
};

template<>
struct as_abi<common_string> {
    using type = TString;
};

template<>
struct as_param<common_string> {
    using type = common_string_view;
};

template<>
struct as_abi<string_view> {
    using type = TString;
};

template<>
struct as_abi<string> {
    using type = TString;
};

template<>
struct as_param<string> {
    using type = string_view;
};

template<>
struct as_abi<u16string_view> {
    using type = TString;
};

template<>
struct as_abi<u16string> {
    using type = TString;
};

template<>
struct as_param<u16string> {
    using type = u16string_view;
};
}  // namespace taihe

template<>
struct std::hash<taihe::string> {
    std::size_t operator()(taihe::string_view sv) const noexcept
    {
        return std::hash<std::string_view>()(std::string_view(sv));
    }
};

#endif  // TAIHE_STRING_HPP
