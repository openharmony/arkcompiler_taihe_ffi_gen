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

const lib = requireNapi('./record_test.so', RequireBaseDir.SCRIPT_DIR);

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

  let strRecord: Record<string, string> = lib.createStringString(3);
  if ( strRecord["0"] !== "abc" || strRecord["1"] !== "abc" || strRecord["2"] !== "abc") throw new Error(`Unexpected result`);
  console.log(strRecord)
  console.log(`Key: 0, Value: ` + strRecord["0"]);

  let recrec: Record<string, Record<string, number>> = {
    "a": record,
    "b": record,
    "c": record,
  };
  let resrecrec = lib.changeRecRec(recrec);
  if ( resrecrec["a"]?.["key0"] !== 0 || resrecrec["a"]?.["key1"] !== 2 || resrecrec["a"]?.["key2"] !== 4 || resrecrec["a"]?.["key3"] !== 6 ) throw new Error(`Unexpected result`);
  if ( resrecrec["b"]?.["key0"] !== 0 || resrecrec["b"]?.["key1"] !== 2 || resrecrec["b"]?.["key2"] !== 4 || resrecrec["b"]?.["key3"] !== 6 ) throw new Error(`Unexpected result`);
  if ( resrecrec["c"]?.["key0"] !== 0 || resrecrec["c"]?.["key1"] !== 2 || resrecrec["c"]?.["key2"] !== 4 || resrecrec["c"]?.["key3"] !== 6 ) throw new Error(`Unexpected result`);

  let enumRecord = lib.getStringColor();
  if ( enumRecord["key1"] !== lib.Color.RED || enumRecord["key2"] !== lib.Color.GREEN ) throw new Error(`Unexpected result`);
  console.log(enumRecord);
  let enum_record: Record<string, lib.Color> = {
    "key0": lib.Color.BLUE,
    "key1": lib.Color.GREEN,
    "key2": lib.Color.RED,
  };
  lib.setStringColor(enum_record);

  let structRecord = lib.getStringData();
  if ( structRecord["key1"].a !== "a1" || structRecord["key1"].b !== "b1" || structRecord["key1"].c !== 1 ) throw new Error(`Unexpected result`);
  if ( structRecord["key2"].a !== "a2" || structRecord["key2"].b !== "b2" || structRecord["key2"].c !== 2 ) throw new Error(`Unexpected result`);
  for (const key in structRecord) {
      console.log(`${key}: ${structRecord[key].a}, ${structRecord[key].b}, ${structRecord[key].c}`);
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
  if ( ifaceRecord["key1"].getId() !== "basea" || ifaceRecord["key2"].getId() !== "baseb" ) throw new Error(`Unexpected result`);
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
