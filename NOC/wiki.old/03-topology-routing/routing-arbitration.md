# Routing 与 Arbitration

上级：[Topology 与 Routing](./README.md)

相关：[VC / Deadlock](../02-router-microarchitecture/virtual-channel-deadlock.md)、[Source Routing 与 Compiler-Driven NoC](./source-routing-compiler-driven-noc.md)、[Topology 量化对比](./topology-layout.md)

## 读这页前先统一几个词

- `routing`：决定 packet 该走哪条路径
- `arbitration`：决定多个竞争者里谁先拿到同一个资源
- `deterministic routing`：同一源和目的之间，总是走同一类固定路径
- `adaptive routing`：路径会根据实时拥塞情况变化
- `stall`：本周期本来想前进，但因为资源或约束没有前进成功

## Routing（路由）决定 packet（数据包）走哪条路

架构探索里，routing 的价值不只是把包送到终点，而是决定：

- 哪些链路成为热点
- 延迟分布是否可预测
- 是否容易验证
- 是否容易和编译器配合

## 三类你必须掌握的 routing

### Deterministic routing

例如 XY（先水平再垂直的维序路由）、YX、dimension-order（维序路由，按固定维度顺序转发）。

优点：

- 简单
- 可预测
- 易验证

缺点：

- 遇到热点时缺乏绕行能力

### Source routing

路径由编译器或 runtime 预先决定，header（头 flit，数据包的首个传输单元，携带路由等控制信息）携带路由信息。

它对 AI tile dataflow（数据流）很重要，因为：

- 流量往往更规整
- 编译器更容易提前规划通路
- router 本地逻辑可以更轻

### Adaptive routing

根据拥塞情况动态选路。

优点：

- 某些不规则 traffic 下更灵活

代价：

- 验证更复杂
- 乱序与 deadlock（死锁，多个数据包循环等待资源导致永久阻塞）处理更难
- 不一定适合高度编排的数据流主路径

## Arbitration（仲裁）决定谁先过

即使 routing 已经确定，多个输入争同一输出时仍需要仲裁。

而且仲裁不只发生在 switch output 上，也可能发生在 VC 分配、注入口接入、目的端 ejection（弹出）等共享资源上。

常见策略：

- round-robin（轮询）
- fixed priority（固定优先级）
- age-based（基于报文年龄）
- QoS-aware arbitration（服务质量感知仲裁）

## 为什么必须区分 stall 类型

一个 packet 没过，并不都叫“拥塞”。

至少要区分：

- credit stall（信用计数阻塞）：下游没空位
- switch stall（交换阻塞）：仲裁没赢
- routing restriction：路径本身受限

不同 stall 类型对应完全不同的优化手段。

## AI NoC 的实用建议

- 主数据流优先保持简单、可预测、可静态规划
- control / sync 不要与 bulk data（大块数据传输）共用同一低优先级路径
- 动态流量场景再评估 adaptive routing 的价值

## XY Routing 路径示例

在 4×4 mesh 中，从 (0,0) 到 (3,2) 的 XY routing 路径：

```text
  (0,0)  (1,0)  (2,0)  (3,0)
    ★ ───→ ○ ───→ ○ ───→ ○
    |      |      |      |
  (0,1)  (1,1)  (2,1)  (3,1)
    ○      ○      ○      ○
    |      |      |      |
  (0,2)  (1,2)  (2,2)  (3,2)
    ○      ○      ○      ◆
    |      |      |      |
  (0,3)  (1,3)  (2,3)  (3,3)
    ○      ○      ○      ○

XY routing: ★(0,0) → (1,0) → (2,0) → (3,0) → (3,1) → (3,2)◆
先走 X 方向 3 hop，再走 Y 方向 2 hop，总计 5 hop

YX routing: ★(0,0) → (0,1) → (0,2) → (1,2) → (2,2) → (3,2)◆
先走 Y 方向 2 hop，再走 X 方向 3 hop，总计 5 hop（相同 hop 数，不同路径）
```

XY 和 YX 的区别不在于 hop 数（都是最短路径），而在于**中间经过的链路不同**，导致不同的链路利用率分布。

## Turn Model 与 Minimal Adaptive Routing

### 为什么需要 Turn Model

- XY routing 是确定性的：给定 src 和 dst，路径唯一
- 如果某条链路拥塞，packet 无法绕行
- Adaptive routing 允许多条路径，但完全自适应会引入死锁

Turn model 提供折中：**禁止特定方向转弯，允许有限的路径选择，同时保证无死锁**。

### 常见 Turn Model（2D mesh）

在 2D mesh 中，packet 可以做 8 种转弯（N→E, N→W, S→E, S→W, E→N, E→S, W→N, W→S）。

