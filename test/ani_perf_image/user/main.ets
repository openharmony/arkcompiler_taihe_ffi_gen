import {image} from "@ohos.multimedia.image"

loadLibrary("ani_perf_image");

// let imageSourceApi: image.ImageSource;
// let pixelMap: image.PixelMap;
// let filesDir: string | undefined
// let cacheDir: string | undefined
// let fdNumber: number;
// let globalimageSource: image.ImageSource;
// let globalpixelmap: image.PixelMap

function runTestFunction(prompt: string, n: int, fn: () => void): void {
    const s = Chrono.nanoNow();
    for (let i: int = 0; i < n; i++) {
        fn();
    }
    const t = Chrono.nanoNow();
    let durationNs: double = (t - s) / n;
    console.log(`>> Done ${prompt}: ${durationNs / 1000} ms.`);
}

function testImage() {
    // create image source test
    const imageSource: image.ImageSource = image.createImageSource();

    // create pixel map test
    const defaultWidth: int = 41;
    const defaultHeight: int = 41;

    const desiredSize: image.Size|
        undefined = {width: defaultWidth, height: defaultHeight};
    const desiredRegion: image.Region|undefined = {
        size: {width: defaultWidth, height: defaultHeight},
        x: 0,
        y: 0
    };
    const decodeOpts: image.DecodingOptions = {
        index: 0,
        sampleSize: 1,
        rotate: 0,
        editable: true,
        desiredSize,
        desiredRegion,
        desiredPixelFormat: image.PixelMapFormat.RGBA_8888,
        fitDensity: 1
    };
    const pixelMap = imageSource.createPixelMapSync(decodeOpts);
}
function main() {
    runTestFunction("preheat", 500, testImage);
    runTestFunction("test", 2000, testImage);
}
