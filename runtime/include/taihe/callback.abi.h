#pragma once

#include <taihe/object.abi.h>

// TCallback
// Represents a callback structure containing a pointer to the data block
// and a function pointer.
//
// # Members
// - `data_ptr`: A pointer to the data block.
// - `func_ptr`: A pointer to the function associated with the callback.
struct TCallback {
  void *func_ptr;
  struct DataBlockHead *data_ptr;
};
