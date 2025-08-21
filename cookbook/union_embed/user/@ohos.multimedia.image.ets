export interface Image {
    name: string;
    getage(): int;
}

export class Image_inner implements Image {
    name: string = "leo"
    getage(): int {
        return 10;
    }
}