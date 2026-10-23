#include "assembler.hpp"
#include "executable.hpp"
#include "hpu/delivery/application_package.hpp"
#include "hpu/model/hardware_ntt.hpp"
#include "hpu/model/instruction_executor.hpp"
#include "util/hpu_asm.hpp"

#include <algorithm>
#include <array>
#include <filesystem>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

extern "C" int stage_golden(const std::uint32_t *, const std::uint32_t *,
                             std::uint32_t *, unsigned, std::uint32_t, unsigned, unsigned);

#ifndef HPU_FRONTEND_COMMIT
#define HPU_FRONTEND_COMMIT "unknown"
#endif
#ifndef HPU_FRONTEND_TREE_STATE
#define HPU_FRONTEND_TREE_STATE "unknown"
#endif

namespace fs = std::filesystem;
namespace runtime = hpu::runtime;
namespace delivery = hpu::delivery;
using Words = std::vector<std::uint32_t>;

namespace {
// 四个不同的NTT素数均支持N<=8192；这是指令测试参数，不宣称加密安全级别。
constexpr std::array<std::uint32_t, 4> moduli{{2013265921U, 1811939329U, 469762049U, 998244353U}};
constexpr std::array<std::uint32_t, 4> roots{{31U, 13U, 3U, 3U}};
constexpr std::array<std::size_t, 5> degrees{{128, 1024, 2048, 4096, 8192}};
constexpr std::array<const char *, 9> operations{{
    "padd", "psub", "pmul", "pmac", "pntt", "pintt", "pmodld", "psync", "pfree"}};

struct Options {
    std::string operation;
    std::size_t degree = 0;
    unsigned level = 0;
    fs::path output;
    bool verify_only = false;
};

Options arguments(int argc, char **argv) {
    if (argc != 5 && argc != 6)
        throw std::invalid_argument("usage: hpu_instruction_case_generator OP N LEVEL OUTPUT [--verify-only]");
    Options result;
    result.operation = argv[1];
    std::size_t used = 0;
    result.degree = std::stoul(argv[2], &used);
    if (used != std::string(argv[2]).size() ||
        std::find(degrees.begin(), degrees.end(), result.degree) == degrees.end())
        throw std::invalid_argument("N must be 128, 1024, 2048, 4096 or 8192");
    const auto level = std::stoul(argv[3], &used);
    if (used != std::string(argv[3]).size() || level < 1 || level > 4)
        throw std::invalid_argument("LEVEL must be an actual RNS count in [1,4]");
    result.level = static_cast<unsigned>(level);
    result.output = argv[4];
    if (std::find(operations.begin(), operations.end(), result.operation) == operations.end())
        throw std::invalid_argument("unknown instruction operation");
    if (argc == 6) {
        if (std::string(argv[5]) != "--verify-only") throw std::invalid_argument("unknown option");
        result.verify_only = true;
    }
    if (result.output.empty() || fs::exists(result.output) || fs::is_symlink(result.output))
        throw std::invalid_argument("output must be a new nonempty path");
    return result;
}

std::uint32_t power(std::uint32_t base, std::uint64_t exponent, std::uint32_t q) {
    std::uint64_t result = 1, factor = base;
    while (exponent) {
        if (exponent & 1) result = result * factor % q;
        factor = factor * factor % q;
        exponent >>= 1;
    }
    return static_cast<std::uint32_t>(result);
}

Words input(std::size_t n, std::uint32_t q, unsigned profile, bool right = false) {
    Words words(n);
    const std::array<std::uint32_t, 8> left{{0, 1, q - 1, q - 1, 1, q / 2, q - 2, 17}};
    const std::array<std::uint32_t, 8> other{{0, q - 1, 1, q - 1, 1, q / 2, q - 1, 23}};
    for (std::size_t i = 0; i < n; ++i)
        words[i] = profile ? (right ? other[i % 8] : left[i % 8])
            : static_cast<std::uint32_t>((i * i * 31ULL + i * (right ? 123457ULL : 654323ULL)
                + (right ? 29 : 17)) % q);
    return words;
}

std::string list(const Words &words) {
    std::ostringstream out;
    out << '[';
    for (std::size_t i = 0; i < words.size(); ++i) {
        if (i) out << ',';
        out << words[i];
    }
    return out.str() + ']';
}

std::string quoted(const std::string &text) {
    std::string out = "\"";
    for (char c : text) { if (c == '"') out += '"'; out += c; }
    return out + '"';
}

struct Binding { std::string allocation; runtime::HpuMemSpan span; };

struct Generator {
    const Options &options;
    runtime::HpuMemImage image{1ULL << 20};
    delivery::ApplicationPackageRequest request;
    std::vector<Binding> bindings;
    std::vector<std::string> scenarios;
    std::size_t serial = 0;

