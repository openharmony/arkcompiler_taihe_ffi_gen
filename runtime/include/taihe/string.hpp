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
#include <taihe/string_builder.h>
#include <initializer_list>
#include <taihe/common.hpp>

#include <algorithm>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace taihe {
struct common_string_view;
struct common_string;
struct copy_cached_common_string_view;
struct acquire_cached_common_string_view;

struct string_view;
struct string;
struct copy_cached_string_view;
struct acquire_cached_string_view;
struct string_builder;

struct u16string_view;
struct u16string;
struct copy_cached_u16string_view;
struct acquire_cached_u16string_view;
struct u16string_builder;

enum class string_encoding { utf8, utf16, unknown };
}  // namespace taihe

namespace taihe {
struct common_string_view {
    common_string_view(char const *value TH_NONNULL, std::size_t size)
        : common_string_view(tstr_new_copyable_borrowed_utf8(value, size, nullptr))
    {
    }

    common_string_view(char const *value TH_NONNULL) : common_string_view(value, std::char_traits<char>::length(value))
    {
    }

    common_string_view(static_flag_t, char const *value TH_NONNULL, std::size_t size)
        : common_string_view(tstr_new_static_utf8(value, size))
    {
    }

    common_string_view(static_flag_t, char const *value TH_NONNULL)
        : common_string_view(static_flag, value, std::char_traits<char>::length(value))
    {
    }

    common_string_view(char16_t const *value TH_NONNULL, std::size_t size)
        : common_string_view(tstr_new_copyable_borrowed_utf16(reinterpret_cast<uint16_t const *>(value), size, nullptr))
    {
    }

    common_string_view(char16_t const *value TH_NONNULL)
        : common_string_view(value, std::char_traits<char16_t>::length(value))
    {
    }

    common_string_view(static_flag_t, char16_t const *value TH_NONNULL, std::size_t size)
        : common_string_view(tstr_new_static_utf16(reinterpret_cast<uint16_t const *>(value), size))
    {
    }

    common_string_view(static_flag_t, char16_t const *value TH_NONNULL)
        : common_string_view(static_flag, value, std::char_traits<char16_t>::length(value))
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
        return tstr_is_empty(m_handle);
    }

    bool is_utf8() const noexcept
    {
        return tstr_encoding(m_handle) == TSTRING_ENCODING_UTF8;
    }

    bool is_utf16() const noexcept
    {
        return tstr_encoding(m_handle) == TSTRING_ENCODING_UTF16;
    }

    [[nodiscard]]
    string_encoding encoding() const noexcept
    {
        switch (tstr_encoding(m_handle)) {
            case TSTRING_ENCODING_UTF8:
                return string_encoding::utf8;

            case TSTRING_ENCODING_UTF16:
                return string_encoding::utf16;

            default:
                return string_encoding::unknown;
        }
    }

    friend struct common_string;
    friend struct string_view;
    friend struct string;
    friend struct u16string_view;
    friend struct u16string;

protected:
    struct TString m_handle;

    explicit common_string_view(struct TString handle) : m_handle(handle)
    {
    }
};

struct common_string : public common_string_view {
    common_string(char const *value TH_NONNULL, std::size_t size) : common_string(tstr_new_copied_utf8(value, size))
    {
    }

    common_string(char const *value TH_NONNULL) : common_string(value, std::char_traits<char>::length(value))
    {
    }

    common_string(static_flag_t, char const *value TH_NONNULL, std::size_t size)
        : common_string(tstr_new_static_utf8(value, size))
    {
    }

    common_string(static_flag_t, char const *value TH_NONNULL)
        : common_string(static_flag, value, std::char_traits<char>::length(value))
    {
    }

    common_string(char const *value TH_NONNULL, std::size_t size, TStringGlobalRefContext ctx)
        : common_string(tstr_new_acquired_utf8(value, size, ctx))
    {
    }

    common_string(char16_t const *value TH_NONNULL, std::size_t size)
        : common_string(tstr_new_copied_utf16(reinterpret_cast<uint16_t const *>(value), size))
    {
    }

    common_string(char16_t const *value TH_NONNULL) : common_string(value, std::char_traits<char16_t>::length(value))
    {
    }

