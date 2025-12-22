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

import {BusinessError} from "@ohos.base";
import * as notification from "notification";
import * as user from "user";

loadLibrary("import");

function main() {
    let userA = user.makeUser("12345@huawei.com");
    let userB = user.makeUser("67890@outlook.com");
    let noter = notification.makeNotificationService();
    noter.sendMessage(userA);
    noter.sendMessage(userB);
}