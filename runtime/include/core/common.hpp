#pragma once

#include <concepts>
#include <type_traits>

extern "C" {
#include <taihe/common.h>
}

namespace taihe::core {
template<typename cpp_t> struct as_abi {};

template<typename cpp_t>
using as_abi_t = typename as_abi<cpp_t>::type;

template<typename cpp_t> as_abi_t<cpp_t> into_abi(cpp_t val);
template<typename cpp_t> cpp_t from_abi(as_abi_t<cpp_t> val);

template<> struct as_abi<int8_t  > { using type = int8_t  ; };
template<> struct as_abi<int16_t > { using type = int16_t ; };
template<> struct as_abi<int32_t > { using type = int32_t ; };
template<> struct as_abi<int64_t > { using type = int64_t ; };
template<> struct as_abi<uint8_t > { using type = uint8_t ; };
template<> struct as_abi<uint16_t> { using type = uint16_t; };
template<> struct as_abi<uint32_t> { using type = uint32_t; };
template<> struct as_abi<uint64_t> { using type = uint64_t; };
template<> struct as_abi<bool    > { using type = bool    ; };
template<> struct as_abi<float   > { using type = float   ; };
template<> struct as_abi<double  > { using type = double  ; };
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

template<> struct as_abi<int8_t   &> { using type = int8_t   *; };
template<> struct as_abi<int16_t  &> { using type = int16_t  *; };
template<> struct as_abi<int32_t  &> { using type = int32_t  *; };
template<> struct as_abi<int64_t  &> { using type = int64_t  *; };
template<> struct as_abi<uint8_t  &> { using type = uint8_t  *; };
template<> struct as_abi<uint16_t &> { using type = uint16_t *; };
template<> struct as_abi<uint32_t &> { using type = uint32_t *; };
template<> struct as_abi<uint64_t &> { using type = uint64_t *; };
template<> struct as_abi<bool     &> { using type = bool     *; };
template<> struct as_abi<float    &> { using type = float    *; };
template<> struct as_abi<double   &> { using type = double   *; };
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

template<> struct as_abi<int8_t   const &> { using type = int8_t   const *; };
template<> struct as_abi<int16_t  const &> { using type = int16_t  const *; };
template<> struct as_abi<int32_t  const &> { using type = int32_t  const *; };
template<> struct as_abi<int64_t  const &> { using type = int64_t  const *; };
template<> struct as_abi<uint8_t  const &> { using type = uint8_t  const *; };
template<> struct as_abi<uint16_t const &> { using type = uint16_t const *; };
template<> struct as_abi<uint32_t const &> { using type = uint32_t const *; };
template<> struct as_abi<uint64_t const &> { using type = uint64_t const *; };
template<> struct as_abi<bool     const &> { using type = bool     const *; };
template<> struct as_abi<float    const &> { using type = float    const *; };
template<> struct as_abi<double   const &> { using type = double   const *; };
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
