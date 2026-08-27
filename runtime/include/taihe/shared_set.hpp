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

#ifndef TAIHE_SHARED_SET_HPP
#define TAIHE_SHARED_SET_HPP

#include <taihe/shared_set.abi.h>
#include <taihe/array.hpp>
#include <taihe/callback.hpp>
#include <taihe/common.hpp>
#include <taihe/error.hpp>
#include <taihe/expected.hpp>
#include <taihe/invoke.hpp>
#include <taihe/object.hpp>

#include <cstdint>
#include <utility>

namespace taihe {
template<typename K>
struct shared_set_view;

template<typename K>
struct shared_set;

template<typename K>
struct shared_set_view {
    using view_type = shared_set_view<K>;
    using holder_type = shared_set<K>;

    using size_type = std::uint64_t;
    using size_result_type = expected<size_type, error>;
    using void_result_type = expected<void, error>;
    using bool_result_type = expected<bool, error>;

    using key_owner_type = K;
    using key_param_type = taihe::as_param_t<K>;
    using keys_result_type = expected<array<key_owner_type>, error>;
    using key_visitor_type = callback_view<bool_result_type(key_param_type)>;

    struct ftable_type {
        uint64_t version;

        struct {
            as_abi_func_t<size_result_type, view_type> getSize;
            as_abi_func_t<keys_result_type, view_type> getKeys;
            as_abi_func_t<void_result_type, view_type, key_visitor_type> forEachKey;
            as_abi_func_t<bool_result_type, view_type, key_param_type> has;
            as_abi_func_t<void_result_type, view_type, key_param_type> insert;
            as_abi_func_t<bool_result_type, view_type, key_param_type> checkedInsert;
            as_abi_func_t<void_result_type, view_type, key_param_type> remove;
            as_abi_func_t<bool_result_type, view_type, key_param_type> checkedRemove;
            as_abi_func_t<void_result_type, view_type> clear;
        } methods;
    };

    struct vtable_type {
        struct ftable_type const *ftbl_ptr_0;
    };

    struct abi_type {
        vtable_type const *vtbl_ptr;
        DataBlockHead *data_ptr;
    } m_handle;

    explicit shared_set_view(abi_type handle) : m_handle(handle)
    {
    }

    template<
        typename... InterfaceBases,
        std::enable_if_t<
            (is_vtable_static_castable_from_to_v<vtable_type, typename InterfaceBases::vtable_type> && ...), int> = 0>
    operator interface_view<InterfaceBases...>() const &
    {
        return interface_view<InterfaceBases...>(
            this->m_handle.data_ptr,
            vtable_helper<vtable_type>::template static_cast_to<typename InterfaceBases::vtable_type>(
                this->m_handle.vtbl_ptr)...);
    }

    template<
        typename... InterfaceBases,
        std::enable_if_t<
            (is_vtable_static_castable_from_to_v<vtable_type, typename InterfaceBases::vtable_type> && ...), int> = 0>
    operator interface_holder<InterfaceBases...>() const &
    {
        return interface_holder<InterfaceBases...>(
            tobj_dup(this->m_handle.data_ptr),
            vtable_helper<vtable_type>::template static_cast_to<typename InterfaceBases::vtable_type>(
                this->m_handle.vtbl_ptr)...);
    }

    bool is_error() const &
    {
        return m_handle.vtbl_ptr == nullptr;
    }

    size_result_type getSize() const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.getSize;
        return call_abi_func<size_result_type, view_type>(abi_func, *this);
    }

