# Packet / Flit / Wormhole

上级：[Router 微架构](./README.md)

相关：[Credit / Backpressure](./credit-backpressure.md)、[NI / DMA / 存储接口](../04-ai-dataflow-system/ni-dma-memory-interface.md)

## 核心心智模型

一个 packet（数据包）不是瞬间从源端移动到目的端，而是被切成多个 flit（flow control unit，流控单元），在多个 router 和 link（链路）上像流水线一样逐跳推进。

## Packet / Flit / Phit

### Packet

packet 是一次完整通信事务的语义单位。

在 AI dataflow NoC 中，一个 packet 可能表示：

- tile（计算单元）间的 activation（激活值）stream
- DMA（Direct Memory Access，直接存储器访问）write burst
- DMA read request
- read response
- partial sum（部分和）fragment
- barrier（同步屏障）或 descriptor（描述符）

### Flit

flit 是 router buffer（缓冲区）、credit（信用计数）、仲裁所围绕的流控单位。  
现代 NoC 建模中，第一版最值得建立的是 flit-level 模型。

一个 packet 被切分成多个 flit，各 flit 有不同角色：

```
一个 packet（例如 256 字节的 activation 数据块）
  ├── header flit  ← 第一个 flit，携带目的地址、路由信息、消息类型
  ├── body flit 0  ← 有效载荷数据
  ├── body flit 1  ← 有效载荷数据
  ├── body flit 2  ← 有效载荷数据
  └── tail flit    ← 最后一个 flit，标记 packet 结束，触发释放 VC 等路径资源
```

- header flit 负责探路：到达每个 router 时触发路由计算（RC）和 VC 分配（VA）
- body flit 只需做 switch allocation（SA）：路由和 VC 已由 header 确定
- tail flit 离开时释放沿途占用的 VC，让其他 packet 可以使用

### Flit 宽度与 link 物理线宽的关系

flit 宽度是逻辑概念，link 宽度是物理概念，两者的比值决定了传输行为：

| 关系 | 含义 | 举例 |
| --- | --- | --- |
| flit 宽度 = link 宽度 | 一个 flit 一个周期传完，此时 flit = phit | flit 128-bit，link 128-bit |
| flit 宽度 > link 宽度 | 一个 flit 需多个周期传完，每周期传的那一份叫 phit | flit 256-bit，link 128-bit → 2 个周期 |
| flit 宽度 < link 宽度 | 每周期 link 没被填满，带宽浪费 | 通常不这样设计 |

架构探索阶段通常假设 flit 宽度 = link 宽度（即 flit = phit），简化建模。

### Phit

phit（physical unit，物理传输单元）是物理链路每周期真正可传输的位宽单位。  
如果你当前目标是架构探索而不是物理链路设计，通常可以暂时不引入 phit。

## Router 的最小结构

可以先把 router 理解为下面四部分：

- input buffer：每个 input port 有若干 VC，每个 VC 是一个独立的 FIFO 队列
- routing / allocation logic：决定 flit 走哪个 output port、用哪个下游 VC
- internal crossbar（交叉开关）：全连接交换矩阵，按 SA 结果建立 input → output 通路
- output link：连接到下游 router 的物理链路

### Router 流水线五阶段

更接近真实实现的流水阶段通常包括：

| 阶段 | 名称 | 做什么 | 谁经历 |
| --- | --- | --- | --- |
| RC | Route Computation | header 到达后，根据目的地址计算应走的 output port | 仅 header flit |
| VA | VC Allocation | 在下游 router 分配一个空闲 VC（整个 packet 生命周期内占用） | 仅 header flit |
| SA | Switch Allocation | 仲裁竞争 crossbar 通路，获胜者通过 | 所有 flit（每周期竞争） |
| ST | Switch Traversal | flit 实际穿过 crossbar 到达 output port | 所有 flit |
| LT | Link Traversal | flit 在物理 link 上传输到下游 router | 所有 flit |

关键区别：header flit 需要走完 RC → VA → SA → ST → LT 全部五个阶段；body / tail flit 只需走 SA → ST → LT 三个阶段（复用 header 建立的路由和 VC）。

