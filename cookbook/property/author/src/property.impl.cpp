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
#include "property.impl.hpp"

#include <iostream>
#include <string>

using namespace taihe;
using namespace property;

namespace {

class CounterImpl {
public:
    CounterImpl(string_view label) : count_(0), label_(label)
    {
    }

    ::taihe::expected<int32_t, ::taihe::error> getCount()
    {
        return count_;
    }

    ::taihe::expected<string, ::taihe::error> getLabel()
    {
        return label_;
    }

    ::taihe::expected<void, ::taihe::error> setLabel(string_view val)
    {
        label_ = std::string(val.data(), val.size());
        return {};
    }

    ::taihe::expected<void, ::taihe::error> increment()
    {
        ++count_;
        std::cout << label_ << ": " << count_ << std::endl;
        return {};
    }

private:
    int32_t count_;
    std::string label_;
};

::taihe::expected<Config, ::taihe::error> createConfig(string_view name, int32_t version, string_view description)
{
    return Config {name, version, description};
}

::taihe::expected<Counter, ::taihe::error> createCounter(string_view label)
{
    return make_holder<CounterImpl, Counter>(label);
}
}  // namespace

TH_EXPORT_CPP_API_createConfig(createConfig);
TH_EXPORT_CPP_API_createCounter(createCounter);
// NOLINTEND
