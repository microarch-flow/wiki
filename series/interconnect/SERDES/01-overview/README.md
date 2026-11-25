# 01 全局链路：一组数据怎样到达另一端？

<!-- nav-title: 01 全局链路 -->

上级：[SerDes Wiki](../README.md)

先看完整路径，再看各个电路。这里用一条单向 lane 建立概念；双向通信和多 lane 是进一步的组合，不应默认所有实现的 lane 定义相同。

## 阅读顺序

1. [跟一个 32 位字走完链路](./link-end-to-end.md)
2. [串行化的原因与取舍](./why-serdes.md)
3. [PHY、SerDes 与协议](./phy-serdes-protocol.md)
4. [位宽、速率与时钟](./rates-clocks-and-ui.md)

读完后，应能说出每个观察点的数据形式，并能解释线速率为何不能直接等同于全部数字逻辑的时钟。接下来进入[电信号与通道](../02-signal-channel/README.md)。
