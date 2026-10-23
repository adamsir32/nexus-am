#include "fixture.hpp"
#include "hpu/seal/evaluator.hpp"

#include <array>
#include <iostream>

namespace frontend = hpu::seal_adapter;
namespace fs = std::filesystem;

void generate_composite(const std::string &, std::size_t, const fs::path &, bool);

namespace {
struct Options {
    std::string scheme, operation, profile;
    std::size_t degree;
    fs::path output;
    bool verify_only = false;
};

Options arguments(int argc, char **argv) {
    if (argc != 6 && argc != 7)
        throw std::invalid_argument("usage: generator SCHEME OP N kernel|library|regression|primitive OUTPUT [--verify-only]");
    Options options{argv[1], argv[2], argv[4], 0, argv[5], false};
    std::size_t used = 0;
    options.degree = std::stoul(argv[3], &used);
    if (used != std::string(argv[3]).size() || options.degree < 128 || options.degree > 8192 ||
        (options.degree & (options.degree - 1)))
        throw std::invalid_argument("N must be a power of two in [128,8192]");
    if (options.scheme != "ckks" && options.scheme != "bfv" && options.scheme != "bgv")
        throw std::invalid_argument("SCHEME must be ckks, bfv or bgv");
    const std::array<std::string, 5> library_operations{{"hadd", "hmul", "reline", "modswitch", "rotate"}};
    if (options.profile == "kernel" || options.profile == "primitive") {
        if (options.operation != "keyswitch" && options.operation != "ntt" &&
            options.operation != "intt" && options.operation != "bconv")
            throw std::invalid_argument("kernel profile supports keyswitch, ntt, intt or bconv");
        if (options.operation != "keyswitch" && options.scheme != "ckks")
            throw std::invalid_argument("scheme-independent composite kernels use SCHEME=ckks");
        if (options.profile == "primitive" && options.operation == "keyswitch")
            throw std::invalid_argument("keyswitch requires the kernel profile");
    } else if (options.profile == "library" || options.profile == "regression") {
        if (std::find(library_operations.begin(), library_operations.end(), options.operation) == library_operations.end())
            throw std::invalid_argument("unknown library operation");
        if (options.profile == "regression" && options.degree != 4096)
            throw std::invalid_argument("regression profile requires N4096");
    } else throw std::invalid_argument("unknown profile");
    if (argc == 7) {
        if (std::string(argv[6]) != "--verify-only")
            throw std::invalid_argument("unknown option");
        options.verify_only = true;
    }
    if (options.output.empty()) throw std::invalid_argument("output directory is empty");
    if (fs::exists(options.output) || fs::is_symlink(options.output))
        throw std::runtime_error("refusing to overwrite existing output: " + options.output.string());
    return options;
}

void require_equal(const seal::Ciphertext &actual, const seal::Ciphertext &expected,
                   const char *name) {
    if (actual.size() != expected.size() || actual.parms_id() != expected.parms_id() ||
        actual.poly_modulus_degree() != expected.poly_modulus_degree() ||
        actual.coeff_modulus_size() != expected.coeff_modulus_size() ||
        actual.is_ntt_form() != expected.is_ntt_form() || actual.scale() != expected.scale() ||
        actual.correction_factor() != expected.correction_factor())
        throw std::runtime_error(std::string(name) + ": oracle metadata differs from original fixture");
    const auto count = expected.size() * expected.coeff_modulus_size() * expected.poly_modulus_degree();
    if (!std::equal(expected.data(), expected.data() + count, actual.data()))
        throw std::runtime_error(std::string(name) + ": oracle words differ from original fixture");
}

std::size_t expected_node_count(const std::string &operation) {
    return operation == "hmul" ? 2 : 1;
}
} // namespace

int main(int argc, char **argv) {
    try {
        const auto options = arguments(argc, argv);
        if (options.operation == "ntt" || options.operation == "intt" || options.operation == "bconv") {
            generate_composite(options.operation, options.degree, options.output, options.verify_only);
            return 0;
        }
        const bool library = options.profile == "library";
        // 保留原fixture：标准库为CF1/1和半行旋转，kernel/regression为CF3/5和步长1。
        Fixture fixture(options.scheme, options.operation, options.degree, "", 30,
                        library ? static_cast<int>(options.degree / 4) : 1, !library, 0);
        if (fixture.q_rns_count > 4) throw std::runtime_error("group cases require input level <= 4");
        if (library) fixture.stem = "seal_" + fixture.stem;

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

        frontend::CompileOptions compile_options;
        compile_options.require_instruction_verification = true;
        compile_options.optimize_resources = true;
        const auto compiled = application.compile(fixture.stem, compile_options);
        if (!compiled.verified() || !compiled.instruction_verified() ||
            compiled.node_count() != expected_node_count(options.operation))
            throw std::runtime_error("strict frontend verification did not pass");
        require_equal(compiled.oracle_result(output), fixture.expected, "result");
        if (options.operation == "hmul")
            require_equal(compiled.oracle_result(tensor), fixture.tensor, "tensor");
        if (!options.verify_only) {
            auto package = compiled.package();
            package.producer = {"inline-asm", HPU_FRONTEND_COMMIT, HPU_FRONTEND_TREE_STATE};
            hpu::delivery::write_application_package(options.output, package);
        }
        std::cout << fixture.stem << " fixture_raw_words=PASS instruction_model=PASS"
                  << " hardware=NOT_VERIFIED native_package_written=" << !options.verify_only << '\n';
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "group-case generation failed: " << error.what() << '\n';
        return 1;
    }
}
