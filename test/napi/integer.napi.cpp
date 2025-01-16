#include <iostream>

#include <node/node_api.h>

napi_value napi_ohos_int_sub(napi_env env, napi_callback_info info)
{
    size_t argc = 2;
    napi_value args[2] = {nullptr};

    napi_get_cb_info(env, info, &argc, args , nullptr, nullptr);

    int32_t value0;
    napi_get_value_int32(env, args[0], &value0);

    int32_t value1;
    napi_get_value_int32(env, args[1], &value1);

    int32_t value = value0 + value1;

    napi_value result;
    napi_create_int32(env, value, &result);
    return result;

}

napi_value module_init(napi_env env, napi_value exports) {
    napi_property_descriptor desc[] = {
        {"sub_i32", nullptr, napi_ohos_int_sub, nullptr, nullptr, nullptr, napi_default,
        nullptr},
    };

    napi_define_properties(env, exports, sizeof(desc) / sizeof(desc[0]), desc);
    return exports;
}

NAPI_MODULE(my_api, module_init);