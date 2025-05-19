import {Book, Bookstore, Category, ConstructBook, CppBook, FancyBook, GetStringArray, IsString, MapBookToYear, PrintBook, PrintBookAdvanced, PrintBooksWithFilter, RustBook} from "ohos.book.store";
import {BusinessError} from "@ohos.base";

loadLibrary("essential");

function main() {
    let book_cpp0 = ConstructBook("C++ Primer (5th ed.)", 2012, Category.CPP);
    let book_cpp1 = ConstructBook("Effective C++", 1997, Category.CPP);
    let book_rust0: Book = {
        title: "The Rust Programming Language",
        year: 2018,
        category: Category.RUST
    };
    let book_rust1: Book = {
        title: "Rust for Rustaceans",
        year: 2021,
        category: Category.RUST
    };
    let all_books: Book[] = [book_cpp0, book_cpp1, book_rust0, book_rust1];

    console.log("All books:");
    for (let i = 0; i < all_books.length; ++i) {
        PrintBook(all_books[i]);
    }
    console.log("");

    console.log("Book mapping:");
    for (let pair of MapBookToYear(all_books)) {
        console.log("Year " + pair[1] + ": " + pair[0]);
    }
    console.log("");

    console.log("Books of Rust:");
    PrintBooksWithFilter(all_books, (b: Book) => {
        return b.category == Category.RUST;
    });
    console.log("");

    Bookstore.SayHello();
    let store = new Bookstore();
    store.addBook(book_rust0, 20.0, 2);

    store.discount = 50;  // 打五折
    store.saleBook(book_rust0);
    console.log("Total sales: " + store.totalSales)
    store.discount = 20;  // 打八折
    store.saleBook(book_rust0);
    console.log("Total sales: " + store.totalSales)

    try {
        // 卖光了，不能再卖了。
        store.saleBook(book_rust0);
    } catch (error) {
        console.log("error: " + error);
    }
    console.log("");

    PrintBookAdvanced(new RustBook(
        "The Rust Programming Language", 2018, Category.RUST, 2018));
    PrintBookAdvanced(
        new CppBook("Effective C++", 1997, Category.CPP, "Borland C++"));
    console.log("");

    let fancy_book = new FancyBook();
    console.log(
        `Got a fancy book: ${fancy_book.title} by ${fancy_book.publisher},` +
        ` costs \$${fancy_book.price} with discount ${fancy_book.discount}%`);
    console.log("");

    const s = "hello";
    const i = 233;
    console.log(`${s} is string? ${IsString(s)}`);
    console.log(`${i} is string? ${IsString(i)}`);
    console.log(`GetStringArray = ${GetStringArray()}`);
}
