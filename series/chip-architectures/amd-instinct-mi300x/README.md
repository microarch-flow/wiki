# AMD Instinct MI300X 怎样划分逻辑 GPU？

一颗 MI300X 有八个计算芯粒（XCD）和八个 HBM3 堆栈，显存总容量为 192 GB。驱动可以把八个 XCD 呈现为一个 GPU，也可以让应用分别使用各个 XCD。计算分区决定应用向哪组计算单元提交工作。内存分区决定本地显存分配使用哪些 HBM 堆栈。本文按 AMD 驱动文档 30.10.1 讨论单颗 MI300X 的裸机配置。 [MI300X 数据表](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf) · [AMD 分区概览](https://instinct.docs.amd.com/projects/amdgpu-docs/en/docs-30.10.1/gpu-partitioning/mi300x/overview.html)

## 八个逻辑 GPU 怎样对应四个内存域

先看计算分区。SPX 把八个 XCD 作为一个逻辑 GPU。CPX 把每个 XCD 各自呈现为一个逻辑 GPU。应用在 CPX 下选择某个逻辑设备时，提交给该设备的工作使用对应的 XCD。

再看内存分区。NPS1 将八个 HBM 堆栈作为一个交织域，地址可以分布到八个堆栈。NPS4 将八个堆栈分成四组。每个域有两个 HBM 堆栈。按 AMD 文档，每个域内的两个逻辑 GPU 各有 24 GB 显存份额，各自的地址在该域的两个堆栈上交织。 [AMD 计算与内存分区说明](https://instinct.docs.amd.com/projects/amdgpu-docs/en/docs-30.10.1/gpu-partitioning/mi300x/overview.html#b-memory-partitioning-nps)

| 资源 | SPX + NPS1 | CPX + NPS4 |
| --- | --- | --- |
| 逻辑 GPU | 1 个，含 8 个 XCD | 8 个，各含 1 个 XCD |
| HBM 交织域 | 1 个，含 8 个堆栈 | 4 个，各含 2 个堆栈 |
| 单个逻辑 GPU 的标称显存 | 192 GB | 24 GB |

在 CPX + NPS4 中，**48 GB 是一个内存域的容量，24 GB 是其中一个逻辑 GPU 的份额**。这两个数字分别回答数据会分布到哪里、应用能为一块逻辑 GPU 预算多少显存。本文的数字采用 AMD 的 GB 口径。 [AMD 分区速查与核对方法](https://instinct.docs.amd.com/projects/amdgpu-docs/en/docs-30.10.1/gpu-partitioning/mi300x/quick-start-guide.html)

## 一个模型副本能放进哪个分区

假设要在一块逻辑 GPU 上常驻 160 亿个 BF16 权重，每个权重占 2 B。仅权重就需要 **160 亿 × 2 B = 320 亿 B**，即 32 GB。这个副本已经超出单个 CPX 设备标称的 24 GB。SPX 的标称容量可以容纳这部分权重，完整运行还要为 KV cache、激活和工作区留出显存。

如果继续使用 CPX，需要缩小每个副本的显存需求，或按框架支持的方式把模型分到多个逻辑设备。分片需要考虑跨设备传输以及每片的最大占用。若多个较小的副本能分别在单个 CPX 内运行，CPX 提供了独立放置计算工作的粒度。实际吞吐还取决于每个副本的负载、批大小和显存访问。

## 怎样核对当前配置和可用显存

1. 用 `amd-smi static --partition` 查看 **计算模式、内存模式和分区编号**。以驱动报告的当前状态为准。AMD 30.10.1 速查页的状态示例显示 `CPX + NPS1`，而前一节演示设置 `CPX + NPS4`，核对时应读出两个字段。
2. 在推理进程中选定目标逻辑 GPU，用 HIP 的 `hipMemGetInfo` 查询该设备的可分配总量和当前空闲量，单位为字节。对每个分区分别做预算。空闲量随已有分配变化。
3. 若要比较两种配置的性能，固定模型、精度、并发和请求长度，记录运行时版本、分区与每个副本的资源用量。

[AMD SMI 分区核对示例](https://instinct.docs.amd.com/projects/amdgpu-docs/en/docs-30.10.1/gpu-partitioning/mi300x/quick-start-guide.html#verifying-partition-creation) · [HIP 显存查询接口](https://rocm.docs.amd.com/projects/HIP/en/docs-7.0.0/reference/hip_runtime_api/modules/memory_management.html)

## 接下来怎么读

- 看 GPU 内部的张量搬运和运算怎样重叠。 [NVIDIA H100 SXM](../nvidia-h100-sxm/README.md)
- 看同一产品家族如何让 CPU 和 GPU 在一个封装内共享内存。 [AMD MI300A](../../interconnect/D2D/04-product-cases/amd-mi300a.md)
