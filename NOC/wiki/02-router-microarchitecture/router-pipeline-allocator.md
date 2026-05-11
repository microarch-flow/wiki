# Router Pipeline 与 Allocator

上级：[Router 微架构](./README.md)

相关：[Packet / Flit / Wormhole](./packet-flit-wormhole.md)、[Credit / Backpressure](./credit-backpressure.md)、[VC / Deadlock](./virtual-channel-deadlock.md)

## 为什么这一页重要

很多人能理解 wormhole（虫洞交换）和 credit（信用计数），但一到真正实现 router（路由器），就会卡在：

- 每周期到底先做什么
- header 和 body 的处理为什么不同
- VA 与 SA 的边界在哪里
- 哪些 stall（停顿）属于 allocator（分配器），而不是属于 link（链路）或 buffer（缓冲区）

这一页的目标是把 router 从"概念图"推进到"可实现模型"。

## 一个典型的五阶段 pipeline

| 阶段 | 全称 | 做什么 | 谁经历 |
| --- | --- | --- | --- |
| RC | Route Computation（路由计算） | 根据 header 中的目的地址计算 output port | 仅 header |
| VA | VC Allocation（虚通道分配） | 在下游 router 分配一个空闲 VC | 仅 header |
| SA | Switch Allocation（开关分配） | 仲裁竞争 crossbar 通路 | 所有 flit |
| ST | Switch Traversal（开关穿越） | flit 穿过 crossbar 到 output port | 所有 flit |
| LT | Link Traversal（链路穿越） | flit 在物理 link 上传到下游 router | 所有 flit |

关键区别：**header 走 5 个阶段（RC→VA→SA→ST→LT），body/tail 只走 3 个阶段（SA→ST→LT）。**

并不是所有实现都严格分成五拍，但这个分解足够作为 simulator 和架构分析的主心骨。

### 一个 flit 过一个 router 要几个周期？

```
Header flit:  RC(1) + VA(1) + SA(1) + ST(1) + LT(1) = 5 周期
              （VA 可能因为没有空闲 VC 而等待多个周期）
              （SA 可能因为竞争失败而等待多个周期）

Body/Tail flit: SA(1) + ST(1) + LT(1) = 3 周期
                （SA 可能因为竞争失败而等待）

理想情况下（无 stall）：
  header 花 5 周期穿过一个 router
  之后每个 body/tail flit 每周期过一个（SA→ST→LT 流水起来后每周期吐一个）
```

## 端到端时序图

一个 4-flit packet（header + body0 + body1 + tail）穿过单个 router 的时序：

```
周期:   1    2    3    4    5    6    7    8
       ─── ─── ─── ─── ─── ─── ─── ───
Header: RC   VA   SA   ST   LT
Body0:            等待  等待  SA   ST   LT
Body1:                  等待  等待  SA   ST   LT → 周期9
Tail:                         等待  等待  SA   ST → LT 周期9-10

说明：
  - Body0 在周期 1-2 等待（header 还没完成 VA，路径未建立）
  - Body0 在周期 5 开始 SA 时，header 的 ST 腾出 crossbar → body0 可以用
  - 之后每周期一个 flit 流水通过 SA→ST→LT
```

**多 hop 路径上的流水并行**（header 穿过 Router A → B → C）：

```
周期:   1    2    3    4    5    6    7    8    9   10
       ─── ─── ─── ─── ─── ─── ─── ─── ─── ───
Router A:
  Header: RC   VA   SA   ST   LT
  Body0:                  等   SA   ST   LT
  Body1:                       等   SA   ST   LT

Router B:                          ← header 到达
  Header:                     RC   VA   SA   ST   LT
  Body0:                                等   SA   ST   LT

Router C:                                    ← header 到达
  Header:                               RC   VA   SA   ST   LT

关键观察：
  - 周期 6 时：header 在 B 做 RC，body0 在 A 做 SA — 并行进行
  - 周期 8 时：header 在 C 做 RC，body0 在 B 做 SA，body1 在 A 做 SA
  - 这就是 wormhole 的流水效果："虫子"同时跨越多个 router
```

## RC：Route Computation

作用：

- 读取 header 中的目的地址
- 决定候选输出端口
- 生成下一跳路由信息

对 deterministic routing（确定性路由，如 XY routing）来说，RC 是纯组合逻辑——根据当前位置和目的地直接算出方向：

