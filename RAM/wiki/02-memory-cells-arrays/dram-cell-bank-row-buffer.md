# DRAM 单元、Bank 与 Row Buffer

上级：[02 存储单元与阵列结构](./README.md)

相关：[DRAM 命令与时序](../03-ddr-protocol-families/dram-commands-timing.md)、[控制器、并行度与页策略](../04-system-architecture/controller-parallelism-page-policy.md)

## DRAM 单元是什么

DRAM 的基本存储单元通常可以概括为 `1T1C`：

- `1 个晶体管` 作为访问开关
- `1 个电容` 存储电荷

直觉上：

- 有足够电荷，可视为 `1`
- 没有或接近没有电荷，可视为 `0`

这也是 DRAM 能做出高密度、大容量、较低每 bit 成本的根本原因。

## 为什么 DRAM 需要刷新

电容会漏电，因此数据不能一直稳定保存。

这意味着：

- DRAM 必须周期性 refresh
- refresh 会占用阵列资源
- refresh 不是实现细节，而是 DRAM 体系的一部分

所以 DRAM 的容量优势，是用刷新开销和更复杂的控制换来的。

## DRAM 不是逐 bit 直接访问

DRAM 的关键特征不是“随机访问很慢”，而是它的访问方式是分层的：

- 阵列被划分成多个 `bank`
- 每个 bank 里有很多 `row`
- 每一行里有很多 `column`

一次典型访问不是直接从一个 bit 读出，而是：

1. `ACT`：先打开目标 row
2. 把整行内容感测到 `sense amplifier / row buffer`
3. `READ / WRITE`：从这行里按列读写
4. 如果后续要切到别的 row，才执行 `PRE`：关闭该行，为下一次行切换做准备

## Row Buffer 为什么重要

Row buffer 可以看成 DRAM bank 的“当前工作行”。

如果下一个访问仍然落在当前打开的行：

- 属于 `row hit`
- 不需要重新激活
- 延迟更低

如果下一个访问不再落在当前打开的行，需要先区分两种情况：

- `row miss`：当前 bank 没有打开任何行，需要 `ACT -> READ/WRITE`
- `row conflict`：当前 bank 打开的是别的行，需要 `PRE -> ACT -> READ/WRITE`

第二种情况通常代价更高。

这就是为什么 DRAM 的实际性能，不只是看接口峰值，还强烈依赖访问局部性。

## Bank 并行的意义

一个 bank 同一时刻只能维持有限的操作节奏，但多个 bank 可以并行工作。

所以 DRAM 提升有效吞吐并不只是靠频率，还靠：

- 增加 bank 数量
- 改进 bank group
- 让控制器把请求分散到不同 bank

从系统角度看，bank 就是 DRAM 的核心并行资源之一。

## DRAM 电路层面的几个难点

- 电容越小，感测越困难
- 漏电越明显，刷新压力越大
- 感测放大器要在速度、功耗、稳定性之间平衡
- 阵列越大，位线和字线的 RC 延迟越难处理

所以 DRAM 的“便宜和大”，不是没有代价，而是把困难集中到了阵列、电路和控制器协同上。

## 一句话理解

DRAM 的本质不是“慢内存”，而是 `高密度存储阵列 + 行缓冲访问模型 + 需要刷新` 的工程折中体。
