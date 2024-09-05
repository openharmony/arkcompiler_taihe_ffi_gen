#pragma once
#include <stdint.h>

////////////////////////
// REFERENCE COUNTING //
////////////////////////

typedef uint32_t TRefCount;

// Increments the refcount and returns the *original* value before add.
inline TRefCount tref_inc(TRefCount *c) {
  return __atomic_fetch_add(c, 1, __ATOMIC_SEQ_CST);
}

// Decrements the refcount and returns whether the memory should be freed.
inline int tref_dec(TRefCount *c) {
  return __atomic_sub_fetch(c, 1, __ATOMIC_SEQ_CST) == 0;
}
