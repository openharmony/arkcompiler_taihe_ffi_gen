#pragma once

#include <array>
#include <exception>

#include <taihe/common.hpp>
#include <taihe/object.abi.h>
#include <type_traits>

////////////
// traits //
////////////

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

template<typename InterfaceView>
struct interface_view_traits {
    static constexpr bool value = false;
};
}

//////////////////////
// Raw Data Handler //
//////////////////////

namespace taihe::core {
struct data_view;
struct data_holder;

struct data_view {
    DataBlockHead* m_handle;

    explicit data_view(DataBlockHead* other_handle) : m_handle(other_handle) {}

    data_view(data_view const& other)
        : data_view(other.m_handle) {}
};

struct data_holder : public data_view {
    explicit data_holder(DataBlockHead* other_handle) : data_view(other_handle) {}

    data_holder& operator=(data_holder other) {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    ~data_holder() {
        tobj_drop(this->m_handle);
    }

    data_holder(data_view const& other)
        : data_holder(tobj_dup(other.m_handle)) {}

    data_holder(data_holder const& other)
        : data_holder(tobj_dup(other.m_handle)) {}

    data_holder(data_holder&& other)
        : data_holder(other.m_handle) {
        other.m_handle = nullptr;
    }
};

inline bool same_impl(adl_helper_t, data_view lhs, data_view rhs) {
    return lhs.m_handle == rhs.m_handle;
}

inline std::size_t hash_impl(adl_helper_t, data_view val) {
    return (std::size_t)val.m_handle;
}
}

////////////////////////////////
// Data blocks and Type infos //
////////////////////////////////

namespace taihe::core {
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

template<typename... InfoContainers>
struct typeinfo_t {
    uint64_t version;
    void (*free_ptr)(struct DataBlockHead*);
    uint64_t len = (InfoContainers::dict_len + ... + 0);
    struct IdMapItem idmap[(InfoContainers::dict_len + ... + 1)] = {};
};
}

///////////////////////////////////////
// Specific Impl Type Object Handler //
///////////////////////////////////////

namespace taihe::core {
template<typename Impl, typename... InfoContainers>
struct impl_view;

template<typename Impl, typename... InfoContainers>
struct impl_holder;

template<typename Impl, typename... InfoContainers>
struct impl_view {
    using impl_type = Impl;

    data_block_impl<Impl>* m_handle;

    explicit impl_view(data_block_impl<Impl>* other_handle) : m_handle(other_handle) {}

    impl_view(impl_view<Impl, InfoContainers...> const& other)
        : impl_view(other.m_handle) {}

    template<typename InterfaceView, std::enable_if_t<interface_view_traits<InterfaceView>::value, int> = 0>
    operator InterfaceView() const& {
        using InfoContainer = typename interface_view_traits<InterfaceView>::info_container;
        DataBlockHead* ret_handle = this->m_handle;
        return InterfaceView{{
            static_cast<typename InfoContainer::vtable_t const*>(this->template vtbl_ptr<InfoContainer>),
            ret_handle,
        }};
    }

    template<typename InterfaceHolder, std::enable_if_t<interface_holder_traits<InterfaceHolder>::value, int> = 0>
    operator InterfaceHolder() const& {
        using InfoContainer = typename interface_holder_traits<InterfaceHolder>::info_container;
        DataBlockHead* ret_handle = tobj_dup(this->m_handle);
        return InterfaceHolder{{
            static_cast<typename InfoContainer::vtable_t const*>(this->template vtbl_ptr<InfoContainer>),
            ret_handle,
        }};
    }

    Impl* operator->() const {
        return this->m_handle;
    }

    Impl& operator*() const {
        return *this->m_handle;
    }

public:
    static constexpr typeinfo_t<InfoContainers...> rtti = [] {
        struct typeinfo_t<InfoContainers...> rtti = {0, &delete_impl<Impl>};
        static_concat(rtti.idmap, 0, InfoContainers::template typeinfo_space<Impl>::idmap...);
        return rtti;
    }();