    common_string(static_flag_t, char16_t const *value TH_NONNULL, std::size_t size)
        : common_string(tstr_new_static_utf16(reinterpret_cast<uint16_t const *>(value), size))
    {
    }

    common_string(static_flag_t, char16_t const *value TH_NONNULL)
        : common_string(static_flag, value, std::char_traits<char16_t>::length(value))
    {
    }

    common_string(char16_t const *value TH_NONNULL, std::size_t size, TStringGlobalRefContext ctx)
        : common_string(tstr_new_acquired_utf16(reinterpret_cast<uint16_t const *>(value), size, ctx))
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

    common_string(common_string &&other) noexcept : common_string(std::exchange(other.m_handle, tstr_new_invalid()))
    {
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
        tstr_drop(m_handle);
    }

    friend struct string_view;
    friend struct string;
    friend struct u16string_view;
    friend struct u16string;

private:
    explicit common_string(struct TString handle) : common_string_view(handle)
    {
    }
};

struct copy_cached_common_string_view : public common_string_view {
    copy_cached_common_string_view(char const *value TH_NONNULL, std::size_t size)
        : copy_cached_common_string_view([value, size](TStringCopyCache *cache) {
            return tstr_new_copyable_borrowed_utf8(value, size, cache);
        })
    {
    }

    copy_cached_common_string_view(char const *value TH_NONNULL)
        : copy_cached_common_string_view(value, std::char_traits<char>::length(value))
    {
    }

    copy_cached_common_string_view(char16_t const *value TH_NONNULL, std::size_t size)
        : copy_cached_common_string_view([value, size](TStringCopyCache *cache) {
            return tstr_new_copyable_borrowed_utf16(reinterpret_cast<uint16_t const *>(value), size, cache);
        })
    {
    }

    copy_cached_common_string_view(char16_t const *value TH_NONNULL)
        : copy_cached_common_string_view(value, std::char_traits<char16_t>::length(value))
    {
    }

    copy_cached_common_string_view(copy_cached_common_string_view const &) = delete;
    copy_cached_common_string_view(copy_cached_common_string_view &&) = delete;
    copy_cached_common_string_view &operator=(copy_cached_common_string_view const &) = delete;
    copy_cached_common_string_view &operator=(copy_cached_common_string_view &&) = delete;

    ~copy_cached_common_string_view()
    {
        tstr_copy_cache_drop(&m_cache);
    }

private:
    TStringCopyCache m_cache;

    template<typename Initializer>
    explicit copy_cached_common_string_view(Initializer &&initializer)
        : common_string_view(std::forward<Initializer>(initializer)(&m_cache))
    {
    }
};

struct acquire_cached_common_string_view : public common_string_view {
    acquire_cached_common_string_view(char const *value TH_NONNULL, std::size_t size, TStringLocalRefContext ctx)
        : acquire_cached_common_string_view([value, size, ctx](TStringAcquireCache *cache) {
            return tstr_new_acquirable_borrowed_utf8(value, size, cache, ctx);
        })
    {
    }

    acquire_cached_common_string_view(char16_t const *value TH_NONNULL, std::size_t size, TStringLocalRefContext ctx)
        : acquire_cached_common_string_view([value, size, ctx](TStringAcquireCache *cache) {
            return tstr_new_acquirable_borrowed_utf16(reinterpret_cast<uint16_t const *>(value), size, cache, ctx);
        })
    {
    }

    acquire_cached_common_string_view(acquire_cached_common_string_view const &) = delete;
    acquire_cached_common_string_view(acquire_cached_common_string_view &&) = delete;
    acquire_cached_common_string_view &operator=(acquire_cached_common_string_view const &) = delete;
    acquire_cached_common_string_view &operator=(acquire_cached_common_string_view &&) = delete;

    ~acquire_cached_common_string_view()
    {
        tstr_acquire_cache_drop(&m_cache);
    }

private:
    TStringAcquireCache m_cache;

    template<typename Initializer>
    explicit acquire_cached_common_string_view(Initializer &&initializer)
        : common_string_view(std::forward<Initializer>(initializer)(&m_cache))
    {
    }
};