    keys_result_type getKeys() const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.getKeys;
        return call_abi_func<keys_result_type, view_type>(abi_func, *this);
    }

    void_result_type forEachKey(key_visitor_type visitor) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.forEachKey;
        if (abi_func == nullptr) {
            keys_result_type values = getKeys();
            if (!values.has_value()) {
                return unexpected(std::move(values).error());
            }
            for (auto const &key : values.value()) {
                bool_result_type res = visitor(key);
                if (!res.has_value()) {
                    return unexpected(std::move(res).error());
                }
                if (!res.value()) {
                    break;
                }
            }
            return {};
        }
        return call_abi_func<void_result_type, view_type, key_visitor_type>(abi_func, *this, visitor);
    }

    bool_result_type has(key_param_type key) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.has;
        return call_abi_func<bool_result_type, view_type, key_param_type>(abi_func, *this, key);
    }

    void_result_type insert(key_param_type key) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.insert;
        return call_abi_func<void_result_type, view_type, key_param_type>(abi_func, *this, key);
    }

    bool_result_type checkedInsert(key_param_type key) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.checkedInsert;
        if (abi_func == nullptr) {
            bool_result_type old_value = has(key);
            if (!old_value.has_value()) {
                return unexpected(std::move(old_value).error());
            }
            if (old_value.value()) {
                return false;
            }
            void_result_type res = insert(key);
            if (!res.has_value()) {
                return unexpected(std::move(res).error());
            }
            return true;
        }
        return call_abi_func<bool_result_type, view_type, key_param_type>(abi_func, *this, key);
    }

    void_result_type remove(key_param_type key) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.remove;
        return call_abi_func<void_result_type, view_type, key_param_type>(abi_func, *this, key);
    }

    bool_result_type checkedRemove(key_param_type key) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.checkedRemove;
        if (abi_func == nullptr) {
            bool_result_type old_value = has(key);
            if (!old_value.has_value()) {
                return unexpected(std::move(old_value).error());
            }
            if (!old_value.value()) {
                return false;
            }
            void_result_type res = remove(key);
            if (!res.has_value()) {
                return unexpected(std::move(res).error());
            }
            return true;
        }
        return call_abi_func<bool_result_type, view_type, key_param_type>(abi_func, *this, key);
    }

    void_result_type clear() const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.clear;
        return call_abi_func<void_result_type, view_type>(abi_func, *this);
    }

    // clang-format off
    template<typename ImplBlock>
    static constexpr ftable_type ftbl_impl = {
        .version = 0,
        .methods = {
            .getSize = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::getSize,
                size_result_type, view_type>,
            .has = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::has,
                bool_result_type, view_type, key_param_type>,
            .getKeys = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::getKeys,
                keys_result_type, view_type>,
            .forEachKey = taihe::method_as_abi_func_optional_v<ImplBlock, &ImplBlock::impl_type::forEachKey,
                void_result_type, view_type, key_visitor_type>,
            .insert = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::insert,
                void_result_type, view_type, key_param_type>,
            .checkedInsert = taihe::method_as_abi_func_optional_v<ImplBlock, &ImplBlock::impl_type::checkedInsert,
                bool_result_type, view_type, key_param_type>,
            .remove = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::remove,
                void_result_type, view_type, key_param_type>,
            .checkedRemove = taihe::method_as_abi_func_optional_v<ImplBlock, &ImplBlock::impl_type::checkedRemove,
                bool_result_type, view_type, key_param_type>,
            .clear = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::clear,
                void_result_type, view_type>,
        },
    };
    // clang-format on

    template<typename ImplBlock>
    static constexpr vtable_type vtbl_impl = {
        .ftbl_ptr_0 = &ftbl_impl<ImplBlock>,
    };

    template<typename ImplBlock>
    static constexpr void const *qivp_impl([[maybe_unused]] InterfaceId id)
    {
        return nullptr;
    }
};

template<typename K>
struct shared_set : shared_set_view<K> {
    using typename shared_set_view<K>::vtable_type;
    using typename shared_set_view<K>::abi_type;

    explicit shared_set(abi_type handle) : shared_set_view<K>(handle)
    {
    }

    ~shared_set()
    {
        tobj_drop(this->m_handle.data_ptr);
    }

    shared_set &operator=(shared_set other)
    {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    shared_set(shared_set<K> &&other)
        : shared_set({
              other.m_handle.vtbl_ptr,
              std::exchange(other.m_handle.data_ptr, nullptr),
          })
    {
    }

    shared_set(shared_set<K> const &other)
        : shared_set({
              other.m_handle.vtbl_ptr,
              tobj_dup(other.m_handle.data_ptr),
          })
    {
    }

    shared_set(shared_set_view<K> const &other)
        : shared_set({
              other.m_handle.vtbl_ptr,
              tobj_dup(other.m_handle.data_ptr),
          })
    {
    }

    template<
        typename... InterfaceBases,
        std::enable_if_t<
            (is_vtable_static_castable_from_to_v<vtable_type, typename InterfaceBases::vtable_type> && ...), int> = 0>
    operator interface_view<InterfaceBases...>() const &
    {
        return interface_view<InterfaceBases...>(
            this->m_handle.data_ptr,
            vtable_helper<vtable_type>::template static_cast_to<typename InterfaceBases::vtable_type>(
                this->m_handle.vtbl_ptr)...);
    }

    template<
        typename... InterfaceBases,
        std::enable_if_t<
            (is_vtable_static_castable_from_to_v<vtable_type, typename InterfaceBases::vtable_type> && ...), int> = 0>
    operator interface_holder<InterfaceBases...>() const &
    {
        return interface_holder<InterfaceBases...>(
            tobj_dup(this->m_handle.data_ptr),
            vtable_helper<vtable_type>::template static_cast_to<typename InterfaceBases::vtable_type>(
                this->m_handle.vtbl_ptr)...);
    }

    template<
        typename... InterfaceBases,
        std::enable_if_t<
            (is_vtable_static_castable_from_to_v<vtable_type, typename InterfaceBases::vtable_type> && ...), int> = 0>
    operator interface_holder<InterfaceBases...>() &&
    {
        return interface_holder<InterfaceBases...>(
            std::exchange(this->m_handle.data_ptr, nullptr),
            vtable_helper<vtable_type>::template static_cast_to<typename InterfaceBases::vtable_type>(
                this->m_handle.vtbl_ptr)...);
    }
};

template<typename K>
struct as_abi<shared_set_view<K>> {
    using type = TSharedSet;
};

template<typename K>
struct as_abi<shared_set<K>> {
    using type = TSharedSet;
};

template<typename K>
struct as_param<shared_set<K>> {
    using type = shared_set_view<K>;
};
}  // namespace taihe

template<typename K>
struct std::hash<taihe::shared_set<K>> {
    std::size_t operator()(taihe::shared_set_view<K> val) const noexcept
    {
        return std::hash<taihe::data_holder>()(val);
    }
};

#endif  // TAIHE_SHARED_SET_HPP