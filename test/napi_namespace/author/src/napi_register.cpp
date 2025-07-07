#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Weverything"
#pragma clang diagnostic warning "-Wextra"
#pragma clang diagnostic warning "-Wall"
#include "ns_test_a.napi.h"
#include "ns_test_b.napi.h"
#include "ns_test_c.napi.h"

EXTERN_C_START
napi_value Init(napi_env env, napi_value exports) {
  napi_value ns_functiontest;
  napi_create_object(env, &ns_functiontest);
  Init__ns_test_c(env, ns_functiontest);
  napi_set_named_property(env, exports, "functiontest", ns_functiontest);
  napi_value ns_ns1;
  napi_create_object(env, &ns_ns1);
  Init__ns_test_a(env, ns_ns1);
  napi_value ns_ns1_ns2;
  napi_create_object(env, &ns_ns1_ns2);
  napi_value ns_ns1_ns2_ns3;
  napi_create_object(env, &ns_ns1_ns2_ns3);
  napi_value ns_ns1_ns2_ns3_ns4;
  napi_create_object(env, &ns_ns1_ns2_ns3_ns4);
  napi_value ns_ns1_ns2_ns3_ns4_ns5;
  napi_create_object(env, &ns_ns1_ns2_ns3_ns4_ns5);
  Init__ns_test_b(env, ns_ns1_ns2_ns3_ns4_ns5);
  napi_set_named_property(env, ns_ns1_ns2_ns3_ns4, "ns5",
                          ns_ns1_ns2_ns3_ns4_ns5);
  napi_set_named_property(env, ns_ns1_ns2_ns3, "ns4", ns_ns1_ns2_ns3_ns4);
  napi_set_named_property(env, ns_ns1_ns2, "ns3", ns_ns1_ns2_ns3);
  napi_set_named_property(env, ns_ns1, "ns2", ns_ns1_ns2);
  napi_set_named_property(env, exports, "ns1", ns_ns1);
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

extern "C" __attribute__((constructor)) void RegisterEntryModule(void) {
  napi_module_register(&demoModule);
}

#pragma clang diagnostic pop
