# Graphcore GC200 的 tile 怎样计算、同步和交换

<div class="chip-legacy-anchors" aria-hidden="true"><span id="graphcore-ipucolossus-mk2-gc200"></span></div>

Graphcore Colossus Mk2（GC200）把处理器与局部存储放在许多独立的 tile 内。若一个算子需要另一 tile 的结果，编译器安排显式的数据交换。批量同步并行模型（BSP）规定了这次交换如何与本地计算衔接。 [GC200 Hot Chips 2021](https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Graphcore.SimonKnowles.v04.pdf)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="芯片架构图"></span><span id="tile特性"></span></div>

## tile 的职责与资源

GC200 有 1472 个 tile。每个 tile 包含多线程处理器和 624 KiB 局部存储。tile 在计算阶段使用本地数据，可运行各自的程序。厂商把处理器上的线程上下文和发射时隙分别列为 7 个和 6 个。监督线程可将时隙交给工作线程执行一个 codelet。单个 tile 内仍有向量和矩阵计算资源。 [厂商演讲，第 5 和 10 至 11 页](https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Graphcore.SimonKnowles.v04.pdf)

厂商演讲规格页列出 896 MiB 片上 SRAM，架构对照页列出 897 MiB。按 1472 × 624 KiB 计算也是 897 MiB。本文保留两页的口径差异，工作集能否放入应按实际可分配的 tile 内存和张量布局确认。 [厂商演讲，第 5 和 8 页](https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Graphcore.SimonKnowles.v04.pdf)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="执行模型"></span></div>

## 两个 tile 如何交换中间结果

假定一个 BSP 步骤由两个 tile 参加。tile A 持有输入 x，计算中间值 f(x)。tile B 持有输入 y，需要结合 y 与 f(x) 才能生成结果。

1. **计算。** A 计算 f(x)，B 可以完成只依赖 y 的局部工作。此时两个 tile 都使用自己的局部存储。
2. **同步。** 假定 A 在时刻 4 完成，B 在时刻 7 完成，并且两者同时开始。当前同步域最早在时刻 7 满足全部参与者到达的条件。
3. **交换。** 按程序安排把 f(x) 传到 B 的局部存储。下一计算阶段，B 才用它生成输出。

时间取值是教学假设，未计屏障和交换本身的时间。该例说明同一步中较慢的参与者会延后后续阶段。若映射让每个 tile 的计算接近、交换量可控，等待时间会减少。应根据具体同步域、工作分配和通信量分析。 [IPU Programmer’s Guide 固定存档，第 2 章](https://raw.githubusercontent.com/microarch-flow/chip-architecture-wiki/3086204c049a762eb59033f8141fba9e91f4c669/Graphcore_IPU/raw/docs-graphcore-ai-ipu-programmers-guide-en-latest.pdf)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="fabric"></span><span id="芯片迭代过程"></span></div>

## 读带宽时先区分通信边界

| 厂商在 GC200 规格页列出的量 | 口径 |
| --- | --- |
| 62 TB/s | 片上存储带宽。 |
| 7.8 TB/s | tile 间带宽。 |
| 320 GB/s | 芯片间带宽。 |

三个量对应各自的资源，不能相加求应用可见带宽。IPU 的 Streaming Memory 由程序显式安排与 tile 局部存储的数据复制。容量按实际系统配置查找。BSP 规定参与者何时交换，物理交换网络的分层、仲裁和精确时延仍需实现资料或测量。 [厂商演讲，第 5 页](https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Graphcore.SimonKnowles.v04.pdf#page=5) · [IPU Programmer’s Guide 存档](https://raw.githubusercontent.com/microarch-flow/chip-architecture-wiki/3086204c049a762eb59033f8141fba9e91f4c669/Graphcore_IPU/raw/docs-graphcore-ai-ipu-programmers-guide-en-latest.pdf)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="融资和经营情况"></span><span id="从中该获取的经验教训"></span><span id="graphcore-当年的下注20162019-语境下并不荒谬"></span><span id="可能因素原稿分析待独立核验"></span><span id="可带走的原则"></span><span id="我的判断"></span></div>

## 接下来怎么读

- 查看相邻 PE 如何通过消息激活已绑定的任务。 [Cerebras WSE 与 CS](../Cerebras/README.md)
- 查看编译器怎样安排功能切片之间的具体时序。 [Groq 第一代 TSP](../groq-tsp/README.md)
- 查阅历史背景和原始讨论。 [原稿存档](https://github.com/microarch-flow/chip-architecture-wiki/blob/3086204c049a762eb59033f8141fba9e91f4c669/Graphcore_IPU/README.md)
