# Torus 与 Ring 专题

上级：[Topology 与 Routing](./README.md)

相关：[Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./topology-family-deep-dive.md)

## 为什么把 torus 和 ring 放一起

它们都可以看成“比 mesh 更强调闭环路径”的家族，但系统价值完全不同：

- torus 更像对 mesh 的增强
- ring 更像极简互连

## Torus

### 核心直觉

torus 在 mesh 基础上增加环回边，目标是：

- 降低边界效应
- 缩短逻辑最远距离
- 提高横截面带宽

### 优点

- 平均 hop 通常更好
- 边角节点不再天然弱势

### 关键问题

- 环回边往往是长链路
- 物理实现成本不再像 mesh 那样规整
- 长链路 pipeline 可能吃掉逻辑 hop 优势

### 适合什么

- 真正愿意把长链路代价纳入设计的系统

## Ring

### 核心直觉

ring 用最小结构换最简单实现。

### 优点

- 小规模时非常省
- 控制简单
- 验证也简单

### 关键问题

- 扩展性差
- 共享路径很强，热点敏感
- 大规模时延和带宽都容易掉队

### 适合什么

- 小 cluster 内互连
- 控制面
- 较轻量子网络

## 什么时候 torus 胜过 mesh

通常在你确实需要更低逻辑 hop，而且愿意接受：

- 长链路
- 更复杂物理实现
- credit round-trip 可能变长

否则理论优势未必会兑现。

## 什么时候 ring 仍有价值

不是作为大规模全局主互连，而是作为：

- local ring
- side network
- 小规模 cluster fabric

## 你至少该做的实验

- mesh vs torus：同规模下加入长链路代价后是否还占优
- ring 作为 cluster-local fabric 是否优于 local crossbar

## 本页结论

torus 和 ring 都不是“更高级的 mesh 替代品”。  
torus 更适合在愿意付物理代价时换取逻辑 hop 改善；ring 更适合作为局部、轻量、低复杂度互连。
