/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
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

import { BusinessError } from "@ohos.base";
import * as shared from "shared_containers";

loadLibrary("ani_shared_containers");

function assertTrue(v: boolean) {
    arktest.assertEQ(v, true);
}

function assertFalse(v: boolean) {
    arktest.assertEQ(v, false);
}

function assertStringArrayEQ(actual: Array<string>, expected: Array<string>) {
    arktest.assertEQ(actual.length, expected.length);
    for (let i: int = 0; i < expected.length; i++) {
        arktest.assertEQ(actual[i], expected[i]);
    }
}

function assertIntArrayEQ(actual: Array<int>, expected: Array<int>) {
    arktest.assertEQ(actual.length, expected.length);
    for (let i: int = 0; i < expected.length; i++) {
        arktest.assertEQ(actual[i], expected[i]);
    }
}

function assertMapEntryArrayContains(
    entries: Array<[string, string]>,
    k: string,
    v: string,
): boolean {
    for (let i: int = 0; i < entries.length; i++) {
        if (entries[i][0] === k && entries[i][1] === v) {
            return true;
        }
    }
    return false;
}

function assertRecordEntryArrayContains(
    entries: Array<[int, string]>,
    k: int,
    v: string,
): boolean {
    for (let i: int = 0; i < entries.length; i++) {
        if (entries[i][0] === k && entries[i][1] === v) {
            return true;
        }
    }
    return false;
}

function assertBusinessError(expectedCode: int, call: () => void) {
    let thrown: boolean = false;
    let code: int = 0;

    try {
        call();
    } catch (error) {
        thrown = true;
        let e = error as BusinessError;
        code = e.code;
    }

    assertTrue(thrown);
    arktest.assertEQ(code, expectedCode);
}

function assertAnyError(call: () => void) {
    let thrown: boolean = false;

    try {
        call();
    } catch (error) {
        thrown = true;
    }

    assertTrue(thrown);
}

function makeVector(): Array<string> {
    return ["a", "b", "c"];
}

function makeSet(): Set<string> {
    let s: Set<string> = new Set<string>();
    s.add("a");
    s.add("b");
    s.add("c");
    return s;
}

function makeMap(): Map<string, string> {
    let m: Map<string, string> = new Map<string, string>();
    m.set("a", "1");
    m.set("b", "2");
    m.set("c", "3");
    return m;
}

function makeRecord(): Record<int, string> {
    return {
        1: "a",
        2: "b",
        3: "c",
    };
}

function makeArrayBufferU8(): ArrayBuffer {
    let buf: ArrayBuffer = new ArrayBuffer(4);
    let view: Uint8Array = new Uint8Array(buf);
    view[0] = 1;
    view[1] = 2;
    view[2] = 3;
    view[3] = 255;
    return buf;
}

function makeArrayBufferI8(): ArrayBuffer {
    let buf: ArrayBuffer = new ArrayBuffer(4);
    let view: Int8Array = new Int8Array(buf);
    view[0] = -1;
    view[1] = 0;
    view[2] = 1;
    view[3] = 127;
    return buf;
}

function makeTypedArrayU8(): Uint8Array {
    return new Uint8Array([1, 2, 3, 255]);
}

function makeTypedArrayI8(): Int8Array {
    return new Int8Array([-128, -1, 0, 127]);
}

function makeTypedArrayU32(): Uint32Array {
    return new Uint32Array([1, 2, 3]);
}

function makeTypedArrayI32(): Int32Array {
    return new Int32Array([-1, 0, 1]);
}

function makeTypedArrayF64(): Float64Array {
    return new Float64Array([1.5, -2.25, 3.75]);
}

function testVectorBasic() {
    let v: Array<string> = makeVector();
    let wrapper: shared.VectorWrapper = shared.makeVectorWrapper(v);

    arktest.assertEQ(wrapper.getSize(), 3 as long);
    assertStringArrayEQ(wrapper.getItems(), ["a", "b", "c"]);

    arktest.assertEQ(wrapper.get(0 as long), "a");
    arktest.assertEQ(wrapper.get(1 as long), "b");
    arktest.assertEQ(wrapper.get(2 as long), "c");

    wrapper.set(1 as long, "bb");
    arktest.assertEQ(v[1], "bb");
    arktest.assertEQ(wrapper.get(1 as long), "bb");

    let old: string = wrapper.getAndSet(1 as long, "bbb");
    arktest.assertEQ(old, "bb");
    arktest.assertEQ(v[1], "bbb");

    wrapper.insert(1 as long, "x");
    assertStringArrayEQ(v, ["a", "x", "bbb", "c"]);

    wrapper.insertLast("z");
    assertStringArrayEQ(v, ["a", "x", "bbb", "c", "z"]);

    let removed: string = wrapper.getAndRemove(1 as long);
    arktest.assertEQ(removed, "x");
    assertStringArrayEQ(v, ["a", "bbb", "c", "z"]);

    let last: string = wrapper.getAndRemoveLast();
    arktest.assertEQ(last, "z");
    assertStringArrayEQ(v, ["a", "bbb", "c"]);

    wrapper.remove(1 as long);
    assertStringArrayEQ(v, ["a", "c"]);

    wrapper.removeLast();
    assertStringArrayEQ(v, ["a"]);

    wrapper.clear();
    arktest.assertEQ(v.length, 0);
    arktest.assertEQ(wrapper.getSize(), 0 as long);
}

