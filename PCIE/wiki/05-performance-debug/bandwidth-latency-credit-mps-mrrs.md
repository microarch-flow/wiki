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

**MPS 决定 TLP 开销折扣**：每个 TLP 固定开销约 24 字节（framing + seq + header + LCRC），于是

```
有效吞吐 = 名义带宽 × MPS / (MPS + 24)
```

MPS=128 → ~84%，MPS=256 → ~91%，MPS=512 → ~95%。这才是「包头开销占比」的量化形式。

**MRRS / RCB 决定 completion 拆分**：单个 read 最多请求 MRRS 字节，返回数据在 RCB（64/128 字节）边界拆成多个 completion，每个各带一份 header 开销 —— 拆得越碎，read 路径有效效率越低。

**credit 是可计算的背压**：Posted / Non-Posted / Completion 各有独立信用池，data credit 单位 = 16 字节（4DW）。某类信用耗尽即停发，与链路是否空闲无关。

## 一句话理解

PCIE 调优不是只看 x 几和 Gen 几，更要看 credit、请求粒度和 completion 往返能否一起把流水线撑起来。
