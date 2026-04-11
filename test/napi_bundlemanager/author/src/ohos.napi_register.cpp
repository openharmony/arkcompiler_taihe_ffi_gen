#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Weverything"

#include "ohos.bundle.bundleManager.napi.h"

napi_value Init(napi_env env, napi_value exports)
{
    napi_value exports_bundle;
    napi_create_object(env, &exports_bundle);
    napi_value exports_bundle_bundleManager;
    napi_create_object(env, &exports_bundle_bundleManager);
    ohos::bundle::bundleManager::NapiInit(env, exports_bundle_bundleManager);
    NAPI_CALL(env, napi_set_named_property(env, exports_bundle, "bundleManager", exports_bundle_bundleManager));
    NAPI_CALL(env, napi_set_named_property(env, exports, "bundle", exports_bundle));
    return exports;
}

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
