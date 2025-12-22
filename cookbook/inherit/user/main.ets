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
import * as inherit from "inherit";

loadLibrary("inherit");

function main() {
    // 初始化银行卡
    let card = inherit.makeCreditCard(1000.0);
    // 查看当前是否可以进行国际交易
    console.log(card.intlEnabled);
    // 设置为可进行国际交易
    card.intlEnabled = true;
    // 查看当前是否可以进行国际交易
    console.log(card.intlEnabled);
    // 查看余额
    console.log(card.balance);
    // 购买一件国际商品
    console.log("Buy an international product")
    card.pay(50.0);
    // 查看余额
    console.log(card.balance);
}