```
XY routing 的 RC 逻辑：
  if dst_x > cur_x → output_port = East
  if dst_x < cur_x → output_port = West
  if dst_x == cur_x and dst_y > cur_y → output_port = North
  if dst_x == cur_x and dst_y < cur_y → output_port = South
  if dst_x == cur_x and dst_y == cur_y → output_port = Local（到达目的地）
```

对 source routing（源路由）来说，RC 更简单——直接从 header 的路由字段中读取下一跳方向，不需要计算。

关键点：

- RC 只对 header 生效
- body/tail 复用 header 已建立的 output_port，跳过 RC

## VA：Virtual Channel Allocation

### 做什么

为 header 在目标 output port 的下游 router 分配一个空闲 VC。这是 wormhole + VC 体系的核心步骤，因为 packet 要持续占用这个 VC 直到 tail 离开。

### 具体流程

```
Header 完成 RC 后知道要去 East port
→ VA 检查 East 方向下游 router 有哪些 VC 空闲

情况 1：有空闲 VC
  下游 VC0 空闲 → 分配成功
  → 记录绑定关系：当前 input VC → East output port → 下游 VC0
  → 进入 SA 阶段

情况 2：所有下游 VC 都被占用
  → VA 失败，header 停在 VA 阶段等待（VA stall / VC_UNAVAILABLE）
  → 后续 body/tail 也全部等待（header 没走，谁都走不了）
  → 每周期重新尝试 VA，直到某个下游 VC 被 tail 释放
```

### 多个 header 同时想要同一个下游 VC

```
Input Port 0 的 header 想去 East，需要下游 VC
Input Port 2 的 header 也想去 East，也需要下游 VC

如果下游只剩 1 个空闲 VC：
  VA 内部仲裁 → 只有一个 header 获得分配
  另一个 header 继续等（VC_UNAVAILABLE）
  
  VA 仲裁策略通常是 round-robin 或 fixed priority
```

### VA 和 SA 的本质区别

| | VA（VC Allocation） | SA（Switch Allocation） |
|---|---|---|
| 分配什么 | 下游 router 的一个 VC（逻辑通道） | 本 router crossbar 的一个通路（物理通道） |
| 谁参与 | 仅 header flit | 所有 flit（header/body/tail） |
| 占用时长 | 整个 packet 生命周期（header 到 tail） | 仅当前周期（每个 flit 独立竞争） |
| 失败后果 | packet 卡在 VA 阶段，无法前进 | flit 等一个周期后重试 |
| 类比 | 申请一个停车位的长期使用权 | 每个路口的绿灯放行权 |

**一句话区分：VA 是"长期占位"，SA 是"每周期放行"。**

## SA：Switch Allocation

