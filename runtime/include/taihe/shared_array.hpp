/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef TAIHE_SHARED_ARRAY_HPP
#define TAIHE_SHARED_ARRAY_HPP

#include <taihe/shared_array.abi.h>
#include <taihe/common.hpp>

#include <algorithm>
#include <cstddef>
#include <stdexcept>
#include <type_traits>
#include <utility>

namespace taihe {
template<typename T>
struct shared_array_view;

template<typename T>
struct shared_array;

template<typename T>
struct acquire_cached_shared_array_view;

template<typename T>
struct shared_array_view {
    static_assert(std::is_scalar_v<std::remove_cv_t<T>>, "shared_array<T> requires a scalar element type");

    using value_type = T;
    using size_type = std::size_t;
    using reference = value_type &;
    using const_reference = value_type const &;
    using pointer = value_type *;
    using const_pointer = value_type const *;
    using iterator = pointer;
    using const_iterator = const_pointer;

    explicit shared_array_view(struct TSharedArray handle) : m_handle(handle)
    {
    }

    shared_array_view(static_flag_t, pointer data, size_type size)
        : shared_array_view(tarr_new_static(data, size * sizeof(value_type)))
    {
    }

    pointer data() const noexcept
    {
        return reinterpret_cast<pointer>(tarr_data(m_handle));
    }

    size_type size() const noexcept
    {
        return tarr_byte_length(m_handle) / sizeof(value_type);
    }

    bool empty() const noexcept
    {
        return tarr_is_empty(m_handle);
    }

    reference operator[](size_type pos) const noexcept
    {
        return data()[pos];
    }

    reference at(size_type pos) const
    {
        if (pos >= size()) {
            TH_THROW(std::out_of_range, "Index out of range");
        }
        return data()[pos];
    }

    iterator begin() const noexcept
    {
        return data();
    }

    iterator end() const noexcept
    {
        return data() + size();
    }

    const_iterator cbegin() const noexcept
    {
        return data();
    }

    const_iterator cend() const noexcept
    {
        return data() + size();
    }

    shared_array_view<T> subview(size_type offset, size_type count) const
    {
        return shared_array_view<T>(tarr_subview(m_handle, offset * sizeof(value_type), count * sizeof(value_type)));
    }

    template<typename U>
    shared_array_view<U> reinterpret_as() const
    {
        if (tarr_byte_length(m_handle) % sizeof(U) != 0) {
            TH_THROW(std::invalid_argument, "Cannot reinterpret due to size mismatch");
        }
        return shared_array_view<U>(m_handle);
    }

    friend struct shared_array<T>;

protected:
    struct TSharedArray m_handle;
};

template<typename T>
struct shared_array : public shared_array_view<T> {
    using typename shared_array_view<T>::pointer;
    using typename shared_array_view<T>::size_type;
    using typename shared_array_view<T>::value_type;

    explicit shared_array(struct TSharedArray handle) : shared_array_view<T>(handle)
    {
    }

    explicit shared_array(size_type size) : shared_array(tarr_new_internal(size * sizeof(value_type)))
    {
    }

    shared_array(size_type size, value_type const &value) : shared_array(size)
    {
        std::fill_n(this->data(), size, value);
    }

    shared_array(static_flag_t, pointer data, size_type size)
        : shared_array(tarr_new_static(data, size * sizeof(value_type)))
    {
    }

    shared_array(pointer data, size_type size, struct TSharedArrayGlobalRefContext ctx)
        : shared_array(tarr_new_acquired(data, size * sizeof(value_type), ctx))
    {
    }

    shared_array(shared_array_view<T> const &other) : shared_array(tarr_dup(other.m_handle))
    {
    }

    shared_array(shared_array<T> const &other) : shared_array(tarr_dup(other.m_handle))
    {
    }

    shared_array(shared_array<T> &&other) noexcept : shared_array(other.m_handle)
    {
        other.m_handle = tarr_new_invalid();
    }

    shared_array &operator=(shared_array other)
    {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    ~shared_array()
    {
        tarr_drop(this->m_handle);
    }
};

template<typename T>
struct acquire_cached_shared_array_view : public shared_array_view<T> {
    using typename shared_array_view<T>::pointer;
    using typename shared_array_view<T>::size_type;
    using typename shared_array_view<T>::value_type;

    acquire_cached_shared_array_view(pointer data, size_type size, struct TSharedArrayLocalRefContext ctx)
        : acquire_cached_shared_array_view([data, size, ctx](struct TSharedArrayAcquireCache *cache) {
            return tarr_new_acquirable_borrowed(data, size * sizeof(value_type), cache, ctx);
        })
    {
    }

    acquire_cached_shared_array_view(acquire_cached_shared_array_view const &) = delete;
    acquire_cached_shared_array_view(acquire_cached_shared_array_view &&) = delete;
    acquire_cached_shared_array_view &operator=(acquire_cached_shared_array_view const &) = delete;
    acquire_cached_shared_array_view &operator=(acquire_cached_shared_array_view &&) = delete;

    ~acquire_cached_shared_array_view()
    {
        tarr_acquire_cache_drop(&m_cache);
    }

private:
    struct TSharedArrayAcquireCache m_cache;

    template<typename Initializer>
    explicit acquire_cached_shared_array_view(Initializer &&initializer)
        : shared_array_view<T>(std::forward<Initializer>(initializer)(&m_cache))
    {
    }
};

template<typename T>
bool operator==(shared_array_view<T> const &lhs, shared_array_view<T> const &rhs)
{
    return lhs.size() == rhs.size() && lhs.data() == rhs.data();
}

template<typename T>
bool operator!=(shared_array_view<T> const &lhs, shared_array_view<T> const &rhs)
{
    return !(lhs == rhs);
}
}  // namespace taihe

template<typename T>
struct std::hash<taihe::shared_array<T>> {
    std::size_t operator()(taihe::shared_array_view<T> val) const noexcept
    {
        return std::hash<void *>()(val.data()) ^ std::hash<std::size_t>()(val.size());
    }
};

namespace taihe {
template<typename T>
struct as_abi<shared_array_view<T>> {
    using type = struct TSharedArray;
};

template<typename T>
struct as_abi<shared_array<T>> {
    using type = struct TSharedArray;
};

template<typename T>
struct as_param<shared_array<T>> {
    using type = shared_array_view<T>;
};
}  // namespace taihe

#endif  // TAIHE_SHARED_ARRAY_HPP