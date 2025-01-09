#include <taihe/common.h>
#include <taihe/object.abi.h>

struct DataBlockHead* tobj_dup(struct DataBlockHead* data_ptr) {
  if (data_ptr && data_ptr->m_count != 0) {
    ++data_ptr->m_count;
  }
  return data_ptr;
}

void tobj_drop(struct DataBlockHead* data_ptr) {
  if (data_ptr && --(data_ptr->m_count) == 0) {
    data_ptr->rtti_ptr->free_ptr(data_ptr);
  }
}
