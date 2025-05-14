#pragma once

#include <taihe/common.hpp>

#include <type_traits>

namespace taihe {
template<typename Signature>
struct callback_view;

template<typename Signature>
struct callback;

template<typename Return, typename... Params>
struct callback_view<Return(Params...)> {
  struct callback_data_head {
    struct rtti_type {
      void (*free)(struct callback_data_head *);
      as_abi_t<Return> (*func)(callback_data_head *data_ptr,
                               as_abi_t<Params>... params);
    } const *rtti_ptr;

    TRefCount m_count;
  };

  callback_data_head *data_ptr;

  explicit callback_view(callback_data_head *data_ptr) : data_ptr(data_ptr) {}

  Return operator()(Params... params) const {
    if constexpr (std::is_void_v<Return>) {
      return data_ptr->rtti_ptr->func(data_ptr, into_abi<Params>(params)...);
    } else {
      return from_abi<Return>(
          data_ptr->rtti_ptr->func(data_ptr, into_abi<Params>(params)...));
    }
  }
};

template<typename Return, typename... Params>
struct callback<Return(Params...)> : callback_view<Return(Params...)> {
  using typename callback_view<Return(Params...)>::callback_data_head;

  template<typename Impl>
  struct callback_head_full : callback_data_head {
    using typename callback_data_head::rtti_type;

    Impl impl;

    static as_abi_t<Return> c_call(callback_data_head *data_ptr,
                                   as_abi_t<Params>... params) {
      if constexpr (std::is_void_v<Return>) {
        return static_cast<callback_head_full<Impl> *>(data_ptr)->impl(
            from_abi<Params>(params)...);
      } else {
        return into_abi<Return>(
            static_cast<callback_head_full<Impl> *>(data_ptr)->impl(
                from_abi<Params>(params)...));
      }
    };

    static void c_free(callback_data_head *data_ptr) {
      delete static_cast<callback_head_full<Impl> *>(data_ptr);
    };

    static constexpr rtti_type rtti = {
        .free = &c_free,
        .func = &c_call,
    };

    template<typename... Args>
    callback_head_full(Args &&...args) : impl(std::forward<Args>(args)...) {
      this->rtti_ptr = &rtti;
      tref_set(&this->m_count, 1);
    }
  };

  template<typename Impl, typename... Args>
  static callback<Return(Params...)> from(Args &&...args) {
    return callback<Return(Params...)>{
        new callback_head_full<Impl>(std::forward<Args>(args)...),
    };
  }

  using callback_view<Return(Params...)>::data_ptr;

  explicit callback(callback_data_head *data_ptr)
      : callback_view<Return(Params...)>(data_ptr) {}

  callback(callback<Return(Params...)> &&other) : callback{other.data_ptr} {
    other.data_ptr = nullptr;
  }

  callback(callback<Return(Params...)> const &other)
      : callback{other.data_ptr} {
    if (data_ptr) {
      tref_inc(&data_ptr->m_count);
    }
  }

  callback(callback_view<Return(Params...)> const &other)
      : callback{other.data_ptr} {
    if (data_ptr) {
      tref_inc(&data_ptr->m_count);
    }
  }

  ~callback() {
    if (data_ptr && tref_dec(&data_ptr->m_count)) {
      data_ptr->rtti_ptr->free(data_ptr);
    }
  }

  callback &operator=(callback other) {
    std::swap(data_ptr, other.data_ptr);
    return *this;
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
  using type = void *;
};

template<typename Return, typename... Params>
struct as_abi<callback<Return(Params...)>> {
  using type = void *;
};

template<typename Return, typename... Params>
struct as_param<callback<Return(Params...)>> {
  using type = callback_view<Return(Params...)>;
};
}  // namespace taihe
