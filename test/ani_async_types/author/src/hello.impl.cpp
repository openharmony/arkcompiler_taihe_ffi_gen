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

void futureResultWithCallback(int64_t ms, ::taihe::string_view val, ::taihe::completer<expected_type> completer)
{
    std::thread([ms, val = taihe::string(val), completer = std::move(completer)]() mutable {
        std::cout << "[Future Result] Waiting for " << ms << " milliseconds..." << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
        std::cout << "[Future Result] Task completed, completing future..." << std::endl;
        completer.complete("C++AsyncProcessed-" + val);
    }).detach();
}

taihe::future<expected_type> futureResultReturnsPromise(int64_t ms, ::taihe::string_view val)
{
    auto [completer, future] = taihe::make_contract<expected_type>();
    futureResultWithCallback(ms, val, std::move(completer));
    return std::move(future);
}

void processUserTypeWithCallback(::hello::weak::UserType user, int64_t ms, ::taihe::string_view result,
                                 ::taihe::completer<expected_type> fin)
{
    std::cout << "[Process UserType With Callback] Calling UserType method with callback..." << std::endl;

    auto [mid, tmp] = taihe::make_contract<expected_type>();

    auto exp = user->fooWithCallback(ms, "C++SyncProcessed-" + result, std::move(mid));

    if (not exp) {
        std::cerr << "[Process UserType With Callback] Error calling UserType method: " << exp.error().message()
                  << std::endl;
        fin.complete(taihe::unexpected<taihe::error>(exp.error()));
        return;
    }

    std::cerr << "[Process UserType With Callback] UserType method called successfully, waiting for result..."
              << std::endl;

    struct Processor {
        taihe::completer<expected_type> fin;

        Processor(taihe::completer<expected_type> fin) : fin(std::move(fin))
        {
        }

        void operator()(expected_type res) const
        {
            if (res) {
                std::cout << "[Process UserType With Callback] UserType method completed successfully." << std::endl;
                fin.complete("C++AsyncProcessed-" + res.value());
            } else {
                std::cerr << "[Process UserType With Callback] UserType method completed with error: "
                          << res.error().message() << std::endl;
                fin.complete(taihe::unexpected<taihe::error>(res.error()));
            }
        }
    };

    tmp.on_complete<Processor>(std::move(fin));
    return;
}

taihe::future<expected_type> processUserTypeReturnsPromise(::hello::weak::UserType user, int64_t ms,
                                                           ::taihe::string_view result)
{
    std::cout << "[Process UserType Returns Promise] Calling UserType method that returns promise..." << std::endl;

    auto exp = user->fooReturnsPromise(ms, "C++SyncProcessed-" + result);

    auto [fin, fut] = taihe::make_contract<expected_type>();

    if (not exp) {
        std::cerr << "[Process UserType Returns Promise] Error calling UserType method: " << exp.error().message()
                  << std::endl;
        fin.complete(taihe::unexpected<taihe::error>(exp.error()));
        return std::move(fut);
    }

    std::cerr
        << "[Process UserType Returns Promise] UserType method called successfully, waiting for promise to complete..."
        << std::endl;

    struct Processor {
        taihe::completer<expected_type> fin;

        Processor(taihe::completer<expected_type> fin) : fin(std::move(fin))
        {
        }

        void operator()(expected_type res) const
        {
            if (res) {
                std::cout << "[Process UserType Returns Promise] UserType method completed successfully." << std::endl;
                fin.complete("C++AsyncProcessed-" + res.value());
            } else {
                std::cerr << "[Process UserType Returns Promise] UserType method completed with error: "
                          << res.error().message() << std::endl;
                fin.complete(taihe::unexpected<taihe::error>(res.error()));
            }
        }
    };

    exp.value().on_complete<Processor>(std::move(fin));
    return std::move(fut);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_futureResultWithCallback(futureResultWithCallback);
TH_EXPORT_CPP_API_futureResultReturnsPromise(futureResultReturnsPromise);
TH_EXPORT_CPP_API_processUserTypeWithCallback(processUserTypeWithCallback);
TH_EXPORT_CPP_API_processUserTypeReturnsPromise(processUserTypeReturnsPromise);
// NOLINTEND
