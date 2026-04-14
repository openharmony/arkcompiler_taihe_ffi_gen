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
#include "external_obj_extend.impl.hpp"
#include "external_obj_extend.proj.hpp"
#include "taihe/runtime.hpp"

namespace {
class MyContext_innerImpl {
public:
    MyContext_innerImpl()
    {
    }

    ::taihe::expected<::taihe::string, ::taihe::error> start()
    {
        return "MyContext start";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> stop()
    {
        return "MyContext stop";
    }
};

::taihe::expected<::external_obj_extend::MyContext_inner, ::taihe::error> createMyContext_inner()
{
    return taihe::make_holder<MyContext_innerImpl, ::external_obj_extend::MyContext_inner>();
}
}  // namespace

TH_EXPORT_CPP_API_createMyContext_inner(createMyContext_inner);
// NOLINTEND
