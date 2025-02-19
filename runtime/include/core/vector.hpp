#pragma once

#include <algorithm>
#include <utility>

#include <taihe/common.hpp>

namespace taihe::core {
template<typename T>
struct vector_view;

template<typename T>
struct vector;

template<typename T>
struct vector_view {
public:
    using value_type = T;
    using size_type = std::size_t;
    using reference = T&;
    using const_reference = const T&;
    using pointer = T*;
    using const_pointer = const T*;
    using iterator = T*;
    using const_iterator = const T*;

    void reserve(std::size_t cap) const {
        if (cap < m_handle->len) {
            return;
        }
        m_handle->cap = cap;
        m_handle->buffer = reinterpret_cast<T*>(realloc(m_handle->buffer, sizeof(T) * cap));
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
        T* location = &m_handle->buffer[m_handle->len];
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
        return m_handle->buffer[index];
    }

    void pop_back() const {
        if (m_handle->len == 0) {
            return;
        }
        std::destroy_at(&m_handle->buffer[m_handle->len]);
        --m_handle->len;
    }

    void clear() const noexcept {
        for (std::size_t i = 0; i < m_handle->len; i++) {
            std::destroy_at(&m_handle->buffer[i]);
        }
        m_handle->len = 0;
    }

    friend bool same_impl(adl_helper_t, vector_view lhs, vector_view rhs) {
        return lhs.m_handle == rhs.m_handle;
    }

    friend std::size_t hash_impl(adl_helper_t, vector_view val) {
        return (std::size_t)val.m_handle;
    }

protected:
    struct data_t {
        TRefCount count;
        std::size_t cap;
        T *buffer;
        std::size_t len;
    } *m_handle;

    explicit vector_view(data_t* handle) : m_handle(handle) {}

    friend struct vector<T>;
};

template<typename T>
struct vector : vector_view<T> {
    using typename vector_view<T>::data_t;
    using vector_view<T>::m_handle;

    vector(std::size_t cap = 0) : vector(reinterpret_cast<data_t*>(malloc(sizeof(data_t)))) {
        tref_set(&m_handle->count, 1);
        m_handle->cap = cap;
        m_handle->buffer = reinterpret_cast<T*>(malloc(sizeof(T) * cap));
        m_handle->len = 0;
    }

    vector(vector<T>&& other) noexcept : vector(other.m_handle) {
        other.m_handle = nullptr;
    }

    vector(const vector<T>& other) : vector(other.m_handle) {
        if (m_handle) {
            tref_inc(&m_handle->count);
        }
    }

    vector(const vector_view<T>& other) : vector(other.m_handle) {
        if (m_handle) {
            tref_inc(&m_handle->count);
        }
    }

    vector& operator=(vector other) {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    ~vector() {
        if (m_handle && tref_dec(&m_handle->count)) {
            this->clear();
            free(m_handle->buffer);
            free(m_handle);
        }
    }

private:
    explicit vector(data_t* handle): vector_view<T>(handle) {}
};

template<typename T>
struct cpp_type_traits<vector<T>> {
    using abi_t = void*;
};

template<typename T>
struct cpp_type_traits<vector_view<T>> {
    using abi_t = void*;
};
}