    explicit Generator(const Options &value) : options(value) {
        request.scheme = delivery::SchemeKind::ckks;
        request.case_name = "instruction_" + options.operation + "_l" + std::to_string(options.level)
            + "_n" + std::to_string(options.degree);
        request.program.stem = request.case_name;
        request.producer = {"inline-asm", HPU_FRONTEND_COMMIT, HPU_FRONTEND_TREE_STATE};
        request.program.dma_cache_policy = hpu::compiler::DmaCachePolicy::twiddle_loads_only;
        Words records;
        records.reserve(4 * options.level);
        for (unsigned i = 0; i < options.level; ++i) {
            const auto q = moduli[i];
            const auto max = std::numeric_limits<std::uint64_t>::max();
            const auto mu = max / q + (max % q + 1 >= q);
            records.push_back(q);
            records.push_back(static_cast<std::uint32_t>(mu));
            records.push_back(static_cast<std::uint32_t>(mu >> 32));
            records.push_back(0);
        }
        image.add("constants/modulus_table", records, runtime::AllocationKind::modulus_table);
        load(63, "constants/modulus_table", true);
    }

    void emit(const std::string &assembly) {
        const auto encoded = hpu::assemble_source(assembly);
        if (encoded.size() != 1) throw std::logic_error("one helper must emit one actual instruction");
        request.program.instructions.push_back(encoded.front());
        request.program.assembly += encoded.front().normalized_asm + '\n';
    }

    void load(unsigned object, const std::string &allocation, bool modulus = false, bool twiddle = false) {
        emit(hpu::dload(object, modulus ? hpu::DataType::mod_ctx
            : twiddle ? hpu::DataType::twiddle_parameters : hpu::DataType::poly,
            modulus || twiddle ? hpu::DloadFlag::small_bank : hpu::DloadFlag::regular_bank,
            twiddle ? hpu::CachePolicy::allocate : hpu::CachePolicy::no_allocate));
        bindings.push_back({allocation, image.allocation(allocation).span});
    }

    void load_input(unsigned object, const Words &words, const std::string &role) {
        const auto name = "input/" + std::to_string(serial++) + "/" + role;
        image.add(name, words, runtime::AllocationKind::constant);
        load(object, name);
    }

    void store(unsigned object, const Words &golden, unsigned component, unsigned modulus_id,
               const std::string &scenario, bool release = true) {
        const auto name = "output/" + std::to_string(request.outputs.size());
        const auto output = image.reserve(name, options.degree, runtime::AllocationKind::output);
        emit(hpu::dstore(object, release ? 1 : 0));
        bindings.push_back({name, output.span});
        request.outputs.push_back({"step_0", component, static_cast<std::uint8_t>(modulus_id),
            moduli[modulus_id], options.operation == "pntt" || options.operation == "pintt"
                ? delivery::OutputDomain::canonical_ntt_physical : delivery::OutputDomain::coefficient,
            output.span, golden.size(), golden});
        scenarios.push_back(scenario);
        // 每个结果后有独立只读guard，回放和目标端均不得越界写入。
        image.add("guard/" + std::to_string(request.outputs.size()), Words(64, 0xa53cc35aU),
                  runtime::AllocationKind::constant);
    }

    void free(unsigned object) { emit(hpu::pfree(object)); }

