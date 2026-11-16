# MoE Case Study

上级：[AI Dataflow 系统视角](./README.md)

相关：[Collective Communication](./collective-communication.md)、[Source Routing 与 Compiler-Driven NoC](../03-topology-routing/source-routing-compiler-driven-noc.md)

## 读这页前先统一几个词

- `MoE`：每个 token 只激活部分 expert 的模型
- `dispatch`：把 token 或数据片段送到被选中的 expert
- `gather`：expert 算完后把结果收回来
- `dynamic traffic`：目的地和热点会随输入变化，不像 GEMM 那样规则
- `starvation`：某类流量长期得不到服务，虽然系统整体还在运转

## 为什么 MoE 对 NoC 很“狠”

MoE（混合专家模型）常常把 AI NoC 推向更动态、更不规则的区域，因为它引入了：

- gate（门控）为每个 token 选择少数 expert（专家模块）的分发
- expert 输出的 gather（收集）
- 可能高度不均衡的流量热点

关键不是“所有 token 发给所有 expert”，而是“每个 token 只发给少数被选中的 expert，但不同 token 的选择会随输入变化且可能高度偏斜”。

这使它成为评估 routing（路由）、QoS（服务质量）和 collective（集合通信）价值的高压案例。

## 典型通信形态

- 稀疏、偏斜的 all-to-all-like dispatch
- 稀疏、偏斜的 all-to-all-like gather
- 局部 fan-in / fan-out 突发

这比普通 GEMM（通用矩阵乘法）或规则 pipeline（流水线）更接近网络压力测试。

## 你最该观察的点

- traffic 是否严重偏斜到少数 expert
- source routing（源路由）在动态流量下是否失去优势
- adaptive routing（自适应路由）是否有明显收益
- all-to-all（全交换）是否需要单独 traffic class（流量类别）或 plane

## 常见热点

- 热门 expert 所在 cluster（簇）
- gather 回流路径
- memory response 与 dispatch 混行的共享链路

## 常见 stall

- `SWITCH_CONFLICT`
- `LINK_BUSY`
- `ROUTE_BLOCKED`
- `WAITING_FOR_OTHER_STREAM`

## 一个关键实验

比较：

- deterministic / source routing
- 带有限局部自适应的 routing

观察：

- hotspot link（热点链路）分布
- 尾部延迟
- workload completion time（工作负载完成时间）
- starvation（饥饿）现象

## 为什么它也是 QoS 问题

如果 MoE dispatch / gather 与 control、memory response 完全混跑，系统很容易出现：

- 关键小消息饿死
- barrier（同步屏障）被异常放大
- 端到端时延严重抖动

所以 MoE 不只是 routing 问题，也是 QoS 与公平性问题。

## 具体数值示例

### 配置

| 参数 | 值 | 说明 |
|---|---|---|
| Expert 数量 (E) | 8 | 8 个独立的 FFN expert |
| Top-k | 2 | 每个 token 选 2 个 expert |
| Token batch (B) | 128 | 同时处理的 token 数 |
| Expert 维度 | d_model=4096, d_ff=4096 | 每个 expert 是一个 FFN |
| 数据类型 | FP16 (2B) | |
| Tile 数量 | 16 (4×4 mesh) | 每 2 tile 承载 1 expert |
| Token 维度 | d_model × 2B = 8 KB/token | 每个 token 的数据大小 |

### Dispatch 流量矩阵

```text
128 tokens × top-2 = 256 次 token dispatch

理想均匀分配 (每 expert 收到 256/8 = 32 tokens):

        Expert0  Expert1  Expert2  Expert3  Expert4  Expert5  Expert6  Expert7
Token源  tile0-1  tile2-3  tile4-5  tile6-7  tile8-9  tile10-11 tile12-13 tile14-15
  ─────────────────────────────────────────────────────────────────────────
  均匀:   32       32       32       32       32       32       32       32

每个 expert 收到的数据量: 32 × 8KB = 256 KB
全部 dispatch 数据量: 256 × 8KB = 2 MB
```

### 不均衡场景分析

实际 MoE 中 expert 负载通常不均匀。以 80/20 热点为例：

