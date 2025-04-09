// ==============================================================================
// cppul.h — Modern C++ Wrapper for CppUnitLite
// Author: Christi Mahu
//
// This header provides a clean, modern interface to the CppUnitLite testing
// framework. It encapsulates the original framework and exposes only what's
// needed for writing tests, allowing the underlying implementation to be
// changed without affecting test code.
// ==============================================================================

#ifndef CPPUL_H
#define CPPUL_H

// Include the underlying CppUnitLite headers
// These are kept hidden from client code that only includes cppul.h
#include "cpp_unit_lite_basic/include/CppUnitLite/TestHarness.h"

/**
 * @mainpage CppUL - Modern C++ Wrapper for CppUnitLite
 *
 * @section intro_sec Introduction
 * CppUL is a clean, modern wrapper around the CppUnitLite testing framework.
 * It provides a simplified interface that makes writing tests more intuitive
 * while allowing the underlying implementation to be swapped out if needed.
 *
 * @section usage_sec Basic Usage
 * @code
 * #include "extern/cppul/cppul.h"
 *
 * // Define a simple test
 * TEST(MathFunctions, Addition) {
 *     // Arrange
 *     const auto a = 2;
 *     const auto b = 3;
 *
 *     // Act
 *     const auto result = a + b;
 *
 *     // Assert
 *     CHECK_EQUAL(5, result);
 * }
 *
 * // Main function to run tests
 * int main() {
 *     return cppul::TestRunner::runAllTests();
 * }
 * @endcode
 *
 * @section features_sec Key Features
 * - Simplified test writing with familiar TEST macros
 * - Additional helpers for common testing patterns
 * - Support for test fixtures with setup/teardown
 * - Modern C++ design with auto return types and templates
 */

// =============================================================================
// Re-export necessary functionality from CppUnitLite
// =============================================================================

// We're using the original macros from CppUnitLite to maintain compatibility,
// but we're wrapping the other functionality in our own namespace.

/**
 * @brief TestResult class for tracking test outcomes
 *
 * The TestResult class collects information about test runs,
 * including successes and failures. It's used by the TestRunner
 * to execute tests and report results.
 *
 * This is re-exported from the underlying CppUnitLite framework.
 */
using TestResult = ::TestResult;

/**
 * @namespace cppul
 * @brief Main namespace for the CppUL testing framework
 *
 * This namespace contains all the additional functionality
 * provided by the CppUL wrapper, beyond the basic macros
 * inherited from CppUnitLite.
 */
namespace cppul {
    /**
     * @brief Utility class for running tests
     *
     * TestRunner provides methods for executing all registered tests
     * and obtaining the test results. Use this in your main() function
     * to run all tests defined with the TEST macro.
     *
     * Example:
     * @code
     * int main() {
     *     return cppul::TestRunner::runAllTests();
     * }
     * @endcode
     */
    class TestRunner {
    public:
        /**
         * @brief Run all registered tests with a default TestResult
         *
         * This method creates a TestResult instance and runs all tests
         * that have been registered with the TEST macro.
         *
         * @return int Exit code (0 for success, non-zero for failures)
         */
        static auto runAllTests() -> int {
            // Create a TestResult to collect test outcomes
            TestResult tr;
            
            // Run all tests that were registered with the TEST macro
            // The underlying TestRegistry handles finding and executing tests
            TestRegistry::runAllTests(tr);
            
            // Return the failure count as exit code
            return tr.getFailureCount();
        }
        
        /**
         * @brief Run all tests with a specific TestResult instance
         *
         * This overload allows you to provide your own TestResult
         * instance, which can be useful if you need to customize
         * how test results are collected or reported.
         *
         * @param tr The TestResult instance to use
         * @return int Exit code (0 for success, non-zero for failures)
         */
        static auto runAllTests(TestResult& tr) -> int {
            // Run the tests with the provided TestResult
            TestRegistry::runAllTests(tr);
            
            // Return the failure count as exit code
            return tr.getFailureCount();
        }
    };
}

// =============================================================================
// Additional utility functions that extend CppUnitLite
// =============================================================================

namespace cppul {
    /**
     * @brief Base class for test fixtures
     *
     * TestFixture provides a foundation for creating reusable test
     * setup and teardown logic. Derive from this class to create
     * your own test fixtures that automatically run setup before each
     * test and teardown after each test.
     *
     * Example:
     * @code
     * class DatabaseTest : public cppul::TestFixture {
     * protected:
     *     Database db;
     *
     *     auto setUp() -> void override {
     *         db.connect("test_db");
     *     }
     *
     *     auto tearDown() -> void override {
     *         db.disconnect();
     *     }
     * };
     * @endcode
     */
    class TestFixture {
    public:
        /**
         * @brief Default constructor
         *
         * The constructor runs before each test.
         */
        TestFixture() = default;
        
