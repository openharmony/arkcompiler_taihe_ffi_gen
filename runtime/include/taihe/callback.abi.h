#pragma once

#include <taihe/common.h>

struct TCallbackData {
    TRefCount m_count;
    void (*free)(struct TCallbackData*);
};

struct TCallback {
    struct TCallbackData* m_data;
    void* m_func;
};

TH_EXPORT void tcb_init(struct TCallbackData* data_ptr, void (*free)(struct TCallbackData*));

TH_EXPORT struct TCallbackData* tcb_dup(struct TCallbackData* data_ptr);

TH_EXPORT void tcb_drop(struct TCallbackData* data_ptr);
