#pragma once

#include <functional>
#include <optional>
#include <iostream>
#include <queue>

#include <taihe/common.hpp>
#include <core/object.hpp>

namespace taihe::core {
template<typename T>
struct promise;

template<typename U>
struct promise_helper {
    impl_holder<promise<U>> nextPromise;

    auto operator()(U const& result) {
        nextPromise->operator()(result);
        return make_holder<promise<U>>();
    }
};

template<typename T>
struct promise {
    using result_type = T;

    std::queue<std::function<auto (T const& value) -> void>> thenCallbacks;
    std::optional<T> optValue;

    promise() {}
    ~promise() {}

    template<typename... Args>
    void operator()(Args&&... args) {
        if (optValue.has_value()) {
            return;
        }
    
        optValue.emplace(std::forward<Args>(args)...);
    
        while (!thenCallbacks.empty()) {
            thenCallbacks.front()(*optValue);
            thenCallbacks.pop();
        }
    }

    auto then(auto&& onResolved) -> impl_holder<promise<typename decltype(onResolved(std::declval<T>()))::impl_type::result_type>> {
        using U = decltype(onResolved(std::declval<T>()))::impl_type::result_type;

        auto nextPromise = make_holder<promise<U>>();

        auto thenCallback = [nextPromise, onResolved](T const& value) mutable {
            onResolved(value)
                ->then(promise_helper<U>(std::move(nextPromise)));
        };

        if (optValue.has_value()) {
            thenCallback(*optValue);
        } else {
            thenCallbacks.push(thenCallback);
        }

        return nextPromise;
    }
};

template<typename T>
auto make_resolved(auto&&... args) {
    auto result = make_holder<promise<T>>();
    result->operator()(std::forward<decltype(args)>(args)...);
    return result;
}

template<typename T, typename... InterfaceHolders>
auto make_promise(auto&& asyncFunc) {
    auto result = make_holder<promise<T>, InterfaceHolders...>();
    asyncFunc(result);
    return result;
}
}
