// ==============================================================================
// app_lib.h — Header for App Library
// Author: Christi Mahu
//
// This basic library demonstrates several key C++ concepts:
// 1. Simple math operations
// 2. Namespace organization
// 3. Header/implementation separation
// 4. Modern C++ coding practices
// ==============================================================================

#ifndef CMDEV_APP_LIB_H
#define CMDEV_APP_LIB_H

namespace cmdev {
namespace app {

/**
 * @brief Add two integers
 * 
 * @details This function demonstrates a simple mathematical operation
 * and the use of trailing return type syntax (auto -> int).
 * 
 * Trailing return types provide consistency and improve readability
 * when function templates or complex return types are involved.
 * Even for simple functions like this, using trailing return type
 * helps establish a consistent coding style.
 * 
 * @param a First integer
 * @param b Second integer
 * @return Sum of the two integers
 */
auto add(int a, int b) -> int;

/**
 * @brief Subtract second integer from first
 * 
 * @details This function demonstrates another simple mathematical
 * operation with consistent use of trailing return type.
 * 
 * Function declarations in the header file show the API while
 * the implementation details are in the .cpp file. This separation
 * allows us to hide implementation details from library users.
 * 
 * @param a First integer
 * @param b Second integer
 * @return Difference (a - b)
 */
auto subtract(int a, int b) -> int;

/**
 * @brief Divide first integer by second
 * 
 * @details This function performs integer division. Note that in C++,
 * dividing two integers results in an integer (truncated) result.
 * 
 * A more robust implementation might check for division by zero,
 * but this simple example assumes the caller handles that case.
 * 
 * @param a Dividend
 * @param b Divisor
 * @return Quotient (a / b)
 */
auto divide(int a, int b) -> int;

} // namespace app
} // namespace cmdev

#endif // CMDEV_app_LIB_H
