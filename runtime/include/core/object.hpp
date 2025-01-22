#pragma once

#include <array>
#include <exception>

#include <taihe/common.hpp>
#include <taihe/object.abi.h>
#include <type_traits>

namespace taihe::core {
template<typename ABIFromType, typename ABIIntoType>
struct convert_traits {
    static constexpr bool static_castable = false;
    static constexpr bool dynamic_castable = false;
};

template<typename ABIType>
struct info_container {};

template<typename InterfaceHolder>
struct interface_holder_traits {
    static constexpr bool value = false;
};

template<typename InterfaceShadow>
struct interface_shadow_traits {
    static constexpr bool value = false;
};

//////////////////////
// Raw Data Handler //
//////////////////////

struct data_holder;
struct data_shadow;

struct data_holder {
    DataBlockHead* m_handle;

    explicit data_holder(DataBlockHead* other_handle);
    ~data_holder();
    data_holder(data_holder&& other);
    data_holder(data_holder const& other);
    data_holder(data_shadow const& other);
    data_holder& operator=(data_holder other);
};

struct data_shadow {
    DataBlockHead* m_handle;

    explicit data_shadow(DataBlockHead* other_handle);
    ~data_shadow();
    data_shadow(data_shadow const& other);
    data_shadow(data_holder const& other);
    data_shadow& operator=(data_shadow other);
};

inline data_holder::data_holder(DataBlockHead* other_handle)
    : m_handle(other_handle) {}

inline data_holder::~data_holder() {
    tobj_drop(this->m_handle);
}

inline data_holder::data_holder(data_holder&& other)
    : m_handle(other.m_handle) {
    other.m_handle = nullptr;
}

inline data_holder::data_holder(data_holder const& other)
    : m_handle(tobj_dup(other.m_handle)) {}

inline data_holder::data_holder(data_shadow const& other)
    : m_handle(tobj_dup(other.m_handle)) {}

inline data_holder& data_holder::operator=(data_holder other) {
    std::swap(this->m_handle, other.m_handle);
    return *this;
}

inline data_shadow::data_shadow(DataBlockHead* other_handle)
    : m_handle(other_handle) {}

inline data_shadow::~data_shadow() {}

inline data_shadow::data_shadow(data_shadow const& other)
    : m_handle(other.m_handle) {}

inline data_shadow::data_shadow(data_holder const& other)
    : m_handle(other.m_handle) {}

inline data_shadow& data_shadow::operator=(data_shadow other) {
    std::swap(this->m_handle, other.m_handle);
    return *this;
}

///////////////////////////////////////
// Specific Impl Type Object Handler //
///////////////////////////////////////

template<typename Impl>
struct data_block_impl : DataBlockHead, Impl {
    template<typename... Args>
    data_block_impl(TypeInfo const* rtti_ptr, TRefCount m_count, Args&&... args)
        : DataBlockHead{rtti_ptr, m_count}, Impl(std::forward<Args>(args)...) {}
};

template<typename Impl>
inline static void delete_impl(DataBlockHead *data_ptr) {
    delete static_cast<::taihe::core::data_block_impl<Impl>*>(data_ptr);
}

template<typename T, uint64_t S>
constexpr void static_concat(T (&r)[S], uint64_t j) {}

template<typename T, uint64_t S, uint64_t N, uint64_t... Ns>
constexpr void static_concat(T (&r)[S], uint64_t j, T const (&a)[N], T const (&...as)[Ns]) {
    for (uint64_t i = 0; i < N; i++, j++) {
        r[j] = a[i];
    }
    static_concat(r, j, as...);
}

template<typename Impl, typename... InfoContainers>
struct impl_holder;

template<typename Impl, typename... InfoContainers>
struct impl_shadow;

template<typename... InfoContainers>
struct typeinfo_t {
    uint64_t version;
    void (*free_ptr)(struct DataBlockHead*);
    uint64_t len = (InfoContainers::dict_len + ... + 0);
    struct IdMapItem idmap[(InfoContainers::dict_len + ... + 1)] = {};
};

template<typename Impl, typename... InfoContainers>
struct typeinfo_impl {
    static constexpr typeinfo_t<InfoContainers...> get_rtti() {
        struct typeinfo_t<InfoContainers...> rtti = {0, &delete_impl<Impl>};
        static_concat(rtti.idmap, 0, InfoContainers::template typeinfo_space<Impl>::idmap...);
        return rtti;
    }

    static constexpr typeinfo_t<InfoContainers...> rtti = get_rtti();

    static constexpr void const* get_vtbl_ptr(void const *iid) {
        for (uint64_t i = 0; i < rtti.len; i++) {
            if (iid == rtti.idmap[i].id) {
                return rtti.idmap[i].vtbl_ptr;
            }
        }
        throw;
    }

    template<typename InfoContainer>
    static constexpr void const* vtbl_ptr = get_vtbl_ptr(InfoContainer::iid);
};

template<typename Impl, typename... InfoContainers>
struct impl_holder {
    using impl_type = Impl;
 
    data_block_impl<Impl>* m_handle;

    explicit impl_holder(data_block_impl<Impl>* other_handle)
        : m_handle(other_handle) {}

    ~impl_holder() {
        tobj_drop(this->m_handle);
    }

    impl_holder(impl_holder<Impl, InfoContainers...>&& other)
        : m_handle(other.m_handle) {
        other.m_handle = nullptr;
    }

