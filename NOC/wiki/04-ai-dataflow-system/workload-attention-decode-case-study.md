# Attention Decode Case Study

上级：[AI Dataflow 系统视角](./README.md)

相关：[NI / DMA / 存储接口](./ni-dma-memory-interface.md)、[QoS、公平性与 Stall Taxonomy](../05-modeling-evaluation/qos-fairness-stall-taxonomy.md)

## 读这页前先统一几个词

- `decode`：每次生成一个 token 的自回归阶段
- `control / sync`：不是大数据块，但决定执行顺序的小控制消息和同步消息
- `tail latency`：最慢那部分请求的延迟，常用 P99 之类百分位表示
- `WAITING_FOR_OTHER_STREAM`：本地还在等其他依赖流完成，因而暂时不能继续
- `response-sensitive`：总带宽未必大，但对响应返回时间极其敏感

## 为什么 decode 必须和 prefill 分开

decode（逐token解码）的典型特点是：

- 每一步只新增 1 个 token，下一步必须等待上一步结果
- batch（批次）更小
- step-by-step 生成
- latency（延迟）更敏感
- KV cache（键值缓存）访问路径更重要
<<<<<<< HEAD

所以 decode 的核心常常不是”总搬运量大不大”，而是”关键小消息和关键返回路径能否及时走通”。

## 典型 NoC 压力来源

- KV cache 相关读请求与返回
- 小粒度 control / sync（同步）
- compute stage 之间较细粒度的数据依赖
- 多用户推理下的动态流量叠加

## 它更像什么类型的问题

decode 更像：

- memory-centric
- response-sensitive
- latency-sensitive

这和 prefill 的 bulk throughput 主导很不一样。

## 你最该观察的点

- read response 是否被 bulk traffic 压住
- control / barrier（同步屏障）是否被延迟
- QoS（服务质量）是否显著改善 end-to-end latency
- KV cache placement 是否改变热点分布

## 常见 stall

- `NO_CREDIT`
- `EJECTION_BLOCKED`
- `WAITING_FOR_OTHER_STREAM`

decode 场景下，`WAITING_FOR_OTHER_STREAM` 特别值得小心，因为系统级等待很容易被误判成纯 NoC 问题。

## 一个关键实验

比较：

- 所有 traffic 同优先级
- control / response 高优先级

观察：

- tail latency（尾部延迟）
- response return latency
- barrier latency（屏障延迟）
- workload completion time

## 具体数值示例

### 配置

| 参数 | 值 | 说明 |
|---|---|---|
| seq_len (S) | 2048 | 已生成的 token 数（KV cache 长度） |
| d_model | 4096 | 模型隐藏维度 |
| num_heads (H) | 32 | 注意力头数 |
| head_dim (d) | 128 | d_model / num_heads |
| num_layers (L) | 32 | transformer 层数 |
| 数据类型 | FP16 (2B) | |
| Batch size | 1 | 单用户 decode |
| Tile 数量 | 16 (4×4 mesh) | |
| Link width | 256 bit, 1 GHz | 单链路 32 GB/s |

### 单 Token Decode 的计算量

```text
每层 (per layer):
  QKV 投影: 1 × d_model × 3 × d_model × 2 = 1 × 4096 × 3 × 4096 × 2 = 100.7M ops
  Q × K^T:  1 × S × d × 2 × H = 1 × 2048 × 128 × 2 × 32 = 33.6M ops
  Score × V: 1 × S × d × 2 × H = 33.6M ops
  Output 投影: 1 × d_model × d_model × 2 = 33.6M ops

每层总计: ~201M ops

32 层总计: 201M × 32 = 6.4G ops

16 tile @ 1 TOPS → 计算时间: 6.4G / 16T = 0.4 μs
```

### 单 Token Decode 的 KV Cache 读取量

```text
每层 (per layer):
  K cache: S × d × 2B × H = 2048 × 128 × 2 × 32 = 16 MB
  V cache: S × d × 2B × H = 16 MB
  每层 KV 读取: 32 MB

32 层总 KV 读取: 32 × 32 = 1024 MB = 1 GB

这是单个 token decode 需要读取的 KV cache 总量！
```

### Memory-Bound 的量化证据

