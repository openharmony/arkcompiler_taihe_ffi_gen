#pragma once
#include <stdint.h>
#include <assert.h>

#define TH_NONNULL __attribute__((nonnull))

#define TH_ASSERT(condition, message)                               \
    do {                                                            \
        if (!(condition)) {                                         \
            fprintf(stderr, "Assertion failed: (%s), function %s, " \
                            "file %s, line %d.\n"                   \
                            "Message: %s\n",                        \
                    #condition, __FUNCTION__, __FILE__, __LINE__,   \
                    message);                                       \
            abort();                                                \
        }                                                           \
    } while (0)

#ifdef __cplusplus
#define TH_EXPORT extern "C" __attribute__((visibility("default")))
#else
#define TH_EXPORT __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
#define TH_TYPEOF(value) decltype(value)
#else
#define TH_TYPEOF(value) typeof(value)
#endif

#ifdef __cplusplus
#define TH_STATIC_ASSERT(condition, message) static_assert(condition, message)
#else
#define TH_STATIC_ASSERT(condition, message) static_assert(condition, message)
#endif

#ifdef __cplusplus
#define TH_IS_SAME(u, v) std::is_same<u, v>::value
#else
#define TH_IS_SAME(u, v) __builtin_types_compatible_p(u, v)
#endif

////////////////////////
// REFERENCE COUNTING //
////////////////////////

typedef uint32_t TRefCount;

// Sets the counter to a fixed value.
static inline void tref_set(TRefCount *c, TRefCount i) {
  __atomic_store_n(c, i, __ATOMIC_SEQ_CST);
}

// Increments the refcount and returns the *original* value before add.
static inline TRefCount tref_inc(TRefCount *c) {
  return __atomic_fetch_add(c, 1, __ATOMIC_SEQ_CST);
}

// Decrements the refcount and returns whether the memory should be freed.
static inline int tref_dec(TRefCount *c) {
  return __atomic_sub_fetch(c, 1, __ATOMIC_SEQ_CST) == 0;
}
