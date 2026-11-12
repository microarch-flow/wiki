# AER、计数器与链路调试路径

上级：[05 性能与调试](./README.md)

相关：[Unsupported Request、Completer Abort、Timeout 怎么看](./common-failures-ur-ca-timeout.md)

## 这页在回答什么问题

当 PCIE 出现间歇性错误、掉速或链路异常时，应该先看哪些观测点。

## AER 在做什么

AER 扩展错误记录和报告。规范分类是 **Correctable** 和 **Uncorrectable**；后者再按严重性区分 **Non-Fatal**、**Fatal**。分类不是固定恢复步骤：有些错误可由链路机制纠正，其他错误可能需要软件隔离或恢复。操作系统是否看到报告还受使能、掩码、固件控制和平台处理影响。见 [Linux AER 指南](https://docs.kernel.org/PCI/pcieaer-howto.html)。

## 常见观测点

- link status / negotiated width / speed
- error counter / replay / retry 相关统计
- AER 日志和错误状态
- device driver 中断和 completion 统计

例如在同一负载和时间窗内，分别读取端口链路重放计数的增量、AER 状态/日志及方向吞吐。重放计数增加表明该实现观察到重放；是否有 AER 日志取决于对应错误与报告路径。不能把日志条数直接当成重放次数，也不能仅因开启 AER 就推断它造成重放。

## 调试时先分三层

- 物理层：是否降速、掉 lane、训练不稳
- 链路层：是否重传、credit 异常、吞吐震荡
- 事务层：是否 UR、CA、timeout、访问越界

## 一句话理解

PCIE 调试先别盯单一报错，先把错误归位到物理、链路、事务三层，再决定往设备、平台还是软件方向深入。
