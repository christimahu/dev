#include "Test.h"
#include "TestResult.h"
#include "TestRegistry.h"
#include <iostream>

void TestRegistry::addTest (Test *test) 
{
    instance ().add (test);
}

void TestRegistry::runAllTests (TestResult& result) 
{
    instance ().run (result);
}

TestRegistry& TestRegistry::instance () {
    static TestRegistry registry;
    return registry;
}

void TestRegistry::add (Test *test) {
    tests.push_back (test);
}

void TestRegistry::run (TestResult& result) {
    auto testCount = 0;
    auto errorCount = 0;
    result.startTests ();

    #ifdef VERBOSE_TESTS
    std::cout << "\nRunning tests...\n";
    #endif

    for (auto& test : tests)
    {
        ++testCount;
        #ifdef VERBOSE_TESTS
        std::cout << "Running: " << test->getName() << " ... ";
        #endif
        
        try {
            test->run (result);
            #ifdef VERBOSE_TESTS
            std::cout << "PASSED\n";
            #endif
        }
        catch (std::exception &e) {
            ++errorCount;
            #ifdef VERBOSE_TESTS
            std::cout << "FAILED\n";
            #endif
            std::cout << std::endl
                      << test->getFileName()
                      << "(" << test->getLineNumber() << ") : "
                      << "Error: exception "
                      << "'" << e.what() << "'"
                      << " thrown in "
                      << test->getName()
                      << std::endl;
        }
        catch (...) {
            ++errorCount;
            #ifdef VERBOSE_TESTS
            std::cout << "FAILED\n";
            #endif
            std::cout << std::endl
                      << test->getFileName()
                      << "(" << test->getLineNumber() << ") : "
                      << "Error: unknown exception thrown in "
                      << test->getName()
                      << std::endl;
        }
    }
    result.endTests ();
    const auto failureCount = result.getFailureCount();
    if (failureCount > 0 || errorCount > 0) std::cout << std::endl;
    std::cout << "\nSummary: " << testCount << " tests, "
              << failureCount << " failures, "
              << errorCount << " errors" << std::endl;
}
