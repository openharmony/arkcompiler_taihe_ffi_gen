#ifndef TAIHE_VECTOR_ABI_H
#define TAIHE_VECTOR_ABI_H

#include <taihe/common.h>

struct TVectorHandle {
  TRefCount count;
  size_t cap;
  void *bucket;
  size_t length;
};

struct TVector {
  TVectorHandle *m_handle;
};

#endif  // TAIHE_VECTOR_ABI_H
