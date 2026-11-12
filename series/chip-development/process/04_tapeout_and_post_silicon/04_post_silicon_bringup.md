# Post-silicon Bring-up

## 前置知识

- 建议先读 [Packaging](./03_packaging.md)。
- 建议先读 [DFT 引入](../02_frontend_design_and_verification/05_dft_introduction.md)。
- 建议理解 [Bring-up](../00_overview/05_glossary.md#bring-up)、[ATE](../00_overview/05_glossary.md#ate)、[JTAG](../02_frontend_design_and_verification/05_dft_introduction.md)、[Package](../00_overview/05_glossary.md#package)。

## 核心概念

Bring-up 是第一批硅片或封装样品到手后，让芯片从“物理存在”进入“可控、可观测、可运行”的过程。它的目标不是马上跑完整 benchmark，而是系统性缩小未知空间：电源是否正常、时钟是否锁定、复位是否释放、JTAG/scan 是否可用、boot 是否开始、内存和基本接口是否工作、最小 workload 是否能跑。

Bring-up 成败高度依赖 tapeout 前的 debug 设计。没有 JTAG、scan、MBIST、status register、trace buffer、strap、safe clock、power measurement、error log，硅后团队就只能用外部仪器猜内部状态。

## Bring-up 前准备

准备工作应在 tapeout 前完成：

- Bring-up plan：按电源、时钟、复位、DFT、boot、memory、interface、NPU workload 分阶段。
- EVB/bring-up board：电源 rail、clock source、JTAG、UART/PCIe/USB/Ethernet、测量点、thermal solution。
- Firmware/driver：boot ROM、loader、register access、diagnostic tests、error dump。
- Test pattern：scan、MBIST、ATPG、JTAG boundary scan、ATE smoke tests。
- Lab equipment：bench supply、oscilloscope、logic analyzer、JTAG debugger、thermal chamber、power analyzer、protocol analyzer。
- Reference：仿真波形、FPGA/emulation 结果、C model、expected register map。

## 典型顺序

1. 样品和板卡视觉检查，确认封装、焊接、方向、版本。
2. Board power-off 检查：短路、阻抗、rail isolation、strap。
3. 限流上电，逐 rail 检查电压、电流、时序。
4. 检查 external clock、PLL lock、reset sequencing。
5. 连接 JTAG/scan，读取 IDCODE 或基本 debug register。
6. 运行 MBIST/scan smoke，确认 DFT 通路和 memory 基本状态。
7. 执行 boot ROM 或最小 firmware，验证 register access。
8. 初始化 SRAM/DDR/HBM/PCIe/SerDes 等接口。
9. 跑最小 workload，例如单 tile matmul、DMA copy、interrupt test。
10. 记录 pass/fail、波形、寄存器 dump、电流和温度。

## 角色与典型时长

角色包括硅后验证、board engineer、firmware/driver、DFT/test、design owner、verification owner、clock/power/PHY/IP owner、package/thermal、ATE engineer。Bring-up 可以几天内达到基本 JTAG/boot，也可能因为电源、时钟、接口、DFT 或 RTL bug 卡数周到数月。复杂 AI SoC 和先进封装项目应预期多团队 war room。

## 关键决策点

- 是否先上 ATE 还是实验室板卡：ATE 可快速筛样品，板卡更利于系统 debug。
- 上电顺序和限流策略：错误上电可能损坏样品。
- 先 bring-up 哪个路径：JTAG/scan/MBIST/boot/PCIe/NPU 应按依赖关系推进。
- 遇到异常是否继续尝试：要避免把可疑芯片或板卡反复操作到不可诊断。
- 是否进入 characterization：只有基本功能和可控性稳定后，才适合做系统性测量。

## 先进节点与成熟节点差异

7nm 及以下芯片通常电压裕量更小、功耗密度更高、IR drop 和 thermal 更敏感，bring-up 时需要更谨慎的 rail ramp、current limit、温度监控和低频/低并发 safe mode。先进封装、HBM、SerDes、chiplet 会增加 board/package/SI/PI 问题，导致“芯片不工作”的现象更难归因。

28nm/16nm 或小型 MPW test chip 通常接口少、功耗低、封装简单，bring-up 路径更短。但如果测试和 debug 结构缺失，即使成熟节点也会卡住。成熟节点降低物理风险，不替代 bring-up 计划。

## 常见坑

- 封装样品回来后才开始写 firmware 和 board scripts。
- 只准备 demo workload，没有准备分层 diagnostic tests。
- 没有电流、电压、温度、clock/reset 波形记录，问题不可复现。
- 把所有 fail 都归因于 silicon bug，忽略 board/package/test setup。
- 没有样品追踪，混淆 wafer lot、die location、package lot、board version。
- 忽略 ESD 和热保护，bring-up 中损坏样品。

## 上下游接口

上游来自封装样品、EVB、DFT/test pattern、firmware、register model、bring-up plan。下游输出包括 known-good checklist、fail log、errata 初稿、debug priority、可进入 characterization 的样品列表和需要 ATE/FA 的问题。

Bring-up 会反推设计和流程：如果 JTAG 不通，要查 board/package/DFT/TAP；如果 PLL 不锁，要查电源、reference clock、analog IP；如果 boot hang，要查 ROM、reset、memory map、firmware 和 RTL。

## 创业公司取舍

创业公司可以自动化 bring-up 脚本和数据采集，但不能省 bring-up 基础设施。第一颗芯片应把 debug 可观测性放在性能之后，否则首硅失败时无法定位。Bring-up lab、板卡、仪器、firmware、DFT pattern 和负责人要在 tapeout 前准备，而不是样片到货后临时补。

## 成本视角

Bring-up 成本包括 EVB/PCB、socket、探针和夹具、实验室仪器、样品消耗、firmware/driver 人力、外部实验室或 FA 支持。简单 bring-up 板卡和基本仪器可能是数千到数万美元量级；高功耗 AI 芯片的定制板卡、socket、power delivery、thermal setup、协议分析仪和高速示波器可能进入数十万美元量级，若租用或外包实验室则按时间和设备计费。

可以省的是自动化脚本和通用设备复用；不能省的是电源测量、JTAG/DFT access、样品追踪、board revision 管理和负责 bring-up 的 owner。

## 典型场景

首批样品上电后 PCIe 不枚举。团队如果直接怀疑 SerDes IP，可能浪费数周。分层 bring-up 发现 JTAG 可读，PLL lock 正常，PCIe refclk 抖动超出 spec，board 上某个 clock buffer 配置错误。修复 board 配置后 PCIe 枚举成功。这个例子说明 bring-up 必须先区分 board/package/silicon/software。

## 后续阅读

- [Post-silicon Debug](./05_post_silicon_debug.md)
- [Characterization](./06_characterization.md)
- [Yield Analysis](./07_yield_analysis.md)
- [Field Support](../05_production_and_lifecycle/04_field_support.md)

## 参考公开来源

- [IEEE 1149.1 JTAG overview](https://standards.ieee.org/standard/1149_1-2013.html)
- [Keysight oscilloscope and protocol analysis resources](https://www.keysight.com/)
- [Tektronix oscilloscope resources](https://www.tek.com/)
- [JEDEC JESD47 overview via TI reliability testing reference](https://www.ti.com/quality-reliability/reliability/testing.html)

## 内容可信度说明

- **公开信息（高可信）**：JTAG、scan、MBIST、bench equipment、bring-up basic sequence 的基本概念。
- **行业惯例（中可信）**：上电、clock/reset、JTAG、boot、memory、interface、minimal workload 的分层 bring-up 顺序。
- **经验性观察（中低可信）**：创业团队常低估 firmware、board、instrumentation 和 debug hooks 对 bring-up 的决定性影响。
- **不确定/需向资深工程师确认（低可信）**：具体 bring-up 周期、设备配置、上电限流、clock/power sequence 和安全操作规程。
