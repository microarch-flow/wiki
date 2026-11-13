# 把 register、cache、scratchpad、DRAM、HBM 看作一个系统

上级：[系统视角](./README.md)

相关：[RAM 分类与命名](./taxonomy.md) · [Cache 与 scratchpad](../02-access-paths/cache-vs-scratchpad.md) · [速度、容量、成本、功耗](./memory-hierarchy-tension.md)

## 这页在回答什么问题

一份数据可能存放在设备内存中，也可能被保留在 cache 或 scratchpad 中供计算使用。这些存储资源的区别，不只是容量和访问时间：它们提供不同的访问方式，也由不同的参与方决定数据何时进入、离开或被覆盖。

本文从**系统角色**出发，比较各资源的职责、数据管理和协作方式。不同名称所处的分类角度见 [RAM 分类与命名](./taxonomy.md)；一次读取的完整路径见 [RAM 存储系统概览](../README.md)。

## 各存储层的职责与接口

| 角色 | 接收什么、提供什么 | 谁决定数据的位置和生命周期？ | 常见实现或用途 |
| --- | --- | --- | --- |
| Register file | 接收寄存器读写请求，为执行单元提供操作数并接收结果。 | 指令使用寄存器；编译器和处理器内部机制分别参与分配或映射。端口和时序由具体实现决定。 | 可用存储阵列或触发器等电路实现。 |
| Cache | 接收地址和读写请求；命中时按其权限和策略服务，未命中时可能向其他层请求数据。 | 硬件按查找、填充和替换等策略管理副本；写入策略和一致性能力由实现定义。 | 数据阵列常用 SRAM；系统中也有采用其他存储技术的 cache。 |
| Scratchpad | 接收对显式本地地址或数据区域的访问，向计算单元提供数据并接收写入。 | 软件、编译器或显式调度机制安排放置、搬运和覆盖；具体责任取决于系统。 | 常用片上 SRAM 实现，用于保存一段计算需要的数据。 |
| TCM | 为处理器或其他使用方提供紧耦合的本地访问。 | 地址映射、加载和访问权限由具体实现及软件约定决定。 | 可用于需要分析访问时间的本地代码或数据。 |
| 主存或设备内存 | 接收系统或设备对相应地址空间的访问，为程序数据提供存放空间。 | 地址空间、数据放置和权限由硬件及系统软件共同定义。 | 常使用 DRAM，例如基于 DDR4 SDRAM、LPDDR 或 HBM 的系统。 |

表中列的是不同的**职责**，不是一条所有系统都必须经过的固定路径。一个 cache miss 可能由其他 cache 满足；scratchpad 也可以由计算线程或其他搬运机制填充。资源能否并发服务，还取决于端口、bank、仲裁和共享通路。

Cache 对地址做查找，并按实现规则处理命中、缺失和替换。预取可以预测未来可能访问的数据，但不是每次 cache 填充都依赖预取。Scratchpad 通常要求使用方明确安排数据，因此还需要决定何时启动搬运、何时消费和何时覆盖。两者的访问都可能等待共享资源；详细比较见 [Cache 与 scratchpad](../02-access-paths/cache-vs-scratchpad.md)。

## 角色与存储技术怎样对应？

**角色说明资源做什么，存储技术说明数据怎样保存。**例如，scratchpad 是一种显式管理的本地存储角色，SRAM 是常见的实现技术；不能把“片上 SRAM”和“scratchpad”直接画成必然先后经过的两层。

[NVIDIA 的 CUDA 编程指南](https://docs.nvidia.com/cuda/archive/13.2.1/cuda-programming-guide/02-basics/writing-cuda-kernels.html)描述了一种具体组织：shared memory 可作为使用者管理的 scratchpad，且与 L1 cache 使用同一物理资源。这里，两种角色的管理方式不同，但片上资源可以共享。

HBM 涉及堆叠 DRAM、接口和集成方式；它在系统中承担什么角色，要看具体配置。例如，[Intel Xeon Max 的配置指南](https://cdrdv2-public.intel.com/769060/354227-intel-xeon-cpu-max-series-configuration-and-tuning-guide.pdf)描述了将 HBM 用作 DDR 主存的 memory-side cache 的模式，也描述了将 HBM 和 DDR 作为不同内存区域使用的模式。

同样，DDR4 SDRAM 是具体 DRAM 产品和接口家族；单独的 DDR 还可能表示双倍数据率传输方式。比较接口或器件时，应先写清具体名称和配置。

## 数据交接：何时可以被另一个参与方使用？

数据放进某个资源后，还要确定其他参与方能否看到它。以 CPU 和 non-coherent DMA 共享一个输入 buffer 为例，假设 CPU 使用 write-back cache，DMA 不通过与该 cache 保持硬件一致性的路径读取：

1. CPU 修改 buffer。新值可能仍在 CPU cache 中，对 DMA 读取的内存路径尚不可见。
2. 把 buffer 交给设备前，软件按平台的 DMA 映射与同步规则处理数据，并保证相关写入先于设备开始读取。
3. DMA 完成读取前，CPU 不应违反该系统的 buffer 使用权约定，例如提前修改或复用设备仍在读取的数据。
4. 如果设备也写入 buffer，CPU 再次访问前还要按传输方向和平台规则完成相应的同步或映射结束操作。

这里需要区分三个问题：**数据是否可见、操作是否按要求排序、buffer 何时可以由下一方使用**。硬件一致性可以改变所需的 cache 维护方式，但不会自动替代所有同步和使用权安排。[Linux DMA 映射指南](https://docs.kernel.org/core-api/dma-api-howto.html)说明了 DMA 映射和重复使用 buffer 时的同步要求；具体示例见 [Coherent / Non-Coherent DMA](../../../microarchitecture/DMA/wiki/02-fundamentals/noncoherent-vs-coherent-dma.md)。

## 一句话理解

存储系统由承担不同职责的资源组成。描述一层时，既要说明它服务什么请求，也要说明谁管理数据、使用哪种实现，以及数据何时能被其他参与方使用。

## 建模启示

先确定模型要回答的问题，再按需要区分以下信息：

| 需要区分的内容 | 要回答的问题 |
| --- | --- |
| 角色与实现 | 资源承担 cache、scratchpad 还是其他角色？其容量和访问规则来自什么实现？ |
| 放置与替换 | 谁决定数据何时进入、保留或离开？是否需要表示命中和替换状态？ |
| 搬运与连接 | 谁发起搬运？源、目的地、粒度和沿途共享资源是什么？ |
| 完成与可见性 | 哪个事件表示搬运完成？数据何时对消费者可用，何时允许覆盖？ |
| 性能边界 | 请求在哪个接口被接收和响应？端口、bank 和链路有哪些约束？ |

例如，研究 cache 命中变化时需要考虑地址流、状态和替换规则；研究 scratchpad 数据能否按时供给时，需要考虑放置、搬运、可见性和资源竞争。DMA 是可能发起搬运的参与方，不能仅凭它的存在推断由谁决定数据放置。

## 接下来怎么读？

- [存储系统为何难设计](./problem-statement.md)：从一次请求看状态、共享资源和限制如何连接。
- [局部性与数据搬运](./locality-working-set-data-movement.md)：用访问序列和流量算例分析复用。
- [Cache 与 DRAM 协同](../02-access-paths/cache-dram-coordination.md)：继续看 miss、填充和写回。
- [Scratchpad 和 cache 的实现](../../02-sram/applications/scratchpad-vs-cache.md)：比较管理方式及实现代价。
