# Credit Based Flow Control

上级：[02 Router Microarchitecture](./README.md)
相关：[Input Buffer Organization](./input-buffer-organization.md), [../05-system-integration/noc-vs-bus-revisited.md](../05-system-integration/noc-vs-bus-revisited.md)

## 这页在回答什么问题

为什么多跳 NoC 更偏爱 credit-based flow control，而不是直接把 BUS 世界里熟悉的 `VALID/READY` 沿链路拉长，以及 credit round-trip 如何决定 buffer 深度和 backpressure 传播行为。

这一页的重点不是“credit 是什么”，而是“它解决了什么多跳问题，又带来了什么代价”。

## Flow control 要解决的是安全前进条件

router input buffer 是有限的。上游如果不管下游有没有空位，就会直接把 flit 发进一个已经满的缓冲，结果要么丢数据，要么要求不可实现的零延迟停发。

所以 flow control 的本质很朴素：发送方在每个时刻都要知道自己还能不能安全地继续发。

## 为什么 ready/valid 不适合跨多跳网络

`VALID/READY` 在 BUS 和局部 pipeline 里非常好用，因为它表达的是本地交付：这一拍接收方能不能收。

但在 NoC 链路上，如果你想让“下游满了”这个事实及时传到上游，`READY` 会面临一个根本问题：它需要逆向跨越物理距离和流水延迟。

构造例子：

```text
A -> B -> C
each forward hop = 1 cycle
```

若 C 满了，希望阻止 A 继续发：

```text
cycle 0: C knows it is full
cycle 1: B learns it
cycle 2: A learns it
```

这两拍里，A 如果还按本地 `READY` 旧值继续发，就可能把中间 buffer 冲满。你当然可以继续给 `READY` 路径插更多同步逻辑，但问题会退化成：为了表达多跳 buffer 状态，你在做一条长距离反向时序关键路径。这通常不是一个好交换。

这和 [AXI 五通道与 VALID/READY](../../../BUS/wiki/03-on-chip-protocol-families/axi-five-channels-handshake.md) 的场景不同。AXI 的 `READY` 更多是局部 channel handshaking；NoC 要处理的是网络中间资源的延迟可见性。

## Credit 的核心思路：把远端状态变成本地计数器

credit-based flow control 的做法是：

- 发送方维护一个本地 credit counter
- credit 表示下游 buffer 尚可用的 slot 数
- 每发送一个 flit，credit 减 1
- 下游释放一个 slot，回传一个 credit，发送方再加 1

于是“我能不能发”不再依赖远端实时信号，而只依赖本地计数器是否大于 0。

这就是 credit 成为多跳 NoC 主流方案的原因。它用显式状态换掉了长距离反向时序路径。

## Credit 不是 ACK

这个误解非常普遍。

credit 返回的含义不是“你的 flit 已经送达最终目的地”，而是“我这里腾出了一个 buffer slot，你又可以多发一个 flit 了”。

也就是说，credit 只对局部 hop 有语义。它保证的是逐跳 buffer 安全，不是端到端事务完成。

这和 BUS response 完全不同。BUS response 在语义上更接近 transaction completion；credit 只是流控节奏信号。

## Credit 返回时机决定了 round-trip

什么时候回一个 credit？不是“flit 到达下游”时，而是“flit 离开下游 input buffer”时。

一个典型时序：

```text
cycle 0: upstream sends flit
cycle 1: downstream writes flit into input VC
cycle 2: downstream wins SA, flit leaves input VC
cycle 3: credit returns upstream
```

这个总延迟就是 credit round-trip 的一部分。把它写成公式：

```text
R = forward_link_latency
  + downstream_buffer_residency_until_release
  + credit_return_latency
```

这里面最容易被忽略的是中间那一项。很多人以为 credit 只和链路长度有关，实际上下游内部拥塞、SA 等待、ejection 慢，都会拉长 slot 被占用的时间，从而拉长 credit 返回。

## R 的参数化分解

为了让 R 不是一个"经验数字"，把上面三项拆到可测量的颗粒度：

### forward_link_latency

```text
forward_link_latency
  = wire_propagation_cycles + serialization_cycles + crossing_register_cycles

wire_propagation_cycles  = ceil(link_length_um / (signal_velocity_um_per_cycle))
serialization_cycles     = ceil(flit_width_bits / phit_width_bits)
crossing_register_cycles = 同步寄存器级数 (CDC / 长线插入)
```

在同频同电压短线（≤ 1 mm）场景下，这三项往往都能落到 1 拍以内，合成 `forward_link_latency = 1`。长线、跨 die、跨 voltage island 会按上式叠加。

### downstream_buffer_residency

`buffer_residency` = flit 进入下游 input buffer 到离开 input buffer 的拍数。按 router pipeline 阶段展开：

