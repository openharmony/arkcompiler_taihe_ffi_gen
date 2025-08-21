#include "abilityInfo.ani.hpp"
#include "applicationInfo.ani.hpp"
#include "bundleInfo.ani.hpp"
#include "elementName.ani.hpp"
#include "extensionAbilityInfo.ani.hpp"
#include "hapModuleInfo.ani.hpp"
#include "metadata.ani.hpp"
#include "ohos.bundle.bundleManager.ani.hpp"
#include "overlayModuleInfo.ani.hpp"
#include "skill.ani.hpp"
#if __has_include(<ani.h>)
#include <ani.h>
#elif __has_include(<ani/ani.h>)
#include <ani/ani.h>
#else
#error "ani.h not found. Please ensure the Ani SDK is correctly installed."
#endif
ANI_EXPORT ani_status ANI_Constructor(ani_vm *vm, uint32_t *result) {
  ani_env *env;
  if (ANI_OK != vm->GetEnv(ANI_VERSION_1, &env)) {
    return ANI_ERROR;
  }
  if (ANI_OK != applicationInfo::ANIRegister(env)) {
    std::cerr << "Error from applicationInfo::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != hapModuleInfo::ANIRegister(env)) {
    std::cerr << "Error from hapModuleInfo::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != elementName::ANIRegister(env)) {
    std::cerr << "Error from elementName::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != abilityInfo::ANIRegister(env)) {
    std::cerr << "Error from abilityInfo::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != bundleInfo::ANIRegister(env)) {
    std::cerr << "Error from bundleInfo::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != metadata::ANIRegister(env)) {
    std::cerr << "Error from metadata::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != ohos::bundle::bundleManager::ANIRegister(env)) {
    std::cerr << "Error from ohos::bundle::bundleManager::ANIRegister"
              << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != extensionAbilityInfo::ANIRegister(env)) {
    std::cerr << "Error from extensionAbilityInfo::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != skill::ANIRegister(env)) {
    std::cerr << "Error from skill::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != overlayModuleInfo::ANIRegister(env)) {
    std::cerr << "Error from overlayModuleInfo::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  *result = ANI_VERSION_1;
  return ANI_OK;
}
