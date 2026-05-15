# Attention Prefill Case Study

上级：[AI Dataflow 系统视角](./README.md)

相关：[NI / DMA / 存储接口](./ni-dma-memory-interface.md)、[流量模式](./traffic-patterns.md)

## 读这页前先统一几个词

- `prefill`：先把整段输入 prompt 处理完的阶段
- `Q / K / V`：attention 里的 query、key、value 三类张量
- `bulk traffic`：大块、持续时间长、偏吞吐导向的数据流量
- `serialization latency`：一份数据因为要按 flit 逐段发出而花掉的串行化时间
- `overlap`：NoC 搬运和 compute 同时推进，以减少等待

## 为什么 prefill 要单独看

prefill（预填充）的特点是：

- 整段 prompt 已知，因此绝大多数 token 位置可并行处理
- 并行度高
- 数据块大
- 多数路径更接近吞吐型 bulk traffic
<<<<<<< HEAD

因此它和 decode（逐token解码）不应混成一个 attention（注意力机制）流量模型。

## 典型 NoC 压力来源

- Q / K / V 相关数据块搬运
- 中间激活在 tile（计算单元）间流动
- 大量 DMA（直接内存访问）与 compute overlap（重叠执行）
- 输出写回或下一阶段继续转发

## 它更像什么类型的问题

prefill 更像：

- bulk movement
- pipeline overlap
- HBM（高带宽存储器）+ NoC 双重吞吐协同

而不是纯低延迟事务问题。

## 你最该观察的点

- HBM port 与 NoC 哪个先饱和
- source injection（源端注入）是否形成大面积拥塞
- packet size 对 serialization latency（串行化延迟）与头开销的影响
- cluster-hierarchical 方案是否提升局部复用

## 常见热点

- HBM / DMA 注入端附近
- 大块流量共同经过的主干链路
- 跨 cluster 的边界路径

## 常见 stall

- `LINK_BUSY`
- `SWITCH_CONFLICT`
- `NO_CREDIT`

如果端点没建模好，还容易错误低估：

- `EJECTION_BLOCKED`

## 一个关键实验

比较：

- flat mesh（扁平网格）
- cluster-hierarchical NoC（分层片上网络）

在 prefill-like trace 下的：

- 主干链路利用率
- 平均和尾部延迟
- DMA overlap 成功率
- tile utilization（计算单元利用率）

## 具体数值示例

### 配置

| 参数 | 值 | 说明 |
|---|---|---|
| seq_len (S) | 2048 | 输入序列长度 |
| d_model | 4096 | 模型隐藏层维度 |
| num_heads (H) | 32 | 注意力头数 |
| head_dim (d) | 128 | d_model / num_heads |
| 数据类型 | FP16 (2B) | |
| Tile 数量 | 16 (4×4 mesh) | |
| Link width | 256 bit, 1 GHz | 单链路 32 GB/s |
| HBM 带宽 | 1 TB/s（总） | 假设 4 个 HBM port，每个 256 GB/s |

### 计算量

```text
Attention Prefill 的主要计算:

1. QKV 投影 (3 个 GEMM):
   每个: S × d_model × d_model × 2 ops = 2048 × 4096 × 4096 × 2 = 68.7G ops
   三个共: 206.2G ops

2. Attention Score (Q × K^T):
   per head: S × S × d × 2 = 2048 × 2048 × 128 × 2 = 1.07G ops
   32 heads: 34.4G ops

3. Score × V:
   per head: S × S × d × 2 = 1.07G ops
   32 heads: 34.4G ops

4. Output 投影:
   S × d_model × d_model × 2 = 68.7G ops

总计算量: ~344G ops (per layer)
```

### 数据量

```text
1. QKV 投影 weight:
   3 × d_model × d_model × 2B = 3 × 4096 × 4096 × 2 = 96 MB

2. 输入 activation:
   S × d_model × 2B = 2048 × 4096 × 2 = 16 MB

3. Q, K, V 矩阵 (投影后):
   各 S × d_model × 2B = 16 MB，共 48 MB

4. Attention Score 矩阵:
   S × S × H × 2B = 2048 × 2048 × 32 × 2 = 256 MB（所有 head）
   per head: 2048 × 2048 × 2B = 8 MB

5. Output:
   S × d_model × 2B = 16 MB
```

### 通信量分析（16 tile 并行）

假设按 head 维度分配：32 heads / 16 tiles = 2 heads/tile。

