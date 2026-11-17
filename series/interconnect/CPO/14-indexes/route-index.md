# 路线索引表

上级：[14 术语、公司与路线索引](./README.md)

这些行来自不同维度，不能当成互斥的选项。同一个 optical I/O chiplet 可以采用硅光、外置激光和聚合物波导；链路预算必须使用具体路径和元件参数。

| 路线 / 维度 | 核心要解决的问题 | 主要优点 | 主要代价 | 代表性研究入口 |
| --- | --- | --- | --- | --- |
| 集成位置：Pluggable optics | 保持模块化和可维护性 | 模块可独立替换 | 电通道与面板约束需按系统测量 | 可插拔模块接口 |
| 集成位置：NPO | 让光引擎靠近主封装 | 可能缩短电路径 | 封装边界与维护单元因实现而异 | [分类框架](../01-overview/taxonomy.md) |
| 集成位置：平台化 CPO | 优化带宽密度与系统能效 | 可能缩短高速电段 | 热、测试及维修需共同评估 | Broadcom、NVIDIA |
| 光源位置：External laser CPO | 将光源移离主要热源 | 可能降低光源热耦合 | 供光分发、损耗及冗余 | Ayar Labs 一类路线 |
| 子系统边界：Optical I/O chiplet | 把光 I/O 组织为芯粒 | 便于定义芯粒接口 | 依赖主平台整合 | Ayar Labs |
| 器件工艺：Silicon photonics platform | 稳定提供 PIC / engine 能力 | 平台化潜力强 | 仍需封装与连接配合 | Intel、Marvell |
| 连接材料：Polymer waveguide interface | 探索高密度连接 | 可设计不同连接结构 | 损耗、装配与可靠性需实测 | IBM/相关封装路线 |
