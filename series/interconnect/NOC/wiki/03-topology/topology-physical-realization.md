# Topology Physical Realization

上级：[03 Topology](./README.md)
相关：[Mesh And Torus](./mesh-and-torus.md), [../07-evaluation-methodology/power-area-modeling.md](../07-evaluation-methodology/power-area-modeling.md)

## 这页在回答什么问题

为什么很多 topology 在图论上看起来很强，一落到真实 floorplan 就开始失真，以及 metal layer、线长、pipeline link 和拥塞会怎样重写前面的结论。

这页是 `03-topology` 的落地页。前面几页讨论的是“图怎么连”，这一页讨论的是“图怎么放上硅片”。

## 逻辑最优不等于物理可落地

纯 topology 讨论常默认所有边都是同价、同长、同频率的。芯片上这很少成立。

真实物理世界里，链路代价至少受这些因素控制：

- 跨度有多长
- 要穿过哪些拥塞区域
- 是否要插 pipeline
- 需要占多少金属资源

所以当你比较 topology 时，真正危险的错误不是算错 hop，而是默认每个 hop 的成本都一样。

## 长线为什么会重新定义 topology

长线的直接后果通常有三个：

- 延迟增加
- 功耗上升
- 可能必须插 pipeline stage

一旦插 pipeline，影响就不止是多一拍。它还会让：

- credit round-trip 变长
- input buffer 深度需求上升
- 最坏延迟分析更松

所以一条长链路的代价，常常不是“这一跳慢一点”，而是一整串 router/link 参数要跟着改。

## Mesh 为什么在这里又加分

mesh 最被低估的优点之一，就是绝大多数链路长度规则、相近、好布线。

这意味着：

- 很多链路不需要特殊 pipeline
- per-hop cost 更接近均匀
- 版图团队容易预估资源
- 架构模型与物理模型更容易对齐

这不是小优点。对于大芯片和 deterministic NPU，这种规则性会直接减少“模型里很好，后端一落地全变”的风险。

## Torus、fat-tree、高-radix 结构为什么更容易吃亏

这些结构的问题不在逻辑图，而在少数链路或节点特别突出：

- torus 的 wrap-around 长边
- fat-tree 的高层汇聚节点
- high-radix 拓扑的大路由节点

它们往往会在物理层形成：

- 超长线
- 布线集中区
- 非规则宏布局

这会导致逻辑上少 hop 的结构，在物理上变成“单跳很重、少数区域很难收敛”的结构。

## Topology 和 floorplan 为什么要一起看

NoC 不是悬浮在芯片之上的抽象图。它要连的是真实对象：

- tile array
- SRAM 宏
- HBM / DMA / memory port
- control island

这些对象的位置，反过来决定 topology 是否自然。比如：

- 二维 tile array 天然偏向 mesh
- memory port 若集中在边缘，会拉出方向性热点
- cluster 边界若本就存在，共享 gateway 的集中结构就更自然

所以 topology 的一个隐藏指标其实是：它和 floorplan 的“语义对齐”程度有多高。

## 一个典型误区：把长线只算进 link latency

这不够，因为长线往往还会改变结构参数本身。

举例，某 topology 因为长链路需要额外 2 级 pipeline：

- hop latency 增加
- credit round-trip 增加
- buffer depth 从 4 变成 8
- router 面积上升

如果你只在模型里把链路加 2 cycle，而不把 buffer 和功耗也联动调整，就会系统性低估这类 topology 的实现成本。

## 什么时候应该在架构层提前纳入物理实现

不是所有阶段都要上 detailed floorplan，但这些信号一出现，就该把物理层显式带入：

- 比较对象包含长 wrap-around 或高层跨区链路
- 你在讨论 1GHz 以上且芯片尺寸较大
- memory / HBM 端口分布明显不均
- chiplet 或跨 die 边界已经进入方案空间

这时“纯 topology 筛选”已经不够，至少需要一个 physical penalty 模型。

## 常见误解

常见误解：物理实现是后端问题，前期先忽略。  
实际上：对 NoC 拓扑来说，很多优劣恰恰来自物理实现约束；忽略它会把方案排序做反。

常见误解：长线的影响只是一点额外延迟。  
实际上：它常常连带改变 pipeline、credit、buffer 和功耗模型。

## 一句话理解

片上 topology 的真正筛选，不是“哪张图最短”，而是“哪张图在真实 floorplan 下还能保持自己的逻辑优势”。

## 建模启示

一阶物理抽象至少应加入：

```text
PhysicalLink {
  wire_span
  extra_pipeline_stages
  energy_per_transfer
}
```

并把它联动到：

- `per_hop_latency`
- `credit_round_trip`
- `required_vc_depth`

如果只做逻辑筛选，可以把 `wire_span` 粗略分成 `short/medium/long` 三档；如果开始比较 torus、fat-tree、chiplet gateway 等方案，就不能只留抽象档位，至少要让长链路显式改变 buffer 需求和 link latency，否则排序会失真。
