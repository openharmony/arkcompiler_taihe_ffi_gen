#pragma once

#include <functional>
#include <optional>
#include <iostream>
#include <queue>

#include <taihe/common.hpp>
#include <core/object.hpp>

namespace taihe::core {
template <typename T>
struct Promise;

template <typename U, typename... InterfaceHolders>
struct PromiseInner {
    decltype(make_holder<Promise<U>, InterfaceHolders...>()) promise;

    auto operator()(U const& result) {
        promise->operator()(result);
        return make_holder<Promise<U>, InterfaceHolders...>();
    }
};

template <typename T>
struct Promise {
    std::queue<std::function<auto (T const& value) -> void>> thenCallbacks;
    std::optional<T> optValue;

    Promise() {}
    ~Promise() {}

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

    template <typename U, typename... InterfaceHolders>
    auto then(auto&& onResolved) -> decltype(make_holder<Promise<U>, InterfaceHolders...>()) {
        auto nextPromise = make_holder<Promise<U>, InterfaceHolders...>();

        auto thenCallback = [nextPromise, onResolved](T const& value) mutable {
            onResolved(value)
                ->template then<U, InterfaceHolders...>(PromiseInner<U, InterfaceHolders...>(std::move(nextPromise)));
        };

        if (optValue.has_value()) {
            thenCallback(*optValue);
        } else {
            thenCallbacks.push(thenCallback);
        }

        return nextPromise;
    }
};

template <typename T>
auto make_resolved(auto&&... args) {
    auto promise = make_holder<Promise<T>>();
    promise->operator()(std::forward<decltype(args)>(args)...);
    return promise;
}

template <typename T, typename... InterfaceHolders>
auto make_promise(auto&& asyncFunc) {
    auto promise = make_holder<Promise<T>, InterfaceHolders...>();
    asyncFunc(promise);
    return promise;
}
}
