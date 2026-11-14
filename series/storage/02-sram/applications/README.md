# SRAM 应用形态

上级：[存储系统](../../README.md)

相关：[SRAM 基础](../foundations/README.md) · [系统基础](../../01-memory-hierarchy/01-system-basics/README.md) · [RAM 阅读路线](../../reading-and-reference/01-reading/README.md)

## 这页在回答什么问题

Register file、cache、scratchpad、TCM 和 NPU buffer 的使用目标不同。它们可能采用 SRAM，也可能包含其他存储实现。本章从数据放置、访问并发和时间约束出发，解释这些角色如何使用存储资源。

## 不同系统角色如何使用 SRAM

| 角色 | 主要问题 | 需要确认的边界 |
| --- | --- | --- |
| Register file | 执行管线如何取得操作数和写回结果？ | 读写需求、端口、旁路和冲突处理。 |
| Cache | 硬件怎样判断数据是否在本地？ | tag、data、命中路径和替换策略。 |
| Scratchpad | 使用方怎样放置与访问局部数据？ | 地址空间、搬运、同步与共享资源。 |
| TCM | 紧耦合访问在什么条件下可预测？ | 访问路径、其他请求者、仲裁和时限。 |
| NPU buffer | 权重、激活和部分和如何供给计算？ | 数据生命周期、实际存储位置、带宽与调度。 |

这些名称描述系统角色，不规定必须使用 6T cell 或某个端口组织。例如，寄存器堆也可以由触发器或锁存器实现；同一块 SRAM 可以按配置承担多种数据角色。具体电路与接口仍须结合目标设计。

Cache 与 scratchpad 的管理责任和访问路径，在系统层的 [Cache 与 scratchpad](../../01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md)中统一比较。本章保留一个[阅读入口](./scratchpad-vs-cache.md)，不重复该比较。

## 阅读顺序

1. [Register file](./register-file-as-sram.md)：从操作数供给看逻辑需求、端口与旁路。
2. [Cache 的 tag 与 data](./cache-sram-tag-data-arrays.md)：看查找、比较和数据选择。
3. [Scratchpad 与 cache 导读](./scratchpad-vs-cache.md)：进入系统层比较。
4. [TCM 与实时性](./tcm-itcm-dtcm-in-mcu.md)：分析紧耦合路径与共享带来的等待。
5. [NPU 的 SRAM buffer](./npu-weight-buffer-activation-buffer.md)：从数据角色进入 NPU 的供数与搬运。

若主要研究实时系统，可以在第 3 篇后进入 TCM；若主要研究加速器，可直接读第 5 篇，再进入 [NPU 数据路径与存储组织](../../01-memory-hierarchy/04-npu-case/README.md)。

## 一句话理解

SRAM 是一种存储技术；应用角色还规定数据如何被放置、访问和管理。

## 建模启示

先确定要观察的请求与完成边界，再按问题保留必要的地址映射、端口、仲裁和响应时序。比较不同角色时，还需表示适用的命中与填充、软件放置与同步、旁路，以及数据搬运；不能仅用相同容量推断相同的系统行为。