```text
计算量: 6.4G ops → 0.4 μs (@ 16 TOPS)
KV cache 读取: 1 GB → 1000 μs (@ 1 TB/s HBM)

计算通信比: 0.4 / 1000 = 0.0004

→ Decode 是极度 memory-bound
→ 计算几乎瞬间完成，99.96% 的时间在等内存
→ 每 GB KV cache 只做 6.4G ops → arithmetic intensity ≈ 6.4 ops/byte
→ 远低于 roofline 的拐点（通常 >100 ops/byte）
```

### NoC 在 Decode 中的角色

```text
虽然 NoC 不是带宽瓶颈（HBM 才是），但 NoC 影响:

1. KV cache response 延迟
   每个 tile 请求 KV cache → HBM 返回 response → 经过 NoC 到达 tile
   如果 response 被其他流量阻塞 → tile 计算空等

2. 层间 activation 传递
   每层输出 = 1 × d_model × 2B = 8 KB（极小）
   但延迟敏感：前一层不完成，后一层无法开始

3. Control / barrier
   每层之间需要同步信号
   barrier 延迟直接叠加到 token latency
```

### Response 延迟对 Token Latency 的影响

```text
假设 32 层串行执行，每层:
  HBM read latency: 100ns（HBM 本身）
  NoC response latency: X ns（从 HBM port 到 tile）

Token latency ≈ 32 × (HBM_latency + NoC_latency + compute_latency)
            ≈ 32 × (100ns + X ns + 0.4μs)

如果 NoC response latency 无拥塞: X = 20ns (4 hop × 5ns/hop)
  Token latency ≈ 32 × 520ns = 16.6 μs

如果 NoC response 被 bulk traffic 阻塞: X = 200ns
  Token latency ≈ 32 × 700ns = 22.4 μs (+35%)

如果加了 QoS priority 保护 response: X = 30ns
  Token latency ≈ 32 × 530ns = 17.0 μs (接近理想)
```

### 关键结论

| 观察 | 数值依据 |
|---|---|
| Decode 极度 memory-bound | 计算 0.4μs vs 内存 1000μs |
| KV cache 读取量惊人 | 单 token 1GB（seq_len=2048） |
| NoC 不是带宽瓶颈 | 但 response 延迟直接叠加到 token latency |
| QoS 对 decode 非常重要 | response priority 可减少 35% 的 NoC 引入延迟 |
| KV cache placement 关键 | 距离 compute tile 越近，response latency 越低 |

## 本页结论

decode case 的关键不是追求最大带宽，而是保护关键响应路径和前进所需的小消息。量化分析表明，单 token decode 读取高达 1GB 的 KV cache，是极度 memory-bound 的操作。NoC 的价值不在于提供高带宽，而在于保证 response 和 control 消息的低延迟——QoS priority 可以将 NoC 引入的额外延迟从 200ns 降到 30ns。
=======

所以 decode 的核心常常不是”总搬运量大不大”，而是”关键小消息和关键返回路径能否及时走通”。

## 典型 NoC 压力来源

- KV cache 相关读请求与返回
- 小粒度 control / sync（同步）
- compute stage 之间较细粒度的数据依赖
- 多用户推理下的动态流量叠加

## 它更像什么类型的问题

decode 更像：

- memory-centric
- response-sensitive
- latency-sensitive

这和 prefill 的 bulk throughput 主导很不一样。

## 你最该观察的点

- read response 是否被 bulk traffic 压住
- control / barrier（同步屏障）是否被延迟
- QoS（服务质量）是否显著改善 end-to-end latency
- KV cache placement 是否改变热点分布

## 常见 stall

- `NO_CREDIT`
- `EJECTION_BLOCKED`
- `WAITING_FOR_OTHER_STREAM`

decode 场景下，`WAITING_FOR_OTHER_STREAM` 特别值得小心，因为系统级等待很容易被误判成纯 NoC 问题。

## 一个关键实验

比较：

- 所有 traffic 同优先级
- control / response 高优先级

观察：

- tail latency（尾部延迟）
- response return latency
- barrier latency（屏障延迟）
- workload completion time

## 本页结论

decode case 的关键不是追求最大带宽，而是保护关键响应路径和前进所需的小消息。如果这部分做不好，NoC 可能在链路并不高利用的情况下仍然显著拖慢系统。
>>>>>>> fcf0028b7d9a83d6157907758db21ce2bd383528
