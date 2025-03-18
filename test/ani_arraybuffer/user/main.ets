import * as arraybuffer from "../author_generated/arraybuffer"

loadLibrary("ani_arraybuffer")

function main() {
    // case 1 : test sumArrayu8，The input parameter is ArrayBuffer, and the output parameter is u8
    let numbersU8: byte[] = [1, 2, 3, 4, 5];
    let arrbuf1: ArrayBuffer = new ArrayBuffer(numbersU8.length);
    for (let i = 0; i < numbersU8.length; i++) {
        arrbuf1.set(i, numbersU8[i]);
    }
    let sumArrayu8 = arraybuffer.sumArrayu8(arrbuf1)
    console.log("sumArrayu8 is " + sumArrayu8)
    assertEQ(sumArrayu8, 15)

    // case 2 : test getArrayBuffer，The input parameter is u8, and the output parameter is ArrayBuffer
    let getArrayBuffer = arraybuffer.getArrayBuffer(4 as byte)
    console.log("getArrayBuffer length: " + getArrayBuffer.getByteLength());
    assertEQ(getArrayBuffer.getByteLength(), 4)
    for (let i = 0; i < getArrayBuffer.getByteLength(); i++) {
        console.log(`getArrayBuffer Byte at index ${i}: ${getArrayBuffer.at(i)}`);
        assertEQ(getArrayBuffer.at(i), 4)
    }

    // case 3 : test doubleArrayBuffer，The input parameter is ArrayBuffer, and the output parameter is ArrayBuffer
    let numbers2: byte[] = [3, 4, 5, 6, 7];
    let arrbuf3: ArrayBuffer = new ArrayBuffer(numbers2.length);
    for (let i = 0; i < numbers2.length; i++) {
        arrbuf3.set(i, numbers2[i]);
    }
    let doubleArrayBuffer = arraybuffer.doubleArrayBuffer(arrbuf3)
    console.log("doubleArrayBuffer length: " + doubleArrayBuffer.getByteLength());
    assertEQ(doubleArrayBuffer.getByteLength(), 5)

    for (let i = 0; i < doubleArrayBuffer.getByteLength(); i++) {
        console.log(`doubleArrayBuffer Byte at index ${i}: ${doubleArrayBuffer.at(i)}`);
        assertEQ(doubleArrayBuffer.at(i), numbers2[i] * 2)
    }

    // case 4 : test Uint8Array to ArrayBuffer conversion
    let uint8Array = new Uint8Array([2, 3, 4, 5, 6]);
    let arrbuf4: ArrayBuffer = uint8Array.buffer as ArrayBuffer; // Convert Uint8Array to ArrayBuffer
    // Verify ArrayBuffer length
    console.log("arrbuf4 length: " + arrbuf4.getByteLength());
    assertEQ(arrbuf4.getByteLength(), uint8Array.length);
    // Verify ArrayBuffer content
    for (let i = 0; i < arrbuf4.getByteLength(); i++) {
        console.log(`arrbuf4 Byte at index ${i}: ${arrbuf4.at(i)}`);
        assertEQ(arrbuf4.at(i), uint8Array[i]);
    }
    // Optionally, pass the ArrayBuffer to a function for further validation
    let sumArrayu8FromUint8Array = arraybuffer.sumArrayu8(arrbuf4);
    console.log("sumArrayu8FromUint8Array is " + sumArrayu8FromUint8Array);
    assertEQ(sumArrayu8FromUint8Array, 20); // 2 + 3 + 4 + 5 + 6 = 20

    // case 6 ： test Uint8Array to ArrayBuffer conversion, use DataView
    let uint8ArrayData: Uint8Array = new Uint8Array([8, 9, 10]);
    let arrayBufferFromUint8Array: ArrayBuffer = new ArrayBuffer(uint8ArrayData.length);
    let view = new DataView(arrayBufferFromUint8Array);
    for (let i = 0; i < uint8ArrayData.length; i++) {
        view.setUint8(i, uint8ArrayData[i]);
    }

    for (let i = 0; i < uint8ArrayData.length; i++) {
        let value = view.getUint8(i);
        console.log(`Value at index ${i} in ArrayBuffer: ${value}`);
        assertEQ(value, uint8ArrayData[i]);
    }
    // Optionally, pass the ArrayBuffer to a function for further validation
    let sumArrayBufferFromUint8Array = arraybuffer.sumArrayu8(arrayBufferFromUint8Array);
    console.log("sumArrayBufferFromUint8Array is " + sumArrayBufferFromUint8Array);
    assertEQ(sumArrayBufferFromUint8Array, 27); // 8 + 9 + 10 = 27
}
