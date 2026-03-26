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

const lib = requireNapi('./async_test.so', RequireBaseDir.SCRIPT_DIR);

function main() {
    console.log("before call function addRetPromise success");
    let p1 = lib.addRetPromise(1, 2);
    p1.then((res) => {
        console.log("success", res);
    })
    .catch((ret) => {
        console.log("failed", ret);
    });
    console.log("after call function addRetPromise success");

    console.log("before call function addRetPromise failed");
    let p2 = lib.addRetPromise(0, 2);
    p2.then((res) => {
        console.log("success", res);
    })
    .catch((ret) => {
        console.log("failed", ret.message);
    });
    console.log("after call function addRetPromise failed");

    console.log("before call function addWithAsync success");
    lib.addWithAsync(1, 2, (error: Error | null, result?: number) => {
        if (error !== null) {
            console.log("failed in f", error.message);
        } else {
            console.log("success in f", result!);
        }
    })
    console.log("after call function addWithAsync success");

    console.log("before call function addWithAsync failed");
    lib.addWithAsync(0, 2, (error: Error | null, result?: number) => {
        if (error !== null) {
            console.log("failed in f", error.message);
        } else {
            console.log("success in f", result!);
        }
    })
    console.log("after call function addWithAsync failed");

    let mybase = new lib.IBase();
    mybase.makeSync();
    mybase.makeRetPromise();
    mybase.makeWithAsync((error: Error | null) => {
        if (error !== null) {
            console.log("failed in make", error.message);
        } else {
            console.log("success in make");
        }
    });

    lib.IBase.printSync();
    lib.IBase.printRetPromise();
    lib.IBase.printWithAsync((error: Error | null) => {
        if (error !== null) {
            console.log("failed in print", error.message);
        } else {
            console.log("success in print");
        }
    });

    let mydata: lib.Data = lib.toStructSync("a", "b", 1);
    lib.toStructRetPromise("a", "b", 1);
    lib.toStructWithAsync("a", "b", 1, (error: Error | null, result?: lib.Data) => {
        if (error !== null) {
            console.log("failed in toStruct", error.message);
        } else {
            console.log("success in toStruct", result!.a, result!.b, result!.c);
        }
    });

    lib.fromStructSync(mydata);
    lib.fromStructRetPromise(mydata);
    lib.fromStructWithAsync(mydata, (error: Error | null) => {
        if (error !== null) {
            console.log("failed in fromStruct", error.message);
        } else {
            console.log("success in fromStruct");
        }
    });
    console.log("finish main");
}

main();
