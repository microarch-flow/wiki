# DRAM 命令与时序

上级：[03 DDR 协议与家族](./README.md)

相关：[DRAM 单元、Bank 与 Row Buffer](../02-memory-cells-arrays/dram-cell-bank-row-buffer.md)、[控制器、并行度与页策略](../04-system-architecture/controller-parallelism-page-policy.md)

## 为什么 DRAM 时序参数很多

DRAM 不是一个“发地址就立刻回数据”的简单设备。

它的内部动作要经历：

- 开行
- 感测
- 列读写
- 关行
- 刷新

所以 JEDEC 时序参数，本质上是在把这些内部物理动作暴露给控制器。

## 四个最基本命令

| 命令 | 作用 | 直觉理解 |
| --- | --- | --- |
| `ACT` | Activate 一行 | 打开目标货架 |
| `READ` | 从当前打开行读取列数据 | 从已打开货架取货 |
| `WRITE` | 向当前打开行写列数据 | 往已打开货架放货 |
| `PRE` | Precharge，关闭当前行 | 清空现场，准备开下一行 |

此外还有 `REF`，用于 refresh。

## 常见时序参数在约束什么

### `tRCD`

从 `ACT` 到 `READ/WRITE` 之间的最小等待时间。

直觉上，它对应“开行之后，row buffer 还需要一段时间才能稳定工作”。

### `CL / CAS Latency`

从发出读命令到数据开始返回的延迟。

它不是整个内存访问的全部延迟，而是读命令后的关键一段。

### `tRP`

precharge 所需时间。

它约束“旧行关闭、位线恢复”的过程需要多久。

### `tRAS`

一行从 activate 开始后，至少要保持开启多久。

它反映了行级操作不能无限压缩。

### `tRFC`

refresh 完成所需时间。

容量上升后，refresh 对可用带宽和尾延迟的影响会更加明显。

## Prefetch、Burst 与 Bank Group 先各指什么

- `prefetch`：一次访问时，DRAM 核心阵列先把更宽的一块数据搬到 I/O 缓冲区；这里不是指 CPU 的软件/硬件预取
- `burst`：一次 `READ/WRITE` 后，外部总线连续传出的多个 data beat
- `bank group`：把 bank 再分组；同组访问和跨组访问可能受不同的时序约束

## Prefetch 与 Burst 为什么重要

现代 DDR 接口并不是让核心阵列直接以外部 I/O 的速度工作，而是通过预取和 burst 来桥接两者。

直觉上：

- 内部阵列按自己的节奏准备更宽的数据块
- 外部 I/O 以更高传输速率把这块数据送出去

这样可以在不让核心阵列无限提频的情况下继续扩大外部带宽。

## 为什么 bank group 也很关键

随着速率提升，单纯增加外部传输次数并不够，还需要让不同 bank 间的访问冲突更可控。

bank group 的意义在于：

- 提升高频场景下的并行组织能力
- 区分“同组访问更紧”与“跨组访问更松”的时序关系
- 帮助控制器更有效地铺排请求

## 一句话理解

DRAM 时序不是记参数游戏，而是 `内部阵列物理动作 -> 外部命令接口` 的映射。
