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

#include "test.impl.hpp"

#include <optional>

namespace {
// You can add using namespace statements here if needed.

class MyObjectContainerImpl {
    taihe::optional<test::MyObject> obj_;

public:
    // You can add member variables and constructor here.
    void Save(::test::weak::MyObject obj)
    {
        this->obj_.emplace(obj);
    }

    ::taihe::optional<::test::MyObject> Take()
    {
        return std::exchange(this->obj_, std::nullopt);
    }
};

class MyCallbackContainerImpl {
    taihe::optional<taihe::callback<void(::taihe::string_view s)>> callback_;

public:
    // You can add member variables and constructor here.
    void Save(::taihe::callback_view<void(::taihe::string_view s)> callback)
    {
        this->callback_.emplace(callback);
    }

    ::taihe::optional<::taihe::callback<void(::taihe::string_view s)>> Take()
    {
        return std::exchange(this->callback_, std::nullopt);
    }
};

::test::MyObjectContainer CreateObjectContainer()
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<MyObjectContainerImpl, ::test::MyObjectContainer>();
}

::test::MyCallbackContainer CreateCallbackContainer()
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<MyCallbackContainerImpl, ::test::MyCallbackContainer>();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_CreateObjectContainer(CreateObjectContainer);
TH_EXPORT_CPP_API_CreateCallbackContainer(CreateCallbackContainer);
// NOLINTEND
