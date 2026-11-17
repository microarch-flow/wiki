---
title: "PCIe 读取为何需要并发：完整返回时间与 Tag 窗口"
---

<div id="pcie-read-completion-延迟为什么敏感" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# PCIe 读取为何需要并发：完整返回时间与 Tag 窗口

上级：[数据路径、DMA 与中断](README.md)

设备读主机内存时，请求发出后还要等数据返回。若待完成请求数量有限，链路即使很宽，也可能被请求窗口限制。分析前先区分实际平均在途数、硬件槽容量和软件队列深度。

<div id="一个最短链条" class="pcie-legacy-anchor"></div>

## RTT 到哪个事件为止

本文的请求 RTT 从 Memory Read 发出，计到全部所需数据成功返回、对应请求槽可回收。它包括请求路径、目标服务、排队及 Completion 返回。第一笔 CplD 到达只表示开始返回，不一定释放 Tag。

教学例：512 B 请求分成两个 256 B CplD，首包在 0.6 µs 到达，末包在 1.0 µs 到达。用于请求槽占用的 RTT 是 1.0 µs。若改用首包延迟，模型会高估有限槽数的吞吐能力。

<div id="量化小节littles-law" class="pcie-legacy-anchor"></div>

## 从稳态计数推导吞吐

在同一稳定采样窗口内，设请求完成率为 λ，平均完整 RTT 为 T，时间平均在途数为 N̄，每请求平均有效字节为 S。无持续积压增长，且统计对象和成功完成口径一致时，Little 定律给出：

> **N̄ = λT，B = λS，因此 B = N̄S / T。**

这里 B 是该请求流交付的有效字节率。不能把所有协议流量计入 N̄，却只把某个业务的字节计入 B；错误重试和未结束的瞬态也需单独处理。

<div id="为什么它比-write-更敏感" class="pcie-legacy-anchor"></div>
<div id="最值得记住的判断" class="pcie-legacy-anchor"></div>

## 用槽容量预测需要多少并发

若 Requester 最多允许 N<sub>cap</sub> 笔请求在途，则 N̄ ≤ N<sub>cap</sub>。给定目标吞吐 B<sub>target</sub> 和该负载下的 T、S，至少需要：

> **N<sub>cap</sub> ≥ ⌈B<sub>target</sub> × T / S⌉。**

这只是必要的容量条件。预测还须满足请求供给、请求方向带宽、返回方向带宽、目标服务和完成缓冲等限制。RTT 会随负载变化，不能无限提高槽数却把排队时延固定不变。

## 一个可复算的例子

假设 Gen4 x8，目标有效吞吐 12.8 GB/s，完整 RTT=1 µs，每请求有效数据 512 B；GB 采用十进制。

> 所需容量下界 = ⌈12.8 × 10⁹ × 10⁻⁶ / 512⌉ = **25 笔请求**。

Gen4 x8 仅扣编码后的单向上界约 15.75 GB/s；实际可用带宽还要扣协议开销。若设备只有 16 个可用槽，且仍采用上述 RTT 与长度，窗口上界为 8.192 GB/s，无法达到目标。若有 32 个槽，只能说明窗口条件有余量，不能保证达到 12.8 GB/s。

<div id="最常见的四类瓶颈" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 哪个参数改变了等待

| 变化 | 可能影响 | 必须同时检查 |
| --- | --- | --- |
| 请求变小 | 同样字节率需要更多请求 | 4 KiB 边界、剩余长度、生成策略 |
| 返回末片更晚 | 槽占用时间增加 | Completion 拥塞、目标服务 |
| 软件队列加深 | 可能改善请求供给 | Requester 是否仍只有固定少量 Tag |
| 增大 MRRS | 允许更长请求 | 实际长度、返回分包和接收缓冲 |

普通写不等待逐笔事务 Completion，但仍受信用与接收服务约束。不能用本读窗口公式直接描述所有写瓶颈。

Tag 能力、分包规则和带宽表集中在[建模速查](../08-reference/pcie-modeling-params.md)，观测方法见[瓶颈拆解](../05-performance-debug/host-device-bottleneck-breakdown.md)。Little 定律的原始来源：[Little，1961](https://doi.org/10.1287/opre.9.3.383)。
