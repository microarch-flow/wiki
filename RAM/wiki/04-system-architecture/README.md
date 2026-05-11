# 系统架构视角

上级：[RAM Wiki 首页](../README.md)

## 本章包含什么

- [地址映射与层级结构](./channel-rank-bank-address-mapping.md)
- [控制器、并行度与页策略](./controller-parallelism-page-policy.md)
- [Row Locality 与 Page Policy 深化](./row-locality-page-policy-deep-dive.md)
- [带宽 vs 延迟](./bandwidth-vs-latency.md)
- [从 SRAM 到 HBM 的系统分层](./cache-dram-hbm-system-view.md)
- [不同系统为什么选不同内存](./why-systems-choose-different-memory.md)
- [内存控制器建模与性能分析](./memory-controller-modeling-analysis.md)

## 本章主线

这一章不再只看单个器件，而是回答：

- 系统怎么组织 channel / rank / bank / row
- 为什么理论带宽很高，实际却不一定能用满
- SRAM、DDR、GDDR、HBM 在完整芯片里各自承担什么角色
