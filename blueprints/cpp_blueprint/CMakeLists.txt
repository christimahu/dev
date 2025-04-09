# ==============================================================================
# Root CMakeLists.txt for App Project
# Author: Christi Mahu
#
# PURPOSE:
# This is the top-level CMake configuration file that coordinates the entire
# build process for the project.
# ==============================================================================

# Minimum CMake version required for modern features
cmake_minimum_required(VERSION 3.14)

# ==============================================================================
# PROJECT CONFIGURATION
# ==============================================================================
# These variables can be set via CMake presets to easily rename the project
if(NOT DEFINED PROJECT_NAME)
  set(PROJECT_NAME "app")
endif()

if(NOT DEFINED PROJECT_DISPLAY_NAME)
    set(PROJECT_DISPLAY_NAME "App")
endif()

if(NOT DEFINED PROJECT_PREFIX)
  set(PROJECT_PREFIX "app")
endif()

if(NOT DEFINED PROJECT_DESCRIPTION)
    set(PROJECT_DESCRIPTION "App")
endif()

# Define component names based on prefix
set(LIB_NAME "${PROJECT_PREFIX}_lib")
set(CLI_NAME "${PROJECT_PREFIX}_cli")
set(TEST_NAME "${PROJECT_PREFIX}_test")

# Define the project with metadata
project(${PROJECT_NAME}
    VERSION 0.1.0
    DESCRIPTION "${PROJECT_DESCRIPTION}"
    LANGUAGES CXX
)

# ==============================================================================
# PROJECT OPTIONS - Control what gets built
# ==============================================================================
option(BUILD_TESTING "Build tests for the project" ON)
option(BUILD_CLI "Build the command line interface" ON)

# ==============================================================================
# GLOBAL COMPILER SETTINGS
# ==============================================================================
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Optional: Add warnings for better code quality
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# ==============================================================================
# OUTPUT DIRECTORIES
# ==============================================================================
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# ==============================================================================
# TESTING CONFIGURATION
# ==============================================================================
if(BUILD_TESTING)
    include(CTest)
    enable_testing()
endif()

# ==============================================================================
# SUBDIRECTORIES - Build components in the correct order
# ==============================================================================
# First, build the external dependencies
add_subdirectory(extern/cppul)

# Then, build our library and applications
add_subdirectory(src)

# Finally, if testing is enabled, build the tests
if(BUILD_TESTING)
    add_subdirectory(test)
endif()

# ==============================================================================
# INSTALLATION RULES
# ==============================================================================
include(GNUInstallDirs)
install(DIRECTORY ${CMAKE_BINARY_DIR}/bin/
        DESTINATION ${CMAKE_INSTALL_BINDIR}
        USE_SOURCE_PERMISSIONS
        FILES_MATCHING PATTERN "*"
        PATTERN "*.ilk" EXCLUDE
        PATTERN "*.pdb" EXCLUDE)

# ==============================================================================
# SUMMARY - Output build configuration for the user
# ==============================================================================
message(STATUS "==== ${PROJECT_DISPLAY_NAME} Build Configuration ====")
message(STATUS "Project name: ${PROJECT_NAME}")
message(STATUS "Project prefix: ${PROJECT_PREFIX}")
message(STATUS "Library name: ${LIB_NAME}")
message(STATUS "CLI name: ${CLI_NAME}")
message(STATUS "Test name: ${TEST_NAME}")
message(STATUS "Build testing: ${BUILD_TESTING}")
message(STATUS "Build CLI: ${BUILD_CLI}")
message(STATUS "Output directory: ${CMAKE_BINARY_DIR}")
message(STATUS "=======================================")
