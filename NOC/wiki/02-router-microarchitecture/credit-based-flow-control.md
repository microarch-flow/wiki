# Credit Based Flow Control

上级：[02 Router Microarchitecture](./README.md)
相关：[Input Buffer Organization](./input-buffer-organization.md), [../05-system-integration/noc-vs-bus-revisited.md](../05-system-integration/noc-vs-bus-revisited.md)

## 这页在回答什么问题

为什么多跳 NoC 更偏爱 credit-based flow control，而不是直接把 BUS 世界里熟悉的 `VALID/READY` 沿链路拉长，以及 credit round-trip 如何决定 buffer 深度和 backpressure 传播行为。

这一页的重点不是“credit 是什么”，而是“它解决了什么多跳问题，又带来了什么代价”。

## Flow control 要解决的是安全前进条件

router input buffer 是有限的。上游如果不管下游有没有空位，就会直接把 flit 发进一个已经满的缓冲，结果要么丢数据，要么要求不可实现的零延迟停发。

所以 flow control 的本质很朴素：发送方在每个时刻都要知道自己还能不能安全地继续发。

## 为什么长链路需要处理反馈延迟

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

这两拍里，A 如果还按本地 `READY` 旧值继续发，就可能把中间 buffer 冲满。也可以采用逐跳 ready/valid，并用寄存器与 skid buffer 容纳反馈延迟期间在途的数据。这样不必把 READY 组合地穿越全部 hop；但必须保证每级预留足够容量。credit 是另一种显式记录下游 slot 发送授权的选择。

这和 [AXI 五通道与 VALID/READY](../../../BUS/wiki/03-on-chip-protocol-families/axi-five-channels-handshake.md) 的场景不同。AXI 的 `READY` 更多是局部 channel handshaking；NoC 要处理的是网络中间资源的延迟可见性。

## Credit 的核心思路：把远端状态变成本地计数器

credit-based flow control 的做法是：

- 发送方维护一个本地 credit counter，记录已获授权且尚未使用的下游 slot 数
- 每成功发送一个 flit，预留一个 slot，credit 减 1
- 下游移出该 flit、释放 slot 后，生成并回传一个 credit
- 返还 credit 到达发送端并到达约定的可用采样点后，发送方才将它计入可用信用

在发送判定的采样点，`credit > 0` 是该 VC 的 slot 流控条件。发送还须满足 VC 分配、链路和仲裁等其他条件。`credit = 0` 时，即使下游 FIFO 有物理空槽，也不能凭空槽直接发送。

以固定深度 `B` 的单跳、单 VC 为例。假设初始 FIFO 和正反向管线为空，全部 `B` 个 slot 授权可用；每个发送的 flit 预留一个 slot，每次出队恰好生成一个返还 credit，没有丢失、重复或其他预留，且释放和生成 credit 在同一提交动作中完成。在同一状态快照中：

```text
B = C + F + Q + K_return
C：发送端可用 credit 数             F：已预留 slot 的正向在途 flit 数
Q：下游 FIFO 已占 slot 数           K_return：尚未在发送端可用的返还 credit 数
```

这里 `K_return` 包括已到达发送端但尚未到可用采样点的返还 credit。下游物理空槽数为 `B - Q = C + F + K_return`；其中正向在途 flit 已预留 `F` 个槽，`K_return` 个槽的授权尚未重新可用。例如 `B=2, C=0, F=0, Q=1, K_return=1`，FIFO 有一个空槽，发送端仍须停发，直到返还信用可用。

这就是 credit 成为多跳 NoC 主流方案的原因。它用显式状态换掉了长距离反向时序路径。

## Credit 不是 ACK

这个误解非常普遍。

返还 credit 表示这一跳的下游此前释放了一个 buffer slot，不表示 flit 已送达最终目的地。该 credit 到达可用采样点后，才增加一次 slot 发送授权。

