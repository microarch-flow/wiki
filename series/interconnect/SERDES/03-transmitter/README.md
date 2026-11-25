# 03 发送端：怎样把并行位送进通道？

<!-- nav-title: 03 发送端 -->

上级：[SerDes Wiki](../README.md)

发送端接收数字数据、时钟和配置，按约定产生电信号。串行化决定位的时间顺序；时钟生成、驱动和均衡决定波形如何发出。

先在[32 位字的发送时序](../01-overview/link-end-to-end.md#launch)中找出首位、末位和装载边沿。本章继续看发送端的时钟和电路。

## 阅读顺序

1. [PLL、分频与多相时钟](./clock-pll-and-multiphase.md)
2. [发送驱动、摆幅与终端](./driver-swing-and-termination.md)
3. [发送均衡与 FFE](./tx-equalization-ffe.md)
4. [TX 串行化与均衡案例](./tx-path-worked-example.md)

接着读[接收端](../04-receiver/README.md)，观察通道输出如何被采样与恢复。
