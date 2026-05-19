# 02 链路、分层与事务基础

这一部分先解决“PCIE 是怎样组织起来的”：

- 角色和拓扑怎么分
- 三层各自负责什么
- 一个请求为什么会表现成 TLP、DLLP 和 completion

## 推荐阅读顺序

1. [Root Complex、Switch、Endpoint 在系统里各做什么](./topology-root-complex-switch-endpoint.md)
2. [分层架构：Transaction / Data Link / Physical](./layered-architecture-transaction-data-link-physical.md)
3. [TLP、DLLP 与 Completion 语义](./tlp-dllp-completion-basics.md)
4. [Posted / Non-Posted / Completion 与 Ordering](./posted-nonposted-completion-ordering.md)