struct string_view {
    using value_type = char;
    using size_type = std::size_t;
    using const_reference = value_type const &;
    using const_pointer = value_type const *;
    using const_iterator = const_pointer;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    string_view(char const *value TH_NONNULL, size_type size)
        : string_view(tstr_new_copyable_borrowed_utf8(value, size, nullptr))
    {
    }

    string_view(char const *value TH_NONNULL) : string_view(value, std::char_traits<char>::length(value))
    {
    }

    string_view(static_flag_t, char const *value TH_NONNULL, size_type size)
        : string_view(tstr_new_static_utf8(value, size))
    {
    }

    string_view(static_flag_t, char const *value TH_NONNULL)
        : string_view(static_flag, value, std::char_traits<char>::length(value))
    {
    }

    string_view() : string_view(static_flag, "", 0)
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

    operator common_string() const
    {
        return common_string(tstr_dup(m_handle));
    }

    operator std::string_view() const noexcept
    {
        return {tstr_buf_utf8(m_handle), tstr_len_utf8(m_handle)};
    }

    // methods
    const_reference operator[](size_type pos) const
    {
        return tstr_buf_utf8(m_handle)[pos];
    }

    const_reference at(size_type pos) const
    {
        if (pos >= size()) {
            TH_THROW(std::out_of_range, "Index out of range");
        }
        return tstr_buf_utf8(m_handle)[pos];
    }

    bool empty() const noexcept
    {
        return tstr_is_empty(m_handle);
    }

    size_type size() const noexcept
    {
        return tstr_len_utf8(m_handle);
    }

    const_reference front() const
    {
        if (empty()) {
            TH_THROW(std::out_of_range, "Empty string");
        }
        return tstr_buf_utf8(m_handle)[0];
    }

    const_reference back() const
    {
        if (empty()) {
            TH_THROW(std::out_of_range, "Empty string");
        }
        return tstr_buf_utf8(m_handle)[size() - 1];
    }

    // To be deprecated
    const_pointer c_str() const noexcept
    {
        return tstr_buf_utf8(m_handle);
    }

    const_pointer data() const noexcept
    {
        return tstr_buf_utf8(m_handle);
    }

    const_iterator begin() const noexcept
    {
        return tstr_buf_utf8(m_handle);
    }

    const_iterator cbegin() const noexcept
    {
        return begin();
    }

    const_iterator end() const noexcept
    {
        return tstr_buf_utf8(m_handle) + tstr_len_utf8(m_handle);
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
    friend struct copy_cached_string_view;

    string_view substr(std::size_t pos, std::size_t len = -1) const;

protected:
    struct TString m_handle;

    explicit string_view(struct TString handle) : m_handle(handle)
    {
    }
};

struct string : public string_view {
    string(char const *value TH_NONNULL, size_type size) : string(tstr_new_copied_utf8(value, size))
    {
    }

    string(char const *value TH_NONNULL) : string(value, std::char_traits<char>::length(value))
    {
    }

    string(static_flag_t, char const *value TH_NONNULL, size_type size) : string(tstr_new_static_utf8(value, size))
    {
    }

    string(static_flag_t, char const *value TH_NONNULL)
        : string(static_flag, value, std::char_traits<char>::length(value))
    {
    }

    string() : string(static_flag, "", 0)
    {
    }

    string(char const *value TH_NONNULL, size_type size, TStringGlobalRefContext ctx)
        : string(tstr_new_acquired_utf8(value, size, ctx))
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

    string(string &&other) noexcept : string(std::exchange(other.m_handle, tstr_new_invalid()))
    {
    }

    // Explicit downcast
    explicit string(common_string_view other) : string(tstr_dup_as_utf8(other.m_handle))
    {
    }

    explicit string(char16_t const *value TH_NONNULL, size_type size) : string(common_string_view(value, size))
    {
    }

    explicit string(char16_t const *value TH_NONNULL) : string(value, std::char_traits<char16_t>::length(value))
    {
    }

    // Implicit upcast
    operator common_string_view() const & noexcept
    {
        return common_string_view(m_handle);
    }

    operator common_string() const & noexcept
    {
        return common_string(tstr_dup(m_handle));
    }

    operator common_string() && noexcept
    {
        common_string str = common_string(m_handle);
        m_handle = tstr_new_invalid();
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
        tstr_drop(m_handle);
    }