```text
热点分布: Expert 0 和 Expert 1 各收到 40% tokens

        Expert0  Expert1  Expert2  Expert3  Expert4  Expert5  Expert6  Expert7
均匀:      32      32       32       32       32       32       32       32
80/20:    ~51     ~51      ~26      ~26      ~26      ~26      ~26      ~26

热门 expert 数据量: 51 × 8KB = 408 KB (均匀时的 1.6×)
冷门 expert 数据量: 26 × 8KB = 208 KB (均匀时的 0.81×)
```

### All-to-All 通信量估算

```text
Dispatch (tokens → experts):
  每个 tile 发出 128/16 × 2 = 16 次 dispatch
  每次 dispatch: 8 KB
  每 tile 发出: 16 × 8KB = 128 KB
  全系统: 16 tile × 128 KB = 2 MB

Gather (experts → tokens):
  与 dispatch 对称: 2 MB

总 all-to-all 通信: 4 MB (dispatch + gather)
```

### NoC 压力分析

```text
All-to-all 对 NoC 的压力:

4×4 Mesh, bisection BW = 4 × 32 GB/s = 128 GB/s
All-to-all 数据量: 4 MB
理论最小通信时间: 4 MB / 128 GB/s = 31.25 ns (如果完美利用 bisection BW)

但 all-to-all 不能完美利用 bisection BW:
  实际利用率通常 40%-60%
  实际时间: ~52-78 ns

每个 expert 的计算时间:
  FFN 计算: 32 tokens × 4096 × 4096 × 2 × 2 ops = 2.15G ops
  @ 1 TOPS (per 2-tile expert): 2.15 μs

计算通信比: 2.15 μs / 0.078 μs ≈ 27×
→ MoE 的 dispatch/gather 通信量不大，但 pattern 很恶劣
```

### 为什么 Pattern 比 Volume 更重要

```text
MoE 的 all-to-all 总量只有 4 MB，看起来不大。
但问题在于:

1. 时间集中: dispatch 和 gather 发生在计算前后的极短窗口
   → 瞬时 injection rate 极高

2. 空间不规则: 每个 token 去哪个 expert 是动态决定的
   → 无法提前规划固定路径
   → source routing 的路径可能需要 per-batch 更新

3. 热点不可预测: 哪个 expert 是热门在 inference 时才知道
   → 热门 expert 所在 tile 的入口被冲击
   → 静态负载均衡失效

4. Dispatch 和 gather 对称但时序交叉:
   → gather response 可能和下一批 dispatch 重叠
   → 如果不隔离，互相干扰
```

### 不均衡场景的 NoC 影响

| 场景 | 热门 expert 入口流量 | 冷门 expert 入口流量 | Max/Avg 比 |
|---|---|---|---|
| 均匀 | 256 KB | 256 KB | 1.0 |
| 80/20 轻度不均 | 408 KB | 208 KB | 1.6 |
| 极端不均（1 expert 50%） | 640 KB | 109 KB | 5.9 |

在极端不均场景下：

- 热门 expert 所在的 2 个 tile 的 local port 注入带宽可能不足
- 热门 expert 附近的 mesh 链路利用率远高于平均
- Gather 时热门 expert 的输出路径也同样拥塞
- 整体完成时间被最慢的 expert（热门 expert）决定

### 关键实验参数

| 实验 | 变量 | 观察指标 |
|---|---|---|
| 均匀 vs 不均衡 dispatch | expert 负载分布 | max link utilization、tail latency |
| XY vs adaptive routing | routing 算法 | 热门 expert 周围的拥塞、绕行效果 |
| 共享 NoC vs 隔离 dispatch plane | 网络组织 | dispatch 对 control 的干扰 |
| Expert placement | expert 物理位置 | 热门 expert 在中心 vs 边缘的差异 |

## 本页结论

MoE case 的价值，在于它逼你面对 AI NoC 中最不规整、最容易失衡的流量形态。量化分析表明 MoE 的通信总量不大（~4MB），但 all-to-all pattern 的瞬时冲击、动态热点和负载不均衡使其成为 routing、QoS 和 fairness 的极限压力测试。如果一套 NoC 方案只在规则 GEMM 下表现好，而在 MoE 下明显失稳，那它的系统适用性就是受限的。
