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
#include "user.impl.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"
#include "user.proj.hpp"

using namespace taihe;
using namespace user;

namespace {
// To be implemented.

class IUserImpl {
public:
    IUserImpl(string_view path) : m_email(path)
    {
    }

    string getEmail()
    {
        return this->m_email;
    }

    void setEmail(string_view path)
    {
        this->m_email = path;
    }

private:
    string m_email;
};

IUser makeUser(string_view path)
{
    return make_holder<IUserImpl, IUser>(path);
}
}  // namespace

TH_EXPORT_CPP_API_makeUser(makeUser);
// NOLINTEND
