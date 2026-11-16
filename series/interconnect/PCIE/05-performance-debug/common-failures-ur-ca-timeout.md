# Unsupported Request、Completer Abort、Timeout 怎么看

上级：[05 性能与调试](./README.md)

相关：[AER、计数器与链路调试路径](./aer-counters-link-debug.md)

## 这页在回答什么问题

PCIE bring-up 和调试里最常见的几类错误，通常各自意味着什么。

## Unsupported Request 常提示什么

- 地址或请求类型对目标不合法
- BAR / 路由 / capability 没配对
- software 访问了设备不支持的窗口

## Completer Abort 常提示什么

- 目标设备无法完成该请求
- 下游状态不完整
- 某段资源配置或功能使能没有闭环

## 区分 PCIe Completion Timeout 和软件超时

PCIe Completion Timeout 指 requester 为 non-posted 请求等待所需事务返回，超过规定时间窗口仍未完成。例如配置读或 Memory Read 没有收到全部所需 Completion，可能涉及路由、链路或目标；应检查 requester 错误状态和路径。UR、CA 则可作为这些请求的 Completion Status 返回，收到它们是有返回的错误证据。

软件等待 CQE 超时是另一观察点：即使配置访问和 DMA 的 PCIe 事务均正常，设备执行未完成、CQE 未发布或软件消费队列错误也会使等待超时。普通 posted Memory Write 不收到与该写对应的常规错误 Completion，其错误须通过适用的报告机制定位。

## 调试时不要直接跳结论

这三类错误都要同时回看：

- 请求是 config、MMIO 还是 DMA 相关
- 问题发生在枚举期、运行期还是异常恢复期
- 设备、switch、root complex 哪一侧先表现异常

## 一句话理解

UR、CA、timeout 不是“报个错就结束”，它们是在提示哪一段系统契约没有闭环。
