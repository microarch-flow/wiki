# Bank 为什么是 DRAM 并行性的最小单位

上级：[DRAM 基础](./README.md)
相关：[Row buffer：DRAM 内部的小 cache](./row-buffer-as-cache.md), [为什么说 DRAM 的实际性能由 MC 决定](../06-memory-controller/why-mc-is-the-real-bottleneck.md)

## 这页在回答什么问题

为什么 DRAM 的并行性不是从 channel 才开始，而是先从 bank 这个内部组织单位开始。更具体地说，bank 到底隔离了哪些状态、共享了哪些资源，以及为什么“bank 数量更多”并不自动等于“真实带宽就更高”。

## 正文

一旦理解了 row buffer 和 open row 这套机制，接下来的自然问题就是：如果 DRAM 每次只能在一个打开行上便宜访问，那它如何支撑系统所需的高吞吐？答案之一就是 bank。bank 的核心作用，不是单纯把容量切块，而是把“打开行状态”和一部分阵列操作状态复制出多份，让不同访问流有机会在 DRAM 内部并行推进。没有 bank，DRAM 会几乎退化成一个只能围绕单一 open row 来回切换的大阵列，row conflict 会频繁到难以忍受。

最直观的理解方式是把 bank 看成“一个相对独立维护 open row 和 sense amp 工作副本的子阵列”。每个 bank 通常都有自己的一组行阵列、对应的 row buffer / sense amp 阵列，以及与之关联的局部状态。这样一来，bank A 可以保持 row 100 打开，bank B 同时保持 row 37 打开，后续请求如果分别命中这两个 bank 的当前 open row，就都能享受较低访问成本。换句话说，bank 把原本只能有一个的“当前打开行”状态复制成了多个并存状态，这正是 DRAM 内部并行度的第一来源。

这也是为什么说 bank 是 DRAM 并行性的最小单位。对 controller 来说，很多调度和命中判断首先不是在 channel 级发生，而是在“这个请求落到哪个 bank、那个 bank 当前 open 的是哪一行、那个 bank 什么时候才会再次 ready”这一层发生。即使只有一个 channel，只要内部有多个 bank，系统仍然可能通过 bank 级并行把多个请求交织起来：一个 bank 正在做 activate 或 precharge 时，另一个 bank 也许已经可以服务列访问。常见误解是把 DRAM 并行只理解成“多 channel 带宽叠加”；实际上，在进入多 channel 之前，bank-level parallelism 已经决定了单颗 DRAM 器件的大部分可调度空间。

但 bank 并不意味着完全独立。理解 bank 的关键，不只是看它隔离了什么，还要看它仍然共享什么。它隔离的是每个 bank 自己的行阵列、open row 状态以及一部分局部 timing 演化；它共享的则可能包括通道上的命令总线、数据总线、I/O 引脚、电源噪声预算、某些全局时序约束，甚至在更细粒度上还会共享 bank group 级别的高速接口资源。也就是说，多个 bank 可以让“阵列内部工作”并行，但最终把数据送出芯片、发送命令或满足某些总线级切换约束时，它们仍然会在更高层相互争用。

这个“局部独立、全局共享”的结构，正是 DRAM 性能分析容易出错的地方。你如果只看到 bank 数量，可能会以为 `N` 个 bank 就能提供近似 `N` 倍并行；但真实情况是，只有当请求流足够分散、row locality 不太差、命令总线没有被占满、读写方向切换没有太频繁时，这些 bank 才能真正同时把价值释放出来。若多个请求虽然落到不同 bank，却需要争抢同一个数据总线发送 burst，或者在时间上反复触发全局受限的命令间隔，那么 bank 数再多也不等于吞吐线性上升。

bank 存在的另一个重要目的，是让 row 冲突的损失局部化。假设没有 bank，任何换行都会把整个阵列当前状态推翻；有了 bank，至少 bank A 的 row conflict 不会直接把 bank B 正在打开的行冲掉。这样 controller 才能把不同地址流映射到不同 bank，试图在“保行局部性”和“扩并行度”之间折中。于是 bank 不只是硬件分块，更是地址映射的目标对象。后面讲地址映射时你会看到，物理地址如何切到 bank 位，几乎直接决定了系统是在利用 bank 并行，还是在制造 bank hotspot。

