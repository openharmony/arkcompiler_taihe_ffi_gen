#include "sys.time.proj.hpp"
#include "core/promise.hpp"

#include <iostream>
#include <thread>
#include <chrono>

using namespace sys::time;
using namespace taihe::core;

auto make_future_string(string_view sv, uint64_t ms) {
    return make_promise<taihe::core::string_view, ICallbackString>(
        [sv, ms](weak::sys::time::ICallbackString promise) {
            setTimeout(into_holder<ICallbackVoid>([promise = ICallbackString(promise), s = string(sv), ms]() { promise(s); }), ms);
        }
    );
}

int main() {
    std::cout << "Before promise" << std::endl;
    auto a = make_future_string("Promise 1", 1000)
        ->template then<taihe::core::string_view, ICallbackString>(
            [](taihe::core::string_view str) {
                std::cout << str.c_str() << std::endl;
                return make_future_string("Promise 2", 1000);
            })
        ->template then<taihe::core::string_view, ICallbackString>(
            [](taihe::core::string_view str) {
                std::cout << str.c_str() << std::endl;
                return make_future_string("Promise 3", 1000);
            })
        ->template then<uint64_t>(
            [](taihe::core::string_view str) {
                std::cout << str.c_str() << std::endl;
                return make_resolved<uint64_t>(0);
            });
    std::cout << "After promise" << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(5000));
}