## Virtual Channel（VC）详解

### VC 是什么

VC（Virtual Channel，虚通道）是在同一条物理 link 上开辟的多条逻辑队列。

想象一条单车道公路（物理 link），画上虚线分成多条"虚拟车道"。flit 物理上还是共用这条路（每周期只能传一个 flit），但排队是分开的：

```
物理 link（每周期只能传 1 个 flit）
  ┌─────────────────────────────────────┐
  │  VC0 buffer: [flit][flit][flit]  ← 流量 A 的队列
  │  VC1 buffer: [flit][flit]        ← 流量 B 的队列
  │  VC2 buffer: [flit]              ← 流量 C 的队列
  └─────────────────────────────────────┘
  每个周期 SA 从某个 VC 中选一个 flit 发到物理 link 上
```

每个 VC 独立维护自己的 buffer 和 credit 计数。VC 的分配发生在 VA 阶段：header flit 到达时申请下游的一个空闲 VC，一旦分配成功，整个 packet 的所有 flit 都使用这个 VC，直到 tail flit 离开时才释放。

### 没有 VC 会出什么问题

**问题一：HOL blocking（队头阻塞）。** 只有一个队列时，队头 flit 因目的端口被占而走不了，排在后面的、去往其他端口的 flit 也全部被堵住——即使它们的目的端口是空闲的。

```
没有 VC 的情况（只有一个 FIFO）：
  队列: [flit→East（被堵）][flit→South][flit→North]
  结果: 去 South 和 North 的 flit 也走不了，被队头挡住

有 VC 的情况：
  VC0: [flit→East（被堵）]     ← 只有这个 VC 被阻塞
  VC1: [flit→South]  → 正常发送 ← 不受影响
  VC2: [flit→North]  → 正常发送 ← 不受影响
```

**问题二：协议死锁。** request 和 response 存在依赖关系——request 到了对方才产生 response，response 回来了才释放 buffer。如果混在同一队列：request 填满 buffer → response 进不来 → 没有 response 就不释放 buffer → 永久卡死。分到不同 VC 可打破这个循环。

**问题三：QoS 无法实现。** 没有 VC，小的 control packet（barrier、descriptor）会被大的 data packet 堵住，控制面延迟不可控。

### VC 数量与 buffer 的关系

**每个 VC 都需要自己独立的 buffer 空间**，这是硬面积开销。总 buffer 预算在 VC 之间分配时存在核心权衡：

```
假设 1 个 input port，buffer 总预算 = 8 个 flit slot

方案 A：1 个 VC
  VC0: [  ][  ][  ][  ][  ][  ][  ][  ]  ← 8 slot，深度大

方案 B：2 个 VC（平分）
  VC0: [  ][  ][  ][  ]  ← 4 slot
  VC1: [  ][  ][  ][  ]  ← 4 slot

方案 C：4 个 VC（平分）
  VC0: [  ][  ]  ← 2 slot
  VC1: [  ][  ]  ← 2 slot
  VC2: [  ][  ]  ← 2 slot
  VC3: [  ][  ]  ← 2 slot
```

| | VC 少（1-2 个） | VC 多（4-8 个） |
|---|---|---|
| 每个 VC 的 buffer 深度 | 深，抗 credit round-trip 能力强 | 浅，容易 credit 耗尽，link 空转 |
| HOL blocking | 严重 | 大幅缓解 |
| 协议隔离 | 不够，死锁风险高 | 充分 |
| 硬件面积 | 小 | 大（更多 buffer + 更复杂的 SA） |

**关键约束：每个 VC 的深度 ≥ credit round-trip 周期数。** 比如 credit round-trip = 3 个周期，则每个 VC 至少 3 个 slot 才能保持 link 不空转。4 个 VC × 3 slot = 12 flit 的 buffer 总预算。

### 实际怎么选

先确定 VC 数量（由协议隔离需求决定），再算每个 VC 最小深度（由 credit round-trip 决定），两者相乘 = buffer 总预算。

典型 AI NoC 选择 2-4 个 VC，每个 VC 深度 4-8 flit，总计 8-32 flit slot per input port：

