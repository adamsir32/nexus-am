cmake_minimum_required(VERSION 3.16)
project(hpu_case_generators LANGUAGES C CXX)

set(INLINE_ASM_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../third_party/inline-asm" CACHE PATH
    "Pinned inline-asm checkout")
get_filename_component(INLINE_ASM_ROOT "${INLINE_ASM_ROOT}" ABSOLUTE)
get_filename_component(HPU_FIXTURE_ROOT
    "${CMAKE_CURRENT_SOURCE_DIR}/../common" ABSOLUTE)
find_package(Git REQUIRED)

function(read_git directory output)
    execute_process(COMMAND "${GIT_EXECUTABLE}" -C "${directory}" ${ARGN}
        RESULT_VARIABLE result OUTPUT_VARIABLE value OUTPUT_STRIP_TRAILING_WHITESPACE)
    if(NOT result EQUAL 0)
        message(FATAL_ERROR "Cannot read pinned Git provenance in ${directory}")
    endif()
    set(${output} "${value}" PARENT_SCOPE)
endfunction()

read_git("${INLINE_ASM_ROOT}" HPU_FRONTEND_COMMIT rev-parse HEAD)
if(NOT HPU_FRONTEND_COMMIT STREQUAL "4e26659cc0c9c3887c60491e8455ff5fd6028025")
    message(FATAL_ERROR "Operator comparison requires inline-asm 4e26659")
endif()
read_git("${INLINE_ASM_ROOT}" frontend_status status --porcelain)
if(frontend_status)
    set(HPU_FRONTEND_TREE_STATE "dirty-at-configure")
else()
    set(HPU_FRONTEND_TREE_STATE "clean-at-configure")
endif()
read_git("${INLINE_ASM_ROOT}" frontend_seal_tree rev-parse HEAD:third_party/modified-SEAL)
# 已核对的主线对照版本；CI只需要checkout实验依赖，不重新取旧主线源码。
set(HPU_BASELINE_INLINE_COMMIT "03a32c168404f3ad64e6a4d7ad82a081f910314b")
set(baseline_seal_tree "036be909da472f4343b6bac6add0dcb3be5bd057")
if(NOT frontend_seal_tree STREQUAL baseline_seal_tree)
    message(FATAL_ERROR "A/B comparison requires the same modified-SEAL source tree")
endif()
if(NOT EXISTS "${HPU_FIXTURE_ROOT}/fixture.hpp")
    message(FATAL_ERROR "The shared hputest Fixture is missing")
endif()

set(HPU_ENABLE_SEAL_INTEGRATION ON CACHE BOOL "" FORCE)
set(HPU_ENABLE_SEAL_DIFFERENTIAL_ORACLE OFF CACHE BOOL "" FORCE)
set(HPU_ENABLE_SEAL_BFV_ORACLE OFF CACHE BOOL "" FORCE)
set(HPU_ENABLE_DEPLOYMENT_APPLICATION_TESTS OFF CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(SEAL_USE_MSGSL OFF CACHE BOOL "" FORCE)
set(SEAL_USE_ZLIB OFF CACHE BOOL "" FORCE)
set(SEAL_USE_ZSTD OFF CACHE BOOL "" FORCE)
set(SEAL_USE_INTEL_HEXL OFF CACHE BOOL "" FORCE)
add_subdirectory("${INLINE_ASM_ROOT}" inline-asm EXCLUDE_FROM_ALL)

add_executable(hpu_frontend_operator_generator generator.cpp)
target_compile_features(hpu_frontend_operator_generator PRIVATE cxx_std_17)
target_compile_options(hpu_frontend_operator_generator PRIVATE -Wall -Wextra -Werror)
target_include_directories(hpu_frontend_operator_generator PRIVATE "${HPU_FIXTURE_ROOT}")
target_compile_definitions(hpu_frontend_operator_generator PRIVATE
    HPU_FRONTEND_COMMIT="${HPU_FRONTEND_COMMIT}"
    HPU_FRONTEND_TREE_STATE="${HPU_FRONTEND_TREE_STATE}"
    HPU_BASELINE_INLINE_COMMIT="${HPU_BASELINE_INLINE_COMMIT}"
    HPU_BASELINE_SEAL_TREE="${baseline_seal_tree}")
target_link_libraries(hpu_frontend_operator_generator PRIVATE
    hpu_seal_delivery SEAL::seal hpu_filesystem_compat)

# 04/05共享固定版本的前端与原fixture，只导出单份严格验证的运行包。
add_executable(hpu_group_case_generator ../group_cases/generator.cpp ../group_cases/composite.cpp)
target_compile_features(hpu_group_case_generator PRIVATE cxx_std_17)
target_compile_options(hpu_group_case_generator PRIVATE -Wall -Wextra -Werror)
target_include_directories(hpu_group_case_generator PRIVATE "${HPU_FIXTURE_ROOT}")
target_compile_definitions(hpu_group_case_generator PRIVATE
    HPU_FRONTEND_COMMIT="${HPU_FRONTEND_COMMIT}"
    HPU_FRONTEND_TREE_STATE="${HPU_FRONTEND_TREE_STATE}")
target_link_libraries(hpu_group_case_generator PRIVATE
    hpu_seal_delivery SEAL::seal hpu_filesystem_compat)

# 指令矩阵使用独立C参考；.c文件由C编译器处理，避免C++符号混淆。
add_executable(hpu_instruction_case_generator
    ../instruction_cases/generator.cpp ../../runtime/it_stage_reference.c)
target_compile_features(hpu_instruction_case_generator PRIVATE c_std_11 cxx_std_17)
target_compile_options(hpu_instruction_case_generator PRIVATE -Wall -Wextra -Werror)
target_include_directories(hpu_instruction_case_generator PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../include")
target_compile_definitions(hpu_instruction_case_generator PRIVATE
    HPU_FRONTEND_COMMIT="${HPU_FRONTEND_COMMIT}"
    HPU_FRONTEND_TREE_STATE="${HPU_FRONTEND_TREE_STATE}")
target_link_libraries(hpu_instruction_case_generator PRIVATE
    hpu_delivery_core hpu_hardware_model hpu_encode hpu_filesystem_compat)
