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
// This file is a test file.
// NOLINTBEGIN

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Weverything"
#pragma clang diagnostic warning "-Wextra"
#pragma clang diagnostic warning "-Wall"
#include "my_module_a.napi.h"
#include "my_module_a.ns1.napi.h"
#include "my_module_a.ns1.ns2.ns3.ns4.ns5.napi.h"
#include "my_module_b.functiontest.napi.h"

// implement the inject declare in .d.ts file
// implement for inject overload functions
#include "my_module_b_functiontest.hpp"
#include "taihe/runtime.hpp"

static napi_value my_module_a_concat(napi_env env, [[maybe_unused]] napi_callback_info info)
{
    size_t argc = 1;
    napi_value args[1] = {nullptr};
    napi_get_cb_info(env, info, &argc, args, nullptr, nullptr);
    napi_valuetype valueType;
    napi_typeof(env, args[0], &valueType);

    switch (valueType) {
        case napi_number: {
            int32_t value0_num;
            napi_get_value_int32(env, args[0], &value0_num);
            int32_t value_num = concat_i32(value0_num);
            napi_value result_num = nullptr;
            napi_create_int32(env, value_num, &result_num);
            return result_num;
        }
        case napi_string: {
            size_t value0_len = 0;
            napi_get_value_string_utf8(env, args[0], nullptr, 0, &value0_len);
            TString value0_abi;
            char *value0_buf = tstr_initialize(&value0_abi, value0_len + 1);
            napi_get_value_string_utf8(env, args[0], value0_buf, value0_len + 1, &value0_len);
            value0_buf[value0_len] = '\0';
            value0_abi.length = value0_len;
            taihe::string value0_str(value0_abi);
            ::taihe::string value_str = concat_str(value0_str);
            napi_value result_str = nullptr;
            napi_create_string_utf8(env, value_str.c_str(), value_str.size(), &result_str);
            return result_str;
        }
        default:
            napi_throw_error(env, nullptr, "param type is unknown");
            return nullptr;
    }
}

napi_value Init_my_module_b_concat(napi_env env, napi_value exports)
{
    if (::taihe::get_env() == nullptr) {
        ::taihe::set_env(env);
    }
    napi_property_descriptor desc[] = {
        {"concat", nullptr, my_module_a_concat, nullptr, nullptr, nullptr, napi_default, nullptr},
    };
    napi_define_properties(env, exports, sizeof(desc) / sizeof(desc[0]), desc);
    return exports;
}

EXTERN_C_START
napi_value Init(napi_env env, napi_value exports)
{
    napi_value ns_ns1;
    napi_create_object(env, &ns_ns1);
    Init__my_module_a_ns1(env, ns_ns1);
    napi_value ns_ns1_ns2;
    napi_create_object(env, &ns_ns1_ns2);
    napi_value ns_ns1_ns2_ns3;
    napi_create_object(env, &ns_ns1_ns2_ns3);
    napi_value ns_ns1_ns2_ns3_ns4;
    napi_create_object(env, &ns_ns1_ns2_ns3_ns4);
    napi_value ns_ns1_ns2_ns3_ns4_ns5;
    napi_create_object(env, &ns_ns1_ns2_ns3_ns4_ns5);
    Init__my_module_a_ns1_ns2_ns3_ns4_ns5(env, ns_ns1_ns2_ns3_ns4_ns5);
    Init__my_module_a_ns1_ns2_ns3_ns4_ns5(env, exports);
    NAPI_CALL(env, napi_set_named_property(env, ns_ns1_ns2_ns3_ns4, "ns5", ns_ns1_ns2_ns3_ns4_ns5));
    NAPI_CALL(env, napi_set_named_property(env, ns_ns1_ns2_ns3, "ns4", ns_ns1_ns2_ns3_ns4));
    NAPI_CALL(env, napi_set_named_property(env, ns_ns1_ns2, "ns3", ns_ns1_ns2_ns3));
    NAPI_CALL(env, napi_set_named_property(env, ns_ns1, "ns2", ns_ns1_ns2));
    Init__my_module_a_ns1(env, exports);
    NAPI_CALL(env, napi_set_named_property(env, exports, "ns1", ns_ns1));
    Init__my_module_a(env, exports);
    napi_value ns_functiontest;
    napi_create_object(env, &ns_functiontest);
    Init__my_module_b_functiontest(env, ns_functiontest);

    // Add register for concat function
    Init_my_module_b_concat(env, ns_functiontest);

    Init__my_module_b_functiontest(env, exports);
    NAPI_CALL(env, napi_set_named_property(env, exports, "functiontest", ns_functiontest));

    // implement the inject declare in .d.ts file
    // implement for inject module const variable
    napi_value value_rate = nullptr;
    napi_create_double(env, 0.618, &value_rate);
    napi_set_named_property(env, exports, "rate", value_rate);

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
