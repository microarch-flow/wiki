# DRAM 刷新：保持数据的条件与资源占用

上级：<span id="刷新dram-的原罪和它的代价"></span>[DRAM 单元与阵列](./README.md)

相关：[1T1C 单元](./1t1c-cell-destructive-read.md) · [DRAM 可靠性](./dram-reliability-retention-rowhammer-ecc.md) · [控制器刷新调度](../../04-dram-controller/refresh-management-distributed-postponed.md)

## 刷新：DRAM 的原罪和它的代价？ {#这页在回答什么问题}

电荷泄漏之后，器件怎样保持尚未被访问的数据？刷新需要占用哪些资源？旧标题将它称为“DRAM 的原罪和它的代价”；工程上需要具体区分保持要求和实际服务损失。

## 电荷泄漏与刷新占用

在规定的工作条件下，刷新对所覆盖单元进行感测和恢复。外部发起的 refresh 命令由器件按相应模式执行；self-refresh 则由器件在受支持的低功耗状态中维护数据，进入、退出和外部时钟要求依产品定义。普通访问对被激活行的恢复并不保证覆盖所有行。

几个容易混淆的时间量：

- `tREFW` 是目标模式规定的刷新窗口；常见的 64 ms 不能套用到所有温度或配置。
- `tREFI` 是该模式下的平均刷新命令间隔；允许推迟或提前的数量以及最终期限依器件和模式而定。
- `tRFC` 是一条对应刷新操作的恢复时间；其受影响范围要看 all-bank、same-bank 等具体命令。

以 [Micron DDR5 技术说明](https://tw.micron.com/content/dam/micron/global/public/products/white-paper/ddr5-new-features-white-paper.pdf)中所列 16 Gb 器件和普通 all-bank 刷新为例，`tREFI = 3.9 μs`、`tRFC = 295 ns`。按固定间隔连续发出时，`295 / 3900 ≈ 7.6%` 是受刷新影响的 rank 名义占用比例；这不是系统有效带宽必然下降 7.6% 的测量值，调度、其他 rank、请求队列及空闲时间都会改变观察结果。

该资料也描述 DDR5 的 same-bank refresh：它涉及各 bank group 中相同编号的 bank，而不是整个 rank 只有一个 bank。其他 bank 的访问还受适用的命令和时序约束。温度、刷新模式与器件密度变化时应重新查表。

## 一句话理解

刷新维持未访问数据，但其覆盖范围、频率和占用都由目标器件的模式决定。

## 建模启示

记录刷新作用域、到期规则、恢复时间和请求竞争。比较调度策略时分别报告名义占用、请求等待和有效带宽；不要把 `tRFC / tREFI` 直接当成实测性能损失。
