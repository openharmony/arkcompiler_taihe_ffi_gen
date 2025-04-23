#include "thread_test.impl.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"
#include "thread_test.proj.hpp"

#include <chrono>
#include <iostream>
#include <thread>

using namespace taihe;

namespace {
// To be implemented.

void invokeFromOtherThreadAfter(double sec, callback_view<void()> cb) {
  std::cerr << "-- begin invokeFromOtherThreadAfter --" << std::endl;
  std::thread thread([sec, cb = callback<void()>(cb)]() {
    std::this_thread::sleep_for(
        std::chrono::milliseconds(static_cast<int>(sec * 1000)));
    std::cerr << "invokeFromOtherThreadAfter: " << sec << " seconds"
              << std::endl;
    cb();
  });
  thread.detach();
  std::cerr << "-- end invokeFromOtherThreadAfter --" << std::endl;
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_invokeFromOtherThreadAfter(invokeFromOtherThreadAfter);
// NOLINTEND