    friend struct string_builder;
    template<typename Initializer>
    static string initialize(size_type capacity, Initializer &&initializer);

    friend string concat(std::initializer_list<string_view> sv_list);
    static string concat(std::initializer_list<common_string_view> sv_list);
    string &operator+=(common_string_view other);

private:
    explicit string(struct TString handle) : string_view(handle)
    {
    }
};

struct copy_cached_string_view : public string_view {
    copy_cached_string_view(char const *value TH_NONNULL, size_type size)
        : copy_cached_string_view([value, size](TStringCopyCache *cache) {
            return tstr_new_copyable_borrowed_utf8(value, size, cache);
        })
    {
    }

    copy_cached_string_view(char const *value TH_NONNULL)
        : copy_cached_string_view(value, std::char_traits<char>::length(value))
    {
    }

    copy_cached_string_view(copy_cached_string_view const &) = delete;
    copy_cached_string_view(copy_cached_string_view &&) = delete;
    copy_cached_string_view &operator=(copy_cached_string_view const &) = delete;
    copy_cached_string_view &operator=(copy_cached_string_view &&) = delete;

    ~copy_cached_string_view()
    {
        tstr_copy_cache_drop(&m_cache);
    }

    static copy_cached_string_view substr(string_view str, std::size_t pos, std::size_t len = -1);

private:
    TStringCopyCache m_cache;

    template<typename Initializer>
    explicit copy_cached_string_view(Initializer &&initializer)
        : string_view(std::forward<Initializer>(initializer)(&m_cache))
    {
    }
};

struct acquire_cached_string_view : public string_view {
    acquire_cached_string_view(char const *value TH_NONNULL, size_type size, TStringLocalRefContext ctx)
        : acquire_cached_string_view([value, size, ctx](TStringAcquireCache *cache) {
            return tstr_new_acquirable_borrowed_utf8(value, size, cache, ctx);
        })
    {
    }

    acquire_cached_string_view(acquire_cached_string_view const &) = delete;
    acquire_cached_string_view(acquire_cached_string_view &&) = delete;
    acquire_cached_string_view &operator=(acquire_cached_string_view const &) = delete;
    acquire_cached_string_view &operator=(acquire_cached_string_view &&) = delete;

    ~acquire_cached_string_view()
    {
        tstr_acquire_cache_drop(&m_cache);
    }

private:
    TStringAcquireCache m_cache;

    template<typename Initializer>
    explicit acquire_cached_string_view(Initializer &&initializer)
        : string_view(std::forward<Initializer>(initializer)(&m_cache))
    {
    }
};

struct string_builder {
    using value_type = char;
    using size_type = std::size_t;
    using reference = value_type &;
    using pointer = value_type *;
    using const_reference = value_type const &;
    using const_pointer = value_type const *;

    explicit string_builder(size_type capacity) : string_builder(tstr_builder_new_utf8(capacity))
    {
    }

    ~string_builder()
    {
        tstr_builder_drop(m_builder);
    }

    string_builder(string_builder const &) = delete;

    string_builder(string_builder &&other) noexcept
        : m_builder(std::exchange(other.m_builder, tstr_builder_new_invalid()))
    {
    }

    string_builder &operator=(string_builder other)
    {
        std::swap(this->m_builder, other.m_builder);
        return *this;
    }

    pointer data() noexcept
    {
        return tstr_builder_mut_buf_utf8(m_builder);
    }

    const_pointer data() const noexcept
    {
        return tstr_builder_buf_utf8(m_builder);
    }

    reference operator[](size_type pos) noexcept
    {
        return tstr_builder_mut_buf_utf8(m_builder)[pos];
    }

    const_reference operator[](size_type pos) const noexcept
    {
        return tstr_builder_buf_utf8(m_builder)[pos];
    }

    size_type capacity() const noexcept
    {
        return tstr_builder_cap_utf8(m_builder);
    }

    bool reallocate(size_type capacity, size_type initialized_length = -1)
    {
        return tstr_builder_reallocate_utf8(&m_builder, capacity, initialized_length);
    }

    string finish(size_type length) &&
    {
        string result(tstr_builder_finish_utf8(m_builder, length));
        m_builder = tstr_builder_new_invalid();
        return result;
    }

private:
    struct TStringBuilder m_builder;

