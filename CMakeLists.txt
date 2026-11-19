cmake_minimum_required(VERSION 3.22)
project(FolkInstruments VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

option(FOLK_BUILD_PLUGINS "Build the five JUCE plugins (VST3 and Standalone)" ON)
option(FOLK_BUILD_TESTS "Build the Catch2 tests" ON)
set(FOLK_JUCE_DIR "" CACHE PATH "Existing JUCE checkout at the pinned commit; empty means fetch it")
set(FOLK_JUCE_COMMIT dabd5ad13cd869cba41046947fffc8e5ce5cd662)   # tag 8.0.17-security
set(FOLK_CATCH2_COMMIT 08092139210881f01a34e60c5f2fd6afa0ea4024) # tag v3.16.1

include(FetchContent)

add_library(folkdsp STATIC core/src/stubs.cpp core/src/strings.cpp core/src/tuning.cpp core/src/engine_base.cpp core/src/reed.cpp core/src/reed_engine.cpp core/src/harmonica.cpp)
target_include_directories(folkdsp PUBLIC core/include)
if(MSVC)
  target_compile_options(folkdsp PRIVATE /W4 /permissive-)
  target_compile_definitions(folkdsp PUBLIC _USE_MATH_DEFINES)
else()
  target_compile_options(folkdsp PRIVATE -Wall -Wextra -Wpedantic)
endif()

add_executable(folk-render tools/folk-render/main.cpp)
target_link_libraries(folk-render PRIVATE folkdsp)

add_executable(reed_probe tools/reed_probe.cpp)
target_link_libraries(reed_probe PRIVATE folkdsp)

if(FOLK_BUILD_TESTS)
  FetchContent_Declare(Catch2 GIT_REPOSITORY https://github.com/catchorg/Catch2.git GIT_TAG ${FOLK_CATCH2_COMMIT})
  FetchContent_MakeAvailable(Catch2)
  add_executable(folk-tests tests/cpp/test_tuning.cpp tests/cpp/test_strings.cpp tests/cpp/test_engine.cpp)
  target_link_libraries(folk-tests PRIVATE folkdsp Catch2::Catch2WithMain)
  add_executable(folk-locale-tests tests/cpp/test_locale.cpp)
  target_link_libraries(folk-locale-tests PRIVATE folkdsp Catch2::Catch2WithMain)
  add_executable(folk-perf tests/cpp/test_perf.cpp)
  target_link_libraries(folk-perf PRIVATE folkdsp Catch2::Catch2WithMain)
  if(MSVC)
    target_compile_definitions(folk-tests PRIVATE _USE_MATH_DEFINES)
  endif()
  enable_testing()
  add_test(NAME folk-tests COMMAND folk-tests)
  add_test(NAME folk-locale-tests COMMAND folk-locale-tests)
  add_test(NAME folk-perf COMMAND folk-perf)
  set_tests_properties(folk-perf PROPERTIES LABELS perf)
endif()

if(FOLK_BUILD_PLUGINS)
  add_subdirectory(plugins)
endif()
