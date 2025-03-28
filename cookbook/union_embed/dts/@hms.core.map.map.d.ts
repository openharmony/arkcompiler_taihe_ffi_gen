import type image from "@ohos.multimedia.image";

interface BaseOverlay {
    getId(): string;
    getZIndex(): number;
    getTag(): Object;
    isVisible(): boolean;
    remove(): void;
    setZIndex(zIndex: number): void;
    setTag(tag: Object): void;
    setVisible(visible: boolean): void;
}

interface BasePriorityOverlay extends BaseOverlay {
    getMaxZoom(): number;
    getMinZoom(): number;
    setPriority(priority: number): void;
    setZoom(minZoom: number, maxZoom: number): void;
    startAnimation(): void;
    clearAnimation(): void;
}

interface Bubble extends BasePriorityOverlay {
    setIcons(icons: Array<string | image.PixelMap | Resource>): Promise<void>;
    setPositions(positions: Array<Array<mapCommon.LatLng>>): void;
}
