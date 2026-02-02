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

import * as map from "@hms.core.map.map";
import {createResource, Resource} from "@hms.core.map.map_inner";
import {BusinessError} from "@ohos.base";
import {Image, Image_inner} from "@ohos.multimedia.image";

loadLibrary("union_embed");

function main() {
    let BaseOverlay_cls = new map.BaseOverlay_inner()
    let BasePriorityOverlay_cls = new map.BasePriorityOverlay_inner()
    let Bubble_cls = new map.Bubble_inner()

    console.log(BaseOverlay_cls.getId())
    console.log(BaseOverlay_cls.getZIndex())

    console.log(BasePriorityOverlay_cls.getId())
    console.log(BasePriorityOverlay_cls.getZIndex())
    console.log(BasePriorityOverlay_cls.getMaxZoom())
    console.log(BasePriorityOverlay_cls.getMinZoom())

    console.log(Bubble_cls.getId())
    console.log(Bubble_cls.getZIndex())
    console.log(Bubble_cls.getMaxZoom())
    console.log(Bubble_cls.getMinZoom())

    let Resource_cls = createResource()
    let image_cls = new Image_inner()
    let array_union_input: (string|Image|Resource)[] =
        ["aaa", Resource_cls, image_cls];
    let promise_res =
        waitForCompletion(() => Bubble_cls.setIcons(array_union_input));

    let array_array_input: ((Resource[])[]) =
        [[Resource_cls, Resource_cls], [Resource_cls]]
    Bubble_cls.setPositions(array_array_input)

    CoroutineExtras.stopTaskpool();
}
