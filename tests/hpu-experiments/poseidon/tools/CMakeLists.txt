cmake_minimum_required(VERSION 3.19)
project(hpu_poseidon_experiment LANGUAGES C CXX)
set(SEAL_TOOLS "" CACHE PATH "Explicit matching historical SEAL tools; not current IT frontend")
if(NOT EXISTS "${SEAL_TOOLS}/CMakeLists.txt" OR NOT EXISTS "${SEAL_TOOLS}/fixture.hpp")
  message(FATAL_ERROR "Supply SEAL_TOOLS from the matching historical experiment checkout; current IT is not a legacy adapter")
endif()
if(NOT DEFINED POSEIDON_ROOT OR NOT DEFINED POSEIDON_BUILD)
  message(FATAL_ERROR "Build Poseidon explicitly and supply POSEIDON_ROOT and POSEIDON_BUILD")
endif()
add_subdirectory("${SEAL_TOOLS}" seal-tools EXCLUDE_FROM_ALL)
find_library(POSEIDON_LIBRARY NAMES poseidon_shared
  PATHS "${POSEIDON_BUILD}/lib" "${POSEIDON_BUILD}" NO_DEFAULT_PATH REQUIRED)
execute_process(COMMAND git -C "${POSEIDON_ROOT}" rev-parse HEAD
  OUTPUT_VARIABLE POSEIDON_REVISION OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ERROR_IS_FATAL ANY)
add_executable(hpu_poseidon_case_generator
  poseidon_main.cpp poseidon_fixture.cpp poseidon_bridge.cpp
  "${SEAL_TOOLS}/ckks.cpp" "${SEAL_TOOLS}/bfv.cpp" "${SEAL_TOOLS}/bgv.cpp")
target_compile_features(hpu_poseidon_case_generator PRIVATE cxx_std_17)
target_compile_options(hpu_poseidon_case_generator PRIVATE -Wall -Wextra -Werror)
target_include_directories(hpu_poseidon_case_generator PRIVATE "${SEAL_TOOLS}")
target_include_directories(hpu_poseidon_case_generator SYSTEM PRIVATE
  "${POSEIDON_ROOT}/src" "${POSEIDON_BUILD}" ${POSEIDON_GMP_INCLUDE})
target_compile_definitions(hpu_poseidon_case_generator PRIVATE POSEIDON_REVISION="${POSEIDON_REVISION}")
target_link_libraries(hpu_poseidon_case_generator PRIVATE hpu_seal_delivery hpu_filesystem_compat "${POSEIDON_LIBRARY}")
