#ifndef TAIHE_CALLBACK_ABI_H
#define TAIHE_CALLBACK_ABI_H

#include <taihe/object.abi.h>

// TCallback
// Represents a callback structure containing a pointer to the data block
// and a function pointer.
//
// # Members
// - `vtbl_ptr`: A pointer to the function associated with the callback.
// - `data_ptr`: A pointer to the data block.
struct TCallback {
  void *vtbl_ptr;
  struct DataBlockHead *data_ptr;
};

#endif  // TAIHE_CALLBACK_ABI_H
