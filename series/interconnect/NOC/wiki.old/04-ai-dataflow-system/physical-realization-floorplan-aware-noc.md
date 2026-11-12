# Physical Realization 与 Floorplan-Aware NoC

上级：[AI Dataflow 系统视角](./README.md)

相关：[Topology 与物理布局](../03-topology-routing/topology-layout.md)、[Router Pipeline 与 Allocator](../02-router-microarchitecture/router-pipeline-allocator.md)

## 读这页前先统一几个词

- `physical realization`：把抽象 NoC 落成真实版图、时序和布线实现
- `long wire`：跨距离较大的链路；它常常需要额外 pipeline stage
- `timing closure`：让设计在目标频率下满足时序约束
- `frequency`：电路时钟频率；频率越高，单周期越短，布线和逻辑越难收敛
- `floorplan-aware`：做架构判断时显式考虑物理摆放和线长，而不是只看抽象图论指标

## 为什么这页必要

前面的 wiki 主要站在架构建模层。  
但只要你开始认真比较 topology、router radix、link width，很快就会碰到一个事实：

NoC 不是只在逻辑图上存在，它最终要落到 floorplan（版图规划）、长线、时序和功耗上。

## 逻辑最优不等于物理可落地

一个 topology（拓扑）在抽象图上可能平均 hop（跳数）更少，但现实里可能：

- wire 更长
- 时序更难收敛
- 需要更多 pipeline stage（流水级）
- 面积和功耗上升

所以 architecture exploration 的后半段，必须逐步加入 physical awareness。

## 长线为什么重要

router（路由器）之间的 link（链路）不是”零成本边”。  
随着芯片尺寸上升，长线会带来：

- 更大延迟
- 更高能耗
- 更强时序压力

这意味着某些逻辑上“一跳更少”的方案，未必系统上更快。

## Pipeline Link 的意义

当链路太长时，常见做法不是硬扛，而是加 pipeline stage。

结果是：

- 单跳 latency 变大
- credit（信用计数）round-trip 变长
- buffer 深度需求上升

所以 physical realization 会反过来改写你对 buffer、latency、throughput 的判断。

## Router Radix 的物理代价

更高 radix（端口数）的 router 在逻辑上可能减少 hop。  
但代价通常包括：

- crossbar（交叉开关）更大
- allocator（分配器）更复杂
- wiring 更密
- 面积、功耗和频率压力更大

因此 `少 hop` 和 `高频可收敛` 之间常常是 tradeoff，而不是同时免费得到。

## Link Width vs Frequency

想提升带宽，常见有两条路：

- 加宽链路
- 提高频率

但两者都受物理实现约束：

- 更宽的 link 增加布线压力和功耗
- 更高频率增加时序难度

所以实际设计中，带宽扩展往往不是纯参数问题，而是 floorplan 问题。

## Floorplan Compatibility 为什么必须显式讨论

真实芯片里的 tile（计算单元）、SRAM（片上静态存储）、DMA（直接内存访问）、HBM（高带宽存储器）port 并不是抽象网格点。  
它们的相对位置会影响：

- 链路长度
- memory port 距离
- cluster 划分
- 可否做规则 mesh

有些 topology 在论文图里很好看，但与真实版图不兼容。

## 对 Hierarchical NoC 的物理直觉

hierarchical NoC 往往有一个物理上的优势：

- 短距离通信留在本地 cluster
- 长距离流量只走较少的 global link

这能同时帮助：

- 降低全局长线压力
- 增强局部复用
- 降低全局 router 数量

但代价是局部结构更复杂，软件映射也更受限。

## 在架构探索里怎么纳入这一层

第一版不需要做 full physical design，但至少可以加入近似项：

- 链路按物理距离分短 / 长两类
- 长链路增加额外 hop latency 或 pipeline latency
- 不同 topology 估算平均 wire length
- memory port 放置按真实边界位置建模

这已经能显著提升结果可信度。

## 你至少要比较的几个问题

- flat mesh（扁平网格）的全局长线多不多
- hierarchical NoC 是否显著减少长链路依赖
- 更高 radix router 是否真的值得
- memory port 的边缘放置是否拉长关键路径

## 一个高价值实验

对同一 topology，比两组模型：