```text
buffer_residency
  = t_BW + t_RC + t_VA_wait + t_SA_wait + t_ST

t_BW  = 1                                    # buffer write
t_RC  = 1 if HEADER else 0                   # body/tail 不重新 RC
t_VA_wait = VA_pipeline + VA_contention      # 多数实现 VA_pipeline = 1
t_SA_wait = SA_pipeline + SA_contention      # 多数实现 SA_pipeline = 1
t_ST  = 1                                    # switch traversal
```

`VA_contention` 与 `SA_contention` 是和负载强相关的随机变量。空载下都 = 0，可得 `buffer_residency_min`；满载（每个端口都有竞争者）下两者期望 ≈ `(N_contenders - 1) / 2`，其中 `N_contenders` 是同输出端口/同输出 VC 上的竞争 input VC 数。

一个常用的近似：

```text
E[buffer_residency] ≈ 3 + E[VA_contention] + E[SA_contention]
                   ≈ 3 + (P-1)/(2·η_VA) + (P-1)/(2·η_SA)
```

其中 `P` = router radix（含 local 端口），`η_VA / η_SA` = allocator 效率（separable 0.6~0.8，iSLIP 收敛后接近 1，wavefront 接近 1 但延迟更高）。

### credit_return_latency

```text
credit_return_latency
  = credit_pipeline_register_cycles + return_wire_cycles + upstream_credit_table_write
```

一个常见简化是反向通道与正向通道对称布线，因此 `return_wire_cycles ≈ forward_wire_cycles`。`upstream_credit_table_write = 1` 拍（SRAM/寄存器写）。

### 合成

```text
R = forward_link_latency
  + (3 + E[VA_contention] + E[SA_contention])    # downstream residency
  + credit_return_latency
```

## 典型数值例子

5-port mesh router、128 bit flit、单 phit、1 GHz、短链（1 拍前向 + 1 拍返向）、4 VC、单端口期望 VA/SA 竞争者 = 1：

| 项 | 取值 |
|----|------|
| `forward_link_latency` | 1 |
| `t_BW + t_RC + t_ST` | 3 |
| `E[VA_contention]` | 0.5 |
| `E[SA_contention]` | 0.5 |
| `credit_return_latency` | 1 + 1 = 2 |
| **R_total** | **≈ 8 拍** |

把同样参数换到 1 mm 长线、需要 2 级同步寄存器、SA 竞争重（5 个竞争者，iSLIP）：

| 项 | 取值 |
|----|------|
| `forward_link_latency` | 1 + 2 = 3 |
| `t_BW + t_RC + t_ST` | 3 |
| `E[VA_contention]` | 0.5 |
| `E[SA_contention]` | 2 |
| `credit_return_latency` | 3 + 1 = 4 |
| **R_total** | **≈ 12.5 拍** |

两个数字之间的差异说明：**buffer_depth 不是按拓扑选，而是按 R 选**。同一拓扑不同物理实现，buffer 需求差 1.5 倍是常见的。

## Buffer 深度为什么至少要覆盖 R

如果一个活跃 VC 的 buffer 深度小于 credit round-trip `R`，上游在还没等到第一个 credit 回来之前就会用光所有 slot，被迫停发，链路出现气泡。

例子：

```text
R = 3 cycles
buffer depth = 2

cycle 0: send flit0, credit 2->1
cycle 1: send flit1, credit 1->0
cycle 2: stop, waiting for credit
cycle 3: first credit returns
```

这说明 buffer depth 不是“存突发流量的桶”而已，它还决定稳态下链路能否被打满。

### 推导：使链路饱和的最小 buffer_depth

把"稳态下链路始终有 flit 可发"作为目标，等价于：发送方任意时刻 credit > 0。

```text
稳态吞吐 = 1 flit / 拍 (单 VC 占满链路)
in_flight (含 link 上 + 下游 buffer 中) = R
要求 buffer_depth >= R
```

更严格的，若一个 input port 上有 `V` 个 VC 轮流发往同一下游端口，每个 VC 只独占链路 `1/V` 拍，则**单 VC** 的 buffer 需求降为：

```text
per_vc_buffer_depth >= ceil(R / V)
```

但**所有 VC 加总**的 buffer 总深度仍需 ≥ R，否则下游聚合带宽达不到链路带宽。

实用经验：

| 目标 | 建议 |
|------|------|
| 单 VC 打满链路 | `buffer_depth = R + 1~2`（留出 jitter 余量）|
| V 个 VC 共享链路 | `per_vc_depth = ceil(R/V) + 1`、`Σ ≥ R + V` |
| 突发吞吐（短突发 + 长空闲）| 再加 `burst_length` 缓冲 |
| 远大于 R 的深度 | 多数情况下浪费面积，只是把延迟变成在途积压 |

