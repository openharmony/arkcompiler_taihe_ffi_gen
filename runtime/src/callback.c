#include <taihe/common.h>
#include <taihe/callback.abi.h>

void tcb_init(struct TCallbackData* data_ptr, void (*free)(struct TCallbackData*)) {
  data_ptr->free = free;
  tref_set(&data_ptr->m_count, 1);
}

struct TCallbackData* tcb_dup(struct TCallbackData* data_ptr) {
  if (!data_ptr) {
    return NULL;
  }
  tref_inc(&data_ptr->m_count);
  return data_ptr;
}

void tcb_drop(struct TCallbackData* data_ptr) {
  if (!data_ptr) {
    return;
  }
  if (tref_dec(&data_ptr->m_count)) {
    data_ptr->free(data_ptr);
  }
}
