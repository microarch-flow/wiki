# 02 链路、分层与事务基础

上级：[系统 I/O 互连（PCIe）](../README.md)

先画出请求经过的实体，再区分事务返回、逐跳确认和接收信用。基础示例采用 Non-Flit 模式；Flit Mode 的差异在相应文章单列。

## 推荐阅读顺序

1. [拓扑与角色](./topology-root-complex-switch-endpoint.md)
2. [协议三层职责](./layered-architecture-transaction-data-link-physical.md)
3. [一次读取与 Completion](./tlp-dllp-completion-basics.md)
4. [信用流控与链路重放](./credit-flow-control-and-replay.md)
5. [请求类型与排序](./posted-nonposted-completion-ordering.md)
