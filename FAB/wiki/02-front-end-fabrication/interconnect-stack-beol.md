# BEOL 的金属互联:从 M0 到 redistribution

上级:[前道工艺](./README.md)
相关:[前道工艺的整体节奏:FEOL/MOL/BEOL](./process-flow-overview.md), [互连组件与数据路径分解](../../BUS/wiki/04-microarchitecture-integration/interconnect-components.md), [封装内的信号完整性](../06-cross-cutting-engineering/signal-integrity-in-package.md)

## 这页在回答什么问题

BEOL 金属栈如何把 transistor 连接成真实系统，以及为什么片上 BUS/NoC/PDN 不是抽象连线。重点是理解金属层级、RC、via、拥塞和 top interface 如何限制架构实现。

## 金属栈的层级直觉

BEOL 可以看成一组不同尺度的金属资源：

```text
transistor / contact
  -> M0 / M1: local standard-cell routing
  -> lower metals: short local signals
  -> middle metals: block-level routing
  -> upper metals: long wires / clock / power
  -> top metal / pad / bump interface
```

越靠下，pitch 越细、密度越高、线更窄，适合局部连接但电阻更高；越靠上，金属更厚、更适合长距离信号和供电，但层数有限、资源昂贵。架构师在逻辑图上画一条宽总线或 NoC link，物理上要消耗这些金属资源和 via 资源。

## 为什么 wire 会成为瓶颈

先进节点里，transistor 变小不意味着 wire 同比例变好。细线电阻上升、线间电容、via 电阻、repeaters、clock skew、IR drop 和 electromigration 都会限制系统频率和能效。长距离通信的代价经常不由逻辑门决定，而由 BEOL wire 决定。

这直接连接到 BUS wiki 的路径分解：decoder、arbiter、buffer、adapter 和 return path 不只是 RTL 模块，它们需要布局在物理位置上，并通过金属栈连接。若 return path 绕远、共享仲裁点靠近拥塞区域，模型中的低延迟路径会在布局布线后变成高 RC、高功耗路径。

## BEOL 与 PDN

供电网络也占用 BEOL。高功耗 compute tile 需要足够的 power straps、vias 和 decap 支撑瞬态电流；这些资源会和 signal routing 竞争。若架构把 compute density 拉高，但没有留出 PDN 和热路径，频率目标可能被 IR drop 和温升限制。

| 金属资源 | 主要服务 | 架构冲突 |
| --- | --- | --- |
| lower metal | 标准单元局部连接 | cell density 与 routability |
| middle metal | block 内信号、macro 周边 | SRAM/NoC/控制逻辑拥塞 |
| upper metal | long wire、clock、power | NoC、global bus、PDN 竞争 |
| top metal/pad | bump、I/O、封装接口 | floorplan 与 package co-design |

## 从 BEOL 到 redistribution

BEOL 的顶层会连接到 pad、bump 或封装接口。到了封装侧，RDL redistribution layer 会继续把 die I/O 重新映射到 package 需要的位置。二者都叫“互联”，但物理尺度和责任不同：BEOL 是 die 内金属栈，RDL 是 package 级重布线。后续 [RDL:截面结构与制造流程](../04-back-end-packaging/key-components/rdl-redistribution-layer.md) 会从封装侧展开。

这个边界对 chiplet 和 HBM 很关键。die 内 NoC 到 die 边缘的路径受 BEOL 约束；die 边缘到 HBM/interposer/RDL 的路径受 package 约束。跨 die 性能模型必须把这两段分开。

## 常见误解

常见误解是“片上互联只要 RTL 支持足够带宽就行”。实际带宽需要金属宽度、层分配、repeaters、buffers、clocking、PDN 和热共同支撑。RTL 能发出请求，不代表 BEOL 能以目标频率和功耗承载这些线。

另一个误解是“先进节点线也一定更短更快”。局部线可能更密，但全局线、via、拥塞和 RC 不会按 logic density 理想缩放。大规模 NoC 和宽 bus 往往需要 floorplan-aware 设计。

## 一句话理解

BEOL 是片上系统真正的物理互联资源；它把 BUS/NoC/PDN 从逻辑结构变成受 RC、via、拥塞和金属层限制的物理路径。

## 架构师启示

如果我设计一个 mesh NoC，不能只按 hop 数估算延迟和能耗。每条 link 的物理长度、使用金属层、是否跨 SRAM macro、是否与 PDN/clock 竞争，都会改变真实性能。NoC wiki 中的 [topology physical realization](../../NOC/wiki/03-topology/topology-physical-realization.md) 应该和本页一起读。

一个具体决策例子：若 workload 需要高 bisection bandwidth，增加 NoC 宽度可能不如优化 tile placement 和 memory adjacency 有效。因为宽 link 会消耗 BEOL 资源，增加拥塞与功耗，而更好的 floorplan 可以减少长线和 repeater 代价。
