/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
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

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Weverything"

#include "my_module_a.ns1.ns2.ns3.ns4.ns5.napi.h"
#include "my_module_a.ns1.napi.h"
#include "my_module_a.napi.h"

EXTERN_C_START
napi_value Init(napi_env env, napi_value exports)
{
    napi_value exports_ns1;
    napi_create_object(env, &exports_ns1);
    napi_value exports_ns1_ns2;
    napi_create_object(env, &exports_ns1_ns2);
    napi_value exports_ns1_ns2_ns3;
    napi_create_object(env, &exports_ns1_ns2_ns3);
    napi_value exports_ns1_ns2_ns3_ns4;
    napi_create_object(env, &exports_ns1_ns2_ns3_ns4);
    napi_value exports_ns1_ns2_ns3_ns4_ns5;
    napi_create_object(env, &exports_ns1_ns2_ns3_ns4_ns5);
    my_module_a::ns1::ns2::ns3::ns4::ns5::NapiInit(env, exports_ns1_ns2_ns3_ns4_ns5);
    NAPI_CALL(env, napi_set_named_property(env, exports_ns1_ns2_ns3_ns4, "ns5", exports_ns1_ns2_ns3_ns4_ns5));
    NAPI_CALL(env, napi_set_named_property(env, exports_ns1_ns2_ns3, "ns4", exports_ns1_ns2_ns3_ns4));
    NAPI_CALL(env, napi_set_named_property(env, exports_ns1_ns2, "ns3", exports_ns1_ns2_ns3));
    NAPI_CALL(env, napi_set_named_property(env, exports_ns1, "ns2", exports_ns1_ns2));
    my_module_a::ns1::NapiInit(env, exports_ns1);
    NAPI_CALL(env, napi_set_named_property(env, exports, "ns1", exports_ns1));
    my_module_a::NapiInit(env, exports);
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
