// ==============================================================================
// app_test.cpp — Tests for CPP Blueprint Lite Library
// Author: Christi Mahu
//
// This file contains unit tests for the math functions in the app_lib library.
// It demonstrates:
// 1. How to use the CppUnitLite testing framework
// 2. Basic test cases for mathematical functions
// 3. Test organization and structure
// ==============================================================================

#include "../extern/cppul/cppul.h"
#include "../src/app_lib/app_lib.h"

/**
 * @brief Test cases for the add function
 * 
 * This test group checks the addition function with different input scenarios:
 * - Adding positive numbers
 * - Adding negative numbers
 * - Adding numbers with different signs
 * 
 * The TEST macro comes from the CppUnitLite framework and creates a new test case.
 * The first parameter is a test name, and the second is the class or function group
 * being tested.
 */
TEST(MathFunctions, Addition) {
    // Test case 1: Positive numbers
    // Two positive numbers should add to give a positive sum
    CHECK_EQUAL(10, cmdev::app::add(5, 5));
    
    // Test case 2: Negative numbers
    // Two negative numbers should add to give a negative sum
    CHECK_EQUAL(-10, cmdev::app::add(-5, -5));
    
    // Test case 3: Mixed signs
    // Adding a positive and negative number of the same magnitude should give zero
    CHECK_EQUAL(0, cmdev::app::add(5, -5));
}

/**
 * @brief Test cases for the subtract function
 * 
 * This test group checks the subtraction function with different input scenarios:
 * - Subtracting for a positive result
 * - Subtracting for a negative result
 * - Subtracting equal numbers to get zero
 * 
 * The CHECK_EQUAL macro compares two values and fails the test if they are not equal.
 */
TEST(MathFunctions, Subtraction) {
    // Test case 1: Positive result
    // When the first number is larger, the result should be positive
    CHECK_EQUAL(5, cmdev::app::subtract(10, 5));
    
    // Test case 2: Negative result
    // When the second number is larger, the result should be negative
    CHECK_EQUAL(-5, cmdev::app::subtract(5, 10));
    
    // Test case 3: Zero result
    // Subtracting a number from itself should give zero
    CHECK_EQUAL(0, cmdev::app::subtract(5, 5));
}

/**
 * @brief Test cases for the divide function
 * 
 * This test group checks the division function with different input scenarios:
 * - Even division (no remainder)
 * - Integer division with truncation
 * - Division with negative numbers
 * 
 * Note that we don't test division by zero here, as the behavior is undefined
 * and should be handled by the caller.
 */
TEST(MathFunctions, Division) {
    // Test case 1: Even division
    // When the division is exact, we get an integer result
    CHECK_EQUAL(2, cmdev::app::divide(10, 5));
    
    // Test case 2: Integer division truncation
    // In C++, integer division truncates (rounds toward zero)
    CHECK_EQUAL(1, cmdev::app::divide(3, 2));  // 3/2 = 1.5, truncated to 1
    
    // Test case 3: Negative division
    // Dividing a negative number by a positive gives a negative result
    CHECK_EQUAL(-2, cmdev::app::divide(-10, 5));
}

/**
 * @brief Main entry point for tests
 * 
 * This function initializes the test framework and runs all registered tests.
 * The cppul::TestRunner class handles test execution and reporting, and the
 * return value indicates success (0) or failure (non-zero).
 * 
 * @return Exit code: 0 for success, non-zero for test failures
 */
int main() {
    // Run all tests and return the result
    return cppul::TestRunner::runAllTests();
}
