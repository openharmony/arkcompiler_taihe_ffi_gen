#pragma once

#include <taihe/common.h>

// TArray
// Represents a dynamic array structure containing the size and data pointer.
//
// # Members
// - `m_size`: The size of the array.
// - `m_data`: A pointer to the data in the array.
struct TArray {
  size_t m_size;
  void *m_data;
};