function testVectorForEach() {
    let v: Array<string> = makeVector();
    let wrapper: shared.VectorWrapper = shared.makeVectorWrapper(v);

    let indexes: Array<long> = [];
    let values: Array<string> = [];

    wrapper.forEachItem((i: long, value: string): boolean => {
        indexes.push(i);
        values.push(value);
        return true;
    });

    arktest.assertEQ(indexes.length, 3);
    arktest.assertEQ(indexes[0], 0 as long);
    arktest.assertEQ(indexes[1], 1 as long);
    arktest.assertEQ(indexes[2], 2 as long);
    assertStringArrayEQ(values, ["a", "b", "c"]);
}

function testVectorForEachEarlyStop() {
    let v: Array<string> = makeVector();
    let wrapper: shared.VectorWrapper = shared.makeVectorWrapper(v);

    let visited: Array<string> = [];

    wrapper.forEachItem((i: long, value: string): boolean => {
        visited.push(value);
        return i < 1 as long;
    });

    assertStringArrayEQ(visited, ["a", "b"]);
}

function testVectorForEachErrorPropagation() {
    let v: Array<string> = makeVector();
    let wrapper: shared.VectorWrapper = shared.makeVectorWrapper(v);

    assertBusinessError(77, () => {
        wrapper.forEachItem((i: long, value: string): boolean => {
            if (i === 1 as long) {
                throw new BusinessError(77, "visitor error");
            }
            return true;
        });
    });
}

function testVectorOutOfBounds() {
    let v: Array<string> = makeVector();
    let wrapper: shared.VectorWrapper = shared.makeVectorWrapper(v);

    assertAnyError(() => {
        wrapper.get(3 as long);
    });

    assertAnyError(() => {
        wrapper.set(3 as long, "x");
    });

    assertAnyError(() => {
        wrapper.getAndSet(3 as long, "x");
    });

    assertAnyError(() => {
        wrapper.insert(5 as long, "x");
    });

    assertAnyError(() => {
        wrapper.remove(3 as long);
    });

    assertAnyError(() => {
        wrapper.getAndRemove(3 as long);
    });

    wrapper.clear();

    assertAnyError(() => {
        wrapper.removeLast();
    });

    assertAnyError(() => {
        wrapper.getAndRemoveLast();
    });

    assertAnyError(() => {
        wrapper.get(0 as long);
    });
}

function testSetBasic() {
    let s: Set<string> = makeSet();
    let wrapper: shared.SetWrapper = shared.makeSetWrapper(s);

    arktest.assertEQ(wrapper.getSize(), 3 as long);
    assertTrue(wrapper.has("a"));
    assertTrue(wrapper.has("b"));
    assertFalse(wrapper.has("x"));

    wrapper.insert("x");
    assertTrue(s.has("x"));
    assertTrue(wrapper.has("x"));
    arktest.assertEQ(wrapper.getSize(), 4 as long);

    assertFalse(wrapper.checkedInsert("x"));
    assertTrue(wrapper.checkedInsert("y"));
    assertTrue(s.has("y"));

    wrapper.remove("a");
    assertFalse(s.has("a"));
    assertFalse(wrapper.has("a"));

    assertFalse(wrapper.checkedRemove("not-exist"));
    assertTrue(wrapper.checkedRemove("b"));
    assertFalse(s.has("b"));

    wrapper.clear();
    arktest.assertEQ(s.size, 0);
    arktest.assertEQ(wrapper.getSize(), 0 as long);
}

function testSetKeysAndForEach() {
    let s: Set<string> = makeSet();
    let wrapper: shared.SetWrapper = shared.makeSetWrapper(s);

    let keys: Array<string> = wrapper.getKeys();
    arktest.assertEQ(keys.length, 3);
    assertTrue(keys.includes("a"));
    assertTrue(keys.includes("b"));
    assertTrue(keys.includes("c"));

    let visited: Array<string> = [];
    wrapper.forEachKey((k: string): boolean => {
        visited.push(k);
        return true;
    });

    arktest.assertEQ(visited.length, 3);
    assertTrue(visited.includes("a"));
    assertTrue(visited.includes("b"));
    assertTrue(visited.includes("c"));
}

function testSetForEachEarlyStop() {
    let s: Set<string> = makeSet();
    let wrapper: shared.SetWrapper = shared.makeSetWrapper(s);

    let count: int = 0;

    wrapper.forEachKey((k: string): boolean => {
        count++;
        return false;
    });

    arktest.assertEQ(count, 1);
}

