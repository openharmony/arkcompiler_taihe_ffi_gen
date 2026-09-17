/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef TAIHE_EXPECTED_HPP
#define TAIHE_EXPECTED_HPP

#include <stdexcept>
#include <utility>
#include <type_traits>

#include <taihe/common.hpp>

#define TH_TRY(expr)                                                                          \
    ({                                                                                        \
        auto &&__result = (expr);                                                             \
        if (!__result.has_value()) {                                                          \
            return ::taihe::unexpected(::std::forward<decltype(__result)>(__result).error()); \
        }                                                                                     \
        *::std::forward<decltype(__result)>(__result);                                        \
    })

namespace taihe {
struct unexpect_t {
    explicit unexpect_t() = default;
};

constexpr inline unexpect_t unexpect {};

template<typename E>
class unexpected {
public:
    template<class... Args>
    explicit constexpr unexpected(std::in_place_t, Args &&...args) : unex(std::forward<Args>(args)...)
    {
    }

    template<class G = E, typename std::enable_if_t<
                              std::is_constructible_v<E, G &&> &&
                                  !std::is_same_v<std::remove_cv_t<std::remove_reference_t<G>>, std::in_place_t> &&
                                  !std::is_same_v<std::remove_cv_t<std::remove_reference_t<G>>, unexpected>,
                              int> = 0>
    explicit constexpr unexpected(G &&err) : unex(std::forward<G>(err))
    {
    }

    constexpr unexpected(unexpected const &) = default;
    constexpr unexpected(unexpected &&) = default;

    constexpr unexpected &operator=(unexpected const &) = default;
    constexpr unexpected &operator=(unexpected &&) = default;

    constexpr E const &error() const & noexcept
    {
        return unex;
    }

    constexpr E &error() & noexcept
    {
        return unex;
    }

    constexpr E const &&error() const && noexcept
    {
        return std::move(unex);
    }

    constexpr E &&error() && noexcept
    {
        return std::move(unex);
    }

    template<class G>
    friend constexpr bool operator==(unexpected const &x, unexpected<G> const &y)
    {
        return x.error() == y.error();
    }

private:
    E unex;
};

template<typename E>
unexpected(E) -> unexpected<E>;

template<typename T, typename E>
class expected;

template<typename E>
class expected<void, E> {
public:
    using value_type = void;
    using error_type = E;

    constexpr expected(expected const &other) noexcept(std::is_nothrow_copy_constructible_v<E>)
        : has_val(other.has_value())
    {
        if (!has_val) {
            new (&unex) E(other.error());
        }
    }

    constexpr expected(expected &&other) noexcept(std::is_nothrow_move_constructible_v<E>) : has_val(other.has_value())
    {
        if (!has_val) {
            new (&unex) E(std::move(other).error());
        }
    }

    template<typename G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr expected(expected<void, G> const &other) : has_val(other.has_value())
    {
        if (!has_val) {
            new (&unex) E(other.error());
        }
    }

    template<typename G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr expected(expected<void, G> &&other) : has_val(other.has_value())
    {
        if (!has_val) {
            new (&unex) E(std::move(other).error());
        }
    }

    constexpr expected() noexcept : has_val(true)
    {
    }

    explicit constexpr expected(std::in_place_t) : has_val(true)
    {
    }

    template<class G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr expected(unexpected<G> const &other) : has_val(false), unex(other.error())
    {
    }

    template<class G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr expected(unexpected<G> &&other) : has_val(false), unex(std::move(other).error())
    {
    }

    template<typename... Args>
    explicit constexpr expected(unexpect_t, Args &&...args) noexcept(std::is_nothrow_constructible_v<E, Args &&...>)
        : has_val(false), unex(std::forward<Args>(args)...)
    {
    }

    ~expected() noexcept(std::is_nothrow_destructible_v<E>)
    {
        if (!has_val) {
            unex.~E();
        }
    }

    expected &operator=(expected const &other) noexcept(std::is_nothrow_copy_constructible_v<E> &&
                                                        std::is_nothrow_copy_assignable_v<E> &&
                                                        std::is_nothrow_destructible_v<E>)
    {
        if (this != &other) {
            if (has_val != other.has_value()) {
                if (!has_val) {
                    unex.~E();
                }
                has_val = other.has_value();
                if (!has_val) {
                    new (&unex) E(other.error());
                }
            } else if (!has_val) {
                unex = other.error();
            }
        }
        return *this;
    }

