# 知识地图

这页只保留章节级入口。

如果你要：

- 快速开始：看 [首页](./README.md)
- 学 DRAM / SRAM 基础：看 [存储单元与阵列结构](./02-memory-cells-arrays/README.md)
- 学 DDR / HBM：看 [DDR 协议与家族](./03-ddr-protocol-families/README.md)

## 01 概览与问题定义

- [首页](./01-overview/README.md)

## 02 存储单元与阵列结构

- [首页](./02-memory-cells-arrays/README.md)
- [DRAM 单元、Bank 与 Row Buffer](./02-memory-cells-arrays/dram-cell-bank-row-buffer.md)
- [SRAM 6T 单元与 Cache 阵列](./02-memory-cells-arrays/sram-6t-cell-cache-array.md)
- [SRAM vs DRAM 对照](./02-memory-cells-arrays/sram-vs-dram.md)

## 03 DDR 协议与家族

- [首页](./03-ddr-protocol-families/README.md)
- [DDR、数据率与带宽](./03-ddr-protocol-families/ddr-double-data-rate-bandwidth.md)
- [DRAM 命令与时序](./03-ddr-protocol-families/dram-commands-timing.md)
- [Prefetch、Burst 与 Bank Group](./03-ddr-protocol-families/prefetch-burst-bank-group.md)
- [为什么不能只靠提频](./03-ddr-protocol-families/why-frequency-cannot-scale-forever.md)
- [DRAM 家族对照：DDR / LPDDR / GDDR / HBM](./03-ddr-protocol-families/ddr-lpddr-gddr-hbm-comparison.md)
- [DDR5 / LPDDR5 / GDDR6 / HBM3 代际对照](./03-ddr-protocol-families/generation-comparison-ddr5-lpddr5-gddr6-hbm3.md)

## 04 系统架构视角

- [首页](./04-system-architecture/README.md)
- [地址映射与层级结构](./04-system-architecture/channel-rank-bank-address-mapping.md)
- [控制器、并行度与页策略](./04-system-architecture/controller-parallelism-page-policy.md)
- [Row Locality 与 Page Policy 深化](./04-system-architecture/row-locality-page-policy-deep-dive.md)
- [带宽 vs 延迟](./04-system-architecture/bandwidth-vs-latency.md)
- [从 SRAM 到 HBM 的系统分层](./04-system-architecture/cache-dram-hbm-system-view.md)
- [不同系统为什么选不同内存](./04-system-architecture/why-systems-choose-different-memory.md)
- [内存控制器建模与性能分析](./04-system-architecture/memory-controller-modeling-analysis.md)

## 05 封装、制造与成本

- [首页](./05-packaging-manufacturing/README.md)
- [DRAM 制造流程](./05-packaging-manufacturing/dram-manufacturing-flow.md)
- [常见内存封装形态](./05-packaging-manufacturing/dimm-pop-mcp-hbm-package-forms.md)
- [HBM、2.5D 与 3D 集成](./05-packaging-manufacturing/hbm-2p5d-3d-integration.md)
- [为什么 HBM 贵](./05-packaging-manufacturing/why-hbm-is-expensive.md)

## 06 术语与速查

- [首页](./06-reference/README.md)
- [第一性原理速查](./06-reference/first-principles.md)
- [术语表](./06-reference/glossary.md)
- [高频问题](./06-reference/high-frequency-questions.md)
