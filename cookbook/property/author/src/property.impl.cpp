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

    int32_t getCount()
    {
        return count_;
    }

    string getLabel()
    {
        return label_;
    }

    void setLabel(string_view val)
    {
        label_ = std::string(val.data(), val.size());
    }

    void increment()
    {
        ++count_;
        std::cout << label_ << ": " << count_ << std::endl;
    }

private:
    int32_t count_;
    std::string label_;
};

Config createConfig(string_view name, int32_t version, string_view description)
{
    return {name, version, description};
}

Counter createCounter(string_view label)
{
    return make_holder<CounterImpl, Counter>(label);
}
}  // namespace

TH_EXPORT_CPP_API_createConfig(createConfig);
TH_EXPORT_CPP_API_createCounter(createCounter);
// NOLINTEND
