#pragma once
#include <stdint.h>

#define TH_NONNULL __attribute__((nonnull))
#define TH_EXPORT __attribute__((visibility("default")))

////////////////////////
// REFERENCE COUNTING //
////////////////////////

typedef uint32_t TRefCount;

// Increments the refcount and returns the *original* value before add.
static inline TRefCount tref_inc(TRefCount *c) {
  return __atomic_fetch_add(c, 1, __ATOMIC_SEQ_CST);
}

// Decrements the refcount and returns whether the memory should be freed.
static inline int tref_dec(TRefCount *c) {
  return __atomic_sub_fetch(c, 1, __ATOMIC_SEQ_CST) == 0;
}
