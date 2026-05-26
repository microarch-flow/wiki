# Compiler NOC Co Design

上级：[06 AI NOC Specifics](./README.md)

相关：[Deterministic NOC And Static Scheduling](./deterministic-noc-and-static-scheduling.md)、[Address Map And Routing Table](../05-system-integration/address-map-and-routing-table.md)

## 这页在回答什么问题

这页回答：如果 NoC 的价值越来越依赖 placement、route plan、DMA 计划和 traffic class 选择，那么 compiler/runtime 到底需要参与到什么程度。

## compiler 参与的不只是“把算子放到 tile 上”

真正有价值的 compiler-NoC 协同通常至少包括：

- placement
- memory placement
- DMA 计划
- route 选择或 route id 选择
- collective 组织方式
- phase overlap / double-buffering

这说明 NoC 已经不是下层透明细节，而是编译器决策空间的一部分。

## 为什么 AI NoC 特别需要它

因为很多 AI 通信图并不随机，而是：

- 可以由算子分块推导
- 可以由数据布局推导
- 可以由阶段边界推导

一旦这些信息已知，不利用它们去帮助 NoC，就是把本可提前解决的问题留给运行时局部仲裁去硬扛。

## compiler 真正能换来什么

最常见的收益有：

- 把高冲突流错开时间窗口
- 让热点路径提前被识别
- 选择更合理的 tile / memory placement
- 决定哪些流该用 source routing、哪些流该独立 class

换句话说，compiler 不是替代 NoC，而是减少 NoC 运行时需要“即兴应对”的次数。

## 它也有边界

compiler 并不能自动解决：

- 未知的动态热点
- 运行时才显现的负载不均
- endpoint 实时消费波动
- cross-die 瞬时竞争

因此更现实的协同方式通常是：

- compiler 决定主要结构
- hardware 负责局部安全、隔离和保底前进

## 为什么这会影响 DSL

如果 DSL 只会描述物理连线，不会描述：

- route intent
- traffic class
- phase schedule
- memory placement intent

那它就不能承载真正的 compiler-NoC 协同。

## 一句话理解

compiler-NoC 协同的价值，在于把 AI workload 中可提前知道的通信结构，提前变成更可控的网络行为。

## 建模启示

模型和 DSL 最少要让 compiler 能表达：

- who talks to whom
- when
- via which class / network / route family
- with what buffering or overlap intent

只有这样，系统才能比较“靠编译器预先整形流量”和“完全让网络运行时自己消化流量”之间的真实差别。