    impl_holder(impl_holder<Impl, InfoContainers...> const& other)
        : m_handle(static_cast<data_block_impl<Impl>*>(tobj_dup(other.m_handle))) {}

    impl_holder(impl_shadow<Impl, InfoContainers...> const& other)
        : m_handle(static_cast<data_block_impl<Impl>*>(tobj_dup(other.m_handle))) {}

    template<typename InterfaceHolder, std::enable_if_t<interface_holder_traits<InterfaceHolder>::value, int> = 0>
    operator InterfaceHolder() && {
        using InfoContainer = typename interface_holder_traits<InterfaceHolder>::info_container;
        DataBlockHead* ret_handle = this->m_handle;
        this->m_handle = nullptr;
        return InterfaceHolder{{
            static_cast<typename InfoContainer::vtable_t const*>(typeinfo_impl<Impl, InfoContainers...>::template vtbl_ptr<InfoContainer>),
            ret_handle,
        }};
    }

    template<typename InterfaceHolder, std::enable_if_t<interface_holder_traits<InterfaceHolder>::value, int> = 0>
    operator InterfaceHolder() const& {
        using InfoContainer = typename interface_holder_traits<InterfaceHolder>::info_container;
        DataBlockHead* ret_handle = tobj_dup(this->m_handle);
        return InterfaceHolder{{
            static_cast<typename InfoContainer::vtable_t const*>(typeinfo_impl<Impl, InfoContainers...>::template vtbl_ptr<InfoContainer>),
            ret_handle,
        }};
    }

    template<typename InterfaceShadow, std::enable_if_t<interface_shadow_traits<InterfaceShadow>::value, int> = 0>
    operator InterfaceShadow() const& {
        using InfoContainer = typename interface_shadow_traits<InterfaceShadow>::info_container;
        DataBlockHead* ret_handle = this->m_handle;
        return InterfaceShadow{{
            static_cast<typename InfoContainer::vtable_t const*>(typeinfo_impl<Impl, InfoContainers...>::template vtbl_ptr<InfoContainer>),
            ret_handle,
        }};
    }

    impl_holder& operator=(impl_holder other) {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    Impl* operator->() const {
        return this->m_handle;
    }

    Impl& operator*() const {
        return *this->m_handle;
    }
};

template<typename Impl, typename... InfoContainers>
struct impl_shadow {
    using impl_type = Impl;
 
    data_block_impl<Impl>* m_handle;

    explicit impl_shadow(data_block_impl<Impl>* other_handle)
        : m_handle(other_handle) {}

    ~impl_shadow() {}

    impl_shadow(impl_holder<Impl, InfoContainers...> const& other)
        : m_handle(other.m_handle) {}

    impl_shadow(impl_shadow<Impl, InfoContainers...> const& other)
        : m_handle(other.m_handle) {}

    template<typename InterfaceHolder, std::enable_if_t<interface_holder_traits<InterfaceHolder>::value, int> = 0>
    operator InterfaceHolder() const& {
        using InfoContainer = typename interface_holder_traits<InterfaceHolder>::info_container;
        DataBlockHead* ret_handle = tobj_dup(this->m_handle);
        return InterfaceHolder{{
            static_cast<typename InfoContainer::vtable_t const*>(typeinfo_impl<Impl, InfoContainers...>::template vtbl_ptr<InfoContainer>),
            ret_handle,
        }};
    }

    template<typename InterfaceShadow, std::enable_if_t<interface_shadow_traits<InterfaceShadow>::value, int> = 0>
    operator InterfaceShadow() const& {
        using InfoContainer = typename interface_shadow_traits<InterfaceShadow>::info_container;
        DataBlockHead* ret_handle = this->m_handle;
        return InterfaceShadow{{
            static_cast<typename InfoContainer::vtable_t const*>(typeinfo_impl<Impl, InfoContainers...>::template vtbl_ptr<InfoContainer>),
            ret_handle,
        }};
    }

    impl_shadow& operator=(impl_shadow other) {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    Impl* operator->() const {
        return this->m_handle;
    }

    Impl& operator*() const {
        return *this->m_handle;
    }
};

template<typename Impl, typename... InterfaceHolders, typename... Args>
inline auto make_holder(Args&&... args) {
    data_block_impl<Impl>* handle = reinterpret_cast<data_block_impl<Impl>*>(malloc(sizeof(data_block_impl<Impl>)));
    tobj_init(
        handle,
        reinterpret_cast<TypeInfo const*>(
            &typeinfo_impl<Impl, typename interface_holder_traits<InterfaceHolders>::info_container...>::rtti
        )
    );
    new (static_cast<Impl*>(handle)) Impl(std::forward<Args>(args)...);
    return impl_holder<Impl, typename interface_holder_traits<InterfaceHolders>::info_container...>{handle};
}

template<typename... InterfaceHolders, typename Impl>
inline auto into_holder(Impl&& impl) {
    data_block_impl<Impl>* handle = reinterpret_cast<data_block_impl<Impl>*>(malloc(sizeof(data_block_impl<Impl>)));
    tobj_init(
        handle,
        reinterpret_cast<TypeInfo const*>(
            &typeinfo_impl<Impl, typename interface_holder_traits<InterfaceHolders>::info_container...>::rtti
        )
    );
    new (static_cast<Impl*>(handle)) Impl(std::forward<Impl>(impl));
    return impl_holder<Impl, typename interface_holder_traits<InterfaceHolders>::info_container...>{handle};
}
}
