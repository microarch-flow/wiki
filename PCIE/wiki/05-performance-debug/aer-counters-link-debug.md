# AER、计数器与链路调试路径

上级：[05 性能与调试](./README.md)

相关：[Unsupported Request、Completer Abort、Timeout 怎么看](./common-failures-ur-ca-timeout.md)

## 这页在回答什么问题

当 PCIE 出现间歇性错误、掉速或链路异常时，应该先看哪些观测点。

## AER 在做什么

AER 提供的是错误可见性框架，帮助你区分：

- 可恢复错误
- 不可恢复错误
- 链路或事务层异常

它的价值不只是“报错”，而是把错误类型组织成可诊断信号。

## 常见观测点

- link status / negotiated width / speed
- error counter / replay / retry 相关统计
- AER 日志和错误状态
- device driver 中断和 completion 统计

## 调试时先分三层

- 物理层：是否降速、掉 lane、训练不稳
- 链路层：是否重传、credit 异常、吞吐震荡
- 事务层：是否 UR、CA、timeout、访问越界

## 一句话理解

PCIE 调试先别盯单一报错，先把错误归位到物理、链路、事务三层，再决定往设备、平台还是软件方向深入。
