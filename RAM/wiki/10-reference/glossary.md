# 术语表

上级：[参考资料](./README.md)
相关：[RAM 家族的分类与命名体系](../01-overview/taxonomy.md), [DRAM 协议层](../05-dram-protocol-families/README.md)

## 这页在回答什么问题

哪些术语需要统一口径，才能避免在不同章节里把同一个词说成不同层级的对象。

## 正文

这一页不是为了把所有出现过的名词堆成一本字典，而是为了统一边界。存储器讨论最常见的问题，不是完全不知道一个词，而是把几个本来不在同一层的词放到一起硬比。例如把 `SRAM` 和 `HBM` 当成同层对象，把 `cache` 和 `DDR` 放在一列里，把 `DIMM` 和 `LPDDR` 当成同类选项。这就像把"钢铁"（材料）、"桥梁"（结构）和"高速公路"（系统）放在同一张比较表里评谁更好——它们根本不在同一个维度上。这些混层一旦发生，后面的分析几乎一定会歪。

因此，这份术语表按“它属于哪一层”来组织，而不是按字母顺序排。你可以把它理解成一个快速纠偏工具：当某个词听起来熟，但你不确定它到底是在讲 cell、阵列、协议、系统角色还是封装形态时，先来这里对一下位置。

## 介质与 bitcell

`SRAM`

Static RAM。通常以 6T bitcell 实现，用更高每 bit 面积换稳定保持和更低局部访问代价。它首先是一种存储介质，不是某种具体系统角色；cache、register file、scratchpad、TCM 都可能用 SRAM 做。

`DRAM`

Dynamic RAM。通常以 1T1C bitcell 实现，用更高密度换来破坏性读出、refresh 和更复杂的访问状态机。它首先也是一种介质，不自动等于 DDR、HBM 或主存。

`6T cell`

经典 SRAM bitcell，由两个交叉耦合反相器和两个访问晶体管组成。它是稳定双稳态存储的基本实现，不等于整个 SRAM 阵列。

`1T1C cell`

经典 DRAM bitcell，由一个访问晶体管和一个电容组成。它存的是可泄漏电荷，不是稳定逻辑状态，所以必须依赖感测和 refresh。

`retention`

数据保持能力。在 SRAM 里通常指低电压下还能否保持状态；在 DRAM 里通常指电容电荷在必须 refresh 前能维持多久。

## 阵列与局部结构

`wordline (WL)`

字线。控制一行 bitcell 是否被选通。它负责“开门”，不直接承担远距离数据搬运。

`bitline (BL/BLB)`

位线。连接同一列多个单元的数据导线。在 SRAM 和 DRAM 里都重要，但角色不同：SRAM 中是差分读写通路，DRAM 中会和共享 sense amp 紧耦合。

`sense amplifier`

感测放大器。负责把很小的电压差放大成稳定逻辑值。SRAM 中它主要加速差分判决；DRAM 中它同时承担感测、恢复和 row buffer 的一部分角色。

`mat / sub-array`

SRAM 或 DRAM 阵列内部更小的可实现砖块。它们不是协议可见对象，而是决定布线长度、局部延迟和能耗的物理组织层次。

`bank`

可独立维护局部状态并提供一定并行度的阵列子块。对 SRAM 而言，bank 常是并发和局部带宽边界；对 DRAM 而言，bank 更是 controller 可见的调度与 open-row 状态边界。

`bank group`

DRAM 中对多个 bank 的进一步组织层。它通常出现在更高速 I/O 时代，用来约束不同 bank 之间的访问节奏。

`row buffer`

DRAM 中当前已打开一行在 sense amp 一侧形成的工作副本。它像 cache，是因为命中后后续访问更便宜；它又不像独立 cache，因为它并不是 tag+replace 管理的单独层。可以把它想成餐厅的备菜台——当前这桌客人点的菜已经摆在台上，再点同类的很快；但换桌客人点了完全不同的菜，备菜台就得全部清掉重新摆。

