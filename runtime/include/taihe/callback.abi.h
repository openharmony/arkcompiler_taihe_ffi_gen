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
  struct DataBlockHead *data_ptr;
  void *func_ptr;
};
