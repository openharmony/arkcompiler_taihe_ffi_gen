import {BusinessError} from "@ohos.base";
import * as poly from "poly";

loadLibrary("polymorphism");

function main() {
    let unknownObj = poly.getAnimal(poly.AnimalTag.ANIMAL);
    let dogObj = poly.getAnimal(poly.AnimalTag.DOG);
    let catObj = poly.getAnimal(poly.AnimalTag.CAT);
    poly.interactAnimal(unknownObj);
    poly.interactAnimal(dogObj);
    poly.interactAnimal(catObj);

    let unknownPer = poly.getPerson(poly.PersonTag.PERSON, "Mike", 18);
    let workerPer = poly.getPerson(poly.PersonTag.WORKER, "Tom", 30);
    let studentPer = poly.getPerson(poly.PersonTag.STUDENT, "jimmy", 20);
    poly.introduceYourself(unknownPer);
    poly.introduceYourself(workerPer);
    poly.introduceYourself(studentPer);
}