    explicit string_builder(struct TStringBuilder builder) : m_builder(builder)
    {
    }
};

template<typename Initializer>
string string::initialize(size_type capacity, Initializer &&initializer)
{
    string_builder builder(capacity);
    char *buf = builder.data();
    char *end = std::forward<Initializer>(initializer)(buf);
    return std::move(builder).finish(end - buf);
}

inline string concat(std::initializer_list<string_view> sv_list)
{
    static_assert(alignof(string_view) == alignof(struct TString));
    return string(tstr_concat_as_utf8(sv_list.size(), reinterpret_cast<struct TString const *>(sv_list.begin())));
}

inline string string::concat(std::initializer_list<common_string_view> sv_list)
{
    static_assert(alignof(common_string_view) == alignof(struct TString));
    return string(tstr_concat_as_utf8(sv_list.size(), reinterpret_cast<struct TString const *>(sv_list.begin())));
}

inline string operator+(string_view left, string_view right)
{
    return concat({left, right});
}

inline string &string::operator+=(common_string_view other)
{
    return *this = string::concat({*this, other});
}

inline string_view string_view::substr(std::size_t pos, std::size_t len) const
{
    return string_view(tstr_substr_utf8(this->m_handle, pos, len, nullptr));
}

inline copy_cached_string_view copy_cached_string_view::substr(string_view sv, std::size_t pos, std::size_t len)
{
    return copy_cached_string_view([pos, len, sv](TStringCopyCache *cache) {
        return tstr_substr_utf8(sv.m_handle, pos, len, cache);
    });
}

inline namespace literals {
inline taihe::string_view operator""_tsv(char const *value, size_t size)
{
    return taihe::string_view(static_flag, value, size);
}

inline taihe::string operator""_ts(char const *value, size_t size)
{
    return taihe::string(static_flag, value, size);
}
}  // namespace literals

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
}  // namespace taihe

template<>
struct std::hash<taihe::string> {
    std::size_t operator()(taihe::string_view sv) const noexcept
    {
        return std::hash<std::string_view>()(std::string_view(sv));
    }
};

namespace taihe {
struct u16string_view {
    using value_type = char16_t;
    using size_type = std::size_t;
    using const_reference = value_type const &;
    using const_pointer = value_type const *;
    using const_iterator = const_pointer;
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    u16string_view(char16_t const *value TH_NONNULL, size_type size)
        : u16string_view(tstr_new_copyable_borrowed_utf16(reinterpret_cast<uint16_t const *>(value), size, nullptr))
    {
    }

    u16string_view(char16_t const *value TH_NONNULL) : u16string_view(value, std::char_traits<char16_t>::length(value))
    {
    }

    u16string_view(static_flag_t, char16_t const *value TH_NONNULL, size_type size)
        : u16string_view(tstr_new_static_utf16(reinterpret_cast<uint16_t const *>(value), size))
    {
    }

    u16string_view(static_flag_t, char16_t const *value TH_NONNULL)
        : u16string_view(static_flag, value, std::char_traits<char16_t>::length(value))
    {
    }

    u16string_view() : u16string_view(static_flag, u"", 0)
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
            TH_THROW(std::invalid_argument, "u16string_view requires UTF-16 common_string_view");
        }

