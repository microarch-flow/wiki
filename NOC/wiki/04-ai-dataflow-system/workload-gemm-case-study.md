# GEMM Case Study

上级：[AI Dataflow 系统视角](./README.md)

相关：[流量模式](./traffic-patterns.md)、[Collective Communication](./collective-communication.md)

## 读这页前先统一几个词

- `GEMM`：矩阵乘矩阵，是很多 AI 芯片最常见的核心算子
- `weight-stationary`：尽量让权重留在本地，激活值在网络里流动
- `output-stationary`：尽量让输出部分和留在本地累加
- `forwarding`：结果不先回全局存储，而是直接转给下游 tile
- `partial sum`：还没归并完成的中间累加结果

## 为什么先看 GEMM
<<<<<<< HEAD

GEMM（通用矩阵乘法）是最适合作为 NoC 第一批 workload（工作负载）case study 的对象，因为它：

- 结构规则
- 映射方式相对清楚
- 容易暴露 broadcast（广播）、forwarding（前传）、reduce（归约）等典型通信

## 典型数据流问题

你至少要先明确：

- 权重是否常驻本地
- activation（激活值）是广播还是分片送达
- partial sum（部分和）是否本地归约还是跨 tile（计算单元）归约
- 输出是否直接 forward 到下一阶段

## 常见通信形态

- one-to-many：权重或 activation 分发
- point-to-point：tile pipeline forwarding
- many-to-one：partial sum gather（收集）

## 对 NoC 最敏感的架构选择

- weight-stationary（权重驻留）vs output-stationary（输出驻留）
- tile placement（放置策略）
- cluster 内共享 SRAM 的大小
- 是否采用 tile-to-tile forwarding

## 常见热点位置

- 靠近 source 的 broadcast path
- partial sum 汇聚点
- cluster 间边界链路
- HBM（高带宽存储器）/ DMA（直接内存访问）注入端

## 建模时至少要扫的参数

- packet size（数据包大小）
- flit size（流控单元大小）
- local SRAM（本地静态存储）大小
- cluster 大小
- forwarding 开关
- multicast（组播）是否存在

## 你最可能看到的 stall

- `SWITCH_CONFLICT`：多个 tile 同时抢共享输出
- `NO_CREDIT`：destination FIFO 或聚合路径堵住
- `EJECTION_BLOCKED`：本地累加或写回接口来不及消费

## 一个高价值对比实验

比较：

- 回写 SRAM / HBM 再读出
- 直接 tile-to-tile forwarding

观察：

- link utilization（链路利用率）
- latency（延迟）
- producer stall（生产者停顿）
- 总工作完成时间

## 具体数值示例

### 配置

| 参数 | 值 | 说明 |
|---|---|---|
| 矩阵规模 | M=N=K=1024 | C[1024×1024] = A[1024×1024] × B[1024×1024] |
| 数据类型 | FP16 (2B) | 每个元素 2 字节 |
| Tile 数量 | 16 (4×4 mesh) | 每个 tile 处理一个子矩阵块 |
| Tile 分块 | 256×256 per tile | 每个 tile 负责输出矩阵的 256×256 子块 |
| Dataflow | weight-stationary | 权重常驻 tile 本地 SRAM |
| Link width | 256 bit, 1 GHz | 单链路带宽 32 GB/s |

### 每个 Tile 的计算量

```text
每个 tile 计算: C_tile[256×256] = A_tile[256×K] × B_tile[K×256]

实际分步: 将 K=1024 分成 4 个 step，每 step K_step=256
  每 step 计算量: 256 × 256 × 256 × 2 = 33.6M ops (MAC 算 2 ops)
  总计算量: 33.6M × 4 = 134.2M ops

假设 tile 算力 = 1 TOPS (FP16):
  每 step 计算时间: 33.6M / 1T = 33.6 μs
  总计算时间: 134.2 μs
```

### 通信量分析

#### Weight 加载（每 step）

```text
每个 tile 每 step 需要的 weight:
  B_tile[256×256] × 2B = 128 KB

如果 weight-stationary 且权重预加载到本地 SRAM:
  运行时 weight 通信 = 0（已预加载）

如果需要每 step 从 HBM 加载:
  16 tile × 128 KB = 2 MB / step
  4 step 共 8 MB
```

#### Activation 分发（每 step）

```text
Weight-stationary 映射:
  矩阵 A 按行分给 4 行 tile，每行 tile 共享同一段 A
  A_row[256×256] × 2B = 128 KB / step / row

分发方式:
  方式一 (unicast): 每行 4 个 tile 各自从 HBM 读取 → 4 × 128KB = 512 KB / row
  方式二 (broadcast): 读一份 128KB 广播给同行 4 个 tile → 128 KB / row

broadcast 节省的带宽: 512 - 128 = 384 KB / row / step
全矩阵: 384 KB × 4 rows × 4 steps = 6.1 MB 节省
```

#### Partial Sum Reduce（每 step）

