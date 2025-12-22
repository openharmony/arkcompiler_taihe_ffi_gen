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

import * as test from "test";

loadLibrary("ani_containers");

function recoverMap(s: Array<test.Pair>): Map<string, string> {
    let m: Map<string, string> = new Map<string, string>();
    for (let i: int = 0; i < s.length; i++) {
        m.set(s[i].key, s[i].value);
    }
    return m;
}

function testDeserializeMap() {
    let serialized: Array<test.Pair> = [
        {key: "key1", value: "value1"},
        {key: "key2", value: "value2"},
    ];
    let deserialized: Map<string, string> = test.deserializeMap(serialized);
    arktest.assertEQ(deserialized.size, 2);
    arktest.assertEQ(deserialized.get("key1"), "value1");
    arktest.assertEQ(deserialized.get("key2"), "value2");
}

function testSerializeMap() {
    let m: Map<string, string> = new Map<string, string>();
    m.set("key1", "value1");
    m.set("key2", "value2");
    let serialized: Array<test.Pair> = test.serializeMap(m);
    let recovered: Map<string, string> = recoverMap(serialized);
    arktest.assertEQ(recovered.size, 2);
    arktest.assertEQ(recovered.get("key1"), "value1");
    arktest.assertEQ(recovered.get("key2"), "value2");
}

function recoverSet(s: Array<string>): Set<string> {
    let set: Set<string> = new Set<string>();
    for (let i: int = 0; i < s.length; i++) {
        set.add(s[i]);
    }
    return set;
}

function testDeserializeSet() {
    let serialized: Array<string> = ["item1", "item2", "item3"];
    let deserialized: Set<string> = test.deserializeSet(serialized);
    arktest.assertEQ(deserialized.size, 3);
    arktest.assertEQ(deserialized.has("item1"), true);
    arktest.assertEQ(deserialized.has("item2"), true);
    arktest.assertEQ(deserialized.has("item3"), true);
}

function testSerializeSet() {
    let s: Set<string> = new Set<string>();
    s.add("item1");
    s.add("item2");
    s.add("item3");
    let serialized: Array<string> = test.serializeSet(s);
    let recovered: Set<string> = recoverSet(serialized);
    arktest.assertEQ(recovered.size, 3);
    arktest.assertEQ(recovered.has("item1"), true);
    arktest.assertEQ(recovered.has("item2"), true);
    arktest.assertEQ(recovered.has("item3"), true);
}

function recoverVector(v: Array<string>): Array<string> {
    return v;
}

function testDeserializeVector() {
    let serialized: Array<string> = ["elem1", "elem2", "elem3"];
    let deserialized: Array<string> = test.deserializeVector(serialized);
    arktest.assertEQ(deserialized.length, 3);
    arktest.assertEQ(deserialized[0], "elem1");
    arktest.assertEQ(deserialized[1], "elem2");
    arktest.assertEQ(deserialized[2], "elem3");
}

function testSerializeVector() {
    let v: Array<string> = ["elem1", "elem2", "elem3"];
    let serialized: Array<string> = test.serializeVector(v);
    let recovered: Array<string> = recoverVector(serialized);
    arktest.assertEQ(recovered.length, 3);
    arktest.assertEQ(recovered[0], "elem1");
    arktest.assertEQ(recovered[1], "elem2");
    arktest.assertEQ(recovered[2], "elem3");
}

function main() {
    let suite = new arktest.ArkTestsuite("Containers Test Suite");

    suite.addTest("Deserialize Map Test", testDeserializeMap);
    suite.addTest("Serialize Map Test", testSerializeMap);
    suite.addTest("Deserialize Set Test", testDeserializeSet);
    suite.addTest("Serialize Set Test", testSerializeSet);
    suite.addTest("Deserialize Vector Test", testDeserializeVector);
    suite.addTest("Serialize Vector Test", testSerializeVector);

    exit(suite.run());
}
