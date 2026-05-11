# 内存控制器建模与性能分析

上级：[04 系统架构视角](./README.md)

相关：[地址映射与层级结构](./channel-rank-bank-address-mapping.md)、[控制器、并行度与页策略](./controller-parallelism-page-policy.md)

## 为什么要单独建模内存控制器

如果只看 DRAM 颗粒规格，你能知道理论上限；但你仍然不知道：

- 实际请求会如何排队
- bank 冲突有多严重
- refresh 会怎样打断关键路径
- read/write 切换会损失多少吞吐

这些问题都属于控制器建模范畴。

## 建模的最小层次

一个够用的控制器性能模型，至少应包含：

- 地址映射：`channel/rank/bank/row/column`
- 命令序列：`ACT/READ/WRITE/PRE/REF`
- 时序约束：`tRCD/tRP/tRAS/tRFC` 等
- 请求队列：读写请求如何进入和出队
- 调度策略：按 row hit、年龄、QoS 还是混合策略排序

如果缺了其中任一层，模型就很容易过于理想化。

## 三类最常见的研究问题

### 问题 1：带宽为什么跑不满

常见根因：

- bank 并行度不够
- row conflict 太多
- 请求粒度和 burst 不匹配
- write drain 和切换损失过大

### 问题 2：p99 latency 为什么很差

常见根因：

- refresh 打断
- 热点 bank 排队
- 低优先级请求长期饥饿
- 控制器过度偏向 row-hit 优化

### 问题 3：某种内存升级为什么收益不如预期

常见根因：

- workload 并不能利用新增带宽
- 上游 cache/NoC 已先成为瓶颈
- 地址映射没有把更多并行资源用起来

## 一个实用的分析顺序

1. 先看 workload 是流式还是随机
2. 再看地址映射如何落到 bank/row
3. 再看调度是否偏好 row hit
4. 再看 refresh、写回和冲突是否成为尾延迟来源

这个顺序通常比一上来盯 JEDEC 参数更高效。

## 与 NoC/系统建模的关系

对 AI 芯片来说，内存控制器不该被单独看作黑盒，因为它和：

- DMA 请求模式
- NoC 流量形态
- SRAM tiling 策略
- HBM/DDR 通道组织

是强耦合的。

所以更完整的研究往往是：

`workload -> on-chip memory behavior -> NoC traffic -> memory controller scheduling -> DRAM service`

## 一句话理解

`内存控制器建模的意义，是把“峰值带宽表”翻译成“真实 workload 下会发生什么”。`
