# RAM 存储系统概览：数据如何从存储走到计算

<!-- nav-title: 存储层级与数据路径 -->

上级：[存储系统](../README.md)

相关：[存储层次与系统角色](01-system-basics/memory-hierarchy-as-system.md) · [局部性与数据搬运](01-system-basics/locality-working-set-data-movement.md) · [学习路线](../reading-and-reference/01-reading/learning-roadmap.md)

计算需要输入数据，也会产生需要保存的结果。存储系统要在容量、访问时间、带宽、能耗和成本等约束下，把数据提供给计算单元。

数据可以放在哪里？读取时经过哪些资源？一次搬运怎样服务后续计算？本文用处理器读取和加速器搬运两个例子，建立理解存储层级与数据路径的基础。

## 1. 为什么需要存储层级？ {#1-ram-是什么}

计算经常需要快速访问一小部分数据，也需要保存更大的数据集合。靠近计算的存储资源可以承担频繁访问，但增加容量、端口和带宽需要面积、功耗和布线等资源。系统因此会结合多种存储资源，让不同位置承担不同职责。

近端存储能否减少搬运，与工作负载的**局部性**和数据能否保留有关：数据在被取回后，是否会在一段时间内再次使用；相邻数据被一起取回后，是否会被后续计算使用。如果数据一直没有再次使用，或者复用前已经被替换，本地副本就不能带来同样的收益。[MIT 的存储层次课程](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/pages/c14/c14s1/)用 cache 和局部性解释了这种分层方式。

RAM 是 random-access memory，通常译为随机存取存储器：它允许根据地址选择存储位置，不必从头顺序经过更早的位置。随机存取本身不保证所有地址访问时间相同，也不保证多个请求没有资源冲突。

### 存储技术、系统角色与接口 {#4-不要把不同层的名字混在一起}

理解一条数据路径时，要区分资源是什么，以及系统怎样使用它：

- **SRAM 和 DRAM**是存储技术；它们各有保存数据和组织访问的方式。
- **Cache** 和 **scratchpad** 是系统角色。Cache 通常由硬件查找、填充和替换数据；scratchpad 通常由软件、编译器或其他调度机制安排数据放置与使用。
- **DDR 等接口**规定控制器和相应存储器之间怎样交换命令、数据及时序。一个系统会同时涉及存储技术、角色和接口。

例如，cache 的数据阵列和 scratchpad 常用 SRAM；主存或设备内存常用 DRAM。Cache 还需要 tag、命中判断和替换等逻辑，不能把它等同于 SRAM。名称的进一步区分见 [RAM 分类与命名](./01-system-basics/taxonomy.md)。

### SRAM 与 DRAM 的常见用途 {#5-sram-和-dram-的基本差异}

常见 SRAM 单元用双稳态电路保存数据，不需要 DRAM 式周期刷新；常见 DRAM 单元用电荷保存数据，需要按器件要求维持数据。SRAM 常用于片上局部存储，DRAM 常用于容量较大的主存或设备内存。单元结构、访问过程和系统选择的关系见 [SRAM 与 DRAM 的分化](./01-system-basics/sram-dram-divergence.md)。

## 2. 先看两条数据路径

[![处理器例子中，请求从处理器经 cache 和内存控制器到 DRAM，数据沿反方向返回。加速器例子中，DMA 发起读取和写入请求，数据从 DRAM 经控制器和片上互连到 scratchpad，再供计算单元使用。](../assets/ram-system-overview.svg?v=bb10dad340f4)](../assets/ram-system-overview.svg){.ram-overview-diagram-wide}
[![处理器例子中，请求从处理器经 cache 和内存控制器到 DRAM，数据沿反方向返回。加速器例子中，DMA 发起读取和写入请求，数据从 DRAM 经控制器和片上互连到 scratchpad，再供计算单元使用。](../assets/ram-system-overview-mobile.svg?v=3ebd87e14804)](../assets/ram-system-overview.svg){.ram-overview-diagram-mobile}

图中虚线表示请求，实线表示数据的源和目的地。连线表示逻辑关系，不限定 DMA 的内部数据通路；点击图可查看大图。

### 路径 A：处理器读取，cache 未命中

处理器发出读取后，cache 根据地址查找数据。命中时，cache 可以直接返回所需数据；未命中时，请求继续发往下一级。在多级 cache 中，某一级 miss 可能由下一级 cache 满足。

下文采用一级 cache 的例子：所需数据不在 cache 中，内存控制器接收并调度读取，DRAM 返回数据，cache 填充后再响应处理器。

### 路径 B：DMA 将数据搬入 scratchpad

在另一个系统中，DMA 发起读取外存和写入 scratchpad 的请求。数据经过控制器与片上互连，进入 scratchpad。搬运完成且满足同步和可见性条件后，计算单元才能使用这批数据。

