# CPO 一页版总览

上级：[13 一页版总览](./README.md)

## CPO 是什么

CPO（Co-Packaged Optics）把光引擎与主 ASIC 在封装层级紧密集成，目标是缩短高速电段，以缓解部分高带宽交换与计算系统中的：

- 长高速电链路功耗
- 面板密度限制
- 系统扩展压力

## 它为什么重要

当目标配置受电通道、功耗或面板密度限制时，CPO 提供一种重新划分系统边界的选择。约束是否成立需要按具体系统验证。

最核心的驱动力是：

- bandwidth density
- electrical I/O power
- AI factory scale

## 它和 pluggable / NPO 的关系

| 方案 | 光电转换位置 | 优势 | 代价 |
| --- | --- | --- | --- |
| 前面板可插拔模块 | 前面板/板边 | 可独立替换 | 板级电段和面板空间需评估 |
| NPO | 引擎靠近 ASIC 封装 | 可能缩短电路径 | 基板层级、接口和替换单元依实现而异 |
| CPO | 引擎与 ASIC 在封装级集成；光源可外置 | 可能改善带宽密度与能效 | 需评估热、测试、良率和维护 |

术语边界在不同资料中可能重叠；具体说明见[分类框架](../01-overview/taxonomy.md)。

## 它最关键的工程难点

- 热
- 激光器位置
- optical engine 与 package integration
- fiber / connector / attach
- KGD 与系统良率
- 测试与现场维护

## 它最重要的技术主线

- external laser / remote light source
- optical I/O chiplet
- silicon photonics / PIC
- polymer waveguide / connectorization
- advanced packaging / co-design

## 它最重要的产业判断

以下是研究视角，不是出货排名。具体公告日期和支持范围见[公司生态来源表](../18-sources-and-updates/company-ecosystem-sources.md)。

- AI / HPC 是值得观察的场景，不能据此推断全部网络的采用顺序
- adoption 速度取决于客户资格、维护和系统收益，需以实际数据检验
- 先进封装很重要，但平台需求和运维接受度同样重要
- 平台和部件供应商的角色均需结合项目交付与责任边界确认

## 当前最值得跟踪的公司主线

- Broadcom：交换平台型 CPO
- NVIDIA：AI factory photonics 路线
- Cisco：system + optics 内化路线
- Ayar Labs：optical I/O chiplet 路线
- AMD：photonics 能力补齐路线

## 一句话结论

CPO 通过封装级集成改变 I/O 路径，并同时改变光学、制造和维护边界；适用性由具体系统的收益与代价决定。
