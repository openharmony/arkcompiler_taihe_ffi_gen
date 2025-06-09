import {BusinessError} from "@ohos.base";
import * as async_test from "async_test";

loadLibrary("ani_async");

function testSyncAdd() {
    {
        let res: int|undefined;
        let err: BusinessError|undefined;
        try {
            res = async_test.addSync(1, 2);
        } catch (e) {
            err = e as BusinessError;
        }
        assertEQ(res, 3, "addSync should correctly add 1 + 2");
    }
    {
        let res: int|undefined;
        let err: BusinessError|undefined;
        try {
            res = async_test.addSync(0, 2);
        } catch (e) {
            err = e as BusinessError;
        }
        assertEQ(err?.code, 1, "addSync should throw an error");
        assertEQ(
            err?.message, "some error happen in add impl",
            "addSync should throw an error when first parameter is 0");
    }
    console.log("testSyncAdd end");
}

function testAsyncAdd() {
    {
        let promise = new Promise<int>((resolve, reject) => {
            async_test.add(10, 20, (err: BusinessError|null, data?: int) => {
                if (err !== null) {
                    reject(err);
                } else {
                    resolve(data!);
                }
            });
        });
        let res: int|undefined;
        let err: BusinessError|undefined;
        try {
            res = await promise;
        } catch (e) {
            err = e as BusinessError;
        }
        assertEQ(res, 30, "add callback should receive 10 + 20 = 30");
    }
    {
        let promise = new Promise<int>((resolve, reject) => {
            async_test.add(0, 2, (err: BusinessError|null, data?: int) => {
                if (err !== null) {
                    reject(err);
                } else {
                    resolve(data!);
                }
            });
        });
        let res: int|undefined;
        let err: BusinessError|undefined;
        try {
            res = await promise;
        } catch (e) {
            err = e as BusinessError;
        }
        assertEQ(err?.code, 1, "add callback should receive an err");
        assertEQ(
            err?.message, "some error happen in add impl",
            "add callback should receive an err when first parameter is 0");
    }
    console.log("testAsyncAdd end");
}

function testPromiseAdd() {
    {
        let res: int|undefined;
        let err: BusinessError|undefined;
        try {
            res = await async_test.add(1, 2);
        } catch (e) {
            err = e as BusinessError;
        }
        assertEQ(res, 3, "add promise should correctly add 1 + 2");
    }
    {
        let res: int|undefined;
        let err: BusinessError|undefined;
        try {
            res = await async_test.add(0, 2);
        } catch (e) {
            err = e as BusinessError;
        }
        assertEQ(err?.code, 1, "add promise should throw an error");
        assertEQ(
            err?.message, "some error happen in add impl",
            "add promise should throw an error when first parameter is 0");
    }
    console.log("testPromiseAdd end");
}

function testIBase() {
    const ibase = async_test.getIBase();
    assertEQ(ibase.get(), "My IBase", "IBase.get() should return 'My IBase'");

    await ibase.setPromise("interface async set");
    assertEQ(
        await ibase.getPromise(), "interface async set",
        "getPromise should resolve with the value set in setAsync");
}

function testStaticAsyncMethods() {
    await async_test.IBase.printPromise();
}

function testStructMethods() {
    await async_test.fromStruct(
        {a: "abc", b: "efg", c: 3});  // should not throw an error

    {
        let err: BusinessError|undefined;
        try {
            await async_test.fromStruct({a: "abc", b: "efg", c: 0});
        } catch (e) {
            err = e as BusinessError;
        }
        assertEQ(err?.code, 1, "fromStruct should throw an error");
        assertEQ(
            err?.message, "some error happen in fromStructSync_impl",
            "fromStruct should throw an error when c is 0");
    }

    let data: async_test.Data = await async_test.toStruct("aaa", "bbb", 1);
    assertEQ(data.a, "aaa", "Data.a should be 'aaa'");
    assertEQ(data.b, "bbb", "Data.b should be 'bbb'");
    assertEQ(data.c, 1, "Data.c should be 1");

    {
        let err: BusinessError|undefined;
        try {
            data = await async_test.toStruct("aaa", "bbb", 0);
        } catch (e) {
            err = e as BusinessError;
        }
        assertEQ(err?.code, 1, "toStruct should throw an error");
        assertEQ(
            err?.message, "some error happen in toStructSync_impl",
            "toStruct should throw an error when c is 0");
    }
}

function main() {
    const suite = new ArkTestsuite("Async Test Suite");

    suite.addTest("Sync Add Tests", testSyncAdd);
    suite.addTest("Async Add Tests", testAsyncAdd);
    suite.addTest("Promise Add Tests", testPromiseAdd);
    suite.addTest("IBase Tests", testIBase);
    suite.addTest("Static Async Methods Tests", testStaticAsyncMethods);
    suite.addTest("Struct Methods Tests", testStructMethods);

    exit(suite.run());
}
