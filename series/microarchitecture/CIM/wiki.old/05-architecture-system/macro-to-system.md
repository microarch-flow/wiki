# 从 Macro 到 Chip

## 为什么这一页必须单独讲

`CIM` 里最常见的误判之一，就是把 `macro-level` 的强结果直接外推成 `chip-level` 或 `system-level` 优势。

但现实通常是：

- 宏本身很强
- 拼成 tile 后开始出现 buffer 与归约成本
- 做成 chip 后互联、控制和利用率问题暴露
- 接到真实系统后，host、DRAM 和软件协同进一步吃掉收益

因此，这一页的核心不是重复“宏很重要”，而是解释：

1. 为什么收益会在层级放大过程中失真
2. 哪些新增组件会逐层吞掉收益
3. 什么时候 macro 指标仍然有意义，什么时候已经失去判断价值

## 一条更实际的层级链

可以把系统拆成五层：

1. `cell`
2. `macro`
3. `tile`
4. `chip`
5. `board / system`

每升一级，不只是规模变大，而是新增了一批之前不存在的约束。

## 1. Cell-level

### 这一层在证明什么

这一层通常在证明：

- bitcell 或 device 是否支持局部计算
- 基本读写路径和计算路径是否兼容
- 某种物理机制是否成立

### 这一层最容易高估的地方

在 `cell-level`，很多问题还没有真正出现：

- 大阵列误差累积
- 多宏协同
- 数据搬运
- 控制路径

因此，`cell-level` 结果更适合证明原理，而不适合直接推导系统价值。

## 2. Macro-level

### 这一层在证明什么

这是大多数 `CIM` 论文的核心展示层。

它通常在证明：

- 一个阵列或宏能完成某类计算
- 局部能耗、面积、吞吐有吸引力
- 外围电路与阵列在一个有限范围内能闭环

### 为什么这一级最容易“看起来很强”

因为在这一层：

- 数据路径最短
- 调度最简单
- 互联开销最小
- 控制逻辑最轻

这使得 `TOPS/W`、area efficiency 等指标最容易显得好看。

### 这一级最常见的遗漏

- `ADC / DAC` 是否算全
- buffer 是否只算了局部最小配置
- 输入输出是否假设理想供给
- 结果是否只针对单个 kernel

## 3. Tile-level

### 为什么 tile 是第一个真实分水岭

一旦多个 macro 被拼成 tile，系统问题就开始真正出现。

这时必须新增：

- local buffer / scratchpad
- tile controller
- macro 间互联
- partial sum 合并路径

### 这一层最常见的损耗来源

- 宏与宏之间的数据搬运
- 本地归约成本
- buffer 读写能耗
- controller 与时序开销

### 为什么很多设计在这里开始掉速

因为宏级高并行度不等于 tile 级高利用率。

常见原因包括：

- 切块后碎片增多
- 不同宏负载不均衡
- partial sum 需要跨宏合并
- 输入与权重供给不能持续跟上

## 4. Chip-level

### 这一层新增了什么

从 tile 到 chip，新增的不是“更多 tile”这么简单，而是：

- 片上 `NoC`
- 全局 buffer / memory hierarchy
- 全局调度和同步
- host interface
- 电源、时钟、热设计约束

### 这一层最常见的失真来源

- `NoC` 成本上升
- 全局归约路径变长
- DRAM / off-chip access 重新成为瓶颈
- 热和功耗约束限制峰值并发
- 软件栈只能支撑部分 workload

### 一个关键现实

很多宏论文默认：

- 输入持续可得
- 权重稳定驻留
- 结果可以理想输出

但在 chip 里，这三件事都必须被真实系统资源支撑，否则峰值指标没有意义。

## 5. Board / System-level

### 到了系统层，问题彻底换了

系统层关心的已经不再只是阵列效率，而是：

- host 与 accelerator 如何协同
- 板级带宽是否足够
- 软件栈是否能自动部署
- 客户 workload 是否真能受益

### 这一层常见的新增损耗

- host 同步开销
- 板级接口延迟
- 外部 DRAM / HBM 访问
- 驱动与 runtime 开销
- 部署环境中的利用率下降

### 为什么 system-level 才是真正的商业判断层

