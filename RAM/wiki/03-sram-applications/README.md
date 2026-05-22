# SRAM 应用形态

上级：[`RAM/wiki/`](../)
相关：[SRAM 基础](../02-sram-foundations/README.md), [系统视角](../07-system-architecture/README.md)

## 这页在回答什么问题

同样都建立在 SRAM 之上，为什么 register file、cache、scratchpad、TCM 和 NPU buffer 会长成完全不同的系统对象。这一章要回答的不是“它们都用 SRAM 做”，而是“底层约束相同的情况下，上层为什么会演化出不同的管理语义、端口组织和数据流角色”。

## 正文

上一章把 SRAM 作为物理与阵列基础讲完后，一个很自然的下一问是：如果底层都是 6T cell、字线位线、bank 切分和 retention 约束，为什么系统里还会出现这么多名字不同、接口不同、成本结构也不同的“片上存储”？答案是，SRAM 只决定了底层介质的大方向，却没有决定上层到底要把这块介质当成什么资源使用。系统真正关心的，往往不是“这是不是 SRAM”，而是“谁来决定里面放什么、什么时候访问、并发语义多强、是否允许不确定命中、是否接受冲突、恢复代价多大”。

这一章的任务，就是把这些不同应用形态的分叉点讲清楚。`register-file-as-sram.md` 会先处理最极端的一类：它和普通 SRAM 同根，但为了同拍多读多写，被迫接受极端的多端口代价，因此成为“最贵的一类 SRAM”。`cache-sram-tag-data-arrays.md` 处理的是另一条路线：底层仍是 SRAM，但上层引入 tag、比较、替换和命中不确定性，于是问题不再只是存储，而是“如何让硬件透明地赌数据局部性”。`scratchpad-vs-cache.md` 则把同样是片上 SRAM 的两种截然不同管理哲学正面对比出来：一个让硬件猜，一个让软件显式管。

后面的 `npu-weight-buffer-activation-buffer.md` 和 `tcm-itcm-dtcm-in-mcu.md` 则是把 SRAM 的应用进一步推向特定系统场景。NPU buffer 关心的是数据流角色、bank 并发和搬运调度，不会满足于一个笼统的“local SRAM”标签；MCU 里的 TCM 则把确定性压到比平均命中率更高的位置，所以它虽然也是 SRAM，却故意不走 cache 路线。这两篇的意义在于提醒你：应用形态不是在给同一件东西换名字，而是在表达系统把 SRAM 纳入整体架构时，优先保留了哪一组性质。

这也是为什么本章必须放在 SRAM 基础之后、DRAM 主线之前。放在前面，你会很容易把 register file、cache、scratchpad 看成几个独立名词，而不知道它们背后其实是在争夺同一组底层资源约束：端口数、bank 数、访问确定性、局部容量、唤醒粒度和软件可控性。放在 DRAM 之后又会模糊重点，因为本章真正要建立的是“同一物理介质的多种系统语义”，不是“不同物理介质的系统比较”。只有先把 SRAM 基础立住，再来看这些形态，很多系统差异才会显得是必然，而不是风格偏好。

读这一章时，有一个特别有用的判断框架：每遇到一种 SRAM 形态，先问四个问题。第一，谁负责决定里面放什么，是硬件、软件、编译器还是固定流水？第二，并发访问需求来自哪里，是多源操作数、命中查找、DMA 搬运还是多 tile 同时取数？第三，冲突和 miss 能不能接受，还是必须给出确定性服务？第四，数据生命周期有多长，是否值得做 retention、复制、双缓冲或预取。很多看似属于“架构风格”的分歧，顺着这四个问题往下推，最后都会回到前一章讲过的 SRAM 物理与阵列约束。

从建模角度看，这一章也标志着一个重要转变。到这里为止，SRAM 不再只是一个 `capacity + latency + bank_count` 的底层对象，而开始被包装成不同的系统资源类型：有的更像多端口操作数仓库，有的更像概率命中的透明层，有的更像确定性本地存储，有的更像为某种数据流量身定制的局部 buffer。也就是说，同样的 SRAM 物理原型，会在这里分裂成不同的使用语义模型。后面进入 `07-system-architecture/` 时，系统性能差异很多时候正是从这些语义差异，而不是从 bitcell 差异开始放大的。

## 一句话理解

这一章要讲清的不是“哪些东西用 SRAM 做”，而是“同样的 SRAM 介质在不同系统目标下，会被包装成完全不同的资源语义和并发语义”。

## 建模启示

本章对应的核心建模动作，是把统一的 `SramArrayModel` 进一步实例化成几类不同的系统资源，而不是继续把所有片上 SRAM 都视为同一种模块。至少应该区分 `operand_storage`、`hardware_managed_cache`、`software_managed_scratchpad`、`deterministic_tcm`、`stream_buffer` 这几类角色，因为它们对冲突、命中、并发和生命周期的解释完全不同。

一个适合作为后续各页公用入口的抽象草图可以是：

```text
SramBackedResource {
  storage_impl: SramArrayModel
  role: enum { REGFILE, CACHE, SCRATCHPAD, TCM, STREAM_BUFFER }
  allocation_policy: enum { FIXED, HW_MANAGED, SW_MANAGED, DMA_SCHEDULED }
  miss_semantics: enum { NONE, STALL, REFILL, SOFTWARE_VISIBLE }
  concurrency_semantics: enum { MULTI_PORT, BANKED, PIPELINED, DETERMINISTIC }
}
```

如果只关心底层时延，本章的语义层可以先忽略；但只要进入系统吞吐、编程模型或 AI 数据流分析，这些字段就必须显式存在。因为很多“同样容量的 SRAM 为什么效果完全不同”的问题，答案根本不在物理层，而在资源语义层。