- 理想每条链路同延迟
- 长链路带额外 pipeline latency

观察：

- tail latency
- credit stall
- 最优 buffer depth 是否变化

如果结论明显变化，就说明物理约束已不可忽略。

## Wire Delay 估算公式

### 基础数据

在先进工艺节点（7nm / 5nm）下：

```text
全局金属层 wire delay ≈ 50-150 ps/mm（取决于金属层和驱动器）
典型估算值: ~100 ps/mm（中间金属层，含 repeater）

换算:
  1 GHz 时钟周期 = 1 ns = 1000 ps
  1 mm wire ≈ 100 ps ≈ 0.1 cycle
  10 mm wire ≈ 1000 ps ≈ 1 cycle → 需要 1 个 pipeline stage
  20 mm wire ≈ 2000 ps ≈ 2 cycle → 需要 2 个 pipeline stage
```

经验规则：**每 ~10mm wire 需要 1 个 pipeline register**（@1 GHz，先进工艺）。

### 实际芯片尺寸参考

| 芯片类型 | 典型面积 | 边长 | 对角线 |
|---|---|---|---|
| 端侧 AI 芯片 | 50-150 mm² | 7-12 mm | 10-17 mm |
| 云端 AI 芯片 | 400-800 mm² | 20-28 mm | 28-40 mm |
| reticle 极限 | ~850 mm² | ~29 mm | ~41 mm |

### Tile Pitch 估算

```text
tile pitch = 相邻 tile 中心距

端侧 (100 mm², 16 tile, 4×4):
  芯片边长 ~10mm
  tile pitch ≈ 10mm / 4 = 2.5 mm
  相邻 link delay ≈ 0.25 cycle → 单周期可达

云端 (600 mm², 64 tile, 8×8):
  芯片边长 ~25mm
  tile pitch ≈ 25mm / 8 = 3.1 mm
  相邻 link delay ≈ 0.31 cycle → 单周期可达（勉强）

云端 (600 mm², 16 tile, 4×4):
  tile pitch ≈ 25mm / 4 = 6.25 mm
  相邻 link delay ≈ 0.625 cycle → 可能需要 pipeline
```

### Pipeline Stages 推导

| 场景 | Link 长度 | Wire delay | Pipeline stages 需求 |
|---|---|---|---|
| 4×4 mesh, 端侧 (tile pitch 2.5mm) | 2.5 mm | 0.25 ns | 0 (单周期) |
| 4×4 mesh, 云端 (tile pitch 6mm) | 6 mm | 0.6 ns | 0-1 |
| 8×8 mesh, 云端 (tile pitch 3mm) | 3 mm | 0.3 ns | 0 |
| 4×4 torus, wrap link (tile pitch 2.5mm) | 7.5 mm | 0.75 ns | 0-1 |
| 8×8 torus, wrap link (tile pitch 3mm) | 21 mm | 2.1 ns | 2 |
| Hierarchical, cross-cluster link | 10-15 mm | 1-1.5 ns | 1 |

### Pipeline Stage 的连锁代价

```text
每增加 1 个 pipeline stage:

1. 单跳 latency: +1 cycle
2. Credit round-trip: +2 cycle（去 1 cycle + 回 1 cycle）
3. Buffer depth 需求: +2 flit（维持 link 满载需要的额外 buffer）
4. Router 面积: buffer 增大 → router 面积增加 ~10-20%
5. 功耗: pipeline register + 更深 buffer → 动态功耗增加

量化示例:
  原始: link latency=1, credit RT=2, buffer_depth=4
  +1 pipeline: link latency=2, credit RT=4, buffer_depth=6
  +2 pipeline: link latency=3, credit RT=6, buffer_depth=8

buffer 从 4 增到 8 → SRAM 面积翻倍 → router 面积增加 ~30%
```

## 本页结论

physical realization 与 floorplan-aware NoC 的价值，在于提醒你：NoC 不是抽象图论游戏。先进工艺下 wire delay ~100ps/mm，每 ~10mm 需要 1 个 pipeline stage。端侧芯片（tile pitch 2-3mm）大多数 link 可以单周期完成；云端芯片在 8×8 以上的 torus wrap link 或跨 cluster link 几乎必然需要 pipeline，由此带来的 buffer 增长和面积代价不可忽略。
