import * as huks from "../author_generated/huks"

loadLibrary("ani_huks")

function main() {
    console.log("hello main huks");
    let numbers1: byte[] = [1, 2, 3, 4, 5];
    let arrbuf1: ArrayBuffer = new ArrayBuffer(numbers1.length);
    for (let i = 0; i < numbers1.length; i++) {
        arrbuf1.set(i, numbers1[i]);
    }
    let numbers2: byte[] = [3, 4, 5, 6, 7];
    let arrbuf2: ArrayBuffer = new ArrayBuffer(numbers2.length);
    for (let i = 0; i < numbers2.length; i++) {
        arrbuf2.set(i, numbers2[i]);
    }
    const huksOptions: huks.HuksOptions = new huks.HuksOptions(
        [
            new huks.HuksParam(
                huks.HuksTag.HUKS_TAG_KEY_SIZE,
                huks.HuksKeySize.HUKS_RSA_KEY_SIZE_512 as number),
            new huks.HuksParam(huks.HuksTag.HUKS_TAG_KEY, arrbuf1),
        ],
        arrbuf2);

    console.log(huksOptions)

    let huksResult = huks.generateKey("alias", huksOptions);

    console.log(huksResult)
}
