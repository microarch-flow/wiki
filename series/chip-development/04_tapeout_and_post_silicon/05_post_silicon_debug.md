# Post-silicon Debug

## 前置知识

- 建议先读 [Post-silicon Bring-up](./04_post_silicon_bringup.md)。
- 建议先读 [软件背景人的前端陷阱](../02_frontend_design_and_verification/09_software_engineer_pitfalls.md)。
- 建议理解 [Bring-up](../00_overview/05_glossary.md#bring-up)、[DFT](../00_overview/05_glossary.md#dft)、[Respin](../00_overview/05_glossary.md#respin)。

## 核心概念

硅后调试是定位首硅行为与规格、仿真或预期不一致的根因。它比软件调试难，因为可观测性有限，内部信号不能随便加 log，很多问题只在特定温度、电压、频率、样品、封装或 workload 下出现。

硅后 debug 的核心是可控性和可观测性：能设置什么状态、能读出什么内部信息、能复现什么场景、能否把现象缩小到模块/时钟域/电源域/软件路径/物理角落。

## Debug 手段

- JTAG、scan chain、boundary scan、IJTAG。
- MBIST/LBIST、ATPG pattern、scan diagnosis。
- Trace buffer、performance counter、error register、interrupt log。
- Firmware diagnostics、driver stress test、compiler-generated minimal workload。
- ATE、logic analyzer、oscilloscope、protocol analyzer、power analyzer、thermal camera。
- Failure analysis：X-ray、C-SAM、SEM、FIB、emission microscopy、OBIRCH 等，通常需专业机构。

## Debug Flow

1. 准确记录现象：样品编号、lot、board、温度、电压、频率、软件版本、test seed。
2. 复现问题，区分 deterministic、random、PVT dependent、sample dependent。
3. 最小化 testcase：从完整 workload 缩小到最小寄存器序列、DMA、tile、接口或时钟域。
4. 分层隔离：board/package/power/clock/firmware/driver/RTL/IP/DFT/后端。
5. 对比 pre-silicon：仿真、emulation、C model、RTL assertion、STA、CDC、DFT report。
6. 建立假设并验证：改频率、电压、温度、延迟、软件顺序、clock gating、power state。
7. 决定 workaround、errata、ATE screen、ECO 或 respin。

## 常见问题类型

- Clock/reset sequencing 错误。
- CDC/RDC 在硅上随机失败。
- Timing corner 或 IR drop 导致高频/低压/高温 fail。
- Firmware 配置寄存器顺序错误。
- Memory 初始化、ECC、MBIST repair 或 SRAM macro 行为不一致。
- SerDes/PCIe/DDR/HBM training 和 SI/PI 问题。
- Cache coherency、interrupt ordering、DMA boundary、NoC deadlock。
- Board/package 焊接、电源、clock、thermal 问题。

## 角色与典型时长

角色包括硅后 debug lead、RTL owner、DV owner、firmware/driver、board/package、DFT/test、STA/power、PHY/IP vendor、FAE 和客户支持。简单 firmware 或 board 问题可能一天内解决；低概率 CDC、timing corner、IR drop、analog/PHY 或设计 bug 可能持续数周到数月。

## 决策点

- 是继续 debug，还是先建立 software workaround。
- 是否需要 ATE 筛选，把坏样品与可用样品分开。
- bug 是否客户可见，是否必须进入 errata。
- bug 是否影响量产可靠性，是否必须 respin。
- root cause 是否足够确定，还是只能用高置信 workaround。

## 先进节点与成熟节点差异

先进节点下，低电压、高频、强 variation、IR drop、thermal hotspot、SI noise 更容易把 bug 表现成 PVT 相关或低概率 fail。5nm/3nm 这类项目中，问题可能只在某 workload、某温度、某 voltage droop、某封装样品上出现，debug 需要把 STA、power integrity、package SI/PI 和软件 workload 联合起来看。

成熟节点通常电压裕量更大、封装和时序压力较低，物理边界问题可能更少，但 CDC、reset、firmware、DFT 和接口协议 bug 仍然会出现。成熟节点的优势是 debug 环境和成本相对友好，不是 bug 更少。

## Software Workaround 的边界

软件 workaround 很有价值：调整初始化顺序、禁用功能、降低频率、改变调度、避开某些寄存器组合、增加 retry、修改 compiler tiling，都可能救回样品和客户 demo。

但 workaround 救不了所有问题。电源网不足、timing 物理失败、DRC/LVS 错误、SRAM 宏接错、PHY 模拟问题、封装 SI/PI 问题、不可观测死锁，通常需要硬件修改、ATE screen、降级规格或 respin。

## 常见坑

- 把“C model 正确”当作硅正确的证据，忽略 reset、CDC、timing、power、DFT 和软件配置。
- 只追求跑通 demo，不建立可复现最小 testcase。
- 没有统一 bug database 和样品追踪，debug 结论无法复核。
- 创始人凭直觉拍板 respin 或忽略 bug，没有 severity、客户影响和 workaround 评估。
- Pre-silicon verification 缺少 coverage，硅后才发现大量未定义行为。

## 上下游接口

上游输入是 bring-up fail log、实验数据、波形、ATE log、设计资料和 pre-silicon reports。下游输出是 root cause、workaround、errata、ATE screen、characterization 限制、revision fix list 或 respin 决策。

硅后 debug 反馈会回到前端验证：每个硅后 bug 都应问为什么仿真、formal、CDC、STA、DFT 或 bring-up plan 没抓到，并把缺口变成下一版流程改进。

## 创业公司取舍

创业公司要建立小而硬的 bug triage 机制：severity、reproducibility、customer impact、workaround、owner、deadline、respin impact。不要让所有人围绕最响亮的问题转，也不要为了融资 demo 隐藏会影响量产的问题。

第一颗芯片要优先保证 debug infrastructure，少做无法观测的复杂动态硬件。快速迭代的正确方式是让每次硅后反馈更快定位，而不是假设硅后不会有 bug。

## 成本视角

硅后 debug 的显性成本包括工程人力、实验室时间、ATE diagnosis、样品损耗、外部 failure analysis、IP vendor 支持和客户现场支持。基础 lab debug 可能主要是人力和设备折旧；一次专业 FA 或 ATE 深度诊断可能是数千到数万美元量级；如果问题导致客户 demo 延误、量产推迟或 respin，成本会迅速上升到数十万、数百万甚至更高。

成本决策要看信息增益。花钱做 FA、ATE diagnosis 或购买更好仪器，如果能避免错误 respin，通常是值得的；反过来，root cause 不清就重流片，是最昂贵的猜测。

## 典型场景

NPU 在小模型上运行正常，但大模型 attention 偶发 hang。初看像 compiler bug。最小化后发现只在高温低压、NoC 满载、某个 DMA burst 边界出现。Trace buffer 显示一个 ready/valid handshake 偶发丢事务，CDC report 回看发现该路径有 waiver 但缺少 formal 证据。短期 workaround 是 compiler 避开特定 burst 对齐，长期需要 RTL 修复并 respin。

## 后续阅读

- [Characterization](./06_characterization.md)
- [Silicon Revision](./08_silicon_revision.md)
- [前端验证方法学](../02_frontend_design_and_verification/03_verification_methodology.md)
- [快速迭代真实约束](../07_for_software_background_founders/05_fast_iteration_realities.md)

## 参考公开来源

- [IEEE 1149.1 JTAG overview](https://standards.ieee.org/standard/1149_1-2013.html)
- [Siemens Tessent Products](https://www.siemens.com/en-us/products/ic/tessent/offerings/)
- [Synopsys TestMAX DFT](https://www.synopsys.com/implementation-and-signoff/test-automation/testmax-dft.html)
- [Keysight semiconductor test resources](https://www.keysight.com/)

## 内容可信度说明

- **公开信息（高可信）**：JTAG、scan、DFT、ATE、oscilloscope、logic analyzer、failure analysis 的基本用途。
- **行业惯例（中可信）**：复现、最小化、分层隔离、errata/workaround/respin triage 是硅后 debug 常见流程。
- **经验性观察（中低可信）**：软件背景团队常低估硅后可观测性和 bug triage 纪律。
- **不确定/需向资深工程师确认（低可信）**：具体 failure analysis 手段、debug register 设计、ATE diagnosis 能力和客户 errata 接受标准。