    expected &operator=(expected &&other) noexcept(std::is_nothrow_move_constructible_v<E> &&
                                                   std::is_nothrow_move_assignable_v<E> &&
                                                   std::is_nothrow_destructible_v<E>)
    {
        if (this != &other) {
            if (has_val != other.has_value()) {
                if (!has_val) {
                    unex.~E();
                }
                has_val = other.has_value();
                if (!has_val) {
                    new (&unex) E(std::move(other).error());
                }
            } else if (!has_val) {
                unex = std::move(other).error();
            }
        }
        return *this;
    }

    template<typename G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    expected &operator=(expected<void, G> const &other)
    {
        if (has_val != other.has_value()) {
            if (!has_val) {
                unex.~E();
            }
            has_val = other.has_value();
            if (!has_val) {
                new (&unex) E(other.error());
            }
        } else if (!has_val) {
            unex = other.error();
        }
        return *this;
    }

    template<typename G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    expected &operator=(expected<void, G> &&other)
    {
        if (has_val != other.has_value()) {
            if (!has_val) {
                unex.~E();
            }
            has_val = other.has_value();
            if (!has_val) {
                new (&unex) E(std::move(other).error());
            }
        } else if (!has_val) {
            unex = std::move(other).error();
        }
        return *this;
    }

    template<class G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    expected &operator=(unexpected<G> const &other)
    {
        if (has_val) {
            has_val = false;
            new (&unex) E(other.error());
        } else {
            unex = other.error();
        }
        return *this;
    }

    template<class G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    expected &operator=(unexpected<G> &&other)
    {
        if (has_val) {
            has_val = false;
            new (&unex) E(std::move(other).error());
        } else {
            unex = std::move(other).error();
        }
        return *this;
    }

    explicit constexpr operator bool() const noexcept
    {
        return has_val;
    }

    constexpr bool has_value() const noexcept
    {
        return has_val;
    }

    constexpr void value() const
    {
        if (!has_val) {
            TH_THROW(std::runtime_error, "has error");
        }
    }

    constexpr void operator*() const
    {
        TH_ASSERT(has_val, "has error");
    }

    constexpr E const &error() const &
    {
        TH_ASSERT(!has_val, "has no error");
        return unex;
    }

    constexpr E &error() &
    {
        TH_ASSERT(!has_val, "has no error");
        return unex;
    }

    constexpr E const &&error() const &&
    {
        TH_ASSERT(!has_val, "has no error");
        return std::move(unex);
    }

    constexpr E &&error() &&
    {
        TH_ASSERT(!has_val, "has no error");
        return std::move(unex);
    }

    template<class G = E, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr E error_or(G &&default_value) const &
    {
        if (has_val) {
            return static_cast<E>(std::forward<G>(default_value));
        }
        return unex;
    }

    template<class G = E, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr E error_or(G &&default_value) &&
    {
        if (has_val) {
            return static_cast<E>(std::forward<G>(default_value));
        }
        return std::move(unex);
    }

private:
    bool has_val;

    union {
        E unex;
    };
};

template<typename T, typename E>
class expected {
public:
    using value_type = T;
    using error_type = E;

    constexpr expected(expected const &other) noexcept(std::is_nothrow_copy_constructible_v<T> &&
                                                       std::is_nothrow_copy_constructible_v<E>)
        : has_val(other.has_value())
    {
        if (has_val) {
            new (&val) T(other.value());
        } else {
            new (&unex) E(other.error());
        }
    }

    constexpr expected(expected &&other) noexcept(std::is_nothrow_move_constructible_v<T> &&
                                                  std::is_nothrow_move_constructible_v<E>)
        : has_val(other.has_value())
    {
        if (has_val) {
            new (&val) T(std::move(other).value());
        } else {
            new (&unex) E(std::move(other).error());
        }
    }

    template<class U, class G, std::enable_if_t<std::is_convertible_v<U, T> && std::is_convertible_v<G, E>, int> = 0>
    constexpr expected(expected<U, G> const &other) : has_val(other.has_value())
    {
        if (has_val) {
            new (&val) T(other.value());
        } else {
            new (&unex) E(other.error());
        }
    }

    template<class U, class G, std::enable_if_t<std::is_convertible_v<U, T> && std::is_convertible_v<G, E>, int> = 0>
    constexpr expected(expected<U, G> &&other) : has_val(other.has_value())
    {
        if (has_val) {
            new (&val) T(std::move(other).value());
        } else {
            new (&unex) E(std::move(other).error());
        }
    }

    constexpr expected() noexcept(std::is_nothrow_default_constructible_v<T>) : has_val(true), val()
    {
    }

