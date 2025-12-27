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
import * as extobj from "external_obj";
import {Person} from "other.subsystem";

loadLibrary("external_obj");

function main() {
    console.log(extobj.is_string("hello"));
    console.log(extobj.is_string(123));

    let person: Person = {name: "John", age: 30};

    extobj.processPerson(person);

    console.log(extobj.get_objects());
}