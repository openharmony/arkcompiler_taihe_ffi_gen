#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Weverything"
#pragma clang diagnostic warning "-Wextra"
#pragma clang diagnostic warning "-Wall"
#include "my_module_a.napi.h"
#include "my_module_a.ns1.napi.h"
#include "my_module_a.ns1.ns2.ns3.ns4.ns5.napi.h"
#include "my_module_b.functiontest.napi.h"

EXTERN_C_START
napi_value Init(napi_env env, napi_value exports) {
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
  NAPI_CALL(env, napi_set_named_property(env, ns_ns1_ns2_ns3_ns4, "ns5",
                                         ns_ns1_ns2_ns3_ns4_ns5));
  NAPI_CALL(env, napi_set_named_property(env, ns_ns1_ns2_ns3, "ns4",
                                         ns_ns1_ns2_ns3_ns4));
  NAPI_CALL(env,
            napi_set_named_property(env, ns_ns1_ns2, "ns3", ns_ns1_ns2_ns3));
  NAPI_CALL(env, napi_set_named_property(env, ns_ns1, "ns2", ns_ns1_ns2));
  Init__my_module_a_ns1(env, exports);
  NAPI_CALL(env, napi_set_named_property(env, exports, "ns1", ns_ns1));
  Init__my_module_a(env, exports);
  napi_value ns_functiontest;
  napi_create_object(env, &ns_functiontest);
  Init__my_module_b_functiontest(env, ns_functiontest);
  Init__my_module_b_functiontest(env, exports);
  NAPI_CALL(env, napi_set_named_property(env, exports, "functiontest",
                                         ns_functiontest));
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
