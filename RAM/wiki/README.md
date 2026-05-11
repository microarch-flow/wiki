# RAM Wiki

本目录用于把 `RAM/raw/` 下的对话会话，整理成一套面向 `DRAM / SRAM / DDR family / HBM / memory-system architecture` 的可持续扩展知识库。

> `RAM 不是单一器件名词，而是一整套“存储单元、电路阵列、接口协议、控制器调度、封装互连、系统层级”的联合设计问题。`

## Dashboard

| 你现在要做什么 | 直接入口 |
| --- | --- |
| 5 分钟建立 RAM 全局图 | [RAM 在解决什么问题](./01-overview/problem-statement.md) |
| 第一次系统学习 RAM | [学习路线图](./01-overview/learning-roadmap.md) |
| 先搞懂 DRAM 为什么便宜且容量大 | [DRAM 单元、Bank 与 Row Buffer](./02-memory-cells-arrays/dram-cell-bank-row-buffer.md) |
| 先搞懂 SRAM 为什么快 | [SRAM 6T 单元与 Cache 阵列](./02-memory-cells-arrays/sram-6t-cell-cache-array.md) |
| 快速分清 SRAM 和 DRAM | [SRAM vs DRAM 对照](./02-memory-cells-arrays/sram-vs-dram.md) |
| 理解 DDR 带宽公式和 MT/s | [DDR、数据率与带宽](./03-ddr-protocol-families/ddr-double-data-rate-bandwidth.md) |
| 理解 ACT / READ / PRE 与 tRCD / CL / tRP | [DRAM 命令与时序](./03-ddr-protocol-families/dram-commands-timing.md) |
| 补齐 prefetch / burst / bank group 的直觉 | [Prefetch、Burst 与 Bank Group](./03-ddr-protocol-families/prefetch-burst-bank-group.md) |
| 理解频率为什么不能一直涨 | [为什么不能只靠提频](./03-ddr-protocol-families/why-frequency-cannot-scale-forever.md) |
| 一次看懂 DDR / LPDDR / GDDR / HBM | [DRAM 家族对照](./03-ddr-protocol-families/ddr-lpddr-gddr-hbm-comparison.md) |
| 看代际升级到底升级了什么 | [DDR5 / LPDDR5 / GDDR6 / HBM3 代际对照](./03-ddr-protocol-families/generation-comparison-ddr5-lpddr5-gddr6-hbm3.md) |
| 从系统角度理解 channel / rank / bank | [地址映射与层级结构](./04-system-architecture/channel-rank-bank-address-mapping.md) |
| 从架构角度理解实际带宽和延迟 | [控制器、并行度与页策略](./04-system-architecture/controller-parallelism-page-policy.md) |
| 深入看 row hit / miss / conflict 如何影响性能 | [Row Locality 与 Page Policy 深化](./04-system-architecture/row-locality-page-policy-deep-dive.md) |
| 快速分清带宽和延迟不是一回事 | [带宽 vs 延迟](./04-system-architecture/bandwidth-vs-latency.md) |
| 理解 Cache / DRAM / HBM 在系统里的分工 | [从 SRAM 到 HBM 的系统分层](./04-system-architecture/cache-dram-hbm-system-view.md) |
| 理解 CPU / 手机 / GPU / AI 为什么选不同内存 | [不同系统为什么选不同内存](./04-system-architecture/why-systems-choose-different-memory.md) |
| 开始做控制器研究和性能建模 | [内存控制器建模与性能分析](./04-system-architecture/memory-controller-modeling-analysis.md) |
| 先分清 DIMM / PoP / MCP / HBM 封装形态 | [常见内存封装形态](./05-packaging-manufacturing/dimm-pop-mcp-hbm-package-forms.md) |
| 理解 HBM 为什么一定和先进封装绑定 | [HBM、2.5D 与 3D 集成](./05-packaging-manufacturing/hbm-2p5d-3d-integration.md) |
| 理解 DRAM/HBM 为什么贵 | [DRAM 制造流程与 HBM 成本](./05-packaging-manufacturing/why-hbm-is-expensive.md) |
| 快速查核心判断原则 | [第一性原理速查](./06-reference/first-principles.md) |
| 快速查最容易混的概念 | [高频问题](./06-reference/high-frequency-questions.md) |

