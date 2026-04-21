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

//////////////////////
// Raw Data Handler //
//////////////////////

namespace taihe {
struct data_view;
struct data_holder;

struct data_view {
    DataBlockHead *data_ptr;

    explicit data_view(DataBlockHead *other_data_ptr) : data_ptr(other_data_ptr)
    {
    }
};

struct data_holder : public data_view {
    explicit data_holder(DataBlockHead *other_data_ptr) : data_view(other_data_ptr)
    {
    }

    data_holder &operator=(data_holder other)
    {
        std::swap(this->data_ptr, other.data_ptr);
        return *this;
    }

    ~data_holder()
    {
        tobj_drop(this->data_ptr);
    }

    data_holder(data_view const &other) : data_holder(tobj_dup(other.data_ptr))
    {
    }

    data_holder(data_holder const &other) : data_holder(tobj_dup(other.data_ptr))
    {
    }

    data_holder(data_holder &&other) : data_holder(other.data_ptr)
    {
        other.data_ptr = nullptr;
    }
};

inline bool operator==(data_view lhs, data_view rhs)
{
    return lhs.data_ptr->rtti_ptr->same_fptr(lhs.data_ptr, rhs.data_ptr);
}
}  // namespace taihe

template<>
struct std::hash<taihe::data_holder> {
    std::size_t operator()(taihe::data_view val) const
    {
        return val.data_ptr->rtti_ptr->hash_fptr(val.data_ptr);
    }
};

////////////////////////////////////////////////
// Data Block Definition And Helper Functions //
////////////////////////////////////////////////

namespace taihe {
template<typename Impl>
struct data_block : DataBlockHead {
    Impl impl;

    template<typename... Args>
    data_block(TypeInfo const *rtti_ptr, Args &&...args) : impl(std::forward<Args>(args)...)
    {
        tobj_init(this, rtti_ptr);
    }
};

template<typename Impl, typename... Args>
inline DataBlockHead *make_data_ptr(TypeInfo const *rtti_ptr, Args &&...args)
{
    return new data_block<Impl>(rtti_ptr, std::forward<Args>(args)...);
}

template<typename Impl>
inline void free_data_ptr(struct DataBlockHead *data_ptr)
{
    delete static_cast<data_block<Impl> *>(data_ptr);
}

template<typename Impl>
inline Impl *cast_data_ptr(struct DataBlockHead *data_ptr)
{
    return &static_cast<data_block<Impl> *>(data_ptr)->impl;
}
}  // namespace taihe

///////////////////////////////////////
// Specific Impl Type Object Handler //
///////////////////////////////////////

namespace taihe {
template<typename Impl>
struct type_view;
template<typename Impl>
struct type_holder;

template<typename Impl>
struct type_view {
    DataBlockHead *data_ptr;

    explicit type_view(DataBlockHead *other_data_ptr) : data_ptr(other_data_ptr)
    {
    }

    operator data_view() const &
    {
        return data_view(this->data_ptr);
    }

    operator data_holder() const &
    {
        return data_holder(tobj_dup(this->data_ptr));
    }

public:
    Impl *operator->() const
    {
        return cast_data_ptr<Impl>(this->data_ptr);
    }

    Impl &operator*() const
    {
        return *cast_data_ptr<Impl>(this->data_ptr);
    }

    template<typename... Args>
    decltype(auto) operator()(Args &&...args) const
    {
        return cast_data_ptr<Impl>(this->data_ptr)->operator()(std::forward<Args>(args)...);
    }
};

template<typename Impl>
struct type_holder : public type_view<Impl> {
    explicit type_holder(DataBlockHead *other_data_ptr) : type_view<Impl>(other_data_ptr)
    {
    }

    type_holder &operator=(type_holder other)
    {
        std::swap(this->data_ptr, other.data_ptr);
        return *this;
    }

    ~type_holder()
    {
        tobj_drop(this->data_ptr);
    }

    type_holder(type_view<Impl> const &other) : type_holder(tobj_dup(other.data_ptr))
    {
    }

    type_holder(type_holder<Impl> const &other) : type_holder(tobj_dup(other.data_ptr))
    {
    }

    type_holder(type_holder<Impl> &&other) : type_holder(other.data_ptr)
    {
        other.data_ptr = nullptr;
    }

    operator data_view() const &
    {
        return data_view(this->data_ptr);
    }

    operator data_holder() const &
    {
        return data_holder(tobj_dup(this->data_ptr));
    }

