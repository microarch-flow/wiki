# GEMM 通信案例：分块和放置怎样改变流量？

<span id="workload-gemm-on-noc"></span>

上级：[07 工作负载与系统案例](../SUMMARY.md#workload-cases)；原章节：[06 AI NOC Specifics](./README.md)

相关：[工作负载与 NoC 流量](./why-ai-noc-is-different.md)、[广播、多播与复制](./broadcast-multicast-tree.md)、[归约与 AllReduce](./reduction-and-collective-networks.md)

<span id="这页在回答什么问题"></span><span id="gemm-为什么重要"></span>矩阵乘法 C = A × B 可以用不同方式分块和放置。同一个算子可能需要分发输入、在 tile 间转发数据或归约部分和，也可能只在本地累加。流量来自具体映射，而不是算子名称。

## 一个 2×2 tile 的映射

<span id="一个可核算的分块"></span>构造例：A、B、C 都是 4×4 矩阵，输入和最终输出均为 2 B/元素。4 个 tile 排成 2×2，各自负责 C 的一个 2×2 输出块；K 维度分为两个长度为 2 的步骤。每个输入块为 2×2×2 = **8 B**。

对每个 K 步，假设 A 的每个行块已在该行左侧 tile，B 的每个列块已在该列上方 tile。每个 A 块供同行两个 tile 使用，每个 B 块供同列两个 tile 使用。源 tile 使用本地副本，同时向另一个 tile 发送一份；只计算这些分发，不包括预先加载输入、包头、填充及其他流量。

| 统计口径 | 两个 K 步的数量 | 原因 |
| --- | ---: | --- |
| 不同输入块的逻辑 payload | 64 B | 每步 2 个 A 块和 2 个 B 块，共 8 个 8 B 块。 |
| 目的端交付量 | 128 B | 每个块供两个 tile 使用，按每个消费者各计一份。 |
| 本地交付 | 64 B | 每个块的一份在其源 tile 本地使用。 |
| NoC 注入 payload | 64 B | 每个块向另一个 tile 发送一次。 |
| NoC payload byte-hop | 64 B·hop | 每份远端副本均走一条相邻的有向链路。 |

这组网络计数依赖上述具体位置和一跳路径。若输入来自阵列外的存储端点，或每个目的端分别通过更长路径读取，就要重新计数。这里每份块只有一个远端消费者，单独为它增加网络内多播并不会减少远端副本数。[广播、多播与复制](./broadcast-multicast-tree.md)讨论多个远端消费者共享路径时的取舍。

## 部分和在哪里累加

<span id="它最常问的三件事"></span><span id="3-partial-sum-怎么收"></span>在上面的 output-stationary 映射中，每个 tile 对自己的输出块累加两个 K 步的结果，不需要跨 tile 归约 partial sum。全部输出共有 16 个元素，按最终输出 2 B/元素写回时是 **32 B**；写回是否经过 NoC 由目的位置决定。

如果把同一输出块的不同 K 分片分配给不同 tile，就必须按该映射传递并合并部分和。输入与输出使用 2 B 不代表内部累加也是 2 B：假设部分和为 FP32，传送或存放它时应按 4 B/元素计算；最终是否转换及如何舍入由算术契约决定。

## 分发、前传与存储边界

<span id="1-权重和激活怎么分发"></span>输入由谁提供、相同块被多少消费者使用，决定源端注入和共享边是否重复承载数据。比较多份单播与共享树时，应固定目的集合与物理路径，并分别统计注入、每条链路和接收端，而不只比较逻辑块数量。

<span id="2-中间结果要不要直接-forward"></span>中间数据可以留在本地、经网络送到下游 tile，或写入某个共享存储后再读取。只有实际路径经过 HBM，才计入 HBM 往返；经过共享 SRAM、直连或片上网络的代价也要按各自路径计算。直接前传是否更好，还取决于接收缓冲、依赖和能否与计算重叠。

<span id="gemm-更常偏向-deterministic-设计"></span>规则的分块便于提前规划 placement 和依赖，但不自动保证固定完成时刻。实际服务还受端点、缓冲和其他流量影响。[确定性与静态调度](./deterministic-noc-and-static-scheduling.md)说明计划与预留的区别。

## 如何比较候选映射

<span id="它通常不是最难的动态案例"></span><span id="建模启示"></span>固定矩阵、数据类型、结果精度和硬件资源，比较输出本地累加与跨 tile K 分片。分别记录输入块重用、注入 payload、每条链路的 byte-hop、接收与累加等待，以及最终任务完成时间。计算与通信只有在资源和依赖允许时才能重叠。

<span id="一句话理解"></span>规则 GEMM 是检查映射的基线，并不预设一定有 multicast、forwarding 或跨 tile reduce。更大的 4×4 tile 示例和可执行 trace 留在[性能评估章节](../07-evaluation-methodology/from-workload-to-traffic-trace.md)。

空间数据流对存储、复用和通信的影响可参考 [Eyeriss 原论文](https://dspace.mit.edu/entities/publication/f6342515-2b7d-411c-a8ad-a9edb23dd394)；其卷积加速器配置是具体研究实例，不是所有 GEMM 网络的固定结构。
