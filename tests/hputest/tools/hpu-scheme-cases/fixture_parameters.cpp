#include "fixture.hpp"
#include "hpu/seal/bfv_level.hpp"
#include <iomanip>
#include <iostream>

template<class Container> void array(const Container &values) {
    std::cout << '['; bool first=true;
    for (const auto &value:values) { if (!first) std::cout<<','; first=false; std::cout<<value; }
    std::cout<<']';
}

/* 从真实Fixture/SEAL对象提取，避免文档猜测L、dnum、B/m_sk或scale。 */
int main(int argc,char **argv) {
    try {
        if (argc!=5) throw std::invalid_argument("usage: parameters SCHEME OP N library|regression|kernel");
        const std::string scheme=argv[1],op=argv[2],profile=argv[4];
        const auto n=std::stoul(argv[3]);
        Fixture f(scheme,op,n,"",30,profile=="library" ? n/4 : 1,profile!="library");
        const auto data=f.context->first_context_data();
        std::size_t digits=0;
        if (op=="keyswitch" || op=="reline" || op=="hmul") digits=f.relin.key(2).size();
        if (op=="rotate") for (const auto &key:f.galois.data()) if (!key.empty()) {
            if (digits && digits!=key.size()) throw std::runtime_error("inconsistent Galois digit count");
            digits=key.size();
        }
        std::cout<<std::setprecision(17)<<"{\"degree\":"<<n<<",\"scheme\":\""<<scheme
                 <<"\",\"profile\":\""<<profile<<"\",\"operation\":\""<<op
                 <<"\",\"L_chain_index\":"<<data->chain_index()<<",\"Q_rns_count\":"
                 <<data->parms().coeff_modulus().size()<<",\"dnum\":"<<digits
                 <<",\"input_components\":"<<f.input.size()<<",\"input_scale\":"<<f.input.scale()
                 <<",\"right_scale\":"<<f.right.scale()<<",\"output_scale\":"<<f.expected.scale()
                 <<",\"input_correction_factor\":"<<f.input.correction_factor()
                 <<",\"right_correction_factor\":"<<f.right.correction_factor()
                 <<",\"output_correction_factor\":"<<f.expected.correction_factor()
                 <<",\"output_components\":"<<f.expected.size()
                 <<",\"output_Q_rns_count\":"<<f.expected.coeff_modulus_size()
                 <<",\"rotation_steps\":"<<(op=="rotate" ? f.rotation_steps : 0)
                 <<",\"seed\":[\"0x485055534348454d\","<<n<<",1,2,3,4,5,6]";
        if (scheme=="bfv") {
            hpu::seal_adapter::BfvLevelChain chain(*f.context);
            std::cout<<",\"bfv_levels\":[";
            bool first=true;
            for (const auto &level:chain.levels()) {
                if (!first) std::cout<<','; first=false;
                std::cout<<"{\"chain_index\":"<<level.chain_index<<",\"B\":";
                array(level.b_moduli);
                std::cout<<",\"m_sk\":"<<level.m_sk<<",\"Q\":";
                array(level.q_moduli); std::cout<<'}';
            }
            std::cout<<']';
        }
        std::cout<<"}\n";
    } catch (const std::exception &error) { std::cerr<<error.what()<<'\n'; return 1; }
}
