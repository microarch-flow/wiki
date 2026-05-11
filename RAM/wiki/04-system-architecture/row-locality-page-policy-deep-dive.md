# Row Locality 与 Page Policy 深化

上级：[04 系统架构视角](./README.md)

相关：[DRAM 单元、Bank 与 Row Buffer](../02-memory-cells-arrays/dram-cell-bank-row-buffer.md)、[控制器、并行度与页策略](./controller-parallelism-page-policy.md)

## 为什么 row locality 这么关键

DRAM 的单次访问成本，经常不是卡在“总线跑得不够快”，而是卡在：

- 当前目标 row 是否已经打开
- 是否需要先关旧行再开新行

所以 row locality 往往是 DRAM 性能分析里的第一层问题。

## 三种常见情况

### Row Hit

目标访问落在当前已打开 row。

结果：

- 无需重新 activate
- 延迟最低
- 总线更容易被持续喂满

### Row Miss

目标访问所在的 bank 当前没有打开任何 row。

结果：

- 需要 `ACT -> READ/WRITE`
- 延迟上升

### Row Conflict

当前 bank 已经打开了另一个 row，而目标访问需要换到新 row。

结果：

- 先 precharge 旧行
- 再 activate 新行
- 再进行列访问

这通常是最伤性能的一类。

## 为什么 open-page 和 close-page 没有绝对优劣

### Open-page

思路是：

- 尽量保留当前打开 row
- 期待后续继续命中

适合：

- 后续访问经常回到同一 bank、同一 row
- 具有明显行局部性的 workload

风险是：

- 如果后续访问分散，旧行会变成负担

### Close-page

思路是：

- 更快关闭当前 row
- 为下一次不确定访问提前清场

适合：

- 随机访问
- 高并发、低局部性场景

风险是：

- 白白丢掉潜在 row hit 机会

## 行局部性与 bank 并行为什么常常互相拉扯

如果你极端追求 row locality，可能会倾向让访问聚集在少数 bank/row 上。

但如果你极端追求 bank-level parallelism，又可能把流量过度打散，破坏局部性。

所以控制器真正难的地方在于：

- 不是单独优化一个指标
- 而是同时平衡 row hit 与 bank 并行

## 架构研究里怎么用这个视角

分析一个 workload 时，优先看：

- 连续 cache line 是否常落在同一 row
- 多请求是否集中打到少数 hot bank
- open-page 带来的命中收益是否真的大于冲突代价

这类分析比单纯看峰值带宽更接近真实系统行为。

## 一句话理解

`DRAM 的很多真实性能差异，本质上都是在问：请求是在复用当前已打开的行，还是在不断支付换行代价。`