    template<typename InfoContainer>
    static constexpr void const* vtbl_ptr = [] {
        for (uint64_t i = 0; i < rtti.len; i++) {
            if (InfoContainer::iid == rtti.idmap[i].id) {
                return rtti.idmap[i].vtbl_ptr;
            }
        }
        throw;
    }();
};

template<typename Impl, typename... InfoContainers>
struct impl_holder : public impl_view<Impl, InfoContainers...> {
    explicit impl_holder(data_block_impl<Impl>* other_handle) : impl_view<Impl, InfoContainers...>(other_handle) {}

    impl_holder& operator=(impl_holder other) {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    ~impl_holder() {
        tobj_drop(this->m_handle);
    }

    impl_holder(impl_view<Impl, InfoContainers...> const& other)
        : impl_holder(static_cast<data_block_impl<Impl>*>(tobj_dup(other.m_handle))) {}

    impl_holder(impl_holder<Impl, InfoContainers...> const& other)
        : impl_holder(static_cast<data_block_impl<Impl>*>(tobj_dup(other.m_handle))) {}

    impl_holder(impl_holder<Impl, InfoContainers...>&& other)
        : impl_holder(other.m_handle) {
        other.m_handle = nullptr;
    }

    template<typename InterfaceView, std::enable_if_t<interface_view_traits<InterfaceView>::value, int> = 0>
    operator InterfaceView() const& {
        using InfoContainer = typename interface_view_traits<InterfaceView>::info_container;
        DataBlockHead* ret_handle = this->m_handle;
        return InterfaceView{{
            static_cast<typename InfoContainer::vtable_t const*>(this->template vtbl_ptr<InfoContainer>),
            ret_handle,
        }};
    }

    template<typename InterfaceHolder, std::enable_if_t<interface_holder_traits<InterfaceHolder>::value, int> = 0>
    operator InterfaceHolder() const& {
        using InfoContainer = typename interface_holder_traits<InterfaceHolder>::info_container;
        DataBlockHead* ret_handle = tobj_dup(this->m_handle);
        return InterfaceHolder{{
            static_cast<typename InfoContainer::vtable_t const*>(this->template vtbl_ptr<InfoContainer>),
            ret_handle,
        }};
    }

    template<typename InterfaceHolder, std::enable_if_t<interface_holder_traits<InterfaceHolder>::value, int> = 0>
    operator InterfaceHolder() && {
        using InfoContainer = typename interface_holder_traits<InterfaceHolder>::info_container;
        DataBlockHead* ret_handle = this->m_handle;
        this->m_handle = nullptr;
        return InterfaceHolder{{
            static_cast<typename InfoContainer::vtable_t const*>(this->template vtbl_ptr<InfoContainer>),
            ret_handle,
        }};
    }
};

template<typename Impl, typename... InterfaceHolders, typename... Args>
inline auto make_holder(Args&&... args) {
    using ImplHolder = impl_holder<Impl, typename interface_holder_traits<InterfaceHolders>::info_container...>;
    data_block_impl<Impl>* handle = reinterpret_cast<data_block_impl<Impl>*>(malloc(sizeof(data_block_impl<Impl>)));
    tobj_init( handle, reinterpret_cast<TypeInfo const*>(&ImplHolder::rtti));
    new (static_cast<Impl*>(handle)) Impl(std::forward<Args>(args)...);
    return ImplHolder{handle};
}

template<typename... InterfaceHolders, typename Impl>
inline auto into_holder(Impl&& impl) {
    using ImplHolder = impl_holder<Impl, typename interface_holder_traits<InterfaceHolders>::info_container...>;
    data_block_impl<Impl>* handle = reinterpret_cast<data_block_impl<Impl>*>(malloc(sizeof(data_block_impl<Impl>)));
    tobj_init(handle, reinterpret_cast<TypeInfo const*>(&ImplHolder::rtti));
    new (static_cast<Impl*>(handle)) Impl(std::forward<Impl>(impl));
    return ImplHolder{handle};
}
}
