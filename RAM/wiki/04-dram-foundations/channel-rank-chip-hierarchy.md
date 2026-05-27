# Channel、Rank、Chip：从引脚到 cell 的完整物理层级

上级：[DRAM 基础](./README.md)
相关：[Bank 为什么是 DRAM 并行性的最小单位](./bank-organization-parallelism.md), [Bank group、prefetch、burst：高频接口下的必然演化](./bank-group-prefetch-burst.md)

## 这页在回答什么问题

DRAM 从 memory controller 到最终的 cell，中间经过了 channel、rank、chip、bank group、bank、row、column 这一连串层级。这些层级各自隔离了什么、共享了什么，以及一个典型配置下每一层的数量级是多少。

## 正文

前面几页讨论的 row buffer、bank、bank group 都发生在单颗 DRAM chip 内部。但一颗 chip 的数据引脚宽度通常只有 x4、x8 或 x16，远不够填满系统需要的总线宽度。从 controller 到 cell 的完整路径上，还有 channel、rank 和 chip 这几个层级在单颗 chip 之外组织并行和复用关系。把这条完整的层级链理清楚，后面看地址映射、带宽计算和多通道调度时才不会混淆。

### Channel

Channel 是一条独立的数据总线，包含自己的命令/地址线和数据线。两个 channel 之间的命令和数据传输完全独立、互不阻塞。这是 DRAM 系统中最粗粒度的并行边界：跨 channel 的两笔访问不存在任何资源争用。

Channel 和 memory controller 的对应关系并不固定。最经典的配置是一个 controller 管一个 channel，比如桌面 CPU 的双通道就是两个独立 controller 各管一条 channel。但也存在一个 controller 内部管理多条 channel 的设计，常见于服务器和 AI 芯片——它们共享调度逻辑但数据通路独立。判断是否为独立 channel 的标准不在于 controller 数量，而在于命令和数据总线是否互不阻塞。

### Rank

Rank 是挂在同一 channel 上、通过 CS (chip select) 信号分时选中的一组 DRAM chip。同一 rank 内的所有 chip 共享命令/地址总线，收到同一条命令后同时响应，每颗 chip 各贡献数据总线的一部分。比如一个 64-bit 数据总线的 channel，可以由 8 颗 x8 chip 并联组成一个 rank，每颗 chip 贡献 8 bit。

不同 rank 之间分时复用同一条数据总线，同一时刻只有一个 rank 在驱动数据线。Rank 切换需要一小段空闲时间让总线电平稳定下来，这就是 rank-to-rank turnaround 的来源。增加 rank 数可以增加总容量和 bank 级并行度，但不增加峰值带宽，因为数据总线始终只有一条。

### Chip

单颗 DRAM chip 是一个完整的存储器件，内部包含 bank group、bank、row、column 的全部结构。chip 的数据引脚宽度（x4、x8、x16）决定了每次 burst beat 这颗 chip 贡献多少 bit。同一 rank 内多颗 chip 并联，拼出完整的总线宽度。

### 完整层级

把所有层级串起来，从上到下的关系是：

```text
System
  └── Channel          ← 独立总线，完全并行，互不阻塞
        └── Rank       ← 同一 channel 上分时复用，CS 选中
              └── Chip ← 并联拼总线宽度，每颗贡献 x4/x8/x16
                    └── Bank Group  ← 跨 group 访问间隔更短
                          └── Bank  ← 独立 row buffer，可各自打开不同 row
                                └── Row (wordline)
                                      └── Column
```

每一层隔离和共享的资源不同：

| 层级 | 隔离了什么 | 共享了什么 |
|------|-----------|-----------|
| Channel | 命令总线、数据总线、全部时序 | 无（完全独立） |
| Rank | bank 状态、row buffer 状态 | 命令/地址总线、数据总线（分时） |
| Chip | 内部阵列 | 命令/地址线（同 rank 内同时响应） |
| Bank Group | 部分内部数据通路 | 命令接口、I/O 边界逻辑 |
| Bank | row buffer、wordline 状态 | bank group 内部分通路 |

### 典型数量级

以一颗 DDR4 8Gb x8 chip 为例：

| 参数 | 典型值 |
|------|-------|
| Bank groups per chip | 4 |
| Banks per bank group | 4 |
| Banks per chip (总计) | 16 |
| Rows per bank | 65536 (2^16) |
| Columns per row | 1024 (2^10) |
| 每个 column 位置宽度 | 8 bit (x8 chip) |
| **一行数据量** | 1024 × 8 bit = 8 Kbit = **1 KB** |
| Row buffer 大小 | 1 KB（= 一行） |

一个 rank 由 8 颗这样的 x8 chip 并联组成，拼出 64-bit 数据总线。一次 ACT 命令会让 rank 内所有 chip 同时打开同一行号，但每颗 chip 各自打开的是自己阵列中的那一行。一次 BL8 burst 从每颗 chip 取出 8 × 8 bit = 64 bit，8 颗 chip 合计 512 bit = 64 Byte，恰好一条 cache line。

### 怎样用这张层级表

理解这张层级表最重要的不是记住每层有多少个，而是明确每层的并行性质：

- **Channel 间**：完全独立并行，加 channel 直接加带宽
- **Rank 间**：增加容量和 bank 并行度，但共享数据总线，不加峰值带宽
- **Bank group 间**：同一 channel/rank 内，跨 group 访问可以更紧密交错（tCCD_S < tCCD_L）
- **Bank 间**：各自独立的 row buffer 状态，可以流水线化隐藏 ACT/PRE 延迟
- **Row 间**：同一 bank 内切换 row 代价高（PRE + ACT），row hit 则几乎免费

后面看地址映射时，controller 把物理地址的不同 bit 段分配给 channel、rank、bank group、bank、row、column，本质上就是在决定"连续地址的访问落在这张层级表的哪一层展开并行"。

## 一句话理解

DRAM 的物理层级从外到内是 channel → rank → chip → bank group → bank → row → column，每一层隔离不同的资源、提供不同性质的并行，理解这张层级表是后续地址映射和带宽分析的前提。

## 建模启示

对建模来说，最小可用的层级参数集至少需要：

```text
DramHierarchy {
  channels: int
  ranks_per_channel: int
  bank_groups_per_rank: int
  banks_per_bank_group: int
  rows_per_bank: int
  cols_per_row: int
  device_width: int          // x4, x8, x16
  devices_per_rank: int      // = bus_width / device_width
  burst_length: int
}
```

从这组参数可以直接推导出：单次 burst 传输量 = `device_width × devices_per_rank × burst_length`，总容量 = `channels × ranks × banks × rows × cols × device_width`。如果模型要分析 bank-level parallelism 或 rank turnaround 的影响，就需要在调度逻辑中显式区分"同 bank group"和"跨 bank group"、"同 rank"和"跨 rank"的时序差异。
