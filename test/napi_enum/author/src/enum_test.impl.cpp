#include "enum_test.impl.hpp"
#include "enum_test.proj.hpp"

namespace {
static constexpr std::size_t COLOR_COUNT = 3;
static constexpr std::size_t WEEKDAY_COUNT = 7;
static constexpr std::size_t NUMTYPEI8_COUNT = 3;
static constexpr std::size_t NUMTYPEI16_COUNT = 3;
static constexpr std::size_t NUMTYPEI32_COUNT = 3;
static constexpr std::size_t NUMTYPEI64_COUNT = 3;
static constexpr std::size_t BOOL_COUNT = 3;

::enum_test::Color nextEnum(::enum_test::Color color) {
  return (::enum_test::Color::key_t)(((int)color.get_key() + 1) % COLOR_COUNT);
}

taihe::string getValueOfEnum(::enum_test::Color color) {
  return color.get_value();
}

::enum_test::Color fromValueToEnum(::taihe::string_view name) {
  auto color = ::enum_test::Color::from_value(name);
  return color;
}

::enum_test::Weekday nextEnumWeekday(::enum_test::Weekday day) {
  return (::enum_test::Weekday::key_t)(((int)day.get_key() + 1) %
                                       WEEKDAY_COUNT);
}

int32_t getValueOfEnumWeekday(::enum_test::Weekday day) {
  return day.get_value();
}

::enum_test::Weekday fromValueToEnumWeekday(int day) {
  auto weekday = ::enum_test::Weekday::from_value(day);
  return weekday;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_nextEnum(nextEnum);
TH_EXPORT_CPP_API_getValueOfEnum(getValueOfEnum);
TH_EXPORT_CPP_API_fromValueToEnum(fromValueToEnum);
TH_EXPORT_CPP_API_nextEnumWeekday(nextEnumWeekday);
TH_EXPORT_CPP_API_getValueOfEnumWeekday(getValueOfEnumWeekday);
TH_EXPORT_CPP_API_fromValueToEnumWeekday(fromValueToEnumWeekday);
// NOLINTEND