    operator data_holder() &&
    {
        return data_holder(std::exchange(this->data_ptr, nullptr));
    }
};

template<typename Impl>
inline bool operator==(type_view<Impl> lhs, type_view<Impl> rhs)
{
    return lhs.data_ptr->rtti_ptr->same_fptr(lhs.data_ptr, rhs.data_ptr);
}
}  // namespace taihe

template<typename Impl>
struct std::hash<taihe::type_holder<Impl>> {
    std::size_t operator()(taihe::type_view<Impl> val) const
    {
        return val.data_ptr->rtti_ptr->hash_fptr(val.data_ptr);
    }
};

/////////////////////////////////////////////////
// Hash And Same Impl For Data Pointer Handler //
/////////////////////////////////////////////////

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

template<typename Impl>
inline std::size_t hash_data_ptr(struct DataBlockHead *val_data_ptr)
{
    return hash_impl<Impl>(data_view(val_data_ptr));
}

template<typename Impl>
inline bool same_data_ptr(struct DataBlockHead *lhs_data_ptr, struct DataBlockHead *rhs_data_ptr)
{
    return same_impl<Impl>(data_view(lhs_data_ptr), data_view(rhs_data_ptr));
}
}  // namespace taihe

//////////////////////////////////////////////////////
// Specific Impl Type With Interface Object Handler //
//////////////////////////////////////////////////////

namespace taihe {
template<typename Impl, typename... InterfaceTypes>
struct impl_view;
template<typename Impl, typename... InterfaceTypes>
struct impl_holder;

template<typename Impl, typename... InterfaceTypes>
struct impl_view {
    DataBlockHead *data_ptr;

    explicit impl_view(DataBlockHead *other_data_ptr) : data_ptr(other_data_ptr)
    {
    }

    template<typename InterfaceView, std::enable_if_t<!InterfaceView::is_holder, int> = 0>
    operator InterfaceView() const &
    {
        return InterfaceView({
            this->template get_vtbl_ptr<InterfaceView>(),
            this->data_ptr,
        });
    }

    template<typename InterfaceHolder, std::enable_if_t<InterfaceHolder::is_holder, int> = 0>
    operator InterfaceHolder() const &
    {
        return InterfaceHolder({
            this->template get_vtbl_ptr<InterfaceHolder>(),
            tobj_dup(this->data_ptr),
        });
    }

    operator data_view() const &
    {
        return data_view(this->data_ptr);
    }

    operator data_holder() const &
    {
        return data_holder(tobj_dup(this->data_ptr));
    }

    operator type_view<Impl>() const &
    {
        return type_view<Impl>(this->data_ptr);
    }

    operator type_holder<Impl>() const &
    {
        return type_holder<Impl>(tobj_dup(this->data_ptr));
    }

public:
    Impl *operator->() const
    {
        return cast_data_ptr<Impl>(this->data_ptr);
    }

    Impl &operator*() const
    {
        return *cast_data_ptr<Impl>(this->data_ptr);
    }

    template<typename... Args>
    decltype(auto) operator()(Args &&...args) const
    {
        return cast_data_ptr<Impl>(this->data_ptr)->operator()(std::forward<Args>(args)...);
    }

public:
    static inline void const *qiid(InterfaceId id)
    {
        void const *dest_vtbl_ptr;
        bool success = ([&] {
            using InterfaceType = InterfaceTypes;
            void const *cand_vtbl_ptr = InterfaceType::template qiid_impl<Impl>(id);
            if (cand_vtbl_ptr) {
                dest_vtbl_ptr = cand_vtbl_ptr;
                return true;
            }
            return false;
        }() || ...);
        return success ? dest_vtbl_ptr : nullptr;
    }

    static constexpr TypeInfo rtti = {
        .free_fptr = &free_data_ptr<Impl>,
        .hash_fptr = &hash_data_ptr<Impl>,
        .same_fptr = &same_data_ptr<Impl>,
        .qiid_fptr = &qiid,
    };

