# HBF 高带宽闪存：专题导读

<span id="hbf-wiki从-nand-到近计算存储系统"></span>

## HBF Wiki：从 NAND 到近计算存储系统 {#专题范围}

本专题讨论器件、接口和系统软件如何协作。High Bandwidth Flash（HBF，高带宽闪存）尝试把 NAND 的容量与封装内的高带宽接口结合，用于靠近处理器的数据层。一个 stack 的带宽指标，并不能单独说明一次读取的延迟或应用速度。

本专题以一次 4 KiB 权重读取为贯穿案例，从器件读到系统。器件机制使用公开资料解释；HBF 接口主要以 [OCP High-Level Base Die Specification v0.7.0，2026-08-03](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)为边界。厂商目标、教学假设和实测数据分别标注。前置 NAND 知识根据公开资料补充，不假定所有产品都有相同的内部实现。

## 阅读顺序

1. [HBF 的系统定位](./01-position.md)
2. [NAND 阵列基础](./02-nand-foundations.md)
3. [HBF 结构与接口](./03-architecture.md)
4. [一次 4 KiB 读取](./04-read-walkthrough.md)
5. [地址映射与并行度](./05-mapping-and-performance.md)
6. [写入与可靠性](./06-write-and-reliability.md)
7. [推理工作负载与建模](./07-workload-and-modeling.md)
8. [规范与研发进度](./08-spec-and-industry.md)
9. [术语、资料与自测](./09-reference.md)

首次学习建议按顺序阅读。已经熟悉 NAND 时，可以从第 3 篇开始。只想查容量、带宽、功耗和产品进展，可以先看第 8 篇；需要安排数据放置和预取时，可在第 5、6 篇之后阅读第 7 篇。

## 一个贯穿案例

假设模型权重已经装入 HBF。host 将全局地址按 4 KiB 条带依次分给 16 个 channel；xPU 请求全局地址 `[0x5000, 0x6000)`。按这个教学映射，它落在 channel 5 的局部第 0 页。再假设 base die 的相关缓存未命中，且没有读取错误。第 4 篇追踪请求；第 5 篇计算映射，并引入其他请求和资源冲突。

这个案例是教学模型。它不声称某一产品采用示例中的物理地址映射，也不代表实际延迟、吞吐或数值测量。OCP v0.7 的 host 侧读取以 64 B 为粒度；4 KiB 可以由多个事务组成，是否支持 burst 取决于产品。

## 与其他专题的关系

- [RAM：存储层级作为系统](../01-memory-hierarchy/01-system-basics/memory-hierarchy-as-system.md)：理解容量、带宽和访问距离的系统权衡。
- [NPU 数据路径与存储组织](../01-memory-hierarchy/04-npu-case/README.md)：理解计算映射与数据搬运的关系。
- [HBM 堆叠、宽接口与伪通道](../03-dram/protocols/hbm-stacked-wide-io.md)：比较 DRAM 的访问组织。
- [RAM：HBM 封装与 TSV](../06-system-integration/packaging/hbm-2.5d-3d-tsv.md)：区分存储介质与堆叠封装。
- [NoC：互连与存储系统](../../interconnect/NOC/wiki/05-system-integration/noc-meets-memory-system.md)：理解路径共享、流控和资源竞争。
- [FAB：封装信号完整性](../../chip-development/FAB/wiki/06-cross-cutting-engineering/signal-integrity-in-package.md)：理解近距互连仍需面对的物理约束。

外部资料的版本、适用范围和待验证问题集中列在[术语、资料与自测](./09-reference.md)。
