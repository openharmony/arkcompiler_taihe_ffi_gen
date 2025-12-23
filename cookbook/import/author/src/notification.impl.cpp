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

#include "notification.impl.hpp"
#include <iostream>
#include "notification.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace notification;

namespace {
class INotificationServiceImpl {
public:
    INotificationServiceImpl()
    {
    }

    void sendMessage(::user::weak::IUser a)
    {
        string_view user_email = a->getEmail();
        std::cout << "Welcome " << a->getEmail() << std::endl;
    }
};

INotificationService makeNotificationService()
{
    return make_holder<INotificationServiceImpl, INotificationService>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeNotificationService(makeNotificationService);
// NOLINTEND
