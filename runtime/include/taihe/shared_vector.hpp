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

#ifndef TAIHE_SHARED_VECTOR_HPP
#define TAIHE_SHARED_VECTOR_HPP

#include <taihe/shared_vector.abi.h>
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
template<typename T>
struct shared_vector_view;

template<typename T>
struct shared_vector;

template<typename T>
struct shared_vector_view {
    using view_type = shared_vector_view<T>;
    using holder_type = shared_vector<T>;

    using size_type = std::uint64_t;
    using size_result_type = expected<size_type, error>;
    using void_result_type = expected<void, error>;
    using bool_result_type = expected<bool, error>;

    using value_type = T;
    using param_type = taihe::as_param_t<T>;
    using value_result_type = expected<value_type, error>;
    using value_results_type = expected<array<value_type>, error>;
    using value_visitor_type = callback_view<bool_result_type(size_type, param_type)>;

    struct ftable_type {
        uint64_t version;

        struct {
            as_abi_func_t<size_result_type, view_type> getSize;
            as_abi_func_t<value_results_type, view_type> getItems;
            as_abi_func_t<void_result_type, view_type, value_visitor_type> forEachItem;
            as_abi_func_t<value_result_type, view_type, size_type> get;
            as_abi_func_t<void_result_type, view_type, size_type, param_type> set;
            as_abi_func_t<value_result_type, view_type, size_type, param_type> getAndSet;
            as_abi_func_t<void_result_type, view_type, size_type, param_type> insert;
            as_abi_func_t<void_result_type, view_type, param_type> insertLast;
            as_abi_func_t<void_result_type, view_type, size_type> remove;
            as_abi_func_t<void_result_type, view_type> removeLast;
            as_abi_func_t<value_result_type, view_type, size_type> getAndRemove;
            as_abi_func_t<value_result_type, view_type> getAndRemoveLast;
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

    explicit shared_vector_view(abi_type handle) : m_handle(handle)
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

    value_results_type getItems() const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.getItems;
        return call_abi_func<value_results_type, view_type>(abi_func, *this);
    }

    void_result_type forEachItem(value_visitor_type visitor) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.forEachItem;
        if (abi_func == nullptr) {
            value_results_type values = getItems();
            if (!values.has_value()) {
                return unexpected(std::move(values).error());
            }
            size_type index = 0;
            for (auto const &value : values.value()) {
                bool_result_type res = visitor(index++, value);
                if (!res.has_value()) {
                    return unexpected(std::move(res).error());
                }
                if (!res.value()) {
                    break;
                }
            }
            return {};
        }
        return call_abi_func<void_result_type, view_type, value_visitor_type>(abi_func, *this, visitor);
    }

