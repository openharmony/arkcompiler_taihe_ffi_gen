import * as lib from "maythrow";

function main() {
    try {
        let res = lib.maythrow(0);
        console.log('Success:', res);
    } catch (error) {
        console.error('maythrow Error caught:', error.message);
    }

    try {
        let res = lib.maythrow(1);
        console.log('Success:', res);
    } catch (error) {
        console.error('maythrow Error caught:', error.message);
    }

    try {
        let res = lib.getDataMaythrow();
        console.log('Success:', res);
    } catch (error) {
        console.error('getDataMaythrow Error caught:', error.message);
    }

    try {
        lib.noReturnMaythrow();
    } catch (error) {
        console.error('noReturnMaythrow Error caught:', error.message);
    }

    try {
        lib.noReturnTypeError();
    } catch (error) {
        console.error('noReturnTypeError Error caught:', error.message, error.code);
    }
    
    try {
        lib.noReturnRangeError();
    } catch (error) {
        console.error('noReturnRangeError Error caught:', error.message, error.code);
    }
}

main()