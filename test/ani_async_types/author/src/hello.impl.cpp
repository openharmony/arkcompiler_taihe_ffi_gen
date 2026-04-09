/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
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

#include "hello.impl.hpp"
#include "hello.proj.hpp"
#include "stdexcept"

#include <chrono>
#include <iostream>
#include <thread>

namespace {
using expected_type = ::taihe::expected<::taihe::string, ::taihe::error>;

void futureResultWithCallback(int64_t ms, ::taihe::string_view val, ::taihe::completer<expected_type> setter)
{
    std::thread([ms, val = taihe::string(val), setter = std::move(setter)]() mutable {
        std::cout << "[Future Result] Waiting for " << ms << " milliseconds..." << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
        std::cout << "[Future Result] Task completed, setting result..." << std::endl;
        setter.emplace_result(std::move(val));
    }).detach();
}

taihe::future<expected_type> futureResultReturnsPromise(int64_t ms, ::taihe::string_view val)
{
    auto [setter, result] = taihe::make_async_pair<expected_type>();
    futureResultWithCallback(ms, val, std::move(setter));
    return std::move(result);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_futureResultWithCallback(futureResultWithCallback);
TH_EXPORT_CPP_API_futureResultReturnsPromise(futureResultReturnsPromise);
// NOLINTEND
