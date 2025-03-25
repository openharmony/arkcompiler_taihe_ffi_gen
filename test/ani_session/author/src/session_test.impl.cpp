#include "session_test.impl.hpp"

#include <cstdint>
#include <iostream>

#include "session_test.IfaceD.proj.2.hpp"
using namespace taihe::core;
namespace {
class IfaceA {
 public:
  void func_a() {
    throw std::runtime_error("Function IfaceA::func_a Not implemented");
  }
};
class IfaceB {
 public:
  void func_b() {
    throw std::runtime_error("Function IfaceB::func_b Not implemented");
  }
  void func_a() {
    throw std::runtime_error("Function IfaceB::func_a Not implemented");
  }
};
class IfaceC {
 public:
  void func_c() {
    throw std::runtime_error("Function IfaceC::func_c Not implemented");
  }
  void func_a() {
    throw std::runtime_error("Function IfaceC::func_a Not implemented");
  }
};
class IfaceD {
 public:
  string func_d() { return "d"; }
  string func_b() { return "b"; }
  string func_a() { return "a"; }
  string func_c() { return "c"; }
};
::session_test::IfaceD getIfaceD() {
  return make_holder<IfaceD, ::session_test::IfaceD>();
}
class Session {
 public:
  void beginConfig() {
    throw std::runtime_error("Function Session::beginConfig Not implemented");
  }
};
class PhotoSession {
 public:
  bool canPreconfig() { return true; }
  void beginConfig() { std::cout << "PhotoSession" << std::endl; }
  string func_a() {
    std::cout << "func_a in PhotoSession" << std::endl;
    return "psa";
  }
  string func_c() {
    std::cout << "func_c in PhotoSession" << std::endl;
    return "psc";
  }
};
class VideoSession {
 public:
  bool canPreconfig() { return true; }
  void beginConfig() { std::cout << "VideoSession" << std::endl; }
  string func_a() {
    std::cout << "func_a in VideoSession" << std::endl;
    return "vsa";
  }
  string func_c() {
    std::cout << "func_c in VideoSession" << std::endl;
    return "vsc";
  }
};
::session_test::session_type getSession(int32_t ty) {
  if (ty == 1) {
    return ::session_test::session_type::make_ps(
        make_holder<PhotoSession, ::session_test::PhotoSession>());
  } else {
    return ::session_test::session_type::make_vs(
        make_holder<VideoSession, ::session_test::VideoSession>());
  }
}
}  // namespace
TH_EXPORT_CPP_API_getIfaceD(getIfaceD);
TH_EXPORT_CPP_API_getSession(getSession);
