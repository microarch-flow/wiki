# 多网络组织（Multi-Network / Multi-Plane NoC）

上级：[AI Dataflow 系统视角](./README.md)

相关：[NoC 分类框架](../01-overview/taxonomy.md)、[Collective Communication](./collective-communication.md)、[QoS、公平性与 Stall Taxonomy](../05-modeling-evaluation/qos-fairness-stall-taxonomy.md)、[Broadcast / Multicast / Reduction 网络](./broadcast-multicast-reduction-network.md)

## 为什么真实 AI 芯片不是只有一张 NoC

一个 AI 加速器上同时存在多种截然不同的流量：

| 流量类型 | 带宽需求 | 延迟敏感度 | 典型大小 | 频率 |
|---|---|---|---|---|
| activation / weight 搬运 | 极高 | 中 | 大块（KB-MB） | 持续 |
| partial sum reduce | 高 | 高 | 中等 | 持续 |
| DMA descriptor / command | 低 | 高 | 小（几十 B） | 频繁 |
| barrier / semaphore | 极低 | 极高 | 几 B | 间歇 |
| debug / trace / profiling | 低 | 不敏感 | 可变 | 后台 |

如果所有流量共用一张 NoC：

- 大块 data transfer 会占满链路，饿死小而紧急的 control 消息
- control 消息被阻塞会导致整条 pipeline stall，尾延迟急剧上升
- 不同 traffic class 的死锁域耦合在一起，死锁避免更复杂
- QoS 只能靠 VC 隔离，但 VC 数量有限且共享物理线材

所以真实 AI 芯片几乎都采用某种形式的多网络设计。

## 常见的网络分离方式

### 按功能分

```text
┌─────────────────────────────────────────┐
│              AI Accelerator             │
│                                         │
│  ┌───────────┐  Data NoC (mesh)         │
│  │ tile  tile│──────────────────────     │
│  │ tile  tile│                     │    │
│  └───────────┘                     │    │
│       │              ┌─────────────┘    │
│       │              │                  │
│  Control NoC (ring)  │  DMA NoC (mesh)  │
│  ─────────────────   │  ────────────    │
│                      │                  │
│  Reduction NoC (tree)│  Sync NoC (bus)  │
│  ────────────────────┘  ────────────    │
└─────────────────────────────────────────┘
```

典型分离：

| 网络 | 拓扑选择 | 链路宽度 | 职责 |
|---|---|---|---|
| **Data NoC** | mesh / concentrated mesh | 宽（256-512 bit） | activation、weight 的大块搬运 |
| **Control NoC** | ring / bus / 窄 mesh | 窄（32-64 bit） | command、descriptor、event、配置 |
| **DMA / Memory NoC** | mesh / tree | 宽（256+ bit） | HBM ↔ SRAM 的大块数据搬运 |
| **Reduction NoC** | tree / 专用 overlay | 中等 | partial sum reduce、all-reduce |
| **Synchronization NoC** | bus / ring | 极窄 | barrier、credit、semaphore |
| **Debug / Profiling NoC** | daisy-chain / ring | 窄 | trace 采集、performance counter 读取 |

并非每个芯片都有 6 张网络。常见的最小配置是 **data + control 两张**，复杂设计可能有 3-4 张。

### 按方向分

某些设计不按功能分网络，而是按数据流方向分：

- **East-West network**：同行 tile 之间的水平数据流
- **North-South network**：跨行的垂直数据流
- **DMA network**：tile 与外部存储之间

这种分法在 systolic array 风格的加速器中较常见。

## 多网络 vs 多 VC：两种隔离策略的取舍

将不同 traffic class 隔离开有两种主要方式：

### 方式一：物理隔离（多张独立网络）

每种 traffic class 有自己的物理链路、router、buffer。

优点：

- 完全隔离，互不干扰
- 每张网络可以独立优化拓扑、链路宽度、router 规格
- 死锁域完全独立
- 建模简单，每张网络独立分析

缺点：

- 面积开销大（多套 router + 链路）
- 布线资源翻倍或更多
- 低利用率时资源浪费（某张网络空闲但带宽不能借给另一张）

### 方式二：逻辑隔离（单网络 + 多 VC / 多 virtual network）

共享物理链路和 router，用 VC（virtual channel）或 virtual network 隔离不同 traffic class。

优点：

- 面积小，共享物理资源
- 带宽可以在 traffic class 之间弹性共享
- 布线压力小

缺点：

- HOL blocking（队头阻塞）风险：一个 VC 满了可能阻塞同一物理链路上的其他 VC
- QoS 保障弱于物理隔离
- 死锁分析更复杂（VC 之间的依赖关系）
- 建模需要精确模拟 VC 仲裁行为

### 实践中的混合方案

大多数 AI 芯片采用混合策略：

- **data 和 control 物理隔离**（带宽差异太大，必须分开）
- **data 内部用多 VC 区分优先级**（如 DMA read response vs write data）
- **reduction 可能用专用网络或 data NoC 上的专用 VC**（取决于 reduce 频率）
- **debug 用极简的 daisy-chain 或 scan chain**（不值得占用 NoC 资源）

## 对建模的影响

### 单网络建模的风险

如果建模时只用一张 NoC 模拟所有流量：

- 容易低估 control 消息延迟（被 data 流量淹没）
- 容易低估 tail latency（不同 traffic class 的干扰被平均掉）
- 容易高估 data 带宽利用率（实际要给 control 留余量）
- 死锁分析不准确

### 多网络建模的最低要求

第一版 simulator 至少应该支持：

- 定义多张独立网络，每张有自己的拓扑、链路宽度、router 参数
- 每个 traffic source 指定走哪张网络
- 分别统计每张网络的利用率、延迟、拥塞
- 观察 data 和 control 的交互效应（如 control 延迟导致 data pipeline stall）

### 架构探索时的关键问题

- 哪些 traffic class 必须物理隔离？哪些可以用 VC 隔离？
- control NoC 的延迟上界是多少？（它决定了 pipeline stall 的最坏情况）
- data NoC 需要几个 VC？每个 VC 服务什么流量？
- reduction 流量是用专用网络还是走 data NoC 的专用 VC？
- 多张网络的总面积和布线成本是否可接受？

## 与 QoS 的关系

多网络设计本身就是一种粗粒度的 QoS 机制：

- 物理隔离 = 最强的 QoS 保障（互不影响）
- 每张网络内部可以再用 VC + priority 做细粒度 QoS

但要注意：多网络不能解决所有 QoS 问题。即使 data 和 control 分开了，data NoC 内部仍然可能有不同优先级的流量互相干扰（如 DMA read response 和 activation streaming）。

## 本页结论

多网络组织是 AI 加速器 NoC 区别于传统 SoC 互连的重要特征之一。建模时不要把所有流量塞进一张 NoC——至少要区分 data 和 control 两张网络。架构探索时，"需要几张网络"和"每张网络什么拓扑/带宽"是与拓扑选择同等重要的设计决策。