    void arithmetic(unsigned layer) {
        const auto q = moduli[layer];
        const auto &op = options.operation;
        const unsigned variants = op == "pmul" ? 10 : 4;
        for (unsigned variant = 0; variant < variants; ++variant) {
            const auto a = input(options.degree, q, variant == 0 || (op == "pmul" && variant == 1) ? 0 : 1);
            const auto b = input(options.degree, q, variant == 0 || (op == "pmul" && variant == 1) ? 0 : 1, true);
            const unsigned dst = op == "padd" || op == "psub" ? (variant == 1 ? 0 : variant == 2 ? 1 : 2)
                : op == "pmul" ? (variant == 2 || variant == 9 ? 0 : 2) : (variant == 3 ? 0 : 2);
            load_input(0, a, "a");
            Words golden(options.degree);
            std::string scenario = op + "/variant" + std::to_string(variant);
            bool right_loaded = false;
            if (op == "padd" || op == "psub") {
                load_input(1, b, "b"); right_loaded = true;
                emit(op == "padd" ? hpu::padd(dst, 0, 1) : hpu::psub(dst, 0, 1));
                if (variant == 3) emit(op == "padd" ? hpu::padd(2, 2, 0) : hpu::psub(2, 2, 0));
                for (std::size_t i = 0; i < golden.size(); ++i) {
                    auto value = op == "padd" ? (std::uint64_t(a[i]) + b[i]) % q
                        : (std::uint64_t(a[i]) + q - b[i]) % q;
                    if (variant == 3) value = op == "padd" ? (value + a[i]) % q : (value + q - a[i]) % q;
                    golden[i] = static_cast<std::uint32_t>(value);
                }
            } else if (op == "pmul") {
                if (variant == 0 || variant == 2) {
                    load_input(1, b, "b"); right_loaded = true;
                    emit(hpu::pmul(dst, 0, 1));
                    for (std::size_t i = 0; i < golden.size(); ++i)
                        golden[i] = static_cast<std::uint32_t>(std::uint64_t(a[i]) * b[i] % q);
                } else if (variant < 8) {
                    const std::array<unsigned, 8> immediates{{0, 7, 0, 0, 1, 255, 64, 192}};
                    const auto immediate = immediates[variant];
                    emit(hpu::pmul_imm(dst, 0, immediate));
                    for (std::size_t i = 0; i < golden.size(); ++i)
                        golden[i] = static_cast<std::uint32_t>(std::uint64_t(a[i]) * immediate % q);
                    scenario += "/imm" + std::to_string(immediate);
                } else {
                    const auto psi = power(roots[layer], (q - 1ULL) / (2 * options.degree), q);
                    const auto c = variant == 8 ? 1U : power(static_cast<std::uint32_t>(options.degree), q - 2ULL, q);
                    const auto ratio = variant == 8 ? psi : power(psi, q - 2ULL, q);
                    const auto name = "tables/q" + std::to_string(layer) + (variant == 8 ? "/pre_twist" : "/post_untwist_scale");
                    image.add(name, hpu::model::pack_online_pmul_parameters(c, ratio, q, options.degree),
                              runtime::AllocationKind::twiddle);
                    load(62, name, false, true);
                    emit(hpu::pmul_online(dst, 0, 62));
                    std::uint64_t factor = c;
                    for (std::size_t i = 0; i < golden.size(); ++i) {
                        golden[i] = static_cast<std::uint32_t>(std::uint64_t(a[i]) * factor % q);
                        factor = factor * ratio % q;
                    }
                    free(62);
                    scenario += variant == 8 ? "/online-pre" : "/online-post-inplace";
                }
            } else {
                const bool immediate = variant == 2;
                const auto initial = variant == 0 ? 0U : variant == 1 ? q - 1U : 1U;
                const auto repeats = variant == 1 ? 2U : 1U;
                if (dst != 0) load_input(2, Words(options.degree, initial), "accumulator");
                if (!immediate) { load_input(1, b, "b"); right_loaded = true; }
                for (unsigned i = 0; i < repeats; ++i)
                    emit(immediate ? hpu::pmac_imm(dst, 0, 255) : hpu::pmac(dst, 0, 1));
                for (std::size_t i = 0; i < golden.size(); ++i) {
                    const auto product = std::uint64_t(a[i]) * (immediate ? 255U : b[i]) % q;
                    golden[i] = static_cast<std::uint32_t>(((dst == 0 ? a[i] : initial) + repeats * product) % q);
                }
            }
            store(dst, golden, variant, layer, scenario);
            if (dst != 0) free(0);
            if (right_loaded && dst != 1) free(1);
        }
    }

