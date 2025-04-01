#include "ohos.book.store.impl.hpp"
#include <cstdint>
#include "ohos.book.store.Book.proj.1.hpp"
#include "ohos.book.store.Category.proj.0.hpp"
#include "ohos.book.store.CppOrRustBook.proj.1.hpp"
#include "ohos.book.store.MapOption.proj.1.hpp"
#include "taihe/array.hpp"
#include "taihe/callback.hpp"
#include "taihe/map.hpp"
#include "taihe/optional.hpp"
#include "taihe/runtime.hpp"
#include "taihe/string.hpp"

using namespace taihe;
using namespace ::ohos::book::store;

namespace {
Book ConstructBook(string_view title, int32_t year, Category kind) {
  // 使用 Modern C++ 初始化结构体。
  return Book{title, year, kind};
}

void PrintBook(Book const& b) {
  printf("PrintBook: %s, year %d, kind = %s\n",
         b.title.c_str(),  // 使用 taihe::string::c_str() 获取字符串。
         b.year,
         b.category.get_value()  // 使用 enum 类型的 get_value() 获取绑定的值。
  );
}

map<string, int32_t> MapBookToYear(MapOption const& opt) {
  map<string, int32_t> ret;
  // 通过 get_tag() 判断类型，通过 get_xxx_ref() 获得对应的值。
  if (opt.get_tag() == MapOption::tag_t::one_book) {
    Book const& book = opt.get_one_book_ref();
    ret.emplace(book.title, book.year);
  } else {
    // 使用标准的 STL 风格访问 many_books 数组。
    for (auto const& book : opt.get_many_books_ref()) {
      ret.emplace(book.title, book.year);
    }
  }
  return ret;
}

void PrintBooksWithFilter(array_view<Book> books,
                          optional_view<callback<bool(Book const&)>> filter) {
  for (auto& book : books) {
    bool should_print = true;
    // 判断 Optional 是否有值。
    if (filter) {
      // 使用 (*filter) 获取 filter 背后的 callback，并调用 callback。
      should_print = (*filter)(book);
    }

    // Taihe 导出的函数和普通函数没什么差别，可以随意调用。
    if (should_print) PrintBook(book);
  }
}

class BookstoreImpl {
  double m_discount_percent = 0.0f;
  double m_total_sales = 0.0f;
  std::unordered_map<std::string, std::pair<double, int32_t>> m_books = {};

public:
  void addBook(Book const& book, double price, int32_t count) {
    m_books.emplace(std::string{book.title}, std::make_pair(price, count));
    PrintBook(book);
    printf("addBook: price = %lf, count = %d\n", price, count);
  }

  void saleBook(Book const& book) {
    auto iter = m_books.find(std::string{book.title});
    auto price = iter->second.first;
    auto& count = iter->second.second;
    if (count == 0) {
      // 使用 taihe::set_error 抛异常。
      taihe::set_error(book.title + " has been sold out");
      return;
    }

    count -= 1;
    m_total_sales += price * (1 - m_discount_percent / 100);

    printf("saleBook: price = %lf, count = %d, title = %s\n", price, count,
           book.title.c_str());
  }

  double getDiscount() {
    return m_discount_percent;
  }

  void setDiscount(double percent) {
    m_discount_percent = percent;
  }

  double getTotalSales() {
    return m_total_sales;
  }
};

Bookstore CreateBookstore() {
  return make_holder<BookstoreImpl, Bookstore>();
}

void SayHello() {
  printf("Welcome to my book store!\n");
}

void PrintBookAdvanced(CppOrRustBook const& book) {
  if (book.holds_rust()) {
    RustBook the_book = book.get_rust_ref();
    PrintBook(the_book.base);
    printf("Hint: use Rust edition %d to try.\n", the_book.rust_version);
  }
  if (book.holds_cpp()) {
    CppBook the_book = book.get_cpp_ref();
    PrintBook(the_book.base);
    printf("Hint: use %s to compile.\n", the_book.compiler.c_str());
  }
}

FancyBook MakeFancyBook() {
  // 内部临时写一个类吧！只要函数都具备，就可以转换到 Taihe 对象。
  struct FancyRustBook {
    string getPublisher() {
      return "No Starch Press";
    }

    string getTitle() {
      return "The Rust Programming Language";
    }

    double getDiscount() {
      return 0.0 /* No discount, sorry.*/;
    }

    double getPrice() {
      return 50.0;
    }
  };

  // 把这个类包装为 Taihe 对象。
  // 注意，这里的 class 只实现了与之相关的 FancyBook 接口。
  return make_holder<FancyRustBook, FancyBook>();
}

bool IsString(uintptr_t s) {
  ani_boolean res;
  ani_class cls;
  ani_env* env = get_env();
  env->FindClass("Lstd/core/String;", &cls);
  env->Object_InstanceOf((ani_object)s, cls, &res);
  return res;
}

array<uintptr_t> GetStringArray() {
  ani_env* env = get_env();
  // 首个元素为字符串 "AAA"
  ani_string ani_arr_0;
  env->String_NewUTF8("AAA", 3, &ani_arr_0);
  // 接下来的元素为 undefined
  ani_ref ani_arr_1;
  env->GetUndefined(&ani_arr_1);
  return array<uintptr_t>({(uintptr_t)ani_arr_0, (uintptr_t)ani_arr_1});
}
}  // namespace

TH_EXPORT_CPP_API_ConstructBook(ConstructBook);
TH_EXPORT_CPP_API_PrintBook(PrintBook);
TH_EXPORT_CPP_API_MapBookToYear(MapBookToYear);
TH_EXPORT_CPP_API_PrintBooksWithFilter(PrintBooksWithFilter);
TH_EXPORT_CPP_API_CreateBookstore(CreateBookstore);
TH_EXPORT_CPP_API_SayHello(SayHello);
TH_EXPORT_CPP_API_PrintBookAdvanced(PrintBookAdvanced);
TH_EXPORT_CPP_API_MakeFancyBook(MakeFancyBook);
TH_EXPORT_CPP_API_IsString(IsString);
TH_EXPORT_CPP_API_GetStringArray(GetStringArray);
