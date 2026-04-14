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
#include <vector>

#include "taihe/array.hpp"
#include "taihe/runtime.hpp"
#include "taihe/string.hpp"

#include "test.impl.hpp"
#include "test.proj.hpp"

namespace {
// To be implemented.

class CallbackManagerImpl {
    std::vector<::taihe::callback<::taihe::expected<::taihe::string, ::taihe::error>()>> callbacks_;

public:
    CallbackManagerImpl()
    {
    }

    ::taihe::expected<bool, ::taihe::error> addCallback(
        ::taihe::callback_view<::taihe::expected<::taihe::string, ::taihe::error>()> new_cb)
    {
        for (auto const &old_cb : callbacks_) {
            if (old_cb == new_cb) {
                std::cerr << "Callback already exists." << std::endl;
                return false;
            }
        }
        callbacks_.emplace_back(new_cb);
        return true;
    }

    ::taihe::expected<bool, ::taihe::error> removeCallback(
        ::taihe::callback_view<::taihe::expected<::taihe::string, ::taihe::error>()> cb)
    {
        for (auto it = callbacks_.begin(); it != callbacks_.end(); ++it) {
            if (*it == cb) {
                callbacks_.erase(it);
                return true;
            }
        }
        std::cerr << "Callback not found." << std::endl;
        return false;
    }

    ::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> invokeCallbacks()
    {
        std::vector<::taihe::string> results;
        for (auto const &cb : callbacks_) {
            auto result = cb();
            if (result.has_value()) {
                results.push_back(result.value());
            }
        }
        return ::taihe::array<::taihe::string>(::taihe::copy_data, results.data(), results.size());
    }
};

::taihe::expected<::test::CallbackManager, ::taihe::error> getCallbackManager()
{
    return taihe::make_holder<CallbackManagerImpl, ::test::CallbackManager>();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_getCallbackManager(getCallbackManager);
// NOLINTEND
