#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <taihe/common.h>
#include <taihe/string.abi.h>

static inline struct TStringHeap* to_heap(struct TString tstr) {
  if (tstr.flags & TSTRING_REF) return NULL;
  return (struct TStringHeap*)((char*)tstr.ptr - offsetof(struct TStringHeap, buffer));
}

static inline struct TStringHeap* allocate_heap(struct TString *tstr_ptr, uint32_t length) {
  size_t bytes_required = sizeof(struct TStringHeap) + sizeof(char) * (length + 1);
  struct TStringHeap* sh = malloc(bytes_required);
  tref_set(&sh->count, 1);
  sh->buffer[length] = '\0';
  tstr_ptr->flags = 0;
  tstr_ptr->length = length;
  tstr_ptr->ptr = sh->buffer;
  return sh;
}

struct TString tstr_new(const char* buf TH_NONNULL, size_t len) {
  struct TString tstr;
  struct TStringHeap* sh = allocate_heap(&tstr, len);
  memcpy(sh->buffer, buf, sizeof(char) * len);
  return tstr;
}

struct TString tstr_dup(struct TString tstr) {
  if (tstr.ptr == NULL) {
    return tstr;
  }
  struct TStringHeap* sh = to_heap(tstr);
  if (sh) {
    tref_inc(&sh->count);
    return tstr;
  }
  return tstr_new(tstr.ptr, tstr.length);
}

void tstr_drop(struct TString tstr) {
  if (tstr.ptr == NULL) {
    return;
  }
  struct TStringHeap* sh = to_heap(tstr);
  if (sh && tref_dec(&sh->count)) {
    free(sh);
    return;
  }
  return;
}

struct TString tstr_concat(struct TString left, struct TString right) {
  size_t len = left.length + right.length;
  struct TString tstr;
  struct TStringHeap* sh = allocate_heap(&tstr, len);
  tref_set(&sh->count, 1);
  char* buf = sh->buffer;
  memcpy(buf, left.ptr, left.length);
  buf += sizeof(char) * left.length;
  memcpy(buf, right.ptr, right.length);
  buf += sizeof(char) * right.length;
  return tstr;
}

struct TString tstr_substr(struct TString tstr, size_t pos, size_t len) {
  if (pos > tstr.length) {
    len = 0;
  } else if (pos + len > tstr.length) {
    len = tstr.length - pos;
  }
  struct TString sstr;
  struct TStringHeap* sh = allocate_heap(&sstr, len);
  memcpy(sh->buffer, tstr.ptr + sizeof(char) * pos, sizeof(char) * len);
  return sstr;
}
