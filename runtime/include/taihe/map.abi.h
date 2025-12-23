#ifndef TAIHE_MAP_ABI_H
#define TAIHE_MAP_ABI_H

#include <taihe/common.h>

struct TMapNode {
  TMapNode *next;
  char data[];
};

struct TMapHandle {
  TRefCount count;
  size_t cap;
  TMapNode **bucket;
  size_t length;
};

struct TMap {
  TMapHandle *m_handle;
};

#endif  // TAIHE_MAP_ABI_H