## 快速开始

### 路线 1：第一次系统认识 RAM

1. [RAM 在解决什么问题](./01-overview/problem-statement.md)
2. [RAM 分类框架](./01-overview/taxonomy.md)
3. [SRAM vs DRAM 对照](./02-memory-cells-arrays/sram-vs-dram.md)
4. [学习路线图](./01-overview/learning-roadmap.md)

### 路线 2：先把 DRAM / DDR 主线学透

1. [DRAM 单元、Bank 与 Row Buffer](./02-memory-cells-arrays/dram-cell-bank-row-buffer.md)
2. [DDR、数据率与带宽](./03-ddr-protocol-families/ddr-double-data-rate-bandwidth.md)
3. [DRAM 命令与时序](./03-ddr-protocol-families/dram-commands-timing.md)
4. [Prefetch、Burst 与 Bank Group](./03-ddr-protocol-families/prefetch-burst-bank-group.md)
5. [为什么不能只靠提频](./03-ddr-protocol-families/why-frequency-cannot-scale-forever.md)
6. [DRAM 家族对照：DDR / LPDDR / GDDR / HBM](./03-ddr-protocol-families/ddr-lpddr-gddr-hbm-comparison.md)
7. [DDR5 / LPDDR5 / GDDR6 / HBM3 代际对照](./03-ddr-protocol-families/generation-comparison-ddr5-lpddr5-gddr6-hbm3.md)
8. [HBM、2.5D 与 3D 集成](./05-packaging-manufacturing/hbm-2p5d-3d-integration.md)

### 路线 3：从芯片架构视角学习

1. [SRAM 6T 单元与 Cache 阵列](./02-memory-cells-arrays/sram-6t-cell-cache-array.md)
2. [DRAM 单元、Bank 与 Row Buffer](./02-memory-cells-arrays/dram-cell-bank-row-buffer.md)
3. [地址映射与层级结构](./04-system-architecture/channel-rank-bank-address-mapping.md)
4. [控制器、并行度与页策略](./04-system-architecture/controller-parallelism-page-policy.md)
5. [Row Locality 与 Page Policy 深化](./04-system-architecture/row-locality-page-policy-deep-dive.md)
6. [带宽 vs 延迟](./04-system-architecture/bandwidth-vs-latency.md)
7. [从 SRAM 到 HBM 的系统分层](./04-system-architecture/cache-dram-hbm-system-view.md)
8. [不同系统为什么选不同内存](./04-system-architecture/why-systems-choose-different-memory.md)
9. [内存控制器建模与性能分析](./04-system-architecture/memory-controller-modeling-analysis.md)

## 工作台

### 学习

- [概览与问题定义](./01-overview/README.md)
- [存储单元与阵列结构](./02-memory-cells-arrays/README.md)
- [DDR 协议与家族](./03-ddr-protocol-families/README.md)
- [系统架构视角](./04-system-architecture/README.md)
- [封装、制造与成本](./05-packaging-manufacturing/README.md)

### 查阅

- [第一性原理速查](./06-reference/first-principles.md)
- [术语表](./06-reference/glossary.md)
- [高频问题](./06-reference/high-frequency-questions.md)
- [知识地图](./SUMMARY.md)

## 这套 Wiki 的边界

这套 wiki 的主线不是 NAND / SSD，也不是完整 CPU cache coherence，而是：

- 面向 `SRAM + DRAM` 的 RAM 基础原理
- 面向 `DDR / LPDDR / GDDR / HBM` 的接口和产品路线
- 面向 `controller / bank parallelism / row locality / packaging` 的系统级判断
- 面向 `AI / GPU / CPU / mobile` 场景的内存选型逻辑

## 维护原则

- 每页尽量只回答一个核心问题
- 优先区分 `cell / array / interface / controller / package / system`
- 优先保留可比较、可推导、可用于架构判断的内容
- 把“带宽、延迟、容量、功耗、成本、封装复杂度”的权衡作为统一主线
- 原始素材来自 `RAM/raw/chat_0.md` 到 `RAM/raw/chat_2.md`
