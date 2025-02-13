#pragma once

#include <utility>

#include <taihe/common.hpp>

namespace taihe::core {
template<typename K, typename V>
struct map {
    map(std::size_t cap = 16) : m_handle(reinterpret_cast<TMapData*>(calloc(1, sizeof(TMapData)))) {
        TMapItem** bucket = reinterpret_cast<TMapItem**>(calloc(cap, sizeof(TMapItem*)));
        tref_set(&m_handle->count, 1);
        m_handle->cap = cap;
        m_handle->bucket = bucket;
        m_handle->size = 0;
    }

    void reserve(std::size_t cap) const {
        if (cap == 0) {
            return;
        }
        TMapItem** bucket = reinterpret_cast<TMapItem**>(calloc(cap, sizeof(TMapItem*)));
        for (std::size_t i = 0; i < m_handle->cap; i++) {
            TMapItem* current = m_handle->bucket[i];
            while (current) {
                TMapItem* next = current->next;
                std::size_t index = taihe::core::hash(current->key) % cap;
                current->next = bucket[index];
                bucket[index] = current;
                current = next;
            }
        }
        free(m_handle->bucket);
        m_handle->cap = cap;
        m_handle->bucket = bucket;
    }

    ~map() {
        if (m_handle && tref_dec(&m_handle->count)) {
            clear();
            free(m_handle->bucket);
            free(m_handle);
        }
    }

    map(const map& other) : m_handle(other.m_handle) {
        if (m_handle) {
            tref_inc(&m_handle->count);
        }
    }

    map(map&& other) noexcept : m_handle(other.m_handle) {
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

    void clear() const {
        for (std::size_t i = 0; i < m_handle->cap; i++) {
            TMapItem** current_ptr = &m_handle->bucket[i];
            while (m_handle->bucket[i]) {
                TMapItem* next = m_handle->bucket[i]->next;
                delete m_handle->bucket[i];
                m_handle->bucket[i] = next;
            }
        }
        m_handle->size = 0;
    }

    template<bool cover = false, typename... Args>
    V* emplace(K key, Args&&... args) const {
        std::size_t index = taihe::core::hash(key) % m_handle->cap;
        TMapItem* current = m_handle->bucket[index];
        while (current) {
            if (taihe::core::same(current->key, key)) {
                if (cover) {
                    current->val = V{std::forward<Args>(args)...};
                }
                return &current->val;
            }
            current = current->next;
        }
        TMapItem* item = new TMapItem{
            .key = std::move(key),
            .val = V{std::forward<Args>(args)...},
            .next = m_handle->bucket[index],
        };
        m_handle->bucket[index] = item;
        m_handle->size++;
        std::size_t required_cap = m_handle->size;
        if (required_cap >= m_handle->cap) {
            reserve(required_cap * 2);
        }
        return &item->val;
    }

    V* find(K const& key) const {
        std::size_t index = taihe::core::hash(key) % m_handle->cap;
        TMapItem* current = m_handle->bucket[index];
        while (current) {
            if (taihe::core::same(current->key, key)) {
                return &current->val;
            }
            current = current->next;
        }
        return nullptr;
    }

    bool erase(K const& key) const {
        std::size_t index = taihe::core::hash(key) % m_handle->cap;
        TMapItem** current_ptr = &m_handle->bucket[index];
        while (*current_ptr) {
            if (taihe::core::same((*current_ptr)->key, key)) {
                TMapItem* current = *current_ptr;
                *current_ptr = (*current_ptr)->next;
                delete current;
                m_handle->size--;
                return true;
            } else {
                current_ptr = &(*current_ptr)->next;
            }
        }
        return false;
    }

    friend bool same_impl(map const& lhs, map const& rhs) {
        return lhs.m_handle == rhs.m_handle;
    }

    friend std::size_t hash_impl(map const& val) {
        return val.m_handle;
    }

private:
    struct TMapItem {
        K key;
        V val;
        TMapItem* next;
    };

    struct TMapData {
        TRefCount count;
        std::size_t cap;
        TMapItem** bucket;
        std::size_t size;
    } *m_handle;
};

template<typename K, typename V>
struct cpp_type_traits<map<K, V>> {
    using abi_t = void*;
};

template<typename K, typename V>
struct cpp_type_traits<map<K, V> const&> {
    using abi_t = void* const*;
};
}
