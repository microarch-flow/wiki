# 03 计算范式

这一部分不按介质分，而是按计算机制分。

按介质分类只能回答“权重存在哪里”，但很多判断还取决于另一个问题：

> 它到底是用数字方式算，还是用模拟方式算，或者只是在阵列内做一部分模拟、其余交给数字外围？

这正是本章的作用。

## 子主题

- [Digital CIM](./digital-cim.md)
- [Analog CIM](./analog-cim.md)
- [Mixed-Signal CIM](./mixed-signal-cim.md)

## 本章关注点

- 乘法和累加发生在哪里
- 精度、验证和量产难度如何权衡
- 阵列内计算和外围数字逻辑如何分工

## 建议阅读方式

- 先读 [Digital CIM](./digital-cim.md)，建立最稳妥的基准线
- 再读 [Analog CIM](./analog-cim.md)，理解为什么理论收益更高
- 最后读 [Mixed-Signal CIM](./mixed-signal-cim.md)，理解为什么大量真实设计会落在折中区域

## 与案例库的对应关系

- `HBM-PIM` 这类路线通常不适合简单塞进本章三分法，它更偏 system-side processing
- `TSMC 16nm CIM Macro` 更适合用本章来追问它到底偏 digital 还是 mixed-signal
- `东京大学 ReRAM-CiM` 更适合作为 analog / mixed-signal 路线的典型观察对象
