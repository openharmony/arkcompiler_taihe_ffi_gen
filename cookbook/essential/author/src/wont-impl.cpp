#include "ohos.book.store.impl.hpp"
#include "taihe/string.hpp"

using namespace taihe;
using namespace ::ohos::book::store;

// Won't Implement
namespace {
void SaveBookToInternet(string_view url) {
  TH_THROW(std::runtime_error, "SaveBookToInternet not implemented");
}

void SaveBookToFile(weak::Path p) {
  TH_THROW(std::runtime_error, "SaveBookToFile not implemented");
}

string uploadBook(Book const &b) {
  TH_THROW(std::runtime_error, "uploadBook not implemented");
}

void onBookSold() {
  TH_THROW(std::runtime_error, "onBookSold not implemented");
}

void onNewBook() {
  TH_THROW(std::runtime_error, "onNewBook not implemented");
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_SaveBookToInternet(SaveBookToInternet);
TH_EXPORT_CPP_API_SaveBookToFile(SaveBookToFile);
TH_EXPORT_CPP_API_uploadBook(uploadBook);
TH_EXPORT_CPP_API_onBookSold(onBookSold);
TH_EXPORT_CPP_API_onNewBook(onNewBook);
// NOLINTEND