## 接口、协议与时序

`DDR`

有两层常见含义。狭义是 `Double Data Rate`，即一个时钟周期在上下两个边沿都传输数据；广义是 `DDR SDRAM` 这条主存产品路线。讨论时要分清是在讲传输机制，还是在讲一个协议家族。

`LPDDR`

Low Power DDR。面向移动和低功耗系统的 DRAM 路线，重点是待机功耗、I/O 能耗和近封装集成，不是“低频版 DDR”。

`GDDR`

Graphics DDR。面向图形和独立加速器显存的板级高带宽路线，核心是更激进的单 pin 速率和持续吞吐，不是“装在 GPU 上的普通 DDR”。

`HBM`

High Bandwidth Memory。它同时带有协议家族属性和强封装耦合属性：协议侧是宽 I/O DRAM 路线，系统侧通常依赖 stack + 2.5D/3D 集成。讨论 HBM 时最好明确你是在讲协议、stack，还是整个平台集成形态。

`prefetch`

在 DRAM 语境里，指 core array 一次准备更宽数据，再由外部 I/O 分多拍发出的桥接机制。这里不是 CPU 中“猜未来地址”的预取。

`burst`

一次 `READ` 或 `WRITE` 命令在总线上连续传出的多个数据 beat。burst 是 I/O 时间展开，不是额外缓存层。

`MT/s`

Mega Transfers per second。每秒百万次传输，常用于表示 DDR 类接口的数据传输速率。它不等于内部 core 时钟频率。

`ACT`

Activate。DRAM 打开某一行并把其内容感测到 row buffer。

`PRE`

Precharge。关闭当前打开行并把相关位线恢复到下一次激活前的初始状态。

`RD / WR`

Read / Write。DRAM 在已打开行上执行列访问的读写命令。

`REF / refresh`

为抵消 DRAM 电容漏电而周期性执行的数据保持操作。它是 DRAM 路线的基本税，不是可有可无的附加功能。

`tRCD / tCL / tRAS / tRP`

DRAM 常见时序参数。它们不是任意规格数字，而是开行、列访问、恢复和关行等物理等待窗口的接口化表达。

## 访问行为与 controller 术语

`row hit`

请求目标行正好是该 bank 当前已打开行，因此可直接在现有 row buffer 上做列访问。

`row miss`

目标 bank 当前没有打开任何行，因此通常需要先 `ACT` 再 `RD/WR`。

`row conflict`

目标 bank 当前打开的是另一行，因此通常需要先 `PRE` 当前行，再 `ACT` 新行，再做访问。

`row locality`

请求流连续复用同一已打开行的能力。它是 DRAM 有效带宽、page policy 和调度收益的核心来源之一。

`page policy`

memory controller 在一次访问后是否保留当前 open row 的策略。它不是页面管理，而是对未来 row locality 的下注。

`open-page`

倾向保留当前打开行，期待后续继续命中它。

`close-page`

倾向尽快关闭当前行，减少未来切换到别的 row 时的冲突成本。

`FR-FCFS`

First-Ready First-Come-First-Serve。常见 DRAM 调度策略，优先服务 timing-legal 且通常更偏 row-hit 的请求，再在同类候选中考虑先来先服务。

`write drain`

controller 集中处理一批写请求的阶段，主要为了减少总线读写方向切换带来的成本。

`QoS`

Quality of Service。共享内存系统中，为吞吐、延迟、公平性或隔离需求设定的服务质量策略，不限于某一种调度算法。

## 系统角色与资源语义

`register file`

贴近执行管线、强调同拍多读多写和严格语义的本地存储。它通常用 SRAM 类结构实现，但系统角色远比普通 SRAM 严苛。

`cache`

硬件管理局部性的存储层。它的本质不是用了 SRAM，而是通过 tag、替换和 refill 把平均访问代价压低。

`scratchpad`

软件或编译器显式管理的本地存储，通常不依赖自动替换。它和 cache 可能都由 SRAM 实现，但资源语义完全不同。

