# AXI Response 与错误路径

上级：[03 片上总线协议族](./README.md)

相关：[地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md)、[AXI 五通道与 VALID/READY](./axi-five-channels-handshake.md)、[AXI Channel、ID 与 Outstanding](./axi-channel-id-outstanding.md)、[Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md)、[争用、QoS 与可观测性](../05-performance-debug/contention-qos-observability.md)

## 这页在回答什么问题

当 AXI 访问成功、decode 失败、slave 报错或 fabric 合成错误时，response path 如何定义事务闭环，以及调试时应该沿哪些边界定位。

## Response 是 completion，不只是错误码

AXI 的 response 语义回答两个问题：这笔事务是否以某种状态结束，以及这个结束状态能否被 master 消费。写事务通过 `B` channel 返回 `BRESP`，读事务通过 `R` channel 随读数据返回 `RRESP`。没有 response，master 就无法可靠释放 outstanding slot，也无法判断软件等待的访问是否完成。

因此，成功 response 也必须建模。`OKAY` 不是“没有信息”，而是事务成功闭合的证据；错误 response 则是在闭合事务的同时，告诉 master 这次访问不能按正常结果解释。对写路径，`BVALID && BREADY` 是 master 消费写 completion 的位置；对读路径，最后一个 `R` beat 被消费后，读 burst 才完整闭合。

AXI response 不是根因报告系统。`DECERR`、`SLVERR`、`OKAY`、`EXOKAY` 这类编码只表达协议层状态类别，不会自动包含具体寄存器、权限表、ECC syndome、bridge timeout 计数或下游日志。调试必须把 response 类别和产生位置、路径状态、slave 状态寄存器、trace/counter 联系起来。

容易误解：response 只在失败时重要。实际上，response 是 completion 本身；成功和失败都会释放状态、推进软件等待和影响 ordering。

## AXI 常见 response 类别

不同 AMBA/AXI 版本和系统实现会有具体差异，这里只抓架构判断需要的类别：

| Response | 语义入口 | 调试含义 |
|---|---|---|
| `OKAY` | 正常完成 | 请求被接受并以正常状态闭合 |
| `EXOKAY` | exclusive access 成功相关状态 | 需要结合 exclusive/atomic 语义解释 |
| `SLVERR` | slave 接收请求后无法正常完成 | 目标内部错误、非法寄存器语义、保护/ECC/状态机异常等 |
| `DECERR` | 地址没有被有效 decode 或被 fabric 拒绝 | decode miss、无目标、访问窗口非法、fabric 合成错误入口 |

这张表不替代协议规范，也不保证每个系统都把所有底层问题原样映射到这些类别。关键是：response 类别只能告诉你错误被包装成了哪类 completion，不能单独证明根因发生在哪一层。

容易误解：看到 `DECERR` 就一定是地址写错。实际上，decode miss 是主要线索，但 bridge、firewall、timeout wrapper 或系统策略也可能把某些路径问题包装成 decode/error 类 completion。

## 错误可能产生在不同位置

AXI 错误路径要沿访问生命周期定位，而不是只看最终 `BRESP/RRESP`。

第一类是 decode 或路由阶段错误。地址没有命中任何 slave，命中了被禁用窗口，或被 interconnect/firewall 拒绝，fabric 可以直接生成错误 response。此时 slave 可能根本没有看到这笔请求。

第二类是 slave 内部错误。请求已经到达目标，但目标无法按语义完成：访问不存在的寄存器，状态机不允许当前写入，ECC/parity/protection 失败，内部 timeout，或者目标不支持请求的 size、burst、WSTRB 组合。此时 response 来自 slave 或靠近 slave 的 wrapper。

第三类是 bridge 或 fabric 合成错误。下游协议没有返回、CDC/width adapter 发现非法组合、低速外设长期无响应、IOMMU/SMMU 或保护逻辑拒绝访问时，中间层可能生成 response，避免 master 永久挂住。这里的错误类别是“包装后的完成状态”，根因还在更下游或更上层策略里。

容易误解：最终 response 出现在 master 侧，就说明 master 附近出错。实际上，response 只是沿返回路径回到 master；产生点可能在 decode、bridge、slave、protection block 或 timeout wrapper。

## 读写错误路径不完全一样

