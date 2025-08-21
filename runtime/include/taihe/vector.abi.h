#pragma once

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
