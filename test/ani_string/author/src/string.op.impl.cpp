#include "core/string.hpp"

#include "stdexcept"
#include "string_op.StringPair.proj.1.hpp"
#include "string_op.impl.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
string concatString(string_view a, string_view b) { return concat(a, b); }
string makeString(string_view a, int32_t b) {
  string result = "";
  while (b-- > 0) {
    result = concat(result, a);
  }
  return result;
}
::string_op::StringPair split(string_view a, int32_t n) {
  int32_t l = a.size();
  if (n > l) {
    n = l;
  } else if (n + l < 0) {
    n = 0;
  } else if (n < 0) {
    n = n + l;
  }
  return {
      substr(a, 0, n),
      substr(a, n, l - n),
  };
}
int32_t to_i32(string_view a) { return std::atoi(a.c_str()); }
string from_i32(int32_t a) { return to_string(a); }
}  // namespace
TH_EXPORT_CPP_API_concatString(concatString);
TH_EXPORT_CPP_API_makeString(makeString);
TH_EXPORT_CPP_API_split(split);
TH_EXPORT_CPP_API_to_i32(to_i32);
TH_EXPORT_CPP_API_from_i32(from_i32);