`TCM`

Tightly Coupled Memory。强调确定性和低抖动的本地存储，常见于 MCU 或实时系统。它更像 deterministic scratchpad，而不是简化版 cache。

`weight buffer / activation buffer / accumulator buffer`

NPU 中按数据角色划分的片上 SRAM 资源。它们共享同一种介质，但在生命周期、读写方向、局部带宽模式和建模语义上不同。

`double buffering`

通过两个或多组槽位把“当前消费”和“下一块填充”重叠起来的组织方式。它的价值来自时间重叠，不来自简单地把容量翻倍。

`memory hierarchy`

系统中不同距离、不同带宽、不同容量、不同共享语义的存储层集合。它不是一个静态金字塔图，而更像多层资源网络。

`NUMA`

Non-Uniform Memory Access。不同处理单元到不同内存资源的访问代价不一致的系统组织，不只是“多 socket”同义词。

## 通道、模块与封装形态

`channel`

memory controller 与 DRAM 设备之间的一条相对独立的数据与命令通路。它是带宽扩展的重要边界，但并不消除更内部的 bank 或 row 状态约束。

`rank`

在 DRAM 模块或子系统中，共享某些通道资源的一组设备组织。它常用于容量扩展和时序组织，但不是 DRAM die 内部结构。

`DIMM / SODIMM`

传统可插拔内存模块形态。它们描述的是系统集成方式，不是 DRAM 介质种类。

`PoP`

Package on Package。移动系统中把内存与主芯片以更近封装方式叠接的集成形态，常与 LPDDR 路线配套。

`MCP`

Multi-Chip Package。把多个 die 或芯片组合进一个封装中的通用术语，语义比 PoP 更宽。

`TSV`

Through-Silicon Via。穿硅通孔，用于 die 垂直互连，是 HBM stack 等 3D 集成的重要基础。

`interposer`

2.5D 集成里位于多个 die 之间的高密度中介层。它提供短距高密度互连，不等于主动计算 die。

`2.5D`

多个 die 并排放在中介层或类似高密度载体上，通过短距互连连接的集成方式。

`3D`

die 在垂直方向直接堆叠形成更高集成密度的组织方式。它可以指 memory stack，也可以指更广义的 3D 集成。

`logic die / base die`

HBM stack 底部承接电源、信号和部分控制逻辑的 die。它不是“额外一层 DRAM 容量”。

`CXL`

一种把更远的扩展内存、共享内存设备或加速器内存语义化接入系统的互连接口路线。它不是封装技术，也不会把远端内存物理上变近。

## 常用度量

`bandwidth`

单位时间可传输的数据量。讨论时要说明是理论峰值、持续可用值，还是某条具体链路的局部能力。

`latency`

从发起到首个有效结果返回所经历的时间。它和带宽相关，但不是同一件事。

`capacity`

可存储的数据总量。容量大不自动等于访问代价低。

`pJ/bit`

每传输 1 bit 数据的大致能量代价，常用于比较不同 I/O 或不同集成方式的能效。

`working set`

在某个时间窗口内真正需要高效访问的那部分数据集合。它比“模型总大小”更能决定局部 buffer 是否有价值。

## 一句话理解

存储器术语最重要的不是记住定义，而是先分清它是在讲介质、阵列、协议、控制、系统角色还是封装形态。

## 建模启示

术语混层的最大风险，是把本来属于不同抽象层的对象塞进同一模型维度，最后得出没有意义的比较。例如，把 `HBM`、`cache`、`DIMM`、`SRAM` 当成四个同类选项，会让模型同时混进介质、系统角色和封装形态。

更稳的做法，是在模型里先给术语归类：

```text
TermCategory = enum {
  medium,
  array_structure,
  protocol_timing,
  controller_policy,
  system_role,
  packaging_integration,
  metric
}
```

只要某个比较对象不在同一 `TermCategory`，就应该先追问“是不是少了一层中间抽象”，而不是直接比较它们谁更好。
