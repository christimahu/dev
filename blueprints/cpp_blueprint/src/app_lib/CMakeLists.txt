# ==============================================================================
# CMakeLists.txt for app_lib
# Author: Christi Mahu
#
# PURPOSE:
# This file configures the build for the core library component.
# The library is built as a STATIC library, which means its code will be
# directly incorporated into the binaries that use it (the CLI and tests).
# This approach is useful for small libraries where the overhead of loading
# a dynamic library would be unnecessary.
# ==============================================================================

# ==============================================================================
# LIBRARY TARGET - Build as a static library
# ==============================================================================
add_library(${LIB_NAME} STATIC
    app_lib.cpp
    app_lib.h
)

# Apply modern C++ standard - this ensures the library uses C++23 features
target_compile_features(${LIB_NAME} PUBLIC cxx_std_23)

# ==============================================================================
# INCLUDE DIRECTORIES
# ==============================================================================
# Make the headers available to clients of the library
# The PUBLIC keyword means these includes are also available to targets
# that link against our library
target_include_directories(${LIB_NAME}
    PUBLIC
        # Make the directory containing this CMakeLists.txt accessible
        # so that #include "app_lib.h" works in client code
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        # This is for installed headers - when the library is installed
        # headers will be in include/ directory
        $<INSTALL_INTERFACE:include>
)

# ==============================================================================
# INSTALLATION
# ==============================================================================
# Install the library and its headers
include(GNUInstallDirs)

# Install the library binary
install(TARGETS ${LIB_NAME}
    EXPORT cmdevTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Install the headers
install(FILES app_lib.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/cmdev
)

# ==============================================================================
# ALIAS TARGET
# ==============================================================================
# Create an alias with a namespace for use within the build tree
# This makes it consistent with the installed target (cmdev::app_lib)
add_library(cmdev::${LIB_NAME} ALIAS ${LIB_NAME})
