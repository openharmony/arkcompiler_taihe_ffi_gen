import { RGB, Color, Theme } from "./rgb"

export function add(a: number, b: number): number;
export function mul(a: number, b: number): boolean;
export function sub(a: number, b: number, c: boolean): number;
export function to_rgb(a: number): RGB;
export function from_rgb(a: RGB): number;
export function make_RGB(r:number, g:number, b:number): RGB;
export function make_Color(a: String): Color;
export function from_color(color: Color): number;
export function to_color(a: String, b: boolean, c: number, d: RGB): Color;
export function make_Theme(a: Color): Theme;
export function from_theme(theme: Theme): RGB;
export function to_theme(a: Color): Theme;