    template<typename InterfaceDest,
             std::enable_if_t<
                 (std::is_convertible_v<typename InterfaceTypes::view_type, typename InterfaceDest::view_type> || ...),
                 int> = 0>
    static inline typename InterfaceDest::vtable_type const *get_vtbl_ptr()
    {
        typename InterfaceDest::vtable_type const *dest_vtbl_ptr;
        bool success = ([&] {
            using InterfaceType = InterfaceTypes;
            if constexpr (std::is_convertible_v<typename InterfaceType::view_type, typename InterfaceDest::view_type>) {
                typename InterfaceType::vtable_type const *type_vtbl_ptr = &InterfaceType::template vtbl_impl<Impl>;
                typename InterfaceType::view_type type_obj({type_vtbl_ptr, nullptr});
                typename InterfaceDest::view_type dest_obj = type_obj;
                dest_vtbl_ptr = dest_obj.m_handle.vtbl_ptr;
                return true;
            }
            return false;
        }() || ...);
        return success ? dest_vtbl_ptr : nullptr;
    }
};

template<typename Impl, typename... InterfaceTypes>
struct impl_holder : public impl_view<Impl, InterfaceTypes...> {
    using impl_view<Impl, InterfaceTypes...>::rtti;

    explicit impl_holder(DataBlockHead *other_data_ptr) : impl_view<Impl, InterfaceTypes...>(other_data_ptr)
    {
    }

    template<typename... Args>
    static impl_holder make(Args &&...args)
    {
        return impl_holder(make_data_ptr<Impl>(&rtti, std::forward<Args>(args)...));
    }

    impl_holder &operator=(impl_holder other)
    {
        std::swap(this->data_ptr, other.data_ptr);
        return *this;
    }

    ~impl_holder()
    {
        tobj_drop(this->data_ptr);
    }

    impl_holder(impl_view<Impl, InterfaceTypes...> const &other) : impl_holder(tobj_dup(other.data_ptr))
    {
    }

    impl_holder(impl_holder<Impl, InterfaceTypes...> const &other) : impl_holder(tobj_dup(other.data_ptr))
    {
    }

    impl_holder(impl_holder<Impl, InterfaceTypes...> &&other) : impl_holder(std::exchange(other.data_ptr, nullptr))
    {
    }

    template<typename InterfaceView, std::enable_if_t<!InterfaceView::is_holder, int> = 0>
    operator InterfaceView() const &
    {
        return InterfaceView({
            this->template get_vtbl_ptr<InterfaceView>(),
            this->data_ptr,
        });
    }

    template<typename InterfaceHolder, std::enable_if_t<InterfaceHolder::is_holder, int> = 0>
    operator InterfaceHolder() const &
    {
        return InterfaceHolder({
            this->template get_vtbl_ptr<InterfaceHolder>(),
            tobj_dup(this->data_ptr),
        });
    }

    template<typename InterfaceHolder, std::enable_if_t<InterfaceHolder::is_holder, int> = 0>
    operator InterfaceHolder() &&
    {
        return InterfaceHolder({
            this->template get_vtbl_ptr<InterfaceHolder>(),
            std::exchange(this->data_ptr, nullptr),
        });
    }

    operator data_view() const &
    {
        return data_view(this->data_ptr);
    }

    operator data_holder() const &
    {
        return data_holder(tobj_dup(this->data_ptr));
    }

    operator data_holder() &&
    {
        return data_holder(std::exchange(this->data_ptr, nullptr));
    }

    operator type_view<Impl>() const &
    {
        return type_view<Impl>(this->data_ptr);
    }

    operator type_holder<Impl>() const &
    {
        return type_holder<Impl>(tobj_dup(this->data_ptr));
    }

    operator type_holder<Impl>() &&
    {
        return type_holder<Impl>(std::exchange(this->data_ptr, nullptr));
    }
};

template<typename Impl, typename... InterfaceTypes>
inline bool operator==(impl_view<Impl, InterfaceTypes...> lhs, impl_view<Impl, InterfaceTypes...> rhs)
{
    return data_view(lhs) == data_view(rhs);
}
}  // namespace taihe

template<typename Impl, typename... InterfaceTypes>
struct std::hash<taihe::impl_holder<Impl, InterfaceTypes...>> {
    std::size_t operator()(taihe::data_view val) const noexcept
    {
        return std::hash<taihe::data_holder>()(val);
    }
};

//////////////////////////////////////////////////
// Helper Function To Create Impl Holder Object //
//////////////////////////////////////////////////

namespace taihe {
template<typename Impl, typename... InterfaceTypes, typename... Args>
inline auto make_holder(Args &&...args)
{
    return impl_holder<Impl, InterfaceTypes...>::make(std::forward<Args>(args)...);
}

template<typename... InterfaceTypes, typename Impl>
inline auto as_holder(Impl &&impl)
{
    return make_holder<Impl, InterfaceTypes...>(std::forward<Impl>(impl));
}
}  // namespace taihe

#endif  // TAIHE_OBJECT_HPP
