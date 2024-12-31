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
}

template<typename Impl>
struct WithDataBlockHead : DataBlockHead, Impl {};

template<typename FTable, typename Impl>
struct FTableImpl {};

template<typename VTable, typename Impl>
struct VTableImpl {};

template<typename RTTI, typename Impl>
struct RTTIImpl {};

template<typename Impl>
struct TypeTag {};

template<typename Impl>
TypeTag<Impl> type_tag;
}
