#pragma once

#include <array>

#include <taihe/common.hpp>
#include <taihe/object.abi.h>

namespace taihe::core {
struct data_holder;
struct data_view;

struct data_holder {
    DataBlockHead* m_handle;

    data_holder(DataBlockHead* other_handle);
    ~data_holder();
    data_holder(data_holder && other);
    data_holder(data_holder const& other);
    data_holder(data_view const& other);
    data_holder& operator=(data_holder other);
};

struct data_view {
    DataBlockHead* m_handle;

    data_view(DataBlockHead* other_handle);
    ~data_view();
    data_view(data_holder const& other);
    data_view(data_view const& other);
    data_view& operator=(data_view other);
};

data_holder::data_holder(DataBlockHead* other_handle)
    : m_handle(other_handle) {}

data_holder::~data_holder() {
    tobj_drop(this->m_handle);
}

data_holder::data_holder(data_holder && other)
    : m_handle(other.m_handle) {
    other.m_handle = nullptr;
}

data_holder::data_holder(data_holder const& other)
    : m_handle(tobj_dup(other.m_handle)) {}

data_holder::data_holder(data_view const& other)
    : m_handle(tobj_dup(other.m_handle)) {}

data_holder& data_holder::operator=(data_holder other) {
    std::swap(this->m_handle, other.m_handle);
    return *this;
}

data_view::data_view(DataBlockHead* other_handle)
    : m_handle(other_handle) {}

data_view::~data_view() {}

data_view::data_view(data_holder const& other)
    : m_handle(other.m_handle) {}

data_view::data_view(data_view const& other)
    : m_handle(other.m_handle) {}

data_view& data_view::operator=(data_view other) {
    std::swap(this->m_handle, other.m_handle);
    return *this;
}

template<typename Impl>
struct data_block_impl : DataBlockHead, Impl {
    template<typename... Args>
    data_block_impl(TypeInfo const* rtti_ptr, TRefCount m_count, Args&&... args)
        : DataBlockHead{rtti_ptr, m_count}, Impl(std::forward<Args>(args)...) {}
};

template<typename FTable, typename Impl>
struct ftable_impl {};

template<typename VTable, typename Impl>
struct vtable_impl {};

template<typename RTTI, typename Impl>
struct typeinfo_impl {};

template<typename InterfaceOwner>
struct interface_owner_traits {};

template<typename InterfaceOwner, typename Impl, typename interface_owner_traits<InterfaceOwner>::type = nullptr, typename... Args>
InterfaceOwner new_instance(Args&&... args) {
    return InterfaceOwner{{
        .vtbl_ptr = &vtable_impl<typename interface_owner_traits<InterfaceOwner>::vtable, Impl>::vtbl,
        .data_ptr = new data_block_impl<Impl>(
            reinterpret_cast<TypeInfo const*>(&typeinfo_impl<typename interface_owner_traits<InterfaceOwner>::typeinfo, Impl>::rtti), 1,
            std::forward<Args>(args)...
        ),
    }};
}
}