    template<class U = T, typename std::enable_if_t<
                              std::is_constructible_v<T, U &&> && std::is_convertible_v<U &&, T> &&
                                  !std::is_same_v<std::remove_cv_t<std::remove_reference_t<U>>, std::in_place_t> &&
                                  !std::is_same_v<std::remove_cv_t<std::remove_reference_t<U>>, expected> &&
                                  !std::is_same_v<std::remove_cv_t<std::remove_reference_t<U>>, unexpected<E>> &&
                                  !std::is_same_v<std::remove_cv_t<std::remove_reference_t<U>>, unexpect_t>,
                              int> = 0>
    constexpr expected(U &&value) noexcept(std::is_nothrow_constructible_v<T, U &&>)
        : has_val(true), val(std::forward<U>(value))
    {
    }

    template<typename... Args>
    explicit constexpr expected(std::in_place_t,
                                Args &&...args) noexcept(std::is_nothrow_constructible_v<T, Args &&...>)
        : has_val(true), val(std::forward<Args>(args)...)
    {
    }

    template<class G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr expected(unexpected<G> const &other) : has_val(false), unex(other.error())
    {
    }

    template<class G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr expected(unexpected<G> &&other) : has_val(false), unex(std::move(other).error())
    {
    }

    template<typename... Args>
    explicit constexpr expected(unexpect_t, Args &&...args) noexcept(std::is_nothrow_constructible_v<E, Args &&...>)
        : has_val(false), unex(std::forward<Args>(args)...)
    {
    }

    ~expected() noexcept(std::is_nothrow_destructible_v<T> && std::is_nothrow_destructible_v<E>)
    {
        if (has_val) {
            val.~T();
        } else {
            unex.~E();
        }
    }

    constexpr expected &operator=(expected const &other) noexcept(std::is_nothrow_copy_constructible_v<T> &&
                                                                  std::is_nothrow_copy_constructible_v<E> &&
                                                                  std::is_nothrow_copy_assignable_v<T> &&
                                                                  std::is_nothrow_copy_assignable_v<E> &&
                                                                  std::is_nothrow_destructible_v<T> &&
                                                                  std::is_nothrow_destructible_v<E>)
    {
        if (this != &other) {
            if (has_val == other.has_value()) {
                if (has_val) {
                    val = other.value();
                } else {
                    unex = other.error();
                }
            } else {
                if (has_val) {
                    val.~T();
                } else {
                    unex.~E();
                }
                has_val = other.has_value();
                if (has_val) {
                    new (&val) T(other.value());
                } else {
                    new (&unex) E(other.error());
                }
            }
        }
        return *this;
    }

    constexpr expected &operator=(expected &&other) noexcept(std::is_nothrow_move_constructible_v<T> &&
                                                             std::is_nothrow_move_constructible_v<E> &&
                                                             std::is_nothrow_move_assignable_v<T> &&
                                                             std::is_nothrow_move_assignable_v<E> &&
                                                             std::is_nothrow_destructible_v<T> &&
                                                             std::is_nothrow_destructible_v<E>)
    {
        if (this != &other) {
            if (has_val == other.has_value()) {
                if (has_val) {
                    val = std::move(other).value();
                } else {
                    unex = std::move(other).error();
                }
            } else {
                if (has_val) {
                    val.~T();
                } else {
                    unex.~E();
                }
                has_val = other.has_value();
                if (has_val) {
                    new (&val) T(std::move(other).value());
                } else {
                    new (&unex) E(std::move(other).error());
                }
            }
        }
        return *this;
    }

    template<class U, class G, std::enable_if_t<std::is_convertible_v<U, T> && std::is_convertible_v<G, E>, int> = 0>
    constexpr expected &operator=(expected<U, G> const &other)
    {
        if (has_val == other.has_value()) {
            if (has_val) {
                val = other.value();
            } else {
                unex = other.error();
            }
        } else {
            if (has_val) {
                val.~T();
            } else {
                unex.~E();
            }
            has_val = other.has_value();
            if (has_val) {
                new (&val) T(other.value());
            } else {
                new (&unex) E(other.error());
            }
        }
        return *this;
    }

    template<class U, class G, std::enable_if_t<std::is_convertible_v<U, T> && std::is_convertible_v<G, E>, int> = 0>
    constexpr expected &operator=(expected<U, G> &&other)
    {
        if (has_val == other.has_value()) {
            if (has_val) {
                val = std::move(other).value();
            } else {
                unex = std::move(other).error();
            }
        } else {
            if (has_val) {
                val.~T();
            } else {
                unex.~E();
            }
            has_val = other.has_value();
            if (has_val) {
                new (&val) T(std::move(other).value());
            } else {
                new (&unex) E(std::move(other).error());
            }
        }
        return *this;
    }

