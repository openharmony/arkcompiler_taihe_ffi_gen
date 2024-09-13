// string.hpp
#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <utility>
#include <string_view>

extern "C" {
#include <taihe/string.abi.h>
}

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

        string(const char* value)
            : m_handle(tstr_new(value, std::strlen(value))) {}

        string(const char* value, size_type size)
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
            return *this = string{ value };
        }

        string& operator=(char const* const value) {
            return *this = string{ value };
        }

        string& operator=(std::initializer_list<char> value) {
            return *this = string{ value };
        }
        
        operator std::string_view() const noexcept {
            if (m_handle)
            {
                return { tstr_buf(m_handle), tstr_len(m_handle) };
            }
            return { "", 0 };
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

        // need ?
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
        TString* m_handle;
    };
}
}
