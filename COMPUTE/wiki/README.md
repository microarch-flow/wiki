# COMPUTE 域 Wiki:AI 算力单元为何长成这样

> 数据搬到之后**怎么算、为什么算力单元长这样**。从一个逻辑门,自底向上到芯片顶层布局,由一条主线串起:**计算 / 通信比**。

本 wiki 从 Dwarkesh Patel × Reiner Pope(MatX CEO,前 Google TPU 架构师)《Chip design from the bottom up》(2026-05)出发,按架构师深度展开成完整知识库。

---

## 全域主线

> 芯片面积里真正做乘加的逻辑是零头,绝大部分面积花在把数据从一个地方搬到另一个地方(选数、存储、同步、布线)。每一层的设计动作,本质都是在抬高"有用计算 / 数据搬运"这个比值。

这条主线在六个层级反复出现,详见纲领篇 [01-overview/compute-communication-ratio](./01-overview/compute-communication-ratio.md)。其余每篇收尾都回指它。

---

## 章节地图

| 章节 | 主题 | 主线位置 |
|---|---|---|
| [01 · 总览](./01-overview/) | 问题 + 纲领 + 路线 | 定义比值 |
| [02 · datapath 基础](./02-datapath-foundations/) | 门→MAC、压缩树、位宽、数字格式、mux | 降精度(分子)+ 暴露 mux(分母) |
| [03 · systolic array](./03-systolic-array/) | 阵列、dataflow、trickle-feed、sizing | 上提循环,净赚 y 倍 |
| [04 · 时钟与流水](./04-clocking-and-pipeline/) | 全局时钟、流水寄存器、反馈环、频率≠吞吐 | 同步是纯分母,别过切 |
| [05 · FPGA vs ASIC](./05-fpga-vs-asic/) | LUT/mux 的可配置开销 | 固化省掉 10× 配置税 |
| [06 · 存储 discipline](./06-memory-discipline/) | cache vs scratchpad | 把分母变确定 |
| [07 · 芯片顶层组织](./07-chip-organization/) | CPU/GPU 核、脑vs芯片、GPU=平铺TPU | 砍专用化不需要的分母 |
| [08 · 面向 archax 的建模](./08-modeling-for-archax/) | 7 条建模启示升格 | 把比值做成 IR 一等量 |

---

## 阅读路径

- **从头建立直觉**:按 01→08 顺序通读,每章读完回到[纲领篇](./01-overview/compute-communication-ratio.md)对一眼"这章在六层级表里哪一行"。
- **只查某个决策**(weight- vs output-stationary、cache vs scratchpad、FPGA vs ASIC):直接跳对应篇,各篇自带前置链接。
- **为建模而来**:先读[纲领](./01-overview/compute-communication-ratio.md)再读 [08 建模启示](./08-modeling-for-archax/modeling-insights.md)。

---

## 与其他域的接口

COMPUTE 的"分母"(数据搬运、存储、互连、制造)是其他域的主体。COMPUTE 只建接口、不重写邻域:

- **RAM** — cache/scratchpad 确定性语义 → [06-memory-discipline](./06-memory-discipline/cache-vs-scratchpad.md)
- **CIM** — systolic 驻留 vs 存内计算的边界(驻留处是否就是计算处)→ [03 why-systolic](./03-systolic-array/why-systolic-array.md#5-与-cim-的边界)
- **NOC / DMA** — 阵列进出口 / 跨单元带宽衔接片上互连 → [03 trickle-feed](./03-systolic-array/weight-loading-and-trickle-feed.md)、[07 gpu-as-tiled-tpu](./07-chip-organization/gpu-as-tiled-tpu.md)
- **FAB** — 门数→die area→成本/良率 → [02 quadratic-bitwidth](./02-datapath-foundations/quadratic-bitwidth-scaling.md)、[05 fpga-vs-asic](./05-fpga-vs-asic/lut-mux-and-10x-overhead.md)
- **Workload** — 低精度敏感性、dataflow 适配、batch↔吞吐/延迟 → [`Workload/.../cnn-backbone`](../../../workload-wiki/01-foundation-model-components/cnn-backbone.md)、[`attention-and-transformer`](../../../workload-wiki/01-foundation-model-components/attention-and-transformer.md)、[`attention-variants-and-efficiency`](../../../workload-wiki/01-foundation-model-components/attention-variants-and-efficiency.md)(独立仓库 `/mnt/e/workload-wiki`,同盘相对链接)

详见 [01-overview/taxonomy-and-roadmap](./01-overview/taxonomy-and-roadmap.md#3-域边界compute-不重写什么)。