- VC0：request 类流量（DMA read request、write 等）
- VC1：response 类流量（read response、data return）
- VC2（可选）：control 类流量（barrier、descriptor、sync）
- VC3（可选）：用于 deadlock escape 或特殊 QoS

更多细节参见 [VC / Deadlock](./virtual-channel-deadlock.md) 和 [Buffer Depth / Credit Sizing / Allocator Policy](./buffer-depth-credit-sizing-allocator-policy.md)。

## Switch Allocation（SA）详解

SA 是 router 流水线中**每个周期都要做的仲裁决策**：决定哪个 input port 的哪个 VC 的 flit 获得 crossbar 通路。

### 为什么需要 SA

crossbar 的每个 output port 每周期只能接受一个 flit，但可能有多个 input port 同时想往同一个 output port 发。SA 就是解决这个竞争的。

### SA 的典型两阶段流程

```
阶段 1：port 内选择（Local Arbitration）
  每个 input port 有多个 VC，先在 port 内部选出一个获胜 VC

  Input Port 0（来自 West）:
    VC0 想去 East  ──┐
    VC1 想去 South ──┼── 内部仲裁 → 选出 VC0（去 East）
    VC2 空闲       ──┘

  Input Port 1（来自 North）:
    VC0 想去 East  ──┐
    VC1 想去 North ──┼── 内部仲裁 → 选出 VC0（去 East）
    VC2 想去 East  ──┘

阶段 2：port 间竞争（Global Arbitration）
  各 input port 的获胜者按目的 output port 分组竞争

  竞争 East output port：
    Input 0 的 VC0 ──┐
    Input 1 的 VC0 ──┼── 全局仲裁 → Input 0 获胜，通过 crossbar
                     └── Input 1 本周期 switch stall（下周期重试）
```

### SA 的前提条件（缺一不可）

- 该 flit 的路由已计算完成（知道去哪个 output port）
- 如果是 header flit，VA 已完成（已分到下游 VC）
- 下游对应 VC 还有 credit（有 buffer 空间接收这个 flit）

SA 失败的后果就是 **switch stall**——flit 本周期无法前进，但不消耗 credit，下周期继续参与竞争。与 credit stall（下游 buffer 满导致完全无法发送）不同，switch stall 是竞争失败，资源本身可能是有的。

## 三种 switching

### Store-and-forward（存储转发）

下游 router 必须先收完整个 packet，才能继续转发。

优点：

- 模型简单
- 局部控制直观

缺点：

- 延迟大：每一跳都要等整个 packet 到齐
- buffer 需求高：每个 router 要能存下至少一个完整 packet

### Virtual cut-through（虚直通）

如果下游有空间容纳整个 packet，就提前开始转发。

它比 store-and-forward 更灵活，但仍然要求较大的 buffer 条件（worst case 仍需 packet 级 buffer）。

### Wormhole（虫洞交换）

header flit 先行探路，body/tail 紧随其后，packet 像"虫子"一样跨多个 router 拉开。

优点：

- buffer 极小：每个 VC 只需存放少量 flit（而非整个 packet）
- 可流水：header 已到下一跳时，body 还在上一跳传输
- 更适合面积和延迟敏感的 NoC

代价：

- packet 长期占住路径资源：被阻塞时，沿途所有 router 的 VC 和 link 都被占用
- 阻塞会通过 wormhole 链条扩散

### Wormhole 下 flit 如何保证路径一致性

这是 wormhole 最核心的机制：**只有 header flit 做路由计算，后续 body/tail flit 沿同一条路径走，因为 VC 和 output port 在 header 通过时就被"锁定"了。**

```
时间线示例（3-hop 路径：Router A → B → C → 目的地）

周期 1: Header 到达 Router A
         → RC: 计算出应走 East port
         → VA: 分配 Router B 的 VC2
         → SA: 获得 crossbar 通路
         → 从此刻起 Router A 的这个 input VC 与 East / 下游 VC2 绑定

周期 2: Header 传到 Router B（做 RC/VA/SA）
         Body0 进入 Router A（只需做 SA，路由和 VC 已确定）

周期 3: Header 传到 Router C
         Body0 传到 Router B
         Body1 进入 Router A
         ……"虫子"同时跨越三个 router

周期 N: Tail flit 离开 Router A
         → Router A 释放该 VC（其他 packet 可以使用了）

周期 N+1: Tail 离开 Router B → 释放 B 的 VC
周期 N+2: Tail 离开 Router C → 释放 C 的 VC → packet 传输完成
```

