---
title: "计算微架构：执行、数据通路与资源协作"
---

# 计算微架构：执行、数据通路与资源协作

<span id="微架构执行数据通路与资源协作" aria-hidden="true"></span>给芯片一段计算，谁来算，先得到的数放在哪里，下一项工作要等到哪一拍？从一个点积开始，逐拍跟踪数据和指令，再把同样的问题带到计算阵列和整块任务。

## 从一个点积到整块矩阵：六个问题 {#first-reads}

1. [芯片怎样算出一个点积？](./00-overview/microarchitecture-decisions.md)　用一个乘法器算出 `2×4 + 3×5`，再换成两个，看看哪一拍能省下来。
2. [第一份结果还没出来，下一份能开始吗？](./02-pipeline/pipeline-register-insertion.md)　跟着几组输入走过三级流水线，比较独立运算和依赖前一次结果的运算。
3. [第二条指令在等，第三条能先执行吗？](./03-instruction-execution/dependencies-bypass-issue.md)　逐拍看三条指令的操作数何时到齐、执行端口由谁使用，以及结果何时提交。
4. **多个单元怎样分工？** 先读《[十个独立的加法，怎样分给几条执行通道？](./04-parallel-execution/simd-vector-simt.md)》，数出最后一组有几条通道在工作。再读《[四个乘加单元，为什么两拍算不完八次乘加？](./04-parallel-execution/why-systolic-array.md)》，看看最右下角何时凑齐两个操作数。
5. [第一块还在算，第二块能开始搬吗？](./06-task-control/dma-compute-writeback.md)　跟着两块数据从搬入走到写回，看两块缓冲共用一个端口时，哪一步必须等。
6. [同一块矩阵，CPU、GPU 和 NPU 怎样算？](./07-chip-organization/cpu-vs-gpu-core-area.md)　把同一份工作交给三种处理器，对照谁发起运算、操作数怎样到达、部分和留在哪里。

## 专题地图 {#topics}

| 专题 | 核心问题 | 目前的入口 |
| --- | --- | --- |
| [数值格式与运算数据通路](./01-datapath/README.md) | 操作数如何表示、选择并完成运算 | MAC、压缩树、位宽、格式、选择网络 |
| [流水线、时序与时钟域](./02-pipeline/README.md) | 数据何时采样，何时推进或等待 | 电路基础、setup/hold、流水级、依赖、反压 |
| [指令执行与处理器控制](./03-instruction-execution/README.md) | 指令何时可执行，结果何时成为正式状态 | 指令生命周期、数据依赖、旁路与发射 |
| [并行执行与计算阵列](./04-parallel-execution/README.md) | 工作如何分配到通道与 PE | SIMD、向量、SIMT、systolic 与 dataflow |
| [DMA 与异步数据搬运](./05-dma/README.md) | 搬运任务如何展开、执行和完成 | 九章：语义、引擎、编程、集成、建模与案例 |
| [任务控制、同步与资源管理](./06-task-control/README.md) | 多个引擎如何协作，buffer 何时能复用 | DMA、计算、写回的事件与所有权 |
| [处理单元与片上组织](./07-chip-organization/README.md) | 同一块矩阵怎样分给不同执行资源 | CPU、GPU、NPU 的执行过程与跨单元分块 |
| [存内与近存计算](./08-in-memory-computing/README.md) | 把计算移近或放入存储路径会改变什么 | CIM、PIM、NMC 的物理机制与系统边界 |
| [功耗管理与实现权衡](./09-power-implementation/README.md) | 执行方式如何影响能量与实现成本 | 频率、功率、任务能量、FPGA/ASIC |

[分析方法与查阅练习](./reading-and-reference/README.md)提供指标定义、建模建议、自测和跨专题路线。分支预测、乱序窗口、LSU/TLB、CDC 电路和电源状态管理还未形成完整专题；现有导读会指出相应边界。

## 按处理器类型阅读

- **CPU 路线**：[第三条指令能先执行吗](./03-instruction-execution/dependencies-bypass-issue.md) → [从取指到提交](./03-instruction-execution/instruction-lifecycle.md) → [流水线与时序](./02-pipeline/README.md) → [三种处理器怎样算同一块矩阵](./07-chip-organization/cpu-vs-gpu-core-area.md)。
- **GPU 路线**：[十个加法怎样分给执行通道](./04-parallel-execution/simd-vector-simt.md) → [三种处理器怎样算同一块矩阵](./07-chip-organization/cpu-vs-gpu-core-area.md) → [矩阵分给两个单元时的数据传递](./07-chip-organization/gpu-as-tiled-tpu.md) → [GPU Copy Engine](./05-dma/07-workloads-case-studies/gpu-copy-engine-case-card.md)。
- **NPU 路线**：[运算数据通路](./01-datapath/README.md) → [阵列逐拍示例](./04-parallel-execution/why-systolic-array.md) → [数据流](./04-parallel-execution/dataflow-taxonomy.md) → [跨引擎协作](./06-task-control/dma-compute-writeback.md)。

<section class="reading-section" id="on-chip-data-supply" markdown="1">

## 片上存储与数据供给

沿同一数据路径阅读：[分块与双缓冲](./05-dma/04-programming-model/tiling-double-buffering.md) → [SRAM 端口](../storage/02-sram/foundations/single-port-dual-port-multi-port.md) → [权重载入与阵列供数](./04-parallel-execution/weight-loading-and-trickle-feed.md)。

各篇分别解释软件编排、存储服务能力和阵列加载，不把三者合并成一个理想带宽参数。

</section>

<section class="reading-section" id="architecture-modeling" markdown="1">

## 架构建模与性能分析

先固定[工作负载](../workload/06-chip-workload-analysis/workload-analysis-methodology.md)和[统计指标](./reading-and-reference/02-analysis/compute-communication-ratio.md)，再建立资源和事件模型。[DRAM 控制器建模](../storage/04-dram-controller/mc-modeling-for-simulation.md)与 [NoC 验证和校准](../interconnect/NOC/08-simulator-construction/verification-and-calibration.md)给出相邻系统的具体做法。

[Archax 建模建议](./reading-and-reference/03-modeling/modeling-insights.md)是一个应用入口。建议字段与目标版本实际支持的字段需要分别核对。

</section>

## 与相邻系列的接口

[存储系统](../storage/README.md)负责 cache、SRAM、DRAM 和控制器；[芯片与系统互连](../interconnect/README.md)负责事务、NoC 和链路；[SerDes](../interconnect/SERDES/README.md)解释高速电链路。这里保留影响执行的请求、带宽、顺序、可见性和反压接口。

完整器件参数与芯片实例，仍需回到对应代际的官方文档。本文的机制分类是阅读组织方式，不是把所有产品固定分成九类。