SA 的两阶段仲裁机制和详细流程已在 [Packet / Flit / Wormhole 的 SA 详解](./packet-flit-wormhole.md#switch-allocationsa详解) 中展开。这里只强调与 pipeline 相关的要点。

### SA 的前提条件

一个 flit 要参与 SA 竞争，必须同时满足：

- 路由已确定（RC 已完成）
- 如果是 header：VA 已完成（已分到下游 VC）
- 下游对应 VC 有 credit（有 buffer 空间接收）

缺少任何一个条件，该 flit 本周期不参与 SA：

```
条件检查流程：
  RC done?  ── No → 还在做路由计算，不参与 SA
       │
      Yes
       │
  是 header?  ── Yes → VA done? ── No → 还在等 VC 分配，不参与 SA
       │                    │
      No（body/tail）       Yes
       │                    │
       ├────────────────────┘
       │
  credit > 0?  ── No → credit stall（下游满了）
       │
      Yes
       │
  → 参与 SA 仲裁 → 赢了: 通过  /  输了: switch stall（下周期重试）
```

## ST：Switch Traversal

SA 获胜的 flit 穿过 router 内部的 crossbar（交叉开关矩阵），从 input port 到 output port。

对高层模型来说，ST 是 1 个周期的内部移动。第一版 simulator 不必把 crossbar 内部再拆细，但应保留这一阶段在时序上的存在感——它占用 crossbar 资源，影响其他 flit 在同周期能否通过。

## LT：Link Traversal

flit 从当前 router 的 output port 出发，在物理 link 上传输到下游 router 的 input port。

第一版假设：每条链路每周期最多传 1 个 flit，LT = 1 周期。

如果以后要做更细粒度建模，需要考虑：

- **多周期长链路**：物理距离远的 link 需要插入流水寄存器，LT > 1 周期
- **phit 拆分**：flit 宽度 > link 宽度时，一个 flit 需要多周期传输
- **pipeline link**：长链路内部分多级流水，每级之间用寄存器隔开

## Header、Body、Tail 为什么不能混着看

```
             经历的阶段        资源行为             状态影响
  Header:   RC→VA→SA→ST→LT   申请路由+申请VC+竞争通路   建立绑定关系
  Body:        SA→ST→LT      只竞争通路              消耗带宽和buffer
  Tail:        SA→ST→LT      竞争通路+释放VC          解除绑定关系
```

### Header

- 决定路径（RC 结果写入 VC 状态）
- 决定 VC（VA 建立 input VC → output port → downstream VC 的绑定）
- 决定 message class 的资源归属——即这个 VC 接下来"属于"哪种消息类型（request/response/control 等），直到 tail 释放

### Body

- 跟随 header 已建立的通路前进
- 每周期独立竞争 SA（可能被其他 flit 抢占）
- 主要消耗的是带宽和 buffer slot

### Tail

- 表示 packet 结束
- **触发 VC 释放**：tail 离开当前 router 时，该 router 的 input VC 从 ACTIVE 回到 IDLE
- 如果 simulator 里 tail 不显式释放 VC，那个 VC 就永远被占着——新的 packet 进不来

## Allocator 的两类职责

### VC Allocator

解决"我能不能拿到下游逻辑通道"的问题。

- 输入：哪些 header 需要下游 VC，哪些下游 VC 空闲
- 输出：每个 header 分配到哪个下游 VC（或等待）
- 特点：**长期资源占用**——分配后整个 packet 持续使用，直到 tail 释放

### Switch Allocator

解决"本周期多个候选里谁先通过物理 crossbar"的问题。

- 输入：哪些 flit 满足条件（RC done、VA done、credit > 0）
- 输出：每个 output port 本周期让哪个 flit 通过
- 特点：**每周期瞬时竞争**——每个周期独立决策，不影响下一周期

### 两者的协作关系

```
Header 到达 → RC（1周期）→ VA（可能多周期）→ SA（可能多周期）→ ST → LT
                            ↑                    ↑
                         VC Allocator          Switch Allocator
                         分配下游 VC            仲裁 crossbar 通路
                         （长期占位）            （每周期放行）

Body/Tail 到达 → 跳过 RC 和 VA → SA（可能多周期）→ ST → LT
                                   ↑
                                Switch Allocator
                                （每周期放行）
```

## Stall 分类与诊断

Router 内部的 stall 可以精确分为四类：

| Stall 类型 | 卡在哪个阶段 | 原因 | 诊断信号 |
|-----------|------------|------|---------|
| RC_BLOCKED | RC | 路由计算未完成（对 1 周期 deterministic routing 几乎不会发生） | — |
| VC_UNAVAILABLE | VA | 下游 output port 的所有 VC 都被其他 packet 占用 | 下游 VC 全部处于 ACTIVE 状态 |
| CREDIT_STALL | SA 前 | 下游 VC 的 buffer 满了，credit = 0 | credit counter = 0 |
| SWITCH_CONFLICT | SA | credit > 0，但 SA 仲裁竞争失败 | SA grant 未命中 |

**诊断优先级：先看 VC_UNAVAILABLE 和 CREDIT_STALL 的比例，再看 SWITCH_CONFLICT。** 前两者说明系统资源不足或消费太慢（结构性问题），后者是正常竞争（通常可接受）。

```
如果 VC_UNAVAILABLE 占比高：
  → VC 数量不够，或某些 VC 被长 packet 长期占用
  → 优化：增加 VC 数量、减小 packet size、加快 tail 释放

如果 CREDIT_STALL 占比高：
  → 下游消费不够快或 buffer 太浅
  → 优化：加深 buffer、加快下游消费、减少注入速率

如果 SWITCH_CONFLICT 占比高：
  → 多个流量汇聚到同一 output port
  → 优化：调整 routing 分散流量、增加 link 带宽
```

## 推荐的 Router Tick 顺序

第一版 simulator 可以按下面顺序实现每个周期的处理：

```
1. 接收：处理从上游 link 到达的 flit，写入 input buffer
2. 接收：处理从下游返回的 credit，更新 credit counter
3. RC：对新到达的 header 做路由计算
4. VA：对已完成 RC 的 header 尝试分配下游 VC
5. SA：对满足条件的 flit 做 switch 仲裁
6. ST：SA 获胜的 flit 穿过 crossbar
7. LT：从 output buffer 发到下游 link
8. Credit 返回：对被 pop 出 input buffer 的 slot，向上游发送 credit
9. Ejection：对 local port 到达的 flit 交付给 tile
```

### 为什么顺序重要

```
错误示例 1：先发 credit 再处理到达
  → 可能对还没到达的 flit 提前返回 credit → 状态不一致

错误示例 2：先做 SA 再做 VA
  → header 还没拿到 VC 就参与 SA 竞争 → 不知道往哪个下游 VC 发
  → SA 获胜后发现没有合法的下游 VC → 逻辑错误

错误示例 3：先做 LT 再做 ST
  → flit 还没穿过 crossbar 就发到了下游 link → 数据还在 input buffer
```

关键不是唯一正确顺序，而是必须保证：**RC → VA → SA → ST → LT 的因果链不被打破，credit 更新和 buffer 状态保持一致。**

## Speculative Allocator（投机分配器）

第一版 simulator 不需要实现，但值得了解概念。

标准流程中，SA 必须等 VA 完成后才能开始——如果 VA 多等了 1 周期，整条 pipeline 就多 stall 1 周期。

Speculative allocator 的思路：**让 SA 和 VA 在同一周期并行进行。** SA 先"乐观地假设 VA 会成功"进行仲裁，如果 VA 最终成功了则直接通过，如果 VA 失败了则取消本周期的 SA 结果。

```
标准流程（串行）：
  周期 1: RC
  周期 2: VA        ← 等 VA 结果
  周期 3: SA        ← 等 VA 完成才开始
  周期 4: ST
  周期 5: LT
  → header 过 router 需要 5 周期

Speculative（并行 VA+SA）：
  周期 1: RC
  周期 2: VA + SA   ← 同时进行
          如果 VA 成功 → SA 结果有效
          如果 VA 失败 → SA 结果作废，下周期重来
  周期 3: ST
  周期 4: LT
  → header 过 router 最快 4 周期（省了 1 周期）
```

代价：逻辑更复杂，需要处理"投机失败后回滚"的情况。在高流量场景下 VA 经常失败时，speculative 的收益会下降。

## 你在 simulator 里至少要建哪些状态

| 状态 | 说明 |
|------|------|
| input buffer occupancy | 每个 VC 当前存了多少 flit |
| VC state（IDLE / RC / VA / ACTIVE） | 每个 input VC 当前处于哪个阶段 |
| VC 绑定关系（output_port + downstream_vc） | header 完成 VA 后写入，tail 离开时清除 |
| output credit table | 对每个下游 VC 的剩余 credit 计数 |
| output VC availability | 下游 router 各 VC 是否空闲（用于 VA 判断） |
| per-cycle SA request / grant | 每周期哪些 flit 参与竞争、谁获胜 |
| stall 分类计数器 | 分别统计 VC_UNAVAILABLE / CREDIT_STALL / SWITCH_CONFLICT 的周期数 |

## 常见实现误区

| 误区 | 为什么有问题 |
|------|-------------|
| credit 在 flit 到达下游时立即返还 | credit 应在 buffer slot 释放时返还，不是到达时 |
| 不区分 header 与 body 的资源申请行为 | body 不做 RC/VA，如果让 body 也走 VA 会浪费周期并可能分配多余 VC |
| tail 不显式释放 VC | VC 永远处于 ACTIVE，新 packet 无法使用，等价于资源泄漏 |
| 只做 SA 不做 VA | 没有 VC 分配逻辑，wormhole 下无法正确跟踪 packet 的下游通路 |
| 只统计总延迟不统计 allocator stall | 无法区分瓶颈在 VA 还是 SA，优化方向不同 |

## 架构分析里应该问什么

- allocator stall 在总 stall 里占比多大？如果占比很小，说明瓶颈在 link 带宽或端点消费
- 是 VC_UNAVAILABLE 为主还是 SWITCH_CONFLICT 为主？前者需要更多 VC 或更小 packet，后者需要分散 routing
- 不同 message class（如 request / response / control）是否在 allocator 处互相压制？是否需要 VC 隔离
- hierarchical NoC（层次化互连）是否减少了全局 allocator 压力？cluster 内部 crossbar 没有 SA 竞争

## 本页结论

router pipeline 与 allocator 是把 NoC 从"链路网络"变成"资源竞争系统"的关键。  
如果不把 RC / VA / SA / ST / LT 和两类 allocator 分开建模，就很难把 stall 根因拆清楚。header 建路、body 跟随、tail 释放——这三者的行为差异是 wormhole router 正确性的基础。
