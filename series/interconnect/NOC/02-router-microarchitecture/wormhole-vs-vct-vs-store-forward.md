# 存储转发、虚直通与虫洞交换有什么区别？

上级：[02 路由器与逐跳流控](../SUMMARY.md#02-router-microarchitecture)；原章节：[02 路由器与逐跳流控](./README.md)

相关：[Packet、Flit 与 Phit](./packet-flit-phit-hierarchy.md)、[虚通道基础](./virtual-channel-fundamentals.md)

<span id="wormhole-vs-vct-vs-store-forward"></span><span id="这页在回答什么问题"></span>一个 packet 到达中间节点后，什么时候可以向下一跳发送？如果输出被占用，已经接收的数据放在哪里？不同交换方式对这两个问题给出不同答案。

## 三种转发方式

| 方式 | 何时开始向下一跳发送 | 缓冲与阻塞 |
| --- | --- | --- |
| <span id="store-and-forward最直观也最昂贵"></span>存储转发（store-and-forward） | 本节点收齐整个 packet 后。 | 本节点需要能保存完整 packet；下一跳等待与本地收包较容易分开。 |
| <span id="virtual-cut-through先减延迟但仍要保整包缓冲"></span>虚直通（virtual cut-through，VCT） | 头部确定输出且满足实现的发送条件后，可以在收齐前开始。 | 遇阻时保留整包所需的缓冲能力；一种实现会在接收前为整包预留空间。 |
| <span id="wormhole按-flit-把路径拉成管道"></span>虫洞交换（wormhole） | 头 flit 取得所需资源后先行，其余 flit 逐步跟随。 | 中间节点不必为每个包预留整包空间；受阻的包可能分布在多个节点。 |

VCT 的原始思路是在输出可用时提前转发，遇阻时缓存；不同实现的预留时点和条件可能不同。[Kermani 与 Kleinrock，1979](https://www.lk.cs.ucla.edu/data/files/Kermani/Virtual%20Cut-through%20A%20New%20Computer%20Communication%20Switching.pdf)

wormhole 中，一个包可能持有沿途的 VC 上下文和若干缓冲槽。物理 crossbar 和链路可以按 flit 仲裁；如果实现允许，其他 VC 的 flit 可在空隙中通过。**持有 VC 不等于一直独占物理链路。**[Dally，1992](https://groups.csail.mit.edu/cag/PSRG/papers/dally-ieee92.pdf)

## 用同一条三跳路径比较

<span id="一个三跳例子"></span>下面是构造例子，不是硬件测量。路径为 R0 → R1 → R2 → R3；一个包包含头 H、两个 body 和尾 T，共 4 个 flit。拍 0 开始前，整个包已在 R0 可发送。各链路每拍传一个 flit，下一拍开始时到达相邻节点；无竞争、无空拍。节点可在到达拍转发。VCT 的例子假设各跳均可为该包预留足够空间。

| 方式 | R0 → R1 的发送拍 | R1 → R2 的发送拍 | R2 → R3 的发送拍 | T 到达 R3 |
| --- | --- | --- | --- | --- |
| 存储转发 | 0–3 | 4–7 | 8–11 | 拍 12 开始 |
| 所述 VCT | 0–3 | 1–4 | 2–5 | 拍 6 开始 |
| 所述 wormhole | 0–3 | 1–4 | 2–5 | 拍 6 开始 |

VCT 与 wormhole 在这个无阻塞例子中有相同时间线，但它们对缓冲的要求不同。存储转发每跳都先收齐包；另外两种可以让多个 hop 同时传输同一个包的不同 flit。

本例把路由和节点内部转发简化到到达拍即可开始。实际流水级、链路延迟、接收条件和竞争都会改变时间；它也不同于[模拟器拍末快照契约](../08-simulator-construction/router-pipeline-pseudocode.md#时间与快照契约)，不能混用拍号。

## 遇到阻塞会发生什么

<span id="packet-大小在-wormhole-下为什么尤其敏感"></span>在所述 wormhole 模型中，如果头部因下游资源不可用而停住，后续 flit 会在沿途有限的队列中等待。已有的 VC 绑定和缓冲槽可能持续被占用；阻塞能否继续传播，取决于在途流量、空槽和流控。

较长的包可能更久地持有包级上下文，也需要更多链路传输机会。其他 VC 是否可以交错前进，取决于队列和仲裁规则；不能仅凭包长推断另一个包一定等待多久。

<span id="为什么-wormhole-特别适合-npu"></span>较小的逐跳缓冲可能有利于面积受限的设计，但也要考虑资源耦合、控制和验证成本。NPU 或其他系统是否选择 wormhole，需要结合包长、流量、布局和服务要求比较。

## 用于建模时保留哪些条件

<span id="常见误解"></span>无争用例子说明了提前转发可以减少等待，不证明某种交换方式在所有负载和实现下延迟最低。VCT 的整包可容纳条件，也不能直接替代所选实现的流控规则。

<span id="建模启示"></span>记录每种方式的转发条件、缓冲容量、资源持有和释放时机。若关心逐 flit 阻塞，还需要队列、仲裁和流控状态；若只研究粗粒度容量，可以选择更简单的近似，但不能据此声称已算出逐跳等待。

<span id="一句话理解"></span>三种方式的关键区别是何时转发，以及遇阻时数据和资源留在哪里。
