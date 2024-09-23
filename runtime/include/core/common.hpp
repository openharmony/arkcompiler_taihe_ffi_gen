// common.hpp
#pragma once
#include <tuple>
#include <type_traits>

#include <taihe/common.h>

namespace taihe::core {
template<typename cpp_t, typename abi_t> abi_t into_abi(cpp_t &&val);
template<typename cpp_t, typename abi_t> cpp_t from_abi(abi_t &&val);

template<> inline int8_t   into_abi(std::add_rvalue_reference_t<int8_t  > _val) { return _val; }
template<> inline int16_t  into_abi(std::add_rvalue_reference_t<int16_t > _val) { return _val; }
template<> inline int32_t  into_abi(std::add_rvalue_reference_t<int32_t > _val) { return _val; }
template<> inline int64_t  into_abi(std::add_rvalue_reference_t<int64_t > _val) { return _val; }
template<> inline uint8_t  into_abi(std::add_rvalue_reference_t<uint8_t > _val) { return _val; }
template<> inline uint16_t into_abi(std::add_rvalue_reference_t<uint16_t> _val) { return _val; }
template<> inline uint32_t into_abi(std::add_rvalue_reference_t<uint32_t> _val) { return _val; }
template<> inline uint64_t into_abi(std::add_rvalue_reference_t<uint64_t> _val) { return _val; }
template<> inline bool     into_abi(std::add_rvalue_reference_t<bool    > _val) { return _val; }
template<> inline float    into_abi(std::add_rvalue_reference_t<float   > _val) { return _val; }
template<> inline double   into_abi(std::add_rvalue_reference_t<double  > _val) { return _val; }
template<> inline int8_t   from_abi(std::add_rvalue_reference_t<int8_t  > _val) { return _val; }
template<> inline int16_t  from_abi(std::add_rvalue_reference_t<int16_t > _val) { return _val; }
template<> inline int32_t  from_abi(std::add_rvalue_reference_t<int32_t > _val) { return _val; }
template<> inline int64_t  from_abi(std::add_rvalue_reference_t<int64_t > _val) { return _val; }
template<> inline uint8_t  from_abi(std::add_rvalue_reference_t<uint8_t > _val) { return _val; }
template<> inline uint16_t from_abi(std::add_rvalue_reference_t<uint16_t> _val) { return _val; }
template<> inline uint32_t from_abi(std::add_rvalue_reference_t<uint32_t> _val) { return _val; }
template<> inline uint64_t from_abi(std::add_rvalue_reference_t<uint64_t> _val) { return _val; }
template<> inline bool     from_abi(std::add_rvalue_reference_t<bool    > _val) { return _val; }
template<> inline float    from_abi(std::add_rvalue_reference_t<float   > _val) { return _val; }
template<> inline double   from_abi(std::add_rvalue_reference_t<double  > _val) { return _val; }

template<> inline int8_t   *into_abi(std::add_rvalue_reference_t<int8_t   &> _val) { return &_val; }
template<> inline int16_t  *into_abi(std::add_rvalue_reference_t<int16_t  &> _val) { return &_val; }
template<> inline int32_t  *into_abi(std::add_rvalue_reference_t<int32_t  &> _val) { return &_val; }
template<> inline int64_t  *into_abi(std::add_rvalue_reference_t<int64_t  &> _val) { return &_val; }
template<> inline uint8_t  *into_abi(std::add_rvalue_reference_t<uint8_t  &> _val) { return &_val; }
template<> inline uint16_t *into_abi(std::add_rvalue_reference_t<uint16_t &> _val) { return &_val; }
template<> inline uint32_t *into_abi(std::add_rvalue_reference_t<uint32_t &> _val) { return &_val; }
template<> inline uint64_t *into_abi(std::add_rvalue_reference_t<uint64_t &> _val) { return &_val; }
template<> inline bool     *into_abi(std::add_rvalue_reference_t<bool     &> _val) { return &_val; }
template<> inline float    *into_abi(std::add_rvalue_reference_t<float    &> _val) { return &_val; }
template<> inline double   *into_abi(std::add_rvalue_reference_t<double   &> _val) { return &_val; }
template<> inline int8_t   &from_abi(std::add_rvalue_reference_t<int8_t   *> _val) { return *_val; }
template<> inline int16_t  &from_abi(std::add_rvalue_reference_t<int16_t  *> _val) { return *_val; }
template<> inline int32_t  &from_abi(std::add_rvalue_reference_t<int32_t  *> _val) { return *_val; }
template<> inline int64_t  &from_abi(std::add_rvalue_reference_t<int64_t  *> _val) { return *_val; }
template<> inline uint8_t  &from_abi(std::add_rvalue_reference_t<uint8_t  *> _val) { return *_val; }
template<> inline uint16_t &from_abi(std::add_rvalue_reference_t<uint16_t *> _val) { return *_val; }
template<> inline uint32_t &from_abi(std::add_rvalue_reference_t<uint32_t *> _val) { return *_val; }
template<> inline uint64_t &from_abi(std::add_rvalue_reference_t<uint64_t *> _val) { return *_val; }
template<> inline bool     &from_abi(std::add_rvalue_reference_t<bool     *> _val) { return *_val; }
template<> inline float    &from_abi(std::add_rvalue_reference_t<float    *> _val) { return *_val; }
template<> inline double   &from_abi(std::add_rvalue_reference_t<double   *> _val) { return *_val; }

template<> inline int8_t   const *into_abi(std::add_rvalue_reference_t<int8_t   const &> _val) { return &_val; }
template<> inline int16_t  const *into_abi(std::add_rvalue_reference_t<int16_t  const &> _val) { return &_val; }
template<> inline int32_t  const *into_abi(std::add_rvalue_reference_t<int32_t  const &> _val) { return &_val; }
template<> inline int64_t  const *into_abi(std::add_rvalue_reference_t<int64_t  const &> _val) { return &_val; }
template<> inline uint8_t  const *into_abi(std::add_rvalue_reference_t<uint8_t  const &> _val) { return &_val; }
template<> inline uint16_t const *into_abi(std::add_rvalue_reference_t<uint16_t const &> _val) { return &_val; }
template<> inline uint32_t const *into_abi(std::add_rvalue_reference_t<uint32_t const &> _val) { return &_val; }
template<> inline uint64_t const *into_abi(std::add_rvalue_reference_t<uint64_t const &> _val) { return &_val; }
template<> inline bool     const *into_abi(std::add_rvalue_reference_t<bool     const &> _val) { return &_val; }
template<> inline float    const *into_abi(std::add_rvalue_reference_t<float    const &> _val) { return &_val; }
template<> inline double   const *into_abi(std::add_rvalue_reference_t<double   const &> _val) { return &_val; }
template<> inline int8_t   const &from_abi(std::add_rvalue_reference_t<int8_t   const *> _val) { return *_val; }
template<> inline int16_t  const &from_abi(std::add_rvalue_reference_t<int16_t  const *> _val) { return *_val; }
template<> inline int32_t  const &from_abi(std::add_rvalue_reference_t<int32_t  const *> _val) { return *_val; }
template<> inline int64_t  const &from_abi(std::add_rvalue_reference_t<int64_t  const *> _val) { return *_val; }
template<> inline uint8_t  const &from_abi(std::add_rvalue_reference_t<uint8_t  const *> _val) { return *_val; }
template<> inline uint16_t const &from_abi(std::add_rvalue_reference_t<uint16_t const *> _val) { return *_val; }
template<> inline uint32_t const &from_abi(std::add_rvalue_reference_t<uint32_t const *> _val) { return *_val; }
template<> inline uint64_t const &from_abi(std::add_rvalue_reference_t<uint64_t const *> _val) { return *_val; }
template<> inline bool     const &from_abi(std::add_rvalue_reference_t<bool     const *> _val) { return *_val; }
template<> inline float    const &from_abi(std::add_rvalue_reference_t<float    const *> _val) { return *_val; }
template<> inline double   const &from_abi(std::add_rvalue_reference_t<double   const *> _val) { return *_val; }
}
