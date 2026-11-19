# NVIDIA H100 SXM 的 TMA 怎样给 Tensor Core 供数

一次矩阵乘法可以把输入分成多块。Hopper GPU 的张量内存加速器（TMA）负责搬运其中一块。流式多处理器（SM）可以在搬运期间用 Tensor Core 处理上一块。数据准备和缓冲回收都需要同步。本文跟踪单颗 H100 SXM 上一个线程块内的这条路径。

## 从设备全局内存到共享内存

H100 SXM 配置 80 GB HBM3，标称显存带宽为 3.35 TB/s。这里的 GB 和 TB/s 采用厂商数据表口径。程序向 TMA 提供的是**全局内存地址和张量布局**，缓存状态会影响某次请求是否需要访问 HBM。在本文的路径中，目标是当前 SM 上由线程块管理的共享内存。 [H100 数据表](https://resources.nvidia.com/en-us-gpu-resources/h100-datasheet-24306?download=1) · [Hopper 调优指南](https://docs.nvidia.com/cuda/hopper-tuning-guide/#tensor-memory-accelerator)

| 对象 | 职责 |
| --- | --- |
| 张量映射描述符 | 记录地址、形状、步长和共享内存布局。发起搬运时指定目标缓冲和分块坐标。 |
| TMA | 按描述符将输入分块异步搬入共享内存。在本文使用的方向上，完成事务计入内存屏障（mbarrier）。 |
| Warpgroup | 由四个 warp 协作执行异步矩阵乘加（WGMMA）。这里选择两份操作数都在共享内存的形式，累加结果位于寄存器中。 |

指令对地址、对齐和布局有约束。实现时需要按所用指令和数据类型核对，并处理边界块。本文只讨论尺寸整除、描述符合法的分块。 [CUDA 异步搬运说明](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/async-copies.html) · [PTX WGMMA 指令说明](https://docs.nvidia.com/cuda/archive/12.0.0/parallel-thread-execution/index.html#asynchronous-warpgroup-level-matrix-instructions)

## 一个缓冲何时能读、何时能覆盖

每个缓冲容纳矩阵 A 和 B 的一对分块。填充、消费与回收按以下顺序完成。

1. **发起搬运。** 生产者取得空闲缓冲，发起 A、B 两次搬运。消费前需要观察到两份数据都已到达当前屏障阶段。
2. **发起计算。** 消费者等待数据就绪，用该缓冲发起 WGMMA，将这一段收缩维的结果累加到寄存器中。
3. **归还缓冲。** 消费者确认还在引用该缓冲的异步矩阵乘加已经完成，再通知生产者覆盖这块共享内存。

第一处同步保护**读之前的数据就绪**。第二处同步保护**覆盖之前的最后一次读取**。例如，插入 WGMMA 指令后立即发起同一地址的 TMA 写入，可能让仍在运行的计算读到下一块的数据。实际内核还要遵守 WGMMA 指令的 fence、commit 和 wait 规则。 [CUTLASS 的 Hopper WGMMA 编程说明](https://docs.nvidia.com/cutlass/4.5.2/media/docs/pythonDSL/mma_docs/wgmma_programming.html)

## 双缓冲能重叠多少时间

假定输出分块为 64 × 64，收缩维每次处理 64 个元素。A、B 分块均为 64 × 64 个 BF16 元素，每元素 2 B。单个缓冲至少需要 16 KiB，两个缓冲合计至少需要 32 KiB。该数值只包含两组输入，实际分配还要核对填充、对齐、屏障和其他共享内存用量。

假定三组输入，每组搬运耗时 3 个时间单位，计算耗时 5 个。假定一组搬运可以与另一组计算完全重叠，忽略发起、同步和写回开销。理想时间线如下。

| 时间区间 | 计算路径 | 搬运路径 |
| --- | --- | --- |
| 0–3 | 等待第 0 组 | 第 0 组写入槽 0 |
| 3–8 | 处理第 0 组 | 第 1 组写入槽 1，时刻 6 完成 |
| 8–13 | 处理第 1 组 | 第 2 组写入槽 0，时刻 11 完成 |
| 13–18 | 处理第 2 组 | 本轮搬运结束 |

在这些假设下，逐组串行需要 24 个时间单位，双缓冲需要 18 个。首组的搬运和最后一组的计算仍在关键路径上。增加缓冲会占用共享内存，可能减少同一 SM 上能同时驻留的线程块。实际收益取决于有效带宽、计算时间、同步开销与资源争用。

## 接下来怎么读

- 看软件怎样显式为另一种矩阵引擎分配输入和累加缓冲。 [AWS Inferentia2](../AWS-NeuronCore/README.md)
- 比较两类芯片中的矩阵单元、局部存储和共享边界。 [GPU 与 TPU 的片上组织](../../microarchitecture/07-chip-organization/gpu-as-tiled-tpu.md)
- 将单芯片资源扩展到指定模型的设备容量与推理预算。 [Llama 3 70B 与 H100 条件算例](../../inference-runtime/09-measurement-and-cases/15-quantitative-estimation.md)