关键规则：

- **VC 是 packet 级占用**：header 分配 VC 后，整个 packet 所有 flit 都用这个 VC，直到 tail 离开才释放
- **body/tail 跳过 RC 和 VA**：只需每周期竞争 SA
- **阻塞链式扩散**：如果 header 在 Router C 被阻塞（比如下游 credit 耗尽），整条"虫子"都停住——Router B 和 A 的 VC 和 link 也被占着，其他 packet 无法使用这些资源

### VC 的状态机视角

用状态机描述 VC 在 wormhole 下的完整生命周期：

```
VC 状态机（以 Router A 的某个 input port 的 VC0 为例）

状态 1：IDLE（空闲）
  VC0 无绑定，无目的地属性
  → 等待下一个 header flit 到来

状态 2：ACTIVE（占用中）—— header 到达，RC + VA 完成
  VC0.output_port = East        ← RC 计算结果
  VC0.downstream_vc = RouterB.VC2  ← VA 分配结果
  → 从此刻起 VC0 被这个 packet 独占
  → 后续 body flit 直接复用这两个属性，只做 SA

状态 3：RELEASING —— tail flit 通过 SA 离开
  VC0.output_port = 无效
  VC0.downstream_vc = 无效
  → 回到 IDLE，可接受下一个 packet 的 header
```

**沿途每个 router 的 VC 独立释放**——tail 经过哪里，哪里的 VC 就回到 IDLE，不需要等整条路径全部传完：

```
周期 T  : RouterA.VC0 [tail]    RouterB.VC2 [body1]   RouterC.VC1 [header]
周期 T+1: RouterA.VC0 → IDLE    RouterB.VC2 [tail]     RouterC.VC1 [body0]
周期 T+2:                       RouterB.VC2 → IDLE     RouterC.VC1 [tail]
周期 T+3:                                              RouterC.VC1 → IDLE
```

靠近源端的 VC 先释放，靠近目的端的 VC 后释放——"虫尾"扫过哪里，哪里恢复自由。

这正是 wormhole 的核心权衡：**用极小的 buffer 换来流水传输，但付出的代价是阻塞时影响范围更大。** 所以需要 VC 来隔离不同流量、需要 credit 来做精确流控、需要 deadlock 预防来避免永久卡死——这三者都是为了对冲 wormhole 的这个代价。

## 为什么 wormhole 对 AI NoC 特别重要

AI 芯片里的流量通常具有：

- tile 数量多
- packet 量大
- 流量持续时间长
- producer-consumer（生产者-消费者）pipeline 明显

此时 wormhole 的低 buffer、低延迟和高吞吐优势很自然，但也意味着：

- destination ejection（目的端弹出）变慢会把阻塞一路传回源头
- bulk data 可能压住 control packet
- request / response 若混池，容易形成协议级耦合

## Packet 大小是架构参数，不只是格式参数

大 packet：

- header 开销更低
- 对连续 bulk transfer 更有利

但也会：

- 增大序列化延迟
- 加重 HOL blocking（队头阻塞）
- 拉长资源占用时间（wormhole 下"虫子"更长，占住更多 router）

小 packet：

- 更灵活
- 更适合混合 traffic

但也会：

- 增大 header 比例
- 增加 router 处理压力

## 对建模最重要的三个提醒

- 不要把 packet 当成单周期"数据块"
- 不要只看总带宽，要看 serialization latency（串行化延迟）
- 不要忽略 destination ejection 和本地 NI（Network Interface，网络接口）FIFO（先进先出队列）

## 本页结论

面向 AI dataflow 的 NoC，最重要的入口不是复杂拓扑，而是先建立 `packet -> flit -> wormhole -> 资源占用 -> 阻塞扩散` 这条主线。后面的 credit、VC、deadlock 都建立在这条主线之上。
