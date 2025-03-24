#include <chrono>
#include <thread>

#include "sys.time.impl.hpp"
#include "sys.time.proj.hpp"

using namespace sys::time;
using namespace taihe::core;

void setTimeoutImpl(callback_view<void()> cb, uint64_t ms) {
  std::thread([cb = callback<void()>(cb), ms]() {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
    cb();
  }).detach();
}

TH_EXPORT_CPP_API_setTimeout(setTimeoutImpl)

#include <sys/select.h>
#include <unistd.h>

#include <iostream>

    using namespace std;

void getInputWithTimeoutImpl(weak::IPromiseStringString ps, uint64_t s) {
  std::thread([ps = IPromiseStringString(ps), s]() {
    fd_set readSet;
    FD_ZERO(&readSet);
    FD_SET(STDIN_FILENO, &readSet);

    struct timeval tv = {(decltype(tv.tv_sec))s, 0};

    if (select(STDIN_FILENO + 1, &readSet, NULL, NULL, &tv) < 0) {
      perror("select");
    }

    if (FD_ISSET(STDIN_FILENO, &readSet)) {
      std::string input;
      std::cin >> input;
      ps->resolve(input);
    } else {
      ps->reject("Timeout");
    }
  }).detach();
}

TH_EXPORT_CPP_API_getInputWithTimeout(getInputWithTimeoutImpl);
