#ifndef TAIHE_SET_ABI_H
#define TAIHE_SET_ABI_H

#include <taihe/common.h>

struct TSetNode {
  TSetNode *next;
  char data[];
};

struct TSetHandle {
  TRefCount count;
  size_t cap;
  TSetNode **bucket;
  size_t length;
};

struct TSet {
  TSetHandle *m_handle;
};

#endif  // TAIHE_SET_ABI_H
