#include "assembler.hpp"
#include "executable.hpp"
#include "hpu/model/hardware_ntt.hpp"

#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {
constexpr unsigned kN = 4096;
constexpr std::uint32_t kQ = 50061313;

void write_text(const fs::path& path, const std::string& text) {
    fs::create_directories(path.parent_path());
    std::ofstream out(path);
    if (!(out << text)) throw std::runtime_error("不能写入 " + path.string());
}

void write_words(const fs::path& path, const std::vector<std::uint32_t>& words) {
    fs::create_directories(path.parent_path());
    std::ofstream out(path, std::ios::binary);
    for (auto word : words) {
        const char bytes[] = {char(word), char(word >> 8), char(word >> 16), char(word >> 24)};
        out.write(bytes, 4);
    }
    if (!out) throw std::runtime_error("不能写入 " + path.string());
}

std::vector<std::uint32_t> input(unsigned profile, bool second) {
    std::vector<std::uint32_t> values(kN);
    const std::uint32_t edge_a[] = {0, 1, kQ-1, kQ-2, 0, 1, kQ-1, kQ-2};
    const std::uint32_t edge_b[] = {0, 1, 1, kQ-1, kQ-1, kQ-2, kQ-1, kQ-2};
    // AM确定性输入，不声明为上游reference向量。
    std::uint32_t state = second ? 0x48505542U : 0x48505541U;
    for (unsigned i = 0; i < kN; ++i) {
        state = state * 1664525U + 1013904223U;
        values[i] = profile ? (second ? edge_b[i % 8] : edge_a[i % 8]) : state % kQ;
    }
    return values;
}

std::uint32_t primitive_omega() {
    for (std::uint32_t candidate = 2; candidate < kQ; ++candidate) {
        const auto omega = hpu::model::pow_mod(candidate, (kQ-1) / kN, kQ);
        if (hpu::model::pow_mod(omega, kN, kQ) == 1 &&
            hpu::model::pow_mod(omega, kN/2, kQ) == kQ-1) return omega;
    }
    throw std::runtime_error("找不到4096阶本原根");
}

