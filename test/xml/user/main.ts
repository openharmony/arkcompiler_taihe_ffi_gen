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