# 本轮官方连续主体计时

基点为`631f9970`，inline-asm固定到`feature/compute-profiling@4e26659cc0c9c3887c60491e8455ff5fd6028025`。原资源管理与NTT ABI v4已在上游main；本轮按要求选择专用profiling分支，不修改SDK、AM或RTL。

00～06独立用例C和旁侧ASM均未改，07仍为N1024/N8192、输入level4、三方案各六项，共36项；默认总数109，另6项API诊断。编号与分离式源码结构不变。07的72份optimized/noopt ASM更新来自官方实际编译结果：安全预加载使顺序/对象分配改变，并新增首尾窗口边界PSYNC，不是删除覆盖或手写改编码。

生成器仅开启官方`CompileOptions.profile_execution=true`；接收器逐字验证原生profiled C/H、DMA、窗口及两次clock hook，目标端直接编译官方源码。main调用具名`hpu_run_*_profiled`，每次PSYNC匹配递增序号、真实PLIC事件与fresh rearm；不重做CTE初始化，不重置SRAM。尾部也完成后sample才valid，最终golden/只读区/guard仍全部检查。

口径为`execution_window_irq_v1`、`completion=plic_irq`、`profile=continuous`。排除entry准备IO和原有尾IO，保留主体全部算术、必要DMA和ISR/回调开销，不宣称纯计算。旧端到端/轮询样本拒绝混算。4个BFV noopt KeySwitch/Reline原本就有1次首算术前workspace DSTORE，逐项核对allocation、跨度和DMA属性与普通包相同，非新增输出写；单列prefix_dstore_count，未擅改官方窗口。所有本批suffix_dload_count为0，但仍按实际统计，不写死。

验证记录：72个profile包全部通过官方validator、严格指令模型、原生输入/golden及窗口/C/H验收，全部算术落在单一窗口，DMA次数/字节均未增加；72份旁侧ASM逐字节匹配。Ubuntu24.04/GCC13全套契约检查通过，新增统计回归另行通过。109项默认及6项API实际重编译，36项07在GCC13/GCC14的新ELF均通过字码、嵌入数据、官方回调/时间戳和自检路径门禁；N8192 BFV noopt/silent另验前序workspace写、计时及无UART输出。未运行RTL/FPGA，未填入任何未测cycle或加速比。

# 上轮布局与PSYNC中断修复

基点为`fd0db077`，inline-asm从`3ab94da`升级至`cfee951e4056660e521d55a3535d82335a49bb08`。指令编码/旁侧ASM不变，按NTT ABI v4及bit-reversed系数域重新生成镜像、在线因子和golden；不能复用旧布局数据。

此前native共享接收端一直保留末尾PSYNC，但`wait_program`/`performance_wait`只观察MMIO完成电平，未验证CPU中断。此次03～07默认改回真实PLIC source257/context1完成事件。COMMIT配置轮询和00～02明确指定的MMIO用例保留，不把这些测试的判据一并改掉。

修复了三个相连问题：

- CTE机器态初始化仅执行一次；后续open/rearm只配置IRQ，不在S态再次写机器CSR，也不清空既有handler注册表。
- `mscratch`无条件指向16字节对齐的真实保存区，安装早于mtvec/开中断；timer只配置自身调度字段。禁用timer不再跳过异常入口准备，未把保存区指针设零。
- AM递归构建显式接收HPU模式，模式切换使AM缓存失效。HPU模式开放S态cycle访问、初始化PLIC，且不设置CPU定向测试在0x90000000的禁止PMP窗口；默认CPU模式保留原PMP/timer策略。

机器异常入口仅接受固定PC、固定指令、S态来源的受控IRQ重武装请求；其它非法指令或机器异常保留mepc/mcause/mtval并失败，不再无条件跳过4字节。

03_08专门回归空闲/DMA/计算三个官方fixed入口，每个两轮，涵盖rearm及跨close/open，总计6个事件、CTE初始化1次。各片段末尾一次PSYNC；选中输出精确比较golden，未选输出检查仍为初始毒值，全部只读区和guard仍查。是否恰好处于硬件忙周期应由实际波形确认，host模型不作此声明。

07计时口径改为`issue_to_irq_done_v1`、`completion=plic_irq`：IRQ配置在起点之前，DLOAD/计算/DSTORE/PSYNC及ISR处理在区间内，close/自检/UART在终点之后。MMIO电平本身不能冒充一次ISR，解析器拒收旧`issue_to_done_v2`。

验证记录：原166项契约测试、新10项prefix接收测试及新增共享wait委托测试通过；IRQ生命周期/故障注入、三种前序各两轮的真实main主机回归通过。109项默认用例完成新布局模型、实际ELF/BIN、字码与嵌入数据检查，36项07通过实际成功路径cycle/IRQ门禁；03_08实际ELF含三个独立入口，mscratch指针/安装顺序、HPU模式的counter/PLIC/PMP策略已核对。未修改RTL、未屏蔽twiddle断言，以上不表示RTL/FPGA已通过。

另6项API诊断重编译/模型检查通过；03_08静默版及07_33的N8192/BGV/L4静默noopt版完成实际目标构建、无UART和相应字码/计时检查。普通CPU amtest也实际重编译成功，ELF保留原PMP定向配置及timer分支；随后切回HPU模式的API构建成功，验证模式缓存切换不会混用。

# 上轮精简与验证范围（fd0db077基线）

基点为`7b10ddea`。按用户要求保留00～02与06，03～05只保留N1024/level4，07只保留N1024/N8192且全部level4。BGV性能原来为level3，本轮按确认真实改为level4，而不是只改标签。

默认用例从711降为109；另6项API诊断保持，总清单115项。保留分离式C、旁侧ASM和文件/行号错误定位。四个受影响组从01按两位连续编号，历史编号对照不参与构建。

不符合范围的602条旧用例已逐文件删除C及对应ASM/noopt ASM，不在仓库另留archive；其中包含原03 N4096九项定向、05特殊回归及其它规模。保留03～05的30份ASM不改字节，C仅改编号/路径；CKKS/BFV性能也保持原L4程序。BGV的12项性能重新生成真实Q4/P1输入、程序和golden，因此不继承旧L3通过记录或周期数。

仅更新必要的构建选择、参数门禁、源码清单与文档。SDK通用参数能力不当作额外IT用例，00～02及06的测试源码保持原样。删除原定向意味着相关旧判据不能凭剩余用例数量自动视为等价覆盖；本轮也不恢复原已取消的CPU benchmark、独立subtest或条件实验入口。

本轮109项默认及6项可选API均完成实际ELF/BIN重编译与相应原生包/ASM、模型、机器字及嵌入数据检查；36项默认07均通过实际ELF计时门禁。12项BGV双variant的真实Q4模型通过，另对07_33_bgv_hmul_reline_l4_n8192执行静默noopt目标构建、无UART及计时检查，均通过。

统一契约回归发现6处解析测试仍引用已删除的旧N4096编号；仅更新测试夹具并增加旧编号拒绝检查，相关8项定向复测通过，其余测试保持通过。源码审计115项零问题，并核对00～02与06源码相对基点无差异。不把这些构建/模型结果写成硬件通过；没有修改RTL或运行RTL/FPGA。删除前源码可从基点Git版本恢复。
