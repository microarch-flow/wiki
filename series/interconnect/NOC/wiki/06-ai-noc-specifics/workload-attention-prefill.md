# Workload Attention Prefill

上级：[06 AI NOC Specifics](./README.md)

相关：[Traffic Patterns And Characterization](../05-system-integration/traffic-patterns-and-characterization.md)、[Memory Centric NOC](./memory-centric-noc.md)

## 这页在回答什么问题

这页回答：attention prefill 的并行阶段怎样形成通信，以及何时由带宽、算力或依赖延迟主导。

## prefill 的本质

prefill 的典型特征是：

- 已知整段 prompt
- 并行度高
- 数据块大
- HBM 与 NoC 都要承载明显 bulk traffic

长 prompt 或大 batch 的映射可能突出 bulk 吞吐；短 prompt、小 batch 或权重反复加载时，延迟、权重供给或算力也可能主导。分析应检查：

- HBM 注入与 NoC 分发的匹配
- 大块流量的空间热点
- placement 和 cluster-local reuse

## 它最容易暴露的瓶颈

最常见的不是 router 微小仲裁细节，而是：

- HBM port 附近主干链路
- weight / activation 分发方式
- flat mesh 与更分层组织的差别

这些只是候选瓶颈，应比较各阶段实际 service demand 与可重叠性。

## 为什么它和 decode 必须分开

虽然都叫 attention，但 prefill 和 decode 在 NoC 上问的是不同问题：

- prefill：bulk throughput、injection、distribution、overlap
- decode：逐步依赖、KV 数据服务与 response/control 延迟

把两者混成一个“attention 流量模型”，通常会让结论失真。

## 一个分块通信例子

假设 batch=1、prompt 4 token、1 个 head、head dimension=4、FP16（2 B），Q/K/V 各为 `4×4×2=32 B`。将 token 0–1 的 Q 放 tile 0、token 2–3 的 Q 放 tile 1；各 tile 若需访问全部 K/V，且 K/V 只驻留在各自产生位置，则每个 tile 向另一 tile 接收 K 和 V 各 `2×4×2=16 B`，双向共 64 B payload。每个 Q 块须在所需 K 到达后做 score，再在所需 V 到达后得到输出；实际 causal mask、缓存与分块可减少交换。FlashAttention 式分块可逐块累积而不物化完整 score 矩阵，通信和缓冲随 mapping 改变。多消费者确实复用同一份 K/V 或权重时，multicast 才可能节省共享路径上的重复传输。

## multicast 和 memory placement 在这里更值钱

如果某些 activation 或 weight 需要被多处消费，那么：

- multicast 的收益会更容易体现
- HBM port 的分布和 address interleaving 会很关键

因为这类大块流一旦用普通重复单播，很快会把靠近 source 的路径打热。

## 一句话理解

prefill 的并行度和数据块大小由 prompt、batch、head、算法与映射决定；其瓶颈须按具体工作量和服务资源验证。

## 建模启示

prefill trace 至少要显式包含：

- 大块 burst
- source-side concentration
- HBM port placement
- phase overlap

评估时优先看：

- main-trunk utilization
- injection hotspot
- overlap 成功率
- workload completion time

这比单看平均 packet latency 更贴近 prefill 的真实问题。
