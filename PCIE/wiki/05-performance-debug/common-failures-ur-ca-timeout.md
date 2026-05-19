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

## Timeout 常提示什么

- 请求发出后没等到预期返回
- 链路、路由或下游设备卡住
- 也可能是软件观察点等待错对象

## 调试时不要直接跳结论

这三类错误都要同时回看：

- 请求是 config、MMIO 还是 DMA 相关
- 问题发生在枚举期、运行期还是异常恢复期
- 设备、switch、root complex 哪一侧先表现异常

## 一句话理解

UR、CA、timeout 不是“报个错就结束”，它们是在提示哪一段系统契约没有闭环。