这里也能看出 bank 和 row buffer 的关系。row buffer 是“每个 bank 当前已打开行的工作副本”，bank 则是“这种副本状态的复制容器”。如果没有 bank，row buffer 命中只是极少数幸运情况；有了多个 bank，不同数据流就有机会各自维持一条短期工作集。因此，你可以把 bank 理解成 row locality 与 memory-level parallelism 之间的桥梁：一方面它允许多个 row buffer 状态并存，另一方面它让 controller 能在多个候选 bank 之间挑选下一个服务对象。

不过 bank 也不是免费午餐。bank 数增加意味着更多局部阵列、更复杂的译码与布线、更大的控制状态空间，也往往伴随更复杂的地址映射和更高的功耗活动粒度。尤其在高频接口下，bank 再继续增加之后，问题会逐渐从“有没有足够多的独立阵列”转移到“这些阵列怎样共享高速 I/O”。这也是为什么后面会出现 `bank group`、prefetch、burst 这些进一步桥接 cell 速度与接口速度的机制。换句话说，bank 解决了第一层阵列并行问题，但它不会自动解决 I/O 和协议层的并行瓶颈。

一个简单的多 bank 交织时序，可以帮助理解它为什么重要：

```text
Cycle     0      1      2      3      4      5
Req A     ACT A -------- RD A -----------------
Req B            ACT B -------- RD B ----------
Req C                           ACT C --- RD C

Bank 0    open row x -> busy -> col access -> ready
Bank 1           open row y -> busy -> col access -> ready
Bank 2                          open row z -> busy -> ready
```

这个图想表达的不是精确 JEDEC timing，而是“一个 bank 在做 activate 时，另一个 bank 仍可推进自己的状态”。如果所有请求都打在同一个 bank，上面的交错基本不成立，系统会退化成严格串行的 `PRE/ACT/RD` 流；只有当请求被合理分散，bank 级并行才会浮现。

再看一个反例也很重要。假设相邻地址被映射得过于集中，四个连续请求都落到同一 bank 的不同行，即便器件内部有很多 bank，controller 看到的仍然可能是：

```text
Req0: PRE/ACT/RD on bank 0
Req1: PRE/ACT/RD on bank 0
Req2: PRE/ACT/RD on bank 0
Req3: PRE/ACT/RD on bank 0
```

这时 bank 并行形同虚设。也就是说，bank 是潜在并行资源，不是自动实现的并行结果。它是否真正转化为有效带宽，取决于地址映射、访问模式、page policy 和控制器调度能否配合。

因此，理解 bank 最稳妥的方式不是把它当成“容量子块”，而是把它当成“可独立维护 open-row 状态、但仍受更高层共享资源约束的最小可调度阵列单元”。后面一切关于 FR-FCFS、page policy、地址交织、bank group、effective bandwidth 的分析，都会围绕这个定义展开。

## 一句话理解

Bank 是 DRAM 内部并行性的最小单位，因为它复制了 open-row 状态和局部阵列工作能力；但它只隔离了部分代价，命令总线、数据总线和更高层时序资源仍然共享。

## 建模启示

对建模来说，bank 不应只是一个容量切片索引，而必须是显式状态对象。至少要给每个 bank 单独建模 `open_row`、`ready_cycle` 和可能的 `refresh/blocking state`，否则模型无法表达 bank-level parallelism，也无法表达热点映射和 row conflict。

一个最小可用的状态草图可以是：

```text
DramBankModel {
  open_row: row_id | INVALID
  ready_cycle: cycle
  state: enum { IDLE, ACTIVATING, ACTIVE, PRECHARGING, REFRESHING }
}
```

在 channel 层还要再保留共享资源：

```text
DramChannelSharedState {
  cmd_bus_ready_cycle: cycle
  data_bus_ready_cycle: cycle
}
```

如果只关心粗粒度吞吐，可以把多个 bank 的效果折叠成一个“并行度系数”；但只要你要分析地址映射、QoS、FR-FCFS 或 row-hit-rate，最好显式建成 `bank array + shared bus` 这两层。因为 DRAM 的核心不是“有多少 bank”，而是“bank 的局部独立性与全局共享性怎样共同塑造服务过程”。

一个足够简洁但有解释力的服务框架可以写成：

```text
for req in schedulable_requests:
  bank = map_to_bank(req.addr)
  if bank.ready_cycle <= now and shared.cmd_bus_ready_cycle <= now:
      issue_command(req, bank)
```

这里只保留了最小骨架，但已经足以让后面的调度策略和冲突分析有真正的落脚点。
