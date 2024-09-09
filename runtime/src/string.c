#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <taihe/common.h>
#include <taihe/string.abi.h>

static inline struct TStringHeap* to_heap(struct TString* s) {
  if (s->flags & TSTRING_SHARED) return NULL;
  return (struct TStringHeap*)s;
}

void tstr_drop(struct TString* s) {
  struct TStringHeap* sh = to_heap(s);
  if (sh && tref_dec(&sh->count)) free(sh);
}

static struct TStringHeap* allocate_header(uint32_t length) {
  // The last member of `TStringHeap` already accounts for the '\0' terminator.
  size_t bytes_required = sizeof(struct TStringHeap) + sizeof(char) * length;
  struct TStringHeap* sh = malloc(bytes_required);
  if (!sh) return NULL;

  sh->header.flags = 0;
  sh->header.length = length;
  sh->header.ptr = sh->buffer;
  tref_init(&sh->count, 1);
  sh->buffer[length] = '\0';
  return sh;
}

const struct TString* tstr_new(const char* buf TH_NONNULL, size_t len) {
  if (len > UINT32_MAX) return NULL;
  if (buf[len] != '\0') return NULL;

  struct TStringHeap* sh = allocate_header(len);
  if (sh) memcpy(sh->buffer, buf, sizeof(char) * len);
  return (struct TString*)sh;
}

const struct TString* tstr_dup(struct TString* s) {
  if (!s) return NULL;

  struct TStringHeap* sh = to_heap(s);
  if (sh) {
    tref_inc(&sh->count);
    return s;
  }

  return tstr_new(s->ptr, s->length);
}
