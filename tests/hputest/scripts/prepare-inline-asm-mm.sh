#!/usr/bin/env bash
set -Eeuo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
test_root=$(cd -- "$script_dir/.." && pwd)
inline_asm_root=${1:-"$test_root/third_party/inline-asm"}
output_root=${2:-"$test_root/build"}
jobs=${3:-${JOBS:-4}}
hpu_seal_root=${4:-"$test_root/third_party/hpu-seal"}
hpu_applications_root=${5:-"$test_root/third_party/hpu-applications"}
build_scope=${HPU_BUILD_SCOPE:-all}
compress_temp_rns=${HPU_COMPRESS_TEMP_RNS:-0}

if [[ $inline_asm_root != /* ]]; then
  inline_asm_root=$(cd -- "$test_root" && realpath -m -- "$inline_asm_root")
fi
if [[ $output_root != /* ]]; then
  output_root=$(cd -- "$test_root" && realpath -m -- "$output_root")
fi
if [[ $hpu_seal_root != /* ]]; then
  hpu_seal_root=$(cd -- "$test_root" && realpath -m -- "$hpu_seal_root")
fi
if [[ $hpu_applications_root != /* ]]; then
  hpu_applications_root=$(cd -- "$test_root" && realpath -m -- "$hpu_applications_root")
fi
if [[ ! $jobs =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: JOBS must be a positive integer: $jobs" >&2
  exit 2
fi
# 先验证分片，避免拼错范围后仍生成整套大数据。
python3 "$script_dir/case_catalog.py" --scope "$build_scope" --table cases >/dev/null
if [[ ! $compress_temp_rns =~ ^[01]$ ]]; then
  echo 'ERROR: HPU_COMPRESS_TEMP_RNS must be 0 or 1' >&2
  exit 2
fi
if [[ ! -f $inline_asm_root/CMakeLists.txt ]] || \
   ! git -C "$inline_asm_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo 'ERROR: inline-asm submodule is not initialized' >&2
  echo 'run: git submodule update --init --recursive tests/hputest/third_party/inline-asm' >&2
  exit 2
fi
if ! git -C "$inline_asm_root" diff --ignore-space-at-eol --quiet -- || \
   ! git -C "$inline_asm_root" diff --cached --quiet --; then
  echo 'ERROR: inline-asm submodule contains tracked modifications' >&2
  exit 2
fi

repository_root=$(git -C "$test_root" rev-parse --show-toplevel)
submodule_path=${inline_asm_root#"$repository_root/"}
gitlink_commit=$(git -C "$repository_root" ls-files -s -- "$submodule_path" |
  awk '$1 == "160000" { print $2 }')
if [[ -z $gitlink_commit ]]; then
  echo "ERROR: inline-asm root is not the tracked Nexus-AM submodule" >&2
  exit 2
fi
producer_commit=$(git -C "$inline_asm_root" rev-parse HEAD)
if [[ $producer_commit != "$gitlink_commit" ]]; then
  echo 'ERROR: inline-asm checkout does not match the Nexus-AM gitlink' >&2
  echo "gitlink:  $gitlink_commit" >&2
  echo "checkout: $producer_commit" >&2
  exit 2
fi
if [[ ! -f $hpu_seal_root/CMakeLists.txt ]] || \
   ! git -C "$hpu_seal_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo 'ERROR: HPU_SEAL submodule is not initialized' >&2
  echo 'run: git submodule update --init --recursive tests/hputest/third_party/hpu-seal' >&2
  exit 2
fi
if ! git -C "$hpu_seal_root" diff --ignore-space-at-eol --quiet -- || \
   ! git -C "$hpu_seal_root" diff --cached --quiet --; then
  echo 'ERROR: HPU_SEAL submodule contains tracked modifications' >&2
  exit 2
fi
hpu_seal_path=${hpu_seal_root#"$repository_root/"}
hpu_seal_gitlink=$(git -C "$repository_root" ls-files -s -- "$hpu_seal_path" |
  awk '$1 == "160000" { print $2 }')
hpu_seal_commit=$(git -C "$hpu_seal_root" rev-parse HEAD)
if [[ -z $hpu_seal_gitlink || $hpu_seal_commit != "$hpu_seal_gitlink" ]]; then
  echo 'ERROR: HPU_SEAL checkout does not match the Nexus-AM gitlink' >&2
  echo "gitlink:  $hpu_seal_gitlink" >&2
  echo "checkout: $hpu_seal_commit" >&2
  exit 2
fi
if [[ ! -f $hpu_applications_root/CMakeLists.txt ]] || \
   ! git -C "$hpu_applications_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo 'ERROR: HPU applications submodule is not initialized' >&2
  echo 'run: git submodule update --init --recursive tests/hputest/third_party/hpu-applications' >&2
  exit 2
fi
if ! git -C "$hpu_applications_root" diff --ignore-space-at-eol --quiet -- || \
   ! git -C "$hpu_applications_root" diff --cached --quiet --; then
  echo 'ERROR: HPU applications submodule contains tracked modifications' >&2
  exit 2
fi
hpu_applications_path=${hpu_applications_root#"$repository_root/"}
hpu_applications_gitlink=$(git -C "$repository_root" ls-files -s -- "$hpu_applications_path" |
  awk '$1 == "160000" { print $2 }')
hpu_applications_commit=$(git -C "$hpu_applications_root" rev-parse HEAD)
if [[ -z $hpu_applications_gitlink || \
      $hpu_applications_commit != "$hpu_applications_gitlink" ]]; then
  echo 'ERROR: HPU applications checkout does not match the Nexus-AM gitlink' >&2
  echo "gitlink:  $hpu_applications_gitlink" >&2
  echo "checkout: $hpu_applications_commit" >&2
  exit 2
fi
for tool in cmake python3 "${CXX:-c++}"; do
  command -v "$tool" >/dev/null || {
    echo "ERROR: missing build tool: $tool" >&2
    exit 2
  }
done


cmake_build="$output_root/inline-asm-cmake"
# 按生产者提交隔离输出，切换分支时不读取旧 submodule 内的 outputs。
producer_work="$output_root/inline-asm-producer/$producer_commit"
producer_mm="$producer_work/outputs/mm"
producer_keyswitch="$producer_work/outputs/keyswitch"
generated_root="$output_root/generated"
import_root="$generated_root/inline-asm/mm"
keyswitch_source_root="$generated_root/keyswitch-source"
keyswitch_import_root="$generated_root/keyswitch-data"
auto_import_root="$generated_root/auto-data"
generated_header="$generated_root/include/hpu/inline_asm_mm_delivery.h"
tool_root="$output_root/inline-asm-tools"
encoding_tsv="$tool_root/encoder_words.tsv"
hpu_seal_build="$output_root/hpu-seal-operators-cmake/$hpu_seal_commit"
hpu_seal_source="$output_root/hpu-seal-producer/$hpu_seal_commit/hadd"
hpu_seal_import="$generated_root/hadd-data"
hpu_reline_build="$output_root/hpu-seal-cmb012-cmake/$hpu_seal_commit"
hpu_reline_source="$output_root/hpu-seal-producer/$hpu_seal_commit/ckks/reline"
hpu_rescale_build="$output_root/hpu-seal-cmb013-cmake/$hpu_seal_commit"
hpu_rescale_source="$output_root/hpu-seal-producer/$hpu_seal_commit/ckks/rescale"
hpu_seal_rotate_build="$output_root/hpu-seal-cmb014-cmake/$hpu_seal_commit"
hpu_seal_rotate_source="$output_root/hpu-seal-producer/$hpu_seal_commit/rotate"
hpu_seal_rotate_import="$generated_root/rotate-data"
hpu_seal_tool_root="$output_root/hpu-seal-tools/$hpu_seal_commit"
hpu_seal_encodings="$hpu_seal_tool_root/hadd_encoder_words.tsv"
hmul_source="$output_root/hpu-seal-producer/$hpu_seal_commit/hmul"
hmul_import="$generated_root/hmul-data"
hmul_encodings="$hpu_seal_tool_root/hmul_encoder_words.tsv"
hpu_seal_encoder="$hpu_seal_tool_root/verify-ckks-encoding"
hpu_applications_build="$output_root/app006-applications-cmake/$hpu_applications_commit"
hpu_applications_posix_root=${HPU_APPLICATION_POSIX_ROOT:-${XDG_CACHE_HOME:-"$HOME/.cache"}/nexus-am-hputest/hpu-applications/$hpu_applications_commit/outputs}

mkdir -p -- "$cmake_build" "$tool_root" "$generated_root" "$producer_work" \
  "$hpu_seal_build" "$hpu_seal_source" "$hmul_source" "$hpu_reline_build" \
  "$hpu_reline_source" "$hpu_rescale_build" "$hpu_rescale_source" \
  "$hpu_seal_rotate_build" \
  "$hpu_seal_rotate_source" "$hpu_seal_tool_root"
mkdir -p -- "$hpu_applications_build" "$hpu_applications_posix_root"
required_outputs=(
  "$producer_mm/mm.c"
  "$producer_mm/mm.h"
  "$producer_mm/mm.asm"
  "$producer_mm/dma_relocation_manifest.csv"
  "$producer_mm/test_data/params.json"
  "$producer_mm/test_data/hardware/line_map.csv"
  "$producer_mm/test_data/hardware/images/input_a.u32.bin"
  "$producer_mm/test_data/hardware/images/input_b.u32.bin"
  "$producer_mm/test_data/hardware/images/expected.u32.bin"
  "$producer_mm/test_data/hardware/constants/mod_ctx.u32.bin"
)

echo "[hputest] generating selected inline-asm MM and KeySwitch inputs at $producer_commit"
cmake -S "$inline_asm_root" -B "$cmake_build" \
  -DBUILD_TESTING=ON \
  -DHPU_ENABLE_SEAL_DIFFERENTIAL_ORACLE=OFF \
  -DHPU_ENABLE_SEAL_BFV_ORACLE=OFF \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "$cmake_build" --parallel "$jobs" --target \
  inline_asm_codegen inline_asm_encode_outputs hpu_reference_vectors \
  hpu_encode_self_test hpu_ntt_hardware_model_test
# 先验证生产者的 STG/DMA 固定向量与生成 C 的机器码，再接收交付。
"$cmake_build/test/encode/hpu_encode_self_test"
"$cmake_build/test/reference/hpu_ntt_hardware_model_test"
(
  cd "$producer_work"
  "$cmake_build/inline_asm_codegen" both \
    --config "$inline_asm_root/config/fhe_test.conf"
  "$cmake_build/test/encode/inline_asm_encode_outputs" \
    --config "$inline_asm_root/config/fhe_test.conf"
  "$cmake_build/test/reference/hpu_reference_vectors" \
    "$producer_work/outputs/ciphertext_multiply/test_data" \
    "$producer_work/outputs" \
    --config "$inline_asm_root/config/fhe_test.conf"
)
for path in "${required_outputs[@]}"; do
  if [[ ! -s $path ]]; then
    echo "ERROR: inline-asm generation omitted required MM output: $path" >&2
    exit 2
  fi
done

"${CXX:-c++}" \
  -std=c++17 -Wall -Wextra -Werror \
  -I"$inline_asm_root/encode/include" \
  "$script_dir/generate-inline-asm-encodings.cpp" \
  "$inline_asm_root/encode/src/instruction.cpp" \
  "$inline_asm_root/encode/src/parser.cpp" \
  "$inline_asm_root/encode/src/encoder.cpp" \
  "$inline_asm_root/encode/src/assembler.cpp" \
  -o "$tool_root/generate-inline-asm-encodings"
"$tool_root/generate-inline-asm-encodings" "$encoding_tsv"

python3 "$script_dir/import-inline-asm-mm.py" \
  --source "$producer_mm" \
  --destination "$import_root" \
  --header "$generated_header" \
  --encodings "$encoding_tsv" \
  --producer-commit "$producer_commit"

python3 "$script_dir/import-stage-data.py" \
  --source "$producer_work/outputs" \
  --destination "$generated_root/instruction-data" \
  --producer-commit "$producer_commit"

python3 "$script_dir/import-transform-data.py" \
  --source "$producer_work/outputs" \
  --destination "$generated_root/transform-data" \
  --producer-commit "$producer_commit" --encodings "$encoding_tsv"

python3 "$script_dir/import-bconv-data.py" \
  --source "$producer_work/outputs" \
  --destination "$generated_root/bconv-data" \
  --producer-commit "$producer_commit" --encodings "$encoding_tsv"

python3 "$script_dir/stage-keyswitch-package.py" \
  --source "$producer_keyswitch" \
  --destination "$keyswitch_source_root" \
  --producer-commit "$producer_commit"

python3 "$script_dir/import-keyswitch-data.py" \
  --source "$producer_work/outputs" \
  --destination "$keyswitch_import_root" \
  --producer-commit "$producer_commit" \
  --encodings "$encoding_tsv"

python3 "$script_dir/import-auto-data.py" \
  --source "$producer_work/outputs" \
  --destination "$auto_import_root" \
  --producer-commit "$producer_commit" \
  --encodings "$encoding_tsv"

echo "[hputest] generating main v1 CKKS/BFV/BGV packages at $hpu_applications_commit"
hpu_main_build="$output_root/hpu-main-cmake/$hpu_applications_commit"
package_parent="$output_root/hpu-main-producer/$hpu_applications_commit"
mkdir -p "$package_parent"
# 本次独立生成，普通/静默编译复用同一份包，不能混用跨次随机密钥。
package_root=$(mktemp -d "$package_parent/generation.XXXXXX")
cmake -S "$test_root/tools/hpu-scheme-cases" -B "$hpu_main_build" \
  -DINLINE_ASM_ROOT="$hpu_applications_root" -DCMAKE_BUILD_TYPE=Release \
  -DLEGACY_INLINE_ASM_ROOT="$inline_asm_root" \
  -DHPU_APPLICATION_OUTPUT_ROOT="$package_root"
main_targets=(hpu_scheme_case_generator hpu_fixture_parameters hpu_cpu_benchmark \
  hpu_program_model hpu_program_model_test hpu_encode_program hpu_render_program \
  hpu_render_legacy_program hpu_legacy_program_model \
  inline_asm_codegen inline_asm_encode_outputs hpu_reference_vectors)
if [[ $build_scope == all || $build_scope == functional ]]; then
  main_targets+=(hpu_fhe_delivery hpu_ckks_multilevel_codegen_test \
    hpu_seal_ckks_application_image_test hpu_seal_ckks_multiply_operation_plan_test \
    hpu_seal_ckks_galois_operation_plan_test)
fi
HPU_DELIVERY_COMMIT="$hpu_applications_commit" \
HPU_DELIVERY_WORKTREE_STATE=clean-at-configure \
  cmake --build "$hpu_main_build" --parallel "$jobs" --target \
    "${main_targets[@]}"
# 直接使用上游回归：N128/N4096、多层Q与两个accumulator的half-P绑定。
if [[ $build_scope == all || $build_scope == functional ]]; then
for native_test in hpu_ckks_multilevel_codegen_test hpu_seal_ckks_application_image_test \
                   hpu_seal_ckks_multiply_operation_plan_test hpu_seal_ckks_galois_operation_plan_test; do
  "$hpu_main_build/inline-asm/$native_test"
done
fi
"$hpu_main_build/hpu_program_model_test"
while IFS=$'\t' read -r case_id stem scheme degree role source; do
  [[ $case_id == case_id ]] && continue
  if [[ $role != application ]]; then
    generator="$hpu_main_build/hpu_scheme_case_generator"
    profile=()
    if [[ $stem == seal_* ]]; then
      profile=(library)
    elif [[ $source == src/05_algorithm_library/04_parameter_regression/* ]]; then
      profile=(regression)
    fi
    q_rns=()
    if [[ $stem =~ _l([0-9]+)_n ]]; then
      q_rns=("${BASH_REMATCH[1]}")
      if [[ ${#profile[@]} == 0 ]]; then profile=(30); fi
    fi
    HPU_DELIVERY_COMMIT="$hpu_applications_commit" \
    HPU_DELIVERY_WORKTREE_STATE=clean-at-configure \
      "$generator" "$scheme" "$role" "$degree" \
        "$package_root/$stem" "${profile[@]}" "${q_rns[@]}"
  fi
  upstream_link=()
  if [[ ${HPU_LINK_UPSTREAM:-0} == 1 ]]; then upstream_link=(--link-upstream); fi
  python3 "$script_dir/import-application-package.py" \
    --source "$package_root/$stem" \
    --destination "$generated_root/application-data/$stem" \
    --validator "$hpu_main_build/inline-asm/hpu_validate_package" \
    --encoder "$hpu_main_build/hpu_encode_program" \
    --program-model "$hpu_main_build/hpu_program_model" \
    --producer-commit "$hpu_applications_commit" "${upstream_link[@]}"
  if [[ $role != application ]]; then
    parameter_profile=kernel
    if [[ $stem == seal_* ]]; then parameter_profile=library; fi
    if [[ $source == src/05_algorithm_library/04_parameter_regression/* ]]; then parameter_profile=regression; fi
    "$hpu_main_build/hpu_fixture_parameters" "$scheme" "$role" "$degree" "$parameter_profile" "${q_rns[@]}" \
      > "$generated_root/application-data/$stem/FIXTURE_PARAMETERS.json"
  fi
done < <(python3 "$script_dir/case_catalog.py" --scope "$build_scope")
# 多规模算子共用main编码器和独立golden；N65536同时保留原03功能交付。
large_generation=$(mktemp -d "$package_parent/large.XXXXXX")
large_delivery="$large_generation/delivery"
mkdir -p "$large_delivery"
large_selection="$large_generation/selection.tsv"
python3 "$script_dir/case_catalog.py" --scope "$build_scope" --table large > "$large_selection"
compress_completed_rns() {
  [[ $compress_temp_rns == 1 ]] || return 0
  local completed_outputs=$1
  local raw_file
  # 原生生成、编码和模型导入均已返回；逐文件压缩本次私有临时输出，可从.gz还原。
  while IFS= read -r -d '' raw_file; do
    python3 "$script_dir/compress-temporary-rns.py" --generation-root "$large_generation" "$raw_file"
  done < <(find "$completed_outputs" -type f -name '*.bin' -size +1M -print0)
}
mapfile -t large_degrees < <(awk -F '\t' 'NR > 1 {n=$2; sub(/^.*_n/, "", n); print n}' "$large_selection" | sort -nu)
for degree in "${large_degrees[@]}"; do
  operators=$(awk -F '\t' -v suffix="_n$degree" 'NR > 1 && $2 ~ suffix "$" {op=$2; sub(suffix "$", "", op); if (op != "auto") {if (seen++) printf ","; printf "%s", op}}' "$large_selection")
  if [[ -n $operators ]]; then
  main_generation="$large_generation/n$degree"
  mkdir -p "$main_generation"
  (
    cd "$main_generation"
    "$hpu_main_build/inline-asm/inline_asm_codegen" both --config "$test_root/config/n$degree.conf"
    "$hpu_main_build/inline-asm/test/encode/inline_asm_encode_outputs" --config "$test_root/config/n$degree.conf"
    "$hpu_main_build/inline-asm/test/reference/hpu_reference_vectors" \
      outputs/ciphertext_multiply/test_data outputs --config "$test_root/config/n$degree.conf"
  )
  python3 "$script_dir/prepare-large-data.py" --source "$main_generation/outputs" \
    --destination "$large_delivery" --renderer "$hpu_main_build/hpu_render_program" \
    --model "$hpu_main_build/hpu_program_model" --legacy-commit "$hpu_applications_commit" \
    --degree "$degree" --only "$operators"
  compress_completed_rns "$main_generation/outputs"
  fi
  if awk -F '\t' -v stem="auto_n$degree" 'NR > 1 && $2 == stem {found=1} END {exit !found}' "$large_selection"; then
  legacy_large="$large_generation/legacy-n$degree"
  mkdir -p "$legacy_large"
  (
    cd "$legacy_large"
    "$cmake_build/inline_asm_codegen" both --config "$test_root/config/n$degree-legacy-auto.conf"
    "$cmake_build/test/encode/inline_asm_encode_outputs" --config "$test_root/config/n$degree-legacy-auto.conf"
    "$cmake_build/test/reference/hpu_reference_vectors" outputs/ciphertext_multiply/test_data outputs \
      --config "$test_root/config/n$degree-legacy-auto.conf"
  )
  python3 "$script_dir/prepare-large-data.py" --source "$legacy_large/outputs" \
    --destination "$large_delivery" --renderer "$hpu_main_build/hpu_render_legacy_program" \
    --model "$hpu_main_build/hpu_legacy_program_model" --legacy-commit "$producer_commit" \
    --degree "$degree" --only auto
  compress_completed_rns "$legacy_large/outputs"
  fi
done
# 只切换本次生成目录的链接；既有交付留在其generation目录，便于回查。
if [[ -e $generated_root/large-data && ! -L $generated_root/large-data ]]; then
  echo 'ERROR: large-data is not a managed generation symlink' >&2
  exit 2
fi
ln -sfn "$large_delivery" "$generated_root/large-data"
selected_perf=$(python3 "$script_dir/case_catalog.py" --scope "$build_scope" --table performance | awk -F '\t' 'NR > 1 {if (seen++) printf ","; printf "%s", $3}')
if [[ -n $selected_perf ]]; then
  python3 "$script_dir/prepare-perf-programs.py" --generated "$generated_root" --only "$selected_perf"
fi
printf '%s\n' "$package_root" > "$generated_root/application-data/PRODUCER_ROOT"
printf '%s\n' "$hpu_applications_commit" > "$generated_root/application-data/PRODUCER_COMMIT"
echo '[hputest] legacy primitive/control + main scheme/application import PASS'
