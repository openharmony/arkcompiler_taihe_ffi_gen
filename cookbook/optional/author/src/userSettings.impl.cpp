#include "userSettings.impl.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"
#include "userSettings.proj.hpp"

using namespace taihe;

namespace {
optional<string> getUserSetting(map_view<string, string> settings,
                                string_view key) {
  auto iter = settings.find_item(key);
  if (iter == nullptr) {
    return optional<string>(std::nullopt);
  }
  return optional<string>(std::in_place, iter->second);
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_getUserSetting(getUserSetting);
// NOLINTEND
