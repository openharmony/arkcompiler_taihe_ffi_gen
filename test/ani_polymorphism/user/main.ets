import {BusinessError} from "@ohos.base";
import * as poly from "poly";

loadLibrary("ani_polymorphism");

function iface_poly_test() {
    let unknownObj = poly.getAnimal(poly.AnimalTag.ANIMAL);
    let dogObj = poly.getAnimal(poly.AnimalTag.DOG);
    let catObj = poly.getAnimal(poly.AnimalTag.CAT);
    arktest.assertEQ(poly.interactAnimal(unknownObj), "Unknown Animal");
    arktest.assertEQ(poly.interactAnimal(dogObj), "Dog");
    arktest.assertEQ(poly.interactAnimal(catObj), "Cat");
}

function struct_poly_test() {
    let unknownPer = poly.getPerson(poly.PersonTag.PERSON, "Mike", 18);
    let workerPer = poly.getPerson(poly.PersonTag.WORKER, "Tom", 30);
    let studentPer = poly.getPerson(poly.PersonTag.STUDENT, "jimmy", 20);
    arktest.assertEQ(poly.introduceYourself(unknownPer), "Unknown Person");
    arktest.assertEQ(poly.introduceYourself(workerPer), "Worker");
    arktest.assertEQ(poly.introduceYourself(studentPer), "Student");
}

function main() {
    const suite = new arktest.ArkTestsuite("Polymorphism Test");
    suite.addTest("iface_poly_test", iface_poly_test);
    suite.addTest("struct_poly_test", struct_poly_test);
    exit(suite.run());
}