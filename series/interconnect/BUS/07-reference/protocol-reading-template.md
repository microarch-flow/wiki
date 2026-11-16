# BUS 协议阅读模板

上级：[07 术语与检查清单](./README.md)

相关：[术语表](./glossary.md)、[BUS 一页版总览](./bus-one-page.md)、[互连方案评估模板](./interconnect-evaluation-template.md)

## 使用方式

读 BUS 协议文档时，不要从字段表开始抄。先判断协议定位，再拆事务模型、流控、顺序、错误、桥接和软件语义。字段名只有落到这些问题上，才对系统设计和调试有价值。

## 推荐模板

```md
# 协议名称

## 1. 协议定位

- 它主要解决什么问题：
- 面向控制面还是数据面：
- 适合的系统规模：
- 典型 master / slave：
- 不适合的场景：

## 2. Resource

- 参与者命名：master/slave、initiator/target、client/manager：
- ID/source/sink/slot：
- channel：
- FIFO/buffer：
- sideband attribute：

## 3. Topology

- 适合 shared bus / matrix / crossbar / NoC bridge：
- 是否支持多 master / 多 slave：
- 是否需要 decoder / arbiter / bridge：
- 是否支持分层互连：
- response path 如何组织：

## 4. Interaction

- read transaction 如何闭环：
- write transaction 如何闭环：
- request / data / response 是否分离：
- burst / beat / narrow transfer 如何定义：
- ordering 规则：
- outstanding 规则：
- backpressure / flow control：
- error response：

## 5. Capability

- burst / alignment / boundary：
- byte strobe / partial access：
- cacheability / attributes：
- QoS / priority：
- coherence / shareability：
- timeout / retry / abort：
- observability：

## 6. 系统集成

- 和 CPU 的关系：
- 和 DMA 的关系：
- 和 DDR controller 的关系：
- 和 MMIO/APB 的关系：
- 和 IOMMU/SMMU 的关系：
- 和 interrupt/completion 的关系：
- 常见 bridge 对象：

## 7. 性能风险

- 最大吞吐受什么限制：
- tail latency 风险：
- response path 风险：
- read/write 混合风险：
- burst 对小请求的影响：

## 8. 正确性风险

- 哪些访问必须保序：
- error 是否能释放资源：
- MMIO side effect 如何处理：
- cache/coherence/barrier 边界：
- reset/low-power 状态下访问行为：

## 9. 调试方法

- 最小 counter：
- 关键 trace：
- waveform 先看哪些握手：
- timeout/fault/hang 如何分类：

## 10. 最容易踩的坑

-

## 11. 最适合的场景

-
```

## 阅读原则

| 原则 | 解释 |
| --- | --- |
| 先定位后字段 | 字段只有对应到事务语义才有意义 |
| 先闭环后优化 | read/write/error/timeout 能闭环，再讨论吞吐 |
| request 和 response 分开 | 返回路径是协议问题高发位置 |
| 协议和系统语义分开 | 协议 response 不等于软件 completion |
| 能力和代价一起看 | outstanding、burst、coherence 都增加验证状态 |

## 一句话理解

协议阅读模板的目标不是抄字段，而是把协议转换成可建模的 Resource、Topology、Interaction 和 Capability。

## 建模启示

读完一个协议后，应该能写出事件表：`request_accept`、`data_beat`、`response_return`、`error_response`、`backpressure_assert`、`id_allocate`、`id_release`、`burst_split`、`attribute_map`。如果写不出这些事件，就说明协议还停留在字段记忆，没有进入系统模型。

协议阅读的最终产物应包括三类内容：事务闭环图、错误/timeout 路径图、系统集成风险表。它们比字段清单更能指导设计、验证和调试。
