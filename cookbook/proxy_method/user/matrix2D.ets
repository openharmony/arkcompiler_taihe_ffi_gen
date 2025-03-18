import * as proxy from "../author_generated/matrix2D__"
loadLibrary("proxy_method");

export class Matrix2D {
    scaleX: (int | undefined);
    scaleY: (int | undefined);
    rotateX: (int | undefined);
    rotateY: (int | undefined);
    translateX: (int | undefined);
    translateY: (int | undefined);
    constructor(
        scaleX: (int | undefined),
        scaleY: (int | undefined),
        rotateX: (int | undefined),
        rotateY: (int | undefined),
        translateX: (int | undefined),
        translateY: (int | undefined),
    ) {
        this.scaleX = scaleX;
        this.scaleY = scaleY;
        this.rotateX = rotateX;
        this.rotateY = rotateY;
        this.translateX = translateX;
        this.translateY = translateY;
    }

    constructor(base: proxy.Matrix2D) {
        this.scaleX = base.scaleX;
        this.scaleY = base.scaleY;
        this.rotateX = base.rotateX;
        this.rotateY = base.rotateY;
        this.translateX = base.translateX;
        this.translateY = base.translateY;
    }

    as_Matrix2D() {
        return new proxy.Matrix2D(this.scaleX, this.scaleY, this.rotateX, this.rotateY, this.translateX, this.translateY)
    }

    identity(): Matrix2D {
        return new Matrix2D(proxy.identity(this.as_Matrix2D()));
    }
    invert(): Matrix2D {
        return new Matrix2D(proxy.invert(this.as_Matrix2D()));
    }
    multiply(other?: Matrix2D): Matrix2D {
        return new Matrix2D(proxy.multiply(this.as_Matrix2D(), other?.as_Matrix2D()));
    }
    rotate(rx?: int, ry?: int): Matrix2D {
        return new Matrix2D(proxy.rotate(this.as_Matrix2D(), rx, ry));
    }
    translate(tx?: int, ty?: int): Matrix2D {
        return new Matrix2D(proxy.translate(this.as_Matrix2D(), tx, ty));
    }
    scale(sx?: int, sy?: int): Matrix2D {
        return new Matrix2D(proxy.scale(this.as_Matrix2D(), sx, sy));
    }
}

