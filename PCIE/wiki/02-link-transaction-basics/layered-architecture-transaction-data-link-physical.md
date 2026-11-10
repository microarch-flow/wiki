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

在传统 **Non-Flit** 模式下，Data Link 层用序号、LCRC、ACK/NAK 与重放缓冲保证相邻端口间的 TLP 传输。ACK 只确认这一跳，重放也只作用于这一跳。

流控约束发送：发送端必须有该 TLP 类别所需的 header/data credit 才能发送；接收端消费缓冲后，通过链路控制信息更新 credit。credit 表示接收容量，不表示请求已经完成。Non-Flit 使用 UpdateFC DLLP 等链路控制包；Flit 模式的控制承载形式不同，不能直接套用这个包模型。

例如，EP 向主机发送 Memory Read，先等待 EP→Switch 链路所需 credit；Switch 收到请求后向 EP 返回该跳的 ACK，并继续向 RC 转发；RC 接收后向 Switch 返回其对应的 ACK。即使 EP 收到链路 ACK，该读 Tag 仍占用，直到匹配的事务 Completion 收齐或请求按错误处理结束。链路未训练成功时，上述正常传输尚不能开始。实现和模式应以目标规范为准；可参见 [PCIe 2.1 基础规范](https://www.intel.com/content/dam/support/us/en/programmable/support-resources/fpga-wiki/asset03/pci-express-base-r2.1.pdf)。

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
