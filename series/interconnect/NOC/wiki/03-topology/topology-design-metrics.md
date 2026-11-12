# Topology Design Metrics

上级：[03 Topology](./README.md)

相关：[Mesh And Torus](./mesh-and-torus.md)、[Topology Selection Framework](./topology-selection-framework.md)、[Credit Based Flow Control](../02-router-microarchitecture/credit-based-flow-control.md)

## 这页在回答什么问题

比较拓扑时，需要同时定义图、流量权重、链路方向和物理布局。平均 hop 只描述距离，不能单独预测拥塞、能耗或延迟。

## 指标与边界

| 指标 | 定义 | 使用条件 |
| --- | --- | --- |
| diameter | 所有节点对的最短路径边数的最大值 | 先指定图是否有向及可达性 |
| 平均最短距离 | 节点对距离按指定权重求平均 | 明确是否包含源等于目的、端点数和权重 |
| bisection capacity | 将节点分成规定两半的切面容量 | 说明取最小切面还是特定切面、方向及每链路带宽 |
| radix | 每 router 的网络端口与本地端口数 | 边界节点和集中端点数可能不同 |
| path diversity | 给定源目的和长度约束下的合法路径数量 | 区分图上路径和 routing 允许的路径 |
| 最大线长 | placement 下链路端点的物理距离 | 需给布局、走线与 pipeline；hop 不是物理距离 |

## 一个可复算的 4×4 例子

假设 16 个 router 各接一个端点，相邻 router 间每方向有容量 W 的全双工链路。mesh 无 wrap；torus 在两个维度均首尾相连。均值按 240 个**有向、非自身**源目的对等权计算，只计 router 间边；不计端点连接。

| 指标 | 4×4 mesh | 4×4 torus |
| --- | --- | --- |
| diameter | 6 | 4 |
| 平均最短距离 | `8/3 ≈ 2.667` hop | `32/15 ≈ 2.133` hop |
| 垂直等分切面、单方向容量 | `4W` | `8W` |
| 内部 router 最大 radix（含 1 local） | 5 | 5 |

若把 16 个自身对也计入平均值，分别为 2.5 和 2 hop。对于 mesh，位移绝对值为 `dx,dy` 时，图上最短路径数为组合数 `C(dx+dy,dx)`；例如 `(0,0)→(2,2)` 有 6 条，但 XY 路由只允许其中一条。torus 的最短路径数还取决于绕环方向和相等距离的处理，不能用一个常数代替。切面容量是链路上限，不证明任何具体 collective 能达到。

若采用未折叠、相邻节点间距为一个 router pitch 的方阵布局，4×4 torus 的 wrap 直线跨度为 3 pitch；折叠布局可缩短 wrap，但也可能改变普通边长度。concentrated mesh 的 router pitch 要由多个 tile 的实际 placement 决定，不能等同单 tile pitch。

## 其他拓扑不能只由 N 推导

- **Ring**：邻接、方向、并行边和 placement 决定距离、切面及长线。
- **Tree/fat-tree**：必须列出每层 switch、端口和上行容量；“k 叉、L 层”不足以唯一确定多路径图或切面。
- **Dragonfly**：组内全连接、每 router 有 `p` 个端点、`a−1` 个本组邻居端口和 `h` 个全局端口时，radix 为 `p+a−1+h`。若要求每组与其余 `g−1` 组各至少有一条直连，而该组仅有 `a×h` 个全局端口，则 `g−1≤a×h`。经典最大规模构造中每对组恰有一条直连且端口用满，取 `g=ah+1`；若不要求组间两两直连，此界不适用，组可以连成更大的环。具体边连接决定距离和切面。见 [原论文](https://research.google.com/pubs/archive/34926.pdf)。

给定邻接表后，可用 BFS 求最短距离、组合枚举或图算法求指定切面，再依端点 placement 和 workload 权重统计。不要把未定义图的 fat-tree、dragonfly 公式或 AllReduce 排名当作通用结论。

## 从结构到时序和容量

每条物理链路应分别根据实际长度、工艺、驱动、寄存器边界和时钟确定延迟。传播时间不能直接 `ceil(线长/信号速度)` 就断言需要多少 pipeline 或 hop；采样、setup、布线及可靠性约束仍需实现校准。前向传输、下游排队/消费与 credit 返回分别决定往返 R。

对目标单 VC 速率 `r` flit/cycle，固定 R 下可用 `ceil(r×R)` 作为稳态窗口容量估算；实际需求还依仲裁、采样、突发和服务而变。它不是任意负载的充分条件。完整时间边界见 [credit 流控](../02-router-microarchitecture/credit-based-flow-control.md)。

对于 collective，先给算法、数据大小、参与者 placement、每阶段物理路径与共享资源，再计算每个瓶颈的服务量和阶段延迟。仅有 average hop 和 bisection 不足以直接排序或证明总时间下界。

## 建模启示

记录 `adjacency`、每条链路方向/带宽/延迟、端点映射、routing 允许集合和流量权重；派生距离、可用路径与切面。物理参数和拥塞状态应来自实现或可复现实验，而不是从拓扑名字推断。
