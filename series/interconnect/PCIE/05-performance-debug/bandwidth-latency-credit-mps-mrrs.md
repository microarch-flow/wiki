# 带宽、延迟、Credit、MPS 与 MRRS

上级：[05 性能与调试](./README.md)

相关：[PCIe Read Completion 延迟为什么敏感](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)、[PCIe 建模参数与公式速查](../08-reference/pcie-modeling-params.md)

## 这页在回答什么问题

做 PCIE 性能分析时，最该先看的几个控制量是什么，它们分别影响什么。

## 带宽不是唯一答案

PCIE 性能至少要拆成：

- 链路名义带宽
- 端到端延迟
- in-flight request 深度
- 包粒度和开销

## Credit 在提醒什么

credit 反映链路级可接收能力。它告诉你：

- 不是想发多少就能发多少
- 下游缓冲和返回能力会反向约束吞吐

## MPS 和 MRRS 常见影响

- `MPS` 更像单次发包粒度上限
- `MRRS` 会影响一次 read request 可请求的数据规模

这两者会联动影响：

- 包头开销占比
- completion 分片数量
- device 是否容易把链路灌满

## 一个最实用的分析方法

先问四件事：

1. 链路速率和宽度是否正确
2. read 还是 write 在主导
3. outstanding 是否足够
4. 包大小和返回粒度是否合理

## 量化小节（建模/估算用）

定性判断之外，下面是可以直接套数的部分，完整参数表见 [PCIe 建模参数与公式速查](../08-reference/pcie-modeling-params.md)。

**链路名义带宽**（单向、每 lane，已扣编码开销）：Gen3 ~985 MB/s、Gen4 ~1.97 GB/s、Gen5 ~3.94 GB/s，乘 lane 数即可。例：Gen5 x16 ≈ 63 GB/s。

**实际 payload 决定开销占比**：Non-Flit 模式下，假设每个有数据 TLP 实际载荷 `P`，并假设非载荷占用 `24 B`，效率为 `P/(P+24)`。例如 `P=128 B` 时约 84%。这里的 24 B 是示例模型，不是所有 TLP 的固定开销；header、可选字段、framing、重传和链路模式会改变结果。MPS 只是上限，不是 P。已计入的开销不能重复扣除。

**MRRS / MPS / RCB 与 completion**：MRRS 限制请求大小，MPS 限制带数据 TLP 大小，RCB 限制允许拆分的位置，不限制单个 CplD 为 64/128 B。若 read 为 256 B 且地址 256 B 对齐、MRRS≥256 B、MPS=256 B、RCB=64 B，可以返回一个 256 B CplD，也可以返回四个 64 B CplD。实际数量取决于 completer。

**credit 与缓冲**：Posted / Non-Posted / Completion 分别流控，传统 data credit 单位为 16 B。某类有限信用不足可阻止对应 TLP；对于通告无限 completion credit 的 Endpoint，requester 仍要保障实际 completion 缓冲。详见[建模速查](../08-reference/pcie-modeling-params.md)。

## 一句话理解

PCIE 调优不是只看 x 几和 Gen 几，更要看 credit、请求粒度和 completion 往返能否一起把流水线撑起来。
