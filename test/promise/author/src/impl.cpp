#include <vector>
#include <thread>
#include <chrono>

#include "sys.time.proj.hpp"
#include "sys.time.impl.hpp"

void setTimeoutImpl(weak::sys::time::ICallbackVoid cb, uint64_t ms) {
    std::thread([cb = sys::time::ICallbackVoid(cb), ms]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
        cb();
    }).detach();
}

struct CallerImpl {
    std::vector<sys::time::ICallbackString> vec;

    void setValue(taihe::core::string_view state) {
        for (weak::sys::time::ICallbackString cb : vec) {
            cb(state);
        }
    }

    void waitForValue(weak::sys::time::ICallbackString cb) {
        vec.emplace_back(cb);
    }
};

auto makeCallerImpl() {
    return taihe::core::make_holder<CallerImpl, sys::time::ICaller>();
}

TH_EXPORT_CPP_API_makeCaller(makeCallerImpl)
TH_EXPORT_CPP_API_setTimeout(setTimeoutImpl)
