# 光链路基础

上级：[04 光引擎与核心器件](./README.md)

相关：[系统栈与接口位置](../03-architecture-platform/system-stack.md)

## 最小对象

理解 CPO，不必先学完整光通信理论，但要先认识这些对象：

- laser：提供光源
- modulator：把电信号调到光上
- waveguide / fiber：传输光
- photodetector：把光转回电
- driver：驱动调制器
- TIA：把探测器微弱电流放大并恢复信号

## 最小链路

发送端可以抽象成：

`SerDes -> driver -> modulator -> waveguide/fiber`

接收端可以抽象成：

`fiber/waveguide -> photodetector -> TIA -> electrical interface`

## 为什么光链路对 CPO 有吸引力

- 远距离或高带宽下，光域传输损耗通常比同等级电域链路更可控
- 不再需要让超高速电信号跑完整块板子
- 面向更高总带宽时，前面板连接和铜通道不再是唯一扩展手段

## 但光链路也不是白送的

- laser 需要电功率并带来热
- 耦合有损耗
- 调制器和探测器有带宽、线性度、偏置和温漂问题
- 封装时要解决精密对准

## 关键指标

- 每通道速率
- 每比特能耗
- 插入损耗
- 链路预算
- 温度稳定性
- 耦合效率

## 一句话理解

CPO 的器件层本质，是把“高速电传输很难”这件事前移为“近距离电驱动 + 尽早进入光域”。