```text
West-First Routing:
  允许的转弯: N→E, N→W, S→E, S→W, E→N, E→S
  禁止的转弯: W→N, W→S
  规则: 必须先向西走完，再做其他方向的转弯

  ┌───┐
  │   ▼
  ◀───○───▶     ○: 当前 router
  │   ▲         ▶▼◀▲: 允许的出方向
  └───┘         先走 West，再自由选 N/S/E

North-Last Routing:
  允许的转弯: N→E, N→W, S→E, S→W, E→S, W→S
  禁止的转弯: E→N, W→N
  规则: 一旦开始向北走，不能再转向其他方向

Negative-First Routing:
  允许的转弯: N→E, S→E, E→N, E→S, S→W, W→S
  禁止的转弯: N→W, W→N (同时禁止两个负方向间的转弯)
  规则: 先走所有负方向（W/S），再走正方向（E/N）
```

### Turn Model 的适应性对比

| 模型 | 禁止的转弯数 | 路径多样性 | 适合场景 |
|---|---|---|---|
| XY (dimension-order) | 4 | 最低（唯一路径） | 规则流量、易验证 |
| West-First | 2 | 中等 | 需要有限绕行能力 |
| North-Last | 2 | 中等 | 同上 |
| Negative-First | 2 | 中等 | 同上 |
| Fully Adaptive | 0 | 最高 | 高度不规则流量（需要额外死锁处理）|

## 仲裁策略量化影响

不同仲裁策略在 4×4 mesh、不同负载下的典型表现：

### 低负载（injection rate < 30% saturation）

| 策略 | Avg Latency | Tail Latency (99th) | Fairness |
|---|---|---|---|
| Round-Robin | 基准 | 基准 | 高 |
| Fixed Priority | ≈基准 | ≈基准 | 低 |
| Age-Based | ≈基准 | 略低于基准 | 极高 |

低负载时仲裁冲突少，策略差异不明显。

### 中等负载（injection rate ≈ 50% saturation）

| 策略 | Avg Latency | Tail Latency (99th) | Fairness |
|---|---|---|---|
| Round-Robin | 1.0× | 1.0× | 高 |
| Fixed Priority | 0.8×（高优先级）/ 1.5×（低优先级） | 0.5× / 3.0× | 低 |
| Age-Based | 1.0× | 0.7× | 极高 |

fixed priority 的高优先级流量延迟很低，但低优先级流量延迟急剧上升。

### 高负载（injection rate > 80% saturation）

| 策略 | Avg Latency | Tail Latency (99th) | Fairness |
|---|---|---|---|
| Round-Robin | 快速上升 | 快速上升 | 高 |
| Fixed Priority | 高优稳定 / 低优可能饥饿 | 低优极高 | 极低 |
| Age-Based | 上升较缓 | 上升较缓 | 极高 |

age-based 在高负载下表现最稳定，因为它自动惩罚"新到的"而保护"等了很久的"。

### 关键结论

- **Round-Robin**：最安全的默认选择，公平且简单
- **Fixed Priority**：适合 control 流量必须低延迟的场景，但必须确保低优先级不会饥饿
- **Age-Based**：tail latency 最优，但实现复杂度稍高（需要每个 flit 携带 age counter）
- **QoS-Aware**：结合 priority + round-robin，不同 traffic class 间用 priority，同 class 内用 round-robin

## AI Workload 场景推荐组合

| 流量类型 | 推荐 Routing | 推荐 Arbitration | 原因 |
|---|---|---|---|
| Weight / activation 搬运 | XY 或 source routing | Round-Robin | 规则流量，公平分配带宽 |
| Control / descriptor | XY | Fixed Priority（高） | 必须低延迟，否则 pipeline stall |
| DMA read response | XY | Priority（中-高） | response 延迟直接影响 compute |
| Partial sum reduce | XY 或 source routing | Round-Robin | 多源汇聚，公平性重要 |
| MoE dispatch | West-First 或 adaptive | Age-Based | 不规则流量，需绕行和公平 |
| Barrier / sync | XY | Fixed Priority（最高） | 极小 packet，延迟极敏感 |

### 一个常见的混合配置

```text
Traffic Class     VC     Routing    Arbitration (inter-class)  Arbitration (intra-class)
─────────────────────────────────────────────────────────────────────────────────────────
Control/Barrier   VC0    XY         Highest priority           Round-Robin
DMA Response      VC1    XY         High priority              Round-Robin
Data Stream       VC2    XY/Source  Medium priority             Round-Robin
Bulk DMA Write    VC3    XY         Low priority               Round-Robin
```

## 本页结论

routing 决定全局路径分布，arbitration 决定局部竞争结果。做 NoC 架构探索时，如果你只改 link width 却不分析 routing 与仲裁，通常只能看到表面现象。对 AI 加速器，推荐从 XY + Round-Robin 出发，再针对 control 流量加 priority、针对不规则流量评估 turn model。
