#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <taihe/common.h>
#include <taihe/string.abi.h>

static inline struct TStringHeap *to_heap(struct TString tstr) {
  if (tstr.flags & TSTRING_REF) return NULL;
  return (struct TStringHeap *)((char *)tstr.ptr - offsetof(struct TStringHeap, buffer));
}

char *tstr_initialize(struct TString *tstr_ptr, uint32_t capacity) {
  size_t bytes_required = sizeof(struct TStringHeap) + sizeof(char) * capacity;
  struct TStringHeap *sh = malloc(bytes_required);
  tref_set(&sh->count, 1);
  tstr_ptr->flags = 0;
  tstr_ptr->ptr = sh->buffer;
  return sh->buffer;
}

struct TString tstr_new(const char *value TH_NONNULL, size_t len) {
  struct TString tstr;
  char *buf = tstr_initialize(&tstr, len + 1);
  memcpy(buf, value, sizeof(char) * len);
  buf[len] = '\0';
  tstr.length = len;
  return tstr;
}

struct TString tstr_dup(struct TString tstr) {
  struct TStringHeap *sh = to_heap(tstr);
  if (sh) {
    tref_inc(&sh->count);
    return tstr;
  }
  return tstr_new(tstr.ptr, tstr.length);
}

void tstr_drop(struct TString tstr) {
  struct TStringHeap *sh = to_heap(tstr);
  if (sh && tref_dec(&sh->count)) {
    free(sh);
    return;
  }
  return;
}

struct TString tstr_concat(struct TString left, struct TString right) {
  size_t len = left.length + right.length;
  struct TString tstr;
  char *buf = tstr_initialize(&tstr, len + 1);
  memcpy(buf, left.ptr, sizeof(char) * left.length);
  buf += left.length;
  memcpy(buf, right.ptr, sizeof(char) * right.length);
  buf += right.length;
  *buf = '\0';
  tstr.length = len;
  return tstr;
}

struct TString tstr_substr(struct TString tstr, size_t pos, size_t len) {
  if (pos > tstr.length) {
    len = 0;
  } else if (pos + len > tstr.length) {
    len = tstr.length - pos;
  }
  struct TString sstr;
  char *buf = tstr_initialize(&sstr, len + 1);
  memcpy(buf, tstr.ptr + pos, sizeof(char) * len);
  buf += len;
  *buf = '\0';
  tstr.length = len;
  return sstr;
}
