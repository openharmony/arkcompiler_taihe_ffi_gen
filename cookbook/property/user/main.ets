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
import * as property from "property";

loadLibrary("property");

function main() {
    // @readonly 示例：struct 的只读字段
    let config = property.createConfig("MyApp", 1, "A demo app");
    console.log(config.name);         // MyApp
    console.log(config.version);      // 1
    console.log(config.description);  // A demo app
    // config.name = "New";             // Error: readonly 属性不可修改
    config.description = "Updated";   // OK: 非 readonly 字段可修改
    console.log(config.description);  // Updated

    // @get / @set 示例：interface 的属性访问器
    let counter = property.createCounter("step");
    console.log(counter.count);  // 0
    console.log(counter.label);  // step
    counter.label = "tick";      // 通过 setter 修改
    console.log(counter.label);  // tick
    counter.increment();         // tick: 1
    counter.increment();         // tick: 2
    console.log(counter.count);  // 2
}
