#include "integer.impl.hpp"
#include "integer.proj.hpp"
#include <iostream>

int32_t ohos_int_add(int32_t a, int32_t b) {
    return a + b;
}

int32_t ohos_int_mul(int32_t a, int32_t b) {
    if ( a * b > 20) {
        return true;
    } else {
        return false;
    }
}

float ohos_int_sub(float a, float b, bool c) {
    if (c) {
        return a - b;
    } else {
        return b;
    }
}

int32_t ohos_from_rgb(integer::RGB const& rgb) {
    return rgb.r + rgb.g + rgb.b;
}

integer::RGB ohos_to_rgb(int32_t a) {
    integer::RGB rgb{a, a/2, a/4};
    return rgb;
}

float ohos_from_color(integer::Color const& color) {
    if (color.flag) {
        return color.rgb.r + 100;
    } else {
        return color.price + 1;
    }
}

integer::Color ohos_to_color(taihe::core::string a, bool b, float c, integer::RGB d) {
    integer::Color color{a, b, c, d};
    return color;
}

integer::RGB ohos_from_theme(integer::Theme const& theme) {
    return theme.color.rgb;
}

integer::Theme ohos_to_theme(integer::Color color) {
    integer::Theme theme{color};
    return theme;
}

taihe::core::string ohos_show() {
    return "success";
}


class Student {
    protected:
        taihe::core::string id;
    public:
        Student(taihe::core::string_view id)
            : id(id) {
            std::cout << "new " << this << std::endl;
        }

        ~Student() {
            std::cout << "del " << this << std::endl;
        }

        taihe::core::string getId() {
            return id;
        }

        void setId(taihe::core::string_view s) {
            id = s;
            return;
        }
};

integer::IBase makeIBaseImpl(taihe::core::string_view id) {
    return make_holder<Student, integer::IBase>(id);
}

void copyIBaseImpl(integer::weak::IBase a, integer::weak::IBase b) {
    a.setId(b.getId());
    return;
}

TH_EXPORT_CPP_API_add(ohos_int_add)
TH_EXPORT_CPP_API_mul(ohos_int_mul)
TH_EXPORT_CPP_API_sub(ohos_int_sub)
TH_EXPORT_CPP_API_from_rgb(ohos_from_rgb)
TH_EXPORT_CPP_API_to_rgb(ohos_to_rgb)
TH_EXPORT_CPP_API_from_color(ohos_from_color)
TH_EXPORT_CPP_API_to_color(ohos_to_color)
TH_EXPORT_CPP_API_from_theme(ohos_from_theme)
TH_EXPORT_CPP_API_to_theme(ohos_to_theme)
TH_EXPORT_CPP_API_show(ohos_show)
TH_EXPORT_CPP_API_makeIBase(makeIBaseImpl)
TH_EXPORT_CPP_API_copyIBase(copyIBaseImpl)
