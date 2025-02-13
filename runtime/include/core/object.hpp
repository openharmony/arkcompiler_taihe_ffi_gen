#pragma once

#include <array>
#include <exception>

#include <taihe/common.hpp>
#include <taihe/object.abi.h>
#include <type_traits>

//////////////////////
// Raw Data Handler //
//////////////////////

namespace taihe::core {
struct data_view;
struct data_holder;

struct data_view {
    DataBlockHead* m_handle;

    explicit data_view(DataBlockHead* other_handle) : m_handle(other_handle) {}
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

namespace taihe::core {
}

///////////////////////////////////////
// Specific Impl Type Object Handler //
///////////////////////////////////////

namespace taihe::core {
template<typename T, uint64_t S>
constexpr void static_concat(T (&r)[S], uint64_t j) {}

template<typename T, uint64_t S, uint64_t N, uint64_t... Ns>
constexpr void static_concat(T (&r)[S], uint64_t j, T const (&a)[N], T const (&...as)[Ns]) {
    for (uint64_t i = 0; i < N; i++, j++) {
        r[j] = a[i];
    }
    static_concat(r, j, as...);
}

template<typename Impl>
struct data_block_impl : DataBlockHead, Impl {
    template<typename... Args>
    data_block_impl(TypeInfo const* rtti_ptr, Args&&... args)
        : Impl(std::forward<Args>(args)...) {
        tobj_init(this, rtti_ptr);
    }
};

template<typename Impl>
inline static void delete_impl(DataBlockHead *data_ptr) {
    delete static_cast<::taihe::core::data_block_impl<Impl>*>(data_ptr);
}

template<typename Impl, typename... InterfaceHolders>
struct impl_view;

template<typename Impl, typename... InterfaceHolders>
struct impl_holder;

template<typename Impl, typename... InterfaceHolders>
struct impl_view {
    using impl_type = Impl;

    data_block_impl<Impl>* m_handle;

    explicit impl_view(data_block_impl<Impl>* other_handle) : m_handle(other_handle) {}

    template<typename InterfaceView, std::enable_if_t<!InterfaceView::is_holder, int> = 0>
    operator InterfaceView() const& {
        DataBlockHead* ret_handle = this->m_handle;
        return InterfaceView{{
            static_cast<typename InterfaceView::vtable_t const*>(this->template vtbl_ptr<InterfaceView>),
            ret_handle,
        }};
    }

    template<typename InterfaceHolder, std::enable_if_t<InterfaceHolder::is_holder, int> = 0>
    operator InterfaceHolder() const& {
        DataBlockHead* ret_handle = tobj_dup(this->m_handle);
        return InterfaceHolder{{
            static_cast<typename InterfaceHolder::vtable_t const*>(this->template vtbl_ptr<InterfaceHolder>),
            ret_handle,
        }};
    }

    operator data_view() const& {
        DataBlockHead* ret_handle = this->m_handle;
        return data_view{ret_handle};
    }

    operator data_holder() const& {
        DataBlockHead* ret_handle = tobj_dup(this->m_handle);
        return data_holder{ret_handle};
    }

    Impl* operator->() const {
        return this->m_handle;
    }

    Impl& operator*() const {
        return *this->m_handle;
    }

public:
    static constexpr struct typeinfo_t {
        uint64_t version;
        void (*free_ptr)(struct DataBlockHead*);
        uint64_t len = ((sizeof(InterfaceHolders::template idmap_impl<Impl>) / sizeof(IdMapItem)) + ... + 0);
        struct IdMapItem idmap[((sizeof(InterfaceHolders::template idmap_impl<Impl>) / sizeof(IdMapItem)) + ... + 1)] = {};
    } rtti = [] {
        struct typeinfo_t rtti = {0, &delete_impl<Impl>};
        static_concat(rtti.idmap, 0, InterfaceHolders::template idmap_impl<Impl>...);
        return rtti;
    }();

    template<typename InterfaceHolder>
    static constexpr void const* vtbl_ptr = [] {
        for (uint64_t i = 0; i < rtti.len; i++) {
            if (InterfaceHolder::iid == rtti.idmap[i].id) {
                return rtti.idmap[i].vtbl_ptr;
            }
        }
        throw;
    }();
};

template<typename Impl, typename... InterfaceHolders>
struct impl_holder : public impl_view<Impl, InterfaceHolders...> {
    explicit impl_holder(data_block_impl<Impl>* other_handle) : impl_view<Impl, InterfaceHolders...>(other_handle) {}

    impl_holder& operator=(impl_holder other) {
        std::swap(this->m_handle, other.m_handle);
        return *this;
    }

    ~impl_holder() {
        tobj_drop(this->m_handle);
    }

    impl_holder(impl_view<Impl, InterfaceHolders...> const& other)
        : impl_holder(static_cast<data_block_impl<Impl>*>(tobj_dup(other.m_handle))) {}

    impl_holder(impl_holder<Impl, InterfaceHolders...> const& other)
        : impl_holder(static_cast<data_block_impl<Impl>*>(tobj_dup(other.m_handle))) {}

    impl_holder(impl_holder<Impl, InterfaceHolders...>&& other)
        : impl_holder(other.m_handle) {
        other.m_handle = nullptr;
    }

    template<typename InterfaceView, std::enable_if_t<!InterfaceView::is_holder, int> = 0>
    operator InterfaceView() const& {
        DataBlockHead* ret_handle = this->m_handle;
        return InterfaceView{{
            static_cast<typename InterfaceView::vtable_t const*>(this->template vtbl_ptr<InterfaceView>),
            ret_handle,
        }};
    }

    template<typename InterfaceHolder, std::enable_if_t<InterfaceHolder::is_holder, int> = 0>
    operator InterfaceHolder() const& {
        DataBlockHead* ret_handle = tobj_dup(this->m_handle);
        return InterfaceHolder{{
            static_cast<typename InterfaceHolder::vtable_t const*>(this->template vtbl_ptr<InterfaceHolder>),
            ret_handle,
        }};
    }

    template<typename InterfaceHolder, std::enable_if_t<InterfaceHolder::is_holder, int> = 0>
    operator InterfaceHolder() && {
        DataBlockHead* ret_handle = this->m_handle;
        this->m_handle = nullptr;
        return InterfaceHolder{{
            static_cast<typename InterfaceHolder::vtable_t const*>(this->template vtbl_ptr<InterfaceHolder>),
            ret_handle,
        }};
    }

    operator data_view() const& {
        DataBlockHead* ret_handle = this->m_handle;
        return data_view{ret_handle};
    }

    operator data_holder() const& {
        DataBlockHead* ret_handle = tobj_dup(this->m_handle);
        return data_holder{ret_handle};
    }

    operator data_holder() && {
        DataBlockHead* ret_handle = this->m_handle;
        this->m_handle = nullptr;
        return data_holder{ret_handle};
    }
};

template<typename Impl, typename... InterfaceHolders, typename... Args>
inline auto make_holder(Args&&... args) {
    using ImplHolder = impl_holder<Impl, InterfaceHolders...>;
    return ImplHolder{
        new data_block_impl<Impl>(reinterpret_cast<TypeInfo const*>(&ImplHolder::rtti), std::forward<Args>(args)...),
    };
}

template<typename... InterfaceHolders, typename Impl>
inline auto into_holder(Impl&& impl) {
    using ImplHolder = impl_holder<Impl, InterfaceHolders...>;
    return ImplHolder{
        new data_block_impl<Impl>(reinterpret_cast<TypeInfo const*>(&ImplHolder::rtti), std::forward<Impl>(impl)),
    };
}
}