function testSetForEachErrorPropagation() {
    let s: Set<string> = makeSet();
    let wrapper: shared.SetWrapper = shared.makeSetWrapper(s);

    assertBusinessError(77, () => {
        wrapper.forEachKey((k: string): boolean => {
            throw new BusinessError(77, "set visitor error");
        });
    });
}

function testMapBasic() {
    let m: Map<string, string> = makeMap();
    let wrapper: shared.MapWrapper = shared.makeMapWrapper(m);

    arktest.assertEQ(wrapper.getSize(), 3 as long);
    assertTrue(wrapper.has("a"));
    assertFalse(wrapper.has("x"));

    arktest.assertEQ(wrapper.tryGet("a"), "1");
    arktest.assertEQ(wrapper.tryGet("x"), undefined);

    wrapper.upsert("a", "11");
    arktest.assertEQ(m.get("a"), "11");
    arktest.assertEQ(wrapper.tryGet("a"), "11");

    wrapper.upsert("x", "99");
    arktest.assertEQ(m.get("x"), "99");
    assertTrue(wrapper.has("x"));

    assertFalse(wrapper.checkedInsert("x", "100"));
    arktest.assertEQ(m.get("x"), "99");

    assertTrue(wrapper.checkedInsert("y", "100"));
    arktest.assertEQ(m.get("y"), "100");

    let old1: string | undefined = wrapper.tryGetAndUpsert("a", "111");
    arktest.assertEQ(old1, "11");
    arktest.assertEQ(m.get("a"), "111");

    let old2: string | undefined = wrapper.tryGetAndUpsert("new", "n");
    arktest.assertEQ(old2, undefined);
    arktest.assertEQ(m.get("new"), "n");

    let old3: string | undefined = wrapper.tryGetAndInsert("a", "should-not-insert");
    arktest.assertEQ(old3, "111");
    arktest.assertEQ(m.get("a"), "111");

    let old4: string | undefined = wrapper.tryGetAndInsert("inserted", "iv");
    arktest.assertEQ(old4, undefined);
    arktest.assertEQ(m.get("inserted"), "iv");

    wrapper.remove("x");
    assertFalse(m.has("x"));

    assertFalse(wrapper.checkedRemove("not-exist"));
    assertTrue(wrapper.checkedRemove("y"));
    assertFalse(m.has("y"));

    let removed: string | undefined = wrapper.tryGetAndRemove("a");
    arktest.assertEQ(removed, "111");
    assertFalse(m.has("a"));

    let removed2: string | undefined = wrapper.tryGetAndRemove("a");
    arktest.assertEQ(removed2, undefined);

    wrapper.clear();
    arktest.assertEQ(m.size, 0);
    arktest.assertEQ(wrapper.getSize(), 0 as long);
}

function testMapKeysValuesEntriesAndForEach() {
    let m: Map<string, string> = makeMap();
    let wrapper: shared.MapWrapper = shared.makeMapWrapper(m);

    let keys: Array<string> = wrapper.getKeys();
    arktest.assertEQ(keys.length, 3);
    assertTrue(keys.includes("a"));
    assertTrue(keys.includes("b"));
    assertTrue(keys.includes("c"));

    let values: Array<string> = wrapper.getValues();
    arktest.assertEQ(values.length, 3);
    assertTrue(values.includes("1"));
    assertTrue(values.includes("2"));
    assertTrue(values.includes("3"));

    let entries: Array<[string, string]> = wrapper.getEntries();
    arktest.assertEQ(entries.length, 3);
    assertTrue(assertMapEntryArrayContains(entries, "a", "1"));
    assertTrue(assertMapEntryArrayContains(entries, "b", "2"));
    assertTrue(assertMapEntryArrayContains(entries, "c", "3"));

    let visitedKeys: Array<string> = [];
    wrapper.forEachKey((k: string): boolean => {
        visitedKeys.push(k);
        return true;
    });
    arktest.assertEQ(visitedKeys.length, 3);

    let visitedValues: Array<string> = [];
    wrapper.forEachValue((v: string): boolean => {
        visitedValues.push(v);
        return true;
    });
    arktest.assertEQ(visitedValues.length, 3);

    let visitedEntries: Array<[string, string]> = [];
    wrapper.forEachEntry((k: string, v: string): boolean => {
        visitedEntries.push([k, v]);
        return true;
    });
    arktest.assertEQ(visitedEntries.length, 3);
    assertTrue(assertMapEntryArrayContains(visitedEntries, "a", "1"));
    assertTrue(assertMapEntryArrayContains(visitedEntries, "b", "2"));
    assertTrue(assertMapEntryArrayContains(visitedEntries, "c", "3"));
}

function testMapForEachEarlyStop() {
    let m: Map<string, string> = makeMap();
    let wrapper: shared.MapWrapper = shared.makeMapWrapper(m);

    let keyCount: int = 0;
    wrapper.forEachKey((k: string): boolean => {
        keyCount++;
        return false;
    });
    arktest.assertEQ(keyCount, 1);

    let valueCount: int = 0;
    wrapper.forEachValue((v: string): boolean => {
        valueCount++;
        return false;
    });
    arktest.assertEQ(valueCount, 1);

    let entryCount: int = 0;
    wrapper.forEachEntry((k: string, v: string): boolean => {
        entryCount++;
        return false;
    });
    arktest.assertEQ(entryCount, 1);
}

