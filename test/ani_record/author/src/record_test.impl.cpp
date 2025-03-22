#include "record_test.impl.hpp"
#include "stdexcept"
#include "record_test.ICpu.proj.2.hpp"
#include "core/map.hpp"
#include "core/string.hpp"
#include "core/array.hpp"
#include "record_test.Data.proj.1.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class ICpu {
public:
    int32_t add(int32_t a, int32_t b) {
        return a + b;
    }
    int32_t sub(int32_t a, int32_t b) {
        return a - b;
    }
};
::record_test::ICpu makeCpu() {
    return make_holder<ICpu, ::record_test::ICpu>();
}
int32_t getCpuSize(map_view<string, ::record_test::ICpu> r) {
    return r.size();
}
int32_t getASize(map_view<int32_t, uintptr_t> r) {
    return r.size();
}
int32_t getStringIntSize(map_view<string, int32_t> r) {
    return r.size();
}
map<string, string> createStringString(int32_t a) {
    map<string, string> m;
    while (a--) {
        m.emplace(to_string(a), "abc");
    }
    return m;
}
map<string, int32_t> getMapfromArray(array_view<::record_test::Data> d) {
    map<string, int32_t> m;
    for (int i = 0; i < d.size(); ++i) {
        m.emplace(d[i].a, d[i].b);
    }
    return m;
}
::record_test::Data getDatafromMap(map_view<string, ::record_test::Data> m, string_view k) {
    auto iter = m.find(k);
    if (iter == nullptr) {
        return {"su", 7};
    }
    return {iter->a, iter->b};
}
void foreachMap(map_view<string, string> my_map) {
    std::cout << "Using begin() and end() for traversal:" << std::endl;
    for (auto it = my_map.begin(); it != my_map.end(); ++it) {
        const auto& [key, value] = *it;
        std::cout << "Key: " << key << ", Value: " << value << std::endl;
    }

    std::cout << "Using range-based for loop for traversal:" << std::endl;
    for (const auto& [key, value] : my_map) {
        std::cout << "Key: " << key << ", Value: " << value << std::endl;
    }

    std::cout << "Using const iterator for traversal:" << std::endl;
    const auto& const_map = my_map;
    for (auto it = const_map.begin(); it != const_map.end(); ++it) {
        const auto& [key, value] = *it;
        std::cout << "Key: " << key << ", Value: " << value << std::endl;
    }

    std::cout << "Using cbegin() and cend() for traversal:" << std::endl;
    for (auto it = my_map.cbegin(); it != my_map.cend(); ++it) {
        const auto& [key, value] = *it;
        std::cout << "Key: " << key << ", Value: " << value << std::endl;
    };
}
}
TH_EXPORT_CPP_API_makeCpu(makeCpu)
TH_EXPORT_CPP_API_getCpuSize(getCpuSize)
TH_EXPORT_CPP_API_getASize(getASize)
TH_EXPORT_CPP_API_getStringIntSize(getStringIntSize)
TH_EXPORT_CPP_API_createStringString(createStringString)
TH_EXPORT_CPP_API_getMapfromArray(getMapfromArray)
TH_EXPORT_CPP_API_getDatafromMap(getDatafromMap)
TH_EXPORT_CPP_API_foreachMap(foreachMap)
