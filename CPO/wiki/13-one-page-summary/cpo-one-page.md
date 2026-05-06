# CPO 一页版总览

上级：[13 一页版总览](./README.md)

## CPO 是什么

CPO（Co-Packaged Optics）本质上是把高速 I/O 的光电转换从板级/模块级前移到封装级或近封装级，以缓解高带宽交换与计算系统中的：

- 长高速电链路功耗
- 面板密度限制
- 系统扩展压力

## 它为什么重要

它不是单一器件创新，而是 AI / HPC 系统规模把传统 pluggable 路线逼近边界后的系统级重构尝试。

最核心的驱动力是：

- bandwidth density
- electrical I/O power
- AI factory scale

## 它和 pluggable / NPO 的关系

| 方案 | 光电转换位置 | 优势 | 代价 |
| --- | --- | --- | --- |
| Pluggable | 前面板/板边 | 生态成熟、可维护性强 | 电链路长、功耗和密度吃亏 |
| NPO | 更靠近封装 | 折中缩短电路径 | 边界不清、收益有限 |
| CPO | 封装级/近封装级 | 带宽密度高、潜在能效更优 | 热、测试、良率、维护复杂 |

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

- 先落地的场景大概率是 AI / HPC，不是所有网络
- adoption 速度会慢于技术想象速度
- 先进封装很重要，但平台需求和运维接受度同样重要
- 平台方决定 adoption 节奏，关键拼图供应商决定路线能否成立

## 当前最值得跟踪的公司主线

- Broadcom：交换平台型 CPO
- NVIDIA：AI factory photonics 路线
- Cisco：system + optics 内化路线
- Ayar Labs：optical I/O chiplet 路线
- AMD：photonics 能力补齐路线

## 一句话结论

CPO 不是“更高级的光模块”，而是高带宽 AI / HPC 系统在物理边界逼近后，对 I/O 架构、封装、光学、制造和维护边界的一次联合重构。
