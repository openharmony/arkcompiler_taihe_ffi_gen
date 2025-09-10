#include "shortcutInfo.impl.hpp"
#include "shortcutInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace shortcutInfo;

namespace {
// To be implemented.

class ShortcutInfoImpl {
public:
  int32_t shortcutInfoImpl = 4096;

  ShortcutInfoImpl() {}

  string GetId() {
    return "ShortcutInfo::GetId";
  }

  string GetBundleName() {
    return "ShortcutInfo::GetBundleName";
  }

  string GetHostAbility() {
    return "ShortcutInfo::GetHostAbility";
  }

  string GetIcon() {
    return "ShortcutInfo::GetIcon";
  }

  string GetLabel() {
    return "ShortcutInfo::GetLabel";
  }

  int32_t GetLabelId() {
    return shortcutInfoImpl;
  }

  int32_t GetIconId() {
    return shortcutInfoImpl;
  }

  string GetDisableMessage() {
    return "ShortcutInfo::GetDisableMessage";
  }

  optional<bool> GetIsStatic() {
    return optional<bool>::make(true);
  }

  optional<bool> GetIsHomeShortcut() {
    return optional<bool>::make(true);
  }

  optional<bool> GetIsEnabled() {
    return optional<bool>::make(true);
  }
};

ShortcutInfo GetShortcutInfo() {
  return make_holder<ShortcutInfoImpl, ShortcutInfo>();
}
}  // namespace

TH_EXPORT_CPP_API_GetShortcutInfo(GetShortcutInfo);
