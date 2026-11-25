# DRAM 地址映射：请求如何落到通道、bank 和行

上级：<span id="地址映射物理地址到-channelrankbankrowcol-的拆分艺术"></span>[DRAM 控制器与请求调度](./README.md)

相关：[控制器：从请求到响应](./why-mc-is-the-real-bottleneck.md) · [多通道与 NUMA](../01-memory-hierarchy/02-access-paths/numa-multi-channel-multi-socket.md) · [行缓冲](../03-dram/foundations/1t1c-cell-destructive-read.md#row-state)

## 这页在回答什么问题

物理地址怎样选择 channel、rank、bank group、bank、row 和 column？同一地址流经过不同映射，可能形成不同的行复用与并行机会。本页讨论控制器一侧的地址解释；操作系统的虚拟页到物理页映射另见[多通道与 NUMA](../01-memory-hierarchy/02-access-paths/numa-multi-channel-multi-socket.md)。

## 物理地址到 channel、rank、bank、row、col 的映射 {#地址位如何选择通道bank-和行}

输入是系统指定地址空间内的字节地址和访问大小。实现先处理地址范围及事务对齐，再选择资源和器件地址。最低位可能表示字节偏移，某些列位可能由 burst 隐含；各字段不一定连续，也可能通过 XOR 等函数组合。具体 channel 选择可以在控制器之外进行。

输出至少应能区分目标 channel、rank、bank group、bank、row、column 和 burst 内字节位置。完整的 bank 身份需要包含其上级资源：不同 rank 或 bank group 内的同号 bank 不是同一个 bank。[AMD 的 LPDDR 地址表](https://docs.amd.com/r/en-US/pg397-lpddrmc-ultrascale-mc/Address-Bit-Table?contentId=RblY29SRJecu~n9B65Q~sw)展示了一个具体实现中 bank group、列位与 burst 对齐的关系；它不是所有产品的固定切分。

### 用同一地址流比较两种映射

假设有 4 个 bank，每行有 8 个 cache-line 列。使用 line index `a`，访问 0—7；初始所有 bank 关行，按该顺序服务，且访问后保持行打开。以下只比较行状态，不计算具体时序或完成时间。byte offset 已在形成 line index 时去除。

X 倾向于将相邻 line 留在同一行；Y 更早在 bank 之间交错。

| 地址字段 | 映射 X | 映射 Y |
| --- | --- | --- |
| bank | `a[4:3]` | `a[1:0]` |
| 列 | `a[2:0]` | `a[4:2]` |
| 行 | `a[5:]` | `a[5:]` |

| 映射 | 0—7 的 bank 序列 | 行命中数 |
| --- | --- | --- |
| X | 0、0、0、0、0、0、0、0 | 7 |
| Y | 0、1、2、3、0、1、2、3 | 4 |

两种映射使用的地址位均被保留。在此序列中，所有目标行都是 0。X 第一次打开 bank 0，后续 7 次命中；Y 的四个 bank 各先打开一次，再各命中一次。Y 提供更多 bank 并行机会，但两种方案谁更快，还取决于请求到达时间、CA/DQ 共享和命令时序。

下一篇沿用映射 X。完成 0—7 后，bank 0 保留打开的 row 0。接下来访问 line 1 或 2 仍指向 bank 0、row 0；访问 line 32 则指向 bank 0、row 1。让这些请求在不同时刻到达，就可以分别观察[控制器先服务哪一笔](./command-scheduling-fr-fcfs.md#queue-choice)，以及在下一笔到达前[保留行还是预充](./command-scheduling-fr-fcfs.md#page-policy)。

### 映射需要满足什么条件？

在被映射的有效地址范围内，不同字节不能因错误的位丢失而意外别名。对使用 XOR 的方案，要检查变换后是否仍有足够信息区分所有受支持地址；地址窗口、保留区和不支持的区域还要按系统契约处理。并非所有映射都能仅用连续 `bit_range` 描述。

映射会影响控制器看到的热点与行局部性，但最终统计还受重排、关行和刷新影响。按相同请求流比较映射时，应记录每个 channel/bank 的请求量、命中或冲突的统计时点，以及队列等待；不要从连续地址直接断言一定命中同一行。

## 一句话理解

地址映射将字节请求分配到具体资源；行复用与并行机会都取决于映射和实际请求流。

## 建模启示

将地址范围、字节偏移、事务切分、channel/rank/bank group/bank/row/column 及可选哈希一起定义。比较结果时保持初始状态、请求顺序和策略一致，并明确地址变换的有效范围。
