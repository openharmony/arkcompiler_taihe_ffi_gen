#pragma once

#include <tuple>
#include <type_traits>
#include <utility>
#include <variant>

#include <taihe/common.h>

namespace taihe::core {
template<typename cpp_t, typename abi_t>
inline abi_t move_into_abi(cpp_t &&cpp_val) {
    abi_t abi_val;
    new (&abi_val) cpp_t(std::move(cpp_val));
    return abi_val;
}

template<typename cpp_t, typename abi_t>
inline abi_t copy_into_abi(cpp_t const &cpp_val) {
    abi_t abi_val;
    new (&abi_val) cpp_t(cpp_val);
    return abi_val;
}

template<typename cpp_t, typename abi_t>
inline abi_t cast_into_abi(cpp_t const &cpp_val) {
    return reinterpret_cast<abi_t const &>(cpp_val);
}

template<typename cpp_t, typename abi_t>
inline cpp_t cast_from_abi(abi_t const &abi_val) {
    union temp {
        abi_t abi_val;
        cpp_t cpp_val;
        temp() {}
        ~temp() {}
    } res;
    res.abi_val = abi_val;
    return res.cpp_val;
}

template<typename cpp_t, typename abi_t>
inline abi_t cast_ref_into_abi(cpp_t cpp_val) {
    return reinterpret_cast<abi_t>(&cpp_val);
}

template<typename cpp_t, typename abi_t>
inline cpp_t cast_ref_from_abi(abi_t abi_val) {
    return reinterpret_cast<cpp_t>(*abi_val);
}

///////////////
// enum tags //
///////////////

template<auto tag>
struct static_tag_t {};

template<auto tag>
constexpr static_tag_t<tag> static_tag = {};

/////////////////////////
// hash and comparison //
/////////////////////////

struct adl_helper_t {};

template<typename T>
inline std::size_t hash(T&& val) {
    adl_helper_t adl_helper;
    return hash_impl(adl_helper, std::forward<T>(val));
}

template<typename L, typename R>
inline bool same(L&& lhs, R&& rhs) {
    adl_helper_t adl_helper;
    return same_impl(adl_helper, std::forward<L>(lhs), std::forward<R>(rhs));
}

template<typename T, typename std::enable_if_t<std::is_arithmetic_v<T>, int> = 0>
inline std::size_t hash_impl(adl_helper_t, T val) {
    return std::hash<T>{}(val);
}

template<typename T, typename std::enable_if_t<std::is_arithmetic_v<T>, int> = 0>
inline bool same_impl(adl_helper_t, T lhs, T rhs) {
    return lhs == rhs;
}
}