也就是说，credit 只对局部 hop 有语义。遵守 slot credit 契约可避免该跳 buffer overflow，但不能证明端到端事务完成。slot credit 与新包的 output VC 分配许可是不同状态；严格策略还需跟踪尾部 free 信号，见 [VC 状态](../08-simulator-construction/core-data-structures.md#三种独立状态)。

这和 BUS response 完全不同。BUS response 在语义上更接近 transaction completion；credit 只是流控节奏信号。

## Credit 返回时机决定了 round-trip

什么时候回一个 credit？不是“flit 到达下游”时，而是“flit 离开下游 input buffer”时。

一个示意时序（假设到达后下一拍可转发、返回后该拍可用；不是第 08 章的快照时序）：

```text
cycle 0: upstream sends flit
cycle 1: downstream writes flit into input VC
cycle 2: downstream wins SA, flit leaves input VC
cycle 3: credit returns upstream and is usable this cycle
```

令 `R` 为从发送消耗 credit 到返还信用可用于发送判定的 credit round-trip。各阶段边界不重叠时，可写成：

```text
R = forward_link_latency
  + downstream_buffer_residency_until_release
  + credit_return_latency
```

这里面最容易被忽略的是中间那一项。很多人以为 credit 只和链路长度有关，实际上下游内部拥塞、SA 等待、ejection 慢，都会拉长 slot 被占用的时间，从而拉长 credit 返回。

## R 的参数化分解

为了让 R 不是一个"经验数字"，把上面三项拆到可测量的颗粒度：

### forward_link_latency

先固定观测边界：发送端在时钟沿启动第一个 phit；接收端在时钟沿采样最后一个 phit。`t_path` 在本例包含 clock-to-Q、组合逻辑、导线传播、接收端 setup 与不利 skew/jitter 裕量。假设同频，序列化后每拍启动一个 phit，没有等待；记 `K = ceil(flit_width_bits / phit_width_bits)`。

若每个 phit 按接口契约在**下一时钟沿**采样，必须满足 `t_path ≤ clock_period`，并满足 hold 条件。于是最后 phit 的接收沿相对首 phit 发射沿为 `K` 拍。单 phit 且 `t_path=0.2T` 时延迟为 1 拍；导线传播与同一周期内的发射过程重叠，不能分别向上取整再相加。若 `t_path=1.2T`，这个下一沿采样设计不满足时序，不能用 `ceil(1.2)=2` 自动把它当成合法两拍链路。

若实现明确支持 `d` 拍后采样，或插入了有定义的流水级，则按其 valid/ready、采样相位、setup/hold、时钟和容量契约推导时序。只有在各 phit 的数据有效窗口覆盖对应采样沿、下一 phit 不覆盖待采样数据、连续发射满足接口约束时，最后 phit 延迟才可以写为 `(K-1)+d`。实际序列化有空拍时必须把空拍加进去。CDC 需要单独建同步与时钟域语义。

### downstream_buffer_residency

`buffer_residency` 是 flit 写入下游 input buffer 后，到它成功离开该 buffer 的时间。它包含实际经过的路由、VC 分配、switch 分配、排队与转发，但阶段可能重叠，也可能仅由 header 执行。应按实现测量边界，不可同时把重叠阶段的完整延迟相加。

例如，假设某 router 将无竞争情况下的相关工作重叠后，header 的基准 residency 为 3 拍；VA 与 SA 分别再等待 `w_va`、`w_sa` 拍，且二者等待不重叠，则本例 `residency = 3 + w_va + w_sa`。这个 3 是示例模型参数，不是通用 router 的最小值。VA 等待受下游 VC 释放影响，可能跨多个 flit 时间；不能仅凭竞争者个数推断固定的等待期望。

### credit_return_latency

```text
credit_return_latency
  = credit_pipeline_register_cycles + return_wire_cycles + upstream_credit_table_write
  # 此式仅用于这些阶段被定义为不重叠且逐段计拍的模型
```

即使反向与正向通道对称布线，也不能直接把两者的完整延迟当成相等：两者载荷大小、序列化、寄存器与采样点可能不同。下面数值例子明确假设返向总链路为 1 拍、credit 表写入再占 1 拍。

### 合成

```text
R = forward_link_latency
  + (3 + E[VA_contention] + E[SA_contention])    # 仅用于上面的特定示例
  + credit_return_latency
```

## 典型数值例子

5-port mesh router、128 bit flit、单 phit、1 GHz、短链（1 拍前向 + 1 拍返向）、4 VC；假设与上面相同的 3 拍基准 residency，且实测或模型给出平均 VA、SA 额外等待均为 0.5 拍：

| 项 | 取值 |
|----|------|
| `forward_link_latency` | 1 |
| 无竞争 residency（含重叠的各阶段）| 3 |
| `E[VA_contention]` | 0.5 |
| `E[SA_contention]` | 0.5 |
| `credit_return_latency` | 1 + 1 = 2 |
| **R_total** | **≈ 7 拍** |

把同样参数换到 1 mm 长线、需要 2 级同步寄存器、SA 竞争重（5 个竞争者，iSLIP）：

| 项 | 取值 |
|----|------|
| `forward_link_latency` | 1 + 2 = 3 |
| 无竞争 residency（含重叠的各阶段）| 3 |
| `E[VA_contention]` | 0.5 |
| `E[SA_contention]` | 2 |
| `credit_return_latency` | 3 + 1 = 4 |
| **R_total** | **≈ 12.5 拍** |

两个数字之间的差异说明：同一拓扑的不同物理实现可以产生不同的 credit 往返时间。选择 buffer 深度还要考虑目标速率、延迟分布和采样规则；只凭平均 `R` 不能保证无气泡。示例是构造值，不能当作芯片实测。

## 单 VC 持续满速时的 Buffer 深度

在以下满载示例中，单 VC 每拍都有待发 flit，链路和下游都能每拍服务一个，credit 在发送后固定 `R` 拍的仲裁前可用。如果 buffer 深度小于 `R`，上游会在第一个 credit 可用前用光授权，被迫停发，链路出现气泡。

例子：

```text
R = 3 cycles
buffer depth = 2

cycle 0: send flit0, credit 2->1
cycle 1: send flit1, credit 1->0
cycle 2: stop, waiting for credit
cycle 3: first credit returns and is usable before arbitration
```

这说明 buffer depth 不是“存突发流量的桶”而已，它还决定稳态下链路能否被打满。

### 推导：单 VC 持续发送需要多少 slot

假设单 VC 每拍总有一个待发 flit，链路及下游都能每拍服务一个，初始 credit 等于 buffer 深度。对拍 `t` 发送的 flit，令 `A` 为返还 credit 到达发送端所在拍相对 `t` 的拍差，`R` 为该 credit 首次可参加发送仲裁的拍差。若它赶上拍 `t+A` 的仲裁采样并可使用，则 `R=A`；若它错过该采样、但下一拍可用，则 `R=A+1`。有额外处理延迟时，以实际首次可用的仲裁拍确定 `R`。在每次返还均为同一固定整数 `R≥1` 的条件下，连续每拍发送需要 `buffer_depth ≥ R`。发出第 `R` 个 flit 后计数可暂时为 0，只要第一枚返还 credit 在下一次仲裁前可用即可。按可用拍定义的 `R` 已包含采样等待，不应再加一。

守恒口径必须包括正向在途 flit、下游 FIFO 和反向在途 credit；不能只数前两项。若 `V` 个 VC 严格轮流发送，每个 VC 间隔 `V` 拍，固定 `R` 与相同采样规则下每个 VC 至少需要 `ceil(R/V)` 个 slot。它是该理想调度的条件，不保证不均匀仲裁、空流、VC 分配等待或延迟抖动下也能满速。

`NO_CREDIT` 高可能说明 credit loop 长或 buffer 浅，但也可能来自下游拥塞、仲裁和端点停顿。链路吞吐低也可能由注入不足或 switch 竞争造成。诊断要同时观察 credit 往返分布、队列、每拍 grant 和实际注入；不能从某个固定百分比单独反推出深度。

## Backpressure 是怎样一级级传回去的

某 VC 的 credit 用尽时，上游不能再向该 VC 发送。若上游自己也因此无法清空更早一级 buffer，就会继续让更上游的 credit 停不回来。于是阻塞会逆流传播。

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

特别是最后一点。很多“router 卡住了”的现象，外观看起来都像 flit 不前进；但 root cause 可能完全不同。credit stall 是所需的 slot credit 尚不可用，switch stall 则是本地 crossbar 没抢到。两者的调参手段不一样。

## 和 BUS backpressure 的相同点与差别

相同点：两者都可以阻止本拍继续发送，避免接收侧容量不足。

差别：

- BUS 局部 channel 在采样沿 `READY=0` 时，该沿没有完成握手
- NoC 在发送判定时 `credit=0`，表示发送端没有可用的 slot 授权；这不等于下游物理 buffer 此刻必然已满

也正因如此，BUS backpressure 更多是接口节奏问题；NoC credit backpressure 更多是网络资源依赖问题。

## 常见误解

常见误解：credit 就是带编号的 ACK。  
实际上：返还 credit 表示一个 hop 的 buffer slot 此前被释放，不说明 packet 或事务已完成。

常见误解：只要链路物理延迟短，buffer 就可以很浅。  
实际上：credit round-trip 还包含下游内部等待时间，局部拥塞同样会拉长 slot 占用。

## 一句话理解

credit-based flow control 用本地计数器跟踪已获得、尚未使用的下游 slot 发送授权；它用状态和 buffer 处理反馈延迟。

## 建模启示

模型至少要记录每个下游 VC 的 `available_credit`、占用队列、分配许可，以及 forward 和 return link 的容量与时序。每次 credit loop 记录 `send_cycle`、`downstream_arrival_cycle`、`buffer_slot_release_cycle` 和 `credit_available_cycle`，并固定它们相对于仲裁和提交的采样点。由同一个样本的 `credit_available_cycle - send_cycle` 得到该样本的 `R`，而非先把可能重叠的阶段机械相加。

事件包括 `flit_send_consumes_credit`、`buffer_slot_released`、`credit_return_arrive` 和 `injection_blocked_no_credit`。拓扑、流水线和仲裁策略改变后，必须重新计算或测量等待分布；负载依赖项不能直接当作独立常数。逐拍模型及 slot 守恒见 [模拟器核心数据结构](../08-simulator-construction/core-data-structures.md#断言与守恒)。

如果只做拓扑层平均带宽比较，可以把 credit 折叠成"链路有效带宽折减因子"；但一旦你关心 backpressure、buffer sizing 或 response tail latency，就必须逐拍建 credit，因为 `R` 和 `buffer_depth` 的关系会直接决定是否出现链路气泡。

做 worst-case latency 分析时，先证明流量到达、仲裁公平性、下游服务及 endpoint 消费都有有限上界，并说明各项能否同时发生。若 consumer 可永久停顿或仲裁可饥饿，则有限 buffer 本身不提供有限延迟上界。
