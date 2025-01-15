#include "sys.time.proj.hpp"
#include "core/promise.hpp"

#include <iostream>
#include <thread>
#include <chrono>

using namespace sys::time;
using namespace taihe::core;

template<typename T, typename E>
auto make_future_value(T&& value, uint64_t ms) {
    return make_promise<T, E>(
        [value = std::forward<T>(value), ms](promise_view<T, E> p) {
            setTimeout(into_holder<ICallback>([p = promise_holder<T, E>(p), value, ms]() { p->resolve(value); }), ms);
        }
    );
}

template<typename T, typename E>
auto make_future_error(E&& error, uint64_t ms) {
    return make_promise<T, E>(
        [error = std::forward<E>(error), ms](promise_view<T, E> p) {
            setTimeout(into_holder<ICallback>([p = promise_holder<T, E>(p), error, ms]() { p->reject(error); }), ms);
        }
    );
}

int main() {
    std::cout << "Before promise" << std::endl;
    auto final_future_string = make_future_value<uint64_t, string>(42, 1000)
        ->chained_then(
            [](int val) {
                std::cout << "Got value: " << val << std::endl;
                std::cout << "Please input in 3 sec:" << std::endl;
                return make_promise<string, string, IPromiseStringString>(getInputWithTimeout, 3);
            }
        )
        ->chained_then(
            [](string_view sv) {
                std::cout << "Your 1st input: " << sv.c_str() << std::endl;
                std::cout << "Please input in 3 sec:" << std::endl;
                return make_promise<string, string, IPromiseStringString>(getInputWithTimeout, 3);
            }
        )
        ->chained_then(
            [](string_view sv) {
                std::cout << "Your 2nd input: " << sv.c_str() << std::endl;
                std::cout << "Please input in 3 sec:" << std::endl;
                return make_promise<string, string, IPromiseStringString>(getInputWithTimeout, 3);
            }
        )
        ->chained_then(
            [](string_view sv) {
                std::cout << "Your 3rd input: " << sv.c_str() << std::endl;
                std::cout << "Please input in 3 sec:" << std::endl;
                return make_promise<string, string, IPromiseStringString>(getInputWithTimeout, 3);
            }
        )
        ->chained_then(
            [](string_view sv) {
                std::cout << "Your final input: " << sv.c_str() << std::endl;
                return make_resolved<int, string>(0);
            }
        )
        ->chained_catch(
            [](string_view sv) {
                std::cout << "Error: " << sv.c_str() << std::endl;
                return make_resolved<int, string>(0);
            }
        )
        ->chained_finally(
            []() {
                std::cout << "Finally" << std::endl;
                return make_resolved<int, string>(0);
            }
        );
    std::cout << "After promise" << std::endl;
    final_future_string->wait();
    std::cout << "Done" << std::endl;
}
