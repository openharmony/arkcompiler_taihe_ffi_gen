#pragma once

#include <taihe/unit.abi.h>
#include <taihe/common.hpp>

namespace taihe {
struct unit {
  unit() = default;
  unit(unit const &) = default;
  unit &operator=(unit const &) = default;
  unit(unit &&) = default;
  unit &operator=(unit &&) = default;
  ~unit() = default;

private:
  // This dummy field is required to ensure that the struct is not empty, which
  // is necessary for C compatibility and ABI layout.
  char dummy = 0;
};

inline bool operator==(unit, unit) {
  return true;
}

template<>
struct as_param<unit> {
  using type = unit;
};

template<>
struct as_abi<unit> {
  using type = TUnit;
};
}  // namespace taihe

template<>
struct std::hash<taihe::unit> {
  std::size_t operator()(taihe::unit) const noexcept {
    return 0;  // unit has no state, so we can return a constant hash value
  }
};
