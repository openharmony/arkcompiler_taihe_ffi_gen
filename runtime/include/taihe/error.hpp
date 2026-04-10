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

#ifndef TAIHE_ERROR_HPP
#define TAIHE_ERROR_HPP

#include <taihe/error.abi.h>
#include <taihe/common.hpp>
#include <taihe/string.hpp>

namespace taihe {
class error {
private:
    int32_t code_;
    taihe::string message_;

public:
    explicit error(taihe::string_view message) : code_(0), message_(message)
    {
    }

    explicit error(taihe::string_view message, int32_t code) : code_(code), message_(message)
    {
    }

    error(error const &) = default;
    error(error &&) = default;
    error &operator=(error const &) = default;
    error &operator=(error &&) = default;

    taihe::string const &message() const noexcept
    {
        return message_;
    }

    int32_t code() const noexcept
    {
        return code_;
    }

    friend bool operator==(error const &lhs, error const &rhs) noexcept
    {
        return lhs.code_ == rhs.code_ && lhs.message_ == rhs.message_;
    }
};

template<>
struct as_abi<error> {
    using type = TError;
};
}  // namespace taihe

#endif  // TAIHE_ERROR_HPP
