# Transformer / LLM

## 为什么这一页重要

很多早期 CIM 工作以 CNN 为主，但今天判断一条路线是否有现实价值，越来越绕不开 Transformer 和 LLM。

问题在于，LLM 并不是一个单一算子，而是一组瓶颈完全不同的子模块组合。因此不能笼统地问“CIM 适不适合 LLM”，而要逐模块拆。

## 关注模块

- Q / K / V projection
- FFN
- Attention score
- KV cache
- Sampling
- MoE routing

## 模块适配度概览

| 模块 | 适配度 | 原因 |
| --- | --- | --- |
| Q / K / V projection | 中高 | 本质是矩阵乘，映射相对直接 |
| FFN | 高 | 大量 GEMM，结构规整 |
| Attention score | 中 | 依赖动态数据和 softmax 路径 |
| KV cache | 高潜力 | 典型 memory-bound，对 near-memory 很敏感 |
| Sampling | 低 | 控制流和非矩阵操作较多 |
| MoE routing | 中 | 稀疏、不规则访问强，系统复杂度高 |

## 需要先区分 prefill 和 decode

### Prefill

特点：

- 大 batch 或长序列阶段
- 大矩阵乘占比高
- 传统 GPU / NPU 已经很强

结论：

- CIM 未必天然占优
- 只有当数据搬运成本主导时，才可能体现价值

### Decode

特点：

- batch 小
- 每步工作量小但重复次数多
- `KV cache` 访问和带宽压力显著

结论：

- 这是 PIM / CIM 更值得重点看的阶段
- 如果路线能减少 memory-side 访问往返，系统收益更可能成立

## 需要回答的问题

- 哪些模块是 compute-bound
- 哪些模块是 memory-bound
- Prefill 和 Decode 的适配度有什么区别
- near-memory / PIM 是否更适合 KV cache

## 评估 CIM / PIM 时的具体问题

### 针对 FFN 与 projection

要看：

- 是否支持足够位宽
- 矩阵切分是否适配 array 大小
- 权重是否能高效驻留

### 针对 KV cache

要看：

- 减少的是哪一段访存
- host 与 memory-side 的同步成本多高
- 长上下文下收益是否放大

### 针对 attention 全链路

要看：

- score 计算是否只是局部加速
- softmax、mask、normalization 是否仍在 host 上完成
- 数据是否因此被来回搬运两次

## 哪些路线更可能受益

| 路线 | 对 LLM 的更强切入点 |
| --- | --- |
| SRAM-CIM | 小模型、edge LLM、固定子算子加速 |
| DRAM / HBM-PIM | decode、long context、KV cache |
| ReRAM-CIM | 固定权重 MVM，但需警惕精度与更新问题 |

## 一个实用判断标准

如果一个方案声称支持 LLM，至少应继续追问：

1. 支持的是 prefill、decode，还是两者都支持？
2. 加速的是 FFN、attention score，还是 KV cache 路径？
3. 指标是单个 kernel，还是端到端 token latency？
4. 是否包含 host 协同和内存访问成本？

## 后续可补充内容

- Prefill / Decode 拆解
- 长上下文场景分析
- Edge LLM 落地约束
