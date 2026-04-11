#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Weverything"

#include "overlayModuleInfo.napi.h"

napi_value Init(napi_env env, napi_value exports)
{
    overlayModuleInfo::NapiInit(env, exports);
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
