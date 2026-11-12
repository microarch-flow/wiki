# 架构探索方法

上级：[建模与评估](./README.md)

相关：[Topology 与物理布局](../03-topology-routing/topology-layout.md)、[流量模式](../04-ai-dataflow-system/traffic-patterns.md)

## 读这页前先统一几个词

- `parameter sweep`：系统性扫描一组参数，观察趋势而不是只看单点结果
- `baseline`：用来对照的新旧方案中的基准方案
- `sensitivity`：结果对某个参数变化是否敏感
- `root cause`：表面现象背后的真正原因
- `tradeoff`：一个方向变好时，另一个方向通常会付出的代价

## 你现在能开始做什么

基于现有知识，已经可以开始第一阶段探索：

评估 `flat mesh（扁平网格）vs cluster-hierarchical NoC（分簇层次化片上网络）` 在 `GEMM（通用矩阵乘法）/ attention-like traffic（注意力类流量）` 下的：

- link utilization（链路利用率）
- stall breakdown（停顿分类统计）
- average / tail latency（平均/尾部延迟）
- tile utilization（计算单元利用率）

## 推荐的参数扫描顺序

### 第一组：网络结构

- 拓扑
- cluster 大小
- HBM（高带宽内存）/ DMA（直接内存访问）端口位置

### 第二组：router / link

- link width（链路宽度）
- buffer depth（缓冲深度）
- flit size（流控单元大小）
- packet size（数据包大小）
- VC（虚通道）数量

### 第三组：系统交互

- source injection rate（源端注入速率）
- destination FIFO（目的端先入先出队列）深度
- DMA burst size（DMA 突发传输大小）
- tile 消费速率

### 第四组：workload / mapping

- placement（放置策略）
- tensor（张量）切分方式
- 是否 tile-to-tile forwarding
- 是否回写全局存储

## 一个有效的分析套路

1. 先找最先饱和的 link / port
2. 再区分是 credit stall（信用停顿）还是 switch stall（交叉开关停顿）
3. 再判断根因在 NoC、NI（网络接口）、DMA 还是 memory endpoint（存储端点）
4. 最后再改参数，而不是先盲目加宽链路

## 你现在还不该追求什么

- 直接得出“最终芯片最优 NoC”
- 只凭单一 synthetic traffic（合成流量）下结论
- 忽略软件映射和端点行为
- 把第一版 simulator 当成 RTL 替代品

## 一阶洞察与严肃结论的边界

第一版模型可以支持：

- 相对比较
- 热点定位
- 参数敏感性分析
- 明显错误架构的快速排除

但还不够支持：

- 精确 tape-out（流片）级时序结论
- 极细粒度 QoS（服务质量）保证
- 复杂协议 correctness 证明

## 端到端探索实例：GEMM on 16-tile 加速器

下面用一个完整实例演示从选拓扑到最终结论的全过程。

### 问题设定

```text
Workload: GEMM, C[1024×1024] = A[1024×1024] × B[1024×1024], FP16
Hardware: 16 compute tiles, 每 tile 1 TOPS, 256KB SRAM
Memory:   4 个 HBM port, 每个 32 GB/s
Dataflow: weight-stationary, 每 tile 负责 C 的 256×256 子块
```

### Step 1: 选候选拓扑（用 L0 Analytical 筛选）

```text
候选         diameter  avg_hop  bisection_BW        router_area
─────────────────────────────────────────────────────────────────
4×4 mesh       6       2.67    4 × link_bw          16 × A_r5
2×2 conc.mesh  2       1.33    2 × link_bw          4 × A_r8
4-cluster hier 4       2.0     2 × link_bw (inter)  4×A_xbar + 4×A_r5
16-crossbar    1       1.0     N/A (non-blocking)   1 × A_r16
```

用 L0 公式快速排除：
- 16-crossbar 面积 ∝ 16² = 256，太大 → 排除
- 保留前三个候选

### Step 2: 确定流量模式（从 workload 推导）

```text
Weight-stationary GEMM 的 3 类主要流量：

1. Activation broadcast: HBM → 每行 4 tile (multicast)
   每 step: 128KB, 共 4 step
   
2. Partial sum reduce: 每列 4 tile → sink tile (many-to-one)
   每 step: 128KB per tile, 4 tile → 1 sink
   
3. Weight preload: HBM → 每 tile (unicast, 仅初始化)
   128KB per tile, 一次性

关键观察：
  activation 走水平方向（row broadcast）
  partial sum 走垂直方向（column reduce）
  两类流量正交 → mesh 天然适配
```

### Step 3: 对比分析（用 L1 Bandwidth-Aware 模型）

#### 候选 A: 4×4 flat mesh

