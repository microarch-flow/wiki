# DRAM 基础

上级：[`RAM/wiki/`](../)
相关：[SRAM 基础](../02-sram-foundations/README.md), [DRAM 协议层](../05-dram-protocol-families/README.md)

## 这页在回答什么问题

如果 SRAM 章节建立的是“局部、稳定、可直接访问”的 RAM 直觉，那么这一章要回答的就是：当存储目标从低延迟转向高密度之后，RAM 为什么会被迫长成完全不同的工程对象。这里要建立的不是几个 DRAM 名词，而是一条从 1T1C 单元一路推到 row buffer、bank 和高频接口演化的因果链。

## 正文

把 DRAM 学成一组协议术语，是最常见也最可惜的路径。你当然可以背下 `ACT / RD / PRE`、`tRCD / tRP / tRAS`、`bank / row / burst` 这些名词，但如果不知道它们在为哪一层物理约束付账，后面做系统判断时就会把很多限制误看成“历史包袱”或“标准细节”。这一章的任务，就是先在协议之前，把 DRAM 的物理和阵列逻辑重新搭起来。

它和 SRAM 的差别，要从最底层的存储方式开始看。SRAM 用双稳态电路把一个 bit 保存在持续再生的局部状态里，因此读取时主要是在小心地观测一个已稳定存在的节点。DRAM 走的是另一条完全不同的路线：用一颗访问晶体管加一颗电容，把一个 bit 存成非常有限的一点电荷。这个选择换来了极高密度，但也立刻引入一串连锁反应。电荷会漏，所以必须 refresh；读取时电荷极弱，所以必须放大；放大的过程会扰动原始状态，所以读出天然带有破坏性；单个 cell 的信号太小，不可能像 SRAM 那样直接做细粒度本地访问，于是必须先把整行接到 sense amp 上，再进行列访问。后面的复杂性都不是附加功能，而是这条物理路线的必然展开。

因此，本章的结构本身就是一条递进链。`1t1c-cell-destructive-read.md` 先解释为什么”一颗电容”会把问题性质彻底改掉。`refresh-the-fundamental-cost.md` 接着说明 refresh 不是维护动作，而是 DRAM 的原罪。`row-column-decode-sense-amplify.md` 再回答为什么 DRAM 访问必须先开行，而不能像 SRAM 那样把单个地址直接读出来。到 `row-buffer-as-cache.md` 和 `bank-organization-parallelism.md` 时，问题会从”单次访问为什么复杂”进一步变成”系统怎样利用这种复杂结构去换取吞吐”。`channel-rank-chip-hierarchy.md` 把视角从单颗 chip 内部扩展到完整的系统层级，理清 channel、rank、chip、bank group、bank、row、column 之间的隔离与共享关系。最后的 `bank-group-prefetch-burst.md` 和 `dram-process-stacking-trends.md` 则把你带到更靠近协议和产品路线的边界，解释为什么高频接口、宽总线和堆叠工艺会自然出现。

这一章还有一个很重要的边界条件：它讨论的是 DRAM 的“器件与阵列主线”，暂时不把重点放在 JEDEC 命令、时序参数和控制器调度上。那些内容会在 `05-dram-protocol-families/` 和 `06-memory-controller/` 里系统展开。本章要先做的，是让你形成一个牢固直觉：DRAM 的命令式接口不是平白无故设计出来的，而是 cell 太弱、访问必须成行、刷新必须持续发生、bank 必须被作为独立并行单元管理之后，系统被迫看见的结果。

和前面的 SRAM 章节相比，这一章的学习重点会明显转向”上下文相关成本”。SRAM 的访问更像固定票价的地铁——无论几点坐、从哪站上，票价基本一样。DRAM 则更像打车——同一段路程，早高峰可能堵 40 分钟，深夜可能 10 分钟就到，甚至同一时刻你选了一辆正在另一个方向的车也会多等很久。某次访问是不是 row hit、所在 bank 是否忙、refresh 是否临近、同一通道上是否还有别的请求，这些条件都会改变真实代价。因此理解 DRAM 时，不要只问”它一次访问多慢”，而要问”在什么上下文里，它会快、会慢、会冲突、会被刷新打断”。

这一章也会为后面的系统层判断打一个非常关键的底子：DRAM 不是“更慢的大内存”这么简单，而是一种要求工作负载、控制器和地址映射共同配合的存储介质。你之后看到的 row locality、page policy、FR-FCFS、effective bandwidth、HBM 宽接口，都会反复回到这里的几条基础逻辑：cell 很弱、整行感测、bank 并行、接口要桥接 cell 速度与 I/O 速度的剪刀差。如果这些基础逻辑先立住，后面的协议和系统内容就会自然连起来。

## 阅读顺序

建议按下面顺序阅读本目录：

1. [1T1C cell——一颗电容为什么改变了一切](./1t1c-cell-destructive-read.md)
2. [刷新：DRAM 的原罪和它的代价](./refresh-the-fundamental-cost.md)
3. [行列解码与读出放大：为什么 DRAM 必须“先开行”](./row-column-decode-sense-amplify.md)
4. [Row buffer：DRAM 内部的小 cache](./row-buffer-as-cache.md)
5. [Bank 为什么是 DRAM 并行性的最小单位](./bank-organization-parallelism.md)
6. [Channel、Rank、Chip：从引脚到 cell 的完整物理层级](./channel-rank-chip-hierarchy.md)
7. [Bank group、prefetch、burst：高频接口下的必然演化](./bank-group-prefetch-burst.md)
8. [DRAM 工艺路线：平面 -> 堆叠 -> 3D](./dram-process-stacking-trends.md)

如果你这次只想补”为什么 DRAM 会暴露出 ACT/RD/PRE 这种命令式接口”的直觉，优先看 1 -> 5。第一次系统阅读，建议完整按 1 -> 8 顺序走。

## 一句话理解

本章要建立的，是 DRAM 从 1T1C 单元到 row buffer、bank 和高频接口演化的因果链：它的复杂性不是后来加上去的，而是高密度存储从一开始就欠下的债。

## 建模启示

对建模来说，这一章标志着一个重要转折：从这里开始，存储资源不能再被视为“近固定延迟的本地数组”，而必须被视为带显式内部状态的阵列系统。哪怕暂时不进到协议层，后续模型也至少需要显式保留 `row_open_state`、`bank_busy_state`、`refresh_state` 这类变量的雏形，因为这些状态正是从本章的物理与阵列约束里长出来的。

一个适合作为后续 DRAM 章节底座的抽象草图可以是：

```text
DramArrayModel {
  channels: int
  banks_per_channel: int
  rows_per_bank: int
  cols_per_row: int
  open_row[channel][bank]: row_id | INVALID
  bank_busy_until[channel][bank]: cycle
  next_refresh_deadline[channel][bank_or_rank]: cycle
}
```

如果只关心非常粗粒度的系统性能，你可以先不显式模拟 sense amp、电荷恢复或 prefetch 深度；但从本章开始，至少要接受一个前提：DRAM 的服务时间取决于访问上下文，而不是单一常数。这也是为什么后面的协议、控制器和系统章节，都会在这个状态模型之上继续加层。
