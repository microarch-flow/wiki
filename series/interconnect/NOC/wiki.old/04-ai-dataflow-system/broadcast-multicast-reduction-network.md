# Broadcast / Multicast / Reduction 网络

上级：[AI Dataflow 系统视角](./README.md)

相关：[Collective Communication](./collective-communication.md)、[多网络组织](./multi-network-organization.md)、[Collective Implementation 深化](./collective-implementation-deep-dive.md)、[流量模式](./traffic-patterns.md)

## 本页与 Collective Communication 的关系

[Collective Communication](./collective-communication.md) 讨论的是"AI workload 中有哪些非点对点通信模式"——是 **what**。

本页讨论的是"这些通信模式如何用专用硬件网络高效支持"——是 **how**。

## 为什么通用 mesh 做 collective 效率不高

用普通 mesh 做 broadcast / reduce 的典型实现是 multiple unicast：

```text
Broadcast：源 tile 依次向每个目标发一份拷贝
  src -> dst0 (unicast)
  src -> dst1 (unicast)
  src -> dst2 (unicast)
  ...
  src -> dstN (unicast)

Reduce：每个源 tile 分别向 sink 发一份数据
  src0 -> sink (unicast)
  src1 -> sink (unicast)
  ...
  srcN -> sink (unicast)
```

这种方式的问题：

- **Broadcast**：源端出口链路被重复使用 N 次，成为热点；中间链路也被重复路径覆盖
- **Reduce**：sink 端入口被 N 个流同时压入，ejection 带宽不足导致 backpressure 蔓延
- **总线材占用**：如果数据在 mesh 中间被复制/汇聚，中间链路的重复占用远高于必要量

理想情况下，broadcast 应该沿树形路径逐级复制（每份数据只穿过每条链路一次），reduce 应该沿树形路径逐级汇聚（在中间节点就完成部分归约）。

## Broadcast / Multicast 网络

### 基本思想

在 base NoC 上叠加一个树形分发结构，数据从 root 沿树逐级复制到 leaf。

```text
           src
            |
         ┌──┴──┐
         │     │
       ┌─┴─┐ ┌┴──┐
       │   │ │   │
      T0  T1 T2  T3

数据只穿过每条链路一次，总线材占用 = O(N)
而 multiple unicast 的总线材占用 = O(N × avg_hop)
```

### 硬件实现方式

#### 方式一：router 内置 multicast 支持

在现有 mesh router 中增加 multicast 能力：

- 一个 flit 进入 router 后，可以同时从多个输出端口复制出去
- 需要 multicast 路由表或 header 中携带 bitmask 指定目标端口
- 复制在网络中间发生，靠近源端的链路不会重复占用

优点：不需要额外物理网络。缺点：router 复杂度增加，switch allocator 需要支持一对多。

#### 方式二：独立的 broadcast / multicast overlay

在 base mesh 旁边铺一张独立的树形网络：

```text
Base mesh (point-to-point data):
R---R---R---R
|   |   |   |
R---R---R---R

Broadcast tree overlay:
        Root
       /    \
      /      \
    Mid0    Mid1
   / \      / \
  T0  T1  T2  T3
```

优点：完全独立，不影响 base mesh 的 point-to-point 流量。缺点：额外面积和布线。

#### 方式三：Multicast group register

- 硬件维护若干 multicast group，每个 group 记录一组目标 tile
- 发送端发包时指定 group ID，网络自动沿预配置的树路径分发
- 适合 group 成员相对固定的场景（如一个 layer 内的 weight broadcast group）

### AI 芯片中的典型应用

| 场景 | 通信模式 | 硬件支持方式 |
|---|---|---|
| Weight broadcast | 1 → N multicast | broadcast tree 或 router multicast |
| Activation 分发到多个 consumer | 1 → k multicast（k < N） | multicast group |
| 控制面 barrier / config | 1 → all broadcast | broadcast tree 或 control NoC flood |

## Reduction 网络

### 基本思想

与 broadcast 对称：多个源的数据沿树形路径逐级汇聚，在中间节点完成部分归约，最终只有一份结果到达 sink。

```text
      T0  T1  T2  T3
       \  /    \  /
      add0    add1
         \    /
          add2
            |
          result

每级 tree 节点做一次加法，数据量逐级减半
```

### 两种实现策略

#### In-network reduction（网络内归约）

在 router 或专用 reduction 节点中内置 ALU（加法器），数据在传输过程中就完成归约。

```text
src0 ──┐
       ├── [add] ──┐
src1 ──┘           ├── [add] ── result
src2 ──┐           │
       ├── [add] ──┘
src3 ──┘
```

优点：

- 减少 sink 端压力（到达 sink 时数据已经是最终结果）
- 减少网络总流量（每级减半）
- 延迟接近 O(log N)

缺点：

- 需要在网络节点中放 ALU
- 数据格式必须固定（通常是定点或浮点加法）
- 需要精确的时序对齐（两个输入必须都到了才能做加法）

#### Endpoint reduction（端点归约）

不修改网络，所有 partial sum 都发送到 sink tile，由 sink tile 的计算单元完成归约。

