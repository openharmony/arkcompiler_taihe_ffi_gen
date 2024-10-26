#include <taihe/common.h>
#include <taihe/object.abi.h>


// dynamic_cast
// yes! return ptr
// no! return NULL
inline void* GetVtptr(struct TypeInfo* typeInfo_ptr, const void* id) {
  size_t len = typeInfo_ptr->len;
  for (int i = 0; i < len; ++i) {
    if ((typeInfo_ptr->idmap[i].id) == id) {
      return typeInfo_ptr->idmap[i].vtableptr;
    }
  }
  return NULL;
}

int Convert(struct THObject src, struct THObject *dst, const void* id) {
  void* vtptr = GetVtptr(src.data_ptr->ti_ptr, id);
  if (vtptr) {
    dst->vtableptr = vtptr;
    dst->data_ptr = src.data_ptr;
    return 1;
  }
  return 0;
}