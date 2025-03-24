#pragma once

#include <taihe/common.h>

struct TCallbackData {
  TRefCount m_count;
  void (*m_free)(struct TCallbackData*);
  void* m_func;
};

struct TCallback {
  struct TCallbackData* data_ptr;
};

TH_EXPORT void tcallback_init(struct TCallbackData* data_ptr, void* func,
                              void (*free)(struct TCallbackData*));

TH_EXPORT struct TCallbackData* tcallback_dup(struct TCallbackData* data_ptr);

TH_EXPORT void tcallback_drop(struct TCallbackData* data_ptr);
