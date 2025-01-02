#pragma once

#include <array>

#include <taihe/common.hpp>
#include <taihe/object.abi.h>

namespace taihe::core {
struct DataOwner;
struct DataRef;

struct DataOwner {
    DataBlockHead* m_handle;

    DataOwner(DataBlockHead* other_handle);
    ~DataOwner();
    DataOwner(DataOwner && other);
    DataOwner(DataOwner const& other);
    DataOwner(DataRef const& other);
    DataOwner& operator=(DataOwner other);
};

struct DataRef {
    DataBlockHead* m_handle;

    DataRef(DataBlockHead* other_handle);
    ~DataRef();
    DataRef(DataOwner const& other);
    DataRef(DataRef const& other);
    DataRef& operator=(DataRef other);
};

DataOwner::DataOwner(DataBlockHead* other_handle)
    : m_handle(other_handle) {}

DataOwner::~DataOwner() {
    tobj_drop(this->m_handle);
}

DataOwner::DataOwner(DataOwner && other)
    : m_handle(other.m_handle) {
    other.m_handle = nullptr;
}

DataOwner::DataOwner(DataOwner const& other)
    : m_handle(tobj_dup(other.m_handle)) {}

DataOwner::DataOwner(DataRef const& other)
    : m_handle(tobj_dup(other.m_handle)) {}

DataOwner& DataOwner::operator=(DataOwner other) {
    std::swap(this->m_handle, other.m_handle);
    return *this;
}

DataRef::DataRef(DataBlockHead* other_handle)
    : m_handle(other_handle) {}

DataRef::~DataRef() {}

DataRef::DataRef(DataOwner const& other)
    : m_handle(other.m_handle) {}

DataRef::DataRef(DataRef const& other)
    : m_handle(other.m_handle) {}

DataRef& DataRef::operator=(DataRef other) {
    std::swap(this->m_handle, other.m_handle);
    return *this;
}

template<typename Impl>
struct WithDataBlockHead : DataBlockHead, Impl {
    template<typename... Args>
    WithDataBlockHead(TypeInfo const* rtti_ptr, TRefCount m_count, Args&&... args)
        : DataBlockHead{rtti_ptr, m_count}, Impl(std::forward<Args>(args)...) {}
};

template<typename FTable, typename Impl>
struct FTableImpl {};

template<typename VTable, typename Impl>
struct VTableImpl {};

template<typename RTTI, typename Impl>
struct RTTIImpl {};

template<typename InterfaceOwner>
struct OwnerInspector {};

template<typename InterfaceOwner, typename Impl, typename OwnerInspector<InterfaceOwner>::Type = nullptr, typename... Args>
InterfaceOwner makeInterface(Args&&... args) {
    return InterfaceOwner{{
        .vtbl_ptr = &VTableImpl<typename OwnerInspector<InterfaceOwner>::VTable, Impl>::vtbl,
        .data_ptr = new WithDataBlockHead<Impl>(
            reinterpret_cast<TypeInfo const*>(&RTTIImpl<typename OwnerInspector<InterfaceOwner>::RTTI, Impl>::rtti), 1,
            std::forward<Args>(args)...
        ),
    }};
}
}
