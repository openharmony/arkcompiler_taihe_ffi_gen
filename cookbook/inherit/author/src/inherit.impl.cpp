/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// This file is a test file.
// NOLINTBEGIN
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
    PayableImpl(double num)
    {
    }

    void pay(double amountDue)
    {
    }

private:
};

class CreditCardImpl {
public:
    CreditCardImpl(double num) : amount(num)
    {
    }

    void topUp(double topUpAmount)
    {
        this->amount += topUpAmount;
    }

    double getBalance()
    {
        return this->amount;
    }

    void pay(double amountDue)
    {
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
};

CreditCard makeCreditCard(double initAmount)
{
    return make_holder<CreditCardImpl, CreditCard>(initAmount);
}
}  // namespace

TH_EXPORT_CPP_API_makeCreditCard(makeCreditCard);
// NOLINTEND
