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
// This file is a test file.
// NOLINTBEGIN

#include "thread_test.impl.hpp"

#include <chrono>
#include <iostream>
#include <thread>

using namespace taihe;

namespace {
static constexpr int32_t THOUSAND = 1000;

void invokeFromOtherThreadAfter(double sec, ::taihe::callback_view<int32_t(int32_t a)> cb)
{
    // Directly call
    cb(1);

    // call in the new thread
    std::cout << "!!!!!!!!!!" << std::endl;
    std::cerr << "-- begin invokeFromOtherThreadAfter --" << std::endl;
    std::thread thread([sec, cb = callback<int32_t(int32_t a)>(cb)]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(sec * THOUSAND)));
        std::cerr << "invokeFromOtherThreadAfter: " << sec << " seconds" << std::endl;
        std::cout << "result: " << cb(1) << std::endl;
    });
    thread.detach();
    std::cerr << "-- end invokeFromOtherThreadAfter --" << std::endl;
}
}  // namespace

TH_EXPORT_CPP_API_invokeFromOtherThreadAfter(invokeFromOtherThreadAfter);
// NOLINTEND
