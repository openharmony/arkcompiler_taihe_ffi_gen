#pragma once

#include <algorithm>
#include <cstddef>
#include <cstdlib>

#include <taihe/common.hpp>
#include <utility>

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
    if (cap < handle->len) {
        return;
    }
    handle->cap = cap;
    handle->data = reinterpret_cast<T*>(realloc(handle->data, sizeof(T) * cap));
}

template<typename T, typename ...Args>
T* tvec_push(TVectorData<T>* handle, Args&&... args) {
    std::size_t required_cap = handle->len + 1;
    if (required_cap > handle->cap) {
        tvec_resize(handle, std::max(required_cap, handle->cap * 2));
    }
    T* location = &handle->data[handle->len];
    new (location) T{std::forward<Args>(args)...};
    ++handle->len;
    return location;
}

template<typename T>
void tvec_pop(TVectorData<T>* handle) {
    if (handle->len == 0) {
        return;
    }
    std::destroy_at(&handle->data[handle->len]);
    --handle->len;
}

template<typename T>
void tvec_clear(TVectorData<T>* handle) {
    for (std::size_t i = 0; i < handle->len; i++) {
        std::destroy_at(&handle->data[i]);
    }
    handle->len = 0;
}

template<typename T>
TVectorData<T>* tvec_dup(TVectorData<T>* handle) {
    if (!handle) {
        return nullptr;
    }
    tref_inc(&handle->count);
    return handle;
}

template<typename T>
void tvec_drop(TVectorData<T>* handle) {
    if (!handle) {
        return;
    }
    if (tref_dec(&handle->count)) {
        tvec_clear(handle);
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
        tvec_resize(m_handle, reserved_cap);
    }

    template <typename... Args>
    T& emplace_back(Args&&... args) const {
        return *tvec_push(m_handle, std::forward<Args>(args)...);
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
        tvec_pop(m_handle);
    }

    void clear() const noexcept {
        tvec_clear(m_handle);
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