### Buffer 不够时的可观察症状

模拟器里能直接看到的现象，按"buffer 不够"程度依次出现：

| 现象 | buffer 与 R 的关系 |
|------|--------------------|
| 稳态吞吐 < 1 flit/拍 | `buffer_depth < R` |
| stall reason 中 `NO_CREDIT` 占比 > 30% | `buffer_depth ≈ R` 但有 contention jitter |
| 链路利用率 ≈ 100%，`NO_CREDIT` < 5% | `buffer_depth ≥ R + 2` |
| 链路利用率 100% 但 packet 平均 latency 偏大 | `buffer_depth >> R`（积压）|

这张表也是 buffer sweep 时的判读基准。

## Backpressure 是怎样一级级传回去的

credit 用尽时，上游停发。若上游自己也因此无法清空更早一级 buffer，就会继续让更上游的 credit 停不回来。于是阻塞会逆流传播。

一个 3-hop 路径例子：

```text
T0 -> R0 -> R1 -> R2 -> Mem
```

若 `Mem` 端口变慢：

1. `R2` input/ejection buffer 释放变慢
2. `R1 -> R2` 的 credit 回不来
3. `R1` 开始停发到 `R2`
4. `R0 -> R1` 的 credit 也开始回不来
5. `T0` 最终在注入端看到停顿

这就是为什么 AI NoC 特别怕 response path 变慢。一次远端 memory service 抖动，会沿 credit 链逐级传播回 producer。

## Credit 的主要代价

credit 好处很明确，但它也不是免费：

- 每个 VC 要有独立 credit state
- 需要反向 credit 通道
- buffer 深度要为 round-trip 买单
- 调试时必须分清 `NO_CREDIT` 和 `SWITCH_CONFLICT`

特别是最后一点。很多“router 卡住了”的现象，外观看起来都像 flit 不前进；但 root cause 可能完全不同。credit stall 是下游 slot 没回来，switch stall 则是本地 crossbar 没抢到。两者的调参手段不一样。

## 和 BUS backpressure 的相同点与差别

相同点：两者都在表达“下游当前不能继续接收”。

差别：

- BUS 里的 `READY=0` 更像局部 channel 的即时拒收
- NoC 里的 `credit=0` 更像把远端 buffer 状态延迟投影回本地

也正因如此，BUS backpressure 更多是接口节奏问题；NoC credit backpressure 更多是网络资源依赖问题。

## 常见误解

常见误解：credit 就是带编号的 ACK。  
实际上：credit 只说明一个 hop 的 buffer slot 被释放，不说明 packet 或事务已完成。

常见误解：只要链路物理延迟短，buffer 就可以很浅。  
实际上：credit round-trip 还包含下游内部等待时间，局部拥塞同样会拉长 slot 占用。

## 一句话理解

credit-based flow control 的本质，是把“下游还有没有空间”从远端实时信号改写成本地可查询计数器；它用状态和 buffer 换掉了长距离时序依赖。

## 建模启示

模型至少要显式维护：

```text
CreditState {
  available_credits_per_downstream_vc[]
}

LinkParams {
  forward_link_latency           # 由 wire / serialization / sync 组成
  return_link_latency
  flit_width_bits
  phit_width_bits
}

RouterParams {
  t_BW; t_RC; t_VA_pipeline; t_SA_pipeline; t_ST   # 各阶段固定开销
  allocator_type                                    # separable / iSLIP / wavefront
  eta_VA; eta_SA                                    # allocator 效率
  buffer_depth_per_vc; num_vcs
}

R_components(link, router, contention) =
  link.forward_link_latency
  + router.t_BW + router.t_RC + router.t_VA_pipeline + router.t_SA_pipeline + router.t_ST
  + contention.E_VA + contention.E_SA
  + link.return_link_latency
  + 1            # upstream credit table write
```

以及事件：

- `flit_send_consumes_credit`
- `buffer_slot_released`
- `credit_return_arrive`
- `injection_blocked_no_credit`

把 `R` 拆成 `(link, router, contention)` 三组参数后，做架构探索时就能正交 sweep：拓扑变了改 link、流水线变了改 router、负载变了改 contention，buffer 需求自动从公式推出，不必每次重跑工程经验。

如果只做拓扑层平均带宽比较，可以把 credit 折叠成"链路有效带宽折减因子"；但一旦你关心 backpressure、buffer sizing 或 response tail latency，就必须逐拍建 credit，因为 `R` 和 `buffer_depth` 的关系会直接决定是否出现链路气泡。

如果要做 deterministic worst-case latency 分析，把 `R` 拆成 `link / router_fixed / contention` 三段后取每段的 worst case 相加即可——上面公式天然支持这种拆分。
