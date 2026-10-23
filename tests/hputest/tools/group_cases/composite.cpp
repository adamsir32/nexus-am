#include "assembler.hpp"
#include "executable.hpp"
#include "hpu/delivery/resource_compiler.hpp"
#include "hpu/model/hardware_ntt.hpp"
#include "hpu/seal/application_image.hpp"
#include "util/bconv.hpp"
#include "util/ntt.hpp"
#include <seal/util/ntt.h>
#include <seal/util/rns.h>

#include <algorithm>
#include <iostream>
#include <limits>
#include <sstream>

namespace fs = std::filesystem;
namespace runtime = hpu::runtime;
namespace resource = hpu::resource;
namespace delivery = hpu::delivery;
using Words = std::vector<std::uint32_t>;

namespace {
const std::string ntt_abi =
    std::string("{\"version\":3,\"coefficient_order\":\"natural\",\"pre_twist_order\":\"natural\","
    "\"post_factor_order\":\"natural\",\"stage_twiddle_order\":\"reference_loader_batch_lane\","
    "\"stage_twiddle_format\":\"hpu-twiddle-k8-v1\",\"twiddle_chains\":8,\"stage_parameter_lines\":2,"
    "\"online_pmul_format\":\"") + hpu::model::kOnlinePmulParameterFormat +
    "\",\"online_pmul_parameter_lines\":" + std::to_string(hpu::model::kOnlinePmulParameterLines) +
    ",\"online_pmul_mode\":1,\"online_pmul_parameter_bank_mask\":32,"
    "\"canonical_ntt_layout\":\"reference_forward_layout\",\"normalization\":\"explicit_post_pmul\","
    "\"twist_fused\":false}";

std::string list(const Words &words) {
    std::ostringstream out;
    out << '[';
    for (std::size_t i = 0; i < words.size(); ++i) {
        if (i) out << ',';
        out << words[i];
    }
    return out.str() + ']';
}

std::string allocation_id(const runtime::HpuMemImage &image, runtime::HpuMemSpan span) {
    for (const auto &allocation : image.allocations())
        if (allocation.span.line_offset <= span.line_offset &&
            allocation.span.line_offset + allocation.span.line_count >= span.line_offset + span.line_count)
            return allocation.id;
    throw std::runtime_error("DMA span has no containing allocation");
}

delivery::ApplicationPackageRequest request_base(const std::string &operation,
    std::size_t degree, const Words &q, const Words &all, runtime::HpuMemImage &image) {
    delivery::ApplicationPackageRequest request;
    request.scheme = delivery::SchemeKind::ckks;
    request.case_name = operation + "_l" + std::to_string(q.size()) + "_n" + std::to_string(degree);
    request.producer = {"inline-asm", HPU_FRONTEND_COMMIT, HPU_FRONTEND_TREE_STATE};
    request.program.stem = request.case_name;
    request.initial_image = &image;
    request.parameters_json = "{\"scheme\":\"ckks\",\"poly_modulus_degree\":" + std::to_string(degree) +
        ",\"plain_modulus\":0,\"key_moduli\":" + list(all) + ",\"ntt_table_abi\":" + ntt_abi +
        ",\"levels\":[{\"moduli\":" + list(q) + "}]}";
    request.operation_graph_json = "{\"operations\":[{\"id\":\"tested\",\"kind\":\"" + operation +
        "\",\"operation_index\":0,\"output\":\"output/result\",\"exported\":true,"
        "\"golden_object_id\":\"step_0\"}],\"final_output\":\"output/result\"}";
    return request;
}

void bind_program(delivery::ApplicationPackageRequest &request,
    resource::OperatorProgram program, const std::string &assembly,
    const std::vector<runtime::HpuMemSpan> &spans, const runtime::HpuMemImage &image) {
    request.program.assembly = assembly;
    request.program.instructions = hpu::assemble_source(assembly);
    request.program.operator_program = std::make_shared<resource::OperatorProgram>(std::move(program));
    request.program.ordered_dma_spans = spans;
    const auto relocations = hpu::collect_dma_relocations(request.program.instructions);
    if (relocations.size() != spans.size()) throw std::runtime_error("composite DMA recipe differs from upstream codegen");
    for (std::size_t i = 0; i < spans.size(); ++i) {
        hpu::compiler::ResolvedDma binding;
        binding.instruction_index = relocations[i].instruction_index;
        binding.allocation_id = allocation_id(image, spans[i]);
        binding.span = spans[i];
        binding.operation_index = 0;
        binding.operation_id = "tested";
        binding.operation_dma_index = i;
        request.program.resource_dma.push_back(std::move(binding));
    }
}

void verify_and_publish(delivery::ApplicationPackageRequest &request, runtime::HpuMemImage &image,
                        const fs::path &output, bool verify_only, const std::string &oracle) {
    // 先以独立SEAL数学oracle核对编码回放，再由公共编译器严格验证优化后程序和等价性。
    const auto replay = hpu::model::execute_instructions(
        request.program.instructions, request.program.ordered_dma_spans, image);
    std::vector<hpu::model::InstructionMemoryExpectation> expected;
    for (const auto &limb : request.outputs)
        expected.push_back({limb.object_id, limb.destination, limb.golden_words});
    const auto compared = hpu::model::compare_instruction_memory(replay, expected);
    if (!compared.verified) throw std::runtime_error("composite baseline differs from SEAL oracle: " + compared.message);
    request.oracle_report_json = "{\"verification_schema_version\":1,\"overall_status\":\"pass\","
        "\"oracle\":\"" + oracle + "\",\"golden_source\":\"independent SEAL mathematical oracle\","
        "\"oracle_verified\":true,\"golden_matches_oracle\":true,\"model_verified\":true,"
        "\"raw_physical_words_equal\":true,\"verified_limb_count\":" + std::to_string(request.outputs.size()) +
        ",\"instruction_execution_verified\":false,\"rtl_verified\":false,\"hardware_verified\":false}";
    delivery::compile_application_resources(request, image, true, true);
    if (!verify_only) delivery::write_application_package(output, request);
    std::cout << request.case_name << " fixture_raw_words=PASS instruction_model=PASS"
              << " hardware=NOT_VERIFIED native_package_written=" << !verify_only << '\n';
}

std::size_t bit_reverse(std::size_t value, std::size_t degree) {
    std::size_t result = 0;
    for (std::size_t span = degree; span > 1; span >>= 1) {
        result = (result << 1) | (value & 1);
        value >>= 1;
    }
    return result;
}

void transform(const std::string &operation, std::size_t degree, std::size_t level,
               const fs::path &output, bool verify_only) {
    seal::EncryptionParameters parameters(seal::scheme_type::ckks);
    parameters.set_poly_modulus_degree(degree);
    const auto original = seal::CoeffModulus::Create(degree, {27, 27, 27, 27, 27});
    std::vector<seal::Modulus> selected(original.begin(), original.begin() + level);
    selected.push_back(original.back());
    parameters.set_coeff_modulus(selected);
    seal::SEALContext context(parameters, true, seal::sec_level_type::none);
    if (!context.parameters_set()) throw std::runtime_error("invalid transform context");
    hpu::seal_adapter::CkksApplicationImageBuilder builder(context, 1ULL << 24);
    const auto modulus_table = builder.add_modulus_table();
    const auto tables = builder.add_canonical_twiddles();
    runtime::HpuMemImage image = builder.image();
    const bool inverse = operation == "intt";
    Words all, q;
    for (const auto &mod : parameters.coeff_modulus()) all.push_back(static_cast<std::uint32_t>(mod.value()));
    q.assign(all.begin(), all.begin() + level);
    auto request = request_base(operation, degree, q, all, image);
    std::vector<runtime::HpuMemSpan> inputs, results;
    for (std::size_t limb = 0; limb < level; ++limb) {
        const auto &table = tables.at(limb);
        const auto modulus = table.modulus;
        if (modulus != q[limb]) throw std::runtime_error("transform modulus order differs from Q");
        Words coefficients(degree);
        for (std::size_t i = 0; i < degree; ++i)
            coefficients[i] = static_cast<std::uint32_t>(
                (i * 1234567ULL + i * i * 31ULL + limb * 891011ULL + 7) % modulus);

        // SEAL使用bit-reversed逻辑NTT顺序；只转换布局，不用HPU算术生成golden。
        std::vector<std::uint64_t> seal_ntt(coefficients.begin(), coefficients.end());
        seal::util::ntt_negacyclic_harvey(
            seal_ntt.data(), context.key_context_data()->small_ntt_tables()[limb]);
        hpu::model::HardwareNttModel model(degree, modulus,
            hpu::model::pow_mod(table.canonical_psi, 2, modulus));
        const auto layout = model.forward_layout();
        Words physical(degree);
        for (std::size_t i = 0; i < degree; ++i) physical[i] = seal_ntt[bit_reverse(layout[i], degree)];
        if (hpu::model::negacyclic_forward(coefficients, modulus, table.canonical_psi) != physical)
            throw std::runtime_error("independent SEAL NTT layout comparison failed");
        const auto suffix = "/q" + std::to_string(limb);
        inputs.push_back(image.add("input/x" + suffix, inverse ? physical : coefficients,
                                   runtime::AllocationKind::constant).span);
        results.push_back(image.reserve("output/result" + suffix, degree,
                                        runtime::AllocationKind::output).span);
        request.outputs.push_back({"step_0", 0, static_cast<std::uint8_t>(limb), modulus,
            inverse ? delivery::OutputDomain::coefficient : delivery::OutputDomain::canonical_ntt_physical,
            results.back(), degree, inverse ? coefficients : physical});
    }
    image.trim_capacity_to_used_lines();

    resource::Recording recording;
    const auto data = resource::make_operand("data", 0);
    const auto twiddle = resource::make_operand("twiddle", 1);
    const auto mod = resource::make_operand("modulus", 2);
    auto assembly = resource::read(mod, hpu::DataType::mod_ctx, hpu::DloadFlag::small_bank);
    std::vector<runtime::HpuMemSpan> spans{modulus_table};
    for (std::size_t limb = 0; limb < level; ++limb) {
        const auto &table = tables.at(limb);
        const auto prefix = "transform/q" + std::to_string(limb);
        assembly += resource::select_modulus(static_cast<int>(limb));
        assembly += resource::read(data, hpu::DataType::poly);
        assembly += inverse ? generate_hpu_intt_body_asm(static_cast<int>(degree), data, twiddle, false, prefix)
                            : generate_hpu_ntt_body_asm(static_cast<int>(degree), data, twiddle, false, prefix);
        assembly += resource::publish(data);
        spans.push_back(inputs[limb]);
        if (!inverse) spans.push_back(table.pre_twist);
        const auto &stages = inverse ? table.inverse_stages : table.forward_stages;
        spans.insert(spans.end(), stages.begin(), stages.end());
        if (inverse) spans.push_back(table.post_untwist_scale);
        spans.push_back(results[limb]);
    }
    assembly += resource::discard(mod);
    assembly += resource::finish_program();
    bind_program(request, recording.finish(), assembly, spans, image);
    verify_and_publish(request, image, output, verify_only, "modified-SEAL util::ntt_negacyclic_harvey");
}

void bconv(std::size_t degree, std::size_t level, const fs::path &output, bool verify_only) {
    // 保留04的FastBConv语义和原基前缀，禁止用精确CRT替代近似转换。
    const Words original_q{50061313, 50077697, 50307073, 50552833};
    const Words q(original_q.begin(), original_q.begin() + level);
    const Words p{90062849, 90095617, 90218497};
    Words all = q;
    all.insert(all.end(), p.begin(), p.end());
    const auto pool = seal::MemoryManager::GetPool();
    std::vector<seal::Modulus> qs, ps;
    for (auto modulus : q) qs.emplace_back(modulus);
    for (auto modulus : p) ps.emplace_back(modulus);
    const seal::util::RNSBase qbase(qs, pool), pbase(ps, pool);
    const seal::util::BaseConverter converter(qbase, pbase, pool);
    std::vector<std::uint64_t> input_words(q.size() * degree), oracle(p.size() * degree);
    for (std::size_t j = 0; j < q.size(); ++j)
        for (std::size_t i = 0; i < degree; ++i)
            input_words[j * degree + i] = (i * 1234567ULL + j * 891011ULL + i * i * 31ULL + 7) % q[j];
    converter.fast_convert_array(seal::util::ConstRNSIter(input_words.data(), degree),
        seal::util::RNSIter(oracle.data(), degree), pool);
    runtime::HpuMemImage image(1ULL << 24);
    Words mod_words;
    for (auto modulus : all) {
        const auto maximum = std::numeric_limits<std::uint64_t>::max();
        const auto mu = maximum / modulus + (maximum % modulus + 1 >= modulus);
        mod_words.insert(mod_words.end(), {modulus, static_cast<std::uint32_t>(mu),
            static_cast<std::uint32_t>((mu >> 32) & 0xffffU), 0});
    }
    const auto mod_table = image.add("constants/modulus_table", mod_words, runtime::AllocationKind::modulus_table);
    std::vector<runtime::HpuMemSpan> sources, inverses, normalized, results;
    std::vector<std::vector<runtime::HpuMemSpan>> constants(p.size());
    for (std::size_t j = 0; j < q.size(); ++j) {
        sources.push_back(image.add("input/q" + std::to_string(j),
            Words(input_words.begin() + j * degree, input_words.begin() + (j + 1) * degree),
            runtime::AllocationKind::constant).span);
        const auto inverse = qbase.inv_punctured_prod_mod_base_array()[j].operand;
        inverses.push_back(image.add("constants/qhat_inverse/q" + std::to_string(j),
            Words(degree, static_cast<std::uint32_t>(inverse)), runtime::AllocationKind::constant).span);
        normalized.push_back(image.reserve("scratch/normalized/q" + std::to_string(j), degree,
            runtime::AllocationKind::workspace).span);
    }
    for (std::size_t k = 0; k < p.size(); ++k) {
        for (std::size_t j = 0; j < q.size(); ++j) {
            std::uint64_t product = 1;
            for (std::size_t l = 0; l < q.size(); ++l) if (l != j) product = product * q[l] % p[k];
            constants[k].push_back(image.add("constants/qhat_mod_p/p" + std::to_string(k) + "/q" + std::to_string(j),
                Words(degree, static_cast<std::uint32_t>(product)), runtime::AllocationKind::constant).span);
        }
        results.push_back(image.reserve("output/p" + std::to_string(k), degree, runtime::AllocationKind::output).span);
    }
    image.trim_capacity_to_used_lines();
    auto request = request_base("bconv", degree, q, all, image);
    for (std::size_t k = 0; k < p.size(); ++k)
        request.outputs.push_back({"step_0", 0, static_cast<std::uint8_t>(q.size() + k), p[k],
            delivery::OutputDomain::coefficient, results[k], degree,
            Words(oracle.begin() + k * degree, oracle.begin() + (k + 1) * degree)});
    resource::Recording recording;
    const auto assembly = generate_hpu_bconv_body_asm(static_cast<int>(level), 3, 0, true, true);
    std::vector<runtime::HpuMemSpan> spans{mod_table.span};
    for (std::size_t j = 0; j < q.size(); ++j)
        spans.insert(spans.end(), {sources[j], inverses[j], normalized[j]});
    for (std::size_t k = 0; k < p.size(); ++k) {
        for (std::size_t j = 0; j < q.size(); ++j)
            spans.insert(spans.end(), {normalized[j], constants[k][j]});
        spans.push_back(results[k]);
    }
    bind_program(request, recording.finish(), assembly, spans, image);
    verify_and_publish(request, image, output, verify_only,
        "modified-SEAL util::BaseConverter::fast_convert_array Q" + std::to_string(level) + " to P3");
}
} // namespace

void generate_composite(const std::string &operation, std::size_t degree, std::size_t level,
                        const fs::path &output, bool verify_only) {
    if (operation == "bconv") bconv(degree, level, output, verify_only);
    else transform(operation, degree, level, output, verify_only);
}
