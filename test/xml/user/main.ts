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

import * as xml from "../generated/ohos.xml";
import * as fs from 'fs';

function main() {
  const filePath = "/home/lyujiayi/project/napi/TaiheCompiler/test/xml/data/test.xml";
  const c = fs.readFileSync(filePath, 'utf-8');
  let a: xml.BufferType = {content: c}
  let parser = xml.makeXmlPullParser(a);

  let po: xml.ParseOptions = {tagValueCallbackFunction: (value0: string, value1: string): boolean => {
    console.log("(tag) ", value0, ": ", value1)
    return true;
  },
  attributeValueCallbackFunction: (value0: string, value1: string): boolean => {
    console.log("(attribute) ", value0, ": ", value1)
    return true;
  }}
  parser.parseXml(po);
}

main();