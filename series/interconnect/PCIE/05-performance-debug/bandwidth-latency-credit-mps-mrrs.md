---
title: "PCIe 性能参数：带宽、Credit、MPS 与 MRRS 限制什么？"
---

<div id="带宽延迟creditmps-与-mrrs" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# PCIe 性能参数：带宽、Credit、MPS 与 MRRS 限制什么？

上级：[性能与调试](README.md)

性能分析应先确定方向和计数对象，再检查资源限制。Gen 和 lane 数给出链路容量；信用、请求长度和在途窗口决定工作负载能否持续使用容量。它们不是可互相替代的“带宽系数”。

## 带宽不是唯一答案

| 量 | 含义 | 观察边界 |
| --- | --- | --- |
| 原始位速率 | 每 lane、每方向的传输速率 | 例如 GT/s，不能直接当应用 GB/s |
| 编码后带宽上界 | 按指定模式扣编码后的容量 | 尚未扣 TLP 等开销 |
| 有效载荷吞吐 | 实际交付的业务字节除以时间 | 必须注明读写方向和是否含描述符 |
| 端到端延迟 | 从定义的起点到终点的时间 | 读完整返回、命令完成、应用完成不能混用 |

Gen5 x16 的 Non-Flit 编码后单向上界约 63.0 GB/s。它既不是双向合计，也不是有效载荷吞吐；完整代际表见[建模速查](../08-reference/pcie-modeling-params.md)。

## Credit 在提醒什么

信用表示接收端对某类 TLP 承诺的缓冲容量。Header 和 Data 任一所需信用不足，都可能阻止该包发送。增大软件队列不能凭空增加对端信用；收到链路 ACK 也不自动返还信用。

Non-Flit 例子、更新延迟及无限 Completion 通告的边界统一见[信用流控与链路重放](../02-link-transaction-basics/credit-flow-control-and-replay.md)。性能模型须另外表示物理缓冲与接收服务速度。

<div id="mps-和-mrrs-常见影响" class="pcie-legacy-anchor"></div>

## MPS、MRRS 与 RCB 分别约束什么

| 参数 | 约束 | 不代表 |
| --- | --- | --- |
| MPS | 带数据 TLP 的最大载荷 | 每个包实际都有这么多数据 |
| MRRS | 一个 Memory Read 请求的最大长度 | Completion 与请求等长 |
| RCB | 适用 Completion 的合法拆分边界 | 每 64/128 B 必须拆一次，或 CplD 只能这么长 |

构造例：地址 256 B 对齐，读长 256 B，MRRS≥256 B、适用 MPS=256 B、RCB=64 B。Completer 可以返回一个 256 B CplD，也可以返回四个 64 B CplD。数据量相同，但包头数量和接收缓冲需求不同。依据：[AMD RCB 说明](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Read-Completion-Boundary)。

增大 MPS 可能减少大包头部占比，但要满足路径配置和实际数据粒度；增大 MRRS 可能提高每个 Tag 携带的数据量，也可能增加返回缓冲压力。两者都不是无条件调到最大。

<div id="量化小节建模估算用" class="pcie-legacy-anchor"></div>

## 先拆请求，再分析返回包

假设从 `0x1F80` 起读取 512 B，MRRS=512 B。虽然长度没有超过 MRRS，第一段到 4 KiB 边界只剩 128 B，因此不能用一笔跨边界请求完成。可先发 128 B 请求，再从 `0x2000` 发剩余 384 B；这是一个合法分法，实际生成器还可拆得更小。

接下来才对每笔请求分析 MPS 与 RCB 下的 Completion。不能直接用“总长度÷RCB”同时算请求数和返回数。跨边界检查参考 [Altera 事务层错误说明](https://docs.altera.com/r/docs/683514/current/transaction-layer-errors)。

<div id="一个最实用的分析方法" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 一个实用的分析顺序

先记录实际链路速率、宽度和模式；再分开读写载荷方向；然后检查实际请求长度、Tag 占用、完整 RTT、信用等待和返回分包。最后用软件提交及目标内存计数解释空闲与排队。

协议效率计算集中在[建模速查](../08-reference/pcie-modeling-params.md)，并发推导集中在[读延迟文章](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)。本页负责选择参数，而不是重复维护所有公式。
