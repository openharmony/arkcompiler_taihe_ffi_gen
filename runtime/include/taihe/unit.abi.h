#ifndef TAIHE_UNIT_ABI_H
#define TAIHE_UNIT_ABI_H

#include <taihe/common.h>

struct TUnit {
  // Placeholder field: C structs cannot be empty, required to satisfy C
  // standard and for ABI layout compatibility
  char dummy;
};

#endif  // TAIHE_UNIT_ABI_H
