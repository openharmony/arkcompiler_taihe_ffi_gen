import * as lib from "./matrix2D"
loadLibrary("proxy_method");

function main() {
    const matrix: lib.Matrix2D = new lib.Matrix2D(1, 1, -5, 5, 10, 10); 
    const matrix_i: lib.Matrix2D = matrix.identity();
    console.log("main matrix2D identity: ", matrix.identity());
    console.log("main matrix2D invert: ", matrix.invert());
    console.log("main matrix2D multiply: ", matrix.multiply(matrix_i));
    console.log("main matrix2D multiply (no param): ", matrix.multiply());
    console.log("main matrix2D rotate: ", matrix.rotate(2, 3));
    console.log("main matrix2D translate: ", matrix.translate(4, 5));
    console.log("main matrix2D scale: ", matrix.scale(6, 7));
}
