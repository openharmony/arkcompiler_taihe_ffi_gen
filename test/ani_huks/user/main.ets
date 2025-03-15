import * as huks from "../author_generated/huks"

loadLibrary("ani_huks")

function main() {
    console.log("hello main huks");
    const huksOptions: huks.HuksOptions = new huks.HuksOptions(
        [
            new huks.HuksParam(
                new huks.HuksTag(2 << 28 | 1, undefined),
                new huks.HuksParamValue(0, true)
            ),
            new huks.HuksParam(
                new huks.HuksTag(5 << 28 | 9, undefined),
                new huks.HuksParamValue(3, [0x12, 0x34])
            ),
        ], [1, 2, 3]
    );

    console.log(huksOptions)

    let huksResult = huks.generateKey("alias", huksOptions);

    console.log(huksResult)
}
