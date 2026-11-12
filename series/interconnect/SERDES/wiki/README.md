# SerDes Wiki：从比特到可恢复的信号

SerDes 让并行数字数据经过串行链路，再在另一端恢复。理解它，需要同时看数据、时钟和物理通道。本专题从一条单向电链路出发，解释信号为什么会变形，以及收发两端如何应对。

如果电压、电流、电容和采样边沿还不熟悉，先读[从电荷到芯片时序](../../../../electrical-timing-foundations.md)。每篇中的数值案例都标明假设；示意图不是电路仿真或硬件测量。

## 阅读路线

| 顺序 | 章节 | 读完后能够回答 |
| --- | --- | --- |
| 1 | [全局链路](./01-overview/README.md) | 数据经过哪些边界？PHY、SerDes、lane 和速率分别是什么？ |
| 2 | [电信号与通道](./02-signal-channel/README.md) | 差分信号怎样传输？反射、损耗和串扰怎样影响采样？ |
| 3 | [发送端](./03-transmitter/README.md) | 并行数据怎样变成按时发送的电信号？FFE 做了什么？ |
| 4 | [接收端](./04-receiver/README.md) | 接收端怎样选择采样时刻和门限，并恢复并行数据？ |
| 5 | [信号与指标](./05-signaling-and-metrics/README.md) | 如何区分调制、编码、眼图、BER、带宽和能耗的口径？ |
| 6 | [初始化与链路训练](./06-link-operation/README.md) | 两端怎样建立链路、调整参数、对齐并观察恢复过程？ |
| 7 | [设计与验证](./07-design-and-validation/README.md) | 如何定义需求，区分仿真、样片、合规与互通证据？ |
| 8 | [系统应用](./08-system-applications/README.md) | PCIe、以太网、D2D、HBM 与光接口怎样比较？ |
| 9 | [建模](./09-modeling/README.md) | 如何定义服务、排队、状态、恢复、功耗及模型边界？ |
| 查阅 | [术语、资料与自测](./10-reference/README.md) | 查找已编写章节的术语、资料来源并检查理解。 |

建议按 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 阅读。每章首页给出篇内顺序。只想建立全局印象时，可先读[一组数据经过 TX、通道和 RX](./01-overview/link-end-to-end.md)，再根据问题进入相应模块。

## 一个贯穿案例

后文多次使用同一个教学假设：单向 NRZ lane；并行端每周期输入 32 bit，时钟为 312.5 MHz；每个周期都提供一个有效字，且串行路径没有额外编码开销。则线速率为 `32 × 312.5 MHz = 10 Gb/s`，NRZ 符号率为 `10 GBd`，一个 UI 是 `100 ps`。这不是任何特定协议的有效载荷带宽。

接收端的离散案例使用 `r[k] = 0.7a[k] + 0.2a[k−1]`，其中符号 `a` 取 `−1` 或 `+1`。这是人为构造的归一化抽样模型，不代表任何通道的实测响应。每篇使用它时会说明是否启用发送均衡以及忽略了什么。

三个阶段的规划正文已编写，覆盖链路、指标、训练、设计验证、系统应用和建模。各篇明确案例和证据边界；专题入门内容不能代替具体协议规范、器件手册或项目测试。

## 与其他专题的关系

- [PCIe 分层架构](../../PCIE/wiki/02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md)：从物理层继续理解协议和事务。
- [封装内的信号完整性](../../../../FAB/wiki/06-cross-cutting-engineering/signal-integrity-in-package.md)：理解封装、回流、串扰及电源噪声。
- [CPO 光链路基础](../../CPO/wiki/04-optical-engine/optical-link-basics.md)：从电接口继续到光引擎。
