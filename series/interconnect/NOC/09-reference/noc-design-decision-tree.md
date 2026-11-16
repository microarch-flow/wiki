# NOC Design Decision Tree

上级：[09 Reference](./README.md)

相关：[Topology Selection Framework](../03-topology/topology-selection-framework.md)、[Architecture Exploration Loop](../07-evaluation-methodology/architecture-exploration-loop.md)

## 这页在回答什么问题

这页回答：面对一个新的 NoC 设计问题，应该先沿什么判断路径收敛，而不是同时在 topology、routing、QoS、memory、simulator 上四处发散。

## 决策树主线

### Step 1: 先判断主流量是什么

先问：

- 规则 bulk flow 为主？
- memory response 为主？
- collective 为主？
- dynamic all-to-all 为主？

如果这里没判断清楚，后面几乎都会跑偏。

### Step 2: 再判断主要瓶颈层级

先区分：

- network core
- endpoint / NI
- local SRAM / memory controller
- workload dependency / scheduling

如果根因不在 network core，先别急着改 topology。

### Step 3: 判断 path diversity 是否真的有价值

先问：

- topology 有明显多路径吗？
- 热点是静态映射问题还是动态拥塞问题？

如果多路径不多、热点又偏静态，那么 deterministic / placement 优化通常比 adaptive routing 更优先。

### Step 4: 判断是否需要 traffic isolation

如果出现：

- control 被 bulk 淹没
- response 关键路径被拖慢
- collective 干扰普通数据流

那就优先考虑：

- class 划分
- VC 隔离
- 多物理网络

### Step 5: 判断是否要上 collective 支持

如果主流量里有：

- 高频 broadcast
- 高 fan-in reduce
- all-reduce

再问：

- 软件复制 / flat gather 的重复占用是不是已经很重？
- 分层 collective 能不能明显降热点？

### Step 6: 判断 compiler/runtime 是否应参与

如果流量可预知、placement 可控、阶段清晰，就优先考虑：

- static scheduling
- source routing
- route / class / overlap 协同

如果流量高度动态，再考虑提升运行时灵活性。

## 一个更具体的速查版本

### 如果是 GEMM-like

优先看：

- broadcast / forwarding / reduce
- local SRAM 复用
- hierarchical 是否值

### 如果是 decode-like

优先看：

- request / response 分离
- response QoS
- memory placement
- ejection 能力

### 如果是 MoE-like

优先看：

- dynamic hotspot
- fairness
- path diversity
- dispatch / gather 隔离

### 如果是 chiplet / cross-die

优先看：

- 分层距离模型
- placement 跨 die 代价
- hierarchical collective
- memory edge 组织

## 什么时候该回头重判

当下面条件变化时，原决策通常要重判：

- workload 结构变了
- memory placement 变了
- chiplet / HBM 组织变了
- control / response 关键性变了
- simulator 发现 stall 主因和原假设不一致

## 一句话理解

NoC 设计决策的关键不是同时优化所有维度，而是先判断“这个系统当下真正怕什么”，再沿最短路径收敛。

## 建模启示

这页最适合在开新 case study 或开新实验前快速过一遍。它的作用不是给唯一答案，而是防止一开始就把注意力放在低优先级问题上。
