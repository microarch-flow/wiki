# AXI 五通道与 VALID/READY

上级：[03 片上总线协议族](./README.md)

相关：[AXI Channel、ID 与 Outstanding](./axi-channel-id-outstanding.md)、[地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md)、[仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)、[AXI Response 与错误路径](./axi-response-error-path.md)

## 这页在回答什么问题

AXI 的五个 channel 和 `VALID/READY` 握手到底在定义什么，为什么一次 channel handshake 不等于整笔 transaction 完成。

## 五个 channel 对应事务生命周期

想象一个高效运转的大餐厅，把服务流程拆成五条独立的传送带——点单、送菜到厨房、厨房回执、取菜、上菜给客人——每条传送带都可以独立运转、独立排队。AXI 就是这样把一次访问拆成五条可独立握手的流：

| Channel | 方向 | 语义 | 在生命周期里的作用 |
|---|---|---|---|
| `AW` | master -> slave | 写地址和写属性 | 建立写事务上下文 |
| `W` | master -> slave | 写数据、byte strobe、last | 消耗写数据通路 |
| `B` | slave -> master | 写响应 | 闭合写事务 |
| `AR` | master -> slave | 读地址和读属性 | 建立读事务上下文 |
| `R` | slave -> master | 读数据、读响应、last | 返回读 payload 并闭合读事务 |

这五条流不是平行的五个“字段组”，而是把 02 章的地址、数据、响应生命周期显式化。地址阶段回答“这笔事务要去哪、按什么规则处理”；数据阶段回答“payload 如何逐 beat 传输”；响应阶段回答“事务以什么状态结束”。

拆分的收益是局部并行：读写可以同时进行，写地址和写数据可以不同节奏到达，读数据可以在地址请求之后延迟返回。代价是每个实现都要维护跨 channel 的状态：`AW` 和 `W` 如何配对，`B` 何时允许返回，`AR` 和 `R` 如何匹配，last beat 何时释放 outstanding。

容易误解：五通道只是 AXI 的信号命名。实际上，五通道定义的是事务生命周期的分段和资源占用边界。

## VALID/READY 定义的是局部交付

VALID/READY 握手就像**双方伸手的交接仪式**：递东西的人举起手说”我准备好了”（VALID），接东西的人也伸出手说”我能接”（READY），只有两只手同时伸出的那一刻，东西才算交出去。

这个规则的关键在于”**只完成当前这一步**”。服务员把点单递给厨房（`AWVALID && AWREADY`），只说明点单被接收了——菜还没做呢；厨房把一道菜放上传送带（`WVALID && WREADY`），只说明这道菜上了传送带——客人还没吃到呢；客人确认收到账单（`BVALID && BREADY`），这才说明这笔订单闭环了。

VALID/READY 的设计交易很明确。它给每条流提供局部弹性，接收方可以在 buffer 满、内部状态不足、下游阻塞时拉低 `READY`；发送方可以在没有新数据时拉低 `VALID`。但这种局部弹性也会制造跨 channel 脱节，迫使实现者增加 FIFO、计数器、skid buffer 和关联状态。

容易误解：`READY` 应该保持为 1。实际上，保持 `READY=1` 只是降低气泡的实现目标；协议允许接收方用 `READY=0` 表达 backpressure。

## 写事务由 AW/W/B 三段闭合

写事务最容易暴露“五通道不是原子事务”的事实。写地址和写数据在不同 channel 上传输，写响应又沿反方向返回。一个实现可以先收到 `AW`，再接收多个 `W` beat；也可能先暂存部分 `W` beat，再等待对应 `AW` 上下文。协议允许这些流解耦，但实现必须保证提交数据和生成 `B` response 时，地址、属性、数据 beat 和 strobe 都已被正确关联。

下面是一个 4-beat 写 burst 的构造时序：

| Cycle | `AW` | `W` | `B` | 事务状态 |
|---:|---|---|---|---|
| 0 | `AWVALID && AWREADY` | - | - | 写地址和属性进入系统 |
| 1 | - | `W beat0` handshake | - | 写数据开始占用 data path |
| 2 | - | `W beat1` handshake | - | burst 继续 |
| 3 | - | `WREADY=0` | - | 写地址已接收，但事务未完成 |
| 4 | - | `W beat2` handshake | - | backpressure 解除 |
| 5 | - | `W beat3 && WLAST` | - | payload 到齐，slave 可以闭合写语义 |
| 6 | - | - | `BVALID && BREADY` | 写 response 被消费，事务完成 |