function testMapForEachErrorPropagation() {
    let m: Map<string, string> = makeMap();
    let wrapper: shared.MapWrapper = shared.makeMapWrapper(m);

    assertBusinessError(77, () => {
        wrapper.forEachKey((k: string): boolean => {
            throw new BusinessError(77, "map key visitor error");
        });
    });

    assertBusinessError(77, () => {
        wrapper.forEachValue((v: string): boolean => {
            throw new BusinessError(77, "map value visitor error");
        });
    });

    assertBusinessError(77, () => {
        wrapper.forEachEntry((k: string, v: string): boolean => {
            throw new BusinessError(77, "map entry visitor error");
        });
    });
}

function testRecordBasic() {
    let r: Record<int, string> = makeRecord();
    let wrapper: shared.RecordWrapper = shared.makeRecordWrapper(r);

    arktest.assertEQ(wrapper.getSize(), 3 as long);
    assertTrue(wrapper.has(1));
    assertFalse(wrapper.has(99));

    arktest.assertEQ(wrapper.tryGet(1), "a");
    arktest.assertEQ(wrapper.tryGet(99), undefined);

    wrapper.upsert(1, "aa");
    arktest.assertEQ(r[1], "aa");

    wrapper.upsert(99, "zz");
    arktest.assertEQ(r[99], "zz");
    assertTrue(wrapper.has(99));

    assertFalse(wrapper.checkedInsert(99, "new"));
    arktest.assertEQ(r[99], "zz");

    assertTrue(wrapper.checkedInsert(100, "hundred"));
    arktest.assertEQ(r[100], "hundred");

    let old1: string | undefined = wrapper.tryGetAndUpsert(1, "aaa");
    arktest.assertEQ(old1, "aa");
    arktest.assertEQ(r[1], "aaa");

    let old2: string | undefined = wrapper.tryGetAndUpsert(10, "ten");
    arktest.assertEQ(old2, undefined);
    arktest.assertEQ(r[10], "ten");

    let old3: string | undefined = wrapper.tryGetAndInsert(1, "should-not-insert");
    arktest.assertEQ(old3, "aaa");
    arktest.assertEQ(r[1], "aaa");

    let old4: string | undefined = wrapper.tryGetAndInsert(11, "eleven");
    arktest.assertEQ(old4, undefined);
    arktest.assertEQ(r[11], "eleven");

    wrapper.remove(99);
    assertFalse(wrapper.has(99));

    assertFalse(wrapper.checkedRemove(404));
    assertTrue(wrapper.checkedRemove(100));
    assertFalse(wrapper.has(100));

    let removed: string | undefined = wrapper.tryGetAndRemove(1);
    arktest.assertEQ(removed, "aaa");
    assertFalse(wrapper.has(1));

    let removed2: string | undefined = wrapper.tryGetAndRemove(1);
    arktest.assertEQ(removed2, undefined);

    wrapper.clear();
    arktest.assertEQ(wrapper.getSize(), 0 as long);
}

function testRecordKeysValuesEntriesAndForEach() {
    let r: Record<int, string> = makeRecord();
    let wrapper: shared.RecordWrapper = shared.makeRecordWrapper(r);

    let keys: Array<int> = wrapper.getKeys();
    arktest.assertEQ(keys.length, 3);
    assertTrue(keys.includes(1));
    assertTrue(keys.includes(2));
    assertTrue(keys.includes(3));

    let values: Array<string> = wrapper.getValues();
    arktest.assertEQ(values.length, 3);
    assertTrue(values.includes("a"));
    assertTrue(values.includes("b"));
    assertTrue(values.includes("c"));

    let entries: Array<[int, string]> = wrapper.getEntries();
    arktest.assertEQ(entries.length, 3);
    assertTrue(assertRecordEntryArrayContains(entries, 1, "a"));
    assertTrue(assertRecordEntryArrayContains(entries, 2, "b"));
    assertTrue(assertRecordEntryArrayContains(entries, 3, "c"));

    let visitedKeys: Array<int> = [];
    wrapper.forEachKey((k: int): boolean => {
        visitedKeys.push(k);
        return true;
    });
    arktest.assertEQ(visitedKeys.length, 3);

    let visitedValues: Array<string> = [];
    wrapper.forEachValue((v: string): boolean => {
        visitedValues.push(v);
        return true;
    });
    arktest.assertEQ(visitedValues.length, 3);

    let visitedEntries: Array<[int, string]> = [];
    wrapper.forEachEntry((k: int, v: string): boolean => {
        visitedEntries.push([k, v]);
        return true;
    });
    arktest.assertEQ(visitedEntries.length, 3);
}

