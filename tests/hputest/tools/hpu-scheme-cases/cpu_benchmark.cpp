#include "fixture.hpp"
#include <chrono>
#include <cstring>
#include <iostream>

/* 188服务器可执行同一Fixture和modified-SEAL；不把主机墙钟冒充SCPU cycle。 */
int main(int argc, char **argv) {
    try {
        if (argc != 5)
            throw std::invalid_argument("usage: hpu_cpu_benchmark ckks|bfv|bgv OP N ROUNDS");
        const std::string scheme=argv[1], operation=argv[2];
        if (scheme!="ckks" && scheme!="bfv" && scheme!="bgv")
            throw std::invalid_argument("unknown scheme");
        const auto n=std::stoul(argv[3]);
        const auto rounds=std::stoul(argv[4]);
        if (rounds==0 || rounds>1000) throw std::invalid_argument("rounds must be 1..1000");
        Fixture f(scheme,operation,n,"",30,operation=="keyswitch" ? 1 : n/4,
                  operation=="keyswitch");
        seal::Evaluator evaluator(*f.context);
        std::uint64_t total=0, minimum=UINT64_MAX, maximum=0;
        for (unsigned round=0;round<rounds;++round) {
            seal::Ciphertext output, tensor;
            const auto start=std::chrono::steady_clock::now();
            if (operation=="hadd") evaluator.add(f.left,f.right,output);
            else if (operation=="hmul") {
                evaluator.multiply(f.left,f.right,tensor);
                evaluator.relinearize(tensor,f.relin,output);
            } else if (operation=="reline" || operation=="keyswitch")
                evaluator.relinearize(f.input,f.relin,output);
            else if (operation=="modswitch") {
                if (scheme=="ckks") evaluator.rescale_to_next(f.input,output);
                else evaluator.mod_switch_to_next(f.input,output);
            } else if (operation=="rotate") {
                if (scheme=="ckks") evaluator.rotate_vector(f.input,f.rotation_steps,f.galois,output);
                else evaluator.rotate_rows(f.input,f.rotation_steps,f.galois,output);
            }
            const auto end=std::chrono::steady_clock::now();
            const auto elapsed=std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count();
            const auto words=f.expected.size()*f.expected.coeff_modulus_size()*n;
            if (output.size()!=f.expected.size() || output.parms_id()!=f.expected.parms_id() ||
                output.scale()!=f.expected.scale() || output.correction_factor()!=f.expected.correction_factor() ||
                std::memcmp(output.data(),f.expected.data(),words*sizeof(std::uint64_t))!=0)
                throw std::runtime_error("CPU output differs from fixed SEAL golden");
            const auto ns=static_cast<std::uint64_t>(elapsed);
            total+=ns; minimum=std::min(minimum,ns); maximum=std::max(maximum,ns);
            std::cout << "CPU_SAMPLE scheme="<<scheme<<" op="<<operation<<" N="<<n
                      <<" round="<<round<<" ns="<<ns<<" raw_words_equal=1\n";
        }
        std::cout << "CPU_STATS rounds="<<rounds<<" average_ns="<<total/rounds
                  <<" min_ns="<<minimum<<" max_ns="<<maximum<<" spread_ns="<<maximum-minimum<<'\n';
    } catch (const std::exception &error) {
        std::cerr<<error.what()<<'\n'; return 1;
    }
}
