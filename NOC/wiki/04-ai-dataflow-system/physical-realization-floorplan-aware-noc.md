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

## 本页结论

physical realization 与 floorplan-aware NoC 的价值，在于提醒你：NoC 不是抽象图论游戏。  
真正靠谱的架构判断，最终都要问一句：这套连法在真实芯片上，线怎么走、频率怎么收、长链路怎么付代价。
