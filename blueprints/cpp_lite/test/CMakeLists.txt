# ==============================================================================
# CMakeLists.txt for test directory
# Author: Christi Mahu
#
# PURPOSE:
# This file configures the build for the test suite. It:
# 1. Builds the test executable
# 2. Links it against the library being tested and the test framework
# 3. Registers it with CTest for running
#
# This approach lets us run tests individually or as a suite,
# and see detailed results for each test case.
# ==============================================================================

# ==============================================================================
# TEST EXECUTABLE
# ==============================================================================
# Create an executable for the test
add_executable(${TEST_NAME} ${TEST_NAME}.cpp)

# Apply modern C++ standard
target_compile_features(${TEST_NAME} PRIVATE cxx_std_23)

# ==============================================================================
# DEPENDENCIES
# ==============================================================================
# Link against both the library being tested and the test framework
# - The library is linked statically (it's built as a static lib)
# - The cppul framework is linked dynamically (shared library)
target_link_libraries(${TEST_NAME}
    PRIVATE
        ${LIB_NAME}  # Our library being tested (static)
        cppul        # The testing framework (dynamic)
)

# ==============================================================================
# TESTING CONFIGURATION
# ==============================================================================
# Add the test to CTest
add_test(
    NAME ${TEST_NAME}
    COMMAND ${TEST_NAME}
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

# Set properties for better CTest output
set_tests_properties(${TEST_NAME} PROPERTIES
    FAIL_REGULAR_EXPRESSION "FAILED"  # Consider test failed if output contains "FAILED"
    PASS_REGULAR_EXPRESSION "Summary: [0-9]+ tests, 0 failures"  # Pass if no failures
)

# Create a helper target to run all tests
add_custom_target(check
    COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure
    DEPENDS ${TEST_NAME}
    COMMENT "Running all tests"
    VERBATIM
)

# ==============================================================================
# OUTPUT SETTINGS
# ==============================================================================
# Ensure test executable goes to the bin directory
set_target_properties(${TEST_NAME}
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
