# AWS Trainium2 怎样组成逻辑核？

一颗 Trainium2 有八个物理 NeuronCore-v3。AWS Neuron 可以让软件看到八个逻辑核，也可以把物理核两两分组，让软件看到四个逻辑核。分组改变了编译器分派工作的单位。本文用一个 NKI 逐元素算子，跟踪两个物理核如何分取同一输入张量并写回结果。 [Trainium2 架构指南](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.33.1/nki/guides/architecture/trainium2_arch.html) · [AWS 逻辑核配置](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.33.1/about-neuron/arch/neuron-features/logical-neuroncore-config.html)

## 同一颗芯片怎样呈现八个或四个逻辑核

物理 NeuronCore（PNC）是实际执行指令的硬件。逻辑 NeuronCore（LNC）是编译器、运行时和应用使用的资源单位。配置中的 1 或 2 表示每个逻辑核包含多少个物理核。

| 配置 | 每个逻辑核包含的物理核 | 一颗芯片上的逻辑核 |
| --- | ---: | ---: |
| `LNC=1` | 1 | 8 |
| `LNC=2` | 2 | 4 |

每个物理核有自己的 28 MiB SBUF 和 2 MiB PSUM。SBUF 保存待处理的分块，PSUM 用于矩阵计算的部分和。整颗芯片配置 96 GiB HBM。在 `LNC=2` 下，组内两个物理核可在同一地址空间访问共享 HBM，并分别执行自己的指令流。临时张量仍按各物理核的片上存储容量规划。 [NeuronCore-v3 的片上存储](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.33.1/nki/guides/architecture/trainium2_arch.html#neuroncore-v3-compute-engine-updates) · [逻辑核的内存与指令流](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.33.1/nki/get-started/about/lnc.html)

这一分组改变的是软件视图。AWS 的配置图也显示，在 `LNC=1` 下，同一对物理核仍可访问对应的 HBM 区域。 [AWS 两种逻辑核配置图](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.33.1/about-neuron/arch/neuron-features/logical-neuroncore-config.html#logical-neuroncore-configurations)

## 两个物理核怎样处理同一个张量

AWS 文档用一个形状为 2 × 128 × 128 的张量演示逐元素求倒数。取 `LNC=2`，输入和输出在共享 HBM，并假定输入元素均为非零。第一个维度有两个切片，分别分给同一逻辑核内的程序 0 和程序 1。

| 步骤 | 程序 0 | 程序 1 |
| --- | --- | --- |
| 读输入 | 用 `program_id` 选切片 0，DMA 搬入本核 SBUF。 | 选切片 1，DMA 搬入本核 SBUF。 |
| 计算 | 对本地切片逐元素求倒数。 | 对本地切片执行同样的运算。 |
| 写回 | DMA 写入共享输出的切片 0。 | DMA 写入共享输出的切片 1。 |

输入按切片划分，两个程序写入各自的输出区域。逐元素结果在写回时已经完整。例如，若切片 0 和切片 1 首元素分别为 2 和 4，输出对应位置就是 0.5 和 0.25。若改成沿收缩维切分矩阵乘，各核会得到部分和，程序还要安排归约才能形成完整输出。 [AWS NKI 共享 HBM 算例](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.33.1/nki/get-started/about/lnc.html#writing-nki-kernels-with-lnc-specific-apis)

## 编译和运行时必须使用同一分组

在计算图中，NKI 内核的 LNC 配置须与 `neuronx-cc` 的 `--logical-nc-config` 一致。加载已编译模型时，运行时的 `NEURON_LOGICAL_NC_CONFIG` 也须匹配。例如，按 `LNC=2` 编译的 NEFF 执行文件内含两份面向物理核的指令流，应加载到同样按两个物理核分组的逻辑核上。 [AWS 编译和运行时配置](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.33.1/about-neuron/arch/neuron-features/logical-neuroncore-config.html#compiler-and-runtime-settings)

`program_id` 在编译时确定，可用于生成各核的指令。设备运行时的控制流另有约束。例如，若输入数据使一个物理核执行四次循环、另一个执行三次，AWS 文档指出这种内核可能挂起或给出错误结果。 [AWS NKI 控制流限制](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.33.1/nki/get-started/about/lnc.html)

逻辑核数说明软件怎样分派片上工作。扩展到多个 Trainium2 时，需要再看芯片之间的连接与集合通信。AWS 的 Trn2 架构文档按实例给出了 NeuronLink-v3 的适用范围。 [EC2 Trn2 实例架构](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.33.1/about-neuron/arch/neuron-hardware/trn2-arch.html)

## 接下来怎么读

- 从单核分块矩阵乘理解 SBUF、PSUM 和计算引擎怎样配合。 [AWS Inferentia2](../AWS-NeuronCore/README.md)
- 比较物理计算资源怎样通过另一种分区方式呈现给应用。 [AMD Instinct MI300X](../amd-instinct-mi300x/README.md)
