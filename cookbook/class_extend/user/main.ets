import * as hello from "hello";

loadLibrary("class_extend");

function main() {
    let a = new hello.UnifiedRecord();
    let x1 = new hello.UnifiedData(a);
    x1.addRecord(a);
    let y1 = x1.getRecords();
    y1[0].getType();

    let b = new hello.Text();
    b.getType();
    b.getDetails();
    let x2 = new hello.UnifiedData(b);
    x2.addRecord(a);
    let y2 = x2.getRecords();
    y2[0].getType();

    let c = new hello.PlainText();
    c.getType();
    c.getDetails();
    c.getTextContent();
    let x3 = new hello.UnifiedData(c);
    x3.addRecord(a);
    let y3 = x3.getRecords();
    y3[0].getType();
}

main()