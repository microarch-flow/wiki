# AWS Inferentia2 的 NeuronCore-v2 怎样搬运和累加张量

<div class="chip-legacy-anchors" aria-hidden="true"><span id="aws-inferentia2-neuroncore-v2"></span></div>

Inferentia2 用独立的计算引擎和软件管理的片上存储执行神经网络。用一个分块矩阵乘可以看清分工。DMA 从 HBM 搬来输入，Tensor Engine 在片上累加，后处理引擎再消费结果。本文以一颗 Inferentia2 上的一个 NeuronCore-v2 为主。

<div class="chip-legacy-anchors" aria-hidden="true"><span id="架构总览"></span><span id="关键参数"></span></div>

## 设备和单核资源

| 范围 | 资源 | 在本例中的职责 |
| --- | --- | --- |
| Inferentia2 设备 | 两个 NeuronCore-v2，32 GiB HBM，32 个 DMA 引擎 | HBM 存放设备数据，DMA 负责搬运。 |
| 单个 NeuronCore-v2 | Tensor、Vector、Scalar、GpSimd 四种计算引擎 | 分别处理矩阵计算、向量运算、单元素运算和可编程操作。 |
| 单个 NeuronCore-v2 | 24 MiB 的 SBUF，2 MiB 的 PSUM | SBUF 暂存输入和可复用的数据，PSUM 保存 Tensor Engine 的部分和。 |

同一设备的 HBM 带宽在 NKI v2.29.1 指南中写为 820 GB/s，在 Inferentia2 架构页 v2.31.1 写为 820 GiB/s。两个文档使用了不同单位，本文按来源记录。做定量模型时应先确定采用的带宽口径及实际测量边界。 [NKI v2.29.1 架构指南](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.29.1/nki/guides/architecture/trainium_inferentia2_arch.html) · [Inferentia2 架构 v2.31.1](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.31.1/about-neuron/arch/neuron-hardware/inferentia2.html)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="片上-memorysbuf-psum-是-2d软件管理"></span><span id="tensor-engine-数据流loadstationary-multiplymoving"></span></div>

## 两段乘法共用一个累加缓冲

SBUF 和 PSUM 各分成 128 个 partition。在 NKI 的片上张量布局中，partition 维指定并行分区，free 维表示每个分区内的元素。布局要满足所选指令的限制。矩阵乘法输入位于 SBUF，结果进入 PSUM。Tensor Engine 可在 PSUM 中以 FP32 继续累加。 [NKI 存储分区和 Tensor Engine 说明](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.29.1/nki/guides/architecture/trainium_inferentia2_arch.html)

取 BF16 输入 A 为 64 × 256、B 为 256 × 64。输出 C 为 64 × 64。将两份输入沿收缩维切成两组。每组的收缩维长度为 128。

1. **搬入第一组。** DMA 将两份操作数放入 SBUF。把 A 的分块按转置布局存放，使两个输入都是 128 × 64，收缩维对应 partition 维。
2. **形成第一组部分和。** Tensor Engine 用 LoadStationary 把 A 的分块装到阵列内部，再用 MultiplyMoving 读取 B 的分块。输出落在 PSUM 的 64 × 64 区域。
3. **加上第二组。** 用同一输出坐标处理第二组输入，并累加到同一片 PSUM。两段完成后，C 的该分块才包含完整的收缩维。
4. **消费结果。** 后处理引擎在依赖满足后消费部分和，完成转换或激活并写入 SBUF。需要返回设备内存时，再通过 DMA 写回 HBM。

NKI 的 `nc_matmul` 对应的数学形式是第一个输入转置后与第二个输入相乘。第一组要初始化这一块部分和，后续组累加时应使用相同的目标布局。实际内核还要处理尾块，并检查 SBUF 和 PSUM 容量及端口约束。 [NKI `nc_matmul` 接口](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.29.1/nki/api/generated/nki.isa.nc_matmul.html)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="执行模型多-sequencer多指令流显式同步"></span><span id="软件栈"></span><span id="aws-的下注和初创相反的一条路"></span></div>

## 引擎并行需要显式依赖

各计算引擎有自己的指令流。编译器使用硬件信号量协调已知的数据依赖。以双缓冲为例，DMA 可以尝试提前搬下一组，同时 Tensor Engine 计算当前组。前提是两组有独立的输入缓冲，所需的内存端口允许重叠。未搬完的数据须等待就绪，仍被引擎读取的缓冲须等到可以复用。 [NKI 引擎、仲裁与同步说明](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.29.1/nki/guides/architecture/trainium_inferentia2_arch.html)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="多-core-多-chip-通信"></span><span id="芯片家族与迭代"></span><span id="战略定位与商业背景"></span></div>

## 从单核扩展到多芯片

Inferentia2 和第一代 Trainium 使用 NeuronCore-v2。横向报告的 Trainium2 使用 NeuronCore-v3，设备容量、SBUF 容量和 NeuronLink 代际应各自查规格。Inferentia2 的 NeuronLink-v2 用于设备间通信。公开 NKI 指南支持解释引擎和缓冲的编程行为，具体跨核拓扑及事务细节仍需实现资料。建模时若假定数据经 HBM 中转，应把它列为待验证的路径。 [Trainium2 NKI 指南](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/guides/architecture/trainium2_arch.html) · [原稿存档](https://github.com/microarch-flow/chip-architecture-wiki/blob/3086204c049a762eb59033f8141fba9e91f4c669/AWS-NeuronCore/README.md)

<div class="chip-legacy-anchors" aria-hidden="true"><span id="从中该获取的经验教训"></span><span id="与-graphcore-cerebras-sambanova-的对照"></span></div>

## 接下来怎么读

- 查看 GPU 上的异步张量搬运、共享内存和缓冲回收。 [NVIDIA H100 SXM](../nvidia-h100-sxm/README.md)
- 比较不同代际的设备参数、工作存储和编程接口。 [七款数据中心 AI 加速器对照](../云端推理芯片架构横向对比报告.md)
