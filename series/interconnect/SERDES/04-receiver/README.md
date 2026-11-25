# 04 接收端：怎样从受损波形恢复数据？

<!-- nav-title: 04 接收端 -->

上级：[SerDes Wiki](../README.md)

接收端面对连续变化的电压。它既要决定“是什么”，也要决定“何时判断”。均衡、采样、时钟恢复和历史判决可能相互影响。

如果要手算错一个采样点与错一个字边界的区别，先看[同一条 32 位记录在 B 的两种结果](../01-overview/link-end-to-end.md#sample)。

## 阅读顺序

1. [接收数据与反馈路径](./receiver-signal-chain.md)
2. [接收前端与 CTLE](./analog-frontend-and-ctle.md)
3. [采样与判决](./sampler-and-decision.md)
4. [CDR 与采样时序](./cdr-and-timing-recovery.md)
5. [DFE 与错误传播](./dfe-and-error-propagation.md)
6. [RX 协同案例](./rx-cooperation-example.md)

读完后，应能解释一次判决的条件，以及正确判决、时钟锁定和字边界对齐为何是不同问题。术语见[术语表](../10-reference/glossary.md)。
