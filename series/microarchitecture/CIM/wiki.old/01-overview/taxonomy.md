# CIM / PIM / Near-Memory 分类

## 为什么这一页重要

这三个词在论文、公司宣传和媒体文章里经常混用。如果不先分清楚，后面讨论技术路线时会持续混乱。

## 基本包含关系

```text
Near-Memory Computing ⊃ PIM ⊃ CIM
```

这个式子不是严格的行业标准，但作为学习和分析框架非常有用。

## 三者的直观区别

| 概念 | 计算位置 | 直观理解 | 常见形态 |
| --- | --- | --- | --- |
| Near-Memory Computing | 靠近内存，但不一定在内存芯片内部 | 把算子尽量放到数据附近 | memory-side accelerator, HBM base die logic |
| PIM | 在内存芯片、堆叠、bank 或其附近加入处理逻辑 | 内存系统里带处理能力 | DRAM-PIM, HBM-PIM, GDDR6-AiM |
| CIM | 直接利用存储阵列或位线、字线参与计算 | 存储阵列本身参与计算 | SRAM-CIM, ReRAM-CIM, Flash-CIM |

## 如何区分

实践里不要只看命名，而是看下面四个维度：

### 1. 计算到底发生在哪里

- 如果只是把一个小加速器放在内存旁边，更接近 `Near-Memory`
- 如果计算逻辑在 DRAM / HBM 的 bank、logic die、base die 附近，更接近 `PIM`
- 如果 bitcell、bitline、wordline 本身参与乘加或逻辑操作，更接近 `CIM`

### 2. 是否利用了存储阵列物理特性

- `CIM` 通常会利用电荷、电流、位线叠加或阵列并行性
- `PIM` 不一定需要阵列本身参与，很多时候只是把逻辑单元推进到 memory-side

### 3. 主要收益来自哪里

- `Near-Memory`：减少 host 与 memory-side 之间往返
- `PIM`：提高 memory-bound 负载的带宽利用率
- `CIM`：减少阵列内外搬运，并把部分计算直接压进存储路径

### 4. 系统接口是否发生变化

越靠近 `PIM / CIM`，越可能需要：

- 新的 command interface
- 新的 memory controller 支持
- 特殊的 compiler / runtime 映射
- 对 workload 的重新切分

## 常见混用场景

以下情况最容易导致概念混乱：

- 产业界把所有 memory-side 计算统一叫“in-memory computing”
- 某些 HBM-PIM 产品被外界直接称为 CIM
- 一些 SRAM-based digital macro 被称为 PIM 或 CIM，取决于作者口径

因此，在本 wiki 里，优先采用“看机制，不看命名”的分类法。

## 在本 wiki 中的使用约定

- 如果讨论的是 `DRAM / HBM` bank 或 logic die 侧处理逻辑，默认归入 `PIM`
- 如果讨论的是 `SRAM / ReRAM / Flash` 阵列及其位线、字线参与计算，默认归入 `CIM`
- 如果讨论的是更宽泛的 memory-side 协同架构，归入 `Near-Memory`

## 区分时要看的维度清单

- 计算位置
- 是否利用存储阵列物理特性
- 数据路径是否显著缩短
- 是否需要专用 memory controller / host interface

## 后续可补充内容

- 典型案例对照表
- 容易混用的术语说明
- 产业界和学术界的口径差异
