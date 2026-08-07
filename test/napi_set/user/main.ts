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

const lib = requireNapi('./set_test.so', RequireBaseDir.SCRIPT_DIR);

function main() {
  const values = new Set<string>(["alpha", "beta", "alpha"]);
  if (lib.getStringSetSize(values) !== 2) throw new Error(`Unexpected input set size`);

  const result: Set<string> = lib.addString(values, "gamma");
  if (!(result instanceof Set)) throw new Error(`Expected a Set result`);
  if (result.size !== 3) throw new Error(`Unexpected result set size`);
  if (!result.has("alpha") || !result.has("beta") || !result.has("gamma")) {
    throw new Error(`Unexpected result set contents`);
  }
  if (values.has("gamma")) throw new Error(`Input set was modified`);

  const duplicateResult: Set<string> = lib.addString(values, "alpha");
  if (duplicateResult.size !== 2) throw new Error(`Duplicate value was inserted`);
}

main();