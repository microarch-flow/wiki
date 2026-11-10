# 九专题基线问题与正文证据

基线为 Git 提交 `567efe5`。可用 `git show 567efe5:<路径>` 查看对应原文；当前正文包含修正和具体条件。本表记录问题、可复算的判例和证据类型，不表示模拟器已运行，也不代替独立验收。

| 专题 | 基线问题 | 当前判例、前提与证据 |
| --- | --- | --- |
| BUS | `axi-narrow-transfer-wstrb.md` 把 `0x1003` 的 4-byte 非对齐首拍写成 lane 3–6。 | AXI4、64-bit 总线、4-byte INCR 传输：首拍只允许 lane 3，下一拍从 `0x1004` 开始。见 [Narrow Transfer 与 WSTRB](../BUS/wiki/03-on-chip-protocol-families/axi-narrow-transfer-wstrb.md)。证据：协议规则和手算示例。 |
| DMA | 基线给出稳态 `max(T_dma,T_comp)`，但缺少有限批次逐拍案例，难以比较首块和总时间。 | 假设独立搬运与计算、双缓冲无冲突，`D=2`、`C=5`、3 个 tile：总时间 17 cycle，稳态间隔 5 cycle。见 [Tiling 与 Double Buffer](../DMA/wiki/04-programming-model/tiling-double-buffering.md)。证据：假设条件下的时间线手算。 |
| NOC | 基线三跳三 flit 表称 tail 在第 8 拍全部弹出，又要求完成延迟为 6 拍，计时边界不一致。 | 在当前快照、链路和消费契约下，tail 第 9 拍进入 ejection，第 10 拍被 consumer 取走。见 [验证与校准场景 1](../NOC/wiki/08-simulator-construction/verification-and-calibration.md)。证据：表格是手算预期；独立脚本复算了 11 拍队列和 credit，未运行用户的模拟器，也未进行硬件实测。 |
| RAM | 基线 SRAM 图把内部阶段画成固定 cycle；DDR4 的 PRE 守卫没有覆盖写数据和写恢复约束。 | SRAM 内部相位与接口边沿需按宏定义；DDR4 示例 `AL=0`、`CWL=9`、`BL=8`、`nWR=12` 时，WR 在周期 0 后显式 PRE 最早为 25，还须满足其他约束。见 [SRAM 访问时序](../RAM/wiki/02-sram-foundations/read-write-cycle-timing.md)和 [DRAM 时序参数](../RAM/wiki/05-dram-protocol-families/timing-parameters-trcd-trp-tras.md)。证据：指定模式的手算，非所有 DDR 变体。 |
| CIM | 基线把 SA、ADC 描述成必经串联链，还给出无具体统计边界的 ADC 面积或能耗比例。 | 8 个独立样本、ADC 每轮各转 1 个：2 个 ADC 要 4 轮，4 个 ADC 要 2 轮，均为 8 次转换。见 [ADC、DAC 与 Sense Amp](../CIM/wiki/04-circuit-and-macro/adc-dac-sa-in-cim.md)。证据：假设条件下的资源计数；不推断面积或能耗比例。 |
| COMPUTE | 基线声称前馈逻辑可任意切分，且只用反馈环决定整片芯片频率。 | 若同域反馈和前馈路径的完整 setup 要求分别为 1.0 ns、1.4 ns，且无更慢路径，频率上限约为 714 MHz；hold 等需另行检查。见 [反馈环与时钟约束](../COMPUTE/wiki/04-clocking-and-pipeline/feedback-loop-clock-constraint.md)。证据：假设路径上的手算。 |
| FAB | 基线把 CP 漏检控制和资格试验置信度当成良率因子相乘，未明确筛选分母。 | 1000 件中 900 件真好均通过、100 件真坏中检出 90 件：910 件通过，其中坏品 10 件，通过品坏品比例 `10/910`；每投入真良品比例 90%。见 [良率与缺陷密度](../FAB/wiki/03-wafer-test-and-cp/yield-and-defect-density.md)。证据：条件概率和手算；资格置信度不是逐件良率。 |
| CPO | 基线把 TIA 模糊地描述为恢复信号，缺少接收判决边界和可核对的光预算。 | CWDM4 表 2-5 在指定条件下预算 `8−5−3=0 dB`；额外未计入损耗 1 dB 后为 −1 dB。见 [光链路基础](../CPO/wiki/04-optical-engine/optical-link-basics.md)。证据：标准示例和手算；不能由余量单独推出 BER，也不能直接套用到其他 CPO 接口。 |
| PCIe | 基线把 RCB 描述为 completion 的拆分粒度，并给出没有目标和实现条件的 10-bit Tag 数。 | 对齐 256 B read，`MRRS≥256 B`、`MPS=256 B`、`RCB=64 B`：可以一个 256 B CplD，也可以四个 64 B CplD。见 [建模参数与公式速查](../PCIE/wiki/08-reference/pcie-modeling-params.md)。证据：协议规则与厂商示例；实际拆分依 completer。 |
