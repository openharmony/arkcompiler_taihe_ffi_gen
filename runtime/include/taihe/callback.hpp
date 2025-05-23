#pragma once

#include <taihe/callback.abi.h>
#include <taihe/common.hpp>
#include <taihe/object.hpp>

#include <type_traits>

namespace taihe {
template<typename Signature>
struct callback_view;

template<typename Signature>
struct callback;

template<typename Return, typename... Params>
struct callback_view<Return(Params...)> {
  static constexpr bool is_holder = false;

  using vtable_type = as_abi_t<Return>(DataBlockHead *, as_abi_t<Params>...);
  using view_type = callback_view<Return(Params...)>;
  using holder_type = callback<Return(Params...)>;

  struct abi_type {
    vtable_type *vtbl_ptr;
    DataBlockHead *data_ptr;
  } m_handle;

  explicit callback_view(abi_type handle) : m_handle(handle) {}

  operator data_view() const & {
    DataBlockHead *ret_data_ptr = m_handle.data_ptr;
    return data_view(ret_data_ptr);
  }

  operator data_holder() const & {
    DataBlockHead *ret_data_ptr = tobj_dup(m_handle.data_ptr);
    return data_holder(ret_data_ptr);
  }

public:
  operator bool() const & {
    return m_handle.vtbl_ptr;
  }

  Return operator()(Params... params) const & {
    if constexpr (std::is_void_v<Return>) {
      return m_handle.vtbl_ptr(m_handle.data_ptr, into_abi<Params>(params)...);
    } else {
      return from_abi<Return>(
          m_handle.vtbl_ptr(m_handle.data_ptr, into_abi<Params>(params)...));
    }
  }

public:
  template<typename Impl>
  static as_abi_t<Return> vtbl_impl(DataBlockHead *data_ptr,
                                    as_abi_t<Params>... params) {
    if constexpr (std::is_void_v<Return>) {
      return cast_data_ptr<Impl>(data_ptr)->operator()(
          from_abi<Params>(params)...);
    } else {
      return into_abi<Return>(cast_data_ptr<Impl>(data_ptr)->operator()(
          from_abi<Params>(params)...));
    }
  };

  template<typename Impl>
  static constexpr struct IdMapItem idmap_impl[0] = {};
};

template<typename Return, typename... Params>
struct callback<Return(Params...)> : callback_view<Return(Params...)> {
  static constexpr bool is_holder = true;

  using typename callback_view<Return(Params...)>::abi_type;

  using callback_view<Return(Params...)>::m_handle;

  explicit callback(abi_type handle)
      : callback_view<Return(Params...)>(handle) {}

  ~callback() {
    if (m_handle.data_ptr && tref_dec(&m_handle.data_ptr->m_count)) {
      m_handle.data_ptr->rtti_ptr->free(m_handle.data_ptr);
    }
  }

  callback &operator=(callback other) {
    std::swap(m_handle, other.m_handle);
    return *this;
  }

  callback(callback<Return(Params...)> &&other) : callback{other.m_handle} {
    other.m_handle.data_ptr = nullptr;
  }

  callback(callback<Return(Params...)> const &other)
      : callback{other.m_handle} {
    if (m_handle.data_ptr) {
      tref_inc(&m_handle.data_ptr->m_count);
    }
  }

  callback(callback_view<Return(Params...)> const &other)
      : callback{other.m_handle} {
    if (m_handle.data_ptr) {
      tref_inc(&m_handle.data_ptr->m_count);
    }
  }

  operator data_view() const & {
    DataBlockHead *ret_data_ptr = m_handle.data_ptr;
    return data_view(ret_data_ptr);
  }

  operator data_holder() const & {
    DataBlockHead *ret_data_ptr = tobj_dup(m_handle.data_ptr);
    return data_holder(ret_data_ptr);
  }

  operator data_holder() && {
    DataBlockHead *ret_data_ptr = m_handle.data_ptr;
    m_handle.data_ptr = nullptr;
    return data_holder(ret_data_ptr);
  }
};

template<typename Return, typename... Params>
struct as_abi<callback_view<Return(Params...)>> {
  using type = TCallback;
};

template<typename Return, typename... Params>
struct as_abi<callback<Return(Params...)>> {
  using type = TCallback;
};

template<typename Return, typename... Params>
struct as_param<callback<Return(Params...)>> {
  using type = callback_view<Return(Params...)>;
};
}  // namespace taihe
