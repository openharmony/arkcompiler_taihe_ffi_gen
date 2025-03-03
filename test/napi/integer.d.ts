import { RGB, Color, Theme, IBase, IShape, ColorOrRGBOrName } from "./rgb"

export function add(a: number, b: number): number;
export function mul(a: number, b: number): boolean;
export function sub(a: number, b: number, c: boolean): number;
export function to_rgb(a: number): RGB;
export function from_rgb(a: RGB): number;
export function makeRGB(r:number, g:number, b:number): RGB;
export function makeColor(a: String): Color;
export function from_color(color: Color): number;
export function to_color(a: String, b: boolean, c: number, d: RGB): Color;
export function makeTheme(a: Color, b: IBase): Theme;
export function from_theme(theme: Theme): RGB;
export function to_theme(a: Color, b: IBase): Theme;
export function show(): String;
export function makeIBase(s: String): IBase;
export function copyIBase(a: IBase, b: IBase);
export function makeIShape(s: String, a: number, b: number): IShape;
export function as_IShape(a: IBase): IShape;
export function impl_IBase(a: any): IBase;
export function process_color_rgb_name(a: ColorOrRGBOrName): ColorOrRGBOrName;