```text
src0 ──→ sink
src1 ──→ sink  ──→ sink 内部做 N 次加法
src2 ──→ sink
src3 ──→ sink
```

优点：网络不需要修改。缺点：sink 端成为瓶颈，延迟 O(N)。

#### 分层 reduction（常见折中）

```text
cluster 内：endpoint reduction（cluster 内 tile 数少，sink 压力可控）
cluster 间：in-network reduction 或 reduction tree
```

这是实践中最常见的方式。

### Reduction tree 的拓扑选择

- **二叉树**：最简单，每级 fan-in = 2，延迟 O(log₂ N)
- **k 叉树**：fan-in = k，减少级数但每级仲裁更复杂
- **与 mesh 对齐的树**：tree 的节点放在 mesh router 旁边，共享物理位置

## Systolic Nearest-Neighbor Links

### 是什么

在 mesh 相邻 tile 之间增加直连数据路径，不经过 NoC router。

```text
普通 mesh：tile -> router -> router -> tile（至少 2 个 router 延迟）

Systolic link：tile -> tile（直连，1 周期或 pipeline 后固定延迟）
```

### 为什么对 AI 芯片重要

Systolic array / dataflow 架构中，大量计算是相邻 tile 之间的 pipeline forwarding：

- 矩阵乘法中 weight 沿一个方向流、activation 沿另一个方向流
- 每个 tile 做一步 MAC 后把结果传给邻居
- 这类通信不需要路由、不需要仲裁、不需要进 buffer

如果走 NoC router，每一跳的延迟（1-3 周期）和仲裁开销会成为 pipeline 的瓶颈。

### 设计要点

- 通常是单向或双向的寄存器级直连
- 宽度与 tile 的数据宽度匹配（如 256 bit）
- 不需要 flow control（因为是 lock-step pipeline，由编译器静态调度）
- 只用于最近邻通信，远距离通信仍走 NoC

### 与 base NoC 的关系

```text
┌─────┐  systolic link  ┌─────┐  systolic link  ┌─────┐
│tile0│ ──────────────→ │tile1│ ──────────────→ │tile2│
└──┬──┘                 └──┬──┘                 └──┬──┘
   │                       │                       │
   │    NoC router         │    NoC router         │
   └──────R────────────────┴──────R────────────────┘
          │                      │
     (用于 DMA、control、非近邻通信)
```

两套路径共存：systolic link 走规则的近邻数据流，NoC 走不规则的远距离通信和 control。

## Stream / Dataflow Channel

### 是什么

producer-consumer 之间的专用数据通道，通常带有独立的 buffer 和 flow control，与通用 NoC 的 traffic 隔离。

### 典型场景

- 两个计算阶段之间的 activation 传输（如 LayerNorm 输出 → 下一层输入）
- DMA engine 到 compute tile 的 weight streaming
- compute tile 到 output buffer 的结果流

### 与通用 NoC 的区别

| 特征 | 通用 NoC | Stream channel |
|---|---|---|
| 路由 | 动态，基于 header | 固定，编译期决定 |
| 带宽保障 | 尽力而为（best-effort） | 专用，带宽预留 |
| Buffer | 共享 VC buffer | 专用 FIFO |
| Flow control | credit-based，与其他流量共享 | 独立 back-pressure |
| 适合 | 不规则、突发流量 | 规则、持续、可预测流量 |

### 设计取舍

- 专用 channel 带宽不能被其他流量借用 → 利用率低时浪费
- 但保证了关键数据流的延迟和带宽 → pipeline 不会被干扰
- 通常由编译器静态配置 channel 的 src/dst 和带宽

## 对架构探索 DSL 的影响

如果你的 DSL 只能描述 point-to-point packet 路由：

```yaml
# 不够
src: tile_0
dst: tile_7
size: 4096
```

那就无法表达 AI workload 中大量出现的非点对点通信。至少需要扩展为：

```yaml
# broadcast / multicast
event:
  kind: multicast
  src: tile_0
  dst_group: [tile_1, tile_2, tile_3, tile_4]
  size: 4096
  network: data_noc
  replication: tree  # or multiple_unicast

# reduction
event:
  kind: reduce
  src_group: [tile_0, tile_1, tile_2, tile_3]
  dst: tile_4
  size: 1024
  op: add
  network: reduction_noc
  strategy: in_network  # or endpoint

# stream channel
event:
  kind: stream
  src: tile_0
  dst: tile_1
  channel: systolic_east
  size: continuous
  bandwidth: 256_bits_per_cycle

# traffic class
event:
  kind: unicast
  src: host
  dst: tile_0
  size: 64
  network: control_noc
  priority: high
```

## 本页结论

AI workload 中的通信不只是 point-to-point。Broadcast、multicast、reduction、systolic forwarding、stream channel 是同等重要的通信原语。用通用 mesh 模拟这些模式会严重高估开销；理解和建模专用硬件支持（broadcast tree、in-network reduction、systolic link、stream channel），是准确评估 AI 加速器 NoC 性能的关键。
