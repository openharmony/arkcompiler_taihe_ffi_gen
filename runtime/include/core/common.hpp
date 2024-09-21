// common.hpp
#pragma once
#include <tuple>
#include <type_traits> // TH_IS_SAME

extern "C" {
#include <taihe/common.h>
}

namespace taihe::core {
template<typename cpp_t, typename abi_t> abi_t into_abi(cpp_t val);
template<typename cpp_t, typename abi_t> cpp_t from_abi(abi_t val);

template<> inline int8_t   into_abi(int8_t   _val) { return _val; }
template<> inline int16_t  into_abi(int16_t  _val) { return _val; }
template<> inline int32_t  into_abi(int32_t  _val) { return _val; }
template<> inline int64_t  into_abi(int64_t  _val) { return _val; }
template<> inline uint8_t  into_abi(uint8_t  _val) { return _val; }
template<> inline uint16_t into_abi(uint16_t _val) { return _val; }
template<> inline uint32_t into_abi(uint32_t _val) { return _val; }
template<> inline uint64_t into_abi(uint64_t _val) { return _val; }
template<> inline bool     into_abi(bool     _val) { return _val; }
template<> inline float    into_abi(float    _val) { return _val; }
template<> inline double   into_abi(double   _val) { return _val; }
template<> inline int8_t   from_abi(int8_t   _val) { return _val; }
template<> inline int16_t  from_abi(int16_t  _val) { return _val; }
template<> inline int32_t  from_abi(int32_t  _val) { return _val; }
template<> inline int64_t  from_abi(int64_t  _val) { return _val; }
template<> inline uint8_t  from_abi(uint8_t  _val) { return _val; }
template<> inline uint16_t from_abi(uint16_t _val) { return _val; }
template<> inline uint32_t from_abi(uint32_t _val) { return _val; }
template<> inline uint64_t from_abi(uint64_t _val) { return _val; }
template<> inline bool     from_abi(bool     _val) { return _val; }
template<> inline float    from_abi(float    _val) { return _val; }
template<> inline double   from_abi(double   _val) { return _val; }

template<> inline int8_t   *into_abi(int8_t   &_val) { return &_val; }
template<> inline int16_t  *into_abi(int16_t  &_val) { return &_val; }
template<> inline int32_t  *into_abi(int32_t  &_val) { return &_val; }
template<> inline int64_t  *into_abi(int64_t  &_val) { return &_val; }
template<> inline uint8_t  *into_abi(uint8_t  &_val) { return &_val; }
template<> inline uint16_t *into_abi(uint16_t &_val) { return &_val; }
template<> inline uint32_t *into_abi(uint32_t &_val) { return &_val; }
template<> inline uint64_t *into_abi(uint64_t &_val) { return &_val; }
template<> inline bool     *into_abi(bool     &_val) { return &_val; }
template<> inline float    *into_abi(float    &_val) { return &_val; }
template<> inline double   *into_abi(double   &_val) { return &_val; }
template<> inline int8_t   &from_abi(int8_t   *_val) { return *_val; }
template<> inline int16_t  &from_abi(int16_t  *_val) { return *_val; }
template<> inline int32_t  &from_abi(int32_t  *_val) { return *_val; }
template<> inline int64_t  &from_abi(int64_t  *_val) { return *_val; }
template<> inline uint8_t  &from_abi(uint8_t  *_val) { return *_val; }
template<> inline uint16_t &from_abi(uint16_t *_val) { return *_val; }
template<> inline uint32_t &from_abi(uint32_t *_val) { return *_val; }
template<> inline uint64_t &from_abi(uint64_t *_val) { return *_val; }
template<> inline bool     &from_abi(bool     *_val) { return *_val; }
template<> inline float    &from_abi(float    *_val) { return *_val; }
template<> inline double   &from_abi(double   *_val) { return *_val; }

template<> inline int8_t   const *into_abi(int8_t   const &_val) { return &_val; }
template<> inline int16_t  const *into_abi(int16_t  const &_val) { return &_val; }
template<> inline int32_t  const *into_abi(int32_t  const &_val) { return &_val; }
template<> inline int64_t  const *into_abi(int64_t  const &_val) { return &_val; }
template<> inline uint8_t  const *into_abi(uint8_t  const &_val) { return &_val; }
template<> inline uint16_t const *into_abi(uint16_t const &_val) { return &_val; }
template<> inline uint32_t const *into_abi(uint32_t const &_val) { return &_val; }
template<> inline uint64_t const *into_abi(uint64_t const &_val) { return &_val; }
template<> inline bool     const *into_abi(bool     const &_val) { return &_val; }
template<> inline float    const *into_abi(float    const &_val) { return &_val; }
template<> inline double   const *into_abi(double   const &_val) { return &_val; }
template<> inline int8_t   const &from_abi(int8_t   const *_val) { return *_val; }
template<> inline int16_t  const &from_abi(int16_t  const *_val) { return *_val; }
template<> inline int32_t  const &from_abi(int32_t  const *_val) { return *_val; }
template<> inline int64_t  const &from_abi(int64_t  const *_val) { return *_val; }
template<> inline uint8_t  const &from_abi(uint8_t  const *_val) { return *_val; }
template<> inline uint16_t const &from_abi(uint16_t const *_val) { return *_val; }
template<> inline uint32_t const &from_abi(uint32_t const *_val) { return *_val; }
template<> inline uint64_t const &from_abi(uint64_t const *_val) { return *_val; }
template<> inline bool     const &from_abi(bool     const *_val) { return *_val; }
template<> inline float    const &from_abi(float    const *_val) { return *_val; }
template<> inline double   const &from_abi(double   const *_val) { return *_val; }
}
