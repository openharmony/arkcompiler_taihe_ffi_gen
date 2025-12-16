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

const lib = requireNapi('./map_test.so', RequireBaseDir.SCRIPT_DIR);

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
  let map = new Map<string, number>();
  map.set("key0", 0);
  map.set("key1", 1);
  map.set("key2", 2);
  let map_size: number = lib.getStringIntSize(map);
  if ( map_size !== 3) throw new Error(`Unexpected result`);
  console.log(map_size);

  let strMap: Map<string, string> = lib.createStringString(5);
  if ( strMap.get("0") !== "abc") throw new Error(`Unexpected result`);
  console.log(strMap)
  console.log(`Key: 0, Value: ` + strMap.get("0"));

  let new_intMap = new Map<number, string>();
  new_intMap.set(0, "a");
  new_intMap.set(1, "b");
  new_intMap.set(2, "c");
  let intMap: Map<number, string> = lib.changeIntString(new_intMap);
  console.log(intMap)

  let enumMap = lib.getStringColor();
  console.log(enumMap);
  let enum_Map = new Map<string, lib.Color>();
  enum_Map.set("key0", lib.Color.BLUE);
  enum_Map.set("key1", lib.Color.GREEN);
  enum_Map.set("key2", lib.Color.RED);
  lib.setStringColor(enum_Map);

  let new_enumMap = new Map<lib.Color, string>();
  new_enumMap.set(lib.Color.BLUE, "a");
  new_enumMap.set(lib.Color.GREEN, "b");
  new_enumMap.set(lib.Color.RED, "c");
  console.log(lib.changeColorString(new_enumMap));

  let structMap: Map<string, lib.Data> = lib.getStringData();
  structMap.forEach((value, key) => {
    console.log("TS MapStringData", key, value.a, value.b, value.c);
  });
  let struct_Map = new Map<string, lib.Data>();
  struct_Map.set("key0", {a: "a0", b: "b0", c: 0});
  struct_Map.set("key1", {a: "a1", b: "b1", c: 1});
  struct_Map.set("key2", {a: "a2", b: "b2", c: 2});
  struct_Map.set("key3", {a: "a3", b: "b3", c: 3});
  struct_Map.set("key4", {a: "a4", b: "b4", c: 4});
  struct_Map.set("key5", {a: "a5", b: "b5", c: 5});
  lib.setStringData(struct_Map)

  let ifaceMap: Map<string, lib.IBase> = lib.getStringIBase();
  ifaceMap.forEach((value, key) => {
    console.log("TS MapStringIBase", key, value.getId());
  });
  let iface_Map = new Map<string, lib.IBase>();
  iface_Map.set("key0", new BaseImpl("0"))
  iface_Map.set("key1", new BaseImpl("1"))
  iface_Map.set("key2", new BaseImpl("2"))
  lib.setStringIBase(iface_Map)
}
// TODO: 直接使用 Taihe Map 不保序，但 TS Map 规定保序
main();
