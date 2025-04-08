#include "userSettings.proj.hpp"
#include "userSettings.impl.hpp"
#include "taihe/runtime.hpp"
#include "stdexcept"

using namespace taihe;

namespace {
optional<string> getUserSetting(map_view<string, string> settings, string_view key) {
    auto iter = settings.find(key);
    if (iter == nullptr) {
        return optional<string>(std::nullopt);
    }
    return optional<string>(std::in_place_t{}, *iter);
}
}  // namespace

TH_EXPORT_CPP_API_getUserSetting(getUserSetting);
