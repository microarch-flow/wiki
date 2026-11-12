# 04 接收端：怎样从受损波形恢复数据？

上级：[SerDes Wiki](../README.md)

接收端面对连续变化的电压。它既要决定“是什么”，也要决定“何时判断”。均衡、采样、时钟恢复和历史判决可能相互影响。

## 阅读顺序

1. [接收端有哪些数据与反馈路径？](./receiver-signal-chain.md)
2. [接收前端与 CTLE 做什么？](./analog-frontend-and-ctle.md)
3. [采样器怎样把波形变成判决？](./sampler-and-decision.md)
4. [CDR 怎样恢复采样时序？](./cdr-and-timing-recovery.md)
5. [DFE 怎样使用历史判决？](./dfe-and-error-propagation.md)
6. [解串、字边界与时钟域](./deserializer-and-alignment.md)
7. [走一遍 RX 协同案例](./rx-cooperation-example.md)

读完后，应能解释一次判决的条件，以及正确判决、时钟锁定和字边界对齐为何是不同问题。术语见[术语表](../10-reference/glossary.md)。
