#include "interface.impl.hpp"
#include "stdexcept"
#include "interface.ICalculator.proj.2.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {

class ICalculator {
public:
    ICalculator(int32_t init): lastResult(init) {}
    int32_t add(int32_t a, int32_t b) {
        lastResult = a + b;
        return lastResult;
    }
    int32_t sub(int32_t a, int32_t b) {
        lastResult = a - b;
        return lastResult;
    }
    int32_t getLastResult() {
        return lastResult;
    }
    void reset() {
        lastResult = 0;
    }
private:
    int32_t lastResult = 0;
};

::interface::ICalculator makeCalculator(int32_t init) {
    return make_holder<ICalculator, ::interface::ICalculator>(init);
}
void restartCalculator(::interface::weak::ICalculator a) {
    a->reset();
}

}

TH_EXPORT_CPP_API_makeCalculator(makeCalculator)
TH_EXPORT_CPP_API_restartCalculator(restartCalculator)
