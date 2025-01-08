#include <vector>
#include <thread>
#include <chrono>

#include "sys.time.proj.hpp"
#include "sys.time.impl.hpp"

using namespace sys::time;

void setTimeoutImpl(weak::ICallbackVoid cb, uint64_t ms) {
    std::thread([cb = ICallbackVoid(cb), ms]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
        cb();
    }).detach();
}

struct CallerImpl {
    std::vector<ICallbackString> vec;

    void setValue(taihe::core::string_view state) {
        for (weak::ICallbackString cb : vec) {
            cb(state);
        }
    }

    void waitForValue(weak::ICallbackString cb) {
        vec.emplace_back(cb);
    }
};

auto makeCallerImpl() {
    return taihe::core::make_holder<CallerImpl, ICaller>();
}

TH_EXPORT_CPP_API_makeCaller(makeCallerImpl)
TH_EXPORT_CPP_API_setTimeout(setTimeoutImpl)
