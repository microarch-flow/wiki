# Wormhole Vs VCT Vs Store Forward

上级：[02 Router Microarchitecture](./README.md)
相关：[Packet Flit Phit Hierarchy](./packet-flit-phit-hierarchy.md), [Virtual Channel Fundamentals](./virtual-channel-fundamentals.md)

## 这页在回答什么问题

为什么 NoC 的 switching 方式会从 store-and-forward 演化到 virtual cut-through，再演化到 wormhole；每一步到底在拿什么换什么。

这不是技术年表，而是一条非常实用的 trade-off 链：你想省多少 buffer，就得接受多少路径占用和 HoL blocking 风险。

## Store-and-forward：最直观，也最昂贵

store-and-forward 的规则是：一个 router 必须先收下整个 packet，才能开始往下一跳转发。

好处很容易理解：

- 控制最简单
- packet 在本地完整可见
- 下游路径争用和本地接收相对解耦

代价同样直接：

- 每个 router 都要为整包准备缓冲
- 每一跳都要额外支付“等整包收齐”的时间

举例，64B packet，128b 链路：

```text
64B = 512b = 4 flit

每跳至少要先花 4 cycles 收满，再开始发下一跳
```

对于多跳路径，这个延迟会按 hop 叠加。你不是在流水前进，而是在每一跳都重新等一遍整包。

## Virtual cut-through：先减延迟，但仍要保整包缓冲

VCT 的关键改动是：header 一旦看见下游有足够空间容纳整个 packet，就可以不等全包收齐，尽早开始转发。

这减少了每 hop 的等待时间，因为 packet 可以像管道一样更早向前流。但它保留了一个重约束：下游必须能接下“整包”。

于是你得到的 trade-off 是：

- 延迟比 store-and-forward 低
- 但 buffer 预算仍然接近按 packet 维度做

所以 VCT 是一个过渡方案。它已经意识到“整包等满再走”过于保守，但还没彻底摆脱整包缓冲这个成本中心。

## Wormhole：按 flit 把路径拉成管道

wormhole 再往前一步：header flit 先建路，后续 body/tail flit 只要前面的路径资源还占着，就可以持续跟进。router 不再需要容纳整包，只需容纳少量 flit。

名字很形象，但真正值得记住的是它的资源行为：packet 像一条虫一样横跨多个 router，每一段身体占着一段缓冲和链路。

好处：

- buffer 需求大幅下降
- 多 hop 能形成真正的流水
- 非常适合片上面积敏感场景

代价：

- packet 占用路径资源的时间跨度变长
- 一个长 packet 可以把后面的短 packet 压很久
- HoL blocking 和 deadlock 风险被放大

也就是说，wormhole 不是“更聪明的转发”，而是“用更小的 buffer 接受更紧的资源耦合”。

## 一个三跳例子

仍假设 64B packet、128b 链路、4 flit。

store-and-forward：

```text
hop0: receive 4 cycles, then send
hop1: receive 4 cycles, then send
hop2: receive 4 cycles, then send
```

wormhole：

```text
cycle 0: header at R0
cycle 1: header at R1, body0 at R0
cycle 2: header at R2, body0 at R1, body1 at R0
cycle 3: header at R3, body0 at R2, body1 at R1, tail at R0
```

这就是 wormhole 对 latency 和 buffer 的真正吸引力。你不再每跳支付整包等待，而是让 packet 跨多个 hop 同时占着路径。

## 为什么 wormhole 特别适合 NPU

NPU 常见特点是：

- 端点数多
- router 数量多
- buffer 面积非常敏感
- 许多流量是可预测、规整的大流

在这种场景下，store-and-forward 太浪费 buffer，VCT 仍偏重，而 wormhole 给出一个更平衡的点：接受更复杂的资源管理，换取可承受的面积和更高的流水化能力。

这也是为什么后面 VC、credit 和 allocator 变得如此重要。它们不是独立新机制，而是 wormhole 代价的后续补丁：

- 因为 wormhole 会放大 HoL blocking，所以需要 VC
- 因为只存少量 flit，所以需要精细 credit
- 因为更多 flit 在途并行，所以 allocator 更重要

## Packet 大小在 wormhole 下为什么尤其敏感

同一条路径上，一个长 packet 会占着更多周期的 crossbar 与 link 机会，即便每一拍只是一个 flit。

所以 packet 大小不只是 header overhead 问题，还会影响：

- 路径占用时长
- 后续流量等待时间
- response 小包的尾延迟

这点对 AI NoC 特别重要。把大块 activation 或 DMA response 做得过大，可能提升平均吞吐，却伤害 control/response 小流的 P99 延迟。

## 常见误解

常见误解：wormhole 一定比 VCT 或 store-and-forward 更好。  
实际上：它只是更适合面积受限、多 hop 的片上网络；如果你极端重视隔离、整包可见性或调试简单性，别的点可能更合理。

常见误解：wormhole 低 buffer 就等于低延迟。  
实际上：它降低的是每 hop 的整包等待，但会通过更长的路径占用时间，把竞争和阻塞传播问题带回来。

## 一句话理解

store-and-forward 用整包缓冲换简单控制，VCT 用整包可容纳换更早转发，wormhole 用 flit 级流水换小 buffer；越往后，buffer 越省，资源耦合越强。

## 建模启示

如果采用 wormhole，模型至少要有：

- `header_establishes_route`
- `tail_releases_route`
- `flit_level_buffer_occupancy`

如果采用 store-and-forward，反而可以把一个 router 简化成“收到整包后延迟一拍再发”的 packet-level 队列；这就是为什么 switching policy 会直接决定模型粒度。

一个通用数据结构可以写成：

```text
SwitchingPolicy = STORE_FORWARD | VCT | WORMHOLE
```

并据此改变 forwarding 条件：

- `STORE_FORWARD`: `packet_fully_buffered == true`
- `VCT`: `downstream_can_accept_full_packet == true`
- `WORMHOLE`: `header_bound && credit_available`

若只关心结构趋势，`VCT` 常可忽略不单建；但如果你想解释“为什么 buffer 从 packet 级缩到 flit 级之后，VC 和 credit 立刻变关键”，那 VCT 这个中间态非常有助于把演化链讲清楚。
