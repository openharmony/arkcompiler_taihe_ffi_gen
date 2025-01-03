#pragma once

#include <tuple>
#include <type_traits>
#include <utility>
#include <variant>

#include <taihe/common.h>

namespace taihe::core {
template<typename cpp_t, typename abi_t> abi_t into_abi(cpp_t val);
template<typename cpp_t, typename abi_t> cpp_t from_abi(abi_t val);

template<auto tag>
struct static_tag_t {};

template<auto tag>
constexpr static_tag_t<tag> static_tag_v = {};
}