        m_handle = value.m_handle;
    }

    // Implicit upcast
    operator common_string_view() const noexcept
    {
        return common_string_view(m_handle);
    }

    operator common_string() const
    {
        return common_string(tstr_dup(m_handle));
    }

    operator std::u16string_view() const noexcept
    {
        return {reinterpret_cast<char16_t const *>(tstr_buf_utf16(m_handle)), tstr_len_utf16(m_handle)};
    }

    // methods
    const_reference operator[](size_type pos) const
    {
        return reinterpret_cast<char16_t const *>(tstr_buf_utf16(m_handle))[pos];
    }

    const_reference at(size_type pos) const
    {
        if (pos >= size()) {
            TH_THROW(std::out_of_range, "Index out of range");
        }
        return reinterpret_cast<char16_t const *>(tstr_buf_utf16(m_handle))[pos];
    }

    bool empty() const noexcept
    {
        return tstr_is_empty(m_handle);
    }

    size_type size() const noexcept
    {
        return tstr_len_utf16(m_handle);
    }

    const_reference front() const
    {
        if (empty()) {
            TH_THROW(std::out_of_range, "Empty string");
        }
        return reinterpret_cast<char16_t const *>(tstr_buf_utf16(m_handle))[0];
    }

    const_reference back() const
    {
        if (empty()) {
            TH_THROW(std::out_of_range, "Empty string");
        }
        return reinterpret_cast<char16_t const *>(tstr_buf_utf16(m_handle))[size() - 1];
    }

    // To be deprecated
    const_pointer c_str() const noexcept
    {
        return reinterpret_cast<char16_t const *>(tstr_buf_utf16(m_handle));
    }

    const_pointer data() const noexcept
    {
        return reinterpret_cast<char16_t const *>(tstr_buf_utf16(m_handle));
    }

    const_iterator begin() const noexcept
    {
        return reinterpret_cast<char16_t const *>(tstr_buf_utf16(m_handle));
    }

    const_iterator cbegin() const noexcept
    {
        return begin();
    }

    const_iterator end() const noexcept
    {
        return reinterpret_cast<char16_t const *>(tstr_buf_utf16(m_handle)) + tstr_len_utf16(m_handle);
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
    friend struct copy_cached_u16string_view;

    u16string_view substr(std::size_t pos, std::size_t len = -1) const;

protected:
    struct TString m_handle;

    explicit u16string_view(struct TString handle) : m_handle(handle)
    {
    }
};

struct u16string : public u16string_view {
    u16string(char16_t const *value TH_NONNULL, size_type size)
        : u16string(tstr_new_copied_utf16(reinterpret_cast<uint16_t const *>(value), size))
    {
    }

    u16string(char16_t const *value TH_NONNULL) : u16string(value, std::char_traits<char16_t>::length(value))
    {
    }

    u16string(static_flag_t, char16_t const *value TH_NONNULL, size_type size)
        : u16string(tstr_new_static_utf16(reinterpret_cast<uint16_t const *>(value), size))
    {
    }

    u16string(static_flag_t, char16_t const *value TH_NONNULL)
        : u16string(static_flag, value, std::char_traits<char16_t>::length(value))
    {
    }

    u16string() : u16string(static_flag, u"", 0)
    {
    }

    u16string(char16_t const *value TH_NONNULL, size_type size, TStringGlobalRefContext ctx)
        : u16string(tstr_new_acquired_utf16(reinterpret_cast<uint16_t const *>(value), size, ctx))
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

    u16string(u16string &&other) noexcept : u16string(std::exchange(other.m_handle, tstr_new_invalid()))
    {
    }

    // Explicit downcast
    explicit u16string(common_string_view other) : u16string(tstr_dup_as_utf16(other.m_handle))
    {
    }

    explicit u16string(char const *value TH_NONNULL, size_type size) : u16string(common_string_view(value, size))
    {
    }

    explicit u16string(char const *value TH_NONNULL) : u16string(value, std::char_traits<char>::length(value))
    {
    }

    // Implicit upcast
    operator common_string_view() const & noexcept
    {
        return common_string_view(m_handle);
    }

    operator common_string() const & noexcept
    {
        return common_string(tstr_dup(m_handle));
    }

    operator common_string() && noexcept
    {
        common_string str = common_string(m_handle);
        m_handle = tstr_new_invalid();
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
        tstr_drop(m_handle);
    }

    friend struct u16string_builder;
    template<typename Initializer>
    static u16string initialize(size_type capacity, Initializer &&initializer);

    friend u16string concat(std::initializer_list<u16string_view> sv_list);
    static u16string concat(std::initializer_list<common_string_view> sv_list);
    u16string &operator+=(common_string_view other);

private:
    explicit u16string(struct TString handle) : u16string_view(handle)
    {
    }
};

struct copy_cached_u16string_view : public u16string_view {
    copy_cached_u16string_view(char16_t const *value TH_NONNULL, size_type size)
        : copy_cached_u16string_view([value, size](TStringCopyCache *cache) {
            return tstr_new_copyable_borrowed_utf16(reinterpret_cast<uint16_t const *>(value), size, cache);
        })
    {
    }

