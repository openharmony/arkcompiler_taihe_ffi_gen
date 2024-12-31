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
}

struct InterfaceMapItem {
    void const *iid;
    void const *pvtbl;
};

struct RTTI {
    std::size_t length;
    InterfaceMapItem imap[];
};

struct CommonHandle {
    RTTI const *prtti;

    void const *dynamicQueryInterface(void const *iid) {
        for (std::size_t i = 0; i < prtti->length; i++) {
            if (iid == prtti->imap[i].iid) {
                return prtti->imap[i].pvtbl;
            }
        }
        return nullptr;
    }
};

template<typename T, std::size_t S>
constexpr void concatArraysInPlace(std::array<T, S> &r, std::size_t j) {}

template<typename T, std::size_t S, std::size_t N, std::size_t... Ns>
constexpr void concatArraysInPlace(std::array<T, S> &r, std::size_t j, std::array<T, N> const &a, std::array<T, Ns> const &...as) {
    for (std::size_t i = 0; i < N; i++, j++) {
        r[j] = a[i];
    }
    concatArraysInPlace(r, j, as...);
}

template<typename T, std::size_t... Ns>
constexpr auto concatArrays(std::array<T, Ns> const &...as) {
    std::array<T, (Ns + ...)> r = {};
    concatArraysInPlace(r, 0, as...);
    return r;
}

template<typename Self, template<typename> typename... TypeInfos>
struct Handle : CommonHandle {
    static constexpr struct {
        std::size_t length = (TypeInfos<Self>::imap.size() + ...);
        std::array<InterfaceMapItem, (TypeInfos<Self>::imap.size() + ...)> imap = concatArrays(TypeInfos<Self>::imap...);
    } rtti = {};

    Handle()
        : CommonHandle{(RTTI *)&rtti} {}

    static constexpr void const *staticQueryInterface(void const *iid) {
        for (std::size_t i = 0; i < rtti.length; i++) {
            if (iid == rtti.imap[i].iid) {
                return rtti.imap[i].pvtbl;
            }
        }
        throw std::logic_error("Static cast failed!");
    }

    template<void const *iid>
    static constexpr void const *staticQueryInterfaceResult = staticQueryInterface(iid);
};

template<typename Self>
struct OwnerPtr {
    Self *pself;

    OwnerPtr<Self>(Self *pself)
        : pself(pself) {}

    operator Self *() && {
        return std::exchange(this->pself, nullptr);
    }

    OwnerPtr<Self>(OwnerPtr<Self> &&other)
        : pself(std::exchange(other.pself, nullptr)) {}

    Self *operator->() {
        return this->pself;
    }

    ~OwnerPtr<Self>() {
        if (this->pself) {
            this->pself->drop();
        }
    }

    OwnerPtr<Self> &operator=(OwnerPtr<Self> other) {
        std::swap(this->pself, other.pself);
        return *this;
    }
};

template<typename Self>
struct RefPtr {
    Self *pself;

    RefPtr<Self>(Self *pself)
        : pself(pself) {}

    operator Self *() {
        return this->pself;
    }

    RefPtr<Self>(OwnerPtr<Self> const &other)
        : pself(other.pself) {}

    RefPtr<Self>(RefPtr<Self> const &other)
        : pself(other.pself) {}

    Self *operator->() {
        return this->pself;
    }

    ~RefPtr<Self>() {}

    RefPtr<Self> &operator=(RefPtr<Self> other) = delete;
};
