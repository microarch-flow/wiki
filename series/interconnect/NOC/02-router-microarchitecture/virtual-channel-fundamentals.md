# 虚通道如何分离队列与共享链路？

上级：[02 路由器与逐跳流控](../SUMMARY.md#02-router-microarchitecture)；原章节：[02 路由器与逐跳流控](./README.md)

相关：[输入缓冲组织](./input-buffer-organization.md)、[Credit 与反压](./credit-based-flow-control.md)

<span id="virtual-channel-fundamentals"></span><span id="这页在回答什么问题"></span>虚通道（Virtual Channel，VC）让多个逻辑队列及其控制状态共享一条物理链路。它把缓冲和包的上下文分开管理，再由仲裁决定谁使用链路。

## 多个队列能改变什么

<span id="没有-vc-时错误耦合来得非常快"></span>假设同一输入端口的包 A 要去 East，但 East 堵住；包 B 要去空闲的 North。若 A 和 B 在同一个 FIFO 中，且 A 在队首，B 不能越过 A。

如果 B 位于另一个可独立选择的 VC，并且 North 的下游资源可用，B 就可以参与仲裁。这个条件很重要：若 A、B 仍被放入同一队列，或 B 也受共享输出与目的端阻塞，增加 VC 不会让 B 自动前进。

<span id="vc-不会增加物理带宽"></span>多个 VC 共享物理链路，不增加链路的峰值传输能力。它们可以让一个队列阻塞时，另一个队列利用原本空闲的传输机会，因此实际利用率可能提高。[Dally，Virtual-Channel Flow Control](https://groups.csail.mit.edu/cag/PSRG/papers/dally-ieee92.pdf)

## 一个包在 VC 上持有哪些状态

<span id="一个简单状态图"></span>以下以本专题的单播 wormhole 教学模型为例。header 在本地 input VC 的队首选择输出并申请下游 VC；body 和 tail 沿用这个绑定，同时仍逐 flit 竞争交换资源。各阶段可以合并，不要求每种实现都有相同状态机。

<span id="常见误解"></span>有三个相关但不同的状态：

| 状态 | 管理什么 | 何时释放或返还 |
| --- | --- | --- |
| 本地 input VC 上下文 | 本包在当前路由器的输出方向和下游 VC 绑定。 | 本例在 tail 成功离开当前 input VC 后清除。 |
| 下游 slot credit | 发送端已获得、尚未使用的下游缓冲槽授权。 | 在本文的逐跳协议中，下游移出一个 flit 后返还一个 credit。 |
| 下游 VC 分配许可 | 后续新包能否取得该下游 VC。 | 本例采用严格策略：下游 tail 离开并返回 free 后，才可重新分配。 |

因此，本地 tail 离开不等于下游 VC 已可分给新包；credit 大于零也不等于该 VC 许可空闲。其他实现可以采用不同复用策略，但必须保证 FIFO 顺序、包边界和上下文切换正确。[核心状态与两种许可策略](../08-simulator-construction/core-data-structures.md#三种独立状态)

## VC、消息类别与死锁

<span id="vc-的第二个动机给资源依赖分层"></span>VC 也可用于区分不同的资源依赖。例如，一种设计将特定路由阶段或消息类别映射到不同 VC，再检查这些资源之间的依赖。具体映射必须结合路由规则、端点、协议和服务条件。

虚拟网络（virtual network）常用于表达协议消息之间的逻辑分组；一个虚拟网络可以映射到一个或多个 VC。具体术语和映射取决于实现。不同 VC 仍可能共享链路、仲裁和目的端，因此队列分开不等于带宽或延迟已有保证。

<span id="ai-noc-和-cpu-coherent-noc-的典型差别"></span>request、response、控制消息或一致性消息的依赖关系可能不同。给它们贴上类别标签，或者简单分到不同 VC，并不足以证明系统无协议死锁。VC 数量也不能单凭 CPU、NPU 等设备名称确定。

依赖图中的环表示需要进一步分析的潜在风险；在自适应路由中，有环并不总意味着实际死锁。escape 子网是否可达、转换规则、资源和端点服务都要纳入所选证明。[Duato，1993](https://web.csl.cornell.edu/courses/ece5750/duato.tpds93.pdf)；进一步区分死锁、活锁和饥饿见[第四章](../04-routing-and-flow-control/deadlock-livelock-starvation.md)。

## 数量与容量的取舍

<span id="vc-数量为什么不是越多越好"></span><span id="一个定量直觉"></span>固定每个 VC 的深度与 flit 宽度时，增加 VC 会增加逻辑缓冲容量，也可能增加仲裁与状态管理。若总 slot 数固定，增加 VC 则可能使每个队列变浅。分配方式和流量决定哪种组织更合适，见[固定容量比较](./input-buffer-organization.md#固定容量如何分配)。

<span id="建模启示"></span>要研究队头阻塞，需要保存每个队列的顺序和可选输出。要验证 VC 生命周期，需要分别记录本地绑定、下游 slot credit 和 VC 许可。只统计活跃 VC 数，不能证明资源依赖或包边界正确。

<span id="一句话理解"></span>VC 将部分排队与上下文分开，物理带宽仍由各 VC 共享；它的收益和安全性取决于映射、分配与服务规则。
