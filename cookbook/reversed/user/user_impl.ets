"use static";

import * as impl_taihe from "impl";

export interface IfaceA {
    foo(): string;
    bar(): int;
}

export class ClassA implements IfaceA, impl_taihe.IfaceA_taihe {
    name: string = "";
    age: int;

    constructor(name: string, age: int) {
        this.name = name;
        this.age = age;
    }

    foo(): string {
        return this.name;
    }

    bar(): int {
        return this.age;
    }
}