        /**
         * @brief Virtual destructor
         *
         * The destructor runs after each test, ensuring proper
         * cleanup of derived fixture classes.
         */
        virtual ~TestFixture() = default;
        
        /**
         * @brief Setup method called before each test
         *
         * Override this method in your fixture class to perform
         * setup operations before each test runs. This is useful
         * for initializing resources or setting up test conditions.
         */
        virtual auto setUp() -> void {}
        
        /**
         * @brief Teardown method called after each test
         *
         * Override this method in your fixture class to perform
         * cleanup operations after each test runs. This is useful
         * for releasing resources or restoring state.
         */
        virtual auto tearDown() -> void {}
    };
    
    /**
     * @brief Check if two floating-point values are close within a tolerance
     *
     * This helper simplifies floating-point comparisons, which should
     * never use exact equality due to precision limitations.
     *
     * Example:
     * @code
     * const auto result = calculatePi();
     * if (cppul::checkClose(3.14159, result, 0.0001)) {
     *     // Values are close enough
     * }
     * @endcode
     *
     * @tparam T The floating-point type (float, double, etc.)
     * @param expected The expected value
     * @param actual The actual value
     * @param tolerance The maximum allowable difference
     * @return bool True if the values are within tolerance of each other
     */
    template <typename T>
    auto checkClose(T expected, T actual, T tolerance) -> bool {
        // Calculate the absolute difference
        const auto diff = expected - actual;
        
        // Check if difference is within tolerance range
        return (diff >= -tolerance && diff <= tolerance);
    }
    
    /**
     * @brief Check if a function throws the expected exception type
     *
     * This helper verifies that a function throws a specific exception type,
     * which is a common pattern in testing error handling.
     *
     * Example:
     * @code
     * // Check that dividing by zero throws a DivideByZeroError
     * auto divideByZero = []() { return 5 / 0; };
     * CHECK(cppul::checkThrows<DivideByZeroError>(divideByZero));
     * @endcode
     *
     * @tparam ExceptionType The type of exception expected
     * @tparam Func The function type (deduced automatically)
     * @param func The function to test (typically a lambda)
     * @return bool True if the function throws the expected exception
     */
    template <typename ExceptionType, typename Func>
    auto checkThrows(Func&& func) -> bool {
        try {
            // Call the function - it should throw
            std::forward<Func>(func)();
            
            // If we get here, no exception was thrown - test fails
            return false;
        } catch (const ExceptionType&) {
            // Caught the expected exception type - test passes
            return true;
        } catch (...) {
            // Caught a different exception type - test fails
            return false;
        }
    }
}

/**
 * @brief Macro for creating fixture-based tests
 *
 * This macro simplifies writing tests that use a fixture class.
 * It automatically creates a test class derived from your fixture,
 * runs setUp before the test, and tearDown after the test.
 *
 * Example:
 * @code
 * // Define a fixture
 * class StringTest : public cppul::TestFixture {
 * protected:
 *     std::string text;
 *
 *     auto setUp() -> void override {
 *         text = "Hello, World!";
 *     }
 * };
 *
 * // Use the fixture in a test
 * FIXTURE_TEST(StringTest, Length) {
 *     // text is already initialized by setUp()
 *     CHECK_EQUAL(13, text.length());
 * }
 * @endcode
 *
 * @param fixture The fixture class to use
 * @param testName The name of the test
 */
#define FIXTURE_TEST(fixture, testName) \
    class fixture##testName##Test : public fixture { \
    public: \
        fixture##testName##Test() : fixture() {} \
        void runTest(TestResult& result_); \
    } fixture##testName##Instance; \
    void fixture##testName##Test::runTest(TestResult& result_) { \
        setUp(); \
        try {

/**
 * @brief End of a fixture test
 *
 * This macro completes a fixture test by adding the tearDown() call
 * and exception handling. It's used in pairs with FIXTURE_TEST.
 *
 * Example:
 * @code
 * FIXTURE_TEST(StringTest, Length) {
 *     CHECK_EQUAL(13, text.length());
 * } END_FIXTURE_TEST
 * @endcode
 */
#define END_FIXTURE_TEST \
        } catch (...) { \
            result_.addFailure(Failure("Unexpected exception", __FILE__, __LINE__)); \
        } \
        tearDown(); \
    }

#endif // CPPUL_H
