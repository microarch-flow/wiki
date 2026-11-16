# 03 发送端：怎样把并行位送进通道？

上级：[SerDes Wiki](../README.md)

发送端接收数字数据、时钟和配置，按约定产生电信号。串行化决定位的时间顺序；时钟生成、驱动和均衡决定波形如何发出。

## 阅读顺序

1. [并行字怎样变成串行流？](./parallel-to-serial.md)
2. [PLL、分频与多相时钟怎样工作？](./clock-pll-and-multiphase.md)
3. [发送驱动、摆幅与终端](./driver-swing-and-termination.md)
4. [发送均衡与 FFE：为什么要改变发送波形？](./tx-equalization-ffe.md)
5. [走一遍 TX 教学案例](./tx-path-worked-example.md)

接着读[接收端](../04-receiver/README.md)，观察通道输出如何被采样与恢复。
