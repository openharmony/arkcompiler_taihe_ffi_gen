#pragma once

#include <vector>
#include <cstddef>
#include <cstdlib>

#include <taihe/common.hpp>

template<typename T>
struct TVector {
    TRefCount count;
    std::size_t len;
    std::size_t cap;
    T data[];
};

template<typename T>
TVector<T>* tvec_dup(TVector<T>* handle) {
    if (handle) {
        tref_inc(&handle->count);
    }
    return handle;
}

template<typename T>
void tvec_drop(TVector<T>* handle) {
    if (handle && tref_dec(&handle->count)) {
        for (std::size_t i = 0; i < handle->len; i++) {
            std::destroy_at(&handle->data[i]);
        }
        free(handle);
    }
}

template<typename T>
TVector<T> tvec_new(std::size_t cap) {
    size_t bytes_required = sizeof(TVector<T>) + sizeof(T) * cap;
    TVector<T>* handle = reinterpret_cast<TVector<T>*>(malloc(bytes_required));
    tref_set(&handle->count, 1);
    handle->len = 0;
    handle->cap = cap;
    return handle;
}

template<typename T>
TVector<T>* tvec_resize(TVector<T>* handle, std::size_t cap) {
    size_t bytes_required = sizeof(TVector<T>) + sizeof(T) * cap;
    handle = reinterpret_cast<TVector<T>*>(realloc(handle, bytes_required));
    handle->cap = cap;
    return handle;
}

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

    vector() : m_handle(tvec_new<T>(0)) {}

    explicit vector(size_type cap) 
        : m_handle(tvec_new<T>(cap)) {}

    explicit vector(TVector<T>* handle)
        : m_handle(handle) {}

    ~vector() {
        tvec_drop(m_handle);
    }

    vector(const vector& other)
        : m_handle(tvec_dup(other.m_handle)) {}

    vector(vector&& other) noexcept
        : m_handle(other.m_handle) {
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

    void reserve(std::size_t requird_cap) {
        if (requird_cap > m_handle->cap) {
            std::size_t new_cap = std::max(requird_cap, m_handle->cap * 2);
            m_handle = tvec_resize(m_handle, new_cap);
        }
    }

    void push_back(T&& value) {
        reserve(m_handle->len + 1);
        new (&m_handle->data[m_handle->len]) T(std::move(value));
        ++m_handle->len;
    }

    void push_back(T const& value) {
        reserve(m_handle->len + 1);
        new (&m_handle->data[m_handle->len]) T(value);
        ++m_handle->len;
    }

    template <typename... Args>
    T& emplace_back(Args&&... args) {
        reserve(m_handle->len + 1);
        T* location = &m_handle->data[m_handle->len];
        new (location) T(std::forward<Args>(args)...);
        ++m_handle->len;
        return *location;
    }

    void pop_back() {
        if (m_handle->len > 0) {
            --m_handle->len;
            std::destroy_at(&m_handle->data[m_handle->len]);
        }
    }

    void clear() noexcept {
        for (std::size_t i = 0; i < m_handle->len; i++) {
            std::destroy_at(&m_handle->data[i]);
        }
        m_handle->len = 0;
    }

    T& operator[](std::size_t index) {
        return m_handle->data[index];
    }

    const T& operator[](std::size_t index) const {
        return m_handle->data[index];
    }

private:
    TVector<T>* m_handle;
};
}
