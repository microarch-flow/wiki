# 分层架构：Transaction / Data Link / Physical

上级：[02 链路、分层与事务基础](./README.md)

相关：[TLP、DLLP 与 Completion 语义](./tlp-dllp-completion-basics.md)

## 这页在回答什么问题

为什么 PCIE 要分层，以及这三层各自解决什么问题。

## Transaction Layer 关心什么

- read / write / message 这类事务语义
- 请求和 completion 的配对关系
- 地址、属性、长度、tag 等事务字段

这层更接近“系统在表达什么请求”。

## Data Link Layer 关心什么

- 相邻节点之间的可靠传输
- 包确认、重传、序号
- flow control credit

这层更接近“链路上怎么把包稳妥送到对端”。

## Physical Layer 关心什么

- lane、速率、训练、均衡
- 电气与编码细节
- 链路建立和物理可达性

这层更接近“比特怎样在介质上真的跑起来”。

## 为什么分层对体系结构有价值

因为很多问题根本不在同一层：

- `AER/Unsupported Request` 往往是事务语义或路由问题
- `credit 不够` 更像链路级流控问题
- `速率降档` 更像物理链路质量问题

不分层，调试会很快失焦。

## 一句话理解

Transaction 层决定“想做什么”，Data Link 层决定“怎么可靠送达”，Physical 层决定“比特是否跑得动”。
