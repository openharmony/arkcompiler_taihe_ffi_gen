#include "import_example.impl.hpp"
#include "import_example.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

void testImport(::export_example::Inner const &obj) {
  std::cout << "obj.str= " << obj.s << ", obj.int= " << obj.i << std::endl;
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_testImport(testImport);
// NOLINTEND
