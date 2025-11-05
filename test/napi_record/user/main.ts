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

import * as lib from "record_test";

class BaseImpl implements lib.IBase {
  id: string;
  constructor(id: string) {
    this.id = id;
  }
  getId(): string {
    return this.id;
  }
  setId(id: string): void {
    this.id = id;
    return;
  }
}

function main() {
  let record: Record<string, number> = {
    "key0": 0,
    "key1": 1,
    "key2": 2,
    "key3": 3,
  };
  let ret2: number = lib.getStringIntSize(record);
  if ( ret2 !== 4) throw new Error(`Unexpected result`);
  console.log(ret2);

  let strRecord: Record<string, string> = lib.createStringString(5);
  if ( strRecord["0"] !== "abc") throw new Error(`Unexpected result`);
  console.log(strRecord)
  console.log(`Key: 0, Value: ` + strRecord["0"]);

  let enumRecord = lib.getStringColor();
  console.log(enumRecord);
  let enum_record: Record<string, lib.Color> = {
    "key0": lib.Color.BLUE,
    "key1": lib.Color.GREEN,
    "key2": lib.Color.RED,
  };
  lib.setStringColor(enum_record);

  let structRecord = lib.getStringData();
  for (const key in structRecord) {
    console.log(`${key}: ${structRecord[key].a, structRecord[key].b, structRecord[key].c}`);
  }
  let struct_record: Record<string, lib.Data> = {
    "key0": {a: "a0", b: "b0", c: 0},
    "key1": {a: "a1", b: "b1", c: 1},
    "key2": {a: "a2", b: "b2", c: 2},
    "key3": {a: "a3", b: "b3", c: 3},
    "key4": {a: "a4", b: "b4", c: 4},
    "key5": {a: "a5", b: "b5", c: 5},
  };
  lib.setStringData(struct_record)

  let ifaceRecord = lib.getStringIBase();
  for (const key in ifaceRecord) {
    console.log(`${key}: ${ifaceRecord[key].getId()}`);
  }
  let iface_record: Record<string, lib.IBase> = {
    "key0": new BaseImpl("0"),
    "key1": new BaseImpl("1"),
    "key2": new BaseImpl("2"),
  };
  lib.setStringIBase(iface_record)
}

main();