    copy_cached_u16string_view(char16_t const *value TH_NONNULL)
        : copy_cached_u16string_view(value, std::char_traits<char16_t>::length(value))
    {
    }

    copy_cached_u16string_view(copy_cached_u16string_view const &) = delete;
    copy_cached_u16string_view(copy_cached_u16string_view &&) = delete;
    copy_cached_u16string_view &operator=(copy_cached_u16string_view const &) = delete;
    copy_cached_u16string_view &operator=(copy_cached_u16string_view &&) = delete;

    ~copy_cached_u16string_view()
    {
        tstr_copy_cache_drop(&m_cache);
    }

    static copy_cached_u16string_view substr(u16string_view str, std::size_t pos, std::size_t len = -1);

private:
    TStringCopyCache m_cache;

    template<typename Initializer>
    explicit copy_cached_u16string_view(Initializer &&initializer)
        : u16string_view(std::forward<Initializer>(initializer)(&m_cache))
    {
    }
};

struct acquire_cached_u16string_view : public u16string_view {
    acquire_cached_u16string_view(char16_t const *value TH_NONNULL, size_type size, TStringLocalRefContext ctx)
        : acquire_cached_u16string_view([value, size, ctx](TStringAcquireCache *cache) {
            return tstr_new_acquirable_borrowed_utf16(reinterpret_cast<uint16_t const *>(value), size, cache, ctx);
        })
    {
    }

    acquire_cached_u16string_view(acquire_cached_u16string_view const &) = delete;
    acquire_cached_u16string_view(acquire_cached_u16string_view &&) = delete;
    acquire_cached_u16string_view &operator=(acquire_cached_u16string_view const &) = delete;
    acquire_cached_u16string_view &operator=(acquire_cached_u16string_view &&) = delete;

    ~acquire_cached_u16string_view()
    {
        tstr_acquire_cache_drop(&m_cache);
    }

private:
    TStringAcquireCache m_cache;

    template<typename Initializer>
    explicit acquire_cached_u16string_view(Initializer &&initializer)
        : u16string_view(std::forward<Initializer>(initializer)(&m_cache))
    {
    }
};

struct u16string_builder {
    using value_type = char16_t;
    using size_type = std::size_t;
    using reference = value_type &;
    using pointer = value_type *;
    using const_reference = value_type const &;
    using const_pointer = value_type const *;

    explicit u16string_builder(size_type capacity) : u16string_builder(tstr_builder_new_utf16(capacity))
    {
    }

    ~u16string_builder()
    {
        tstr_builder_drop(m_builder);
    }

    u16string_builder(u16string_builder const &) = delete;

    u16string_builder(u16string_builder &&other) noexcept
        : m_builder(std::exchange(other.m_builder, tstr_builder_new_invalid()))
    {
    }

    u16string_builder &operator=(u16string_builder other)
    {
        std::swap(this->m_builder, other.m_builder);
        return *this;
    }

    pointer data() noexcept
    {
        return reinterpret_cast<char16_t *>(tstr_builder_mut_buf_utf16(m_builder));
    }

    const_pointer data() const noexcept
    {
        return reinterpret_cast<char16_t const *>(tstr_builder_buf_utf16(m_builder));
    }

    reference operator[](size_type pos) noexcept
    {
        return reinterpret_cast<char16_t *>(tstr_builder_mut_buf_utf16(m_builder))[pos];
    }

    const_reference operator[](size_type pos) const noexcept
    {
        return reinterpret_cast<char16_t const *>(tstr_builder_buf_utf16(m_builder))[pos];
    }

    size_type capacity() const noexcept
    {
        return tstr_builder_cap_utf16(m_builder);
    }

    bool reallocate(size_type capacity, size_type initialized_length = -1)
    {
        return tstr_builder_reallocate_utf16(&m_builder, capacity, initialized_length);
    }

    u16string finish(size_type length) &&
    {
        u16string result(tstr_builder_finish_utf16(m_builder, length));
        m_builder = tstr_builder_new_invalid();
        return result;
    }

private:
    struct TStringBuilder m_builder;

    explicit u16string_builder(struct TStringBuilder builder) : m_builder(builder)
    {
    }
};