function testRecordForEachEarlyStop() {
    let r: Record<int, string> = makeRecord();
    let wrapper: shared.RecordWrapper = shared.makeRecordWrapper(r);

    let keyCount: int = 0;
    wrapper.forEachKey((k: int): boolean => {
        keyCount++;
        return false;
    });
    arktest.assertEQ(keyCount, 1);

    let valueCount: int = 0;
    wrapper.forEachValue((v: string): boolean => {
        valueCount++;
        return false;
    });
    arktest.assertEQ(valueCount, 1);

    let entryCount: int = 0;
    wrapper.forEachEntry((k: int, v: string): boolean => {
        entryCount++;
        return false;
    });
    arktest.assertEQ(entryCount, 1);
}

function testRecordForEachErrorPropagation() {
    let r: Record<int, string> = makeRecord();
    let wrapper: shared.RecordWrapper = shared.makeRecordWrapper(r);

    assertBusinessError(77, () => {
        wrapper.forEachKey((k: int): boolean => {
            throw new BusinessError(77, "record key visitor error");
        });
    });

    assertBusinessError(77, () => {
        wrapper.forEachValue((v: string): boolean => {
            throw new BusinessError(77, "record value visitor error");
        });
    });

    assertBusinessError(77, () => {
        wrapper.forEachEntry((k: int, v: string): boolean => {
            throw new BusinessError(77, "record entry visitor error");
        });
    });
}

function testArrayBufferU8() {
    let buf: ArrayBuffer = makeArrayBufferU8();
    let view: Uint8Array = new Uint8Array(buf);
    let wrapper: shared.ArrayU8Wrapper = shared.makeArrayBufferU8Wrapper(buf);

    arktest.assertEQ(wrapper.size(), 4 as long);
    arktest.assertEQ(wrapper.get(0 as long), 1);
    arktest.assertEQ(wrapper.get(3 as long), 255);

    wrapper.set(0 as long, 42);
    wrapper.set(3 as long, 7);

    arktest.assertEQ(view[0], 42);
    arktest.assertEQ(view[3], 7);
    arktest.assertEQ(wrapper.get(0 as long), 42);
    arktest.assertEQ(wrapper.get(3 as long), 7);
}

function testArrayBufferI8() {
    let buf: ArrayBuffer = makeArrayBufferI8();
    let view: Int8Array = new Int8Array(buf);
    let wrapper: shared.ArrayI8Wrapper = shared.makeArrayBufferI8Wrapper(buf);

    arktest.assertEQ(wrapper.size(), 4 as long);
    arktest.assertEQ(wrapper.get(0 as long), -1);
    arktest.assertEQ(wrapper.get(3 as long), 127);

    wrapper.set(0 as long, -128);
    wrapper.set(1 as long, 64);

    arktest.assertEQ(view[0], -128);
    arktest.assertEQ(view[1], 64);
}

function testTypedArrayU8() {
    let arr: Uint8Array = makeTypedArrayU8();
    let wrapper: shared.ArrayU8Wrapper = shared.makeUint8ArrayWrapper(arr);

    arktest.assertEQ(wrapper.size(), 4 as long);
    arktest.assertEQ(wrapper.get(0 as long), 1);
    arktest.assertEQ(wrapper.get(3 as long), 255);

    wrapper.set(1 as long, 88);
    arktest.assertEQ(arr[1], 88);
}

function testTypedArrayI8() {
    let arr: Int8Array = makeTypedArrayI8();
    let wrapper: shared.ArrayI8Wrapper = shared.makeInt8ArrayWrapper(arr);

    arktest.assertEQ(wrapper.size(), 4 as long);
    arktest.assertEQ(wrapper.get(0 as long), -128);
    arktest.assertEQ(wrapper.get(3 as long), 127);

    wrapper.set(2 as long, -7);
    arktest.assertEQ(arr[2], -7);
}

function testTypedArrayU32() {
    let arr: Uint32Array = makeTypedArrayU32();
    let wrapper: shared.ArrayU32Wrapper = shared.makeUint32ArrayWrapper(arr);

    arktest.assertEQ(wrapper.size(), 3 as long);
    arktest.assertEQ(wrapper.get(0 as long), 1 as long);
    arktest.assertEQ(wrapper.get(2 as long), 3 as long);

    wrapper.set(1 as long, 99 as long);
    arktest.assertEQ(arr[1], 99 as long);
    arktest.assertEQ(wrapper.get(1 as long), 99 as long);
}

function testTypedArrayI32() {
    let arr: Int32Array = makeTypedArrayI32();
    let wrapper: shared.ArrayI32Wrapper = shared.makeInt32ArrayWrapper(arr);

    arktest.assertEQ(wrapper.size(), 3 as long);
    arktest.assertEQ(wrapper.get(0 as long), -1);
    arktest.assertEQ(wrapper.get(2 as long), 1);

    wrapper.set(1 as long, -99);
    arktest.assertEQ(arr[1], -99);
    arktest.assertEQ(wrapper.get(1 as long), -99);
}

