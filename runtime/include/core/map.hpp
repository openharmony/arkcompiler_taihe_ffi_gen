#pragma once

#include "taihe/common.h"
#include "taihe/common.hpp"
#include <utility>

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

template<typename K, typename V>
TMapData<K, V>* tmap_dup(TMapData<K, V>* handle) {
    if (handle) {
        tref_inc(&handle->count);
    }
    return handle;
}

template<typename K, typename V>
void tmap_del_item(TMapItem<K, V>* item) {
    delete item;
}

template<typename K, typename V, typename ...Args>
TMapItem<K, V>* tmap_new_item(K key, Args&& ...args) {
    return new TMapItem<K, V>{
        .key = std::move(key),
        .val = {std::forward<Args>(args)...},
        .next = nullptr,
    };
}

template<typename K, typename V>
void tmap_drop(TMapData<K, V>* handle) {
    if (handle && tref_dec(&handle->count)) {
        for (std::size_t i = 0; i < handle->cap; i++) {
            TMapItem<K, V>* current = handle->bucket[i];
            while (current) {
                TMapItem<K, V>* next = current->next;
                tmap_del_item(current);
                current = next;
            }
        }
        free(handle->bucket);
        free(handle);
    }
}

template<bool reset, typename K, typename V, typename ...Args>
TMapItem<K, V>* tmap_set(TMapData<K, V>* handle, K key, Args&& ...args) {
    std::size_t index = taihe::core::hash(key) % handle->cap;
    TMapItem<K, V>* current = handle->bucket[index];
    while (current) {
        if (taihe::core::same(current->key, key)) {
            if (reset) {
                current->val = V{std::forward<Args>(args)...};
            }
            return current;
        }
        current = current->next;
    }
    TMapItem<K, V>* item = tmap_new_item<K, V>(std::move(key), std::forward<Args>(args)...);
    item->next = handle->bucket[index];
    handle->bucket[index] = item;
    return item;
}

template<typename K, typename V, typename ...Args>
TMapItem<K, V>* tmap_find(TMapData<K, V>* handle, K key) {
    std::size_t index = taihe::core::hash(key) % handle->cap;
    TMapItem<K, V>* current = handle->bucket[index];
    while (current) {
        if (taihe::core::same(current->key, key)) {
            return current;
        }
        current = current->next;
    }
    return nullptr;
}

template<typename K, typename V>
bool tmap_remove(TMapData<K, V>* handle, K key) {
    std::size_t index = taihe::core::hash(key) % handle->cap;
    TMapItem<K, V>** current_ptr = &handle->bucket[index];
    while (*current_ptr) {
        if (taihe::core::same((*current_ptr)->key, key)) {
            TMapItem<K, V>* current = *current_ptr;
            *current_ptr = (*current_ptr)->next;
            delete current;
            return true;
        }
        current_ptr = &(*current_ptr)->next;
    }
    return false;
}

namespace taihe::core {}
