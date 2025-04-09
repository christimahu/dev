# ==============================================================================
# CMakeLists.txt for src directory
# Author: Christi Mahu
#
# PURPOSE:
# This file configures the build for the source code components:
# 1. The library containing the core functionality (built as static library)
# 2. The CLI application that demonstrates the library
#
# By separating these components, we maintain a clean separation
# between the library interface and its usage, allowing the library
# to be reused in other projects.
# ==============================================================================

# We don't need cmake_minimum_required here since it's handled by the root CMakeLists.txt

# ==============================================================================
# SUBDIRECTORIES - Components to build
# ==============================================================================
# Always build the library - it's the core component
add_subdirectory(${LIB_NAME})

# Only build the CLI if requested
if(BUILD_CLI)
    add_subdirectory(${CLI_NAME})
endif()

# ==============================================================================
# EXPORT CONFIGURATION
# ==============================================================================
# This creates a package configuration file that allows other projects
# to find our library using find_package(cmdev)
include(CMakePackageConfigHelpers)

# Create version file
write_basic_package_version_file(
    "${CMAKE_BINARY_DIR}/cmdevConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

# Create config file
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmdevConfig.cmake.in"
    "${CMAKE_BINARY_DIR}/cmdevConfig.cmake"
    INSTALL_DESTINATION lib/cmake/cmdev
)

# Install config files
install(
    FILES
        "${CMAKE_BINARY_DIR}/cmdevConfig.cmake"
        "${CMAKE_BINARY_DIR}/cmdevConfigVersion.cmake"
    DESTINATION lib/cmake/cmdev
)

# Export targets
install(
    EXPORT cmdevTargets
    FILE cmdevTargets.cmake
    NAMESPACE cmdev::
    DESTINATION lib/cmake/cmdev
)
