#include "inherit.impl.hpp"
#include <iostream>
#include "inherit.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace inherit;

namespace {

class PayableImpl {
public:
  PayableImpl(double num) {}

  void pay(double amountDue) {}

private:
};

class CreditCardImpl {
public:
  CreditCardImpl(double num) : amount(num), IntlEnabled(false) {}

  void topUp(double topUpAmount) {
    this->amount += topUpAmount;
  }

  double getBalance() {
    return this->amount;
  }

  bool getIntlEnabled() {
    return this->IntlEnabled;
  }

  void setIntlEnabled(bool tag) {
    this->IntlEnabled = tag;
  }

  void pay(double amountDue) {
    if (amountDue > this->amount) {
      std::cout << "Insufficient balance" << std::endl;
      return;
    }
    this->amount -= amountDue;
    std::cout << "Payment successful" << std::endl;
    return;
  }

private:
  double amount;
  bool IntlEnabled;
};

CreditCard makeCreditCard(double initAmount) {
  return make_holder<CreditCardImpl, CreditCard>(initAmount);
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeCreditCard(makeCreditCard);
// NOLINTEND
