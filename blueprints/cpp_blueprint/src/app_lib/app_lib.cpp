// ==============================================================================
// app_lib.cpp — Implementation for App Library
// Author: Christi Mahu
//
// This file implements the library interface defined in app_lib.h.
// It demonstrates the separation of interface from implementation,
// allowing us to change implementation details without affecting clients.
// ==============================================================================

#include "app_lib.h"

namespace cmdev {
namespace app {

// Implementation of add function
// This simple implementation directly returns the sum of two integers.
// In a more complex library, the implementation might include:
// - Input validation
// - Overflow checking
// - Logging or performance monitoring
auto add(int a, int b) -> int {
    return a + b;
}

// Implementation of subtract function
// This function computes the difference between two integers.
// The implementation is straightforward and just returns a - b.
//
// Note how trailing return types are consistently used throughout
// the codebase to establish a uniform style.
auto subtract(int a, int b) -> int {
    return a - b;
}

// Implementation of divide function
// This function performs integer division of a by b.
//
// In a production library, this function would likely include:
// - A check for division by zero (b == 0)
// - Possibly an exception or error code return mechanism
// - Handling for edge cases like INT_MIN / -1 which can overflow
auto divide(int a, int b) -> int {
    // For a simple educational example, we omit error checking
    // and assume the caller handles edge cases
    return a / b;
}

} // namespace app
} // namespace cmdev