    void stage(unsigned layer) {
        const auto q = moduli[layer];
        std::size_t log_n = 0;
        for (auto n = options.degree; n > 1; n >>= 1) ++log_n;
        const auto psi = power(roots[layer], (q - 1ULL) / (2 * options.degree), q);
        hpu::model::HardwareNttModel model(options.degree, q, power(psi, 2, q));
        const bool inverse = options.operation == "pintt";
        const auto tables = inverse ? model.inverse_twiddles().stages : model.forward_twiddles();
        const std::array<std::size_t, 3> stages{{0, 1, log_n - 1}};
        for (unsigned profile = 0; profile < 2; ++profile) {
            for (unsigned selected = 0; selected < stages.size(); ++selected) {
                const auto id = stages[selected];
                const unsigned object = profile ? 2 : 0, parameter = profile ? 3 : 1;
                const auto a = input(options.degree, q, profile);
                Words golden(options.degree);
                if (stage_golden(a.data(), tables[id].data(), golden.data(),
                    static_cast<unsigned>(options.degree), q, static_cast<unsigned>(id), inverse) != 0)
                    throw std::runtime_error("independent C physical-stage oracle rejected input");
                const auto name = "tables/q" + std::to_string(layer) + "/" + options.operation +
                    "/stage" + std::to_string(id) + "/profile" + std::to_string(profile);
                image.add(name, hpu::model::pack_stage_twiddles(tables[id], q, options.degree), runtime::AllocationKind::twiddle);
                load_input(object, a, "stage-data");
                load(parameter, name, false, true);
                emit(inverse ? hpu::pintt(object, parameter, static_cast<int>(id))
                             : hpu::pntt(object, parameter, static_cast<int>(id)));
                store(object, golden, profile * 3 + selected, layer,
                    options.operation + "/profile" + std::to_string(profile) + "/stage" + std::to_string(id));
                free(parameter);
            }
        }
    }

    void modulus_selection() {
        const auto smallest = *std::min_element(moduli.begin(), moduli.begin() + options.level);
        for (unsigned profile = 0; profile < 2; ++profile) {
            const auto a = input(options.degree, smallest, profile);
            const auto b = input(options.degree, smallest, profile, true);
            load_input(0, a, "retained-a"); load_input(1, b, "retained-b");
            // 正向再逆向遍历所有上下文，最终回到0；每个模数有相同四个场景。
            for (unsigned step = 0; step < 2 * options.level; ++step) {
                const auto layer = step < options.level ? step : 2 * options.level - 1 - step;
                emit(hpu::pmodld(layer));
                emit(hpu::pmul(2, 0, 1));
                Words golden(options.degree);
                for (std::size_t i = 0; i < golden.size(); ++i)
                    golden[i] = static_cast<std::uint32_t>(std::uint64_t(a[i]) * b[i] % moduli[layer]);
                store(2, golden, step < options.level ? profile : profile + 2, layer,
                    "pmodld/profile" + std::to_string(profile) + "/context" + std::to_string(layer)
                    + (step + 1 == 2 * options.level ? "/return-first" : ""));
            }
            free(0); free(1);
        }
    }

    void lifetime(unsigned layer) {
        for (unsigned profile = 0; profile < 2; ++profile) {
            const auto object = profile ? 7U : 0U;
            const auto a = input(options.degree, moduli[layer], profile);
            const auto b = input(options.degree, moduli[layer], profile, true);
            load_input(object, a, "discarded-a"); free(object);
            load_input(object, b, "replacement-b");
            // 恒等模乘使本轮PMODLD成为真实计算依赖；不访问已释放的对象。
            emit(hpu::pmul_imm(object, object, 1));
            store(object, b, profile, layer, "pfree/reuse-p" + std::to_string(object));
        }
    }

    void synchronization(unsigned layer) {
        const auto a = input(options.degree, moduli[layer], 0);
        const auto b = input(options.degree, moduli[layer], 0, true);
        load_input(0, a, "dma-a");
        store(0, a, 0, layer, "psync/dma-prefix");
        load_input(0, a, "compute-a"); load_input(1, b, "compute-b");
        emit(hpu::pmul(2, 0, 1));
        Words golden(options.degree);
        for (std::size_t i = 0; i < golden.size(); ++i)
            golden[i] = static_cast<std::uint32_t>(std::uint64_t(a[i]) * b[i] % moduli[layer]);
        store(2, golden, 1, layer, "psync/compute-prefix"); free(0); free(1);
    }

