#include "assembler.hpp"
#include "executable.hpp"

#include <filesystem>
#include <bitset>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>

/* 测试只描述指令序列；所有编码、GPR绑定和可执行C均由锁定的inline-asm生成。 */
int main(int argc, char **argv) {
    try {
        if (argc != 5)
            throw std::invalid_argument("usage: render-program ASM STEM WINDOW_LINES OUTPUT_DIR");
        std::ifstream input(argv[1]);
        if (!input) throw std::runtime_error("cannot read assembly input");
        const std::string assembly((std::istreambuf_iterator<char>(input)), {});
        const std::string stem = argv[2];
        const auto capacity = std::stoull(argv[3]);
        const std::filesystem::path directory = argv[4];
        const auto encoded = hpu::assemble_source(assembly);
        hpu::validate_executable_program(encoded);
        const auto relocations = hpu::collect_dma_relocations(encoded);
        std::filesystem::create_directories(directory);
        auto write = [&](const std::string &name, const std::string &data) {
            std::ofstream stream(directory / name);
            stream << data;
            if (!stream) throw std::runtime_error("cannot write " + name);
        };
        write(stem + ".asm", assembly);
        write(stem + ".h", hpu::render_executable_header(stem, relocations.size()));
        write(stem + ".c", hpu::render_executable_source(stem, encoded, capacity));
        write("dma_relocation_manifest.csv", hpu::render_dma_manifest(encoded));
        std::string words, commands;
        for (const auto &instruction : encoded) {
            words += std::bitset<32>(instruction.word).to_string() + "\n";
            commands += std::bitset<26>(instruction.command26).to_string() + "\n";
        }
        write(stem + ".inst32", words);
        write(stem + ".cmd26", commands);
    } catch (const std::exception &error) {
        std::cerr << "render-program: " << error.what() << '\n';
        return 1;
    }
}