template<typename Initializer>
u16string u16string::initialize(size_type capacity, Initializer &&initializer)
{
    u16string_builder builder(capacity);
    char16_t *buf = builder.data();
    char16_t *end = std::forward<Initializer>(initializer)(buf);
    return std::move(builder).finish(end - buf);
}

inline u16string concat(std::initializer_list<u16string_view> sv_list)
{
    static_assert(alignof(u16string_view) == alignof(struct TString));
    return u16string(tstr_concat_as_utf16(sv_list.size(), reinterpret_cast<struct TString const *>(sv_list.begin())));
}

inline u16string u16string::concat(std::initializer_list<common_string_view> sv_list)
{
    static_assert(alignof(common_string_view) == alignof(struct TString));
    return u16string(tstr_concat_as_utf16(sv_list.size(), reinterpret_cast<struct TString const *>(sv_list.begin())));
}

inline u16string operator+(u16string_view left, u16string_view right)
{
    return concat({left, right});
}

inline u16string &u16string::operator+=(common_string_view other)
{
    return *this = u16string::concat({*this, other});
}

inline u16string_view u16string_view::substr(std::size_t pos, std::size_t len) const
{
    return u16string_view(tstr_substr_utf16(this->m_handle, pos, len, nullptr));
}

inline copy_cached_u16string_view copy_cached_u16string_view::substr(u16string_view sv, std::size_t pos,
                                                                     std::size_t len)
{
    return copy_cached_u16string_view([pos, len, sv](TStringCopyCache *cache) {
        return tstr_substr_utf16(sv.m_handle, pos, len, cache);
    });
}

inline namespace literals {
inline taihe::u16string_view operator""_tsv(char16_t const *value, size_t size)
{
    return taihe::u16string_view(static_flag, value, size);
}

inline taihe::u16string operator""_ts(char16_t const *value, size_t size)
{
    return taihe::u16string(static_flag, value, size);
}
}  // namespace literals

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
}  // namespace taihe

template<>
struct std::hash<taihe::u16string> {
    std::size_t operator()(taihe::u16string_view sv) const noexcept
    {
        return std::hash<std::u16string_view>()(std::u16string_view(sv));
    }
};

namespace taihe {
template<typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
string to_string(T value)
{
    constexpr std::size_t shortest_capacity = (std::is_signed_v<T> ? 1 : 0)        // sign
                                              + 1                                  // highest digit
                                              + std::numeric_limits<T>::digits10;  // digits
    string_builder builder(shortest_capacity);
    auto first = builder.data();
    auto last = builder.data() + builder.capacity();
    auto [ptr, ec] = std::to_chars(first, last, value);
    if (ec != std::errc {}) {
        TH_THROW(std::runtime_error, "Conversion to char failed");
    }
    return std::move(builder).finish(ptr - first);
}

template<typename T, std::enable_if_t<std::is_floating_point_v<T>, int> = 0>
string to_string(T value)
{
    constexpr std::size_t shortest_capacity = 1                                           // value sign
                                              + 1                                         // value highest digit
                                              + 1                                         // '.'
                                              + std::numeric_limits<T>::max_digits10 - 1  // value digits
                                              + 1                                         // 'e'
                                              + 1                                         // exponent sign
                                              + 1                                         // exponent highest digit
                                              + std::numeric_limits<int>::digits10;       // exponent digits
    string_builder builder(shortest_capacity);
    auto first = builder.data();
    auto last = builder.data() + builder.capacity();
    auto [ptr, ec] = std::to_chars(first, last, value, std::chars_format::general);
    if (ec != std::errc {}) {
        TH_THROW(std::runtime_error, "Conversion to char failed");
    }
    return std::move(builder).finish(ptr - first);
}

inline string to_string(bool value)
{
    if (value) {
        return "true"_ts;
    } else {
        return "false"_ts;
    }
}

inline std::ostream &operator<<(std::ostream &os, string_view sv)
{
    return os << std::string_view(sv);
}
}  // namespace taihe

namespace taihe {
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
}  // namespace taihe

namespace taihe {
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
}  // namespace taihe

namespace taihe {
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

#endif  // TAIHE_STRING_HPP
