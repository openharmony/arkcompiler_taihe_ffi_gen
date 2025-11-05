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

// import * as lib_people from "people";                    // Use .d.ts
// import * as lib_building from "building";                // Use .d.ts
import * as lib_people from "../generated/proxy/people";           // Use .ts
import * as lib_building from "../generated/proxy/building";       // Use .ts

function main() {
    let g = lib_building.make_group();
    if ( g.member.age !== 20 && g.member.name !== "mary" && g.number !== 23) throw new Error(`Unexpected result`);
    console.log(g.member.age, g.member.name, g.number);
    let p = lib_people.make_student();
    if ( p.age !== 22 && p.name !== "mike") throw new Error(`Unexpected result`);
    console.log(p.age, p.name);
}

main();