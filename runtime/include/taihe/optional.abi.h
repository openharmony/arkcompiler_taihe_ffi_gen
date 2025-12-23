#ifndef TAIHE_OPTIONAL_ABI_H
#define TAIHE_OPTIONAL_ABI_H

#include <taihe/common.h>

// TOptional
// Represents an optional value structure containing a pointer to the data.
//
// # Members
// - `m_data`: A pointer to the data in the optional value.
struct TOptional {
  void const *m_data;
};

#endif  // TAIHE_OPTIONAL_ABI_H
