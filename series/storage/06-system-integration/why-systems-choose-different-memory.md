# 不同计算系统如何选择存储层次

<span id="mcucpugpunpu-为什么选择不同存储器"></span>

上级：[存储系统集成与选型](./README.md)
相关：[存储层次与系统角色](../01-memory-hierarchy/01-system-basics/memory-hierarchy-as-system.md) · [DRAM 接口家族比较](../03-dram/protocols/ddr-lpddr-gddr-hbm-tradeoff-map.md)

## 这页在回答什么问题

MCU、CPU、GPU、NPU 为什么会采用不同的存储组织？处理器名称只能提示可能的需求，不能单独决定所用存储器。应先看工作负载的访问模式、软件契约和产品约束，再比较具体的层次组合。

## 不同处理器的存储目标

| 系统与任务示例 | 需要先问的问题 | 可能的存储组织 |
| --- | --- | --- |
| MCU 控制回路 | 中断和关键路径的最坏响应时间是多少？待机功耗、芯片面积如何受限？ | 片上 flash 与 SRAM；需要确定性访问时，也可能配置 TCM。 |
| 通用 CPU | 多种程序的工作集如何变化？软件希望怎样访问内存？ | cache 层次配合系统内存；系统内存可以是 DDR、LPDDR，或其他具体实现。 |
| GPU 图形或并行计算 | 线程的请求能否合并？并行工作能否掩盖延迟？外存是否持续供数不足？ | 寄存器和片上缓存配合 GDDR、HBM 或共享系统内存。 |
| NPU 推理或训练 | 权重、激活和部分和能复用多少次？谁负责放置与搬运？ | 多级片上存储配合 DDR、LPDDR 或 HBM；管理方式取决于设计。 |

这些是问题与候选，不是处理器类型到器件类型的一一映射。同一系统中也可以同时有硬件管理的 cache 和软件管理的缓冲区。某条路径适合实时任务，还须检查仲裁、冲突、刷新和软件执行等最坏情况；TCM 名称本身不能证明整个系统满足 deadline。

### 用实例检查边界

[Arm Cortex-M7 用户指南](https://support.arm.com/documentation/dui0646/c/Introduction/About-the-Cortex-M7-processor-and-core-peripherals/Cortex-M7-processor-features-and-benefits-summary)将 cache 和 TCM 列为可选内存系统功能。具体 MCU 是否包含它们，要看芯片实现。通用 CPU 也不只连接 DIMM：例如 [NVIDIA Grace CPU](https://www.nvidia.com/en-gb/data-center/grace-cpu-superchip/)使用 LPDDR5X。

[Google 第一代 TPU 的论文](https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/)描述了软件管理的片上存储，用于该具体加速器的推理数据流。这是一个 NPU 类系统实例，不表示所有 NPU 都采用相同的片上组织。

### 从需求到选择

假设两个候选系统都能容纳工作集。若任务每次访问的数据量小、对尾延迟敏感，比较时应记录命中率、未命中路径和竞争，而不是只看总带宽。若任务持续流式读取大量数据，则要检查能否形成足够的并发、片上能否消费数据，以及持续有效带宽。

软件模型同样影响选择。硬件管理的 cache 可对软件隐藏部分数据移动；显式管理的缓冲区使软件能控制放置，但需要编译器或程序安排搬运、同步和容量。两者都需要评估冲突与代价，具体机制见 [Cache 与 scratchpad](../01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md)。

## 一句话理解

存储路线是多层资源和管理方式的组合；判断它是否合适，要回到具体任务与系统约束。

## 建模启示

先列硬约束：可用容量、响应时限、功耗上限、封装和供应条件。排除不满足约束的候选后，再比较同一任务下的吞吐、能耗和成本。记录每层的容量、可用带宽、访问管理方式、共享资源及数据放置；不要只凭 MCU、CPU、GPU 或 NPU 的标签填入固定器件。

如果使用加权评分，必须说明各指标的单位、归一化基准、权重和数据来源。结果只适用于所评估的候选集合与工作负载，不能据此声称找到全局或局部最优。
