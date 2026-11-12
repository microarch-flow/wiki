# Why AI NOC Is Different

上级：[06 AI NOC Specifics](./README.md)

相关：[Bus Vs Noc Vs Crossbar](../01-overview/bus-vs-noc-vs-crossbar.md)、[Memory Centric NOC](./memory-centric-noc.md)

## 这页在回答什么问题

这页回答：为什么 AI/NPU 的 NoC 不能直接照抄 CPU coherent NoC 的思路，以及这种差异会怎样改变我们优先关注的机制。

## 它们都叫 NoC，但主矛盾不同

CPU coherent NoC 的主任务通常是：

- 承载 cache miss、response、snoop、invalidate
- 保证协议正确性和 forward progress
- 处理动态、程序驱动、细粒度事务

AI dataflow NoC 的主任务更常是：

- 搬运 tensor block
- 连接 tile pipeline
- 组织 DMA、SRAM、HBM 之间的数据流
- 保持主路径稳定、可预测、易调度

这意味着两类系统在“最怕什么”上不一样。

## CPU coherent NoC 更怕协议复杂度

它更关心：

- request / response / snoop deadlock
- ordering / coherence correctness
- 协议分层和 VN/VC 组织
- 小事务低延迟

AI NoC 当然也关心 deadlock 和 QoS，但它更常见的系统症状是：

- 大块流量和关键小消息互相干扰
- memory response 卡住 compute
- collective 把某些路径压成热点
- endpoint local memory 吃不动导致 backpressure 外溢

## AI NoC 更受 compiler 和 placement 支配

这是最本质的差异之一。

在很多 AI 芯片里，通信图并不完全由程序运行时临场决定，而是被：

- operator mapping
- tile placement
- DMA 计划
- local SRAM 容量
- HBM 分配

提前强烈塑形。

因此 AI NoC 讨论里，“软件-硬件协同”不是锦上添花，而是主线。

## AI NoC 更常面对 collective

CPU coherent NoC 的典型基本单元是 cache-line 事务。AI NoC 则更常面对：

- broadcast / multicast
- gather / reduce
- all-to-all-like dispatch
- tile-to-tile forwarding

这些模式会直接改变：

- topology 偏好
- QoS / multi-network 需求
- 是否值得做专用 collective 支持

## AI NoC 的关键路径经常是 memory 路径

特别是在 decode、KV cache、memory-bound inference 场景下，NoC 的角色往往不是“拼吞吐”，而是：

- 保护 request / response 关键路径
- 让 HBM 返回不要被 bulk traffic 淹没
- 控制 ejection 和 local SRAM 写入口压力

这和 CPU 世界里围绕 coherence 协议组织的关注点很不同。

## deterministic 诉求也更强

很多 AI/NPU 团队更希望得到的是：

- 可静态预测
- 可复现
- 易验证
- 延迟边界更稳

因此他们常常更偏向：

- dimension-order routing
- source routing
- static schedule
- control/data/response 的明确分层

而不是先把灵活性做到最大。

## 常见误区

- 认为 AI NoC 只是“更大带宽的 CPU NoC”
- 认为 AI 流量都很规则，不需要考虑动态性
- 认为只要算力够高，NoC 就只是附属件

更准确的说法是：

- AI NoC 的主要矛盾从 coherence correctness 转向 dataflow orchestration
- AI 流量里既有 GEMM 这类规则模式，也有 decode、MoE 这类动态模式
- 很多系统瓶颈其实首先是 NoC 和 memory path 的组织问题

## 一句话理解

AI NoC 和 CPU coherent NoC 的差别，不只是流量大小，而是系统目标、工作负载结构和软件参与方式都不一样。

## 建模启示

面向 AI NoC 的模型，至少要比 coherent-transaction 模型多表示三类东西：

- workload phase
- collective pattern
- compiler / placement influence

否则你很容易把 AI NoC 误建成“没有 snoop 的 CPU NoC”，而错过真正重要的系统约束。
