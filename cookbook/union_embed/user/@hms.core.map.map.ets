import {make_map_inner, Resource} from "../author_generated/@hms.core.map.map_inner"

import {Image} from "./@ohos.multimedia.image"

export interface BaseOverlay {
    getId(): string;
    getZIndex(): int;
}

export interface BasePriorityOverlay extends BaseOverlay {
    getMaxZoom(): int;
    getMinZoom(): int;
}

export interface Bubble extends BasePriorityOverlay {
    // 当前需要把Aarray<T>替换成T[]
    setIcons(icons: ((string | Resource | Image)[])): Promise<int>;
    setPositions(positions: ((Resource[])[])): void;
}

export class BaseOverlay_inner implements BaseOverlay {
    map_inner_cls = make_map_inner();
    getId(): String {
        return this.map_inner_cls.getId();
    }
    getZIndex(): int {
        return this.map_inner_cls.getZIndex();
    }
}

export class BasePriorityOverlay_inner extends BaseOverlay_inner implements
    BasePriorityOverlay {
    getMaxZoom(): int {
        return this.map_inner_cls.getMaxZoom();
    }
    getMinZoom(): int {
        return this.map_inner_cls.getMinZoom();
    }
}

export class Bubble_inner extends BasePriorityOverlay_inner implements Bubble {
    setIcons(icons: ((string | Image | Resource)[])): Promise<int> {
        return launch this.map_inner_cls.setIcons_sync(icons);
    }
    setPositions(positions: ((Resource[])[])): void {
        return this.map_inner_cls.setPositions(positions);
    }
}