    void finish() {
        if (options.operation == "pmodld") modulus_selection();
        else for (unsigned layer = 0; layer < options.level; ++layer) {
            emit(hpu::pmodld(layer));
            if (options.operation == "pntt" || options.operation == "pintt") stage(layer);
            else if (options.operation == "pfree") lifetime(layer);
            else if (options.operation == "psync") synchronization(layer);
            else arithmetic(layer);
        }
        free(63); emit(hpu::psync());
        image.trim_capacity_to_used_lines();
        request.initial_image = &image;
        hpu::model::InstructionExecutionOptions model_options;
        model_options.ntt_contract = hpu::model::InstructionNttContract::legacy_raw_stage;
        std::vector<hpu::ExecutableDmaSpan> fixed;
        for (const auto &binding : bindings) {
            request.program.ordered_dma_spans.push_back(binding.span);
            fixed.push_back({binding.span.line_offset, binding.span.line_count});
        }
        const auto execution = hpu::model::execute_instructions(request.program.instructions,
            request.program.ordered_dma_spans, image, model_options);
        std::vector<hpu::model::InstructionMemoryExpectation> expected;
        std::vector<bool> writable(image.words().size(), false);
        for (const auto &out : request.outputs) {
            expected.push_back({out.object_id, out.destination, out.golden_words});
            const auto begin = out.destination.line_offset * 64;
            std::fill(writable.begin() + begin, writable.begin() + begin + out.word_count, true);
        }
        const auto comparison = hpu::model::compare_instruction_memory(execution, expected);
        if (!comparison.verified) throw std::runtime_error("independent oracle differs from instruction replay: " + comparison.message);
        for (std::size_t i = 0; i < writable.size(); ++i)
            if (!writable[i] && execution.words[i] != image.words()[i])
                throw std::runtime_error("instruction replay changed readonly/guard word " + std::to_string(i));

        request.program.header = hpu::render_executable_header(request.program.stem, bindings.size());
        const std::string marker = "#ifdef __cplusplus\n}\n#endif\n\n#endif\n";
        const auto at = request.program.header.find(marker);
        if (at == std::string::npos) throw std::logic_error("unexpected official executable header");
        request.program.header.insert(at, "int hpu_run_" + request.program.stem + "(void);\n\n");
        request.program.source = hpu::render_fixed_executable_source(request.program.stem,
            request.program.instructions, image.capacity_lines(), fixed);
        std::ostringstream manifest;
        manifest << "instruction_index,dma_index,operation_index,operation_id,operation_dma_index,direction,object_slot,type_or_release,flag,allocation_id,line_offset,line_count,word_hex,normalized_asm,cp\n";
        const auto relocations = hpu::collect_dma_relocations(request.program.instructions);
        if (relocations.size() != bindings.size()) throw std::logic_error("DMA binding count differs from encoded stream");
        for (std::size_t i = 0; i < bindings.size(); ++i) {
            const auto &r = relocations[i];
            const auto &inst = request.program.instructions[r.instruction_index];
            manifest << r.instruction_index << ',' << i << ",0,tested," << i << ','
                << hpu::to_string(r.direction) << ',' << unsigned(r.object_id) << ',' << unsigned(r.type_or_release)
                << ',' << unsigned(r.flag) << ',' << quoted(bindings[i].allocation) << ','
                << bindings[i].span.line_offset << ',' << bindings[i].span.line_count << ','
                << hpu::format_word_hex(inst.word) << ',' << quoted(inst.normalized_asm) << ',' << unsigned(r.cp) << '\n';
        }
        request.program.resolved_dma_manifest = manifest.str();
        const Words qs(moduli.begin(), moduli.begin() + options.level);
        const std::string abi = "{\"version\":3,\"coefficient_order\":\"natural\",\"pre_twist_order\":\"natural\","
            "\"post_factor_order\":\"natural\",\"stage_twiddle_order\":\"reference_loader_batch_lane\","
            "\"stage_twiddle_format\":\"hpu-twiddle-k8-v1\",\"twiddle_chains\":8,\"stage_parameter_lines\":2,"
            "\"online_pmul_format\":\"hpu-pmul-online-k8-v1\",\"online_pmul_parameter_lines\":2,"
            "\"online_pmul_mode\":1,\"online_pmul_parameter_bank_mask\":32,"
            "\"canonical_ntt_layout\":\"reference_forward_layout\",\"normalization\":\"explicit_post_pmul\",\"twist_fused\":false}";
        request.parameters_json = "{\"test_layer\":\"instruction\",\"encrypted\":false,\"scheme\":\"ckks\","
            "\"poly_modulus_degree\":" + std::to_string(options.degree) + ",\"input_rns_components\":" + std::to_string(options.level)
            + ",\"plain_modulus\":0,\"context_moduli\":" + list(qs) + ",\"key_moduli\":" + list(qs)
            + ",\"levels\":[{\"moduli\":" + list(qs) + "}],\"ntt_table_abi\":" + abi + '}';
        const unsigned count = options.operation == "pmodld" ? 4 : options.operation == "pmul" ? 10
            : options.operation == "pntt" || options.operation == "pintt" ? 6
            : options.operation == "psync" || options.operation == "pfree" ? 2 : 4;
        std::ostringstream scenario_json;
        scenario_json << '[';
        for (std::size_t i = 0; i < scenarios.size(); ++i) {
            if (i) scenario_json << ',';
            scenario_json << "{\"component\":" << request.outputs[i].component
                << ",\"modulus_id\":" << unsigned(request.outputs[i].modulus_id)
                << ",\"modulus\":" << request.outputs[i].modulus
                << ",\"line_offset\":" << request.outputs[i].destination.line_offset
                << ",\"line_count\":" << request.outputs[i].destination.line_count
                << ",\"words\":" << request.outputs[i].word_count
                << ",\"scenario\":\"" << scenarios[i] << "\"}";
        }
        scenario_json << ']';
        request.operation_graph_json = "{\"test_layer\":\"instruction\",\"component_semantics\":\"scenario_not_ciphertext\","
            "\"component_count\":" + std::to_string(count) + ",\"operations\":[{\"id\":\"tested\",\"kind\":\""
            + options.operation + "\",\"operation_index\":0,\"output\":\"output/result\",\"exported\":true,"
            "\"golden_object_id\":\"step_0\"}],\"final_output\":\"output/result\","
            "\"terminal_psync_count\":1,\"timing_verified\":false,\"irq_rearm_verified\":false,"
            "\"scenario_outputs\":" + scenario_json.str()
            + ",\"directed_coverage\":\"original_03_directed_retained\"}";
        request.oracle_report_json = "{\"verification_schema_version\":1,\"test_layer\":\"instruction\","
            "\"overall_status\":\"pass\",\"oracle\":\"independent_u64_modular_and_C_stage_golden\","
            "\"oracle_verified\":true,\"golden_matches_oracle\":true,\"model_verified\":true,"
            "\"raw_physical_words_equal\":true,\"readonly_and_guard_verified\":true,"
            "\"host_instruction_model_verified\":true,\"host_instruction_model\":{\"required\":true,"
            "\"verified\":true,\"status\":\"pass\",\"ntt_contract\":\"legacy_raw_stage\","
            "\"hardware_contract_verified\":false,\"executed_instructions\":"
            + std::to_string(execution.report.executed_instructions) + ",\"compared_words\":"
            + std::to_string(comparison.compared_words) + "},\"instruction_execution_verified\":false,"
            "\"rtl_verified\":false,\"hardware_verified\":false}";
        delivery::validate_application_package_request(request);
        if (!options.verify_only) delivery::write_application_package(options.output, request);
        std::cout << request.case_name << " actual_rns_components=" << options.level
            << " independent_golden=PASS host_instruction_model=PASS readonly_guard=PASS"
            << " output_limbs=" << request.outputs.size() << " hardware=NOT_VERIFIED\n";
    }
};
} // namespace

int main(int argc, char **argv) {
    try {
        const auto options = arguments(argc, argv);
        Generator generator(options);
        generator.finish();
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "instruction case generation failed: " << error.what() << '\n';
        return 1;
    }
}