因为客户最终购买的不是 `macro efficiency`，而是：

- token latency
- end-to-end throughput
- energy per task
- 部署摩擦

也就是“这套系统放进真实业务里值不值”。

## 一条最常见的收益衰减链

很多 `CIM` 方案都会经历类似路径：

1. `macro` 显示出很高局部能效
2. `tile` 开始引入 buffer 与归约成本
3. `chip` 开始受 `NoC`、全局存储和利用率限制
4. `system` 再被 host 协同、软件和外部内存拖慢

因此，真正的问题通常不是“宏有没有收益”，而是：

> 宏的收益在升到 system 时还能剩下多少？

## 每升一级，哪些组件在新增

| 层级 | 主要新增组件 | 最常见新增成本 |
| --- | --- | --- |
| `cell -> macro` | 外围读写、ADC/DAC/SA | 转换与读出成本 |
| `macro -> tile` | local buffer、controller、局部互联 | buffer 与归约成本 |
| `tile -> chip` | NoC、全局 buffer、同步逻辑 | 通信、利用率、热约束 |
| `chip -> system` | host interface、board、runtime、外部内存 | 同步、接口、部署开销 |

## 什么时候 macro 指标仍然有价值

`macro-level` 指标并不是没用，而是要放在正确场景下看。

它更有价值的时候是：

- 比较同一路线内部不同宏设计
- 判断某个电路机制是否值得继续
- 估算理论上限

它价值明显下降的时候是：

- 直接横比不同系统路线
- 用来推断端到端部署收益
- 用来判断商业竞争力

## 分路线看，失真链并不一样

## SRAM-CIM / Digital CIM

更常见的问题是：

- 宏本身比较工程友好
- 但容量有限
- 到 chip 级时容易被 buffer / interconnect / area 约束吃掉收益

也就是说，它更容易走到 chip，但不一定更容易在大系统上体现极端优势。

## ReRAM / Analog CIM

更常见的问题是：

- macro 看起来极具吸引力
- 但一升到 tile / chip，误差、ADC、校准和系统配套迅速变重

所以它的失真往往更早发生，而且更剧烈。

## DRAM / HBM-PIM

这类路线不一定在 macro 上最惊艳，但它从一开始就是 system-oriented。

因此更该看：

- memory-side 到 system 的整体路径
- host 往返是否真的减少
- package / interface 是否支持目标收益

它的问题通常不是“宏衰减成系统”，而是“系统收益是否足够覆盖集成复杂度”。

## 一个实用的分析套路

当你看到一个很强的 `macro` 结果时，可以顺着下面的问题链走：

1. 这个结果目前停留在哪个层级？
2. 升一级会新增哪些组件？
3. 哪些成本还没算进去？
4. 利用率在下一级会下降多少？
5. 最终 bottleneck 会转移到 `ADC`、buffer、`NoC`、DRAM 还是 host？

## 读论文时建议额外记录的字段

- 指标层级：`macro / tile / chip / system`
- macro 数量
- tile 组成
- partial sum 合并位置
- local / global buffer 配置
- 是否包含 `NoC`
- host interface 形态
- 是否来自仿真、post-layout 还是 silicon

## 一个最实用的判断原则

如果一个方案：

- 只展示宏指标
- 没有清楚说明 tile 和 chip 结构
- 没有解释 buffer、controller、NoC 和 host 接口成本

那么它最多证明“宏可能值得研究”，还没有证明“系统收益真实成立”。

反过来，如果一个方案已经能说明：

- 宏如何组成 tile
- tile 如何组成 chip
- 哪些成本在上升
- 为什么端到端收益仍然保得住

那么它才更接近真正有系统意义的路线。

## 与本章其他页面的关系

- [数据流与算子映射](./dataflow-mapping.md)：更关注 workload 如何切到 array / tile
- [互联、归约与存储层次](./interconnect-reduction.md)：更关注通信和归约路径
- [性能与能耗模型](./performance-energy-model.md)：更关注统一能耗拆解模型

本页重点放在：

- 层级放大时的收益失真
- 不同层级新增的系统成本
- `macro` 指标如何正确解读

## 后续可补充内容

- `macro -> tile -> chip -> system` 框图
- 不同路线的失真链案例
- 指标折算示意
