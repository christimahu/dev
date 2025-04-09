# ==============================================================================
# CMakeLists.txt for app_cli
# Author: Christi Mahu
#
# PURPOSE:
# This file configures the build for the command-line interface application.
# The CLI demonstrates the functionality provided by the app_lib library.
#
# This is a separate component from the library to maintain a clean separation
# between the library interface and its usage.
# ==============================================================================

# ==============================================================================
# EXECUTABLE TARGET
# ==============================================================================
# Create an executable target for the CLI application
add_executable(${CLI_NAME}
    app_cli.cpp
)

# Apply modern C++ standard
# We use the same standard as the library for consistency
target_compile_features(${CLI_NAME} PRIVATE cxx_std_23)

# ==============================================================================
# DEPENDENCIES
# ==============================================================================
# Link against the library - this is the core dependency
# The TARGET_LINK_LIBRARIES command is the modern way to express dependencies
target_link_libraries(${CLI_NAME}
    PRIVATE
        ${LIB_NAME}  # Links to our static library
)

# ==============================================================================
# INSTALLATION
# ==============================================================================
# Install the executable
include(GNUInstallDirs)

install(TARGETS ${CLI_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
