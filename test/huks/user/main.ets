import * as huks from "../author_generated/huks"
function main() {
    console.log("hello main huks");
    const token = new Uint8Array([0x01, 0x02, 0x03]);
    const huksOptions: huks.HuksOptions = {
        properties: [
            {
                tag: new huks.HuksTag_inner(1, undefined), // 用具体的 tag 和 value 填充
                value: new huks.HuksParamValue_inner(2, true) // 或者使用其他值
            },
            {
                tag: new huks.HuksTag_inner(3, undefined),
                value: new huks.HuksParamValue_inner(4, 123.45) // 示例为 double
            }
        ],
        inData: token
    };

    const keyAlias: string = "KeyAlias"; 

    console.log(huks.generateKey(keyAlias, huksOptions));
    huks.generateKeyItem(keyAlias, huksOptions);

    console.log(huks.deleteKey(keyAlias, huksOptions));
    huks.deleteKeyItem(keyAlias, huksOptions);

    console.log(huks.importKey(keyAlias, huksOptions));
    huks.importKeyItem(keyAlias, huksOptions);

    console.log(huks.importWrappedKeyItem(keyAlias, "wrappingKeyAlias", huksOptions));

    console.log(huks.exportKey(keyAlias, huksOptions));
    huks.exportKeyItem(keyAlias, huksOptions);

    console.log(getKeyProperties(keyAlias, huksOptions));
    console.log(getKeyItemProperties(keyAlias, huksOptions));
    console.log(isKeyExist(keyAlias, huksOptions));
    console.log(isKeyItemExist(keyAlias, huksOptions));
    console.log(hasKeyItem(keyAlias, huksOptions));
    console.log(init(keyAlias, huksOptions));
    console.log(initSession(keyAlias, huksOptions));

    const handle: number = 3.14;
    console.log(update(handle, token, huksOptions));
    console.log(updateSession(handle, huksOptions, token));
    console.log(finish(handle, huksOptions));
    console.log(finishSession(handle, huksOptions, token));
    console.log(abort(handle, huksOptions));
    abortSession(handle, huksOptions);
    console.log(attestKeyItem(keyAlias, huksOptions));
    console.log(anonAttestKeyItem(keyAlias, huksOptions));
    console.log(getSdkVersion(huksOptions));
    console.log(listAliases(huksOptions));

}