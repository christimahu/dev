// ==============================================================================
// app_cli.cpp — Command Line Interface for App 
// Author: Christi Mahu
//
// This file implements a simple console application that demonstrates how
// to use the app_lib library. It shows:
// 1. How to include and use the library
// 2. How to access functions in the cmdev::app namespace
// 3. Basic console output and formatting
// ==============================================================================

#include <iostream>
#include <iomanip>
#include "../app_lib/app_lib.h"

/**
 * @brief Main entry point for the CLI application
 * 
 * This function demonstrates the three mathematical operations
 * provided by our library:
 * - Addition
 * - Subtraction
 * - Division
 * 
 * It uses modern C++ features like:
 * - Trailing return type (auto -> int)
 * - const for values that don't change
 * - auto for type deduction
 * - Namespaced functions
 * 
 * @return Exit code (0 for success)
 */
auto main() -> int {
    // Welcome message with decorative formatting
    std::cout << "Welcome to the App Demo\n";
    std::cout << "=========================================\n\n";
    
    // Demonstrate the math functions with sample values
    const int a = 10;
    const int b = 5;
    
    std::cout << "Demonstrating math functions with values " << a << " and " << b << ":\n\n";
    
    // Addition - call the add function from the library
    // Note the namespace qualification: cmdev::app::add
    const auto sum = cmdev::app::add(a, b);
    std::cout << "Addition: " << a << " + " << b << " = " << sum << "\n";
    
    // Subtraction - call the subtract function from the library
    const auto difference = cmdev::app::subtract(a, b);
    std::cout << "Subtraction: " << a << " - " << b << " = " << difference << "\n";
    
    // Division - call the divide function from the library
    const auto quotient = cmdev::app::divide(a, b);
    std::cout << "Division: " << a << " / " << b << " = " << quotient << "\n";
    
    // Return success code
    return 0;
}
