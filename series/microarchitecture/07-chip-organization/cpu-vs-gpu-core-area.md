# CPU 与 GPU 的资源组织：控制、并行与存储

<span class="micro-legacy-anchor" id="分支预测的职责"></span>


上级：[07 · 芯片顶层组织](./README.md)
相关：[cache 与 scratchpad](../../storage/01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md)、[阵列组织](./gpu-as-tiled-tpu.md)

## 比较什么

CPU 与 GPU 的核心或计算单元通常面向不同并行度和控制需求。比较面积时应固定产品、工艺、频率、统计边界和单位：例如是一个 CPU core、一个 GPU SM，还是每条算术通道。两者的层级和资源共享方式不同，不能仅凭名称直接比较。

需要分别观察算术单元、寄存器、cache 或其他存储、控制逻辑、网络与时钟。GPU 同样具有调度、控制和存储资源；不能假设其控制面积为零，也不能在没有数据时断言 branch predictor 占 CPU 面积的最大份额。

## 控制机制与比较层级

分支预测、发射和提交的职责见[指令生命周期](../03-instruction-execution/instruction-lifecycle.md)；本页关注这些职责如何与算术和存储资源组合。CPU core 通常是独立执行指令流的单元，GPU SM 是共享调度、寄存器与存储资源的一组执行路径，Tensor Core 则是其中的矩阵执行资源。比较面积或吞吐前，必须选同一统计层级。

## GPU 的 warp 调度实例

以 [NVIDIA A100 Ampere 架构](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf) 为例，SM 以 32 线程 warp 调度指令。活动掩码与分歧的基本机制见 [SIMT 主线](../04-parallel-execution/simd-vector-simt.md)。若某 warp 等待数据，调度器可发射其他已就绪 warp；可驻留的 warp 数受寄存器、shared memory 等资源限制。

因此应观察每条路径的有效 lane 数、就绪 warp、访存等待周期和有效吞吐。仅凭分歧存在不能推定吞吐损失比例；如果没有其他就绪 warp，等待更可能暴露。

## 专用化与模型

专用结构可以针对某些工作量调整数据流或资源比例，但需要验证支持范围和软件映射。比较时分别记录算术与存储资源、控制能力、面积、工作量、有效吞吐、延迟和能耗。不能从某个逻辑块的假设面积直接推导 GPU、CPU 或 TPU 的实际面积份额。
