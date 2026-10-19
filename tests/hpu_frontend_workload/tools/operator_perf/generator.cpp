#include "fixture.hpp"
#include "hpu/seal/evaluator.hpp"

#include <array>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

namespace fs = std::filesystem;
namespace frontend = hpu::seal_adapter;

namespace {
struct Options {
    std::string scheme, operation, profile;
    std::size_t degree = 0;
    fs::path output;
    bool verify_only = false;
    hpu::model::InstructionNttContract contract =
        hpu::model::InstructionNttContract::natural_coefficient_boundaries;
};

std::string quoted(const std::string &value) {
    std::ostringstream out;
    out << '"';
    for (const unsigned char c : value) {
        if (c == '"' || c == '\\') out << '\\' << static_cast<char>(c);
        else if (c < 0x20) out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << unsigned(c);
        else out << static_cast<char>(c);
    }
    out << '"';
    return out.str();
}

Options arguments(int argc, char **argv) {
    if (argc < 6)
        throw std::invalid_argument("usage: generator SCHEME OP N baseline|l16 OUTPUT [--verify-only] [--ntt-contract=legacy-raw-stage]");
    Options options;
    options.scheme = argv[1]; options.operation = argv[2]; options.profile = argv[4]; options.output = argv[5];
    std::size_t used = 0;
    options.degree = std::stoul(argv[3], &used);
    if (used != std::string(argv[3]).size() || (options.degree != 4096 && options.degree != 8192))
        throw std::invalid_argument("operator comparison supports N4096 or N8192");
    if (options.scheme != "ckks" && options.scheme != "bfv" && options.scheme != "bgv")
        throw std::invalid_argument("SCHEME must be ckks, bfv or bgv");
    const std::array<std::string, 6> operations{{"keyswitch", "hadd", "hmul", "reline", "modswitch", "rotate"}};
    if (std::find(operations.begin(), operations.end(), options.operation) == operations.end())
        throw std::invalid_argument("unknown operator");
    if (options.profile != "baseline" && options.profile != "l16")
        throw std::invalid_argument("profile must be baseline or l16");
    if (options.output.empty()) throw std::invalid_argument("output directory is empty");
    for (int i = 6; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--verify-only") options.verify_only = true;
        else if (arg == "--ntt-contract=legacy-raw-stage")
            options.contract = hpu::model::InstructionNttContract::legacy_raw_stage;
        else throw std::invalid_argument("unknown option: " + arg);
    }
    return options;
}

void require_unused_destinations(const Options &options) {
    if (fs::exists(options.output) && !fs::is_directory(options.output))
        throw std::runtime_error("output exists and is not a directory");
    for (const char *name : {"optimized", "noopt", "GENERATION_ERROR.json"}) {
        const auto path = options.output / name;
        if (fs::exists(path) || fs::is_symlink(path))
            throw std::runtime_error("refusing to overwrite existing output: " + path.string());
    }
}

void require_equal(const seal::Ciphertext &actual, const seal::Ciphertext &expected,
                   const std::string &name) {
    if (actual.size() != expected.size() || actual.parms_id() != expected.parms_id() ||
        actual.poly_modulus_degree() != expected.poly_modulus_degree() ||
        actual.coeff_modulus_size() != expected.coeff_modulus_size() ||
        actual.is_ntt_form() != expected.is_ntt_form() || actual.scale() != expected.scale() ||
        actual.correction_factor() != expected.correction_factor())
        throw std::runtime_error(name + ": compiled oracle metadata differs from shared Fixture");
    const auto words = expected.size() * expected.coeff_modulus_size() * expected.poly_modulus_degree();
    if (!std::equal(expected.data(), expected.data() + words, actual.data()))
        throw std::runtime_error(name + ": compiled oracle words differ from shared Fixture");
}

std::vector<std::string> node_operations(const Options &options) {
    if (options.operation == "hmul") return {"multiply", "relinearize"};
    if (options.operation == "keyswitch" || options.operation == "reline") return {"relinearize"};
    if (options.operation == "hadd") return {"add"};
    if (options.operation == "modswitch") return {options.scheme == "ckks" ? "rescale" : "mod_switch"};
    return {options.scheme == "ckks" ? "rotate" : "rotate_rows"};
}

// 原样保留上游小型ABI对象，不重新解释或替换NTT表的含义。
std::string ntt_abi(const std::string &parameters) {
    const auto key = parameters.find("\"ntt_table_abi\"");
    const auto begin = key == std::string::npos ? key : parameters.find('{', key);
    if (begin == std::string::npos) throw std::runtime_error("native package has no ntt_table_abi");
    unsigned depth = 0; bool in_string = false, escaped = false;
    for (std::size_t i = begin; i < parameters.size(); ++i) {
        const char c = parameters[i];
        if (in_string) {
            if (escaped) escaped = false;
            else if (c == '\\') escaped = true;
            else if (c == '"') in_string = false;
        } else if (c == '"') in_string = true;
        else if (c == '{') ++depth;
        else if (c == '}' && --depth == 0) return parameters.substr(begin, i - begin + 1);
    }
    throw std::runtime_error("unterminated native ntt_table_abi");
}

void moduli(std::ostream &out, const std::vector<seal::Modulus> &values,
            std::size_t begin, std::size_t end) {
    out << '[';
    for (auto i = begin; i < end; ++i) {
        if (i != begin) out << ',';
        out << values[i].value();
    }
    out << ']';
}

std::string metadata(const Options &options, const Fixture &fixture,
                     const frontend::CompiledApplication &compiled,
                     const std::string &stem, const std::string &variant) {
    const auto &q = fixture.context->first_context_data()->parms().coeff_modulus();
    const auto &qp = fixture.context->key_context_data()->parms().coeff_modulus();
    const auto &nodes = node_operations(options);
    std::ostringstream out;
    out << std::setprecision(17) << std::boolalpha;
    out << "{\n\"schema\":\"hpu-frontend-operator-perf-fixture\",\"schema_version\":1,\n"
        << "\"scheme\":" << quoted(options.scheme) << ",\"operation\":" << quoted(options.operation)
        << ",\"N\":" << fixture.degree << ",\"degree\":" << fixture.degree
        << ",\"level\":" << q.size() << ",\"profile\":" << quoted(options.profile)
        << ",\"program_stem\":" << quoted(stem) << ",\"variant\":" << quoted(variant)
        << ",\"optimize_resources\":" << (variant == "optimized") << ",\n\"Q\":";
    moduli(out, q, 0, q.size());
    out << ",\"P\":"; moduli(out, qp, q.size(), qp.size());
    out << ",\"input_Q_rns_count\":" << q.size()
        << ",\"output_Q_rns_count\":" << fixture.expected.coeff_modulus_size()
        << ",\"P_rns_count\":" << qp.size() - q.size()
        << ",\"plain_modulus\":" << fixture.context->first_context_data()->parms().plain_modulus().value()
        << ",\"seed\":[\"0x485055534348454d\"," << fixture.degree << ",1,2,3,4,5,6],\n"
        << "\"input_components\":" << fixture.input.size()
        << ",\"left_components\":" << fixture.left.size() << ",\"right_components\":" << fixture.right.size()
        << ",\"output_components\":" << fixture.expected.size()
        << ",\"input_scale\":" << fixture.input.scale() << ",\"left_scale\":" << fixture.left.scale()
        << ",\"right_scale\":" << fixture.right.scale() << ",\"output_scale\":" << fixture.expected.scale()
        << ",\"input_correction_factor\":" << fixture.input.correction_factor()
        << ",\"left_correction_factor\":" << fixture.left.correction_factor()
        << ",\"right_correction_factor\":" << fixture.right.correction_factor()
        << ",\"output_correction_factor\":" << fixture.expected.correction_factor()
        << ",\"rotation_steps\":" << (options.operation == "rotate" ? fixture.rotation_steps : 0)
        << ",\"rotation_generator\":3,\"keyswitch_c0_c1_zero\":" << (options.operation == "keyswitch")
        << ",\"node_count\":" << compiled.node_count() << ",\"node_operations\":[";
    for (std::size_t i = 0; i < nodes.size(); ++i) {
        if (i) out << ',';
        out << quoted(nodes[i]);
    }
    out << "],\n\"verified\":true,\"instruction_verified\":true,"
        << "\"fixture_words_equal\":true,\"fixture_metadata_equal\":true,"
        << "\"hardware_verified\":false,\"hardware_contract_verified\":false,"
        << "\"ntt_contract\":" << quoted(hpu::model::instruction_ntt_contract_name(options.contract))
        << ",\"ntt_table_abi\":" << ntt_abi(compiled.package().parameters_json)
        << ",\"native_package_written\":" << !options.verify_only
        << ",\"producer_commit\":" << quoted(HPU_FRONTEND_COMMIT)
        << ",\"producer_worktree_state\":" << quoted(HPU_FRONTEND_TREE_STATE)
        << ",\"baseline_inline_asm_commit\":" << quoted(HPU_BASELINE_INLINE_COMMIT)
        << ",\"baseline_modified_seal_tree\":" << quoted(HPU_BASELINE_SEAL_TREE)
        << ",\"same_fixture_recipe\":true,\"same_seal_source\":true,"
        << "\"fixture_source\":\"tests/hputest/tools/hpu-scheme-cases/fixture.hpp\","
        << "\"main_comparison_caveat\":" << quoted(options.operation == "hmul"
            ? "Frontend HMUL is explicit multiply+relinearize with two visible graph nodes; main CKKS also has two nodes, while main BFV/BGV use one fused multiply-relinearize node. Final oracle is identical; intermediate output and scheduling obligations may differ."
            : options.operation == "keyswitch"
                ? "KeySwitch uses the shared three-component product with c0/c1 zeroed, then relinearize; it is not the ordinary full-product Reline fixture."
                : "Compare matched logical inputs, final output and issue_to_done_v2 timing; DDR allocation and instruction scheduling may differ.")
        << "\n}\n";
    return out.str();
}

void write_text(const fs::path &path, const std::string &text) {
    if (fs::exists(path) || fs::is_symlink(path))
        throw std::runtime_error("refusing to overwrite " + path.string());
    std::ofstream stream(path);
    stream << text;
    if (!stream) throw std::runtime_error("cannot write " + path.string());
}
} // namespace

