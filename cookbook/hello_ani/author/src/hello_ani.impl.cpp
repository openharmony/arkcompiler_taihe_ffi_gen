#include "hello_ani.impl.hpp"

#include <cstdint>

static int32_t impl_add(int32_t a, int32_t b) {
  return a + b;
}

// NOLINTBEGIN
TH_EXPORT_CPP_API_add(impl_add);
// NOLINTEND