function testTypedArrayF64() {
    let arr: Float64Array = makeTypedArrayF64();
    let wrapper: shared.ArrayF64Wrapper = shared.makeFloat64ArrayWrapper(arr);

    arktest.assertEQ(wrapper.size(), 3 as long);
    arktest.assertEQ(wrapper.get(0 as long), 1.5);
    arktest.assertEQ(wrapper.get(1 as long), -2.25);

    wrapper.set(2 as long, 6.5);
    arktest.assertEQ(arr[2], 6.5);
    arktest.assertEQ(wrapper.get(2 as long), 6.5);
}

function testSharedArrayOutOfBounds() {
    let buf: ArrayBuffer = makeArrayBufferU8();
    let wrapper: shared.ArrayU8Wrapper = shared.makeArrayBufferU8Wrapper(buf);

    assertAnyError(() => {
        wrapper.get(4 as long);
    });

    assertAnyError(() => {
        wrapper.set(4 as long, 1);
    });

    let arr: Int32Array = makeTypedArrayI32();
    let i32Wrapper: shared.ArrayI32Wrapper = shared.makeInt32ArrayWrapper(arr);

    assertAnyError(() => {
        i32Wrapper.get(3 as long);
    });

    assertAnyError(() => {
        i32Wrapper.set(3 as long, 1);
    });
}

function testSerializeUnionVector() {
    let serializer: shared.ContainerSerializer = shared.getSerializer();

    let v: Array<string> = ["a", "b", "c"];
    let result: string = serializer.serialize(v);
    arktest.assertEQ(result, "a,b,c,");
}

function testSerializeUnionSet() {
    let serializer: shared.ContainerSerializer = shared.getSerializer();

    let s: Set<string> = new Set<string>();
    s.add("a");
    s.add("b");

    let result: string = serializer.serialize(s);

    assertTrue(result.includes("a,"));
    assertTrue(result.includes("b,"));
}

function testSerializeUnionMap() {
    let serializer: shared.ContainerSerializer = shared.getSerializer();

    let m: Map<string, string> = new Map<string, string>();
    m.set("a", "1");
    m.set("b", "2");

    let result: string = serializer.serialize(m);

    assertTrue(result.includes("a:1,"));
    assertTrue(result.includes("b:2,"));
}

function testSerializeUnionRecord() {
    let serializer: shared.ContainerSerializer = shared.getSerializer();

    let r: Record<int, string> = {
        1: "a",
        2: "b",
    };

    let result: string = serializer.serialize(r);

    assertTrue(result.includes("1:a,"));
    assertTrue(result.includes("2:b,"));
}

function testSerializeUnionArrayBuffer() {
    let serializer: shared.ContainerSerializer = shared.getSerializer();

    let buf: ArrayBuffer = new ArrayBuffer(3);
    let view: Uint8Array = new Uint8Array(buf);
    view[0] = 1;
    view[1] = 2;
    view[2] = 255;

    let result: string = serializer.serialize(buf);
    arktest.assertEQ(result, "1,2,255,");
}

function testSerializeUnionTypedArray() {
    let serializer: shared.ContainerSerializer = shared.getSerializer();

    let arr: BigInt64Array = new BigInt64Array([-1n, 0n, 99n]);

    let result: string = serializer.serialize(arr);
    arktest.assertEQ(result, "-1,0,99,");
}

class VectorGenerator implements shared.ContainerGenerator {
    private index: int = 0;

    generate(): shared.ContainerUnion {
        this.index++;

        if (this.index === 1) {
            return ["a", "b"];
        }

        if (this.index === 2) {
            let m: Map<string, string> = new Map<string, string>();
            m.set("x", "1");
            return m;
        }

        let buf: ArrayBuffer = new ArrayBuffer(2);
        let view: Uint8Array = new Uint8Array(buf);
        view[0] = 7;
        view[1] = 8;
        return buf;
    }
}

function testGeneratorReturnUnion() {
    let generator: shared.ContainerGenerator = new VectorGenerator();

    let result: Array<string> = shared.testGenerator(generator, 3 as long);

    arktest.assertEQ(result.length, 3);
    arktest.assertEQ(result[0], "a,b,");
    arktest.assertEQ(result[1], "x:1,");
    arktest.assertEQ(result[2], "7,8,");
}

class ErrorGenerator implements shared.ContainerGenerator {
    generate(): shared.ContainerUnion {
        throw new BusinessError(77, "generator error");
    }
}

function testGeneratorErrorPropagation() {
    let generator: shared.ContainerGenerator = new ErrorGenerator();

    assertBusinessError(77, () => {
        shared.testGenerator(generator, 1 as long);
    });
}

