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

const lib = requireNapi('./maythrow.so', RequireBaseDir.SCRIPT_DIR);

function main() {
    try {
        let res = lib.maythrow(0);
        console.log('Success:', res);
    } catch (error) {
        if (error.message !== "some error happen") throw new Error(`Unexpected result`);
        console.error('maythrow Error caught:', error.message);
    }

    try {
        let res = lib.maythrow(1);
        console.log('Success:', res);
    } catch (error) {
        console.error('maythrow Error caught:', error.message);
    }

    try {
        let res = lib.getDataMaythrow();
        console.log('Success:', res);
    } catch (error) {
        console.error('getDataMaythrow Error caught:', error.message);
    }

    try {
        lib.noReturnMaythrow();
    } catch (error) {
        console.error('noReturnMaythrow Error caught:', error.message);
    }

    try {
        lib.noReturnTypeError();
    } catch (error) {
        console.error('noReturnTypeError Error caught:', error.message);
    }
    
    try {
        lib.noReturnRangeError();
    } catch (error) {
        console.error('noReturnRangeError Error caught:', error.message);
    }
}

main()