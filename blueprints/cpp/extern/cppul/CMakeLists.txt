# ==============================================================================
# CMakeLists.txt for CppUnitLite Wrapper (cppul)
# Author: Christi Mahu
#
# PURPOSE:
# This file builds the CppUnitLite wrapper as a dynamic library.
# ==============================================================================

cmake_minimum_required(VERSION 3.14)
project(cppul VERSION 1.0.0 LANGUAGES CXX)

# Build the CppUnitLite test framework as a shared/dynamic library
add_library(cppul SHARED
    cpp_unit_lite_basic/CppUnitLite/Failure.cpp
    cpp_unit_lite_basic/CppUnitLite/Test.cpp
    cpp_unit_lite_basic/CppUnitLite/TestRegistry.cpp
    cpp_unit_lite_basic/CppUnitLite/TestResult.cpp
    cpp_unit_lite_basic/CppUnitLite/WFailure.cpp
)

# Make sure the include paths are correct
target_include_directories(cppul 
    PUBLIC 
        ${CMAKE_CURRENT_SOURCE_DIR}/cpp_unit_lite_basic/include
        ${CMAKE_CURRENT_SOURCE_DIR}/cpp_unit_lite_basic/include/CppUnitLite
        ${CMAKE_CURRENT_SOURCE_DIR}  # For cppul.h
)

# Apply C++23 standard
target_compile_features(cppul PUBLIC cxx_std_23)

# Set output directories
set_target_properties(cppul PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

message(STATUS "CppUL Wrapper configured as dynamic library")
message(STATUS "Library will be built to: ${CMAKE_BINARY_DIR}/lib")