```text
HBM port 分布: 左边缘 2 个 (R0,0 和 R0,2), 右边缘 2 个 (R3,1 和 R3,3)

Activation broadcast 路径 (HBM0 → row 0):
  HBM0 → R(0,0) → R(1,0) → R(2,0) → R(3,0)
  
  R(0,0)→R(1,0) 链路: 承载 row 0 + row 1 的 activation = 256KB
  
最热链路: HBM port 出口，承载全部 broadcast 流量
  流量 = 128KB × 4 rows / 2 ports = 256KB per port per step
  带宽需求 = 256KB / 33.6μs = 7.6 MB/s → 远未饱和 (32 GB/s)

Partial sum reduce 路径 (col 0: T(0,3)→T(0,2)→T(0,1)→T(0,0)):
  每级传 128KB，tree reduce 每级 2 次
  最热链路: 靠近 sink 的垂直链路

结论: GEMM 在此配置下 compute-bound，NoC 不是瓶颈
```

#### 候选 B: 2×2 concentrated mesh

```text
4 个 router，每个 router 连 4 tile (1 cluster)

Activation broadcast:
  同 cluster 内: 通过 local crossbar，无需走 mesh → 零 mesh 流量
  跨 cluster: 需要走 mesh，但只需 router 间传 1 份

Partial sum reduce:
  同 cluster 内: 4 tile 中有 1 对属于同列 → 本地 reduce
  跨 cluster: reduce 跨 2 个 router → 1 hop

最热链路: router 间链路，承载跨 cluster 流量
  流量更少（本地流量被 cluster 内消化）

结论: 比 flat mesh 更低的 mesh 流量，但 router radix 8 → 面积更大
```

#### 候选 C: 4-cluster hierarchical

```text
4 cluster，每 cluster 4 tile + 1 local crossbar
cluster 间 2×2 mesh

类似候选 B，但 cluster 间拓扑更灵活

结论: 与候选 B 类似的流量特性，cluster 间拓扑更可控
```

### Step 4: 参数敏感度分析

```text
固定候选 A (4×4 mesh)，扫描参数：

参数              变化范围        对 completion time 的影响
───────────────────────────────────────────────────────
link_width       128→256→512    < 1%（本就 compute-bound）
buffer_depth     4→8→16         < 0.5%（几乎无拥塞）
tile_size        128→256→512    ±15%（影响计算通信比）
HBM_port_count   2→4→8          < 1%（HBM 带宽充足）
forwarding on/off                ±5%（减少 reduce 路径回写）

结论: 在这个 GEMM 配置下，NoC 参数几乎不敏感。
      真正影响性能的是 tile 计算能力和 tile 分块大小。
```

### Step 5: 压力测试（改变 workload）

```text
将 GEMM 规模扩大，同时增加通信密度：

场景 1: M=N=K=4096, tile_size=256
  activation 每 step: 256×256×2B = 128KB（不变，但 step 数 ×16）
  通信时间占比上升但仍 compute-bound

场景 2: 增加 MoE dispatch/gather 混合
  dispatch 流量: 动态、不规则
  → 4×4 mesh 的中心链路利用率从 5% 跳到 40%
  → partial sum reduce 延迟被 dispatch 流量干扰
  → 尾延迟从 4μs 跳到 12μs

  → 此时 NoC 参数开始敏感！
  → 需要 traffic class 隔离（separate VC for reduce vs dispatch）
  → 候选 B/C 的 cluster 内隔离变得有价值
```

### Step 6: 结论与建议

```text
探索结论：

1. 纯 GEMM workload 下，16 tile 的三种拓扑性能差异 < 5%
   → 选最简单的 4×4 mesh 即可
   
2. 引入 MoE 等不规则流量后，差异显著
   → cluster-hierarchical 方案在混合 workload 下更稳定
   → 需要至少 2 VC 做 traffic class 隔离
   
3. 真正的设计选择不是"mesh vs hierarchical"
   而是"目标 workload 的流量不规则程度"
   
4. 推荐后续实验：
   - 用 L2 cycle-approximate 模型验证 MoE 混合场景
   - 评估 2 VC vs 4 VC 在混合流量下的收益
   - 评估 separate control NoC 的成本收益
```

### 这个实例展示了什么

| 步骤 | 用了什么 | 对应 DSL/工具链的哪一层 |
|---|---|---|
| 候选筛选 | L0 公式 | DSL analytical evaluator |
| 流量推导 | workload → traffic 转换 | DSL L5 schedule 生成 |
| 对比分析 | L1 bandwidth model | DSL L1-L4 + evaluator |
| 参数敏感度 | parameter sweep | DSL + sweep 脚本 |
| 压力测试 | 改变 workload | DSL L5 替换 |
| 结论 | 综合判断 | 人的决策 |

## 本页结论

对你当前阶段最重要的，不是把所有 NoC 细节一次做完，而是先建立一套能把 workload、mapping 和 NoC 性能连起来的探索框架。端到端实例表明：架构探索的核心价值不在于单一 workload 下的绝对性能，而在于发现"在什么条件下 NoC 设计选择开始产生显著差异"——这恰好是 DSL 的设计空间探索要回答的核心问题。
