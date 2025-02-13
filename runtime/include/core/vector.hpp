#pragma once

#include <algorithm>
#include <utility>

#include <taihe/common.hpp>

namespace taihe::core {
template<typename T>
struct vector {
public:
    using value_type = T;
    using size_type = std::size_t;
    using reference = T&;
    using const_reference = const T&;
    using pointer = T*;
    using const_pointer = const T*;
    using iterator = T*;
    using const_iterator = const T*;

    vector(std::size_t cap = 0) : m_handle(reinterpret_cast<TVectorData*>(malloc(sizeof(TVectorData)))) {
        tref_set(&m_handle->count, 1);
        m_handle->cap = cap;
        m_handle->data = reinterpret_cast<T*>(malloc(sizeof(T) * cap));
        m_handle->len = 0;
    }

    void reserve(std::size_t cap) const {
        if (cap < m_handle->len) {
            return;
        }
        m_handle->cap = cap;
        m_handle->data = reinterpret_cast<T*>(realloc(m_handle->data, sizeof(T) * cap));
    }

    ~vector() {
        if (m_handle && tref_dec(&m_handle->count)) {
            this->clear();
            free(m_handle->data);
            free(m_handle);
        }
    }

    vector(const vector& other) : m_handle(other.m_handle) {
        if (m_handle) {
            tref_inc(&m_handle->count);
        }
    }

    vector(vector&& other) noexcept : m_handle(other.m_handle) {
        other.m_handle = nullptr;
    }

    vector& operator=(vector other) {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    std::size_t size() const noexcept {
        return m_handle->len;
    }

    std::size_t capacity() const noexcept {
        return m_handle->cap;
    }

    template <typename... Args>
    T& emplace_back(Args&&... args) const {
        std::size_t required_cap = m_handle->len + 1;
        if (required_cap > m_handle->cap) {
            this->reserve(std::max(required_cap, m_handle->cap * 2));
        }
        T* location = &m_handle->data[m_handle->len];
        new (location) T{std::forward<Args>(args)...};
        ++m_handle->len;
        return *location;
    }

    T& push_back(T&& value) const {
        return emplace_back(std::move(value));
    }

    T& push_back(T const& value) const {
        return emplace_back(value);
    }

    T& operator[](std::size_t index) const {
        return m_handle->data[index];
    }

    void pop_back() const {
        if (m_handle->len == 0) {
            return;
        }
        std::destroy_at(&m_handle->data[m_handle->len]);
        --m_handle->len;
    }

    void clear() const noexcept {
        for (std::size_t i = 0; i < m_handle->len; i++) {
            std::destroy_at(&m_handle->data[i]);
        }
        m_handle->len = 0;
    }

    friend bool same_impl(vector const& lhs, vector const& rhs) {
        return lhs.m_handle == rhs.m_handle;
    }

    friend std::size_t hash_impl(vector const& val) {
        return val.m_handle;
    }

private:
    struct TVectorData {
        TRefCount count;
        std::size_t cap;
        T *data;
        std::size_t len;
    } *m_handle;
};

template<typename T>
struct cpp_type_traits<vector<T>> {
    using abi_t = void*;
};

template<typename T>
struct cpp_type_traits<vector<T> const&> {
    using abi_t = void* const*;
};
}
