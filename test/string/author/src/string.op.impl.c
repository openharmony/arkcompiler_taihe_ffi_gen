#include "string.op.impl.h"

struct TString ohos_concat_str(struct TString a, struct TString b) {
  return tstr_concat(a, b);
}

TH_EXPORT_C_API_concat(ohos_concat_str);
