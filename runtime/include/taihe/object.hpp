/*
 * Copyright (c) 2025-2026 Huawei Device Co., Ltd.
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

#ifndef TAIHE_OBJECT_HPP
#define TAIHE_OBJECT_HPP

#include <taihe/object.abi.h>
#include <taihe/common.hpp>

#include <cstddef>
#include <type_traits>
#include <utility>

//////////////////////////////////////////
// Interface Type Traits Implementation //
//////////////////////////////////////////

namespace taihe {
template<typename T, typename = void>
struct is_interface_type : std::false_type {};

template<typename T>
struct is_interface_type<
    T, std::void_t<typename T::view_type, typename T::holder_type, typename T::vtable_type, typename T::abi_type,
                   decltype(typename T::abi_type {
                       std::declval<typename T::vtable_type const *>(),
                       std::declval<DataBlockHead *>(),
                   }),
                   decltype(std::declval<typename T::abi_type>().vtbl_ptr),
                   decltype(std::declval<typename T::abi_type>().data_ptr),
                   decltype(T(std::declval<typename T::abi_type>())), decltype(std::declval<T>().m_handle)>>
    : std::conjunction<
          // handle type member checks
          std::is_same<decltype(std::declval<typename T::abi_type>().vtbl_ptr), typename T::vtable_type const *>,
          std::is_same<decltype(std::declval<typename T::abi_type>().data_ptr), DataBlockHead *>,
          // interface type member checks
          std::is_same<decltype(std::declval<T>().m_handle), typename T::abi_type>> {};

template<typename T>
constexpr inline bool is_interface_type_v = is_interface_type<T>::value;

template<typename T, typename = void>
struct is_interface_view_type : std::false_type {};

template<typename InterfaceType>
struct is_interface_view_type<InterfaceType, std::enable_if_t<is_interface_type_v<InterfaceType>>>
    : std::is_same<typename InterfaceType::view_type, InterfaceType> {};

template<typename T>
constexpr inline bool is_interface_view_type_v = is_interface_view_type<T>::value;

template<typename T, typename = void>
struct is_interface_holder_type : std::false_type {};

template<typename InterfaceType>
struct is_interface_holder_type<InterfaceType, std::enable_if_t<is_interface_type_v<InterfaceType>>>
    : std::is_same<typename InterfaceType::holder_type, InterfaceType> {};

template<typename T>
constexpr inline bool is_interface_holder_type_v = is_interface_holder_type<T>::value;

template<typename T, typename = void>
struct is_impl_block_type : std::false_type {};

template<typename T>
struct is_impl_block_type<T, std::void_t<typename T::impl_type, decltype(std::declval<T>().get_impl_ptr())>>
    : std::conjunction<std::is_base_of<DataBlockHead, T>,
                       std::is_same<decltype(std::declval<T>().get_impl_ptr()), typename T::impl_type *>> {};

template<typename T>
constexpr inline bool is_impl_block_type_v = is_impl_block_type<T>::value;

template<typename VTableType>
struct vtable_helper {
    template<typename VTableDest>
    static VTableDest const &as_ref(VTableDest const &vtbl_ref)
    {
        return vtbl_ref;
    }

    template<typename VTableDest>
    static VTableDest const &as_ref(VTableDest &&vtbl_ref) = delete;

    template<typename VTableDest, typename = void>
    struct is_static_castable_to : std::false_type {};

    template<typename VTableDest>
    struct is_static_castable_to<VTableDest,
                                 std::void_t<decltype(as_ref<VTableDest>(std::declval<VTableType const &>()))>>
        : std::true_type {};

    template<typename VTableDest, std::enable_if_t<is_static_castable_to<VTableDest>::value, int> = 0>
    static VTableDest const *static_cast_to(VTableType const *vtbl_ptr)
    {
        if (vtbl_ptr == nullptr) {
            return nullptr;
        }
        return &as_ref<VTableDest>(*vtbl_ptr);
    }
};

template<typename VTableType, typename = void>
struct is_vtable_dynamic_castable_to : std::false_type {};

template<typename VTableType>
struct is_vtable_dynamic_castable_to<
    VTableType, std::void_t<decltype(vtable_helper<VTableType>::dynamic_cast_from(std::declval<DataBlockHead *>()))>>
    : std::is_same<decltype(vtable_helper<VTableType>::dynamic_cast_from(std::declval<DataBlockHead *>())),
                   VTableType const *> {};

template<typename VTableType>
constexpr inline bool is_vtable_dynamic_castable_to_v = is_vtable_dynamic_castable_to<VTableType>::value;

template<typename VTableType, typename VTableDest, typename = void>
struct is_vtable_static_castable_from_to : std::false_type {};

template<typename VTableType, typename VTableDest>
struct is_vtable_static_castable_from_to<VTableType, VTableDest,
                                         std::void_t<decltype(vtable_helper<VTableType>::template static_cast_to<
                                                              VTableDest>(std::declval<VTableType const *>()))>>
    : std::is_same<decltype(vtable_helper<VTableType>::template static_cast_to<VTableDest>(
                       std::declval<VTableType const *>())),
                   VTableDest const *> {};

template<typename VTableType, typename VTableDest>
constexpr inline bool is_vtable_static_castable_from_to_v =
    is_vtable_static_castable_from_to<VTableType, VTableDest>::value;

template<typename VTableDest, typename... VTableTypes>
struct is_vtable_static_castable_to_from_any
    : std::bool_constant<(is_vtable_static_castable_from_to_v<VTableTypes, VTableDest> || ...)> {};

template<typename VTableDest, typename... VTableTypes>
constexpr inline bool is_vtable_static_castable_to_from_any_v =
    is_vtable_static_castable_to_from_any<VTableDest, VTableTypes...>::value;

template<typename VTableDest, typename... VTableTypes,
         std::enable_if_t<(is_vtable_static_castable_from_to_v<VTableTypes, VTableDest> || ...), int> = 0>
VTableDest const *vtable_static_cast_to_from_any(VTableTypes const *...vtbl_ptrs)
{
    VTableDest const *dest_vtbl_ptr = nullptr;
    bool success = ([&dest_vtbl_ptr, vtbl_ptrs] {
        if constexpr (is_vtable_static_castable_from_to_v<VTableTypes, VTableDest>) {
            dest_vtbl_ptr = vtable_helper<VTableTypes>::template static_cast_to<VTableDest>(vtbl_ptrs);
            return true;
        }
        return false;
    }() || ...);
    return success ? dest_vtbl_ptr : nullptr;
}
}  // namespace taihe

////////////////////////////////////////
// Object View and Holder Definitions //
////////////////////////////////////////

namespace taihe {
template<typename DataBlock, typename... InterfaceTypes>
struct object_view;
template<typename DataBlock, typename... InterfaceTypes>
struct object_holder;

template<typename DataBlock, typename... InterfaceTypes>
struct object_view {
    static_assert(std::is_base_of_v<DataBlockHead, DataBlock>, "DataBlock must be subclass of DataBlockHead.");
    static_assert((is_interface_type_v<InterfaceTypes> && ...), "All InterfaceTypes must be interfaces.");

    using data_block_type = DataBlock;
    using view_type = object_view<DataBlock, InterfaceTypes...>;
    using holder_type = object_holder<DataBlock, InterfaceTypes...>;

    DataBlock *data_ptr;
    std::tuple<typename InterfaceTypes::vtable_type const *...> vtbl_ptr_tuple;

    template<typename InterfaceDest>
    struct is_interface_static_castable_to
        : is_vtable_static_castable_to_from_any<typename InterfaceDest::vtable_type,
                                                typename InterfaceTypes::vtable_type...> {};

    template<typename InterfaceDest>
    static constexpr bool is_interface_static_castable_to_v = is_interface_static_castable_to<InterfaceDest>::value;

    template<typename InterfaceDest>
    typename InterfaceDest::vtable_type const *interface_static_cast_to() const
    {
        return std::apply(vtable_static_cast_to_from_any<typename InterfaceDest::vtable_type,
                                                         typename InterfaceTypes::vtable_type...>,
                          this->vtbl_ptr_tuple);
    }

    object_view() : data_ptr(nullptr), vtbl_ptr_tuple()
    {
    }

    object_view(DataBlock *other_data_ptr,
                std::tuple<typename InterfaceTypes::vtable_type const *...> other_vtbl_ptr_tuple)
        : data_ptr(other_data_ptr), vtbl_ptr_tuple(other_vtbl_ptr_tuple)
    {
    }

    explicit object_view(DataBlock *other_data_ptr, typename InterfaceTypes::vtable_type const *...other_vtbl_ptrs)
        : data_ptr(other_data_ptr), vtbl_ptr_tuple(other_vtbl_ptrs...)
    {
    }

    template<typename InterfaceView,
             std::enable_if_t<std::conjunction_v<is_interface_view_type<InterfaceView>,
                                                 is_interface_static_castable_to<InterfaceView>>,
                              int> = 0>
    operator InterfaceView() const &
    {
        typename InterfaceView::abi_type handle = {
            this->interface_static_cast_to<InterfaceView>(),
            this->data_ptr,
        };
        return InterfaceView(handle);
    }

    template<typename InterfaceHolder,
             std::enable_if_t<std::conjunction_v<is_interface_holder_type<InterfaceHolder>,
                                                 is_interface_static_castable_to<InterfaceHolder>>,
                              int> = 0>
    operator InterfaceHolder() const &
    {
        typename InterfaceHolder::abi_type handle = {
            this->interface_static_cast_to<InterfaceHolder>(),
            tobj_dup(this->data_ptr),
        };
        return InterfaceHolder(handle);
    }

    template<typename BaseBlock, typename... InterfaceBases,
             std::enable_if_t<std::is_base_of_v<BaseBlock, DataBlock> &&
                                  (is_interface_static_castable_to_v<InterfaceBases> && ...),
                              int> = 0>
    operator object_view<BaseBlock, InterfaceBases...>() const &
    {
        return object_view<BaseBlock, InterfaceBases...>(this->data_ptr,
                                                         this->interface_static_cast_to<InterfaceBases>()...);
    }

    template<typename BaseBlock, typename... InterfaceBases,
             std::enable_if_t<std::is_base_of_v<BaseBlock, DataBlock> &&
                                  (is_interface_static_castable_to_v<InterfaceBases> && ...),
                              int> = 0>
    operator object_holder<BaseBlock, InterfaceBases...>() const &
    {
        return object_holder<BaseBlock, InterfaceBases...>(static_cast<DataBlock *>(tobj_dup(this->data_ptr)),
                                                           this->interface_static_cast_to<InterfaceBases>()...);
    }

public:
    explicit operator bool() const &
    {
        return this->data_ptr != nullptr;
    }

    template<typename T = DataBlock, std::enable_if_t<is_impl_block_type_v<T>, int> = 0>
    typename T::impl_type *get() const
    {
        return this->data_ptr->get_impl_ptr();
    }

    template<typename T = DataBlock, std::enable_if_t<is_impl_block_type_v<T>, int> = 0>
    typename T::impl_type *operator->() const
    {
        return this->get();
    }

    template<typename T = DataBlock, std::enable_if_t<is_impl_block_type_v<T>, int> = 0>
    typename T::impl_type &operator*() const
    {
        return *this->get();
    }

    template<typename... Args>
    decltype(auto) operator()(Args &&...args) const
    {
        return this->get()->operator()(std::forward<Args>(args)...);
    }
};

template<typename DataBlock, typename... InterfaceTypes>
struct object_holder : public object_view<DataBlock, InterfaceTypes...> {
    template<typename InterfaceDest>
    struct is_interface_static_castable_to
        : is_vtable_static_castable_to_from_any<typename InterfaceDest::vtable_type,
                                                typename InterfaceTypes::vtable_type...> {};

    template<typename InterfaceDest>
    static constexpr bool is_interface_static_castable_to_v = is_interface_static_castable_to<InterfaceDest>::value;

    template<typename InterfaceDest>
    typename InterfaceDest::vtable_type const *interface_static_cast_to() const
    {
        return std::apply(vtable_static_cast_to_from_any<typename InterfaceDest::vtable_type,
                                                         typename InterfaceTypes::vtable_type...>,
                          this->vtbl_ptr_tuple);
    }

    object_holder() : object_view<DataBlock, InterfaceTypes...>()
    {
    }

    object_holder(DataBlock *other_data_ptr,
                  std::tuple<typename InterfaceTypes::vtable_type const *...> other_vtbl_ptr_tuple)
        : object_view<DataBlock, InterfaceTypes...>(other_data_ptr, other_vtbl_ptr_tuple)
    {
    }

    explicit object_holder(DataBlock *other_data_ptr, typename InterfaceTypes::vtable_type const *...other_vtbl_ptrs)
        : object_view<DataBlock, InterfaceTypes...>(other_data_ptr, other_vtbl_ptrs...)
    {
    }

    object_holder &operator=(object_holder other)
    {
        std::swap(this->data_ptr, other.data_ptr);
        std::swap(this->vtbl_ptr_tuple, other.vtbl_ptr_tuple);
        return *this;
    }

    ~object_holder()
    {
        tobj_drop(this->data_ptr);
    }

    object_holder(object_view<DataBlock, InterfaceTypes...> const &other)
        : object_holder(static_cast<DataBlock *>(tobj_dup(other.data_ptr)), other.vtbl_ptr_tuple)
    {
    }

    object_holder(object_holder<DataBlock, InterfaceTypes...> const &other)
        : object_holder(static_cast<DataBlock *>(tobj_dup(other.data_ptr)), other.vtbl_ptr_tuple)
    {
    }

    object_holder(object_holder<DataBlock, InterfaceTypes...> &&other)
        : object_holder(std::exchange(other.data_ptr, nullptr), other.vtbl_ptr_tuple)
    {
    }

    template<typename InterfaceView,
             std::enable_if_t<std::conjunction_v<is_interface_view_type<InterfaceView>,
                                                 is_interface_static_castable_to<InterfaceView>>,
                              int> = 0>
    operator InterfaceView() const &
    {
        typename InterfaceView::abi_type handle = {
            this->interface_static_cast_to<InterfaceView>(),
            this->data_ptr,
        };
        return InterfaceView(handle);
    }

    template<typename InterfaceHolder,
             std::enable_if_t<std::conjunction_v<is_interface_holder_type<InterfaceHolder>,
                                                 is_interface_static_castable_to<InterfaceHolder>>,
                              int> = 0>
    operator InterfaceHolder() const &
    {
        typename InterfaceHolder::abi_type handle = {
            this->interface_static_cast_to<InterfaceHolder>(),
            tobj_dup(this->data_ptr),
        };
        return InterfaceHolder(handle);
    }

    template<typename InterfaceHolder,
             std::enable_if_t<std::conjunction_v<is_interface_holder_type<InterfaceHolder>,
                                                 is_interface_static_castable_to<InterfaceHolder>>,
                              int> = 0>
    operator InterfaceHolder() &&
    {
        typename InterfaceHolder::abi_type handle = {
            this->interface_static_cast_to<InterfaceHolder>(),
            std::exchange(this->data_ptr, nullptr),
        };
        return InterfaceHolder(handle);
    }

    template<typename BaseBlock, typename... InterfaceBases,
             std::enable_if_t<std::is_base_of_v<BaseBlock, DataBlock> &&
                                  (is_interface_static_castable_to_v<InterfaceBases> && ...),
                              int> = 0>
    operator object_view<BaseBlock, InterfaceBases...>() const &
    {
        return object_view<BaseBlock, InterfaceBases...>(this->data_ptr,
                                                         this->interface_static_cast_to<InterfaceBases>()...);
    }

    template<typename BaseBlock, typename... InterfaceBases,
             std::enable_if_t<std::is_base_of_v<BaseBlock, DataBlock> &&
                                  (is_interface_static_castable_to_v<InterfaceBases> && ...),
                              int> = 0>
    operator object_holder<BaseBlock, InterfaceBases...>() const &
    {
        return object_holder<BaseBlock, InterfaceBases...>(static_cast<DataBlock *>(tobj_dup(this->data_ptr)),
                                                           this->interface_static_cast_to<InterfaceBases>()...);
    }

    template<typename BaseBlock, typename... InterfaceBases,
             std::enable_if_t<std::is_base_of_v<BaseBlock, DataBlock> &&
                                  (is_interface_static_castable_to_v<InterfaceBases> && ...),
                              int> = 0>
    operator object_holder<BaseBlock, InterfaceBases...>() &&
    {
        return object_holder<BaseBlock, InterfaceBases...>(std::exchange(this->data_ptr, nullptr),
                                                           this->interface_static_cast_to<InterfaceBases>()...);
    }
};

template<typename... InterfaceTypes>
using interface_view = object_view<DataBlockHead, InterfaceTypes...>;
template<typename... InterfaceTypes>
using interface_holder = object_holder<DataBlockHead, InterfaceTypes...>;

using data_view = interface_view<>;
using data_holder = interface_holder<>;

inline bool operator==(data_view lhs, data_view rhs)
{
    return lhs.data_ptr->rtti_ptr->same_fptr(lhs.data_ptr, rhs.data_ptr);
}
}  // namespace taihe

template<typename Impl, typename... InterfaceTypes>
struct std::hash<taihe::object_holder<Impl, InterfaceTypes...>> {
    std::size_t operator()(taihe::object_view<Impl, InterfaceTypes...> val) const noexcept
    {
        return val.data_ptr->rtti_ptr->hash_fptr(val.data_ptr);
    }
};

namespace taihe {
template<typename StaticDataBlock>
struct static_object_factory {
private:
    template<typename Holder>
    struct pack_unpacker;

    template<typename DataBlock, typename... InterfaceTypes>
    struct pack_unpacker<object_view<DataBlock, InterfaceTypes...>> {
        static constexpr TypeInfo static_rtti = {
            .hash_fptr = [](DataBlockHead *data_ptr) -> size_t {
                return static_cast<StaticDataBlock *>(data_ptr)->hash_impl();
            },
            .same_fptr = [](DataBlockHead *data_ptr, DataBlockHead *other_data_ptr) -> bool {
                return static_cast<StaticDataBlock *>(data_ptr)->same_impl(data_view(other_data_ptr));
            },
            .qivp_fptr = [](DataBlockHead *data_ptr, InterfaceId id) -> void const * {
                return static_cast<StaticDataBlock *>(data_ptr)->qivp_impl(id);
            },
        };

        static auto make_view(StaticDataBlock &ref)
        {
            StaticDataBlock *ptr = &ref;
            tobj_init_static(ptr, &static_rtti);
            return object_view<DataBlock, InterfaceTypes...>(ptr, ptr->template get_vtbl_ptr<InterfaceTypes>()...);
        }

        static auto make_holder(StaticDataBlock &ref)
        {
            StaticDataBlock *ptr = &ref;
            tobj_init_static(ptr, &static_rtti);
            return object_holder<DataBlock, InterfaceTypes...>(ptr, ptr->template get_vtbl_ptr<InterfaceTypes>()...);
        }
    };

public:
    static auto make_view(StaticDataBlock &ref)
    {
        return pack_unpacker<typename StaticDataBlock::view_type>::make_view(ref);
    }

    static auto make_holder(StaticDataBlock &ref)
    {
        return pack_unpacker<typename StaticDataBlock::view_type>::make_holder(ref);
    }
};

template<typename ShareableDataBlock>
struct shareable_object_factory {
private:
    template<typename Holder>
    struct pack_unpacker;

    template<typename DataBlock, typename... InterfaceTypes>
    struct pack_unpacker<object_view<DataBlock, InterfaceTypes...>> {
        static constexpr TypeInfo shareable_rtti = {
            .hash_fptr = [](DataBlockHead *data_ptr) -> size_t {
                return static_cast<ShareableDataBlock *>(data_ptr)->hash_impl();
            },
            .same_fptr = [](DataBlockHead *data_ptr, DataBlockHead *other_data_ptr) -> bool {
                return static_cast<ShareableDataBlock *>(data_ptr)->same_impl(data_view(other_data_ptr));
            },
            .qivp_fptr = [](DataBlockHead *data_ptr, InterfaceId id) -> void const * {
                return static_cast<ShareableDataBlock *>(data_ptr)->qivp_impl(id);
            },
            .free_fptr = [](DataBlockHead *data_ptr) -> void {
                delete static_cast<ShareableDataBlock *>(data_ptr);
            },
        };

        template<typename... Args>
        static auto make_holder(Args &&...args)
        {
            ShareableDataBlock *ptr = new ShareableDataBlock(std::forward<Args>(args)...);
            tobj_init_shareable(ptr, &shareable_rtti);
            return object_holder<DataBlock, InterfaceTypes...>(ptr, ptr->template get_vtbl_ptr<InterfaceTypes>()...);
        }
    };

public:
    template<typename... Args>
    static auto make_holder(Args &&...args)
    {
        return pack_unpacker<typename ShareableDataBlock::view_type>::make_holder(std::forward<Args>(args)...);
    }
};

template<typename PromotableDataBlock>
struct promotable_object_factory {
private:
    template<typename Holder>
    struct pack_unpacker;

    template<typename DataBlock, typename... InterfaceTypes>
    struct pack_unpacker<object_view<DataBlock, InterfaceTypes...>> {
        static constexpr TypeInfo promotable_rtti = {
            .hash_fptr = [](DataBlockHead *data_ptr) -> size_t {
                return static_cast<PromotableDataBlock *>(data_ptr)->hash_impl();
            },
            .same_fptr = [](DataBlockHead *data_ptr, DataBlockHead *other_data_ptr) -> bool {
                return static_cast<PromotableDataBlock *>(data_ptr)->same_impl(data_view(other_data_ptr));
            },
            .qivp_fptr = [](DataBlockHead *data_ptr, InterfaceId id) -> void const * {
                return static_cast<PromotableDataBlock *>(data_ptr)->qivp_impl(id);
            },
            .promote_fptr = [](DataBlockHead *data_ptr) -> DataBlockHead * {
                object_holder<DataBlock> promoted = static_cast<PromotableDataBlock *>(data_ptr)->get_promoted();
                return std::exchange(promoted.data_ptr, nullptr);
            },
        };

        static auto make_view(PromotableDataBlock &ref)
        {
            PromotableDataBlock *ptr = &ref;
            tobj_init_promotable(ptr, &promotable_rtti);
            return object_view<DataBlock, InterfaceTypes...>(ptr, ptr->template get_vtbl_ptr<InterfaceTypes>()...);
        }
    };

public:
    static auto make_view(PromotableDataBlock &promotable_ref)
    {
        return pack_unpacker<typename PromotableDataBlock::view_type>::make_view(promotable_ref);
    }
};

template<typename PromotableDataBlock>
struct scoped_view
    : private PromotableDataBlock
    , public PromotableDataBlock::view_type {
    template<typename... Args>
    explicit scoped_view(Args &&...args)
        : PromotableDataBlock(std::forward<Args>(args)...)
        , PromotableDataBlock::view_type(promotable_object_factory<PromotableDataBlock>::make_view(*this))
    {
    }

    scoped_view(scoped_view const &) = delete;
    scoped_view(scoped_view &&) = delete;
    scoped_view &operator=(scoped_view const &) = delete;
    scoped_view &operator=(scoped_view &&) = delete;
};
}  // namespace taihe

///////////////////////////////////////////////////////////
// Customization point for hash and same implementations //
///////////////////////////////////////////////////////////

namespace taihe {
template<typename Impl, typename Enabled = void>
struct hash_impl_t {
    std::size_t operator()(data_view val) const
    {
        return reinterpret_cast<std::size_t>(val.data_ptr);
    }
};

template<typename Impl, typename Enabled = void>
struct same_impl_t {
    bool operator()(data_view lhs, data_view rhs) const
    {
        return lhs.data_ptr == rhs.data_ptr;
    }
};

template<typename Impl>
constexpr inline hash_impl_t<Impl> hash_impl;

template<typename Impl>
constexpr inline same_impl_t<Impl> same_impl;
}  // namespace taihe

//////////////////////////////////////////////////
// Helper Function To Create Impl Holder Object //
//////////////////////////////////////////////////

namespace taihe {
template<typename ImplBlock, typename... RichInterfaceTypes>
struct with_typeinfo : ImplBlock {
    static_assert(is_impl_block_type_v<ImplBlock>, "ImplBlock must be a valid impl block type.");

    using view_type = object_view<ImplBlock, RichInterfaceTypes...>;

    template<typename... Args>
    explicit with_typeinfo(Args &&...args) : ImplBlock(std::forward<Args>(args)...)
    {
    }

    template<typename RichInterfaceType>
    typename RichInterfaceType::vtable_type const *get_vtbl_ptr() const
    {
        static_assert((std::is_same_v<RichInterfaceType, RichInterfaceTypes> || ...),
                      "Only can use supported interface types.");

        return &RichInterfaceType::template vtbl_impl<ImplBlock>;
    }

    void const *qivp_impl(InterfaceId id) const
    {
        void const *dest_vtbl_ptr = nullptr;
        bool success = ([&dest_vtbl_ptr, id] {
            void const *cand_vtbl_ptr = RichInterfaceTypes::template qivp_impl<ImplBlock>(id);
            if (cand_vtbl_ptr) {
                dest_vtbl_ptr = cand_vtbl_ptr;
                return true;
            }
            return false;
        }() || ...);
        return success ? dest_vtbl_ptr : nullptr;
    }

    size_t hash_impl()
    {
        return taihe::hash_impl<typename ImplBlock::impl_type>(object_view<ImplBlock>(this));
    }

    bool same_impl(data_view other)
    {
        return taihe::same_impl<typename ImplBlock::impl_type>(object_view<ImplBlock>(this), other);
    }
};

template<typename Impl>
struct impl_block : DataBlockHead {
    using impl_type = Impl;

    template<typename... Args>
    explicit impl_block(std::in_place_t, Args &&...args) : impl(std::forward<Args>(args)...)
    {
    }

    impl_type *get_impl_ptr()
    {
        return &impl;
    }

private:
    Impl impl;
};

template<typename Impl, typename... InterfaceTypes>
using impl_block_with_typeinfo = with_typeinfo<impl_block<Impl>, InterfaceTypes...>;

template<typename Impl, typename... InterfaceTypes>
using impl_view = object_view<impl_block<Impl>, InterfaceTypes...>;
template<typename Impl, typename... InterfaceTypes>
using impl_holder = object_holder<impl_block<Impl>, InterfaceTypes...>;

template<typename PromotableDataBlock, typename DataBlock>
struct enable_cached {
    object_holder<DataBlock> cache;

    object_holder<DataBlock> get_promoted()
    {
        if (!cache) {
            cache = static_cast<PromotableDataBlock *>(this)->create_promoted();
        }
        return cache;
    }
};

template<typename PromotableDataBlock, typename DataBlock, typename ShareableDataBlock = PromotableDataBlock>
struct enable_cached_copy_promotable : enable_cached<PromotableDataBlock, DataBlock> {
    object_holder<DataBlock> create_promoted()
    {
        return shareable_object_factory<ShareableDataBlock>::make_holder(*static_cast<PromotableDataBlock *>(this));
    }
};

template<typename Impl, typename... InterfaceTypes, typename... Args>
auto make_holder(Args &&...args)
{
    return shareable_object_factory<impl_block_with_typeinfo<Impl, InterfaceTypes...>>::make_holder(
        std::in_place, std::forward<Args>(args)...);
}

template<typename... InterfaceTypes, typename Impl>
auto into_holder(Impl impl)
{
    return make_holder<Impl, InterfaceTypes...>(std::move(impl));
}

template<typename ShareableDataBlock>
struct cached_copy_promotable
    : ShareableDataBlock
    , enable_cached_copy_promotable<cached_copy_promotable<ShareableDataBlock>,
                                    typename ShareableDataBlock::view_type::data_block_type, ShareableDataBlock> {
    template<typename... Args>
    explicit cached_copy_promotable(Args &&...args) : ShareableDataBlock(std::forward<Args>(args)...)
    {
    }
};

template<typename Impl, typename... InterfaceTypes, typename... Args>
auto make_view(Args &&...args)
{
    return scoped_view<cached_copy_promotable<impl_block_with_typeinfo<Impl, InterfaceTypes...>>>(
        std::in_place, std::forward<Args>(args)...);
}

template<typename... InterfaceTypes, typename Impl>
auto into_view(Impl impl)
{
    return make_view<Impl, InterfaceTypes...>(std::move(impl));
}
}  // namespace taihe

#endif  // TAIHE_OBJECT_HPP
