#include "sceneNodeParameters.impl.hpp"
#include "sceneNodeParameters.h"
#include "sceneNodeParameters.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

::sceneNodeParameters::SceneNodeParameters GetSceneNodeParameters() {
  return taihe::make_holder<SceneNodeParametersImpl,
                            ::sceneNodeParameters::SceneNodeParameters>();
}
}  // namespace

TH_EXPORT_CPP_API_GetSceneNodeParameters(GetSceneNodeParameters);