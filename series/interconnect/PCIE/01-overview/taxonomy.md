---
title: "PCIe 问题地图：角色、事务、地址与性能"
---

<div id="pcie-分类框架" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# PCIe 问题地图：角色、事务、地址与性能

上级：[概览与问题定义](README.md)

排查 PCIe 问题前，先给观察对象分类。下面五个维度用于组织工程问题，只有“协议分层”指 PCIe 的三层体系；其他维度并不是叠在它上面的协议层。

<div id="一个实用的五层分类法" class="pcie-legacy-anchor"></div>
<div id="1-系统角色层" class="pcie-legacy-anchor"></div>
<div id="2-协议分层" class="pcie-legacy-anchor"></div>
<div id="3-资源与寻址层" class="pcie-legacy-anchor"></div>
<div id="4-数据路径层" class="pcie-legacy-anchor"></div>
<div id="5-系统能力层" class="pcie-legacy-anchor"></div>

## 五个分析维度

| 维度 | 输入或对象 | 要回答的问题 | 正文 |
| --- | --- | --- | --- |
| 系统角色 | RC、Root Port、Switch、Endpoint | 谁发请求，谁返回，共享哪段路径？ | [拓扑](../02-link-transaction-basics/topology-root-complex-switch-endpoint.md) |
| 协议分层 | TLP、链路控制、物理信号 | 是事务未完成、链路等待还是未建链？ | [分层](../02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md) |
| 资源与寻址 | BDF、BAR、DMA 地址、IOMMU 域 | 请求到哪个资源，使用什么地址？ | [地址视角](../03-configuration-enumeration-addressing/mmio-config-dma-address-view.md) |
| 数据路径 | 描述符、数据、CQE、中断 | 谁拥有缓冲区，哪个事件允许下一步？ | [运行路径](../04-data-path-dma-interrupts/README.md) |
| 系统能力 | AER、SR-IOV、ATS、P2P | 哪些能力已配置，平台是否支持？ | [高级主题](../07-advanced-topics/README.md) |

<div id="为什么这样切分有用" class="pcie-legacy-anchor"></div>

## 同一现象怎样拆开

“设备读得慢”至少有三种不同解释。读请求未发出，可能在等 Tag 或请求方向的信用；请求已发出但返回慢，可能在等翻译、内存或 Completion 链路；数据已收齐但应用仍等待，可能在等设备执行、CQE 或软件处理。

因此应记录请求发出、最终 CplD 收齐、CQE 发布和软件消费四个时刻。仅有应用耗时，无法区分这些原因。

<div id="6-量化-可建模维度" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 把问题转换成可测量参数

| 对象 | 记录什么 | 不能直接推出什么 |
| --- | --- | --- |
| 每段链路 | 速率、宽度、方向吞吐、模式 | 应用必然达到名义带宽 |
| 读请求窗口 | 可用槽数、平均占用、完整 RTT、实际请求长度 | MRRS 就是每笔长度 |
| 接收路径 | 各类信用、物理缓冲、更新延迟 | 有信用就一定有 Tag |
| 错误路径 | AER 状态、重放增量、采样窗口 | AER 日志条数等于重放次数 |
| 软件接口 | 队列占用、批大小、通知和消费时刻 | 中断次数等于完成项数 |

参数定义与公式集中在[建模速查](../08-reference/pcie-modeling-params.md)。一个参数可能同时受多个模块影响，例如 RTT 包含路径服务与排队；分类的作用是确定观察边界，而不是把所有原因强行归到单一模块。
