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
struct ConstexprTagType {};

template<auto tag>
ConstexprTagType<tag> ConstexprTag = {};
}
