import { BusinessError } from '@ohos.base';
import type colorSpaceManager from '@ohos.graphics.colorSpaceManager';
import type resourceManager from '@ohos.resourceManager';
import type rpc from '@ohos.rpc';

type AsyncCallback<T> = (error: BusinessError | null, result: T | undefined) => void;

declare namespace image {
    enum PixelMapFormat {
        UNKNOWN = 0,
        RGB_565 = 2,
        RGBA_8888 = 3,
        BGRA_8888 = 4,
        RGB_888 = 5,
        ALPHA_8 = 6,
        RGBA_F16 = 7,
        NV21 = 8,
        NV12 = 9,
        RGBA_1010102 = 10,
        YCBCR_P010 = 11,
        YCRCB_P010 = 12
    }
    interface Size {
        height: number;
        width: number;
    }
    enum PropertyKey {
        BITS_PER_SAMPLE = 'BitsPerSample',
        ORIENTATION = 'Orientation',
        IMAGE_LENGTH = 'ImageLength',
        IMAGE_WIDTH = 'ImageWidth',
        GPS_LATITUDE = 'GPSLatitude',
        GPS_LONGITUDE = 'GPSLongitude',
        GPS_LATITUDE_REF = 'GPSLatitudeRef',
        GPS_LONGITUDE_REF = 'GPSLongitudeRef',
        DATE_TIME_ORIGINAL = 'DateTimeOriginal',
        EXPOSURE_TIME = 'ExposureTime',
        SCENE_TYPE = 'SceneType',
        ISO_SPEED_RATINGS = 'ISOSpeedRatings',
        F_NUMBER = 'FNumber',
        DATE_TIME = 'DateTime',
        GPS_TIME_STAMP = 'GPSTimeStamp',
        GPS_DATE_STAMP = 'GPSDateStamp',
        IMAGE_DESCRIPTION = 'ImageDescription',
        MAKE = 'Make',
        MODEL = 'Model',
        PHOTO_MODE = 'PhotoMode',
        SENSITIVITY_TYPE = 'SensitivityType',
        STANDARD_OUTPUT_SENSITIVITY = 'StandardOutputSensitivity',
        RECOMMENDED_EXPOSURE_INDEX = 'RecommendedExposureIndex',
        ISO_SPEED = 'ISOSpeedRatings',
        APERTURE_VALUE = 'ApertureValue',
        EXPOSURE_BIAS_VALUE = 'ExposureBiasValue',
        METERING_MODE = 'MeteringMode',
        LIGHT_SOURCE = 'LightSource',
        FLASH = 'Flash',
        FOCAL_LENGTH = 'FocalLength',
        USER_COMMENT = 'UserComment',
        PIXEL_X_DIMENSION = 'PixelXDimension',
        PIXEL_Y_DIMENSION = 'PixelYDimension',
        WHITE_BALANCE = 'WhiteBalance',
        FOCAL_LENGTH_IN_35_MM_FILM = 'FocalLengthIn35mmFilm',
        CAPTURE_MODE = 'HwMnoteCaptureMode',
        PHYSICAL_APERTURE = 'HwMnotePhysicalAperture',
        ROLL_ANGLE = 'HwMnoteRollAngle',
        PITCH_ANGLE = 'HwMnotePitchAngle',
        SCENE_FOOD_CONF = 'HwMnoteSceneFoodConf',
        SCENE_STAGE_CONF = 'HwMnoteSceneStageConf',
        SCENE_BLUE_SKY_CONF = 'HwMnoteSceneBlueSkyConf',
        SCENE_GREEN_PLANT_CONF = 'HwMnoteSceneGreenPlantConf',
        SCENE_BEACH_CONF = 'HwMnoteSceneBeachConf',
        SCENE_SNOW_CONF = 'HwMnoteSceneSnowConf',
        SCENE_SUNSET_CONF = 'HwMnoteSceneSunsetConf',
        SCENE_FLOWERS_CONF = 'HwMnoteSceneFlowersConf',
        SCENE_NIGHT_CONF = 'HwMnoteSceneNightConf',
        SCENE_TEXT_CONF = 'HwMnoteSceneTextConf',
        FACE_COUNT = 'HwMnoteFaceCount',
        FOCUS_MODE = 'HwMnoteFocusMode',
        COMPRESSION = 'Compression',
        PHOTOMETRIC_INTERPRETATION = 'PhotometricInterpretation',
        STRIP_OFFSETS = 'StripOffsets',
        SAMPLES_PER_PIXEL = 'SamplesPerPixel',
        ROWS_PER_STRIP = 'RowsPerStrip',
        STRIP_BYTE_COUNTS = 'StripByteCounts',
        X_RESOLUTION = 'XResolution',
        Y_RESOLUTION = 'YResolution',
        PLANAR_CONFIGURATION = 'PlanarConfiguration',
        RESOLUTION_UNIT = 'ResolutionUnit',
        TRANSFER_FUNCTION = 'TransferFunction',
        SOFTWARE = 'Software',
        ARTIST = 'Artist',
        WHITE_POINT = 'WhitePoint',
        PRIMARY_CHROMATICITIES = 'PrimaryChromaticities',
        YCBCR_COEFFICIENTS = 'YCbCrCoefficients',
        YCBCR_SUB_SAMPLING = 'YCbCrSubSampling',
        YCBCR_POSITIONING = 'YCbCrPositioning',
        REFERENCE_BLACK_WHITE = 'ReferenceBlackWhite',
        COPYRIGHT = 'Copyright',
        JPEG_INTERCHANGE_FORMAT = 'JPEGInterchangeFormat',
        JPEG_INTERCHANGE_FORMAT_LENGTH = 'JPEGInterchangeFormatLength',
        EXPOSURE_PROGRAM = 'ExposureProgram',
        SPECTRAL_SENSITIVITY = 'SpectralSensitivity',
        OECF = 'OECF',
        EXIF_VERSION = 'ExifVersion',
        DATE_TIME_DIGITIZED = 'DateTimeDigitized',
        COMPONENTS_CONFIGURATION = 'ComponentsConfiguration',
        SHUTTER_SPEED = 'ShutterSpeedValue',
        BRIGHTNESS_VALUE = 'BrightnessValue',
        MAX_APERTURE_VALUE = 'MaxApertureValue',
        SUBJECT_DISTANCE = 'SubjectDistance',
        SUBJECT_AREA = 'SubjectArea',
        MAKER_NOTE = 'MakerNote',
        SUBSEC_TIME = 'SubsecTime',
        SUBSEC_TIME_ORIGINAL = 'SubsecTimeOriginal',
        SUBSEC_TIME_DIGITIZED = 'SubsecTimeDigitized',
        FLASHPIX_VERSION = 'FlashpixVersion',
        COLOR_SPACE = 'ColorSpace',
        RELATED_SOUND_FILE = 'RelatedSoundFile',
        FLASH_ENERGY = 'FlashEnergy',
        SPATIAL_FREQUENCY_RESPONSE = 'SpatialFrequencyResponse',
        FOCAL_PLANE_X_RESOLUTION = 'FocalPlaneXResolution',
        FOCAL_PLANE_Y_RESOLUTION = 'FocalPlaneYResolution',
        FOCAL_PLANE_RESOLUTION_UNIT = 'FocalPlaneResolutionUnit',
        SUBJECT_LOCATION = 'SubjectLocation',
        EXPOSURE_INDEX = 'ExposureIndex',
        SENSING_METHOD = 'SensingMethod',
        FILE_SOURCE = 'FileSource',
        CFA_PATTERN = 'CFAPattern',
        CUSTOM_RENDERED = 'CustomRendered',
        EXPOSURE_MODE = 'ExposureMode',
        DIGITAL_ZOOM_RATIO = 'DigitalZoomRatio',
        SCENE_CAPTURE_TYPE = 'SceneCaptureType',
        GAIN_CONTROL = 'GainControl',
        CONTRAST = 'Contrast',
        SATURATION = 'Saturation',
        SHARPNESS = 'Sharpness',
        DEVICE_SETTING_DESCRIPTION = 'DeviceSettingDescription',
        SUBJECT_DISTANCE_RANGE = 'SubjectDistanceRange',
        IMAGE_UNIQUE_ID = 'ImageUniqueID',
        GPS_VERSION_ID = 'GPSVersionID',
        GPS_ALTITUDE_REF = 'GPSAltitudeRef',
        GPS_ALTITUDE = 'GPSAltitude',
        GPS_SATELLITES = 'GPSSatellites',
        GPS_STATUS = 'GPSStatus',
        GPS_MEASURE_MODE = 'GPSMeasureMode',
        GPS_DOP = 'GPSDOP',
        GPS_SPEED_REF = 'GPSSpeedRef',
        GPS_SPEED = 'GPSSpeed',
        GPS_TRACK_REF = 'GPSTrackRef',
        GPS_TRACK = 'GPSTrack',
        GPS_IMG_DIRECTION_REF = 'GPSImgDirectionRef',
        GPS_IMG_DIRECTION = 'GPSImgDirection',
        GPS_MAP_DATUM = 'GPSMapDatum',
        GPS_DEST_LATITUDE_REF = 'GPSDestLatitudeRef',
        GPS_DEST_LATITUDE = 'GPSDestLatitude',
        GPS_DEST_LONGITUDE_REF = 'GPSDestLongitudeRef',
        GPS_DEST_LONGITUDE = 'GPSDestLongitude',
        GPS_DEST_BEARING_REF = 'GPSDestBearingRef',
        GPS_DEST_BEARING = 'GPSDestBearing',
        GPS_DEST_DISTANCE_REF = 'GPSDestDistanceRef',
        GPS_DEST_DISTANCE = 'GPSDestDistance',
        GPS_PROCESSING_METHOD = 'GPSProcessingMethod',
        GPS_AREA_INFORMATION = 'GPSAreaInformation',
        GPS_DIFFERENTIAL = 'GPSDifferential',
        BODY_SERIAL_NUMBER = 'BodySerialNumber',
        CAMERA_OWNER_NAME = 'CameraOwnerName',
        COMPOSITE_IMAGE = 'CompositeImage',
        COMPRESSED_BITS_PER_PIXEL = 'CompressedBitsPerPixel',
        DNG_VERSION = 'DNGVersion',
        DEFAULT_CROP_SIZE = 'DefaultCropSize',
        GAMMA = 'Gamma',
        ISO_SPEED_LATITUDE_YYY = 'ISOSpeedLatitudeyyy',
        ISO_SPEED_LATITUDE_ZZZ = 'ISOSpeedLatitudezzz',
        LENS_MAKE = 'LensMake',
        LENS_MODEL = 'LensModel',
        LENS_SERIAL_NUMBER = 'LensSerialNumber',
        LENS_SPECIFICATION = 'LensSpecification',
        NEW_SUBFILE_TYPE = 'NewSubfileType',
        OFFSET_TIME = 'OffsetTime',
        OFFSET_TIME_DIGITIZED = 'OffsetTimeDigitized',
        OFFSET_TIME_ORIGINAL = 'OffsetTimeOriginal',
        SOURCE_EXPOSURE_TIMES_OF_COMPOSITE_IMAGE = 'SourceExposureTimesOfCompositeImage',
        SOURCE_IMAGE_NUMBER_OF_COMPOSITE_IMAGE = 'SourceImageNumberOfCompositeImage',
        SUBFILE_TYPE = 'SubfileType',
        GPS_H_POSITIONING_ERROR = 'GPSHPositioningError',
        PHOTOGRAPHIC_SENSITIVITY = 'PhotographicSensitivity',
        BURST_NUMBER = 'HwMnoteBurstNumber',
        FACE_CONF = 'HwMnoteFaceConf',
        FACE_LEYE_CENTER = 'HwMnoteFaceLeyeCenter',
        FACE_MOUTH_CENTER = 'HwMnoteFaceMouthCenter',
        FACE_POINTER = 'HwMnoteFacePointer',
        FACE_RECT = 'HwMnoteFaceRect',
        FACE_REYE_CENTER = 'HwMnoteFaceReyeCenter',
        FACE_SMILE_SCORE = 'HwMnoteFaceSmileScore',
        FACE_VERSION = 'HwMnoteFaceVersion',
        FRONT_CAMERA = 'HwMnoteFrontCamera',
        SCENE_POINTER = 'HwMnoteScenePointer',
        SCENE_VERSION = 'HwMnoteSceneVersion',
        IS_XMAGE_SUPPORTED = 'HwMnoteIsXmageSupported',
        XMAGE_MODE = 'HwMnoteXmageMode',
        XMAGE_LEFT = 'HwMnoteXmageLeft',
        XMAGE_TOP = 'HwMnoteXmageTop',
        XMAGE_RIGHT = 'HwMnoteXmageRight',
        XMAGE_BOTTOM = 'HwMnoteXmageBottom',
        CLOUD_ENHANCEMENT_MODE = 'HwMnoteCloudEnhancementMode',
        WIND_SNAPSHOT_MODE = 'HwMnoteWindSnapshotMode',
        GIF_LOOP_COUNT = 'GIFLoopCount'
    }
    enum ImageFormat {
        YCBCR_422_SP = 1000,
        JPEG = 2000
    }
    enum AlphaType {
        UNKNOWN = 0,
        OPAQUE = 1,
        PREMUL = 2,
        UNPREMUL = 3
    }
    enum DecodingDynamicRange {
        AUTO = 0,
        SDR = 1,
        HDR = 2
    }
    enum PackingDynamicRange {
        AUTO = 0,
        SDR = 1
    }
    enum AntiAliasingLevel {
        NONE = 0,
        LOW = 1,
        MEDIUM = 2,
        HIGH = 3
    }
    enum ScaleMode {
        FIT_TARGET_SIZE = 0,
        CENTER_CROP = 1
    }
    enum ComponentType {
        YUV_Y = 1,
        YUV_U = 2,
        YUV_V = 3,
        JPEG = 4
    }
    enum HdrMetadataKey {
        HDR_METADATA_TYPE = 0,
        HDR_STATIC_METADATA = 1,
        HDR_DYNAMIC_METADATA = 2,
        HDR_GAINMAP_METADATA = 3
    }
    enum HdrMetadataType {
        NONE = 0,
        BASE = 1,
        GAINMAP = 2,
        ALTERNATE = 3
    }
    interface Region {
        size: Size;
        x: number;
        y: number;
    }
    interface PositionArea {
        pixels: ArrayBuffer;
        offset: number;
        stride: number;
        region: Region;
    }
    interface ImageInfo {
        size: Size;
        density: number;
        stride: number;
        pixelFormat: PixelMapFormat;
        alphaType: AlphaType;
        mimeType: string;
        isHdr: boolean;
    }
    interface PackingOption {
        format: string;
        quality: number;
        bufferSize?: number;
        desiredDynamicRange?: PackingDynamicRange;
        needsPackProperties?: boolean;
    }
    interface GetImagePropertyOptions {
        index?: number;
        defaultValue?: string;
    }
    interface ImagePropertyOptions {
        index?: number;
        defaultValue?: string;
    }
    interface DecodingOptions {
        index?: number;
        sampleSize?: number;
        rotate?: number;
        editable?: boolean;
        desiredSize?: Size;
        desiredRegion?: Region;
        desiredPixelFormat?: PixelMapFormat;
        fitDensity?: number;
        desiredColorSpace?: colorSpaceManager.ColorSpaceManager;
        desiredDynamicRange?: DecodingDynamicRange;
    }
    interface Component {
        readonly componentType: ComponentType;
        readonly rowStride: number;
        readonly pixelStride: number;
        readonly byteBuffer: ArrayBuffer;
    }
    interface InitializationOptions {
        size: Size;
        srcPixelFormat?: PixelMapFormat;
        pixelFormat?: PixelMapFormat;
        editable?: boolean;
        alphaType?: AlphaType;
        scaleMode?: ScaleMode;
    }
    interface SourceOptions {
        sourceDensity: number;
        sourcePixelFormat?: PixelMapFormat;
        sourceSize?: Size;
    }
    interface HdrStaticMetadata {
        displayPrimariesX: Array<number>;
        displayPrimariesY: Array<number>;
        whitePointX: number;
        whitePointY: number;
        maxLuminance: number;
        minLuminance: number;
        maxContentLightLevel: number;
        maxFrameAverageLightLevel: number;
    }
    interface GainmapChannel {
        gainmapMax: number;
        gainmapMin: number;
        gamma: number;
        baseOffset: number;
        alternateOffset: number;
    }
    interface HdrGainmapMetadata {
        writerVersion: number;
        miniVersion: number;
        gainmapChannelCount: number;
        useBaseColorFlag: boolean;
        baseHeadroom: number;
        alternateHeadroom: number;
        channels: Array<GainmapChannel>;
    }
    type HdrMetadataValue = HdrMetadataType | HdrStaticMetadata | ArrayBuffer | HdrGainmapMetadata;
    function createPixelMap(colors: ArrayBuffer, options: InitializationOptions, callback: AsyncCallback<PixelMap>): void;
    function createPixelMap(colors: ArrayBuffer, options: InitializationOptions): Promise<PixelMap>;
    function createPixelMapSync(colors: ArrayBuffer, options: InitializationOptions): PixelMap;
    function createPixelMapSync(options: InitializationOptions): PixelMap;
    function createPremultipliedPixelMap(src: PixelMap, dst: PixelMap, callback: AsyncCallback<void>): void;
    function createPremultipliedPixelMap(src: PixelMap, dst: PixelMap): Promise<void>;
    function createUnpremultipliedPixelMap(src: PixelMap, dst: PixelMap, callback: AsyncCallback<void>): void;
    function createUnpremultipliedPixelMap(src: PixelMap, dst: PixelMap): Promise<void>;
    function createPixelMapFromParcel(sequence: rpc.MessageSequence): PixelMap;
    function createPixelMapFromSurface(surfaceId: string, region: Region): Promise<PixelMap>;
    function createPixelMapFromSurfaceSync(surfaceId: string, region: Region): PixelMap;
    function createImageSource(uri: string): ImageSource;
    function createImageSource(uri: string, options: SourceOptions): ImageSource;
    function createImageSource(fd: number): ImageSource;
    function createImageSource(fd: number, options: SourceOptions): ImageSource;
    function createImageSource(buf: ArrayBuffer): ImageSource;
    function createImageSource(buf: ArrayBuffer, options: SourceOptions): ImageSource;
    function createImageSource(rawfile: resourceManager.RawFileDescriptor, options?: SourceOptions): ImageSource;
    function CreateIncrementalSource(buf: ArrayBuffer): ImageSource;
    function CreateIncrementalSource(buf: ArrayBuffer, options?: SourceOptions): ImageSource;
    function createImagePacker(): ImagePacker;
    function createImageReceiver(width: number, height: number, format: number, capacity: number): ImageReceiver;
    function createImageReceiver(size: Size, format: ImageFormat, capacity: number): ImageReceiver;
    function createImageCreator(width: number, height: number, format: number, capacity: number): ImageCreator;
    function createImageCreator(size: Size, format: ImageFormat, capacity: number): ImageCreator;
    interface PixelMap {
        readonly isEditable: boolean;
        readPixelsToBuffer(dst: ArrayBuffer): Promise<void>;
        readPixelsToBuffer(dst: ArrayBuffer, callback: AsyncCallback<void>): void;
        readPixelsToBufferSync(dst: ArrayBuffer): void;
        readPixels(area: PositionArea): Promise<void>;
        readPixels(area: PositionArea, callback: AsyncCallback<void>): void;
        readPixelsSync(area: PositionArea): void;
        writePixels(area: PositionArea): Promise<void>;
        writePixels(area: PositionArea, callback: AsyncCallback<void>): void;
        writePixelsSync(area: PositionArea): void;
        writeBufferToPixels(src: ArrayBuffer): Promise<void>;
        writeBufferToPixels(src: ArrayBuffer, callback: AsyncCallback<void>): void;
        writeBufferToPixelsSync(src: ArrayBuffer): void;
        toSdr(): Promise<void>;
        getImageInfo(): Promise<ImageInfo>;
        getImageInfo(callback: AsyncCallback<ImageInfo>): void;
        getImageInfoSync(): ImageInfo;
        getBytesNumberPerRow(): number;
        getPixelBytesNumber(): number;
        getDensity(): number;
        opacity(rate: number, callback: AsyncCallback<void>): void;
        opacity(rate: number): Promise<void>;
        opacitySync(rate: number): void;
        createAlphaPixelmap(): Promise<PixelMap>;
        createAlphaPixelmap(callback: AsyncCallback<PixelMap>): void;
        createAlphaPixelmapSync(): PixelMap;
        scale(x: number, y: number, callback: AsyncCallback<void>): void;
        scale(x: number, y: number): Promise<void>;
        scaleSync(x: number, y: number): void;
        scale(x: number, y: number, level: AntiAliasingLevel): Promise<void>;
        scaleSync(x: number, y: number, level: AntiAliasingLevel): void;
        translate(x: number, y: number, callback: AsyncCallback<void>): void;
        translate(x: number, y: number): Promise<void>;
        translateSync(x: number, y: number): void;
        rotate(angle: number, callback: AsyncCallback<void>): void;
        rotate(angle: number): Promise<void>;
        rotateSync(angle: number): void;
        flip(horizontal: boolean, vertical: boolean, callback: AsyncCallback<void>): void;
        flip(horizontal: boolean, vertical: boolean): Promise<void>;
        flipSync(horizontal: boolean, vertical: boolean): void;
        crop(region: Region, callback: AsyncCallback<void>): void;
        crop(region: Region): Promise<void>;
        cropSync(region: Region): void;
        getColorSpace(): colorSpaceManager.ColorSpaceManager;
        marshalling(sequence: rpc.MessageSequence): void;
        unmarshalling(sequence: rpc.MessageSequence): Promise<PixelMap>;
        setColorSpace(colorSpace: colorSpaceManager.ColorSpaceManager): void;
        readonly isStrideAlignment: boolean;
        applyColorSpace(targetColorSpace: colorSpaceManager.ColorSpaceManager, callback: AsyncCallback<void>): void;
        applyColorSpace(targetColorSpace: colorSpaceManager.ColorSpaceManager): Promise<void>;
        convertPixelFormat(targetPixelFormat: PixelMapFormat): Promise<void>;
        release(callback: AsyncCallback<void>): void;
        release(): Promise<void>;
        setTransferDetached(detached: boolean): void;
        getMetadata(key: HdrMetadataKey): HdrMetadataValue;
        setMemoryNameSync(name: string): void;
        setMetadata(key: HdrMetadataKey, value: HdrMetadataValue): Promise<void>;
    }
    interface Picture {
        getMainPixelmap(): PixelMap;
        getHdrComposedPixelmap(): Promise<PixelMap>;
        getGainmapPixelmap(): PixelMap | null;
        setAuxiliaryPicture(type: AuxiliaryPictureType, auxiliaryPicture: AuxiliaryPicture): void;
        getAuxiliaryPicture(type: AuxiliaryPictureType): AuxiliaryPicture | null;
        setMetadata(metadataType: MetadataType, metadata: Metadata): Promise<void>;
        getMetadata(metadataType: MetadataType): Promise<Metadata>;
        marshalling(sequence: rpc.MessageSequence): void;
        release(): void;
    }
    function createPicture(mainPixelmap: PixelMap): Picture;
    function createPictureFromParcel(sequence: rpc.MessageSequence): Picture;
    function createAuxiliaryPicture(buffer: ArrayBuffer, size: Size, type: AuxiliaryPictureType): AuxiliaryPicture;
    interface AuxiliaryPicture {
        writePixelsFromBuffer(data: ArrayBuffer): Promise<void>;
        readPixelsToBuffer(): Promise<ArrayBuffer>;
        getType(): AuxiliaryPictureType;
        setMetadata(metadataType: MetadataType, metadata: Metadata): Promise<void>;
        getMetadata(metadataType: MetadataType): Promise<Metadata>;
        getAuxiliaryPictureInfo(): AuxiliaryPictureInfo;
        setAuxiliaryPictureInfo(info: AuxiliaryPictureInfo): void;
        release(): void;
    }
    enum AuxiliaryPictureType {
        GAINMAP = 1,
        DEPTH_MAP = 2,
        UNREFOCUS_MAP = 3,
        LINEAR_MAP = 4,
        FRAGMENT_MAP = 5
    }
    enum MetadataType {
        EXIF_METADATA = 1,
        FRAGMENT_METADATA = 2
    }
    interface Metadata {
        getProperties(key: Array<string>): Promise<Record<string, string | null>>;
        setProperties(records: Record<string, string | null>): Promise<void>;
        getAllProperties(): Promise<Record<string, string | null>>;
        clone(): Promise<Metadata>;
    }
    enum FragmentMapPropertyKey {
        X_IN_ORIGINAL = 'XInOriginal',
        Y_IN_ORIGINAL = 'YInOriginal',
        WIDTH = 'FragmentImageWidth',
        HEIGHT = 'FragmentImageHeight'
    }
    interface DecodingOptionsForPicture {
        desiredAuxiliaryPictures: Array<AuxiliaryPictureType>;
    }
    interface AuxiliaryPictureInfo {
        auxiliaryPictureType: AuxiliaryPictureType;
        size: Size;
        rowStride: number;
        pixelFormat: PixelMapFormat;
        colorSpace: colorSpaceManager.ColorSpaceManager;
    }
    interface ImageSource {
        getImageInfo(index: number, callback: AsyncCallback<ImageInfo>): void;
        getImageInfo(callback: AsyncCallback<ImageInfo>): void;
        getImageInfo(index?: number): Promise<ImageInfo>;
        getImageInfoSync(index?: number): ImageInfo;
        createPixelMap(options?: DecodingOptions): Promise<PixelMap>;
        createPixelMap(callback: AsyncCallback<PixelMap>): void;
        createPixelMap(options: DecodingOptions, callback: AsyncCallback<PixelMap>): void;
        createPixelMapSync(options?: DecodingOptions): PixelMap;
        createPixelMapList(options?: DecodingOptions): Promise<Array<PixelMap>>;
        createPixelMapList(callback: AsyncCallback<Array<PixelMap>>): void;
        createPixelMapList(options: DecodingOptions, callback: AsyncCallback<Array<PixelMap>>): void;
        getDelayTimeList(): Promise<Array<number>>;
        getDelayTimeList(callback: AsyncCallback<Array<number>>): void;
        getDisposalTypeList(): Promise<Array<number>>;
        getFrameCount(): Promise<number>;
        getFrameCount(callback: AsyncCallback<number>): void;
        getImageProperty(key: PropertyKey, options?: ImagePropertyOptions): Promise<string>;
        getImageProperty(key: string, options?: GetImagePropertyOptions): Promise<string>;
        getImageProperty(key: string, callback: AsyncCallback<string>): void;
        getImageProperty(key: string, options: GetImagePropertyOptions, callback: AsyncCallback<string>): void;
        getImageProperties(key: Array<PropertyKey>): Promise<Record<PropertyKey, string | null>>;
        modifyImageProperty(key: PropertyKey, value: string): Promise<void>;
        modifyImageProperty(key: string, value: string): Promise<void>;
        modifyImageProperty(key: string, value: string, callback: AsyncCallback<void>): void;
        modifyImageProperties(records: Record<PropertyKey, string | null>): Promise<void>;
        updateData(buf: ArrayBuffer, isFinished: boolean, offset: number, length: number): Promise<void>;
        updateData(buf: ArrayBuffer, isFinished: boolean, offset: number, length: number, callback: AsyncCallback<void>): void;
        release(callback: AsyncCallback<void>): void;
        release(): Promise<void>;
        createPicture(options?: DecodingOptionsForPicture): Promise<Picture>;
        readonly supportedFormats: Array<string>;
    }
    interface ImagePacker {
        packing(source: ImageSource, option: PackingOption, callback: AsyncCallback<ArrayBuffer>): void;
        packing(source: ImageSource, option: PackingOption): Promise<ArrayBuffer>;
        packToData(source: ImageSource, options: PackingOption): Promise<ArrayBuffer>;
        packing(source: PixelMap, option: PackingOption, callback: AsyncCallback<ArrayBuffer>): void;
        packing(source: PixelMap, option: PackingOption): Promise<ArrayBuffer>;
        packToData(source: PixelMap, options: PackingOption): Promise<ArrayBuffer>;
        packToFile(source: ImageSource, fd: number, options: PackingOption, callback: AsyncCallback<void>): void;
        packToFile(source: ImageSource, fd: number, options: PackingOption): Promise<void>;
        packToFile(source: PixelMap, fd: number, options: PackingOption, callback: AsyncCallback<void>): void;
        packToFile(source: PixelMap, fd: number, options: PackingOption): Promise<void>;
        release(callback: AsyncCallback<void>): void;
        release(): Promise<void>;
        packing(picture: Picture, options: PackingOption): Promise<ArrayBuffer>;
        packToFile(picture: Picture, fd: number, options: PackingOption): Promise<void>;
        readonly supportedFormats: Array<string>;
    }
    interface Image {
        clipRect: Region;
        readonly size: Size;
        readonly format: number;
        readonly timestamp: number;
        getComponent(componentType: ComponentType, callback: AsyncCallback<Component>): void;
        getComponent(componentType: ComponentType): Promise<Component>;
        release(callback: AsyncCallback<void>): void;
        release(): Promise<void>;
    }
    interface ImageReceiver {
        readonly size: Size;
        readonly capacity: number;
        readonly format: ImageFormat;
        getReceivingSurfaceId(callback: AsyncCallback<string>): void;
        getReceivingSurfaceId(): Promise<string>;
        readLatestImage(callback: AsyncCallback<Image>): void;
        readLatestImage(): Promise<Image>;
        readNextImage(callback: AsyncCallback<Image>): void;
        readNextImage(): Promise<Image>;
        on(type: 'imageArrival', callback: AsyncCallback<void>): void;
        off(type: 'imageArrival', callback?: AsyncCallback<void>): void;
        release(callback: AsyncCallback<void>): void;
        release(): Promise<void>;
    }
    interface ImageCreator {
        readonly capacity: number;
        readonly format: ImageFormat;
        dequeueImage(callback: AsyncCallback<Image>): void;
        dequeueImage(): Promise<Image>;
        queueImage(interface: Image, callback: AsyncCallback<void>): void;
        queueImage(interface: Image): Promise<void>;
        on(type: 'imageRelease', callback: AsyncCallback<void>): void;
        off(type: 'imageRelease', callback?: AsyncCallback<void>): void;
        release(callback: AsyncCallback<void>): void;
        release(): Promise<void>;
    }
}
export default image;
