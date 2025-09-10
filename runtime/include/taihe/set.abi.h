#pragma once

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
