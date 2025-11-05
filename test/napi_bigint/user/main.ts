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

import * as lib from "bigint_test";

function main() {
    let num1: bigint = lib.processBigInt(18446744073709556846815135465465564525825546451551616n);
    if ( num1 !== 340282366920938559954882708249570542425151457938797744320353482840211456n) throw new Error(`Unexpected result`);
    console.log(num1);
    let num2: bigint = lib.processBigInt(-65535n);
    if ( num2 !== -1208907372870555465154560n) throw new Error(`Unexpected result`);
    console.log(num2);
}

main()
