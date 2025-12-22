/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
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
