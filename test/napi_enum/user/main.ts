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

import * as lib from "enum_test";

function main() {
  let color = lib.Color.GREEN;
  let nextColor = lib.nextEnum(color);
  if (nextColor !== lib.Color.BLUE) throw new Error(`Unexpected result`);
  console.log("nextColor:", nextColor);
  if (lib.FLAG_F32_A !== 1) throw new Error(`Unexpected result`);
  if (lib.FLAG_F32_B !== 3) throw new Error(`Unexpected result`);
  console.log("const value:", lib.FLAG_F32_A, lib.FLAG_F32_B);
  let enum_v = lib.getValueOfEnum(color);
  if (enum_v !== lib.Color.GREEN) throw new Error(`Unexpected result`);
  console.log(enum_v);
  let value_e = lib.fromValueToEnum("Blue");
  if (value_e !== lib.Color.BLUE) throw new Error(`Unexpected result`);
  console.log(value_e, value_e === lib.Color.BLUE)

  let weekday = lib.Weekday.THURSDAY;
  let nextday = lib.nextEnumWeekday(weekday);
  if (nextday !== 5) throw new Error(`Unexpected result`);
  console.log("nextDay: ", nextday)
  let weekday_v = lib.getValueOfEnumWeekday(weekday);
  if (weekday_v !== 4) throw new Error(`Unexpected result`);
  console.log(weekday_v);
  let value_w = lib.fromValueToEnumWeekday(1);
  if (value_w !== 1) throw new Error(`Unexpected result`);
  console.log(value_w, value_w === lib.Weekday.MONDAY);

  if (lib.FLAG_STRING_ONE !== "hello") throw new Error(`Unexpected result`);
  console.log("const value: ", lib.FLAG_F32_A, lib.FLAG_STRING_ONE);
  console.log(lib.FLAG_F32_A === 1, lib.FLAG_STRING_ONE === "hello");
}

main();