    value_result_type get(size_type index) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.get;
        return call_abi_func<value_result_type, view_type, size_type>(abi_func, *this, index);
    }

    void_result_type set(size_type index, param_type value) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.set;
        return call_abi_func<void_result_type, view_type, size_type, param_type>(abi_func, *this, index,
                                                                                 std::forward<param_type>(value));
    }

    value_result_type getAndSet(size_type index, param_type value) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.getAndSet;
        if (abi_func == nullptr) {
            value_result_type old_value = get(index);
            if (!old_value.has_value()) {
                return unexpected(std::move(old_value).error());
            }
            void_result_type res = set(index, std::forward<param_type>(value));
            if (!res.has_value()) {
                return unexpected(std::move(res).error());
            }
            return std::move(old_value).value();
        }
        return call_abi_func<value_result_type, view_type, size_type, param_type>(abi_func, *this, index,
                                                                                  std::forward<param_type>(value));
    }

    void_result_type insert(size_type index, param_type value) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.insert;
        return call_abi_func<void_result_type, view_type, size_type, param_type>(abi_func, *this, index,
                                                                                 std::forward<param_type>(value));
    }

    void_result_type insertLast(param_type value) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.insertLast;
        if (abi_func == nullptr) {
            size_result_type size = getSize();
            if (!size.has_value()) {
                return unexpected(std::move(size).error());
            }
            return insert(size.value(), std::forward<param_type>(value));
        }
        return call_abi_func<void_result_type, view_type, param_type>(abi_func, *this, std::forward<param_type>(value));
    }

    void_result_type remove(size_type index) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.remove;
        return call_abi_func<void_result_type, view_type, size_type>(abi_func, *this, index);
    }

    void_result_type removeLast() const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.removeLast;
        if (abi_func == nullptr) {
            size_result_type size = getSize();
            if (!size.has_value()) {
                return unexpected(std::move(size).error());
            }
            return remove(size.value() - 1);
        }
        return call_abi_func<void_result_type, view_type>(abi_func, *this);
    }

    value_result_type getAndRemove(size_type index) const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.getAndRemove;
        if (abi_func == nullptr) {
            value_result_type old_value = get(index);
            if (!old_value.has_value()) {
                return unexpected(std::move(old_value).error());
            }
            void_result_type res = remove(index);
            if (!res.has_value()) {
                return unexpected(std::move(res).error());
            }
            return std::move(old_value).value();
        }
        return call_abi_func<value_result_type, view_type, size_type>(abi_func, *this, index);
    }

    value_result_type getAndRemoveLast() const &
    {
        auto abi_func = m_handle.vtbl_ptr->ftbl_ptr_0->methods.getAndRemoveLast;
        if (abi_func == nullptr) {
            size_result_type size = getSize();
            if (!size.has_value()) {
                return unexpected(std::move(size).error());
            }
            return getAndRemove(size.value() - 1);
        }
        return call_abi_func<value_result_type, view_type>(abi_func, *this);
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
            .getItems = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::getItems,
                value_results_type, view_type>,
            .forEachItem = taihe::method_as_abi_func_optional_v<ImplBlock, &ImplBlock::impl_type::forEachItem,
                void_result_type, view_type, value_visitor_type>,
            .get = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::get,
                value_result_type, view_type, size_type>,
            .set = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::set,
                void_result_type, view_type, size_type, param_type>,
            .getAndSet = taihe::method_as_abi_func_optional_v<ImplBlock, &ImplBlock::impl_type::getAndSet,
                value_result_type, view_type, size_type, param_type>,
            .insert = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::insert,
                void_result_type, view_type, size_type, param_type>,
            .insertLast = taihe::method_as_abi_func_optional_v<ImplBlock, &ImplBlock::impl_type::insertLast,
                void_result_type, view_type, param_type>,
            .remove = taihe::method_as_abi_func_required_v<ImplBlock, &ImplBlock::impl_type::remove,
                void_result_type, view_type, size_type>,
            .removeLast = taihe::method_as_abi_func_optional_v<ImplBlock, &ImplBlock::impl_type::removeLast,
                void_result_type, view_type>,
            .getAndRemove = taihe::method_as_abi_func_optional_v<ImplBlock, &ImplBlock::impl_type::getAndRemove,
                value_result_type, view_type, size_type>,
            .getAndRemoveLast = taihe::method_as_abi_func_optional_v<ImplBlock, &ImplBlock::impl_type::getAndRemoveLast,
                value_result_type, view_type>,
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

template<typename T>
struct shared_vector : shared_vector_view<T> {
    using typename shared_vector_view<T>::vtable_type;
    using typename shared_vector_view<T>::abi_type;

    explicit shared_vector(abi_type handle) : shared_vector_view<T>(handle)
    {
    }

    ~shared_vector()
    {
        tobj_drop(this->m_handle.data_ptr);
    }

    shared_vector &operator=(shared_vector other)
    {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    shared_vector(shared_vector<T> &&other)
        : shared_vector({
              other.m_handle.vtbl_ptr,
              std::exchange(other.m_handle.data_ptr, nullptr),
          })
    {
    }

    shared_vector(shared_vector<T> const &other)
        : shared_vector({
              other.m_handle.vtbl_ptr,
              tobj_dup(other.m_handle.data_ptr),
          })
    {
    }

    shared_vector(shared_vector_view<T> const &other)
        : shared_vector({
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

template<typename T>
struct as_abi<shared_vector_view<T>> {
    using type = TSharedVector;
};

template<typename T>
struct as_abi<shared_vector<T>> {
    using type = TSharedVector;
};

template<typename T>
struct as_param<shared_vector<T>> {
    using type = shared_vector_view<T>;
};
}  // namespace taihe

template<typename T>
struct std::hash<taihe::shared_vector<T>> {
    std::size_t operator()(taihe::shared_vector_view<T> val) const noexcept
    {
        return std::hash<taihe::data_holder>()(val);
    }
};

#endif  // TAIHE_SHARED_VECTOR_HPP