    template<class U = T, typename std::enable_if<
                              std::is_constructible_v<T, U &&> && std::is_convertible_v<U &&, T> &&
                                  !std::is_same_v<std::remove_cv_t<std::remove_reference_t<U>>, std::in_place_t> &&
                                  !std::is_same_v<std::remove_cv_t<std::remove_reference_t<U>>, expected> &&
                                  !std::is_same_v<std::remove_cv_t<std::remove_reference_t<U>>, unexpected<E>> &&
                                  !std::is_same_v<std::remove_cv_t<std::remove_reference_t<U>>, unexpect_t>,
                              int>::type = 0>
    constexpr expected &operator=(U &&value)
    {
        if (has_val) {
            val = std::forward<U>(value);
        } else {
            unex.~E();
            has_val = true;
            new (&val) T(std::forward<U>(value));
        }
        return *this;
    }

    template<class G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr expected &operator=(unexpected<G> const &other)
    {
        if (!has_val) {
            unex = other.error();
        } else {
            val.~T();
            has_val = false;
            new (&unex) E(other.error());
        }
        return *this;
    }

    template<class G, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr expected &operator=(unexpected<G> &&other)
    {
        if (!has_val) {
            unex = std::move(other).error();
        } else {
            val.~T();
            has_val = false;
            new (&unex) E(std::move(other).error());
        }
        return *this;
    }

    explicit constexpr operator bool() const noexcept
    {
        return has_val;
    }

    constexpr bool has_value() const noexcept
    {
        return has_val;
    }

    constexpr T const &value() const &
    {
        if (!has_val) {
            TH_THROW(std::runtime_error, "has error");
        }
        return val;
    }

    constexpr T &value() &
    {
        if (!has_val) {
            TH_THROW(std::runtime_error, "has error");
        }
        return val;
    }

    constexpr T const &&value() const &&
    {
        if (!has_val) {
            TH_THROW(std::runtime_error, "has error");
        }
        return std::move(val);
    }

    constexpr T &&value() &&
    {
        if (!has_val) {
            TH_THROW(std::runtime_error, "has error");
        }
        return std::move(val);
    }

    constexpr T const &operator*() const &
    {
        TH_ASSERT(has_val, "has error");
        return val;
    }

    constexpr T &operator*() &
    {
        TH_ASSERT(has_val, "has error");
        return val;
    }

    constexpr T const &&operator*() const &&
    {
        TH_ASSERT(has_val, "has error");
        return std::move(val);
    }

    constexpr T &&operator*() &&
    {
        TH_ASSERT(has_val, "has error");
        return std::move(val);
    }

    constexpr T const *operator->() const
    {
        TH_ASSERT(has_val, "has error");
        return &val;
    }

    constexpr T *operator->()
    {
        TH_ASSERT(has_val, "has error");
        return &val;
    }

    template<class U = T, std::enable_if_t<std::is_convertible_v<U, T>, int> = 0>
    constexpr T value_or(U &&default_value) const &
    {
        if (!has_val) {
            return static_cast<T>(std::forward<U>(default_value));
        }
        return val;
    }

    template<class U = T, std::enable_if_t<std::is_convertible_v<U, T>, int> = 0>
    constexpr T value_or(U &&default_value) &&
    {
        if (!has_val) {
            return static_cast<T>(std::forward<U>(default_value));
        }
        return std::move(val);
    }

    constexpr E const &error() const &
    {
        TH_ASSERT(!has_val, "has no error");
        return unex;
    }

    constexpr E &error() &
    {
        TH_ASSERT(!has_val, "has no error");
        return unex;
    }

    constexpr E const &&error() const &&
    {
        TH_ASSERT(!has_val, "has no error");
        return std::move(unex);
    }

    constexpr E &&error() &&
    {
        TH_ASSERT(!has_val, "has no error");
        return std::move(unex);
    }

    template<class G = E, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr E error_or(G &&default_value) const &
    {
        if (has_val) {
            return static_cast<E>(std::forward<G>(default_value));
        }
        return unex;
    }

    template<class G = E, std::enable_if_t<std::is_convertible_v<G, E>, int> = 0>
    constexpr E error_or(G &&default_value) &&
    {
        if (has_val) {
            return static_cast<E>(std::forward<G>(default_value));
        }
        return std::move(unex);
    }

private:
    bool has_val;

    union {
        T val;
        E unex;
    };
};

template<typename T>
struct is_expected : std::false_type {};

template<typename T, typename E>
struct is_expected<taihe::expected<T, E>> : std::true_type {};

template<typename T>
constexpr inline bool is_expected_v = is_expected<T>::value;
}  // namespace taihe

#endif  // TAIHE_EXPECTED_HPP
