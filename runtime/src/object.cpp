#include <taihe/object.abi.h>

void tobj_init(struct DataBlockHead *data_ptr,
               struct TypeInfo const *rtti_ptr) {
  data_ptr->rtti_ptr = rtti_ptr;
  tref_set(&data_ptr->m_count, 1);
}

struct DataBlockHead *tobj_dup(struct DataBlockHead *data_ptr) {
  if (!data_ptr) {
    return nullptr;
  }
  tref_inc(&data_ptr->m_count);
  return data_ptr;
}

void tobj_drop(struct DataBlockHead *data_ptr) {
  if (!data_ptr) {
    return;
  }
  if (tref_dec(&data_ptr->m_count)) {
    data_ptr->rtti_ptr->free_fptr(data_ptr);
  }
}
