cmake_minimum_required(VERSION 3.18)
cmake_policy(SET CMP0091 NEW)

project(lap_sim)

#--------------------------------------------------------------
# Find Chrono (Vehicle module required)
# Points at the local build tree; change Chrono_DIR if you
# installed Chrono elsewhere.
#--------------------------------------------------------------

list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../build/cmake")

find_package(Chrono
    COMPONENTS Vehicle Irrlicht
    CONFIG)

if(NOT Chrono_FOUND)
    message(FATAL_ERROR "Could not find Chrono or its Vehicle module")
endif()

#--------------------------------------------------------------
# Output directories
#--------------------------------------------------------------

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/build/bin")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/build/lib")

# Embed the Chrono library path into the binary so it runs without
# having to set LD_LIBRARY_PATH manually.
# CHRONO_LINKER_FLAGS contains "-L/path/to/lib"; strip the flag to get the dir.
string(REPLACE "-L" "" CHRONO_LIB_DIRS "${CHRONO_LINKER_FLAGS}")
set(CMAKE_BUILD_RPATH "${CHRONO_LIB_DIRS}")
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

#--------------------------------------------------------------
# Match the C++ standard used to build Chrono
#--------------------------------------------------------------

set(CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD ${CHRONO_CXX_STANDARD})

#--------------------------------------------------------------
# Includes
#--------------------------------------------------------------

include_directories(${CHRONO_INCLUDE_DIRS})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)

#--------------------------------------------------------------
# Sources
#--------------------------------------------------------------

set(LAP_SIM_SOURCES
    src/build_vehicle.cpp
)

#--------------------------------------------------------------
# Static library of all vehicle-building code
# (no main() yet — add an executable below when you have one)
#--------------------------------------------------------------

add_library(lap_sim_lib STATIC ${LAP_SIM_SOURCES})

target_compile_definitions(lap_sim_lib PUBLIC
    "CHRONO_DATA_DIR=\"${CHRONO_DATA_DIR}\""
    "LAP_SIM_DATA_DIR=\"${CMAKE_CURRENT_SOURCE_DIR}/data/\"")
target_compile_options(lap_sim_lib PUBLIC ${CHRONO_CXX_FLAGS})
target_link_options(lap_sim_lib PUBLIC ${CHRONO_LINKER_FLAGS})
target_link_libraries(lap_sim_lib ${CHRONO_LIBRARIES})

#--------------------------------------------------------------
# Executable (uncomment and add your main.cpp when ready)
#--------------------------------------------------------------

add_executable(lap_sim src/main.cpp)
target_compile_definitions(lap_sim PUBLIC
    "CHRONO_DATA_DIR=\"${CHRONO_DATA_DIR}\""
    "LAP_SIM_DATA_DIR=\"${CMAKE_CURRENT_SOURCE_DIR}/data/\"")
target_compile_options(lap_sim PUBLIC ${CHRONO_CXX_FLAGS})
target_link_options(lap_sim PUBLIC ${CHRONO_LINKER_FLAGS})
target_link_libraries(lap_sim lap_sim_lib ${CHRONO_LIBRARIES})