```text
每个 tile 需要:
  Q_tile: S × 2d × 2B = 2048 × 256 × 2 = 1 MB
  K_tile: S × 2d × 2B = 1 MB
  V_tile: S × 2d × 2B = 1 MB

QKV 投影 weight (per tile):
  3 × d_model × 2d × 2B = 3 × 4096 × 256 × 2 = 6 MB

HBM → tile 搬运量 (每 tile):
  input activation: 16 MB（或广播后每 tile 取 16 MB）
  weight: 6 MB
  total: ~22 MB

tile → tile 搬运 (如果 attention score 按 S 维度进一步分块):
  attention score per tile: 2048 × 2048 × 2 × 2B / 16 = 1 MB
  但通常 attention score 在 tile 内完成，不需要跨 tile
```

### HBM 带宽需求

```text
总 HBM 读取量:
  weight: 96 MB
  input activation: 16 MB (broadcast 到 16 tile)
  total: ~112 MB

假设计算 + 通信 pipeline:
  16 tile @ 1 TOPS each → 16 TOPS 总算力
  计算时间: 344G / 16T = 21.5 μs

HBM 读取时间 (1 TB/s): 112 MB / 1 TB/s = 112 μs

→ Prefill 是 memory bandwidth-bound
→ HBM 带宽是瓶颈，不是 NoC
→ NoC 的角色是确保 HBM 数据能及时分发到各 tile
```

### 通信量 vs 计算量对比

| 项目 | 量 | 时间 (假设) |
|---|---|---|
| 计算 | 344G ops | 21.5 μs (16 TOPS) |
| HBM 读取 | 112 MB | 112 μs (1 TB/s) |
| NoC 搬运 (activation broadcast) | 16 MB | 0.5 μs (32 GB/s per link) |
| NoC 搬运 (weight 分发) | 96 MB | ~6 μs (分布到 4 HBM port) |

关键观察：

- HBM 带宽是 prefill 的主瓶颈（112 μs >> 21.5 μs）
- NoC 单链路带宽（32 GB/s）远小于 HBM 总带宽（1 TB/s），但 NoC 有多条并行路径
- 如果 4 个 HBM port 同时注入，每个 port 的 4 条 mesh 链路需要分摊 256 GB/s → 每链路 64 GB/s > 32 GB/s → **HBM port 附近的 NoC 链路是局部瓶颈**

### 预期瓶颈

```text
瓶颈 1: HBM port → mesh 注入（HBM 速度 > 单链路带宽 × 出口数）
  → 需要多个 HBM port 分散在 mesh 不同位置

瓶颈 2: Weight broadcast（96 MB 分发到 16 tile）
  → broadcast tree 可显著减少源端链路压力

瓶颈 3: 如果 attention score 需要跨 tile 通信（S 维度分块时）
  → all-to-all pattern，对 bisection BW 有要求
```

## 本页结论

prefill case 的重点，不是事务复杂度，而是大量 bulk traffic 在 memory 和 NoC 之间如何协同。量化分析表明 prefill 是 HBM bandwidth-bound，NoC 的关键作用是确保 HBM 注入的数据能被高效分发，HBM port 附近的链路容易成为局部瓶颈。
=======

因此它和 decode（逐token解码）不应混成一个 attention（注意力机制）流量模型。

## 典型 NoC 压力来源

- Q / K / V 相关数据块搬运
- 中间激活在 tile（计算单元）间流动
- 大量 DMA（直接内存访问）与 compute overlap（重叠执行）
- 输出写回或下一阶段继续转发

## 它更像什么类型的问题

prefill 更像：

- bulk movement
- pipeline overlap
- HBM（高带宽存储器）+ NoC 双重吞吐协同

而不是纯低延迟事务问题。

## 你最该观察的点

- HBM port 与 NoC 哪个先饱和
- source injection（源端注入）是否形成大面积拥塞
- packet size 对 serialization latency（串行化延迟）与头开销的影响
- cluster-hierarchical 方案是否提升局部复用

## 常见热点

- HBM / DMA 注入端附近
- 大块流量共同经过的主干链路
- 跨 cluster 的边界路径

## 常见 stall

- `LINK_BUSY`
- `SWITCH_CONFLICT`
- `NO_CREDIT`

如果端点没建模好，还容易错误低估：

- `EJECTION_BLOCKED`

## 一个关键实验

比较：

- flat mesh（扁平网格）
- cluster-hierarchical NoC（分层片上网络）

在 prefill-like trace 下的：

- 主干链路利用率
- 平均和尾部延迟
- DMA overlap 成功率
- tile utilization（计算单元利用率）

## 本页结论

prefill case 的重点，不是事务复杂度，而是大量 bulk traffic 在 memory 和 NoC 之间如何协同，以及局部复用能否真正减少全局通信压力。
>>>>>>> fcf0028b7d9a83d6157907758db21ce2bd383528
