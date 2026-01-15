/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// This file is a test file.
// NOLINTBEGIN

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Weverything"
#pragma clang diagnostic warning "-Wextra"
#pragma clang diagnostic warning "-Wall"

#include "elementName.napi.h"
#include "ohos.bundle.bundleManager.napi.h"
#include "abilityInfo.napi.h"
#include "extensionAbilityInfo.napi.h"
#include "overlayModuleInfo.napi.h"
#include "applicationInfo.napi.h"
#include "hapModuleInfo.napi.h"
#include "bundleInfo.napi.h"
#include "metadata.napi.h"
#include "skill.napi.h"

EXTERN_C_START
napi_value Init(napi_env env, napi_value exports)
{
    Init__elementName(env, exports);
    napi_value ns_bundle;
    napi_create_object(env, &ns_bundle);
    napi_value ns_bundle_bundleManager;
    napi_create_object(env, &ns_bundle_bundleManager);
    Init__ohos_bundle_bundleManager(env, ns_bundle_bundleManager);
    Init__ohos_bundle_bundleManager(env, exports);
    NAPI_CALL(env, napi_set_named_property(env, ns_bundle, "bundleManager", ns_bundle_bundleManager));
    NAPI_CALL(env, napi_set_named_property(env, exports, "bundle", ns_bundle));
    Init__abilityInfo(env, exports);
    Init__extensionAbilityInfo(env, exports);
    Init__overlayModuleInfo(env, exports);
    Init__applicationInfo(env, exports);
    Init__hapModuleInfo(env, exports);
    Init__bundleInfo(env, exports);
    Init__metadata(env, exports);
    Init__skill(env, exports);
    return exports;
}

EXTERN_C_END
static napi_module demoModule = {
    .nm_version = 1,
    .nm_flags = 0,
    .nm_filename = nullptr,
    .nm_register_func = Init,
    .nm_modname = "entry",
    .nm_priv = ((void *)0),
    .reserved = {0},
};

extern "C" __attribute__((constructor)) void RegisterEntryModule(void)
{
    napi_module_register(&demoModule);
}

#pragma clang diagnostic pop
// NOLINTEND