int main(int argc, char **argv) {
    Options options;
    std::string stage = "arguments";
    bool may_record_failure = false;
    unsigned native_packages_written = 0;
    try {
        options = arguments(argc, argv);
        require_unused_destinations(options);
        may_record_failure = true;
        stage = "fixture";
        const bool kernel = options.operation == "keyswitch";
        // 和现main及CPU基准直接共享Fixture，原level必须传0，不能传3/4。
        Fixture fixture(options.scheme, options.operation, options.degree, "", 30,
                        kernel ? 1 : static_cast<int>(options.degree / 4), kernel,
                        options.profile == "l16" ? 16 : 0);
        const auto stem = "frontend_" + options.scheme + '_' + options.operation + "_l" +
                          std::to_string(fixture.q_rns_count) + "_n" + std::to_string(options.degree);
        frontend::ApplicationBuilder application(*fixture.context);
        auto evaluator = application.evaluator();
        const auto input = application.import_ciphertext("input/x", fixture.input);
        frontend::Ciphertext output, tensor;
        if (options.operation == "hadd" || options.operation == "hmul") {
            const auto right = application.import_ciphertext("input/right", fixture.right);
            if (options.operation == "hadd") evaluator.add(input, right, output);
            else {
                evaluator.multiply(input, right, tensor);
                evaluator.relinearize(tensor, fixture.relin, output);
            }
        } else if (options.operation == "keyswitch" || options.operation == "reline")
            evaluator.relinearize(input, fixture.relin, output);
        else if (options.operation == "modswitch") {
            if (options.scheme == "ckks") evaluator.rescale_to_next(input, output);
            else evaluator.mod_switch_to_next(input, output);
        } else if (options.scheme == "ckks")
            evaluator.rotate_vector(input, fixture.rotation_steps, fixture.galois, output);
        else evaluator.rotate_rows(input, fixture.rotation_steps, fixture.galois, output);
        application.mark_output("result", output);

        const std::array<std::string, 2> variants{{"optimized", "noopt"}};
        std::vector<frontend::CompiledApplication> compiled;
        std::vector<std::string> sidecars;
        // 两个变体全部严格通过后才发布文件，失败不产生可运行的替代包。
        for (const auto &variant : variants) {
            stage = "compile." + variant;
            frontend::CompileOptions compile_options;
            compile_options.optimize_resources = variant == "optimized";
            compile_options.require_instruction_verification = true;
            compile_options.instruction_ntt_contract = options.contract;
            compiled.push_back(application.compile(stem, compile_options));
            const auto &result = compiled.back();
            if (!result.verified() || !result.instruction_verified())
                throw std::runtime_error("strict frontend verification did not pass");
            if (result.node_count() != node_operations(options).size())
                throw std::runtime_error("compiled operator node count differs from requested semantics");
            require_equal(result.oracle_result(output), fixture.expected, variant + ".result");
            if (options.operation == "hmul")
                require_equal(result.oracle_result(tensor), fixture.tensor, variant + ".tensor");
            sidecars.push_back(metadata(options, fixture, result, stem, variant));
        }
        for (std::size_t i = 0; i < variants.size(); ++i) {
            stage = "publish." + variants[i];
            const auto directory = options.output / variants[i];
            fs::create_directories(directory);
            if (!options.verify_only) {
                auto request = compiled[i].package();
                request.producer = {"inline-asm", HPU_FRONTEND_COMMIT, HPU_FRONTEND_TREE_STATE};
                hpu::delivery::write_application_package(directory / "upstream", request);
                ++native_packages_written;
            }
            write_text(directory / "RESOURCE_REPORT.json", compiled[i].resource_report_json() + '\n');
            write_text(directory / "PERF_FIXTURE.json", sidecars[i]);
            std::cout << stem << " variant=" << variants[i]
                      << " fixture_raw_words=PASS instruction_model=PASS hardware=NOT_VERIFIED"
                      << " native_package_written=" << (!options.verify_only ? 1 : 0) << '\n';
        }
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "frontend operator generation failed at " << stage << ": " << error.what() << '\n';
        if (may_record_failure) {
            try {
                fs::create_directories(options.output);
                std::ostringstream failure;
                failure << "{\"status\":\"FAIL\",\"stage\":" << quoted(stage)
                        << ",\"scheme\":" << quoted(options.scheme) << ",\"operation\":" << quoted(options.operation)
                        << ",\"N\":" << options.degree << ",\"profile\":" << quoted(options.profile)
                        << ",\"require_instruction_verification\":true,\"hardware_verified\":false,"
                        << "\"ntt_contract\":" << quoted(hpu::model::instruction_ntt_contract_name(options.contract))
                        << ",\"native_packages_written\":" << native_packages_written
                        << ",\"error\":" << quoted(error.what()) << "}\n";
                write_text(options.output / "GENERATION_ERROR.json", failure.str());
            } catch (const std::exception &record_error) {
                std::cerr << "cannot record generation failure: " << record_error.what() << '\n';
            }
        }
        return 1;
    }
}
