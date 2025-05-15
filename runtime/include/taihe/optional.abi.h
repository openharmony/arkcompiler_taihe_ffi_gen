#pragma once

#include <taihe/common.h>

// TOptional
// Represents an optional value structure containing a pointer to the data.
//
// # Members
// - `m_data`: A pointer to the data in the optional value.
struct TOptional {
  void const *m_data;
};
