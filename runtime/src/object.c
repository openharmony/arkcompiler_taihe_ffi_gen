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

void* alloc_ftable(size_t func_len) {
    size_t bytes_required = sizeof(size_t) + sizeof(void*) * func_len;
    if (bytes_required > UINT32_MAX) return NULL;
    void* new_ftable_ptr = malloc(bytes_required);
    if (!new_ftable_ptr) return NULL;
    return new_ftable_ptr;
}

void* create_new_ftable(void* ftable_ptr, void* default_ftable_ptr) {
    size_t len = *(size_t*)default_ftable_ptr;

    void* dst = alloc_ftable(len);
    if (!dst) return NULL;

    void** ftable = (void**)((char*)dst + sizeof(size_t));

    *(size_t*)dst = len;

    for (size_t i = 0; i < len; ++i) {
        void* func_ptr = NULL;
        if (i < *(size_t*)ftable_ptr) {
            func_ptr = *(void**)((char*)ftable_ptr + sizeof(size_t) + i * sizeof(void*));
        }
        if (func_ptr == NULL && default_ftable_ptr != NULL) {
            if (i < *(size_t*)default_ftable_ptr) {
                func_ptr = *(void**)((char*)default_ftable_ptr + sizeof(size_t) + i * sizeof(void*));
            }
        }
        ftable[i] = func_ptr;
    }

    return dst;
}
