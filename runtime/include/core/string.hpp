// string.hpp
#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <utility>
#include <string_view>
#include <charconv>

extern "C" {
#include <taihe/string.abi.h>
}

namespace taihe::core::param { struct string; }

namespace taihe {
namespace core {
    struct string {
    public:
        // Using
        using value_type = char;
        using size_type = std::size_t;
        using const_reference = value_type const&;
        // using pointer = value_type*;
        using const_pointer = value_type const*;
        using const_iterator = const_pointer;
        using const_reverse_iterator = std::reverse_iterator<const_iterator>;
        // Constructor
        string() noexcept : m_handle(nullptr) {}

        string(const char* value TH_NONNULL)
            : m_handle(tstr_new(value, std::strlen(value))) {}

        string(const char* value TH_NONNULL, size_type size)
            : m_handle(tstr_new(value, size)) {}
        
        string(std::string_view value)
            : string(value.data(), value.size()) {}

        string(std::initializer_list<char> value)
            : string(value.begin(), static_cast<uint32_t>(value.size())) {}
        
        string(string& other)
            : m_handle(tstr_dup(other.m_handle)) {}

        string(string&& other) noexcept
            : m_handle(other.m_handle) {
            other.m_handle = nullptr;
        }

        string(TString* other_handle)
            : m_handle(tstr_dup(other_handle)) {}


        // Destructor
        ~string() {
            if (m_handle) {
                tstr_drop(m_handle);
            }
            m_handle = nullptr;
        }

        // Operator
        string& operator=(string const& other) {
            if (this != &other)
            {
                if (m_handle) {
                    tstr_drop(m_handle);
                }
                m_handle = tstr_dup(other.m_handle);
            }
            return *this;
        }

        string& operator=(string&& other) noexcept {
            if (this != &other)
            {
                if (m_handle) {
                    tstr_drop(m_handle);
                }
                m_handle = tstr_dup(other.m_handle);
                tstr_drop(other.m_handle);
                other.m_handle = nullptr;
            }
            return *this;
        }

        string& operator=(std::string_view const& value) {
            TH_ASSERT(value.data() != nullptr || value.empty(), "std::string_view's data should not be empty!");
            return *this = string{ value };
        }

        string& operator=(char const* const value TH_NONNULL) {
            return *this = string{ value };
        }

        string& operator=(std::initializer_list<char> value) {
            TH_ASSERT(value.size() > 0, "initializer_list's data should not be empty!");
            return *this = string{ value };
        }

        operator std::string_view() const noexcept {
            if (m_handle) {
                return { tstr_buf(m_handle), tstr_len(m_handle) };
            }
            return { "", 0 };
        }

        operator TString*() const noexcept {
            return m_handle;
        }        

