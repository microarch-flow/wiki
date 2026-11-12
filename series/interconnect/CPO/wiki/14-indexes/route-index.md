# 路线索引表

上级：[14 术语、公司与路线索引](./README.md)

这些行来自不同维度，不能当成互斥的选项。同一个 optical I/O chiplet 可以采用硅光、外置激光和聚合物波导；链路预算必须使用具体路径和元件参数。

| 路线 / 维度 | 核心要解决的问题 | 主要优点 | 主要代价 | 代表性研究入口 |
| --- | --- | --- | --- | --- |
| 集成位置：Pluggable optics | 保持模块化和可维护性 | 生态成熟 | 电链路长、密度受限 | 传统数据中心网络 |
| 集成位置：NPO | 折中缩短电路径 | 风险较低 | 收益可能不够极致 | 过渡型平台 |
| 集成位置：平台化 CPO | 极限带宽密度与系统能效 | 更适合高端交换平台 | 热、测试、维护复杂 | Broadcom、NVIDIA |
| 光源位置：External laser CPO | 降低激光热耦合与维护负担 | 热与 serviceability 更友好 | 光源分发更复杂 | Ayar Labs 一类路线 |
| 子系统边界：Optical I/O chiplet | 把光 I/O 子系统化 | 更容易进入 package 生态 | 依赖主平台整合 | Ayar Labs |
| 器件工艺：Silicon photonics platform | 稳定提供 PIC / engine 能力 | 平台化潜力强 | 仍需封装与连接配合 | Intel、Marvell |
| 连接材料：Polymer waveguide interface | 提高密度并改善连接工程 | 装配窗口更可设计 | 可靠性与材料工程复杂 | IBM/相关封装路线 |
