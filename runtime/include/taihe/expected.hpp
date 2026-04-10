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

#include <taihe/error.hpp>

namespace taihe {
struct unexpect_t {
    explicit unexpect_t() = default;
};

constexpr inline unexpect_t unexpect {};

template<typename E>
class unexpected {
public:
    constexpr unexpected(unexpected const &) = default;
    constexpr unexpected(unexpected &&) = default;

    template<class... Args>
    constexpr explicit unexpected(std::in_place_t, Args &&...args) : unex(std::forward<Args>(args)...)
    {
    }

    template<class Err = E>
    constexpr explicit unexpected(Err &&err) : unex(std::forward<Err>(err))
    {
    }

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

    template<class E2>
    friend constexpr bool operator==(unexpected const &x, unexpected<E2> const &y)
    {
        return x.error() == y.error();
    }

private:
    E unex;
};

template<typename T, typename E>
class expected;

template<typename E>
class expected<void, E> {
public:
    using value_type = void;
    using error_type = E;

    constexpr expected() noexcept : has_val(true)
    {
    }

    constexpr expected(expected const &other) noexcept(std::is_nothrow_copy_constructible<E>::value)
        : has_val(other.has_val)
    {
        if (!has_val) {
            new (&unex) E(other.unex);
        }
    }

    constexpr expected(expected &&other) noexcept(std::is_nothrow_move_constructible<E>::value) : has_val(other.has_val)
    {
        if (!has_val) {
            new (&unex) E(std::move(other.unex));
        }
    }

    expected &operator=(expected const &other) noexcept(std::is_nothrow_copy_constructible_v<E> &&
                                                        std::is_nothrow_destructible_v<E>)
    {
        if (this != &other) {
            if (has_val != other.has_val) {
                if (!has_val) {
                    unex.~E();
                }
                has_val = other.has_val;
                if (!has_val) {
                    new (&unex) E(other.unex);
                }
            } else if (!has_val) {
                unex = other.unex;
            }
        }
        return *this;
    }

    expected &operator=(expected &&other) noexcept(std::is_nothrow_move_constructible_v<E> &&
                                                   std::is_nothrow_destructible_v<E>)
    {
        if (this != &other) {
            if (has_val != other.has_val) {
                if (!has_val) {
                    unex.~E();
                }
                has_val = other.has_val;
                if (!has_val) {
                    new (&unex) E(std::move(other.unex));
                }
            } else if (!has_val) {
                unex = std::move(other.unex);
            }
        }
        return *this;
    }

    template<class G>
    constexpr expected(unexpected<G> const &other) : has_val(false), unex(other.error())
    {
    }

    template<class G>
    constexpr expected(unexpected<G> &&other) : has_val(false), unex(std::move(other.error()))
    {
    }

    template<typename... Args>
    constexpr explicit expected(unexpect_t, Args &&...args) noexcept(std::is_nothrow_constructible_v<E, Args &&...>)
        : has_val(false), unex(std::forward<Args>(args)...)
    {
    }

    ~expected() noexcept(std::is_nothrow_destructible_v<E>)
    {
        if (!has_val) unex.~E();
    }

    constexpr explicit operator bool() const noexcept
    {
        return has_val;
    }

    constexpr bool has_value() const noexcept
    {
        return has_val;
    }

    constexpr void value() const
    {
        if (!has_val) TH_THROW(std::runtime_error, "no value");
    }

    constexpr E const &error() const &
    {
        if (has_val) TH_THROW(std::runtime_error, "has value");
        return unex;
    }

    constexpr E &error() &
    {
        if (has_val) TH_THROW(std::runtime_error, "has value");
        return unex;
    }

    constexpr E const &&error() const &&
    {
        if (has_val) TH_THROW(std::runtime_error, "has value");
        return std::move(unex);
    }

