#include "metadata.impl.hpp"
#include "metadata.h"
#include "metadata.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace metadata;

namespace {

Metadata GetMetadata() {
  return make_holder<MetadataImpl, Metadata>();
}
}  // namespace

TH_EXPORT_CPP_API_GetMetadata(GetMetadata);