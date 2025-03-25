#include <cstdint>
#include "hello_ani.impl.hpp"

static int32_t impl_add(int32_t a, int32_t b) {
    return a + b;
  }

TH_EXPORT_CPP_API_add(impl_add);