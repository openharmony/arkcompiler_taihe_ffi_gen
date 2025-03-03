export class RGB {
    constructor(r: number, g: number, b: number){
      this.r = r;
      this.g = g;
      this.b = b;
    }
    r: number;
    g: number;
    b: number;
  }

export class Color {
  constructor(name: string, flag: boolean, price: number, rgb: RGB){
    this.name = name;
    this.flag = flag;
    this.price = price;
    this.rgb = rgb;
  }
  name: string;
  flag: boolean;
  price: number;
  rgb: RGB;
}

export class Theme {
  constructor(color: Color) {
    this.color = color;
  }
  color: Color;
  ibase: IBase;
}

export interface IBase {
  getId(): String;
  setId(id: String): void;
}

export interface IShape extends IBase {
  calculateArea(): number;
  as_IBase();
}

export type ColorOrRGBOrName =
  | { readonly tag: ColorOrRGBOrName.tags.undefined }
  | { readonly tag: ColorOrRGBOrName.tags.color; readonly value: Color }
  | { readonly tag: ColorOrRGBOrName.tags.rgb; readonly value: RGB }
  | { readonly tag: ColorOrRGBOrName.tags.name; readonly value: string };

export namespace ColorOrRGBOrName {
  export enum tags {
    undefined = 0,
    color = 1,
    rgb = 2,
    name = 3,
  }
  export namespace ctor {
    undefined: () => { return { tag: ColorOrRGBOrName.tags.undefined } }
    color: (value: Color) => { return { tag: ColorOrRGBOrName.tags.color, value: value } }
    rgb: (value: RGB) => { return { tag: ColorOrRGBOrName.tags.rgb, value: value }}
    name: (value: string) => {return { tag: ColorOrRGBOrName.tags.rgb, value: value }}
  }
}
