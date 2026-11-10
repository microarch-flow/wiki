# COMPUTE 域 Wiki:AI 算力单元为何长成这样

> 数据搬到之后**怎么算、为什么算力单元长这样**。从一个逻辑门,自底向上到芯片顶层布局,分别考察计算、数据搬运和实现约束。

本 wiki 从 Dwarkesh Patel × Reiner Pope(MatX CEO,前 Google TPU 架构师)《Chip design from the bottom up》(2026-05)出发,按架构师深度展开成完整知识库。

---

## 全域主线

> 计算、数据放置与搬运共同决定性能和成本。比较时需要先固定工作量、边界和单位，再分别评估 MAC/byte、带宽、面积、吞吐和能耗。

[纲领篇](./01-overview/compute-communication-ratio.md)定义指定边界的算术强度。数据复用可改变该比值；时钟、面积和制造则需要各自的指标。

---

## 章节地图

| 章节 | 主题 | 主线位置 |
|---|---|---|
| [01 · 总览](./01-overview/) | 问题 + 纲领 + 路线 | 定义比值 |
| [02 · datapath 基础](./02-datapath-foundations/) | 门→MAC、压缩树、位宽、数字格式、mux | 位宽、选择网络与实现成本 |
| [03 · systolic array](./03-systolic-array/) | 阵列、dataflow、trickle-feed、sizing | 利用权重或数据复用，收益取决于映射 |
| [04 · 时钟与流水](./04-clocking-and-pipeline/) | 全局时钟、流水寄存器、反馈环、频率≠吞吐 | 各时钟域的路径、II 与代价 |
| [05 · FPGA vs ASIC](./05-fpga-vs-asic/) | LUT/mux 的可配置开销 | 固定逻辑与可配置实现的权衡 |
| [06 · 存储 discipline](./06-memory-discipline/) | cache vs scratchpad | 数据放置与服务时间 |
| [07 · 芯片顶层组织](./07-chip-organization/) | CPU/GPU 核、脑vs芯片、GPU 与 TPU 局部矩阵结构 | 通用性与局部资源的权衡 |
| [08 · 面向 archax 的建模](./08-modeling-for-archax/) | 7 条建模启示升格 | 提出带边界的模型与指标 |

---

## 阅读路径

- **从头建立直觉**:按 01→08 顺序通读,每章读完回到[纲领篇](./01-overview/compute-communication-ratio.md)对一眼"这章涉及哪个资源和边界"。
- **只查某个决策**(weight- vs output-stationary、cache vs scratchpad、FPGA vs ASIC):直接跳对应篇,各篇自带前置链接。
- **为建模而来**:先读[纲领](./01-overview/compute-communication-ratio.md)再读 [08 建模启示](./08-modeling-for-archax/modeling-insights.md)。

---

## 与其他域的接口

数据搬运、存储、互连和制造是其他域的主体。COMPUTE 与它们交换边界流量、带宽、时序和实现参数:

- **RAM** — cache/scratchpad 数据放置与资源争用 → [06-memory-discipline](./06-memory-discipline/cache-vs-scratchpad.md)
- **CIM** — systolic 驻留 vs 存内计算的边界(驻留处是否就是计算处)→ [03 why-systolic](./03-systolic-array/why-systolic-array.md#5-与-cim-的边界)
- **NOC / DMA** — 阵列进出口 / 跨单元带宽衔接片上互连 → [03 trickle-feed](./03-systolic-array/weight-loading-and-trickle-feed.md)、[07 gpu-as-tiled-tpu](./07-chip-organization/gpu-as-tiled-tpu.md)
- **FAB** — 门数→die area→成本/良率 → [02 quadratic-bitwidth](./02-datapath-foundations/quadratic-bitwidth-scaling.md)、[05 fpga-vs-asic](./05-fpga-vs-asic/lut-mux-and-10x-overhead.md)
- **Workload** — 低精度敏感性、dataflow 适配、batch↔吞吐/延迟 → [cnn-backbone（仓内相关页）](../../CIM/wiki/07-workloads/cnn-on-cim.md)、[attention-and-transformer（仓内相关页）](../../CIM/wiki/07-workloads/transformer-on-cim.md)、[attention-variants-and-efficiency（仓内相关页）](../../NOC/wiki/06-ai-noc-specifics/workload-attention-decode-kv-cache.md)；原素材另引用独立 Workload 仓库的同名页面，这里链接仓内相关主题，内容范围并不完全相同

详见 [01-overview/taxonomy-and-roadmap](./01-overview/taxonomy-and-roadmap.md#3-域边界compute-不重写什么)。

## 自测

阅读后可用[自测问题](../self-test-questions.md)检查概念、迁移和架构判断。题目不附答案，每题链接到参考正文。