function testClearAllInStruct() {
    let arrayBuffer: ArrayBuffer = makeArrayBufferU8();
    let typedArray: BigInt64Array = new BigInt64Array([1n, 2n, 3n]);

    let containers: shared.ContainerStruct = {
        recordValue: makeRecord(),
        mapValue: makeMap(),
        setValue: makeSet(),
        vectorValue: makeVector(),
        arraybufferValue: arrayBuffer,
        typedarrayValue: typedArray,
    };

    shared.clearAllInStruct(containers);

    arktest.assertEQ(containers.vectorValue.length, 0);
    arktest.assertEQ(containers.setValue.size, 0);
    arktest.assertEQ(containers.mapValue.size, 0);

    let recordWrapper: shared.RecordWrapper = shared.makeRecordWrapper(containers.recordValue);
    arktest.assertEQ(recordWrapper.getSize(), 0 as long);

    let abView: Uint8Array = new Uint8Array(arrayBuffer);
    for (let i: int = 0; i < abView.length; i++) {
        arktest.assertEQ(abView[i], 0);
    }

    for (let i: int = 0; i < typedArray.length; i++) {
        arktest.assertEQ(typedArray[i], 0n);
    }
}

function testClearAnyInUnionVector() {
    let v: Array<string> = makeVector();
    shared.clearAnyInUnion(v);
    arktest.assertEQ(v.length, 0);
}

function testClearAnyInUnionSet() {
    let s: Set<string> = makeSet();
    shared.clearAnyInUnion(s);
    arktest.assertEQ(s.size, 0);
}

function testClearAnyInUnionMap() {
    let m: Map<string, string> = makeMap();
    shared.clearAnyInUnion(m);
    arktest.assertEQ(m.size, 0);
}

function testClearAnyInUnionRecord() {
    let r: Record<int, string> = makeRecord();
    shared.clearAnyInUnion(r);

    let wrapper: shared.RecordWrapper = shared.makeRecordWrapper(r);
    arktest.assertEQ(wrapper.getSize(), 0 as long);
}

function testClearAnyInUnionArrayBuffer() {
    let buf: ArrayBuffer = makeArrayBufferU8();
    shared.clearAnyInUnion(buf);

    let view: Uint8Array = new Uint8Array(buf);
    for (let i: int = 0; i < view.length; i++) {
        arktest.assertEQ(view[i], 0);
    }
}

function testClearAnyInUnionTypedArray() {
    let arr: BigInt64Array = new BigInt64Array([1n, -2n, 3n]);
    shared.clearAnyInUnion(arr);

    for (let i: int = 0; i < arr.length; i++) {
        arktest.assertEQ(arr[i], 0n);
    }
}

function testClearAllInArray() {
    let v: Array<string> = makeVector();
    let s: Set<string> = makeSet();
    let m: Map<string, string> = makeMap();
    let r: Record<int, string> = makeRecord();

    let buf: ArrayBuffer = makeArrayBufferU8();
    let typed: BigInt64Array = new BigInt64Array([1n, 2n]);

    let containers: Array<shared.ContainerUnion> = [
        v,
        s,
        m,
        r,
        buf,
        typed,
    ];

    shared.clearAllInArray(containers);

    arktest.assertEQ(v.length, 0);
    arktest.assertEQ(s.size, 0);
    arktest.assertEQ(m.size, 0);

    let recordWrapper: shared.RecordWrapper = shared.makeRecordWrapper(r);
    arktest.assertEQ(recordWrapper.getSize(), 0 as long);

    let view: Uint8Array = new Uint8Array(buf);
    for (let i: int = 0; i < view.length; i++) {
        arktest.assertEQ(view[i], 0);
    }

    for (let i: int = 0; i < typed.length; i++) {
        arktest.assertEQ(typed[i], 0n);
    }
}

function testClearAllInSharedVector() {
    let v: Array<string> = makeVector();
    let s: Set<string> = makeSet();
    let m: Map<string, string> = makeMap();
    let r: Record<int, string> = makeRecord();

    let buf: ArrayBuffer = makeArrayBufferU8();
    let typed: BigInt64Array = new BigInt64Array([1n, 2n, 3n]);

    let containers: Array<shared.ContainerUnion> = [
        v,
        s,
        m,
        r,
        buf,
        typed,
    ];

    shared.clearAllInSharedVector(containers);

    arktest.assertEQ(v.length, 0);
    arktest.assertEQ(s.size, 0);
    arktest.assertEQ(m.size, 0);

    let recordWrapper: shared.RecordWrapper = shared.makeRecordWrapper(r);
    arktest.assertEQ(recordWrapper.getSize(), 0 as long);

    let view: Uint8Array = new Uint8Array(buf);
    for (let i: int = 0; i < view.length; i++) {
        arktest.assertEQ(view[i], 0);
    }

    for (let i: int = 0; i < typed.length; i++) {
        arktest.assertEQ(typed[i], 0n);
    }
}

