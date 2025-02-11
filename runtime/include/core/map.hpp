#pragma once

#include <utility>

#include <taihe/common.hpp>

template<typename K, typename V>
struct TMapItem {
    K key;
    V val;
    TMapItem* next;
};

template<typename K, typename V>
struct TMapData {
    TRefCount count;
    std::size_t cap;
    TMapItem<K, V>** bucket;
    std::size_t size;
};

template<typename K, typename V, typename ...Args>
TMapItem<K, V>* tmap_new_item(K key, Args&& ...args) {
    return new TMapItem<K, V>{
        .key = std::move(key),
        .val = V{std::forward<Args>(args)...},
        .next = nullptr,
    };
}

template<typename K, typename V>
void tmap_del_item(TMapItem<K, V>* item) {
    delete item;
}

template<typename K, typename V>
TMapData<K, V>* tmap_new(std::size_t cap) {
    TMapData<K, V>* handle = reinterpret_cast<TMapData<K, V>*>(calloc(1, sizeof(TMapData<K, V>)));
    TMapItem<K, V>** bucket = reinterpret_cast<TMapItem<K, V>**>(calloc(cap, sizeof(TMapItem<K, V>*)));
    tref_set(&handle->count, 1);
    handle->cap = cap;
    handle->bucket = bucket;
    handle->size = 0;
    return handle;
}

template<typename K, typename V>
void tmap_resize(TMapData<K, V>* handle, std::size_t cap) {
    if (cap == 0) {
        return;
    }
    TMapItem<K, V>** bucket = reinterpret_cast<TMapItem<K, V>**>(calloc(cap, sizeof(TMapItem<K, V>*)));
    for (std::size_t i = 0; i < handle->cap; i++) {
        TMapItem<K, V>* current = handle->bucket[i];
        while (current) {
            TMapItem<K, V>* next = current->next;
            std::size_t index = taihe::core::hash(current->key) % cap;
            current->next = bucket[index];
            bucket[index] = current;
            current = next;
        }
    }
    free(handle->bucket);
    handle->cap = cap;
    handle->bucket = bucket;
}

template<bool cover = false, typename K, typename V, typename ...Args>
V* tmap_insert(TMapData<K, V>* handle, K key, Args&& ...args) {
    std::size_t index = taihe::core::hash(key) % handle->cap;
    TMapItem<K, V>* current = handle->bucket[index];
    while (current) {
        if (taihe::core::same(current->key, key)) {
            if (cover) {
                current->val = V{std::forward<Args>(args)...};
            }
            return &current->val;
        }
        current = current->next;
    }
    TMapItem<K, V>* item = tmap_new_item<K, V>(std::move(key), std::forward<Args>(args)...);
    item->next = handle->bucket[index];
    handle->bucket[index] = item;
    handle->size++;
    std::size_t required_cap = handle->size;
    if (required_cap >= handle->cap) {
        tmap_resize(handle, required_cap * 2);
    }
    return &item->val;
}

template<typename K, typename V>
V* tmap_find(TMapData<K, V>* handle, K const &key) {
    std::size_t index = taihe::core::hash(key) % handle->cap;
    TMapItem<K, V>* current = handle->bucket[index];
    while (current) {
        if (taihe::core::same(current->key, key)) {
            return &current->val;
        }
        current = current->next;
    }
    return nullptr;
}

template<typename K, typename V>
bool tmap_erase(TMapData<K, V>* handle, K const &key) {
    std::size_t index = taihe::core::hash(key) % handle->cap;
    TMapItem<K, V>** current_ptr = &handle->bucket[index];
    while (*current_ptr) {
        if (taihe::core::same((*current_ptr)->key, key)) {
            TMapItem<K, V>* current = *current_ptr;
            *current_ptr = (*current_ptr)->next;
            tmap_del_item(current);
            handle->size--;
            return true;
        } else {
            current_ptr = &(*current_ptr)->next;
        }
    }
    return false;
}

template<typename K, typename V>
void tmap_clear(TMapData<K, V>* handle) {
    for (std::size_t i = 0; i < handle->cap; i++) {
        TMapItem<K, V>** current_ptr = &handle->bucket[i];
        while (handle->bucket[i]) {
            TMapItem<K, V>* next = handle->bucket[i]->next;
            tmap_del_item(handle->bucket[i]);
            handle->bucket[i] = next;
        }
    }
    handle->size = 0;
}

template<typename K, typename V>
TMapData<K, V>* tmap_dup(TMapData<K, V>* handle) {
    if (!handle) {
        return nullptr;
    }
    tref_inc(&handle->count);
    return handle;
}

template<typename K, typename V>
void tmap_drop(TMapData<K, V>* handle) {
    if (!handle) {
        return;
    }
    if (tref_dec(&handle->count)) {
        tmap_clear(handle);
        free(handle->bucket);
        free(handle);
    }
}

namespace taihe::core {
template<typename K, typename V>
struct map {
    map() : m_handle(tmap_new<K, V>(16)) {}

    ~map() {
        tmap_drop(m_handle);
    }

    map(const map& other)
        : m_handle(tmap_dup(other.m_handle)) {}

    map(map&& other) noexcept
        : m_handle(other.m_handle) {
        other.m_handle = nullptr;
    }

    map& operator=(map other) {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    std::size_t size() const noexcept {
        return m_handle->size;
    }

    std::size_t capacity() const noexcept {
        return m_handle->cap;
    }

    void reserve(std::size_t new_cap) const {
        tmap_resize(m_handle, new_cap);
    }

    void clear() const {
        tmap_clear(m_handle);
    }

    template<bool cover = false, typename... Args>
    V* emplace(K key, Args&&... args) const {
        return tmap_insert<cover>(m_handle, std::move(key), std::forward<Args>(args)...);
    }

    V* find(K const& key) const {
        return tmap_find(m_handle, key);
    }

    bool erase(K const& key) const {
        return tmap_erase(m_handle, key);
    }

    friend bool same_impl(map const& lhs, map const& rhs) {
        return lhs.m_handle == rhs.m_handle;
    }

    friend std::size_t hash_impl(map const& val) {
        return val.m_handle;
    }

private:
    TMapData<K, V>* m_handle;
};
}
