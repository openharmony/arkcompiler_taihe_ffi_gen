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
  using func_type = as_abi_t<Return>(DataBlockHead *, as_abi_t<Params>...);

  DataBlockHead *data_ptr;
  func_type *func_ptr;

  explicit callback_view(DataBlockHead *data_ptr, func_type *func_ptr)
      : data_ptr(data_ptr), func_ptr(func_ptr) {}

  Return operator()(Params... params) const {
    if constexpr (std::is_void_v<Return>) {
      return func_ptr(data_ptr, into_abi<Params>(params)...);
    } else {
      return from_abi<Return>(func_ptr(data_ptr, into_abi<Params>(params)...));
    }
  }
};

template<typename Return, typename... Params>
struct callback<Return(Params...)> : callback_view<Return(Params...)> {
  using typename callback_view<Return(Params...)>::func_type;

  using callback_view<Return(Params...)>::data_ptr;
  using callback_view<Return(Params...)>::func_ptr;

  explicit callback(DataBlockHead *data_ptr, func_type *func_ptr)
      : callback_view<Return(Params...)>{data_ptr, func_ptr} {}

  ~callback() {
    if (data_ptr && tref_dec(&data_ptr->m_count)) {
      data_ptr->rtti_ptr->free(data_ptr);
    }
  }

  callback &operator=(callback other) {
    std::swap(data_ptr, other.data_ptr);
    std::swap(func_ptr, other.func_ptr);
    return *this;
  }

  callback(callback<Return(Params...)> &&other)
      : callback{other.data_ptr, other.func_ptr} {
    other.data_ptr = nullptr;
  }

  callback(callback<Return(Params...)> const &other)
      : callback{other.data_ptr, other.func_ptr} {
    if (data_ptr) {
      tref_inc(&data_ptr->m_count);
    }
  }

  callback(callback_view<Return(Params...)> const &other)
      : callback{other.data_ptr, other.func_ptr} {
    if (data_ptr) {
      tref_inc(&data_ptr->m_count);
    }
  }

  template<typename Impl>
  struct invoke_impl {
    static as_abi_t<Return> invoke(DataBlockHead *data_ptr,
                                   as_abi_t<Params>... params) {
      if constexpr (std::is_void_v<Return>) {
        return cast_data_ptr<Impl>(data_ptr)->operator()(
            from_abi<Params>(params)...);
      } else {
        return into_abi<Return>(cast_data_ptr<Impl>(data_ptr)->operator()(
            from_abi<Params>(params)...));
      }
    };
  };

  template<typename Impl>
  static constexpr TypeInfo rtti_impl = {
      .version = 0,
      .free = &::taihe::del_data_ptr<Impl>,
      .len = 0,
      .idmap = {},
  };

  template<typename Impl, typename... Args>
  static callback<Return(Params...)> from(Args &&...args) {
    return callback<Return(Params...)>(
        ::taihe::new_data_ptr<Impl>(
            reinterpret_cast<TypeInfo const *>(&rtti_impl<Impl>),
            std::forward<Args>(args)...),
        &invoke_impl<Impl>::invoke);
  }
};

template<typename Return, typename... Params>
inline bool same_impl(adl_helper_t, callback_view<Return(Params...)> lhs,
                      callback_view<Return(Params...)> rhs) {
  return lhs.data_ptr == lhs.data_ptr;
}

template<typename Return, typename... Params>
inline std::size_t hash_impl(adl_helper_t,
                             callback_view<Return(Params...)> val) {
  return reinterpret_cast<std::size_t>(val.data_ptr);
}

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
