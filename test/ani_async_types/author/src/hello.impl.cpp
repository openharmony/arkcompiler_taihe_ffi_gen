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

::taihe::expected<void, ::taihe::error> futureResultWithCallback(int64_t ms, ::taihe::string_view val,
                                                                 ::taihe::completer<expected_type> completer)
{
    std::thread([ms, val = taihe::string(val), completer = std::move(completer)]() mutable {
        std::cout << "[Future Result] Waiting for " << ms << " milliseconds..." << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
        std::cout << "[Future Result] Task completed, setting future..." << std::endl;
        completer.complete(std::move(val));
    }).detach();
    return {};
}

taihe::future<expected_type> futureResultReturnsPromise(int64_t ms, ::taihe::string_view val)
{
    auto [completer, future] = taihe::make_contract<expected_type>();
    futureResultWithCallback(ms, val, std::move(completer));
    return std::move(future);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_futureResultWithCallback(futureResultWithCallback);
TH_EXPORT_CPP_API_futureResultReturnsPromise(futureResultReturnsPromise);
// NOLINTEND