这张表里，cycle 0 不是“写完成”，cycle 5 也不一定是 master 可见的完成；对 master 来说，写事务要等 `B` response 被消费后才闭环。若 `BREADY=0`，slave 或 interconnect 的 response buffer 可能被占住，并反压新的写事务。

容易误解：`AW` handshaked 之后，后续只是数据搬运。实际上，写事务的完成语义在 `B` channel；没有 `B`，master 无法释放对应 outstanding 状态。

## 读事务由 AR/R 两段闭合

读事务没有单独的 read response channel，因为读数据和读状态都在 `R` channel 返回。`AR` handshake 建立读请求，后续一个或多个 `R` beat 返回 payload 和 response；burst 读要等最后一个 `R` beat 才能释放整笔事务。

这带来两个建模重点。第一，`ARREADY=1` 不代表读数据会很快返回，slave、memory controller、bridge 和返回路径都可能引入等待。第二，`RREADY=0` 不只是 master 端的小停顿；如果返回数据无法被消费，slave 或 interconnect 的 response buffer 可能满，进一步限制新的 `AR` 接收。

对读路径，`R` channel 是性能和正确性的共同边界。性能上，它决定返回带宽和 tail latency；功能上，它承载 data、response、ID 和 last beat。漏掉其中任何一个，模型都会把“请求已接收”和“数据已完成”混成一件事。

容易误解：读事务只要看 `AR` channel。实际上，`AR` 是请求入口，`R` 才是读事务 completion 的可见路径。

## 通道解耦会重新形成依赖

AXI 的五条传送带设计上是独立的，但在真实餐厅里，它们会因为**资源有限**重新耦合。点单传送带太快、厨房的灶台不够用（`AW` 接太多而 `W` buffer 不够），厨房会爆单；客人的菜太多端不走（`R` path 回不来），新点的菜就没地方放；客人不签账单（`B` 被 master 堵住），服务员就没法清桌接新客人。

这些依赖不是系统设计失败，而是**任何有限资源系统的必然结果**——就像五条传送带速度可以不同，但餐厅的桌子、灶台和服务员总是有限的。优秀的 AXI 实现会明确每条 channel 的接收能力和释放条件；糟糕的实现会在点单成功后才发现厨房已经做不过来了。

调试 AXI hang 时，应该沿五条 channel 分开看：

- `AW` 是否接收过多写地址，超过 `W/B` 能闭合的能力。
- `W` 是否缺 beat、缺 `WLAST`，或被下游 `WREADY=0` 阻塞。
- `B` 是否生成但 master 不消费，导致写路径无法释放。
- `AR` 是否被 outstanding slot、slave request slot 或 ordering rule 限制。
- `R` 是否被返回 FIFO、master `RREADY` 或 last beat 缺失卡住。

## 一句话理解

AXI 五通道把 transaction 拆成可局部握手的地址、数据和响应流；`VALID/READY` 只完成当前 channel 的一次交付，整笔事务必须靠跨 channel 状态重新闭合。

## 建模启示

建模 AXI 时，五个 channel 不能合并成一个“bus busy”状态。每个 channel 至少要有独立的 ready/valid、queue depth、service time、backpressure source 和已传 beat 计数。写路径要关联 `AW/W/B`，读路径要关联 `AR/R`。

性能模型可以把具体信号编码折叠掉，但必须保留 channel 之间的依赖：`AW` 接收是否占用写事务 slot，`W` beat 是否耗尽 data buffer，`B` 是否释放写 outstanding，`AR` 是否占用读 outstanding，最后一个 `R` beat 是否释放读事务。

功能模型还要检查闭合条件：`WLAST` 是否和 burst 长度一致，`WSTRB` 是否匹配窄写语义，`B/RRESP` 是否返回正确错误类别，`RID/BID` 是否匹配原请求，`R last` 是否准确标记读 burst 结束。

最危险的简化是把 `VALID && READY` 解释成整笔事务完成。它只说明当前 channel 当前 beat 交付成功；transaction 是否完成，要看地址、数据、响应、ID、last beat 和 response consumption 是否都已经闭合。