```text
Weight-stationary 映射下，每列 4 个 tile 产生同一输出块的 partial sum:
  每个 tile 的 partial sum: 256 × 256 × 2B = 128 KB

Reduce 方式:
  方式一 (endpoint reduce): 4 个 tile 各发 128KB 到 sink tile
    sink 收到: 4 × 128KB = 512 KB，做 3 次加法
    sink 入口带宽压力: 512 KB / step

  方式二 (tree reduce): 两两先加，再合并
    第一级: 2 对 tile，各传 128KB → 2 个中间结果
    第二级: 2 个中间结果 → 1 个最终结果
    每级传输: 128 KB × 2 = 256 KB
    sink 只收 128 KB
```

### 计算通信比

```text
每 step:
  计算量: 33.6M ops
  通信量 (activation broadcast): 128 KB = 131072 B
  通信量 (partial sum reduce): 128-512 KB

计算时间 (1 TOPS): 33.6 μs
通信时间 (activation, 32 GB/s link): 128KB / 32 GB/s = 4 μs
通信时间 (reduce, 32 GB/s link): 128KB / 32 GB/s = 4 μs

计算通信比: 33.6 / max(4, 4) = 8.4×

→ 这个配置下 GEMM 是 compute-bound（计算受限）
→ NoC 不是主瓶颈，但 reduce 路径如果拥塞可能变成瓶颈
```

### 预期瓶颈位置

```text
4×4 Mesh, weight-stationary:

    HBM port                  HBM port
       ↓                        ↓
    T(0,0)──T(1,0)──T(2,0)──T(3,0)  ← activation row 0
       |       |       |       |
    T(0,1)──T(1,1)──T(2,1)──T(3,1)  ← activation row 1
       |       |       |       |
    T(0,2)──T(1,2)──T(2,2)──T(3,2)  ← activation row 2
       |       |       |       |
    T(0,3)──T(1,3)──T(2,3)──T(3,3)  ← activation row 3
       ↑                        ↑
    reduce col 0            reduce col 3

热点 1: HBM port → row 0 的 broadcast 路径（靠近 HBM 的链路）
热点 2: 每列底部 tile 的 reduce 汇聚（ejection 压力）
热点 3: broadcast 和 reduce 在 mesh 中心重叠的链路
```

### 关键实验参数

| 实验 | 变量 | 观察指标 |
|---|---|---|
| Broadcast 方式 | unicast vs multicast tree | 源端链路利用率、总完成时间 |
| Reduce 方式 | endpoint vs tree reduce | sink ejection stall、tail latency |
| Tile 分块大小 | 128×128 vs 256×256 vs 512×512 | 计算通信比、NoC 压力 |
| Cluster 化 | flat 4×4 vs 2×2 concentrated | cluster 内外流量比、总吞吐 |

## 本页结论

GEMM 的价值不只是”容易建模”，而是它能帮助你把 broadcast、forwarding、reduce 这三类 AI NoC 基本流量一次串起来。量化分析表明，在典型配置下 GEMM 是 compute-bound，但 partial sum reduce 路径和 activation broadcast 路径在高 utilization 时容易成为瓶颈。
=======

GEMM（通用矩阵乘法）是最适合作为 NoC 第一批 workload（工作负载）case study 的对象，因为它：

- 结构规则
- 映射方式相对清楚
- 容易暴露 broadcast（广播）、forwarding（前传）、reduce（归约）等典型通信

## 典型数据流问题

你至少要先明确：

- 权重是否常驻本地
- activation（激活值）是广播还是分片送达
- partial sum（部分和）是否本地归约还是跨 tile（计算单元）归约
- 输出是否直接 forward 到下一阶段

## 常见通信形态

- one-to-many：权重或 activation 分发
- point-to-point：tile pipeline forwarding
- many-to-one：partial sum gather（收集）

## 对 NoC 最敏感的架构选择

- weight-stationary（权重驻留）vs output-stationary（输出驻留）
- tile placement（放置策略）
- cluster 内共享 SRAM 的大小
- 是否采用 tile-to-tile forwarding

## 常见热点位置

- 靠近 source 的 broadcast path
- partial sum 汇聚点
- cluster 间边界链路
- HBM（高带宽存储器）/ DMA（直接内存访问）注入端

## 建模时至少要扫的参数

- packet size（数据包大小）
- flit size（流控单元大小）
- local SRAM（本地静态存储）大小
- cluster 大小
- forwarding 开关
- multicast（组播）是否存在

## 你最可能看到的 stall

- `SWITCH_CONFLICT`：多个 tile 同时抢共享输出
- `NO_CREDIT`：destination FIFO 或聚合路径堵住
- `EJECTION_BLOCKED`：本地累加或写回接口来不及消费

## 一个高价值对比实验

比较：

- 回写 SRAM / HBM 再读出
- 直接 tile-to-tile forwarding

观察：

- link utilization（链路利用率）
- latency（延迟）
- producer stall（生产者停顿）
- 总工作完成时间

## 本页结论

GEMM 的价值不只是“容易建模”，而是它能帮助你把 broadcast、forwarding、reduce 这三类 AI NoC 基本流量一次串起来。
>>>>>>> fcf0028b7d9a83d6157907758db21ce2bd383528
