#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define TH_NONNULL __attribute__((nonnull))

#define TH_ASSERT(condition, message)                                    \
  do {                                                                   \
    if (!(condition)) {                                                  \
      fprintf(stderr,                                                    \
              "Assertion failed: (%s), function %s, file %s, line %d.\n" \
              "Message: %s\n",                                           \
              #condition, __FUNCTION__, __FILE__, __LINE__, message);    \
      abort();                                                           \
    }                                                                    \
  } while (0)

#ifdef __cplusplus
#define TH_EXPORT extern "C" __attribute__((visibility("default")))
#else
#define TH_EXPORT extern __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
#define TH_INLINE inline
#else
#define TH_INLINE static inline
#endif

////////////////////////
// REFERENCE COUNTING //
////////////////////////

typedef uint32_t TRefCount;

// Sets the counter to a fixed value.
TH_INLINE void tref_init(TRefCount *c, TRefCount i) {
  *c = i;
}

// Increments the refcount and returns the *original* value before add.
TH_INLINE void tref_inc(TRefCount *c) {
  __atomic_fetch_add(c, 1, __ATOMIC_RELAXED);
}

// Decrements the refcount and returns whether the memory should be freed.
TH_INLINE bool tref_dec(TRefCount *c) {
  return __atomic_sub_fetch(c, 1, __ATOMIC_ACQ_REL) == 0;
}
