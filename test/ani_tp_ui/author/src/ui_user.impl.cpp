#include "ui_user.impl.hpp"
#include <iostream>
#include "stdexcept"
#include "taihe/runtime.hpp"
#include "ui_user.proj.hpp"

class AntUserDialogActionA {
public:
  AntUserDialogActionA() {}

  ::taihe::string GetName() {
    return this->name;
  }

  void SetName(::taihe::string_view name) {
    this->name = name;
  }

  ::taihe::optional<::taihe::map<::taihe::string, ::taihe::string>>
  GetTraceParams() {
    return this->traceParams;
  }

  void SetTraceParams(
      ::taihe::optional_view<::taihe::map<::taihe::string, ::taihe::string>>
          traceParams) {
    this->traceParams = traceParams;
  }

  void action() {
    std::cout << "ActionA Callback" << std::endl;
  }

private:
  ::taihe::string name = "ActionA";
  ::taihe::optional<::taihe::map<::taihe::string, ::taihe::string>>
      traceParams =
          ::taihe::optional<::taihe::map<::taihe::string, ::taihe::string>>(
              std::nullopt);
};

class AntUserDialogActionB {
public:
  AntUserDialogActionB() {}

  ::taihe::string GetName() {
    return this->name;
  }

  void SetName(::taihe::string_view name) {
    this->name = name;
  }

  ::taihe::optional<::taihe::map<::taihe::string, ::taihe::string>>
  GetTraceParams() {
    return this->traceParams;
  }

  void SetTraceParams(
      ::taihe::optional_view<::taihe::map<::taihe::string, ::taihe::string>>
          traceParams) {
    this->traceParams = traceParams;
  }

  void action() {
    std::cout << "ActionB Callback" << std::endl;
  }

private:
  ::taihe::string name = "ActionB";
  ::taihe::optional<::taihe::map<::taihe::string, ::taihe::string>>
      traceParams =
          ::taihe::optional<::taihe::map<::taihe::string, ::taihe::string>>(
              std::nullopt);
};

class AntUserDialogActionC {
public:
  AntUserDialogActionC() {}

  ::taihe::string GetName() {
    return this->name;
  }

  void SetName(::taihe::string_view name) {
    this->name = name;
  }

  ::taihe::optional<::taihe::map<::taihe::string, ::taihe::string>>
  GetTraceParams() {
    return this->traceParams;
  }

  void SetTraceParams(
      ::taihe::optional_view<::taihe::map<::taihe::string, ::taihe::string>>
          traceParams) {
    this->traceParams = traceParams;
  }

  void action() {
    std::cout << "ActionC Callback" << std::endl;
  }

private:
  ::taihe::string name = "ActionC";
  ::taihe::optional<::taihe::map<::taihe::string, ::taihe::string>>
      traceParams =
          ::taihe::optional<::taihe::map<::taihe::string, ::taihe::string>>(
              std::nullopt);
};

namespace {
void RunNativeBusiness(::ui::weak::AntUserUIProvider ui,
                       ::ui::AntUserDialogBody const &body) {
  ::ui::AntUserDialogAction actionA =
      ::taihe::make_holder<AntUserDialogActionA, ::ui::AntUserDialogAction>();
  ::ui::AntUserDialogAction actionB =
      ::taihe::make_holder<AntUserDialogActionB, ::ui::AntUserDialogAction>();
  ::ui::AntUserDialogAction actionC =
      ::taihe::make_holder<AntUserDialogActionC, ::ui::AntUserDialogAction>();
  ::taihe::array<::ui::AntUserDialogAction> actions = {actionA, actionB,
                                                       actionC};
  ::ui::AntUserModalController controller = ui->ShowDialog(body, actions);
  controller->Dismiss();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_RunNativeBusiness(RunNativeBusiness);
// NOLINTEND
