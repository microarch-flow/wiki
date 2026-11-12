# 存储系统

从一个访问请求出发，研究数据放在哪里、怎样读取，以及哪些资源限制并发。以下六个专题按问题提供入口。原 RAM 章节仍保留原来的阅读顺序和地址。

- **存储层级与数据路径**：[存储系统概览](RAM/wiki/01-overview/README.md) · [系统架构](RAM/wiki/07-system-architecture/README.md) · [cache 与 scratchpad](COMPUTE/wiki/06-memory-discipline/README.md)。
- **SRAM 器件与应用**：[SRAM 基础](RAM/wiki/02-sram-foundations/README.md) · [SRAM 应用](RAM/wiki/03-sram-applications/README.md)。
- **DRAM 器件与接口**：[DRAM 基础](RAM/wiki/04-dram-foundations/README.md) · [DRAM 协议层](RAM/wiki/05-dram-protocol-families/README.md) · [HBM 阅读入口](RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md)。
- **DRAM 控制器与请求调度**：[Memory Controller](RAM/wiki/06-memory-controller/README.md)，了解地址映射、调度与刷新。
- **HBF 高带宽闪存**：[HBF Wiki](HBF/wiki/README.md)，从 NAND 和 base die 到软件访问路径。
- **存储系统集成与选型**：[封装与集成](RAM/wiki/08-packaging-integration/README.md) · [HBM 堆叠与集成](RAM/wiki/08-packaging-integration/hbm-2.5d-3d-tsv.md) · [HBM 成本](RAM/wiki/08-packaging-integration/why-hbm-is-expensive.md) · [HBM 与 LPDDR 选型](RAM/wiki/09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md)。

按原章节顺序阅读可从 [RAM 阅读路线](RAM/wiki/README.md)开始。需要查阅或练习时，可查看[参考资料](RAM/wiki/10-reference/README.md)和[自测问题](RAM/self-test-questions.md)。

制造与封装机制见 [FAB](FAB/wiki/README.md)。[DMA 双缓冲](DMA/wiki/04-programming-model/tiling-double-buffering.md)说明搬运与计算如何配合。
