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

#include <chrono>
#include <iostream>
#include <thread>

namespace {
using expected_type = ::taihe::expected<::taihe::string, ::taihe::error>;

::taihe::expected<void, ::taihe::error> FutureResultWithCallback(int64_t ms, ::taihe::string_view val,
                                                                 ::taihe::completer<expected_type> completer)
{
    if (ms < 0) {
        return taihe::unexpected<taihe::error>("ms cannot be negative");
    }
    std::thread([ms, val = taihe::string(val), completer = std::move(completer)]() mutable {
        std::cout << "[Future Result] Waiting for " << ms << " milliseconds..." << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
        std::cout << "[Future Result] Task completed, completing future..." << std::endl;
        if (val.empty()) {
            completer.complete(taihe::unexpected<taihe::error>("val cannot be empty"));
        } else {
            completer.complete("C++AsyncProcessed-" + val);
        }
    }).detach();
    return {};
}

::taihe::expected<::taihe::future<expected_type>, ::taihe::error> FutureResultReturnsPromise(int64_t ms,
                                                                                             ::taihe::string_view val)
{
    auto [completer, future] = taihe::make_async_pair<expected_type>();
    if (ms < 0) {
        return taihe::unexpected<taihe::error>("ms cannot be negative");
    }
    std::thread([ms, val = taihe::string(val), completer = std::move(completer)]() mutable {
        std::cout << "[Future Result Returns Promise] Waiting for " << ms << " milliseconds..." << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
        std::cout << "[Future Result Returns Promise] Task completed, completing future..." << std::endl;
        if (val.empty()) {
            completer.complete(taihe::unexpected<taihe::error>("val cannot be empty"));
        } else {
            completer.complete("C++AsyncProcessed-" + val);
        }
    }).detach();
    return std::move(future);
}

::taihe::expected<void, ::taihe::error> ProcessUserTypeWithCallback(::hello::weak::UserType user, int64_t etsMs,
                                                                    int64_t cppMs, ::taihe::string_view result,
                                                                    ::taihe::completer<expected_type> fin)
{
    if (etsMs < 0 || cppMs < 0) {
        return taihe::unexpected<taihe::error>("ms cannot be negative");
    }

    auto [mid, tmp] = taihe::make_async_pair<expected_type>();

    auto exp = user->fooWithCallback(etsMs, "C++SyncProcessed-" + result, std::move(mid));

    if (not exp) {
        std::cerr << "[Process UserType With Callback] Error calling UserType method: " << exp.error().message()
                  << std::endl;
        fin.complete(taihe::unexpected<taihe::error>(exp.error()));
    } else {
        std::cerr << "[Process UserType With Callback] UserType method called successfully, waiting for result..."
                  << std::endl;

        tmp.on_complete([fin = std::move(fin), cppMs](expected_type &&res) mutable {
            if (res) {
                std::cout << "[Process UserType With Callback] UserType method completed successfully." << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(cppMs));
                fin.complete("C++AsyncProcessed-" + res.value());
            } else {
                std::cerr << "[Process UserType With Callback] UserType method completed with error: "
                          << res.error().message() << std::endl;
                fin.complete(taihe::unexpected<taihe::error>(res.error()));
            }
        });
    }

    return {};
}

::taihe::expected<::taihe::future<expected_type>, ::taihe::error> ProcessUserTypeReturnsPromise(
    ::hello::weak::UserType user, int64_t etsMs, int64_t cppMs, ::taihe::string_view result)
{
    if (etsMs < 0 || cppMs < 0) {
        return taihe::unexpected<taihe::error>("ms cannot be negative");
    }

    auto exp = user->fooReturnsPromise(etsMs, "C++SyncProcessed-" + result);

    auto [fin, fut] = taihe::make_async_pair<expected_type>();

    if (not exp) {
        std::cerr << "[Process UserType Returns Promise] Error calling UserType method: " << exp.error().message()
                  << std::endl;
        fin.complete(taihe::unexpected<taihe::error>(exp.error()));
    } else {
        std::cerr << "[Process UserType Returns Promise] UserType method called successfully, waiting for promise to "
                     "complete..."
                  << std::endl;

        exp.value().on_complete([fin = std::move(fin), cppMs](expected_type &&res) mutable {
            if (res) {
                std::cout << "[Process UserType Returns Promise] UserType method completed successfully." << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(cppMs));
                fin.complete("C++AsyncProcessed-" + res.value());
            } else {
                std::cerr << "[Process UserType Returns Promise] UserType method completed with error: "
                          << res.error().message() << std::endl;
                fin.complete(taihe::unexpected<taihe::error>(res.error()));
            }
        });
    }

    return std::move(fut);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_futureResultWithCallback(FutureResultWithCallback);
TH_EXPORT_CPP_API_futureResultReturnsPromise(FutureResultReturnsPromise);
TH_EXPORT_CPP_API_processUserTypeWithCallback(ProcessUserTypeWithCallback);
TH_EXPORT_CPP_API_processUserTypeReturnsPromise(ProcessUserTypeReturnsPromise);
// NOLINTEND