        const_reference operator[](size_type pos) const {
            if (pos >= size())
            {
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

        friend void swap(string& lhs, string& rhs) noexcept {
            std::swap(lhs.m_handle, rhs.m_handle);
        }

        const_reference front() const {
            if (empty())
            {
                throw std::out_of_range("Empty string");
            }
            return tstr_buf(m_handle)[0];
        }

        const_reference back() const {
            if (empty())
            {
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
        friend class param::string;

        TString* m_handle;
    };

namespace param {
    struct string {
    public:
        string() noexcept : m_handle(nullptr) {}

        string(string const& values) = delete;
        string& operator=(string const& values) = delete;
        string(std::nullptr_t) = delete;

        // Use other type to be taihe::core::param::string
        string(taihe::core::string const& value) noexcept 
            : m_handle(value.m_handle) {}

        // string(std::string_view const& value) noexcept {
        //     tstr_new_ref(value.data(), value.size(), m_handle);
        // }

        // string(std::string const& value) noexcept {
        //     tstr_new_ref(value.data(), value.size(), m_handle);
        // }

        // string(char const* const value) noexcept {
        //     tstr_new_ref(value, strlen(value), m_handle);
        // }

        string(struct TString* other_handle) noexcept
            : m_handle(other_handle) {}

        operator taihe::core::string const&() const noexcept {
            return *reinterpret_cast<string const*>(this);
        }

        operator TString*() const noexcept {
            return m_handle;
        }
    private:
        TString* m_handle;
    };
}

}
}

namespace taihe {
namespace core {
    // ‌Comparative function
    inline bool operator==(string const& left, string const& right) noexcept {
        return std::string_view(left) == std::string_view(right);
    }

    inline bool operator==(string const& left, std::string const& right) noexcept {
        return std::string_view(left) == std::string_view(right);
    }

    inline bool operator==(std::string const& left, string const& right) noexcept {
        return std::string_view(left) == std::string_view(right);
    }

    inline bool operator==(string const& left, char const* right) noexcept {
        return std::string_view(left) == std::string_view(right);
    }

    inline bool operator==(char const* left, string const& right) noexcept {
        return std::string_view(left) == std::string_view(right);
    }

    bool operator==(string const& left, std::nullptr_t) = delete;

    bool operator==(std::nullptr_t, string const& right) = delete;

    inline bool operator<(string const& left, string const& right) noexcept {
        return std::string_view(left) < std::string_view(right);
    }

    inline bool operator<(std::string const& left, string const& right) noexcept {
        return std::string_view(left) < std::string_view(right);
    }

    inline bool operator<(string const& left, std::string const& right) noexcept {
        return std::string_view(left) < std::string_view(right);
    }

    inline bool operator<(string const& left, char const* right) noexcept {
        return std::string_view(left) < std::string_view(right);
    }

    inline bool operator<(char const* left, string const& right) noexcept {
        return std::string_view(left) < std::string_view(right);
    }

    bool operator<(string const& left, std::nullptr_t) = delete;

    bool operator<(std::nullptr_t, string const& right) = delete;

    inline bool operator!=(string const& left, string const& right) noexcept { return !(left == right); }
    inline bool operator>(string const& left, string const& right) noexcept { return right < left; }
    inline bool operator<=(string const& left, string const& right) noexcept { return !(right < left); }
    inline bool operator>=(string const& left, string const& right) noexcept { return !(left < right); }

    inline bool operator!=(string const& left, std::string const& right) noexcept { return !(left == right); }
    inline bool operator>(string const& left, std::string const& right) noexcept { return right < left; }
    inline bool operator<=(string const& left, std::string const& right) noexcept { return !(right < left); }
    inline bool operator>=(string const& left, std::string const& right) noexcept { return !(left < right); }

    inline bool operator!=(std::string const& left, string const& right) noexcept { return !(left == right); }
    inline bool operator>(std::string const& left, string const& right) noexcept { return right < left; }
    inline bool operator<=(std::string const& left, string const& right) noexcept { return !(right < left); }
    inline bool operator>=(std::string const& left, string const& right) noexcept { return !(left < right); }

    inline bool operator!=(string const& left, char const* right) noexcept { return !(left == right); }
    inline bool operator>(string const& left, char const* right) noexcept { return right < left; }
    inline bool operator<=(string const& left, char const* right) noexcept { return !(right < left); }
    inline bool operator>=(string const& left, char const* right) noexcept { return !(left < right); }

    inline bool operator!=(char const* left, string const& right) noexcept { return !(left == right); }
    inline bool operator>(char const* left, string const& right) noexcept { return right < left; }
    inline bool operator<=(char const* left, string const& right) noexcept { return !(right < left); }
    inline bool operator>=(char const* left, string const& right) noexcept { return !(left < right); }

    bool operator!=(string const& left, std::nullptr_t right) = delete;
    bool operator>(string const& left, std::nullptr_t right) = delete;
    bool operator<=(string const& left, std::nullptr_t right) = delete;
    bool operator>=(string const& left, std::nullptr_t right) = delete;

    bool operator!=(std::nullptr_t left, string const& right) = delete;
    bool operator>(std::nullptr_t left, string const& right) = delete;
    bool operator<=(std::nullptr_t left, string const& right) = delete;
    bool operator>=(std::nullptr_t left, string const& right) = delete;

    // Convert function
    template <typename T>
    inline string string_convert(T value) {
        static_assert(std::is_arithmetic_v<T>);
        char buffer[32];
        std::to_chars_result result;
        if constexpr (std::is_integral_v<T>) {
            result = std::to_chars(std::begin(buffer), std::end(buffer), value);
        } else {
            // Floating point
            result = std::to_chars(std::begin(buffer), std::end(buffer), value, std::chars_format::general);
        }
        if (result.ec != std::errc{}) {
            throw std::runtime_error("Conversion to char failed");
        }
        return string{ std::string_view{buffer, static_cast<std::size_t>(result.ptr - buffer)} };
    }

    inline string to_string(uint8_t value) {
        return string_convert(value);
    }

    inline string to_string(int8_t value) {
        return string_convert(value);
    }

    inline string to_string(uint16_t value) {
        return string_convert(value);
    }

    inline string to_string(int16_t value) {
        return string_convert(value);
    }

    inline string to_string(uint32_t value) {
        return string_convert(value);
    }

    inline string to_string(int32_t value) {
        return string_convert(value);
    }

    inline string to_string(uint64_t value) {
        return string_convert(value);
    }

    inline string to_string(int64_t value) {
        return string_convert(value);
    }

    inline string to_string(float value) {
        return string_convert(value);
    }

    inline string to_string(double value) {
        return string_convert(value);
    }

    // C++20 char8_t
    // inline string to_string(char8_t value) {
    //     char buffer[2] = { value, '\0' };
    //     return string{ std::string_view{ buffer, 1 } };
    // }

    inline string to_string(string const& value) noexcept {
        return value;
    }

    template <typename T, std::enable_if_t<std::is_same_v<T, bool>, int> = 0>
    string to_string(T const value) {
        if (value) {
            return string{ "true" };
        } else {
            return string{ "false" };
        }
    }
}
}