void generate(const fs::path& root, const std::string& commit) {
    const auto mm = root / "inline-asm/mm";
    std::string header = "#ifndef HPU_INLINE_ASM_MM_DELIVERY_H\n#define HPU_INLINE_ASM_MM_DELIVERY_H\n#include <stdint.h>\n";
    header += "/* 由当前64对象编码器生成，禁止复用旧ISA头文件。 */\n";
    header += "#define HPU_INLINE_ASM_ISA_VERSION 12\n#define HPU_INLINE_ASM_SOURCE_COMMIT \"" + commit + "\"\n";
    header += "#define HPU_MM_COEFFICIENTS 4096U\n#define HPU_MM_MODULUS UINT32_C(50061313)\n";
    header += "#define HPU_MM_REQUIRED_WINDOW_LINES 193U\n#define HPU_MM_LINE_BYTES 256U\n#define HPU_MM_WORDS_PER_LINE 64U\n";
    for (const auto& row : std::array<std::pair<const char*, unsigned>, 8>{{
             {"SRC_A",0}, {"SRC_B",64}, {"OUTPUT",128}, {"MOD",192},
             {"LINES_SRC_A",64}, {"LINES_SRC_B",64}, {"LINES_OUTPUT",64}, {"LINES_MOD",1}}}) {
        const std::string name = row.first;
        header += "#define HPU_MM_" + (name.rfind("LINES_", 0) == 0 ? name : "LINE_"+name) + " " + std::to_string(row.second) + "U\n";
    }
    std::string encodings = "macro_name\tword_hex\tnormalized_asm\n";
    auto add = [&](const std::string& macro, const std::string& assembly) {
        const auto encoded = hpu::assemble_line(assembly);
        const auto hex = hpu::format_word_hex(encoded.word);
        header += "/* " + encoded.normalized_asm + " */\n#define " + macro + " UINT32_C(" + hex + ")\n";
        encodings += macro + "\t" + hex + "\t" + encoded.normalized_asm + "\n";
    };
    for (unsigned obj = 0; obj < 8; ++obj) {
        const auto p = "P"+std::to_string(obj);
        const auto operand = "p"+std::to_string(obj);
        add("HPU_INSN_DLOAD_"+p+"_POLY", "dload x10, x11, "+operand+", 0, 0, 0");
        for (unsigned release = 0; release < 2; ++release)
            add("HPU_INSN_DSTORE_"+p+(release ? "_RELEASE" : "_KEEP"),
                "dstore x10, x11, "+operand+", "+std::to_string(release)+", 0");
        add("HPU_INSN_PFREE_"+p, "pfree "+operand);
    }
    add("HPU_INSN_DLOAD_P4_MOD", "dload x10, x11, p4, 1, 0, 0x20");
    add("HPU_INSN_DLOAD_P1_TWIDDLE", "dload x10, x11, p1, 0, 1, 0x20");
    add("HPU_INSN_DLOAD_P3_TWIDDLE", "dload x10, x11, p3, 0, 1, 0x20");
    for (unsigned context = 0; context <= 6; ++context)
        add("HPU_INSN_PMODLD_"+std::to_string(context), "pmodld "+std::to_string(context));
    for (const std::string operation : {"padd", "psub", "pmul", "pmac"}) {
        auto upper = operation;
        for (auto& letter : upper) letter -= 'a'-'A';
        for (const auto& operands : std::array<std::array<unsigned,3>,7>{{
                 {{2,0,1}}, {{0,0,1}}, {{1,0,1}}, {{2,1,0}}, {{7,0,1}}, {{2,2,0}}, {{2,2,1}}}}) {
            std::string macro = "HPU_INSN_"+upper;
            std::string assembly = operation+" ";
            for (unsigned i = 0; i < 3; ++i) {
                macro += "_P"+std::to_string(operands[i]);
                assembly += (i ? ", p" : "p")+std::to_string(operands[i]);
            }
            add(macro, assembly);
        }
        if (operation == "pmul" || operation == "pmac")
            for (unsigned dst : {0U,2U}) for (unsigned immediate : {0U,1U,7U,255U})
                add("HPU_INSN_"+upper+"_IMM"+std::to_string(immediate)+"_P"+std::to_string(dst)+"_P0",
                    operation+" p"+std::to_string(dst)+", p0, "+std::to_string(immediate));
    }
    for (const std::string operation : {"pntt", "pintt"}) {
        const std::string upper = operation == "pntt" ? "PNTT" : "PINTT";
        for (unsigned data : {0U,2U}) for (unsigned stage = 0; stage < 12; ++stage) {
            const auto parameter = data == 0 ? 1 : 3;
            add("HPU_INSN_"+upper+"_P"+std::to_string(data)+"_P"+std::to_string(parameter)+"_STAGE"+std::to_string(stage),
                operation+" p"+std::to_string(data)+", p"+std::to_string(parameter)+", "+std::to_string(stage)+", 0, 0");
        }
    }
    add("HPU_INSN_PSYNC", "psync");
    header += "#endif\n";
    write_text(root / "include/hpu/inline_asm_mm_delivery.h", header);
    write_text(root / "lowlevel-encodings.tsv", encodings);
    const auto program = hpu::assemble_source(
        "dload x10,x11,p4,1,0,0x20\npmodld 0\ndload x10,x11,p0,0,0,0\n"
        "dload x10,x11,p1,0,0,0\npmul p2,p0,p1\npfree p0\npfree p1\n"
        "dstore x10,x11,p2,1,0\npfree p4\npsync\n");
    write_text(mm / "mm.h", hpu::render_executable_header("mm", 4));
    write_text(mm / "mm.c", hpu::render_executable_source("mm", program, 256));
    const auto a = input(0, false);
    const auto b = input(0, true);
    auto expected = a;
    for (unsigned i = 0; i < kN; ++i) expected[i] = std::uint64_t(a[i])*b[i] % kQ;
    const auto hardware = mm / "test_data/hardware";
    write_words(hardware / "images/input_a.u32.bin", a);
    write_words(hardware / "images/input_b.u32.bin", b);
    write_words(hardware / "images/expected.u32.bin", expected);
    const auto mu = UINT64_MAX / kQ;
    std::vector<std::uint32_t> modulus(64);
    modulus[0] = kQ;
    modulus[1] = static_cast<std::uint32_t>(mu);
    modulus[2] = static_cast<std::uint32_t>(mu >> 32);
    write_words(hardware / "constants/mod_ctx.u32.bin", modulus);

    const auto omega = primitive_omega();
    hpu::model::HardwareNttModel model(kN, kQ, omega);
    const auto forward = model.forward_twiddles();
    const auto backward = model.inverse_twiddles();
    for (unsigned inverse = 0; inverse < 2; ++inverse) for (unsigned stage : {0U,1U,11U}) {
        const std::string stem = std::string(inverse ? "intt" : "ntt")+"_stage_"+(stage<10 ? "0" : "")+std::to_string(stage);
        const auto& full = inverse ? backward.stages[stage] : forward[stage];
        const auto packed = hpu::model::pack_stage_twiddles(full, kQ, kN);
        if (hpu::model::expand_stage_twiddles(packed,kQ,kN) != full)
            throw std::runtime_error("K8展开与完整表不一致");
        write_words(root / "instruction-data" / (stem+".u32.bin"), packed);
        write_words(root / "instruction-data" / (stem+"_full.u32.bin"), full);
        for (unsigned profile = 0; profile < 2; ++profile) {
            const auto data = input(profile, false);
            const auto oracle = hpu::model::execute_ntt_stage(data,full,kQ,stage,inverse);
            write_words(root / "stage-model" / (stem+"_profile"+std::to_string(profile)+".u32.bin"), oracle);
        }
    }
    write_words(root / "stage-model/edge_a.u32.bin", input(1, false));
    write_text(root / "lowlevel-producer.txt", commit+"\n");
}
}

int main(int argc, char** argv) {
    try {
        if (argc != 3) throw std::runtime_error("用法：generate-lowlevel 输出目录 producer提交");
        generate(fs::absolute(argv[1]), argv[2]);
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "低层数据生成失败：" << error.what() << '\n';
        return 1;
    }
}
