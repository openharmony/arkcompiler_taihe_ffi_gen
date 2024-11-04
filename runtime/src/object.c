#include <taihe/common.h>
#include <taihe/object.abi.h>

// success: return ptr
// failed: return NULL
void* tobj_get_pvtbl(struct TypeInfo* rtti_ptr, const void* id) {
  size_t len = rtti_ptr->len;
  for (int i = 0; i < len; ++i) {
    if ((rtti_ptr->idmap[i].id) == id) {
      return rtti_ptr->idmap[i].vtbl_ptr;
    }
  }
  return NULL;
}

// dynamic_cast
int tobj_dynamic_cast(struct TObject src, struct TObject *dst, const void* id) {
  void* vtptr = tobj_get_pvtbl(src.data_ptr->rtti_ptr, id);
  if (vtptr) {
    dst->vtbl_ptr = vtptr;
    dst->data_ptr = src.data_ptr;
    return 1;
  }
  return 0;
}

void tobj_addref(struct TObject tobj) {
  if (tobj.data_ptr && tobj.data_ptr->m_count != 0) {
    ++tobj.data_ptr->m_count;
  }
}

void tobj_release(struct TObject tobj) {
  if (tobj.data_ptr && --(tobj.data_ptr->m_count) == 0) {
    free(tobj.data_ptr);
    tobj.data_ptr = NULL;
    tobj.vtbl_ptr = NULL;  
  }
}
