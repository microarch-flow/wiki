# 流量模式

上级：[AI Dataflow 系统视角](./README.md)

相关：[指标与实验设计](../05-modeling-evaluation/metrics-experiments.md)

## 读这页前先统一几个词

- `synthetic traffic`：人为构造的规则流量，用来先看网络的普遍行为
- `workload traffic`：从真实模型执行过程里抽取出的流量
- `mapping`：把逻辑计算任务分给哪些 tile
- `placement`：这些 tile 或数据块在物理阵列上具体放哪里
- `memory behavior`：端点如何读写、缓存、回填和回流数据；它会直接改写 NoC 压力图

## 为什么 traffic pattern 是核心

NoC 不会脱离 workload 自己产生价值。  
真正把某条链路压满的，不是”mesh（网格拓扑）”这个词，而是 workload（工作负载）、mapping（映射策略）、placement（放置策略）和 memory behavior 的共同结果。

## Synthetic traffic 是必要起点

至少应覆盖：

- uniform random
- hotspot
- neighbor / local traffic
- transpose / permutation

作用：

- 验证模型是否基本正确
- 暴露拓扑和 routing 的一般性行为

## AI-like traffic 才是主战场

### GEMM（通用矩阵乘法）/ weight-stationary（权重驻留）

常见特点：

- 权重或 activation（激活值）广播
- 局部复用强
- cluster 内外流量差异明显

### Attention（注意力机制）prefill（预填充阶段）

常见特点：

- 整段 prompt 已知，绝大多数 token 位置可并行处理
- 大块数据搬运
- 并行度高
- HBM（高带宽存储器）与 NoC 都可能形成压力

### Attention decode（逐token解码阶段）

常见特点：

- 每一步只新增 1 个 token，下一步必须等待上一步结果
- batch 小但访问动态
- KV cache（键值缓存）相关路径更敏感
- 系统瓶颈可能更偏 memory-centric

### MoE（混合专家模型）dispatch / gather（分发/收集）

常见特点：

- all-to-all 倾向更强
- 热点更动态
- adaptive routing（自适应路由）、QoS（服务质量）、collective（集合通信）支持价值更高

## 你最应该关注的 traffic 问题

- tile（计算单元）-to-tile forwarding（前传）是否比回写 HBM 更优
- memory placement 如何改变热点
- 哪些流量必须与 bulk data 隔离
- 哪些流量应支持 multicast（组播）/ reduce（归约）
- destination buffering（目的端缓冲）多深才不会过早触发反压

## Synthetic Traffic 的量化注入模型

每种 synthetic traffic 需要明确 3 个参数：**注入率、空间分布、时间行为**。

### Uniform Random

```text
参数:
  injection_rate: λ (flit/cycle/node)
  spatial: 每个 node 等概率选择任意 dst (dst ≠ src)
  temporal: Bernoulli 或 Poisson 到达

  Bernoulli: 每 cycle 以概率 λ 注入 1 个 packet
  Poisson:   inter-arrival time 服从指数分布，均值 = 1/λ

4×4 mesh 的 saturation throughput (XY routing, wormhole):
  ≈ 0.04-0.06 flit/cycle/node (取决于 packet size 和 buffer depth)
```

### Hotspot

```text
参数:
  injection_rate: λ (flit/cycle/node)
  hotspot_fraction: h (0 < h < 1, 发往 hotspot 的流量占比)
  hotspot_nodes: [list of node ids]
  temporal: Bernoulli

  每个 node 每次注入:
    以概率 h → 发往 hotspot_nodes 中随机一个
    以概率 1-h → 发往非 hotspot 的随机 dst

典型配置: h=0.5, 1 个 hotspot node
  → hotspot node 的入口收到 ≈ N×λ×h 的注入，远超单 node 的弹出能力
```

### Neighbor / Local Traffic

```text
参数:
  injection_rate: λ
  locality_radius: r (只发给曼哈顿距离 ≤ r 的 dst)
  temporal: Bernoulli

  r=1: 只发给直接邻居 (4 个 dst)
  r=2: 发给 2 hop 内的所有 node
  r=∞: 退化为 uniform random
```

### Transpose / Permutation

```text
参数:
  injection_rate: λ
  permutation: (x,y) → (y,x)  或其他固定映射
  temporal: Bernoulli

  Transpose 在 mesh 上会产生对角线方向的流量:
    所有流量从左上到右下 (或反过来)
    中心对角线链路利用率最高
```

## AI-like Traffic 的量化特征

| Pattern | Packet Size | Burst Length | Injection 时序 | 空间分布 |
|---|---|---|---|---|
| Weight broadcast | 大 (1-32 KB) | 长 (连续多 packet) | 计算开始前集中注入 | 1 → N |
| Activation streaming | 中 (256B-4KB) | 中 | 与计算 pipeline 交替 | tile-to-tile sequential |
| Partial sum reduce | 中 (256B-4KB) | 短 | 计算完成后突发 | N → 1 |
| KV cache read | 大 (1-32 KB) | 长 | 每 token 一次 | memory → tiles |
| KV cache response | 大 (1-32 KB) | 长 | HBM latency 后突发返回 | memory → requesting tile |
| MoE dispatch | 小 (1-8 KB) | 短 | 路由决策后突发 | all-to-all (irregular) |
| Control / descriptor | 极小 (32-128 B) | 单 packet | 与计算阶段转换同步 | 1-to-1 或 1-to-all |
| Barrier / sync | 极小 (几 B) | 单 flit | 每个 pipeline stage 一次 | all-to-1-to-all |

### 关键差异

- **Synthetic traffic** 是时间均匀的（每 cycle 等概率注入）
- **AI traffic** 是时间突发的（计算阶段几乎不通信，通信阶段集中爆发）
- 这意味着用 synthetic traffic 的平均利用率估算 AI workload 的性能会**低估峰值拥塞**

## 本页结论

traffic pattern 不是评估用的附加项，而是 NoC 建模的输入主语。没有 traffic，NoC 参数比较大多只剩抽象意义。注入模型的三要素——注入率、空间分布、时间行为——必须明确，否则仿真结果不可复现。AI workload 的突发性和非均匀性是与 synthetic traffic 最本质的差异。