这里 DMA 负责发起和执行搬运，内存控制器负责调度 DRAM 访问；图中将请求与数据路径分开表示。其他系统也可以用计算线程或异步复制指令安排数据移动。例如，[CUDA 编程指南](https://docs.nvidia.com/cuda/archive/13.2.2/cuda-programming-guide/03-advanced/advanced-kernel-programming.html#asynchronous-data-copies)介绍了线程复制与异步复制到 shared memory 的方式。

## 3. 跟踪一次读取与后续复用 {#3-逐步看一次-cache-miss}

假设数组 `A` 的每个元素占 4 B，起始地址按 64 B 对齐；一级 cache 的 cache line 为 64 B。处理器顺序读取 `A[0]` 和 `A[1]`。

第一笔读取在 cache 中 miss，所需数据位于 DRAM。本例假设地址翻译已完成，cache 在完整填充该行后才响应；不考虑预取、其他请求、脏块写回和一致性交换，且该行在第二次读取前保持有效。

<!-- ram-overview-demo -->

各资源在这个例子中承担不同职责：

| 资源 | 接收什么 | 完成什么 |
| --- | --- | --- |
| 处理器 | 程序需要的地址与读取大小 | 发出对 `A[0]` 的读取；取得数据后提供给后续计算。 |
| Cache | 已翻译的地址和读取请求 | 查找数据；首次 miss 后请求包含 `A[0]` 的 cache line，并在数据返回后填充。 |
| 内存控制器 | 下游读取请求 | 根据地址映射、资源状态和时序条件安排 DRAM 访问。 |
| DRAM | 控制器发出的命令 | 按当前 bank 状态与协议条件服务读取，返回所需数据。 |

完整的 64 B cache line 回到 cache 后，处理器取得其中的 4 B `A[0]`。接下来读取 `A[1]`：它位于同一条仍有效的 cache line，因此可以在 cache 命中，不需要再次为这次读取访问 DRAM。

第一次跨层搬运带回了相邻数据，第二次读取使用了其中的一部分。这是**空间局部性**的一种利用方式。如果后续再读取仍然有效的 `A[0]`，则体现了对同一数据的时间复用。块大小、访问顺序和数据是否留在本地都会影响收益，详见[局部性与数据搬运](./01-system-basics/locality-working-set-data-movement.md)。

在常见的 load/store 模型中，读取结果可写入寄存器，或通过转发供执行单元使用。计算得到的结果可以继续留在寄存器或局部存储中，也可以由 store 更新 cache 或其他存储层；何时更新下层由系统策略决定。Scratchpad 路径同样需要安排计算结果的去向。

## 4. 怎样观察这条路径？ {#6-用同一边界比较延迟和带宽}

观察一次读取时，**延迟**描述请求从指定起点到指定终点花费的时间。例如，处理器发出读取到取得所需数据的时间。观察一段持续数据流时，**带宽**是指定接口上，在给定时间窗口内传输的数据量除以窗口长度。

统计带宽还要说明数据口径：接口传输的 payload 可能包含任务没有使用的字节；任务有效带宽只统计任务需要的字节。同一份流量按两种口径统计，结果可能不同。有关窗口、边界和损失的例子见[带宽与延迟](./03-performance/bandwidth-vs-latency-fundamental.md)和[峰值与有效带宽](./03-performance/effective-bandwidth-vs-peak.md)。

一笔 miss 的耗时也可能包含互连、控制器或共享通路的等待。多笔请求能否并发，以及它们落到哪些 bank，会影响持续供数。沿途检查请求和资源状态，有助于找到限制，详见[存储系统为何难设计](./01-system-basics/problem-statement.md)。

### 对建模有什么启示？ {#7-对建模有什么启示}

先确定模型要回答的问题，再选择需要保留的细节。描述数据路径时，至少要说明请求从哪里到哪里、经过哪些资源，以及在什么边界观察延迟或带宽；如果要解释争用，还要表示对应的共享资源和等待。

## 5. 接下来怎么读？ {#8-接下来怎么读}

本专题按四类问题组织文章：

- **系统基础**：从[存储系统为何难设计](./01-system-basics/problem-statement.md)、[RAM 分类与命名](./01-system-basics/taxonomy.md)和[存储层次与系统角色](./01-system-basics/memory-hierarchy-as-system.md)建立共同概念。
- **访问路径与数据管理**：阅读 [Cache 与 DRAM 协同](./02-access-paths/cache-dram-coordination.md)和 [Cache 与 scratchpad](./02-access-paths/cache-vs-scratchpad.md)，比较自动填充与显式放置。
- **性能分析与瓶颈**：用[带宽与延迟](./03-performance/bandwidth-vs-latency-fundamental.md)、[峰值与有效带宽](./03-performance/effective-bandwidth-vs-peak.md)分析路径表现。
- **NPU 数据路径案例**：从 [AI 芯片内存架构](./04-npu-case/README.md)进入，再按需查看局部 buffer 和片上带宽。

想深入一颗 SRAM 单元，可阅读 [6T SRAM cell](../02-sram/foundations/6t-cell-bistable-storage.md)；想研究 DRAM 访问，可转到 [DRAM 基础](../03-dram/foundations/README.md)和 [Memory Controller](../04-dram-controller/README.md)。原 RAM 章节的阅读路线见[学习路径与章节依赖](../reading-and-reference/01-reading/learning-roadmap.md)。
