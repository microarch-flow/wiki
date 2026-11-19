# 芯片架构实例

从一块张量出发，看具体芯片怎样为计算供数、安排执行和交换结果。本系列覆盖数据中心 GPU、专用 AI 加速器和端侧 NPU。文章按产品和代际说明机制，实验、标称规格和教学算例各自注明条件。

## 数据中心 GPU

1. [NVIDIA H100 SXM](nvidia-h100-sxm/README.md)。从 TMA 搬运跟到 Tensor Core 计算，理解双缓冲和异步同步点。

## 数据中心专用 AI 加速器

1. [AWS Inferentia2](AWS-NeuronCore/README.md)。用一个分块矩阵乘理解 NeuronCore-v2 的 SBUF、PSUM 和多引擎协作。
2. [Google TPU v4](google-tpu-v4/README.md)。比较 MXU 的规则计算与 SparseCore 的索引查表，再看芯片如何组成 Pod。
3. [Meta MTIA 1 与 2i](Meta_MTIA/README.md)。观察推荐模型的激活缓冲、embedding 和权重怎样使用片上 SRAM。
4. [Groq 第一代 TSP](groq-tsp/README.md)。跟踪操作数和指令在预定时刻经过功能切片。
5. [Graphcore GC200](Graphcore_IPU/README.md)。跟踪独立 tile 的局部计算、同步屏障和数据交换。
6. [Cerebras WSE 与 CS](Cerebras/README.md)。区分晶圆上的任务激活与系统侧的权重广播。
7. [SambaNova SN40L](SambaNova/README.md)。从一个算子子图理解空间流水、布局转换和三级内存。
8. [七款数据中心 AI 加速器对照](云端推理芯片架构横向对比报告.md)。按计算、存储、调度与互连对照 2026 年 6 月报告选定的七款器件。

## 端侧 NPU

1. [STM32N657 Neural-ART](stm32n657-neural-art/README.md)。用量化视觉子图解释 NPU 与 CPU 的分工、缓冲占用和软件回退。

## 按问题查阅

- **矩阵计算怎样供数？** 先看 [H100 的双缓冲](nvidia-h100-sxm/README.md#双缓冲能重叠多少时间)，再看 [Inferentia2 的片上累加](AWS-NeuronCore/README.md#两段乘法共用一个累加缓冲)。
- **推荐模型怎样做查表？** 对照 [TPU v4 的 SparseCore](google-tpu-v4/README.md#索引驱动的查表交给-sparsecore) 与 [MTIA 2i 的共享 SRAM 划分](Meta_MTIA/README.md#为什么共享-sram-分成缓存和暂存区)。
- **谁决定何时计算和交换？** 比较 [Groq 的编译期安排](groq-tsp/README.md#一个编译期安排示例)、[Graphcore 的 BSP 屏障](Graphcore_IPU/README.md#两个-tile-如何交换中间结果) 和 [Cerebras 的 wavelet 触发](Cerebras/README.md#晶圆内的消息怎样启动计算)。
- **工作集超出片上容量怎么办？** 看 [SN40L 的外存分层](SambaNova/README.md#从单-rdu-的三层存储到系统)、[CS 的外部权重流](Cerebras/README.md#外部系统怎样供给训练权重) 和 [端侧模型的内存预算](stm32n657-neural-art/README.md#一个中间张量占多少内存)。

## 原始资料

五篇迁入文章和原始图表可在来源仓的固定版本中查看。本站使用自绘教学图和已注明出处的文字。 [来源仓固定提交](https://github.com/microarch-flow/chip-architecture-wiki/tree/3086204c049a762eb59033f8141fba9e91f4c669) · [图片来源台账](https://github.com/microarch-flow/wiki/blob/main/docs/migration/chip-image-provenance.md)
