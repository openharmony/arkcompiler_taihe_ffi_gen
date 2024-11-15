#pragma once

#include <array>

#include <taihe/common.hpp>
#include <taihe/object.abi.h>

namespace taihe::core {
struct InterfaceMapItem {
    void const *iid;
    void const *pvtbl;
};

struct CommonHandle;

struct RTTI {
    std::size_t length;
    void(*drop)(CommonHandle *pself);
    CommonHandle*(*dup)(CommonHandle *pself);
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

template<typename Self>
void Iobj_drop(CommonHandle *pself) {
    static_cast<Self *>(pself)->drop();
}

template<typename Self>
CommonHandle *Iobj_dup(CommonHandle *pself) {
    return static_cast<Self *>(static_cast<Self *>(pself)->dup());
}

template<typename T, std::size_t S>
constexpr void concatArraysInPlace(std::array<T, S> &r, std::size_t j) {}

template<typename T, std::size_t S, std::size_t N, std::size_t... Ns>
constexpr void concatArraysInPlace(std::array<T, S> &r, std::size_t j, std::array<T, N> const &a, std::array<T, Ns> const &...as) {
    for (std::size_t i = 0; i < N; i++, j++) {
        r[j] = a[i];
    }
    concatArraysInPlace(r, j, as...);
}

constexpr bool operator==(const InterfaceMapItem& lhs, const InterfaceMapItem& rhs) {
    return lhs.iid == rhs.iid;
}

template <std::size_t N>
constexpr std::size_t uniqueArrayInPlace(std::array<InterfaceMapItem, N>& arr) {
    std::size_t uniqueCount = 1;
    for (std::size_t i = 1; i < N; ++i) {
        bool isDuplicate = false;
        for (std::size_t j = 0; j < uniqueCount; ++j) {
            if (arr[i] == arr[j]) {
                isDuplicate = true;
                break;
            }
        }
        if (!isDuplicate) {
            arr[uniqueCount] = arr[i];
            ++uniqueCount;
        }
    }
    return uniqueCount;
}

template<typename Self, typename T, std::size_t... Ns>
constexpr auto buildRtti(std::array<T, Ns> const &...as) {
    struct {
        std::size_t length;
        void (*drop)(CommonHandle *pself);
        CommonHandle*(*dup)(CommonHandle *pself);
        std::array<InterfaceMapItem, (Ns + ...)> imap;
    } r = {(Ns + ...), &Iobj_drop<Self>, &Iobj_dup<Self>, {}};
    concatArraysInPlace(r.imap, 0, as...);
    r.length = uniqueArrayInPlace(r.imap);
    return r;
}

template<typename Self, template<typename> typename... TypeInfos>
struct Handle : CommonHandle {
    static constexpr auto rtti = buildRtti<Self>(TypeInfos<Self>::imap...);

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

template<typename FatPtr>
struct Owner : FatPtr {
    Owner<FatPtr>(FatPtr other)
        : FatPtr(other) {}

    operator FatPtr() && {
        return {
            this->pvtbl,
            std::exchange(this->pself, nullptr),
        };
    }

    template<typename Self>
    Owner<FatPtr>(OwnerPtr<Self> &&other) {
        this->pvtbl = static_cast<typename FatPtr::VTable const *>(Self::template staticQueryInterfaceResult<FatPtr::iid>);
        this->pself = std::exchange(other.pself, nullptr);
    }

    Owner<FatPtr>(Owner<FatPtr> &&other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = std::exchange(other.pself, nullptr);
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, int, void> = 0>
    Owner<FatPtr>(Owner<IFrom> &&other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = std::exchange(other.pself, nullptr);
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, void, int> = 0>
    explicit Owner<FatPtr>(Owner<IFrom> &&other) {
        this->pself = (this->pvtbl = static_cast<typename FatPtr::VTable const *>(other.pself->dynamicQueryInterface(FatPtr::iid)))
                          ? std::exchange(other.pself, nullptr)
                          : nullptr;
    }

    ~Owner<FatPtr>() {
        if (this->pself) {
            this->drop();
        }
    }

    Owner<FatPtr> &operator=(Owner<FatPtr> other) {
        std::swap(this->pvtbl, other.pvtbl);
        std::swap(this->pself, other.pself);
        return *this;
    }
};

template<typename FatPtr>
struct Ref : FatPtr {
    Ref<FatPtr>(FatPtr other)
        : FatPtr(other) {}

    operator FatPtr() {
        return {
            this->pvtbl,
            this->pself,
        };
    }

    template<typename Self>
    Ref<FatPtr>(RefPtr<Self> const &other) {
        this->pvtbl = static_cast<typename FatPtr::VTable const *>(Self::template staticQueryInterfaceResult<FatPtr::iid>);
        this->pself = other.pself;
    }

    template<typename Self>
    Ref<FatPtr>(OwnerPtr<Self> const &other) {
        this->pvtbl = static_cast<typename FatPtr::VTable const *>(Self::template staticQueryInterfaceResult<FatPtr::iid>);
        this->pself = other.pself;
    }

    Ref<FatPtr>(Ref<FatPtr> const &other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = other.pself;
    }

    Ref<FatPtr>(Owner<FatPtr> const &other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = other.pself;
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, int, void> = 0>
    Ref<FatPtr>(Ref<IFrom> const &other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = other.pself;
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, int, void> = 0>
    Ref<FatPtr>(Owner<IFrom> const &other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = other.pself;
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, void, int> = 0>
    explicit Ref<FatPtr>(Ref<IFrom> const &other) {
        this->pself = (this->pvtbl = static_cast<typename FatPtr::VTable const *>(other.pself->dynamicQueryInterface(FatPtr::iid)))
                          ? other.pself
                          : nullptr;
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, void, int> = 0>
    explicit Ref<FatPtr>(Owner<IFrom> const &other) {
        this->pself = (this->pvtbl = static_cast<typename FatPtr::VTable const *>(other.pself->dynamicQueryInterface(FatPtr::iid)))
                          ? other.pself
                          : nullptr;
    }

    ~Ref<FatPtr>() {}

    Ref<FatPtr> &operator=(Ref<FatPtr> other) = delete;
};
}
