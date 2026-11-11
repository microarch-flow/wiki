# 01 全局链路：一组数据怎样到达另一端？

上级：[SerDes Wiki](../README.md)

先看完整路径，再看各个电路。这里用一条单向 lane 建立概念；双向通信和多 lane 是进一步的组合，不应默认所有实现的 lane 定义相同。

## 阅读顺序

1. [为什么需要 SerDes？](./why-serdes.md)
2. [一组数据怎样经过 TX、通道和 RX？](./link-end-to-end.md)
3. [PHY、SerDes 与协议是什么关系？](./phy-serdes-protocol.md)
4. [位宽、线速率、符号率与时钟怎样换算？](./rates-clocks-and-ui.md)

读完后，应能说出每个观察点的数据形式，并能解释线速率为何不能直接等同于全部数字逻辑的时钟。接下来进入[电信号与通道](../02-signal-channel/README.md)。
