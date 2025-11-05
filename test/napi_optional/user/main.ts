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

import { showOptionalInt, makeOptionalInt } from "opt_test";

function main() {
  showOptionalInt(1);
  showOptionalInt(undefined);
  let res1 = makeOptionalInt(true);
  if ( res1 !== 10) throw new Error(`Unexpected result`);
  console.log(res1);
  let res2 = makeOptionalInt(false);
  if ( res2 !== undefined) throw new Error(`Unexpected result`);
  console.log(res2);
}

main();
