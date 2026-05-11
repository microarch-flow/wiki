# Shared Bus、Bus Matrix 与 Crossbar

上级：[04 微架构与系统集成](./README.md)

相关：[互连组件与数据路径分解](./interconnect-components.md)、[AXI Crossbar 案例卡](../06-scenarios-case-studies/axi-crossbar-case-card.md)

## 这页在回答什么问题

当系统从简单走向复杂时，为什么互连组织会从 shared bus 演化到 bus matrix 或 crossbar。

## Shared Bus

特点是：

- 结构最简单
- 实现和验证成本低
- 所有流量更容易串到一起

问题是：

- 并发能力弱
- 一个慢事务容易拖长全局等待
- master/slave 一多就容易成为系统瓶颈

## Bus Matrix

bus matrix 的核心不是“完全自由连接”，而是：

- 允许多个 master 到不同 slave 的部分并发
- 比单总线更少全局串行化
- 通常在成本和并发之间做折中

它适合：

- 中等规模 SoC
- 多个主要 master，但不需要全连接极致并发

## Crossbar

crossbar 更进一步：

- 并发更高
- 局部路径更独立
- 更适合高吞吐主干

但代价也最大：

- 面积和功耗更高
- 仲裁和 response 路径更复杂
- 时序压力更重

## 选型时最该看什么

- master 数量和流量模式
- slave 热点是否集中
- 控制面和数据面是否混跑
- 是否真的需要高并发，而不是只是“想要更高级”

## 一句话理解

shared bus、bus matrix、crossbar 不是代际替换关系，而是针对不同并发需求和成本边界的三种组织方式。
