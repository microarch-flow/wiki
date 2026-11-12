# 存储系统

从一个访问请求出发，研究数据放在哪里、怎样读取，以及哪些资源限制并发。系列按问题提供入口。原 RAM 章节仍保留原来的阅读顺序和地址。

- [RAM 基础导读](RAM/wiki/README.md)：从电路到系统建立共同基础。
- [SRAM 阵列、端口与宏接口](RAM/wiki/02-sram-foundations/README.md)：了解单元、端口和 bank 冲突。
- [DRAM 阵列与命令](RAM/wiki/04-dram-foundations/README.md) · [接口族](RAM/wiki/05-dram-protocol-families/README.md)：了解行状态、刷新与协议。
- HBM：[宽接口](RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md) · [堆叠与集成](RAM/wiki/08-packaging-integration/hbm-2.5d-3d-tsv.md) · [成本](RAM/wiki/08-packaging-integration/why-hbm-is-expensive.md) · [与 LPDDR 选型](RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md)。
- [HBF 高带宽闪存](HBF/wiki/README.md)：从 NAND 和 base die 到软件访问路径。
- [DRAM 控制器与请求调度](RAM/wiki/06-memory-controller/README.md)：了解地址映射、调度与刷新。
- 存储层级与数据放置：[SRAM 应用](RAM/wiki/03-sram-applications/README.md) · [系统架构](RAM/wiki/07-system-architecture/README.md) · [cache 与 scratchpad](COMPUTE/wiki/06-memory-discipline/README.md)。

制造与封装机制见 [FAB](FAB/wiki/README.md)。[DMA 双缓冲](DMA/wiki/04-programming-model/tiling-double-buffering.md)说明搬运与计算如何配合。
