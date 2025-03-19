import * as IfaceTest from "../author_generated/iface_test"

loadLibrary("ani_iface")

class SubFoo implements IfaceTest.Foo {
    bar(): void {}

    name: string = "";
}

interface Person {
    get name(): string;
}

class SubPerson implements Person {
    readonly name: string = "";
}

function main() {
    console.log("run main ... IfaceTest ...")

    let foo = IfaceTest.getFooIface();
    console.log("foo.name is " + foo.name)

    foo.name = "alice"
    console.log("foo.name is " + foo.name)

    foo.name = "bob"
    IfaceTest.printFooName(foo)

    let subFoo = new SubFoo()
    subFoo.name = "aaa"
    console.log("subFoo.name is " + subFoo.name)
}