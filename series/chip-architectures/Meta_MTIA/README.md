# Meta MTIA 1 与 2i 怎样为推荐推理组织片上 SRAM

<div class="chip-legacy-anchors" aria-hidden="true"><span id="meta-mtia-v1-v2"></span><span id="为什么做-mtiarr-推理的规模与经济性"></span></div>

推荐模型常组合 embedding 查表和稠密的多层感知机（MLP）。查表按输入索引读取向量。MLP 可在一个批次内重复使用权重。MTIA 2i 用局部存储、共享 SRAM 和 LPDDR5 配合这两种访问。理解取舍的起点是跟踪每份数据的访问模式与存活时间。 [MTIA 1 论文存档](https://github.com/microarch-flow/chip-architecture-wiki/blob/3086204c049a762eb59033f8141fba9e91f4c669/Meta_MTIA/raw/MTIA_v1.pdf) · [MTIA 2i 论文](https://aisystemcodesign.github.io/papers/MTIA-ISCA25.pdf)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="关键参数官方-isca25-table-2"></span><span id="芯片迭代与路线"></span></div>

## 两代芯片的同口径规格

| 指标 | MTIA 1 | MTIA 2i |
| --- | --- | --- |
| PE 阵列 | 8 × 8 | 8 × 8 |
| 每 PE 局部存储 | 128 KB | 384 KB |
| 共享 SRAM | 128 MB，0.8 TB/s | 256 MB，2.7 TB/s |
| 片外 LPDDR5 | 32–64 GB，176 GB/s | 64–128 GB，204.8 GB/s |
| 稠密 INT8 GEMM 峰值 | 102.4 TOPS | 354 TOPS |
| 2:4 稀疏 INT8 GEMM 峰值 | 未列出 | 708 TOPS |
| TDP | 35 W（典型 25 W） | 85 W（典型 65 W） |

规格采用第二代论文表 2。按 INT8 峰值求比，2i 稠密相对第一代稠密约为 3.46 倍。2i 的 2:4 稀疏峰值相对第一代稠密约为 6.91 倍，比较时要保留各自的操作数条件。实际推荐模型还有查表、向量计算和搬运。第一代论文的 TBE（Table Batched Embedding）测试应按当时的设备和批大小阅读。 [MTIA 2i 论文，表 2](https://aisystemcodesign.github.io/papers/MTIA-ISCA25.pdf#page=3) · [MTIA 1 论文，图 12](https://github.com/microarch-flow/chip-architecture-wiki/blob/3086204c049a762eb59033f8141fba9e91f4c669/Meta_MTIA/raw/MTIA_v1.pdf)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="pe-微架构local-memory-fixed-function-粗粒度流水"></span><span id="执行模型risc-v-生成-custom-instructioncp-调度fixed-function-异步-dataflow"></span><span id="noc"></span><span id="mtia-的下注"></span></div>

## PE 内怎样安排矩阵计算和后处理

在 MTIA 2i 中，处理单元（PE）的 RISC-V 核执行控制程序。命令处理器（CP）接收面向专用单元的命令，跟踪数据依赖和局部缓冲。命令的依赖满足后，对应单元可异步执行。

以一块全连接计算为例。输入经过网络接口（FI）搬入 PE 局部存储。点积引擎（DPE）计算，归约引擎（RE）处理部分和，SIMD 引擎可接着做逐元素计算。存储布局单元（MLU）负责受支持的布局转换。片上网络（NoC）连接 PE、共享 SRAM、内存控制器等资源。并行的搬运与处理仍会受到共享端口和网络负载影响。 [MTIA 2i 论文，第 3 节与图 1、图 2](https://aisystemcodesign.github.io/papers/MTIA-ISCA25.pdf#page=3)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="memory-hierarchy大-sram-当核心lpddr-补容量刻意不用-hbm"></span><span id="模型-芯片协同论文真正的价值"></span><span id="从中该获取的经验教训"></span></div>

## 为什么共享 SRAM 分成缓存和暂存区

MTIA 2i 可把 256 MB 共享 SRAM 按 32 MB 粒度划分。最后一级缓存（LLC）由硬件管理，最后一级暂存区（LLS）由软件分配。暂存区可以让活跃的中间结果在生命周期内保留位置。缓存则可利用权重和 embedding 的访问局部性。模型的参数表放不下时，片外 LPDDR5 提供容量。 [MTIA 2i 论文，第 3.6 和 4.1 节](https://aisystemcodesign.github.io/papers/MTIA-ISCA25.pdf#page=6)

假定某个批次的激活缓冲峰值为 40 MB，且可以用一个连续的逻辑暂存区。按 32 MB 划分，至少分配 64 MB 给 LLS。若没有其他保留区，剩余 192 MB 可作 LLC。扩大批大小可能增加矩阵单元的利用率，也可能把激活推过下一个容量边界。论文中的自动调优会比较保留当前批次与缩小批次后的性能。其中一种候选是缩小批次以让激活停留在 LLS。数值是容量教学例。

<div class="chip-legacy-anchors" aria-hidden="true"><span id="为什么不适合-llm-decode"></span><span id="该警惕的点"></span></div>

## 两个 LLM 结果的适用边界

同一篇论文报告了两组 MTIA 2i 结果，第 3.6 节使用 Llama 2 7B，第 8 节使用 Llama 3 8B。

- **Llama 2 7B。** 论文报告预填充满足 600 ms 首 token 要求，解码未满足每个后续 token 60 ms 的目标。这两个值是实验中的目标。
- **Llama 3 8B。** 论文报告预填充表现可接受，解码未达到时延要求。作者指出该实验的多头注意力和前馈网络均受 LPDDR 带宽限制。

应分别保留模型、代际和作者说明。可用片上容量和实际 LPDDR 字节数会随模型、批大小、布局与内核发生变化。 [MTIA 2i 论文，第 3.6 节](https://aisystemcodesign.github.io/papers/MTIA-ISCA25.pdf#page=6) · [同论文，第 8 节](https://aisystemcodesign.github.io/papers/MTIA-ISCA25.pdf#page=11)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="战略定位与商业背景"></span><span id="与四家的对照"></span></div>

## 接下来怎么读

- 看同一种 embedding 访问在另一款芯片上如何由专用单元和芯片间通信处理。 [Google TPU v4](../google-tpu-v4/README.md)
- 查阅原文中的产业背景和代际记录。 [原稿存档](https://github.com/microarch-flow/chip-architecture-wiki/blob/3086204c049a762eb59033f8141fba9e91f4c669/Meta_MTIA/README.md)