function testEmptyContainers() {
    let v: Array<string> = [];
    let vectorWrapper: shared.VectorWrapper = shared.makeVectorWrapper(v);
    arktest.assertEQ(vectorWrapper.getSize(), 0 as long);
    assertStringArrayEQ(vectorWrapper.getItems(), []);

    let vectorCount: int = 0;
    vectorWrapper.forEachItem((i: long, value: string): boolean => {
        vectorCount++;
        return true;
    });
    arktest.assertEQ(vectorCount, 0);

    let s: Set<string> = new Set<string>();
    let setWrapper: shared.SetWrapper = shared.makeSetWrapper(s);
    arktest.assertEQ(setWrapper.getSize(), 0 as long);
    arktest.assertEQ(setWrapper.getKeys().length, 0);

    let setCount: int = 0;
    setWrapper.forEachKey((k: string): boolean => {
        setCount++;
        return true;
    });
    arktest.assertEQ(setCount, 0);

    let m: Map<string, string> = new Map<string, string>();
    let mapWrapper: shared.MapWrapper = shared.makeMapWrapper(m);
    arktest.assertEQ(mapWrapper.getSize(), 0 as long);
    arktest.assertEQ(mapWrapper.getKeys().length, 0);
    arktest.assertEQ(mapWrapper.getValues().length, 0);
    arktest.assertEQ(mapWrapper.getEntries().length, 0);

    let r: Record<int, string> = {};
    let recordWrapper: shared.RecordWrapper = shared.makeRecordWrapper(r);
    arktest.assertEQ(recordWrapper.getSize(), 0 as long);
    arktest.assertEQ(recordWrapper.getKeys().length, 0);
    arktest.assertEQ(recordWrapper.getValues().length, 0);
    arktest.assertEQ(recordWrapper.getEntries().length, 0);

    let buf: ArrayBuffer = new ArrayBuffer(0);
    let arrayWrapper: shared.ArrayU8Wrapper = shared.makeArrayBufferU8Wrapper(buf);
    arktest.assertEQ(arrayWrapper.size(), 0 as long);

    assertAnyError(() => {
        arrayWrapper.get(0 as long);
    });
}

function main() {
    let suite = new arktest.ArkTestsuite("Shared containers projection tests");

    suite.addTest("vector basic", testVectorBasic);
    suite.addTest("vector forEach", testVectorForEach);
    suite.addTest("vector forEach early stop", testVectorForEachEarlyStop);
    suite.addTest("vector forEach error propagation", testVectorForEachErrorPropagation);
    suite.addTest("vector out of bounds", testVectorOutOfBounds);

    suite.addTest("set basic", testSetBasic);
    suite.addTest("set keys and forEach", testSetKeysAndForEach);
    suite.addTest("set forEach early stop", testSetForEachEarlyStop);
    suite.addTest("set forEach error propagation", testSetForEachErrorPropagation);

    suite.addTest("map basic", testMapBasic);
    suite.addTest("map keys values entries and forEach", testMapKeysValuesEntriesAndForEach);
    suite.addTest("map forEach early stop", testMapForEachEarlyStop);
    suite.addTest("map forEach error propagation", testMapForEachErrorPropagation);

    suite.addTest("record basic", testRecordBasic);
    suite.addTest("record keys values entries and forEach", testRecordKeysValuesEntriesAndForEach);
    suite.addTest("record forEach early stop", testRecordForEachEarlyStop);
    suite.addTest("record forEach error propagation", testRecordForEachErrorPropagation);

    suite.addTest("arraybuffer u8", testArrayBufferU8);
    suite.addTest("arraybuffer i8", testArrayBufferI8);
    suite.addTest("typedarray u8", testTypedArrayU8);
    suite.addTest("typedarray i8", testTypedArrayI8);
    suite.addTest("typedarray u32", testTypedArrayU32);
    suite.addTest("typedarray i32", testTypedArrayI32);
    suite.addTest("typedarray f64", testTypedArrayF64);
    suite.addTest("shared array out of bounds", testSharedArrayOutOfBounds);

    suite.addTest("serialize union vector", testSerializeUnionVector);
    suite.addTest("serialize union set", testSerializeUnionSet);
    suite.addTest("serialize union map", testSerializeUnionMap);
    suite.addTest("serialize union record", testSerializeUnionRecord);
    suite.addTest("serialize union arraybuffer", testSerializeUnionArrayBuffer);
    suite.addTest("serialize union typedarray", testSerializeUnionTypedArray);

    suite.addTest("generator return union", testGeneratorReturnUnion);
    suite.addTest("generator error propagation", testGeneratorErrorPropagation);

    suite.addTest("clear all in struct", testClearAllInStruct);
    suite.addTest("clear any in union vector", testClearAnyInUnionVector);
    suite.addTest("clear any in union set", testClearAnyInUnionSet);
    suite.addTest("clear any in union map", testClearAnyInUnionMap);
    suite.addTest("clear any in union record", testClearAnyInUnionRecord);
    suite.addTest("clear any in union arraybuffer", testClearAnyInUnionArrayBuffer);
    suite.addTest("clear any in union typedarray", testClearAnyInUnionTypedArray);
    suite.addTest("clear all in array", testClearAllInArray);
    suite.addTest("clear all in shared vector", testClearAllInSharedVector);

    suite.addTest("empty containers", testEmptyContainers);

    exit(suite.run());
}
