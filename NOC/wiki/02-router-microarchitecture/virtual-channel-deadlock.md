# VC / Deadlock

上级：[Router 微架构](./README.md)

相关：[Packet / Flit / Wormhole](./packet-flit-wormhole.md)、[Credit / Backpressure](./credit-backpressure.md)、[Routing 与 Arbitration](../03-topology-routing/routing-arbitration.md)、[检查清单](../06-reference/checklists.md)

## 为什么 VC 不是"可有可无的高级功能"

没有 VC（Virtual Channel，虚通道）时，多个 packet 共用一个物理队列。  
只要队头 packet 卡住，后面的 packet 即使目的地完全不同，也会被一并堵住（HOL blocking）。

VC 的基本机制和 buffer 关系已在 [Packet / Flit / Wormhole](./packet-flit-wormhole.md) 中详述，本页聚焦于 VC 的四个核心作用以及 deadlock 的成因与预防。

## VC 的四个核心作用

### 1. 降低 HOL blocking

通过把不同 packet 放进不同逻辑队列，减少错误耦合。（详见 [packet-flit-wormhole 中的 VC 详解](./packet-flit-wormhole.md#virtual-channelvc详解)）

### 2. 隔离 message class

不同类型的流量放在不同 VC 中，互不干扰：

- request（读写请求）
- response（读响应、数据返回）
- control（barrier、descriptor、sync）
- stream / bulk data（tile-to-tile 的大块数据传输）

如果这些流量共池，"小消息被大流量淹没"几乎必然发生。

### 3. 为 QoS 提供抓手

控制面、同步消息、低延迟请求，往往需要和 bulk data 分离。有了 VC，SA（Switch Allocation）仲裁时可以对不同 VC 给予不同优先级。

### 4. 降低 deadlock 风险

VC 不是自动防死锁，但它提供了**协议分层和资源依赖切断**的工具——这是后面详述的重点。

## Deadlock 的本质

deadlock 不是"堵了一会儿"，而是**资源依赖形成了闭环，系统永远无法前进**：

- 每个 packet 都持有一部分资源（占着沿途 router 的 VC 和 buffer slot）
- 同时等待别的 packet 释放资源（需要下游 VC 的空位）
- 所有参与者互相等待，没有任何一方能先退让
- 和暂时拥塞不同：拥塞会随时间缓解，deadlock 永远不会

## 两类你必须区分的 deadlock

### Routing deadlock（路由死锁）

**由路径资源依赖环导致。** 当多个 packet 的路径在 VC/buffer 资源上形成循环等待时发生。

具体例子（2×2 mesh，只有 1 个 VC 的情况）：

```
四个 packet 同时在一个 2×2 mesh 中传输：

  R0 ──→ R1
  ↑       │
  │       ↓
  R3 ←── R2

  Packet A: 在 R0，占着 R0 的 VC，想去 R1 → 但 R1 的 VC 被 B 占满
  Packet B: 在 R1，占着 R1 的 VC，想去 R2 → 但 R2 的 VC 被 C 占满
  Packet C: 在 R2，占着 R2 的 VC，想去 R3 → 但 R3 的 VC 被 D 占满
  Packet D: 在 R3，占着 R3 的 VC，想去 R0 → 但 R0 的 VC 被 A 占满

  A 等 B → B 等 C → C 等 D → D 等 A → 闭环！永远无法前进
```

关键条件：每个 router 只有 1 个 VC，被 wormhole packet 占住后没有替代空间。如果有第二个 VC，packet D 可以用 R0 的另一个 VC，环就被打破了。

### 三种 routing deadlock 的预防方法

#### 方法一：Dimension-order routing（维序路由，如 XY routing）

**原理：通过限制路由方向的先后顺序，使路径资源依赖不可能形成环。**

```
XY routing 规则：所有 packet 先沿 X 方向走完，再沿 Y 方向走

合法路径：                    非法路径（XY routing 禁止）：
  → → → ↓ ↓                   ↓ → ↓ →
  先 X 后 Y ✓                  Y 和 X 交替 ✗

为什么不会死锁？
  X 方向的资源只被"正在走 X"的 packet 占用
  Y 方向的资源只被"已经走完 X、正在走 Y"的 packet 占用
  一个 packet 永远不会从 Y 回到 X → 不可能形成环

  本质：给资源加了全序（X 阶段 < Y 阶段），packet 只能沿序号递增的方向获取资源
```

代价：路径选择完全固定，不能绕开拥塞。某些 (源, 目的) 对的路径必须经过热点 router。

#### 方法二：Turn model（转向模型）

**原理：不完全禁止所有方向，而是只禁止特定的"转弯"组合来打破可能形成的环。**

```
2D mesh 中 packet 可以做 8 种转弯：
  东→北  东→南  西→北  西→南
  北→东  北→西  南→东  南→西

形成环至少需要 4 次转弯（顺时针或逆时针绕一圈）
只要禁止其中任意一种转弯，环就不完整 → 无死锁

例：West-First routing
  规则：如果 packet 需要往 West 走，必须先走完 West，再走其他方向
  禁止：从其他方向转向 West（即 北→西 和 南→西 被禁止）
  效果：打破了逆时针环路的可能性

  ┌──→──→──┐
  ↑        ↓    顺时针环需要 西→北 这个转弯
  └──←──←──┘    如果禁止 北→西 和 南→西，逆时针环断裂
                 再选择性禁止一个顺时针转弯即可

例：North-Last routing
  规则：往 North 走必须是最后一步
  禁止：北→东 和 北→西（到了 North 就不能再转别的方向）
```

代价：比 XY routing 灵活一些（部分路径有多条选择），但仍然不是完全自适应。

#### 方法三：Escape VC（逃逸虚通道）

**原理：大部分 VC 可以使用任意路由（包括自适应路由），但保留一个专用 VC 只走确定无死锁的路由（如 XY）。当自适应路由陷入潜在死锁时，packet 可以"逃"到 escape VC 中，用安全路由脱困。**

```
假设每个 router 有 3 个 VC：

  VC0: 自适应路由（可以绕路避拥塞，但有死锁风险）
  VC1: 自适应路由（同上）
  VC2: Escape VC（只走 XY routing，保证无死锁）

正常情况：
  packet 在 VC0 或 VC1 上用自适应路由，享受负载均衡的好处

潜在死锁时：
  packet 从 VC0/VC1 切换到 VC2
  在 VC2 上用 XY routing 继续前进
  → 因为 XY routing 无死锁，所以 escape VC 保证 forward progress

关键约束：
  一旦进入 escape VC，就不能再回到自适应 VC（否则可能重新陷入环）
  escape VC 是"单向逃生通道"
```

代价：escape VC 的带宽被保留，不能被自适应流量使用；如果频繁触发逃逸，说明自适应路由的效果不好。

### Protocol deadlock（协议死锁）

**由不同消息类型之间的依赖关系形成环。** 即使 routing 本身无死锁，消息类型之间的依赖也可能导致永久卡住。

这和 routing deadlock 的区别：routing deadlock 是"路径资源"形成环；protocol deadlock 是"消息因果关系"形成环。

#### AI NoC 中的具体例子

```
场景：request 和 response 共用同一个 VC

  Tile A 发 read request 给 Tile B（经过 R0 → R1 → R2）
  Tile B 收到 request 后产生 read response 发回 Tile A（经过 R2 → R1 → R0）

  如果 request 和 response 在同一个 VC 中：

  R1 的 VC 状态：
    [A的request flit][A的request flit][B的response flit 想进来]
    → request 占满了 VC buffer
    → response 进不来
    → 但 A 在等 response 回来才会释放后续资源
    → A 的 request 占着 R0 的 VC 不放
    → response 永远进不来 → 死锁！

  解法：request 走 VC0，response 走 VC1
    → response 有独立的 buffer 空间
    → 不会被 request 堵住
    → 依赖环被切断
```

#### 更隐蔽的 AI NoC protocol deadlock 场景

```
场景：DMA response 被 reduce 流量堵住

  Tile A 发 DMA read request → HBM 控制器
  同时，多个 tile 的 partial sum reduce 流量正在经过同一段路径
  reduce 流量占满了 VC buffer
  DMA response 回不来 → Tile A 拿不到数据 → Tile A 不产生 partial sum
  → 但 reduce 在等 Tile A 的 partial sum → 死锁！

  本质：reduce 依赖 Tile A 的计算结果，Tile A 的计算依赖 DMA response，
        DMA response 被 reduce 堵住 → 三方循环等待

  解法：DMA response 和 reduce 流量走不同的 VC
```

## 为什么 credit 不能防死锁

这是最常见的错误理解。区分清楚：

```
Credit 防的是：overflow（缓冲区溢出）
  → 保证 sender 不会发超过 receiver buffer 容量的 flit
  → 是一对一的、逐跳的安全机制

Credit 防不了的是：circular wait（循环等待）
  → 四个 packet 各自合法地占住一个 VC（没有 overflow）
  → 但互相等对方释放 → 永远等下去
  → credit counter 全部 = 0，但不是因为"发多了"，而是因为"对方不走"

类比：
  credit 像高速公路收费站的通行证——防止车太多挤爆公路
  deadlock 像四辆车在十字路口互相让——每辆车都合法停着，但没人能先走
  通行证解决不了十字路口的僵局
```

## AI NoC 的实用 VC/message class 分层方案

### 为什么至少需要分这几层

```
AI dataflow NoC 中的消息类型及其依赖关系：

  control（barrier/descriptor/sync）
    → 触发 DMA 或 compute 开始
    → 如果被堵，整个 pipeline 阶段无法启动

  request（DMA read request / write request）
    → 需要到达 HBM 控制器或远端 SRAM
    → 产生 response

  response（read response / data return）
    → 是 request 的因果后继
    → 如果 response 和 request 共用资源，存在 protocol deadlock 风险

  stream（tile-to-tile activation / partial sum / reduce）
    → 大流量，容易淹没其他类型
    → 如果堵住 control 或 response，整个系统可能停转
```

### 四层分离方案与 VC 映射

```
最小安全分层（2 个 VC 就能实现基本隔离）：
  VC0: request + control
  VC1: response + stream
  → 打破 request/response 依赖环，但 control 可能被 request 挤压

推荐分层（3-4 个 VC）：
  VC0: request（DMA read/write request）
  VC1: response（read response、data return）
  VC2: control（barrier、descriptor、sync）
  VC3（可选）: stream（tile-to-tile bulk data）

  依赖关系和隔离效果：
    control ──触发──→ request ──产生──→ response
       ↑                                    │
       └────── tile 收到 response 后 ───────┘
              发出下一阶段 control

    每个环节在不同 VC 中 → 不会互相堵 → 无 protocol deadlock
```

### 分层的原则

- **有因果依赖的消息类型必须在不同 VC 中**：request 和 response 是最典型的
- **control 最好独立**：control 通常很小但对时序极敏感，被大流量堵住会让整个调度停转
- **面积允许时再分 stream**：stream 流量最大，独立 VC 可防止它淹没其他类型

## AI NoC 中常见的错误理解

| 错误认知 | 实际情况 |
|---------|---------|
| credit 能防死锁 | credit 只防 overflow，不防 circular wait |
| VC 数量越多越好 | VC 越多每个越浅，可能 credit 耗尽导致 link 空转；面积和 SA 复杂度也增长 |
| 没有 cache coherence 就没有 protocol deadlock | AI NoC 的 request/response/control/reduce 之间同样存在因果依赖环 |
| XY routing 就够了不需要想 deadlock | XY routing 只解决 routing deadlock；protocol deadlock 仍需 VC 分层 |
| 死锁很少发生所以不用管 | 死锁一旦发生就是永久卡死，不是概率问题而是正确性问题 |

## 建模时需要显式记录的状态

| 状态 | 用途 |
|------|------|
| 每个 input VC 的 occupancy | 判断是否接近满载、是否有 backpressure |
| VC allocation 状态（IDLE / ACTIVE） | 追踪哪些 VC 被 packet 占用 |
| packet 当前占用的下游资源（output_port + downstream_vc） | 检查是否存在资源依赖环 |
| 各 message class 的 VC 映射 | 验证 request/response/control 是否正确隔离 |
| 是否存在循环等待路径 | 可通过构建 resource wait graph（资源等待图）检测：每个被占用的 VC 是一个节点，"A 等 B 释放"画一条边，如果图中有环就是死锁 |

## 本页结论

VC 的本质不是"把链路切成几份"，而是给 NoC 提供资源隔离与协议组织能力。  
Deadlock 分两类：routing deadlock（路径资源环）靠路由约束解决；protocol deadlock（消息因果环）靠 VC 分层解决。两者都必须在设计阶段显式处理——deadlock 不是性能问题，是正确性问题。