写事务的 completion 在 `B` channel。写地址 `AW` 被接受、写数据 `W` 被接收，都不代表写成功；slave 或 interconnect 必须在 `B` channel 上返回状态。一个写 burst 即使所有 `W` beat 都 handshaked，也要等 `BRESP` 被 master 消费后，master 才能释放对应 outstanding。

读事务的状态随 `R` channel 返回。读 burst 可能有多个 `R` beat，每个 beat 携带 `RRESP`，最后一个 beat 还承担 burst completion 的边界。实现和调试时要关注：错误是否出现在某个 beat，错误 beat 是否仍然满足 last/ID 语义，master 是否消费了这些 beat。

一个构造写错误路径：

| Cycle | `AW` | `W` | `B` | 状态 |
|---:|---|---|---|---|
| 0 | 地址被接收 | - | - | request header 进入系统 |
| 1-4 | - | 4 个写 beat 被接收 | - | payload 到齐 |
| 5 | - | - | `BVALID` with `SLVERR` | slave 报告写事务失败 |
| 6 | - | - | `BVALID && BREADY` | master 消费错误 completion |

这张表里，错误不是“额外事件”，而是事务闭合方式。若 cycle 6 不发生，master 仍可能保持等待状态，写 outstanding 也可能无法释放。

容易误解：写数据被接收就等于写成功。实际上，写成功或失败要看 `B` response；读成功或失败要看 `R` data 和 `RRESP` 的组合。

## Timeout 和 hang 的分界在 response 是否闭合

AXI 协议本身定义 response 语义，但系统是否有 timeout wrapper、timeout 多久触发、触发后返回哪类 response，是 SoC 设计选择。这个边界对调试非常重要。

如果下游长期不返回，fabric 或 bridge 合成一个错误 response，master 最终收到 completion，那么软件看到的是 fault/abort 或错误状态；底层根因可能是下游 hang，也可能是外设服务时间超过阈值。如果没有 timeout 机制，或者 timeout response 被返回路径堵住，master 看到的就是 no progress。

因此调试要先问两个问题：

- 错误 response 是原生 slave 返回，还是 interconnect/bridge/timeout wrapper 合成。
- response 是否已经被 master 消费，还是生成后堵在返回路径上。

这两个问题决定后续看 decode、slave、bridge、timeout counter、还是 `B/R` channel backpressure。

## 调试 response path 的观察点

- 请求是否到达目标：decode 命中、路由选择、slave select、bridge downstream request。
- 错误在哪里产生：fabric decode、firewall/protection、slave 内部、bridge wrapper、timeout wrapper。
- response 是否匹配原请求：`BID/RID`、ordering rule、outstanding slot。
- response 是否被阻塞：`BVALID && !BREADY`、`RVALID && !RREADY`、返回 FIFO 满。
- 错误是否释放状态：master outstanding、interconnect entry、slave request slot、software wait。
- 软件是否能区分类别：访问错地址、权限失败、设备内部错误、timeout 包装错误。

这些观察点比只看 `BRESP/RRESP` 的最终值更可靠。最终值告诉你系统如何闭合事务；路径上的状态告诉你错误为什么以这种方式闭合。

## 一句话理解

AXI response 是事务闭环的状态载体：它既释放 outstanding，也把成功、decode error、slave error 或合成 timeout 这类结果带回 master；调试时要同时看 response 类别、产生位置和返回路径是否被消费。

## 建模启示

建模 AXI response 时，不能把错误当作异常旁路。每笔写事务都要有 `B` completion，每笔读事务都要有带 response 的 `R` beat；成功 response 也要释放 outstanding、推进 ordering 状态和解除软件等待。

性能模型要保留 response path 的排队和 backpressure。`B` 或 `R` 被 master 堵住，会反压 slave、bridge 或 interconnect，进而限制新的 request 接收。只建 request path 不建 response path，会解释不了“地址发不出去但根因在返回侧”的问题。

功能模型要记录 response 的产生点和映射规则：decode miss 生成什么，slave error 如何返回，timeout wrapper 是否合成 completion，bridge 是否保留或转换错误类别，错误 response 是否携带正确 ID/last 语义。对读 burst，还要检查每个 `RRESP` 和最后一个 beat 的闭合关系。

调试模型要把 timeout、fault、hang 分开：有 response 但状态错误是 fault；有 response 但超出预算是 timeout/fault 组合；没有 response 或 response 无法被消费，才进入 no-progress/hang 排查。这个分类能避免把所有 BUS 问题都误判成“slave 慢”。
