# 先进封装里的 PI、PDN、Decap 到底怎么理解

上级：[[10 - 共性工程问题]]

相关：[[04 - Si Interposer]]、[[15 - CTE、热应力与 Warpage：从概念到 3DIC]]

## 为什么这件事重要

很多人刚学先进封装，会把重点放在：

- 互连密度
- 带宽
- HBM
- 热

但到了高性能系统里，另一个经常决定成败的核心问题是：

`电源能不能稳稳地送到负载边上`

这就是 PI、PDN、decap 的世界。

## 1. 什么是 PDN

PDN = `Power Delivery Network`

直观理解：

它就是把电从外部电源一路送到芯片内部开关单元的那整条路径。

这条路径包括很多层：

- 板级
- package substrate
- interposer / RDL
- bump / micro-bump / TSV
- die 内金属网络

所以 PDN 不是芯片内部一件事，而是跨越板、封装和 die 的整条链路。

你也可以把它理解成一套分层供能系统：

- 板级是远端主干
- substrate / interposer 是中间配电层
- die 金属网络是最后几毫米乃至几微米的末端网络

## 2. 什么是 PI

PI = `Power Integrity`

它不是一个具体结构，而是一个结果：

`这条 PDN 在动态负载下，能不能把电压稳定送到负载处`

如果 PI 不好，常见表现就是：

- 电压 droop
- ground bounce
- 噪声耦合
- 时序/功能不稳定

所以 PI 关注的不是“静态有没有电”，而是：

`动态切换最剧烈的时候，电压还能不能稳住。`

## 3. 什么是 decap

decap = decoupling capacitor，去耦电容。

它的作用可以粗略理解成：

- 当负载瞬间需要电流时，先在本地“垫一口电”
- 缩短高频瞬态电流回路
- 降低电源噪声

所以 decap 不只是“多放几个电容”，而是在高速开关系统里给 PDN 提供局部缓冲。

更直觉地说：

- 远处供电响应慢
- 本地 decap 先出手
- 之后远端供电再把电慢慢补回来

## 4. 为什么先进封装时代 PI 更难

### 4.1 电流越来越大

AI/HPC 芯片功耗高，瞬态电流波动更大。

### 4.2 互连层级更多

电要经过：

- substrate
- interposer / RDL
- bump
- TSV
- die metal

层级越多，寄生越复杂。

### 4.3 HBM 和 chiplet 让系统更复杂

当多个 chiplet、HBM、I/O die 共同存在时，供电网络不再是单 die 问题，而是整个 package 的系统问题。

### 4.4 电流瞬态更激烈

AI/HPC 芯片的并行开关活动很强，这意味着：

- 平均功耗重要
- 瞬态电流变化更重要
- 高频电压噪声更难压

## 5. 为什么 decap 位置这么关键

同样一个电容，放在不同地方，效果完全不同。

因为关键不是只有“容量多大”，还有：

- 离负载多近
- 回路多短
- 中间寄生多大

所以先进封装里会特别在意：

- die 内 decap
- interposer decap
- package decap
- embedded decap

## 6. 一个非常简化的等效电路直觉

可以粗略把供电看成：

```text
外部电源 -- 寄生R/L -- package/interposer寄生 -- 负载
```

如果在负载附近加 decap，就相当于在末端并联了一个本地储能节点：

```text
外部电源 -- 长路径 -- 负载
                     |
                   decap
```

这样高频瞬态电流不必每次都从远处拉过来。

## 7. 为什么先进封装会把 decap 外移

最容易想到的做法是把所有 decap 都塞进 logic die。  
但现实里经常不会这么做，因为：

- logic die 面积太贵
- 逻辑工艺不一定最适合做大面积高密度 decap
- interposer / package 硅平台有时更适合承担一部分 decap 职能

## 8. 为什么 interposer / advanced package 会变成 PI 平台

这就是先进封装和传统封装最不一样的地方之一。

传统封装里，封装更多像“连接器”；但在高性能系统里，interposer / package 本身开始承担：

- 高频供电路径优化
- 局部 decap 放置
- power / signal 协同布线

这也是为什么像 CoWoS-S 会强调：

- DTC / eDTC
- 更短 PDN 路径
- 更强 power management

## 9. 你可以怎样理解 DTC / eDTC

本质上，它们是在封装级硅平台上，把一部分高密度 decap 能力从 logic die 内迁移出来。

这样做的动机是：

- die 面积很贵
- logic 工艺不是最适合做超大 decap 的地方
- interposer 更适合铺更大面积、离负载又近

所以可以把它记成：

`不是所有去耦都塞进 logic die，而是把一部分高密度 decap 外移到更合适的封装硅平台。`

## 10. PI 常在哪些层次出问题

### 板级到 package 入口

- 供电主干阻抗
- 回流路径

### substrate / interposer / RDL

- 供电层分布
- 电感
- decap 分布不合理

### bump / micro-bump / TSV

- 局部寄生
- 电流拥挤

### die 内部

- 局部 IR drop
- 高开关活动区的瞬态噪声

## 11. 一个更完整的心智模型

### PDN

是“供电路径”。

### PI

是“这条供电路径在动态负载下稳不稳”。

### decap

是“让这条供电路径在高频瞬态下更稳的局部储能/缓冲结构”。

## 12. 为什么这和先进封装直接相关

因为高性能先进封装不只是连线，更是在重做系统供电拓扑。

当系统从：

- 单大 die
- 传统 substrate

变成：

- 多 chiplet
- HBM
- 2.5D / 3D

PI 就必须在 package 级重新设计。

## 13. 最终压缩理解

`PDN 是路，PI 是路稳不稳，decap 是关键节点上的缓冲站。`

先进封装越高端，package / interposer 就越不只是信号连接层，而是供电网络本体的一部分。
