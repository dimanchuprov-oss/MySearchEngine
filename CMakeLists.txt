cmake_minimum_required(VERSION 3.16)

project(MySearchEngine LANGUAGES CXX)

include(CTest)

add_library(mysearchengine
    src/document_store.cpp
    src/repl.cpp
    src/text_processor.cpp
)
target_include_directories(mysearchengine PUBLIC include)
target_compile_features(mysearchengine PUBLIC cxx_std_17)

if(MSVC)
    target_compile_options(mysearchengine PRIVATE /W4 /permissive-)
else()
    target_compile_options(mysearchengine PRIVATE -Wall -Wextra -Wpedantic)
endif()

add_executable(MySearchEngine src/main.cpp)
target_link_libraries(MySearchEngine PRIVATE mysearchengine)

if(BUILD_TESTING)
    add_executable(mysearchengine_tests tests/test_main.cpp)
    target_link_libraries(mysearchengine_tests PRIVATE mysearchengine)
    add_test(NAME mysearchengine_tests COMMAND mysearchengine_tests)
endif()
