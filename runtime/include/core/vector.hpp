#pragma once

#include <vector>
#include <cstddef>
#include <cstdlib>

#include <taihe/common.hpp>

template<typename T>
struct TVectorData {
    TRefCount count;
    std::size_t cap;
    T *data;
    std::size_t len;
};

template<typename T>
TVectorData<T>* tvec_new(std::size_t cap) {
    TVectorData<T>* handle = reinterpret_cast<TVectorData<T>*>(malloc(sizeof(TVectorData<T>)));
    tref_set(&handle->count, 1);
    handle->cap = cap;
    handle->data = reinterpret_cast<T*>(malloc(sizeof(T) * cap));
    handle->len = 0;
    return handle;
}

template<typename T>
void tvec_resize(TVectorData<T>* handle, std::size_t cap) {
    handle->cap = cap;
    handle->data = reinterpret_cast<T*>(realloc(handle->data, sizeof(T) * cap));
}

template<typename T>
TVectorData<T>* tvec_dup(TVectorData<T>* handle) {
    if (handle) {
        tref_inc(&handle->count);
    }
    return handle;
}

template<typename T>
void tvec_drop(TVectorData<T>* handle) {
    if (handle && tref_dec(&handle->count)) {
        for (std::size_t i = 0; i < handle->len; i++) {
            std::destroy_at(&handle->data[i]);
        }
        free(handle->data);
        free(handle);
    }
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

    // explicit vector(size_type cap) 
    //     : m_handle(tvec_new<T>(cap)) {}

    // explicit vector(TVectorData<T>* handle)
    //     : m_handle(handle) {}

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

    void reserve(std::size_t reserved_cap) const {
        if (reserved_cap > m_handle->len) {
            tvec_resize(m_handle, reserved_cap);
        }
    }

    void require(std::size_t required_cap) const {
        if (required_cap > m_handle->cap) {
            tvec_resize(m_handle, std::max(required_cap, m_handle->cap * 2));
        }
    }

    void push_back(T&& value) const {
        require(m_handle->len + 1);
        new (&m_handle->data[m_handle->len]) T(std::move(value));
        ++m_handle->len;
    }

    void push_back(T const& value) const {
        require(m_handle->len + 1);
        new (&m_handle->data[m_handle->len]) T(value);
        ++m_handle->len;
    }

    template <typename... Args>
    T& emplace_back(Args&&... args) const {
        require(m_handle->len + 1);
        T* location = &m_handle->data[m_handle->len];
        new (location) T(std::forward<Args>(args)...);
        ++m_handle->len;
        return *location;
    }

    void pop_back() const {
        if (m_handle->len > 0) {
            --m_handle->len;
            std::destroy_at(&m_handle->data[m_handle->len]);
        }
    }

    void clear() const noexcept {
        for (std::size_t i = 0; i < m_handle->len; i++) {
            std::destroy_at(&m_handle->data[i]);
        }
        m_handle->len = 0;
    }

    T& operator[](std::size_t index) const {
        return m_handle->data[index];
    }

    friend bool same_impl(vector const& lhs, vector const& rhs) {
        return lhs.m_handle == rhs.m_handle;
    }

    friend std::size_t hash_impl(vector const& val) {
        return val.m_handle;
    }

private:
    TVectorData<T>* m_handle;
};
}
