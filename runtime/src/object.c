#include <taihe/common.h>
#include <taihe/object.abi.h>

// success: return ptr
// failed: return NULL
void* tobj_get_pvtbl(struct TypeInfo* rtti_ptr, const void* id) {
  size_t len = rtti_ptr->len;
  for (size_t i = 0; i < len; ++i) {
    if ((rtti_ptr->idmap[i].id) == id) {
      return rtti_ptr->idmap[i].vtbl_ptr;
    }
  }
  return NULL;
}

struct DataBlockHead* tobj_dup(struct DataBlockHead* data_ptr) {
  if (data_ptr && data_ptr->m_count != 0) {
    ++data_ptr->m_count;
  }
  return data_ptr;
}

void tobj_drop(struct DataBlockHead* data_ptr) {
  if (data_ptr && --(data_ptr->m_count) == 0) {
    data_ptr->rtti_ptr->free_data(data_ptr);
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
