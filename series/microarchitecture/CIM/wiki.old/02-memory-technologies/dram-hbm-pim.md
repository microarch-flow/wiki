# DRAM / HBM-PIM

## 路线定位

这一路线更偏系统级带宽优化，重点不一定是阵列内模拟乘加，而是把处理逻辑推进到 memory-side。

与 SRAM-CIM 或 ReRAM-CIM 相比，`DRAM / HBM-PIM` 更像是在回答另一个问题：

> 当数据已经不得不放在大容量高带宽内存里时，能不能不要每次都把它搬回传统计算核心？

## 为什么它重要

大模型推理、HPC 和部分图计算场景中，真正困难的往往不是片上算力不足，而是：

- 数据量太大，必须驻留在外部内存
- 访问模式频繁触发高带宽需求
- host 与 memory 之间来回搬运代价过高

在这些场景下，PIM 的价值通常来自更好的 `bandwidth` 与 `energy per byte`，而不是单看阵列乘加效率。

## 常见实现位置

这条路线内部也有明显差异，计算逻辑可能放在：

- bank / subarray 附近
- DRAM die 中的特定逻辑区域
- HBM stack 的 logic die 或 base die
- memory module 旁边的 memory-side accelerator

实现位置不同，收益和复杂度也不同。越靠近 memory array，理论上数据搬运越少；越靠近外部 accelerator，设计灵活性越高，但“真近存”的程度会下降。

## 重点问题

- 计算发生在 bank、subarray、logic die 还是 base die
- host、GPU、memory controller 如何协同
- 适合哪些 memory-bound workload
- 编程模型和软件接口是否可用

## 典型优点

- 容量大，适合承载更大模型或更大工作集
- 带宽高，天然适合 memory-bound 任务
- 对 `KV cache`、embedding、稀疏访问、表查询等场景更有吸引力
- 在系统层面更容易体现“少搬一次就是赚”的价值

## 典型限制

- DRAM 工艺不适合复杂逻辑，算子能力通常受限
- 需要改变 memory controller、command interface 或 runtime
- 编程模型更复杂，软件适配成本高
- 很多收益依赖 workload 是否真的 memory-bound

## 更适合哪些 workload

| workload | 适配度 | 原因 |
| --- | --- | --- |
| LLM decode | 中高 | KV cache 和权重访问压力大 |
| Long context inference | 高 | 访存瓶颈突出 |
| Recommendation / search | 高 | 稀疏访问和大表查询多 |
| CNN prefill 式密集计算 | 中 | 传统 GPU / NPU 已很强 |
| HPC memory-bound kernel | 高 | 带宽和数据移动占主导 |

## 和“真正阵列内计算”的区别

不要把 `HBM-PIM` 直接等同于 `ReRAM-CIM` 那类阵列乘加设计。两者的关注点不同：

- `HBM-PIM` 更强调 memory-side processing
- `ReRAM-CIM` 更强调 array-native analog MVM

因此评估口径也应该不同。

## 研究和评估时要特别注意

### 是否真的减少了 host 往返

如果数据最后仍需频繁拉回 GPU / CPU，那么 PIM 的系统价值会显著下降。

### 软件接口是否成熟

需要看是否具备：

- 编译器支持
- memory command 扩展
- runtime 调度能力
- host 协同执行机制

### 指标是否建立在真实系统负载上

如果只是演示局部 kernel，而没有解释与 host 的配合方式，那么结果通常还停留在“局部有效”。

## 关键指标

- memory bandwidth utilization
- energy per byte moved
- host offload ratio
- chip stack integration complexity

## 建议额外记录的指标

- 容量与带宽配置
- host 参与比例
- 支持的指令或算子集合
- memory controller 改动程度
- 系统级延迟收益

## 后续可补充内容

- HBM-PIM 框图
- DRAM command 扩展方式
- 与 CXL memory-side accelerator 的边界