    constexpr E &&error() &&
    {
        if (has_val) TH_THROW(std::runtime_error, "has value");
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
        : has_val(other.has_val)
    {
        if (has_val) {
            new (&val) T(other.val);
        } else {
            new (&unex) E(other.unex);
        }
    }

    constexpr expected(expected &&other) noexcept(std::is_nothrow_move_constructible_v<T> &&
                                                  std::is_nothrow_move_constructible_v<E>)
        : has_val(other.has_val)
    {
        if (has_val) {
            new (&val) T(std::move(other.val));
        } else {
            new (&unex) E(std::move(other.unex));
        }
    }

    template<class U = T, typename std::enable_if<
                              std::is_constructible<T, U &&>::value && std::is_convertible<U &&, T>::value &&
                                  !std::is_same<std::remove_cv_t<std::remove_reference_t<U>>, std::in_place_t>::value &&
                                  !std::is_same<std::remove_cv_t<std::remove_reference_t<U>>, expected>::value &&
                                  !std::is_same<std::remove_cv_t<std::remove_reference_t<U>>, unexpected<E>>::value &&
                                  !std::is_same<std::remove_cv_t<std::remove_reference_t<U>>, unexpect_t>::value,
                              int>::type = 0>
    constexpr expected(U &&value) noexcept(std::is_nothrow_constructible<T, U &&>::value)
        : has_val(true), val(std::forward<U>(value))
    {
    }

    template<class G>
    constexpr expected(unexpected<G> const &other) : has_val(false), unex(other.error())
    {
    }

    template<class G>
    constexpr expected(unexpected<G> &&other) : has_val(false), unex(std::move(other).error())
    {
    }

    template<typename... Args>
    constexpr explicit expected(std::in_place_t,
                                Args &&...args) noexcept(std::is_nothrow_constructible_v<T, Args &&...>)
        : has_val(true), val(std::forward<Args>(args)...)
    {
    }

    template<typename... Args>
    constexpr explicit expected(unexpect_t, Args &&...args) noexcept(std::is_nothrow_constructible_v<E, Args &&...>)
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
            if (has_val == other.has_val) {
                if (has_val) {
                    val = other.val;
                } else {
                    unex = other.unex;
                }
            } else {
                if (has_val) {
                    val.~T();
                } else {
                    unex.~E();
                }
                has_val = other.has_val;
                if (has_val) {
                    new (&val) T(other.val);
                } else {
                    new (&unex) E(other.unex);
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
            if (has_val == other.has_val) {
                if (has_val) {
                    val = std::move(other.val);
                } else {
                    unex = std::move(other.unex);
                }
            } else {
                if (has_val) {
                    val.~T();
                } else {
                    unex.~E();
                }

                has_val = other.has_val;

                if (has_val) {
                    new (&val) T(std::move(other.val));
                } else {
                    new (&unex) E(std::move(other.unex));
                }
            }
        }
        return *this;
    }

    constexpr explicit operator bool() const noexcept
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
            TH_THROW(std::runtime_error, "No value");
        }
        return val;
    }

    constexpr T &value() &
    {
        if (!has_val) {
            TH_THROW(std::runtime_error, "No value");
        }
        return val;
    }

    constexpr T const &&value() const &&
    {
        if (!has_val) {
            TH_THROW(std::runtime_error, "No value");
        }
        return std::move(val);
    }

    constexpr T &&value() &&
    {
        if (!has_val) {
            TH_THROW(std::runtime_error, "No value");
        }
        return std::move(val);
    }

    constexpr E const &error() const &
    {
        if (has_val) {
            TH_THROW(std::runtime_error, "Has value, no error");
        }
        return unex;
    }

    constexpr E &error() &
    {
        if (has_val) {
            TH_THROW(std::runtime_error, "Has value, no error");
        }
        return unex;
    }

    constexpr E const &&error() const &&
    {
        if (has_val) {
            TH_THROW(std::runtime_error, "Has value, no error");
        }
        return std::move(unex);
    }

    constexpr E &&error() &&
    {
        if (has_val) {
            TH_THROW(std::runtime_error, "Has value, no error");
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
