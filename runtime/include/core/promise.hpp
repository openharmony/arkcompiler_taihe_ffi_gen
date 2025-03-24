#pragma once

#include <condition_variable>
#include <core/object.hpp>
#include <functional>
#include <mutex>
#include <taihe/common.hpp>
#include <variant>
#include <vector>

namespace taihe::core {
template <typename V, typename E>
struct promise;

template <typename V, typename E>
using promise_holder = impl_holder<promise<V, E>>;

template <typename V, typename E>
using promise_view = impl_view<promise<V, E>>;

template <typename V, typename E, typename... InterfaceHolders>
auto make_promise() {
  return make_holder<promise<V, E>, InterfaceHolders...>();
}

template <typename V, typename E, typename... InterfaceHolders,
          typename AsyncFunc, typename... Args>
auto make_promise(AsyncFunc&& asyncFunc, Args&&... args) {
  auto result = make_promise<V, E, InterfaceHolders...>();
  asyncFunc(result, std::forward<Args>(args)...);
  return result;
}

template <typename V, typename E, typename... InterfaceHolders,
          typename... Args>
auto make_resolved(Args&&... args) {
  auto result = make_promise<V, E, InterfaceHolders...>();
  result->resolve(std::forward<Args>(args)...);
  return result;
}

template <typename V, typename E, typename... InterfaceHolders,
          typename... Args>
auto make_rejected(Args&&... args) {
  auto result = make_promise<V, E, InterfaceHolders...>();
  result->reject(std::forward<Args>(args)...);
  return result;
}

template <typename V, typename E>
struct promise {
  using value_type = V;
  using error_type = E;

 private:
  std::vector<std::function<void(V const& value)>> onResolvedCallbacks;
  std::vector<std::function<void(E const& value)>> onRejectedCallbacks;
  std::variant<std::monostate, V, E> state;

  std::mutex mutex;
  std::condition_variable cv;

 public:
  promise() : state(std::in_place_index<0>) {}
  ~promise() = default;

  promise(const promise&) = delete;
  promise& operator=(const promise&) = delete;

  // author
  template <typename... Args>
  void resolve(Args&&... args) {
    std::unique_lock<std::mutex> lock(mutex);
    if (state.index() != 0) {
      return;
    }
    V const& value = state.template emplace<1>(std::forward<Args>(args)...);
    for (const auto& callback : onResolvedCallbacks) {
      callback(value);
    }
    onResolvedCallbacks.clear();
    onRejectedCallbacks.clear();
    cv.notify_all();
  }

  template <typename... Args>
  void reject(Args&&... args) {
    std::unique_lock<std::mutex> lock(mutex);
    if (state.index() != 0) {
      return;
    }
    E const& error = state.template emplace<2>(std::forward<Args>(args)...);
    for (const auto& callback : onRejectedCallbacks) {
      callback(error);
    }
    onResolvedCallbacks.clear();
    onRejectedCallbacks.clear();
    cv.notify_all();
  }

  // user
  bool is_pending() const noexcept { return state.index() == 0; }

  void wait() {
    std::unique_lock<std::mutex> lock(mutex);
    cv.wait(lock, [this]() { return state.index() != 0; });
  }

  template <typename Callback>
  void call_on_resolved(Callback&& callback) {
    std::unique_lock<std::mutex> lock(mutex);
    if (state.index() == 0) {
      onResolvedCallbacks.push_back(std::forward<Callback>(callback));
    } else if (V const* ptrValue = std::get_if<1>(&state)) {
      callback(*ptrValue);
    }
  }

  template <typename Callback>
  void call_on_rejected(Callback&& callback) {
    std::unique_lock<std::mutex> lock(mutex);
    if (state.index() == 0) {
      onRejectedCallbacks.push_back(std::forward<Callback>(callback));
    } else if (E const* ptrError = std::get_if<2>(&state)) {
      callback(*ptrError);
    }
  }

  template <typename Callback>
  auto chained_then(Callback&& callback) {
    using promise_type =
        std::remove_reference_t<decltype(*callback(std::declval<V>()))>;
    using U = typename promise_type::value_type;
    auto next = make_promise<U, E>();
    this->call_on_resolved([callback, next](V const& value) {
      auto result = callback(value);
      result->call_on_resolved([next](U const& val) { next->resolve(val); });
      result->call_on_rejected([next](E const& err) { next->reject(err); });
    });
    this->call_on_rejected([next](E const& error) { next->reject(error); });
    return next;
  }

  template <typename Callback>
  auto chained_catch(Callback&& callback) {
    using promise_type =
        std::remove_reference_t<decltype(*callback(std::declval<E>()))>;
    using F = typename promise_type::error_type;
    auto next = make_promise<V, F>();
    this->call_on_rejected([callback, next](E const& error) {
      auto result = callback(error);
      result->call_on_rejected([next](F const& err) { next->reject(err); });
      result->call_on_resolved([next](V const& val) { next->resolve(val); });
    });
    this->call_on_resolved([next](V const& value) { next->resolve(value); });
    return next;
  }

  template <typename Callback>
  auto chained_finally(Callback&& callback) {
    using promise_type = std::remove_reference_t<decltype(*callback())>;
    using U = typename promise_type::value_type;
    using F = typename promise_type::error_type;
    auto next = make_promise<U, F>();
    this->call_on_resolved([callback, next](V const& value) {
      auto result = callback();
      result->call_on_resolved([next](U const& val) { next->resolve(val); });
      result->call_on_rejected([next](F const& err) { next->reject(err); });
    });
    this->call_on_rejected([callback, next](E const& error) {
      auto result = callback();
      result->call_on_resolved([next](U const& val) { next->resolve(val); });
      result->call_on_rejected([next](F const& err) { next->reject(err); });
    });
    return next;
  }
};
}  // namespace taihe::core
